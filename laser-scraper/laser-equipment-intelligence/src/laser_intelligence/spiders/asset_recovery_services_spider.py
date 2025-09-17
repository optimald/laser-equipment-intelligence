"""
Asset Recovery Services spider for asset recovery and liquidation
"""

import scrapy
import time
import random
from playwright.async_api import async_playwright
from scrapy_playwright.page import PageMethod
from laser_intelligence.pipelines.normalization import LaserListingItem


class AssetRecoveryServicesSpider(scrapy.Spider):
    name = 'asset_recovery_services'
    allowed_domains = ['assetrecoveryservices.com']
    start_urls = [
        'https://www.assetrecoveryservices.com/auctions',
        'https://www.assetrecoveryservices.com/auctions?category=medical-equipment',
        'https://www.assetrecoveryservices.com/auctions?category=laser-equipment'
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
        'DOWNLOAD_DELAY': (2, 6),
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
                        PageMethod('wait_for_selector', '.auction-item', timeout=30000),
                        PageMethod('wait_for_timeout', 2000),
                    ],
                },
                headers=self.get_random_headers(),
                callback=self.parse_auction_list,
                dont_filter=True,
            )

    def parse_auction_list(self, response):
        """Parse auction list page"""
        self.logger.info(f'Parsing auction list: {response.url}')
        
        # Extract auction links
        auction_links = response.css('.auction-item a::attr(href)').getall()
        
        for link in auction_links:
            if link and link not in self.processed_urls:
                self.processed_urls.add(link)
                full_url = response.urljoin(link)
                
                yield scrapy.Request(
                    full_url,
                    meta={
                        'playwright': True,
                        'playwright_page_methods': [
                            PageMethod('wait_for_selector', '.lot-item', timeout=30000),
                            PageMethod('wait_for_timeout', 2000),
                        ],
                    },
                    headers=self.get_random_headers(),
                    callback=self.parse_auction_catalog,
                    dont_filter=True,
                )

    def parse_auction_catalog(self, response):
        """Parse individual auction catalog"""
        self.logger.info(f'Parsing auction catalog: {response.url}')
        
        # Extract lot items
        lot_items = response.css('.lot-item')
        
        for lot in lot_items:
            try:
                item = self.extract_lot_data(lot, response)
                if item and self.is_laser_equipment(item):
                    yield item
            except Exception as e:
                self.logger.error(f'Error extracting lot data: {e}')
                continue

    def extract_lot_data(self, lot_element, response):
        """Extract data from lot element"""
        try:
            # Extract basic information
            title = lot_element.css('.lot-title::text').get() or lot_element.css('h3::text').get()
            description = lot_element.css('.lot-description::text').get() or lot_element.css('.description::text').get()
            
            # Extract price information
            price_text = lot_element.css('.lot-price::text').get() or lot_element.css('.price::text').get()
            estimate_text = lot_element.css('.lot-estimate::text').get() or lot_element.css('.estimate::text').get()
            
            # Extract lot number
            lot_number = lot_element.css('.lot-number::text').get() or lot_element.css('.lot-id::text').get()
            
            # Extract images
            images = lot_element.css('img::attr(src)').getall()
            
            # Extract location
            location = lot_element.css('.lot-location::text').get() or lot_element.css('.location::text').get()
            
            # Extract auction end time
            end_time = lot_element.css('.auction-end::text').get() or lot_element.css('.end-time::text').get()
            
            # Create item
            item = LaserListingItem()
            item['source_url'] = response.url
            item['source_listing_id'] = lot_number
            item['title_raw'] = title
            item['description_raw'] = description
            item['asking_price'] = self.parse_price(price_text)
            item['reserve_price'] = self.parse_price(estimate_text)
            item['images'] = [response.urljoin(img) for img in images]
            item['location_city'] = self.parse_location(location)
            item['auction_end_ts'] = self.parse_auction_end_time(end_time)
            item['discovered_at'] = time.time()
            item['source_name'] = 'Asset Recovery Services'
            item['evasion_score'] = 100  # Placeholder, calculated in middleware
            item['scraped_legally'] = True
            
            return item
            
        except Exception as e:
            self.logger.error(f'Error extracting lot data: {e}')
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

    def parse_location(self, location_text):
        """Parse location text"""
        if not location_text:
            return ''
        
        parts = location_text.split(',')
        return parts[0].strip() if parts else location_text.strip()

    def parse_auction_end_time(self, end_time_text):
        """Parse auction end time to timestamp"""
        if not end_time_text:
            return None
        
        try:
            # This would need more sophisticated parsing based on Asset Recovery Services' format
            return None
        except:
            return None

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
        self.logger.info(f'Asset Recovery Services spider closed: {reason}')
        self.logger.info(f'Processed {len(self.processed_urls)} unique URLs')
