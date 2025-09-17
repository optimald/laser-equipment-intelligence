"""
Facebook Marketplace spider (stealth browsers only, heavy throttling)
"""

import scrapy
import time
import random
from playwright.async_api import async_playwright
from scrapy_playwright.page import PageMethod
from laser_intelligence.pipelines.normalization import LaserListingItem


class FacebookMarketplaceSpider(scrapy.Spider):
    name = 'facebook_marketplace'
    allowed_domains = ['facebook.com', 'm.facebook.com']
    start_urls = [
        'https://www.facebook.com/marketplace/search/?query=laser%20equipment',
        'https://www.facebook.com/marketplace/search/?query=sciton%20laser',
        'https://www.facebook.com/marketplace/search/?query=cynosure%20laser',
        'https://www.facebook.com/marketplace/search/?query=cutera%20laser',
        'https://www.facebook.com/marketplace/search/?query=candela%20laser',
        'https://www.facebook.com/marketplace/search/?query=lumenis%20laser',
        'https://www.facebook.com/marketplace/search/?query=alma%20laser',
        'https://www.facebook.com/marketplace/search/?query=inmode%20laser'
    ]

    custom_settings = {
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 120000,  # 2 minutes for FB
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            'headless': False,  # Use visible browser for FB
            'args': [
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        },
        'DOWNLOAD_DELAY': (60, 120),  # Heavy throttling: 1-2 minutes between requests
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 1,  # Single request at a time
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'DOWNLOADER_MIDDLEWARES': {
            'laser_intelligence.middleware.evasion.EvasionMiddleware': 543,
            'laser_intelligence.middleware.proxy.ProxyMiddleware': 544,
            'laser_intelligence.middleware.captcha.CaptchaMiddleware': 545,
            'laser_intelligence.middleware.impersonate.ImpersonateMiddleware': 546,
        },
        'ITEM_PIPELINES': {
            'laser_intelligence.pipelines.normalization.NormalizationPipeline': 300,
            'laser_intelligence.pipelines.scoring.ScoringPipeline': 400,
            'laser_intelligence.pipelines.alerts.AlertsPipeline': 500,
        },
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.processed_urls = set()
        self.request_count = 0
        self.max_requests_per_session = 10  # Limit requests per session

    def start_requests(self):
        """Generate initial requests with heavy throttling"""
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    'playwright': True,
                    'playwright_page_methods': [
                        PageMethod('wait_for_selector', '[data-testid="marketplace_search_results"]', timeout=60000),
                        PageMethod('wait_for_timeout', 5000),  # Wait 5 seconds
                    ],
                    'playwright_include_page': True,
                },
                headers=self.get_random_headers(),
                callback=self.parse_search_results,
                dont_filter=True,
            )

    def parse_search_results(self, response):
        """Parse Facebook Marketplace search results"""
        self.logger.info(f'Parsing search results: {response.url}')
        
        # Check if we've hit request limit
        if self.request_count >= self.max_requests_per_session:
            self.logger.info('Hit request limit for Facebook Marketplace session')
            return
        
        # Extract listing links
        listing_links = response.css('[data-testid="marketplace_search_results"] a::attr(href)').getall()
        
        for link in listing_links:
            if link and link not in self.processed_urls:
                self.processed_urls.add(link)
                full_url = response.urljoin(link)
                
                # Heavy delay between requests
                time.sleep(random.randint(60, 120))
                
                yield scrapy.Request(
                    full_url,
                    meta={
                        'playwright': True,
                        'playwright_page_methods': [
                            PageMethod('wait_for_selector', '[data-testid="marketplace_listing"]', timeout=60000),
                            PageMethod('wait_for_timeout', 3000),
                        ],
                    },
                    headers=self.get_random_headers(),
                    callback=self.parse_listing_detail,
                    dont_filter=True,
                )
                
                self.request_count += 1
                
                # Break if we've hit the limit
                if self.request_count >= self.max_requests_per_session:
                    break

    def parse_listing_detail(self, response):
        """Parse individual listing detail page"""
        self.logger.info(f'Parsing listing detail: {response.url}')
        
        try:
            item = self.extract_listing_data(response)
            if item and self.is_laser_equipment(item):
                yield item
        except Exception as e:
            self.logger.error(f'Error extracting listing data: {e}')

    def extract_listing_data(self, response):
        """Extract listing data from detail page"""
        try:
            # Extract basic information
            title = response.css('[data-testid="marketplace_listing_title"]::text').get() or response.css('h1::text').get()
            description = response.css('[data-testid="marketplace_listing_description"]::text').get() or response.css('.description::text').get()
            
            # Extract price information
            price_text = response.css('[data-testid="marketplace_listing_price"]::text').get() or response.css('.price::text').get()
            
            # Extract condition
            condition = response.css('[data-testid="marketplace_listing_condition"]::text').get() or response.css('.condition::text').get()
            
            # Extract location
            location = response.css('[data-testid="marketplace_listing_location"]::text').get() or response.css('.location::text').get()
            
            # Extract seller information
            seller = response.css('[data-testid="marketplace_listing_seller"]::text').get() or response.css('.seller::text').get()
            
            # Extract images
            images = response.css('[data-testid="marketplace_listing_image"] img::attr(src)').getall()
            
            # Create item
            item = LaserListingItem()
            item['source_url'] = response.url
            item['title_raw'] = title
            item['description_raw'] = description
            item['asking_price'] = self.parse_price(price_text)
            item['condition'] = self.normalize_condition(condition)
            item['images'] = [response.urljoin(img) for img in images]
            item['location_city'] = self.parse_location(location)
            item['seller_name'] = seller
            item['discovered_at'] = time.time()
            item['source_name'] = 'Facebook Marketplace'
            item['evasion_score'] = 100  # Placeholder, calculated in middleware
            item['scraped_legally'] = True
            
            return item
            
        except Exception as e:
            self.logger.error(f'Error extracting listing data: {e}')
            return None

    def parse_price(self, price_text):
        """Parse price text to float"""
        if not price_text:
            return None
        
        try:
            import re
            cleaned = re.sub(r'[^\d.]', '', price_text)
            if cleaned:
                return float(cleaned)
        except (ValueError, TypeError):
            pass
        
        return None

    def normalize_condition(self, condition_text):
        """Normalize condition text"""
        if not condition_text:
            return 'unknown'
        
        condition_mapping = {
            'excellent': 'excellent',
            'good': 'good',
            'fair': 'fair',
            'poor': 'poor',
            'used': 'used',
            'refurbished': 'refurbished',
            'as-is': 'as-is',
        }
        
        return condition_mapping.get(condition_text.lower(), 'unknown')

    def parse_location(self, location_text):
        """Parse location text"""
        if not location_text:
            return ''
        
        parts = location_text.split(',')
        return parts[0].strip() if parts else location_text.strip()

    def is_laser_equipment(self, item):
        """Check if item is laser equipment"""
        laser_keywords = [
            'laser', 'ipl', 'rf', 'hifu', 'cryolipolysis',
            'sciton', 'cynosure', 'cutera', 'candela', 'lumenis',
            'alma', 'inmode', 'btl', 'lutronic', 'bison',
            'aesthetic', 'cosmetic', 'dermatology', 'hair removal'
        ]
        
        text_to_check = f"{item.get('title_raw', '')} {item.get('description_raw', '')}".lower()
        
        return any(keyword in text_to_check for keyword in laser_keywords)

    def get_random_headers(self):
        """Generate random headers for Facebook"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }

    def closed(self, reason):
        """Called when spider closes"""
        self.logger.info(f'Facebook Marketplace spider closed: {reason}')
        self.logger.info(f'Processed {len(self.processed_urls)} unique URLs')
        self.logger.info(f'Made {self.request_count} requests in this session')
