"""
Asset Recovery Services spider for liquidation opportunities and medical equipment recovery
"""

import scrapy
import time
import random
import re
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
from scrapy_playwright.page import PageMethod
from laser_intelligence.pipelines.normalization import LaserListingItem


class AssetRecoveryServicesSpider(scrapy.Spider):
    name = 'asset_recovery_services'
    allowed_domains = ['assetrecoveryservices.com']
    
    # Asset recovery and liquidation opportunities
    start_urls = [
        'https://www.assetrecoveryservices.com/inventory',
        'https://www.assetrecoveryservices.com/inventory?category=medical-equipment',
        'https://www.assetrecoveryservices.com/inventory?category=healthcare-equipment',
        'https://www.assetrecoveryservices.com/inventory?category=laboratory-equipment',
        'https://www.assetrecoveryservices.com/inventory?category=dental-equipment',
        'https://www.assetrecoveryservices.com/inventory?category=aesthetic-equipment',
        'https://www.assetrecoveryservices.com/liquidations',
        'https://www.assetrecoveryservices.com/auctions',
        'https://www.assetrecoveryservices.com/repossessions'
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
        'DOWNLOAD_DELAY': (2, 6),  # Moderate delays
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 10,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 3,
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
        self.processed_liquidations = set()
        
        # Laser equipment keywords for Asset Recovery Services
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
            'laser equipment', 'laser system', 'laser machine', 'laser device'
        ]
    
    def start_requests(self):
        """Generate initial requests for asset recovery listings"""
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    'playwright': True,
                    'playwright_page_methods': [
                        PageMethod('wait_for_selector', '.inventory-list, .asset-list, .equipment-list, .liquidation-list', timeout=30000),
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
        """Parse inventory list page for asset recovery items"""
        self.logger.info(f'Parsing inventory list: {response.url}')
        
        # Extract asset links - try multiple selectors
        asset_links = []
        
        # Common asset link patterns for Asset Recovery Services
        selectors = [
            'a[href*="inventory"]::attr(href)',
            'a[href*="asset"]::attr(href)',
            'a[href*="equipment"]::attr(href)',
            'a[href*="liquidation"]::attr(href)',
            'a[href*="item"]::attr(href)',
            '.inventory-item a::attr(href)',
            '.asset-item a::attr(href)',
            '.equipment-item a::attr(href)',
            '.liquidation-item a::attr(href)',
            '.inventory-link::attr(href)',
            '.asset-link::attr(href)',
            '.equipment-link::attr(href)',
            'h3 a::attr(href)',
            'h2 a::attr(href)',
            '.item-title a::attr(href)',
            '.asset-title a::attr(href)'
        ]
        
        for selector in selectors:
            links = response.css(selector).getall()
            asset_links.extend(links)
        
        # Remove duplicates and filter valid URLs
        asset_links = list(set([link for link in asset_links if link and ('inventory' in link.lower() or 'asset' in link.lower() or 'equipment' in link.lower() or 'item' in link.lower())]))
        
        self.logger.info(f'Found {len(asset_links)} asset links')
        
        for link in asset_links:
            if link not in self.processed_liquidations:
                self.processed_liquidations.add(link)
                full_url = response.urljoin(link)
                
                yield scrapy.Request(
                    full_url,
                    meta={
                        'playwright': True,
                        'playwright_page_methods': [
                            PageMethod('wait_for_selector', '.asset-details, .equipment-details, .inventory-details, .item-details', timeout=30000),
                            PageMethod('wait_for_timeout', 2000),
                        ],
                    },
                    headers=self.get_random_headers(),
                    callback=self.parse_asset_detail,
                    dont_filter=True,
                )
        
        # Follow pagination
        next_page = response.css('.pagination .next::attr(href), .pager .next::attr(href), a[rel="next"]::attr(href), .page-next::attr(href)').get()
        if next_page:
            yield scrapy.Request(
                response.urljoin(next_page),
                meta={
                    'playwright': True,
                    'playwright_page_methods': [
                        PageMethod('wait_for_selector', '.inventory-list, .asset-list, .equipment-list, .liquidation-list', timeout=30000),
                        PageMethod('wait_for_timeout', 3000),
                    ],
                },
                headers=self.get_random_headers(),
                callback=self.parse_inventory_list,
                dont_filter=True,
            )
    
    def parse_asset_detail(self, response):
        """Parse individual asset detail page"""
        self.logger.info(f'Parsing asset detail: {response.url}')
        
        try:
            item = self.extract_asset_data(response)
            if item and self.is_laser_equipment(item):
                yield item
        except Exception as e:
            self.logger.error(f'Error extracting asset data: {e}')
    
    def extract_asset_data(self, response):
        """Extract data from asset detail page"""
        try:
            # Extract title and description
            title = response.css('h1::text, .asset-title::text, .equipment-title::text, .item-title::text').get()
            description = response.css('.asset-description::text, .equipment-description::text, .item-description::text, .description::text').getall()
            description_text = ' '.join(description).strip()
            
            # Extract asset ID
            asset_id = response.css('.asset-id::text, .inventory-number::text, .equipment-id::text').get()
            
            # Extract pricing
            asking_price = response.css('.asking-price::text, .price::text, .cost::text, .value::text').get()
            estimated_value = response.css('.estimated-value::text, .appraisal::text, .market-value::text').get()
            
            # Extract condition
            condition = response.css('.condition::text, .asset-condition::text, .equipment-condition::text').get()
            
            # Extract specifications
            specs = response.css('.specifications::text, .asset-specifications::text, .equipment-specifications::text, .details::text').getall()
            specs_text = ' '.join(specs).strip()
            
            # Extract images
            images = response.css('.asset-images img::attr(src), .equipment-images img::attr(src), .gallery img::attr(src)').getall()
            
            # Extract location information
            location = response.css('.location::text, .warehouse::text, .facility::text, .storage::text').get()
            pickup_location = response.css('.pickup-location::text, .pickup::text').get()
            
            # Extract seller/consignor information
            consignor = response.css('.consignor::text, .seller::text, .owner::text, .client::text').get()
            
            # Extract asset recovery details
            recovery_type = response.css('.recovery-type::text, .liquidation-type::text, .asset-type::text').get()
            recovery_reason = response.css('.recovery-reason::text, .liquidation-reason::text, .reason::text').get()
            
            # Extract additional details
            brand = response.css('.brand::text, .manufacturer::text, .make::text').get()
            model = response.css('.model::text, .model-number::text, .model-name::text').get()
            serial = response.css('.serial::text, .serial-number::text, .serial-no::text').get()
            year = response.css('.year::text, .manufacture-year::text, .model-year::text').get()
            
            # Extract contact information
            contact = response.css('.contact::text, .contact-info::text, .sales-contact::text').get()
            phone = response.css('.phone::text, .telephone::text, .contact-phone::text').get()
            email = response.css('.email::text, .contact-email::text').get()
            
            # Extract availability
            availability = response.css('.availability::text, .status::text, .inventory-status::text').get()
            
            # Create item
            item = LaserListingItem()
            item['source_url'] = response.url
            item['source_listing_id'] = asset_id
            item['title_raw'] = title
            item['description_raw'] = f"{description_text} {specs_text}".strip()
            item['asking_price'] = self.parse_price(asking_price)
            item['est_wholesale'] = self.parse_price(estimated_value)
            item['condition'] = self.normalize_condition(condition)
            item['images'] = [response.urljoin(img) for img in images]
            item['location_city'] = location or pickup_location
            item['seller_name'] = consignor
            item['brand'] = brand
            item['model'] = model
            item['serial_number'] = serial
            item['year'] = self.parse_year(year)
            item['seller_contact'] = contact or phone or email
            item['recovery_type'] = recovery_type
            item['recovery_reason'] = recovery_reason
            item['availability'] = availability
            item['discovered_at'] = time.time()
            item['source_name'] = 'Asset Recovery Services'
            item['evasion_score'] = 100  # Placeholder, calculated in middleware
            item['scraped_legally'] = True
            
            return item
            
        except Exception as e:
            self.logger.error(f'Error extracting asset data: {e}')
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
            'repossessed': 'used',
            'liquidation': 'used',
            'surplus': 'used'
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
        self.logger.info(f'Asset Recovery Services spider closed: {reason}')
        self.logger.info(f'Processed {len(self.processed_urls)} unique URLs')
        self.logger.info(f'Processed {len(self.processed_liquidations)} unique liquidations')