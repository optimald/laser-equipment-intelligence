"""
LaserMatch.io spider for medical laser equipment inventory management system
Extracts all listed items from lasermatch.io for procurement intelligence
"""

import scrapy
import time
import random
import re
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
from scrapy_playwright.page import PageMethod
from laser_intelligence.pipelines.normalization import LaserListingItem


class LaserMatchSpider(scrapy.Spider):
    name = 'lasermatch'
    allowed_domains = ['lasermatch.io']
    
    # LaserMatch.io main pages and categories
    start_urls = [
        'https://lasermatch.io/',
        'https://lasermatch.io/inventory',
        'https://lasermatch.io/listings',
        'https://lasermatch.io/equipment',
        'https://lasermatch.io/medical-equipment',
        'https://lasermatch.io/laser-equipment',
        'https://lasermatch.io/aesthetic-equipment',
        'https://lasermatch.io/dental-equipment',
        'https://lasermatch.io/laboratory-equipment'
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
        'DOWNLOAD_DELAY': (2, 5),  # Moderate delays for inventory site
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 12,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 4,
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
        self.processed_items = set()
        
        # Laser equipment keywords for LaserMatch.io
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
            'nd:yag laser', 'erbium laser', 'ipl device', 'rf device',
            'laser hair removal', 'laser tattoo removal', 'laser skin resurfacing',
            'coolsculpting', 'venus legacy', 'ultraformer', 'ulthera',
            'laser equipment', 'laser system', 'laser machine', 'laser device',
            'aerolase', 'lightpod', 'agnes', 'rf device',
            'medical equipment', 'healthcare equipment', 'dental equipment',
            'aesthetic equipment', 'beauty equipment', 'spa equipment',
            'clinic equipment', 'practice equipment', 'surgery equipment'
        ]
    
    def start_requests(self):
        """Generate initial requests for LaserMatch.io listings"""
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    'playwright': True,
                    'playwright_page_methods': [
                        PageMethod('wait_for_selector', '.inventory-list, .equipment-list, .listing-grid, .item-grid, .product-grid', timeout=30000),
                        PageMethod('wait_for_timeout', 3000),
                        PageMethod('evaluate', 'window.scrollTo(0, document.body.scrollHeight)'),
                        PageMethod('wait_for_timeout', 2000),
                    ],
                },
                headers=self.get_random_headers(),
                callback=self.parse_inventory_list,
                dont_filter=True,
            )
    
    def parse_inventory_list(self, response):
        """Parse inventory list page for equipment items"""
        self.logger.info(f'Parsing inventory list: {response.url}')
        
        # Extract item links - try multiple selectors for LaserMatch.io
        item_links = []
        
        # Common item link patterns for LaserMatch.io
        selectors = [
            'a[href*="item"]::attr(href)',
            'a[href*="equipment"]::attr(href)',
            'a[href*="listing"]::attr(href)',
            'a[href*="product"]::attr(href)',
            'a[href*="inventory"]::attr(href)',
            '.inventory-item a::attr(href)',
            '.equipment-item a::attr(href)',
            '.listing-item a::attr(href)',
            '.product-item a::attr(href)',
            '.item-card a::attr(href)',
            '.equipment-card a::attr(href)',
            '.listing-card a::attr(href)',
            '.product-card a::attr(href)',
            '.inventory-link::attr(href)',
            '.equipment-link::attr(href)',
            '.listing-link::attr(href)',
            '.product-link::attr(href)',
            'h3 a::attr(href)',
            'h2 a::attr(href)',
            '.item-title a::attr(href)',
            '.equipment-title a::attr(href)',
            '.listing-title a::attr(href)',
            '.product-title a::attr(href)'
        ]
        
        for selector in selectors:
            links = response.css(selector).getall()
            item_links.extend(links)
        
        # Remove duplicates and filter valid URLs
        item_links = list(set([link for link in item_links if link and ('item' in link.lower() or 'equipment' in link.lower() or 'listing' in link.lower() or 'product' in link.lower() or 'inventory' in link.lower())]))
        
        self.logger.info(f'Found {len(item_links)} item links')
        
        for link in item_links:
            if link not in self.processed_items:
                self.processed_items.add(link)
                full_url = response.urljoin(link)
                
                yield scrapy.Request(
                    full_url,
                    meta={
                        'playwright': True,
                        'playwright_page_methods': [
                            PageMethod('wait_for_selector', '.item-details, .equipment-details, .listing-details, .product-details', timeout=30000),
                            PageMethod('wait_for_timeout', 2000),
                        ],
                    },
                    headers=self.get_random_headers(),
                    callback=self.parse_item_detail,
                    dont_filter=True,
                )
        
        # Also try to extract items directly from the list page
        self.extract_items_from_list_page(response)
        
        # Follow pagination
        next_page = response.css('.pagination .next::attr(href), .pager .next::attr(href), a[rel="next"]::attr(href), .page-next::attr(href), .load-more::attr(href)').get()
        if next_page:
            yield scrapy.Request(
                response.urljoin(next_page),
                meta={
                    'playwright': True,
                    'playwright_page_methods': [
                        PageMethod('wait_for_selector', '.inventory-list, .equipment-list, .listing-grid, .item-grid, .product-grid', timeout=30000),
                        PageMethod('wait_for_timeout', 3000),
                    ],
                },
                headers=self.get_random_headers(),
                callback=self.parse_inventory_list,
                dont_filter=True,
            )
    
    def extract_items_from_list_page(self, response):
        """Extract items directly from list page without following links"""
        self.logger.info(f'Extracting items from list page: {response.url}')
        
        # Try multiple selectors for item containers
        item_selectors = [
            '.inventory-item',
            '.equipment-item',
            '.listing-item',
            '.product-item',
            '.item-card',
            '.equipment-card',
            '.listing-card',
            '.product-card',
            '.item',
            '.equipment',
            '.listing',
            '.product',
            'tr[class*="item"]',
            'tr[class*="equipment"]',
            'tr[class*="listing"]',
            'div[class*="item"]',
            'div[class*="equipment"]',
            'div[class*="listing"]'
        ]
        
        items = []
        for selector in item_selectors:
            items.extend(response.css(selector))
        
        self.logger.info(f'Found {len(items)} items on list page')
        
        for item_element in items:
            try:
                item = self.extract_item_data_from_element(item_element, response)
                if item and self.is_laser_equipment(item):
                    yield item
            except Exception as e:
                self.logger.error(f'Error extracting item data from element: {e}')
    
    def parse_item_detail(self, response):
        """Parse individual item detail page"""
        self.logger.info(f'Parsing item detail: {response.url}')
        
        try:
            item = self.extract_item_data_from_detail_page(response)
            if item and self.is_laser_equipment(item):
                yield item
        except Exception as e:
            self.logger.error(f'Error extracting item data from detail page: {e}')
    
    def extract_item_data_from_element(self, item_element, response):
        """Extract data from item element on list page"""
        try:
            # Extract basic information
            title = item_element.css('.item-title::text, .equipment-title::text, .listing-title::text, .product-title::text, h3::text, h4::text').get()
            description = item_element.css('.item-description::text, .equipment-description::text, .listing-description::text, .product-description::text, .description::text').getall()
            description_text = ' '.join(description).strip()
            
            # Extract item ID
            item_id = item_element.css('.item-id::text, .equipment-id::text, .listing-id::text, .product-id::text').get()
            
            # Extract pricing
            price = item_element.css('.price::text, .cost::text, .value::text, .asking-price::text').get()
            
            # Extract condition
            condition = item_element.css('.condition::text, .item-condition::text, .equipment-condition::text').get()
            
            # Extract manufacturer/brand
            brand = item_element.css('.brand::text, .manufacturer::text, .make::text').get()
            model = item_element.css('.model::text, .model-number::text').get()
            
            # Extract location
            location = item_element.css('.location::text, .warehouse::text, .facility::text').get()
            
            # Extract images
            images = item_element.css('img::attr(src)').getall()
            
            # Extract availability status
            availability = item_element.css('.availability::text, .status::text, .inventory-status::text').get()
            
            # Create item
            item = LaserListingItem()
            item['source_url'] = response.url
            item['source_listing_id'] = item_id
            item['title_raw'] = title
            item['description_raw'] = description_text
            item['asking_price'] = self.parse_price(price)
            item['condition'] = self.normalize_condition(condition)
            item['images'] = [response.urljoin(img) for img in images]
            item['location_city'] = location
            item['brand'] = brand
            item['model'] = model
            item['availability'] = availability
            item['discovered_at'] = time.time()
            item['source_name'] = 'LaserMatch.io'
            item['evasion_score'] = 100  # Placeholder, calculated in middleware
            item['scraped_legally'] = True
            
            return item
            
        except Exception as e:
            self.logger.error(f'Error extracting item data from element: {e}')
            return None
    
    def extract_item_data_from_detail_page(self, response):
        """Extract data from item detail page"""
        try:
            # Extract title and description
            title = response.css('h1::text, .item-title::text, .equipment-title::text, .listing-title::text, .product-title::text').get()
            description = response.css('.item-description::text, .equipment-description::text, .listing-description::text, .product-description::text, .description::text').getall()
            description_text = ' '.join(description).strip()
            
            # Extract item ID
            item_id = response.css('.item-id::text, .equipment-id::text, .listing-id::text, .product-id::text').get()
            
            # Extract pricing
            asking_price = response.css('.asking-price::text, .price::text, .cost::text, .value::text').get()
            market_value = response.css('.market-value::text, .estimated-value::text, .appraisal::text').get()
            
            # Extract condition
            condition = response.css('.condition::text, .item-condition::text, .equipment-condition::text').get()
            
            # Extract specifications
            specs = response.css('.specifications::text, .item-specifications::text, .equipment-specifications::text, .details::text').getall()
            specs_text = ' '.join(specs).strip()
            
            # Extract images
            images = response.css('.item-images img::attr(src), .equipment-images img::attr(src), .gallery img::attr(src)').getall()
            
            # Extract location information
            location = response.css('.location::text, .warehouse::text, .facility::text, .storage::text').get()
            
            # Extract seller/consignor information
            consignor = response.css('.consignor::text, .seller::text, .owner::text, .client::text').get()
            contact = response.css('.contact::text, .contact-info::text, .sales-contact::text').get()
            
            # Extract additional details
            brand = response.css('.brand::text, .manufacturer::text, .make::text').get()
            model = response.css('.model::text, .model-number::text, .model-name::text').get()
            serial = response.css('.serial::text, .serial-number::text, .serial-no::text').get()
            year = response.css('.year::text, .manufacture-year::text, .model-year::text').get()
            
            # Extract availability
            availability = response.css('.availability::text, .status::text, .inventory-status::text').get()
            
            # Extract category
            category = response.css('.category::text, .equipment-category::text, .type::text').get()
            
            # Create item
            item = LaserListingItem()
            item['source_url'] = response.url
            item['source_listing_id'] = item_id
            item['title_raw'] = title
            item['description_raw'] = f"{description_text} {specs_text}".strip()
            item['asking_price'] = self.parse_price(asking_price)
            item['est_wholesale'] = self.parse_price(market_value)
            item['condition'] = self.normalize_condition(condition)
            item['images'] = [response.urljoin(img) for img in images]
            item['seller_name'] = consignor
            item['location_city'] = location
            item['brand'] = brand
            item['model'] = model
            item['serial_number'] = serial
            item['year'] = self.parse_year(year)
            item['seller_contact'] = contact
            item['availability'] = availability
            item['category'] = category
            item['discovered_at'] = time.time()
            item['source_name'] = 'LaserMatch.io'
            item['evasion_score'] = 100  # Placeholder, calculated in middleware
            item['scraped_legally'] = True
            
            return item
            
        except Exception as e:
            self.logger.error(f'Error extracting item data from detail page: {e}')
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
    
    def parse_year(self, year_text):
        """Parse year text to integer"""
        if not year_text:
            return None
        
        try:
            # Extract year from text
            year_match = re.search(r'\b(19|20)\d{2}\b', year_text)
            if year_match:
                return int(year_match.group())
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
            'unknown': 'unknown',
            'available': 'good',
            'unavailable': 'unknown'
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
        self.logger.info(f'LaserMatch.io spider closed: {reason}')
        self.logger.info(f'Processed {len(self.processed_urls)} unique URLs')
        self.logger.info(f'Processed {len(self.processed_items)} unique items')
