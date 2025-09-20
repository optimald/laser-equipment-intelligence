"""
LabX spider for laboratory equipment marketplace
"""

import scrapy
import time
import random
from playwright.async_api import async_playwright
from scrapy_playwright.page import PageMethod
from laser_intelligence.pipelines.normalization import LaserListingItem


class LabXSpider(scrapy.Spider):
    name = 'labx'
    allowed_domains = ['labx.com']
    start_urls = [
        'https://www.labx.com/search?q=laser+equipment',
        'https://www.labx.com/search?q=medical+laser',
        'https://www.labx.com/search?q=aesthetic+laser',
        'https://www.labx.com/search?q=sciton',
        'https://www.labx.com/search?q=cynosure',
        'https://www.labx.com/search?q=cutera',
        'https://www.labx.com/search?q=candela',
        'https://www.labx.com/search?q=lumenis',
        'https://www.labx.com/search?q=alma',
        'https://www.labx.com/search?q=inmode'
    ]

    custom_settings = {
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 60000,
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            'headless': True,
            'args': [
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        },
        'DOWNLOAD_DELAY': (3, 8),
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 12,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 3,
        'DOWNLOADER_MIDDLEWARES': {
            'laser_intelligence.middleware.evasion.EvasionMiddleware': 543,
            'laser_intelligence.middleware.proxy.ProxyMiddleware': 544,
            'laser_intelligence.middleware.captcha.CaptchaMiddleware': 545,
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

    def start_requests(self):
        """Generate initial requests"""
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    'playwright': True,
                    'playwright_page_methods': [
                        PageMethod('wait_for_selector', '.search-result', timeout=30000),
                        PageMethod('wait_for_timeout', 2000),
                    ],
                },
                headers=self.get_random_headers(),
                callback=self.parse_search_results,
                dont_filter=True,
            )

    def parse_search_results(self, response):
        """Parse LabX search results"""
        self.logger.info(f'Parsing search results: {response.url}')
        
        # Extract listing links
        listing_links = response.css('.search-result a::attr(href)').getall()
        
        for link in listing_links:
            if link and link not in self.processed_urls:
                self.processed_urls.add(link)
                full_url = response.urljoin(link)
                
                yield scrapy.Request(
                    full_url,
                    meta={
                        'playwright': True,
                        'playwright_page_methods': [
                            PageMethod('wait_for_selector', '.listing-details', timeout=30000),
                            PageMethod('wait_for_timeout', 2000),
                        ],
                    },
                    headers=self.get_random_headers(),
                    callback=self.parse_listing_detail,
                    dont_filter=True,
                )

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
            title = response.css('.listing-title::text').get() or response.css('h1::text').get()
            description = response.css('.listing-description::text').get() or response.css('.description::text').get()
            
            # Extract price information
            price_text = response.css('.listing-price::text').get() or response.css('.price::text').get()
            
            # Extract condition
            condition = response.css('.listing-condition::text').get() or response.css('.condition::text').get()
            
            # Extract location
            location = response.css('.listing-location::text').get() or response.css('.location::text').get()
            
            # Extract seller information
            seller = response.css('.listing-seller::text').get() or response.css('.seller::text').get()
            
            # Extract images
            images = response.css('.listing-images img::attr(src)').getall()
            
            # Extract specifications
            specifications = response.css('.listing-specs::text').get() or response.css('.specifications::text').get()
            
            # Create item
            item = LaserListingItem()
            item['source_url'] = response.url
            item['title_raw'] = title
            item['description_raw'] = f"{description} {specifications}".strip()
            item['asking_price'] = self.parse_price(price_text)
            item['condition'] = self.normalize_condition(condition)
            item['images'] = [response.urljoin(img) for img in images]
            item['location_city'] = self.parse_location(location)
            item['seller_name'] = seller
            item['discovered_at'] = time.time()
            item['source_name'] = 'LabX'
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
        """Generate random headers"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        
        return {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }

    def closed(self, reason):
        """Called when spider closes"""
        self.logger.info(f'LabX spider closed: {reason}')
        self.logger.info(f'Processed {len(self.processed_urls)} unique URLs')
