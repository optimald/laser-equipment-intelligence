"""
Iron Horse Auction spider for high-value bankruptcy sales and medical equipment auctions
"""

import scrapy
import time
import random
import re
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
from scrapy_playwright.page import PageMethod
from laser_intelligence.pipelines.normalization import LaserListingItem


class IronHorseAuctionSpider(scrapy.Spider):
    name = 'iron_horse_auction'
    allowed_domains = ['ironhorseauction.com']
    
    # High-value bankruptcy and medical equipment auctions
    start_urls = [
        'https://www.ironhorseauction.com/auctions',
        'https://www.ironhorseauction.com/auctions?category=medical-equipment',
        'https://www.ironhorseauction.com/auctions?category=healthcare-equipment',
        'https://www.ironhorseauction.com/auctions?category=laboratory-equipment',
        'https://www.ironhorseauction.com/auctions?category=dental-equipment',
        'https://www.ironhorseauction.com/auctions?category=aesthetic-equipment'
    ]
    
    custom_settings = {
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 90000,
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            'headless': True,
            'args': [
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--no-sandbox',
                '--disable-dev-shm-usage'
            ]
        },
        'DOWNLOAD_DELAY': (3, 8),  # Medium delays for auction site
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 8,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
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
        self.processed_auctions = set()
        
        # Laser equipment keywords for Iron Horse Auction
        self.laser_keywords = [
            'laser', 'ipl', 'rf', 'hifu', 'cryolipolysis',
            'sciton', 'cynosure', 'cutera', 'candela', 'lumenis',
            'alma', 'inmode', 'btl', 'lutronic', 'bison',
            'joule', 'picosure', 'picoway', 'gentlemax',
            'm22', 'bbl', 'secret rf', 'morpheus8', 'emsculpt',
            'excel v', 'xeo', 'harmony', 'soprano', 'opus',
            'aesthetic', 'cosmetic', 'dermatology', 'hair removal',
            'skin treatment', 'body contouring', 'tattoo removal',
            'medical laser', 'surgical laser', 'therapeutic laser',
            'fractional laser', 'co2 laser', 'diode laser', 'alexandrite laser',
            'nd:yag laser', 'erbium laser', 'ipl device', 'rf device'
        ]
    
    def start_requests(self):
        """Generate initial requests for auction listings"""
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    'playwright': True,
                    'playwright_page_methods': [
                        PageMethod('wait_for_selector', '.auction-list, .auction-item, .catalog-list', timeout=30000),
                        PageMethod('wait_for_timeout', 3000),
                        PageMethod('evaluate', 'window.scrollTo(0, document.body.scrollHeight)'),
                        PageMethod('wait_for_timeout', 2000),
                    ],
                },
                headers=self.get_random_headers(),
                callback=self.parse_auction_list,
                dont_filter=True,
            )
    
    def parse_auction_list(self, response):
        """Parse auction list page for individual auctions"""
        self.logger.info(f'Parsing auction list: {response.url}')
        
        # Extract auction links - try multiple selectors
        auction_links = []
        
        # Common auction link patterns
        selectors = [
            'a[href*="auction"]::attr(href)',
            'a[href*="catalog"]::attr(href)',
            'a[href*="sale"]::attr(href)',
            '.auction-item a::attr(href)',
            '.catalog-item a::attr(href)',
            '.auction-link::attr(href)',
            '.lot-link::attr(href)',
            'h3 a::attr(href)',
            'h2 a::attr(href)'
        ]
        
        for selector in selectors:
            links = response.css(selector).getall()
            auction_links.extend(links)
        
        # Remove duplicates and filter valid URLs
        auction_links = list(set([link for link in auction_links if link and ('auction' in link.lower() or 'catalog' in link.lower() or 'sale' in link.lower())]))
        
        self.logger.info(f'Found {len(auction_links)} auction links')
        
        for link in auction_links:
            if link not in self.processed_auctions:
                self.processed_auctions.add(link)
                full_url = response.urljoin(link)
                
                yield scrapy.Request(
                    full_url,
                    meta={
                        'playwright': True,
                        'playwright_page_methods': [
                            PageMethod('wait_for_selector', '.lot-item, .auction-lot, .item, .listing', timeout=30000),
                            PageMethod('wait_for_timeout', 2000),
                        ],
                    },
                    headers=self.get_random_headers(),
                    callback=self.parse_auction_catalog,
                    dont_filter=True,
                )
        
        # Follow pagination
        next_page = response.css('.pagination .next::attr(href), .pager .next::attr(href), a[rel="next"]::attr(href)').get()
        if next_page:
            yield scrapy.Request(
                response.urljoin(next_page),
                meta={
                    'playwright': True,
                    'playwright_page_methods': [
                        PageMethod('wait_for_selector', '.auction-list, .auction-item, .catalog-list', timeout=30000),
                        PageMethod('wait_for_timeout', 3000),
                    ],
                },
                headers=self.get_random_headers(),
                callback=self.parse_auction_list,
                dont_filter=True,
            )
    
    def parse_auction_catalog(self, response):
        """Parse individual auction catalog for laser equipment lots"""
        self.logger.info(f'Parsing auction catalog: {response.url}')
        
        # Extract auction metadata
        auction_title = response.css('h1::text, .auction-title::text, .catalog-title::text').get()
        auction_date = response.css('.auction-date::text, .sale-date::text, .date::text').get()
        auction_location = response.css('.auction-location::text, .location::text, .venue::text').get()
        
        # Extract lot items - try multiple selectors
        lot_selectors = [
            '.lot-item',
            '.auction-lot', 
            '.item',
            '.listing',
            '.catalog-item',
            '.inventory-item',
            'tr[class*="lot"]',
            'div[class*="lot"]'
        ]
        
        lots = []
        for selector in lot_selectors:
            lots.extend(response.css(selector))
        
        self.logger.info(f'Found {len(lots)} lots in auction')
        
        for lot in lots:
            try:
                item = self.extract_lot_data(lot, response, auction_title, auction_date, auction_location)
                if item and self.is_laser_equipment(item):
                    yield item
            except Exception as e:
                self.logger.error(f'Error extracting lot data: {e}')
        
        # Look for lot detail pages
        lot_links = response.css('a[href*="lot"]::attr(href), a[href*="item"]::attr(href)').getall()
        for link in lot_links:
            if link not in self.processed_urls:
                self.processed_urls.add(link)
                full_url = response.urljoin(link)
                
                yield scrapy.Request(
                    full_url,
                    meta={
                        'playwright': True,
                        'playwright_page_methods': [
                            PageMethod('wait_for_selector', '.lot-details, .item-details, .description', timeout=30000),
                            PageMethod('wait_for_timeout', 2000),
                        ],
                        'auction_title': auction_title,
                        'auction_date': auction_date,
                        'auction_location': auction_location,
                    },
                    headers=self.get_random_headers(),
                    callback=self.parse_lot_detail,
                    dont_filter=True,
                )
    
    def parse_lot_detail(self, response):
        """Parse individual lot detail page"""
        self.logger.info(f'Parsing lot detail: {response.url}')
        
        try:
            auction_title = response.meta.get('auction_title', '')
            auction_date = response.meta.get('auction_date', '')
            auction_location = response.meta.get('auction_location', '')
            
            item = self.extract_detail_page_data(response, auction_title, auction_date, auction_location)
            if item and self.is_laser_equipment(item):
                yield item
        except Exception as e:
            self.logger.error(f'Error extracting detail page data: {e}')
    
    def extract_lot_data(self, lot_element, response, auction_title, auction_date, auction_location):
        """Extract data from lot element"""
        try:
            # Extract lot number
            lot_number = lot_element.css('.lot-number::text, .item-number::text, .inventory-number::text').get()
            
            # Extract title/description
            title = lot_element.css('.lot-title::text, .item-title::text, h3::text, h4::text').get()
            description = lot_element.css('.lot-description::text, .item-description::text, .description::text').getall()
            description_text = ' '.join(description).strip()
            
            # Extract pricing
            estimate = lot_element.css('.estimate::text, .lot-estimate::text, .price-estimate::text').get()
            current_bid = lot_element.css('.current-bid::text, .bid-amount::text, .high-bid::text').get()
            reserve = lot_element.css('.reserve::text, .reserve-price::text').get()
            
            # Extract condition
            condition = lot_element.css('.condition::text, .lot-condition::text').get()
            
            # Extract images
            images = lot_element.css('img::attr(src)').getall()
            
            # Create item
            item = LaserListingItem()
            item['source_url'] = response.url
            item['source_listing_id'] = lot_number
            item['title_raw'] = title
            item['description_raw'] = description_text
            item['asking_price'] = self.parse_price(current_bid) or self.parse_price(estimate)
            item['reserve_price'] = self.parse_price(reserve)
            item['condition'] = self.normalize_condition(condition)
            item['images'] = [response.urljoin(img) for img in images]
            item['auction_title'] = auction_title
            item['auction_date'] = auction_date
            item['auction_location'] = auction_location
            item['discovered_at'] = time.time()
            item['source_name'] = 'Iron Horse Auction'
            item['evasion_score'] = 100  # Placeholder, calculated in middleware
            item['scraped_legally'] = True
            
            return item
            
        except Exception as e:
            self.logger.error(f'Error extracting lot data: {e}')
            return None
    
    def extract_detail_page_data(self, response, auction_title, auction_date, auction_location):
        """Extract data from detail page"""
        try:
            # Extract title and description
            title = response.css('h1::text, .lot-title::text, .item-title::text').get()
            description = response.css('.lot-description::text, .item-description::text, .description::text').getall()
            description_text = ' '.join(description).strip()
            
            # Extract lot number
            lot_number = response.css('.lot-number::text, .item-number::text').get()
            
            # Extract pricing
            estimate = response.css('.estimate::text, .lot-estimate::text').get()
            current_bid = response.css('.current-bid::text, .bid-amount::text').get()
            reserve = response.css('.reserve::text, .reserve-price::text').get()
            
            # Extract condition
            condition = response.css('.condition::text, .lot-condition::text').get()
            
            # Extract specifications
            specs = response.css('.specifications::text, .lot-specifications::text').getall()
            specs_text = ' '.join(specs).strip()
            
            # Extract images
            images = response.css('.lot-images img::attr(src), .item-images img::attr(src)').getall()
            
            # Extract seller information
            seller = response.css('.seller::text, .consignor::text').get()
            
            # Extract location
            location = response.css('.location::text, .pickup-location::text').get()
            
            # Create item
            item = LaserListingItem()
            item['source_url'] = response.url
            item['source_listing_id'] = lot_number
            item['title_raw'] = title
            item['description_raw'] = f"{description_text} {specs_text}".strip()
            item['asking_price'] = self.parse_price(current_bid) or self.parse_price(estimate)
            item['reserve_price'] = self.parse_price(reserve)
            item['condition'] = self.normalize_condition(condition)
            item['images'] = [response.urljoin(img) for img in images]
            item['seller_name'] = seller
            item['location_city'] = location or auction_location
            item['auction_title'] = auction_title
            item['auction_date'] = auction_date
            item['auction_location'] = auction_location
            item['discovered_at'] = time.time()
            item['source_name'] = 'Iron Horse Auction'
            item['evasion_score'] = 100  # Placeholder, calculated in middleware
            item['scraped_legally'] = True
            
            return item
            
        except Exception as e:
            self.logger.error(f'Error extracting detail page data: {e}')
            return None
    
    def parse_price(self, price_text):
        """Parse price text to float"""
        if not price_text:
            return None
        
        try:
            # Remove common price prefixes/suffixes
            cleaned = re.sub(r'[^\d.,]', '', price_text)
            cleaned = cleaned.replace(',', '')
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
            'working': 'good',
            'non-working': 'poor',
            'unknown': 'unknown'
        }
        
        return condition_mapping.get(condition_text.lower(), 'unknown')
    
    def is_laser_equipment(self, item):
        """Check if item is laser equipment"""
        text_to_check = f"{item.get('title_raw', '')} {item.get('description_raw', '')}".lower()
        
        return any(keyword.lower() in text_to_check for keyword in self.laser_keywords)
    
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
        self.logger.info(f'Iron Horse Auction spider closed: {reason}')
        self.logger.info(f'Processed {len(self.processed_urls)} unique URLs')
        self.logger.info(f'Processed {len(self.processed_auctions)} unique auctions')