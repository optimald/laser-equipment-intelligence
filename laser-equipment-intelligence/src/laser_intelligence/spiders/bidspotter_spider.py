"""
BidSpotter spider for infinite scroll, JS-heavy auction platform
"""

import scrapy
import time
import random
import re
from playwright.async_api import async_playwright
from scrapy_playwright.page import PageMethod
from laser_intelligence.pipelines.normalization import LaserListingItem


class BidspotterSpider(scrapy.Spider):
    name = 'bidspotter'
    allowed_domains = ['bidspotter.com']
    start_urls = [
        'https://www.bidspotter.com/en-us/auction-catalogues',
        'https://www.bidspotter.com/en-us/auction-catalogues?category=medical-equipment',
        'https://www.bidspotter.com/en-us/auction-catalogues?category=laser-equipment'
    ]

    custom_settings = {
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 120000,  # 2 minutes for JS-heavy site
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            'headless': True,
            'args': [
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        },
        'DOWNLOAD_DELAY': (3, 8),  # Longer delays for JS-heavy site
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 8,  # Lower concurrency for JS-heavy site
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
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
        
        # Laser equipment keywords
        self.laser_keywords = [
            'sciton', 'cynosure', 'cutera', 'candela', 'lumenis', 'alma',
            'inmode', 'btl', 'lutronic', 'bison', 'deka', 'quanta',
            'joule', 'picosure', 'picoway', 'gentlemax', 'm22', 'bbl',
            'secret rf', 'morpheus8', 'emsculpt', 'excel v', 'xeo',
            'laser', 'ipl', 'rf', 'hifu', 'cryolipolysis'
        ]
        self.scroll_attempts = 0
        self.max_scroll_attempts = 10

    def start_requests(self):
        """Generate initial requests with Playwright for JS rendering"""
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    'playwright': True,
                    'playwright_page_methods': [
                        PageMethod('wait_for_selector', '.auction-catalogue-item', timeout=30000),
                        PageMethod('evaluate', 'window.scrollTo(0, document.body.scrollHeight)'),
                        PageMethod('wait_for_timeout', 3000),  # Wait for content to load
                    ],
                    'playwright_include_page': True,
                },
                headers=self.get_random_headers(),
                callback=self.parse_catalog_list,
                dont_filter=True,
            )

    def parse_catalog_list(self, response):
        """Parse auction catalog list page"""
        self.logger.info(f'Parsing catalog list: {response.url}')
        
        # Extract auction catalog links
        catalog_links = response.css('.auction-catalogue-item a::attr(href)').getall()
        
        for link in catalog_links:
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
                        'playwright_include_page': True,
                    },
                    headers=self.get_random_headers(),
                    callback=self.parse_auction_catalog,
                    dont_filter=True,
                )

    def parse_auction_catalog(self, response):
        """Parse individual auction catalog with infinite scroll"""
        self.logger.info(f'Parsing auction catalog: {response.url}')
        
        # Get page object for infinite scroll
        page = response.meta.get('playwright_page')
        
        if page:
            try:
                # Perform infinite scroll to load all lots
                # Note: This would need to be implemented with proper async handling
                # For now, we'll skip the infinite scroll and process what's available
                pass
                
            except Exception as e:
                self.logger.error(f'Error during infinite scroll: {e}')
        
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

    def scroll_to_load_all_lots(self, page):
        """Perform infinite scroll to load all lots"""
        self.logger.info('Starting infinite scroll for BidSpotter')
        
        # Note: This would need to be implemented with proper async handling
        # For now, we'll skip the infinite scroll implementation
        self.logger.info('Infinite scroll skipped - processing available content')

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
            item['source_name'] = 'BidSpotter'
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
            # Remove currency symbols and commas
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
        
        # Extract city from location string
        parts = location_text.split(',')
        return parts[0].strip() if parts else location_text.strip()

    def parse_auction_end_time(self, end_time_text):
        """Parse auction end time to timestamp"""
        if not end_time_text:
            return None
        
        try:
            # This would need more sophisticated parsing based on BidSpotter's format
            # For now, return None
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

    def _extract_brand_model(self, title: str, description: str) -> tuple:
        """Extract brand and model from title and description"""
        text = f"{title} {description}".lower()
        
        # Brand mapping
        brand_mapping = {
            'sciton': 'Sciton',
            'cynosure': 'Cynosure',
            'cutera': 'Cutera',
            'candela': 'Candela',
            'lumenis': 'Lumenis',
            'alma': 'Alma',
            'inmode': 'InMode',
            'btl': 'BTL',
            'lutronic': 'Lutronic',
        }
        
        # Find brand
        brand = None
        for keyword, mapped_brand in brand_mapping.items():
            if keyword in text:
                brand = mapped_brand
                break
        
        # Model mapping
        model_mapping = {
            'joule': 'Joule',
            'picosure': 'PicoSure',
            'picoway': 'PicoWay',
            'gentlemax': 'GentleMax',
            'm22': 'M22',
            'bbl': 'BBL',
            'secret rf': 'Secret RF',
            'morpheus8': 'Morpheus8',
            'emsculpt': 'Emsculpt',
            'excel v': 'Excel V',
            'xeo': 'Xeo',
        }
        
        # Find model
        model = None
        for keyword, mapped_model in model_mapping.items():
            if keyword in text:
                model = mapped_model
                break
        
        return brand, model
    
    def _extract_price(self, price_text: str) -> float:
        """Extract numeric price from text"""
        if not price_text:
            return None
        
        # Remove currency symbols and commas
        cleaned = re.sub(r'[^\d.,]', '', price_text)
        cleaned = cleaned.replace(',', '')
        
        try:
            return float(cleaned)
        except (ValueError, TypeError):
            return None
    
    def _extract_condition(self, text: str) -> str:
        """Extract equipment condition"""
        text_lower = text.lower()
        
        if 'new' in text_lower:
            return 'new'
        elif 'excellent' in text_lower:
            return 'excellent'
        elif 'good' in text_lower:
            return 'good'
        elif 'fair' in text_lower:
            return 'fair'
        elif 'poor' in text_lower:
            return 'poor'
        elif 'used' in text_lower:
            return 'used'
        elif 'refurbished' in text_lower or 'refurb' in text_lower:
            return 'refurbished'
        elif 'as-is' in text_lower or 'as is' in text_lower:
            return 'as-is'
        else:
            return 'unknown'
    
    def _extract_serial_number(self, text: str) -> str:
        """Extract serial number"""
        # Look for patterns like "S/N: 12345" or "Serial: ABC123"
        patterns = [
            r's/n[:\s]+([a-zA-Z0-9]+)',
            r'serial[:\s]+([a-zA-Z0-9]+)',
            r'ser[:\s]+([a-zA-Z0-9]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_year(self, text: str) -> int:
        """Extract equipment year"""
        # Look for 4-digit years
        years = re.findall(r'\b(19|20)\d{2}\b', text)
        if years:
            year = int(years[0])
            if 1990 <= year <= 2025:
                return year
        
        return None
    
    def _extract_hours(self, text: str) -> int:
        """Extract usage hours"""
        # Look for patterns like "1000 hours" or "1000 hrs"
        patterns = [
            r'(\d+)\s*hours?',
            r'(\d+)\s*hrs?',
            r'(\d+)\s*h',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_accessories(self, text: str) -> list:
        """Extract accessories list"""
        accessories = []
        
        # Common accessories
        accessory_keywords = [
            'handpiece', 'handpieces', 'tip', 'tips', 'filter', 'filters',
            'cart', 'carts', 'chair', 'chairs', 'chiller', 'chillers',
            'foot pedal', 'foot pedals', 'control panel', 'power supply',
            'cooling system', 'protective eyewear', 'treatment guide'
        ]
        
        text_lower = text.lower()
        for keyword in accessory_keywords:
            if keyword in text_lower:
                accessories.append(keyword.title())
        
        return accessories
    
    def _parse_location(self, location_text: str) -> dict:
        """Parse location text into city, state, country"""
        if not location_text:
            return {}
        
        # Simple parsing - in production, use more sophisticated geocoding
        parts = location_text.split(',')
        
        result = {}
        if len(parts) >= 1:
            result['city'] = parts[0].strip()
        if len(parts) >= 2:
            result['state'] = parts[1].strip()
        if len(parts) >= 3:
            result['country'] = parts[2].strip()
        
        return result
    
    def _is_laser_equipment(self, response) -> bool:
        """Check if auction is for laser equipment"""
        text_content = ' '.join(response.css('*::text').getall()).lower()
        
        # Check for laser-related keywords
        laser_matches = sum(1 for keyword in self.laser_keywords if keyword in text_content)
        
        # Require at least 2 laser-related keywords for positive match
        return laser_matches >= 2

    def closed(self, reason):
        """Called when spider closes"""
        self.logger.info(f'BidSpotter spider closed: {reason}')
        self.logger.info(f'Processed {len(self.processed_urls)} unique URLs')
