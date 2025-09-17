"""
DOTmed Auctions spider - High value, medium risk source
"""

import scrapy
import time
import re
from scrapy_playwright.page import PageMethod
from laser_intelligence.pipelines.normalization import LaserListingItem


class DotmedSpider(scrapy.Spider):
    """Spider for DOTmed auction listings"""
    
    name = 'dotmed_auctions'
    allowed_domains = ['dotmed.com']
    
    # Evasion configuration
    custom_settings = {
        'DOWNLOAD_DELAY': (3, 8),  # Random delays between 3-8 seconds
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 4,  # Conservative for high-risk source
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 60000,
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            'headless': True,
            'args': ['--disable-blink-features=AutomationControlled']
        },
    }
    
    def __init__(self):
        self.start_urls = [
            'https://www.dotmed.com/auction/category/medical-equipment',
            'https://www.dotmed.com/auction/category/laser-equipment',
            'https://www.dotmed.com/auction/category/aesthetic-equipment',
        ]
        
        # Laser equipment keywords
        self.laser_keywords = [
            'sciton', 'cynosure', 'cutera', 'candela', 'lumenis', 'alma',
            'inmode', 'btl', 'lutronic', 'bison', 'deka', 'quanta',
            'joule', 'picosure', 'picoway', 'gentlemax', 'm22', 'bbl',
            'secret rf', 'morpheus8', 'emsculpt', 'excel v', 'xeo',
            'laser', 'ipl', 'rf', 'hifu', 'cryolipolysis'
        ]
    
    def start_requests(self):
        """Generate initial requests with evasion headers"""
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    'playwright': True,
                    'playwright_page_methods': [
                        PageMethod('wait_for_selector', '.auction-item', timeout=30000),
                        PageMethod('evaluate', 'window.scrollTo(0, document.body.scrollHeight)'),
                        PageMethod('wait_for_timeout', 2000),  # Wait for dynamic content
                    ],
                },
                callback=self.parse_category,
                dont_filter=True,
            )
    
    def parse_category(self, response):
        """Parse auction category page"""
        self.logger.info(f'Parsing category: {response.url}')
        
        # Extract auction listing links
        auction_links = response.css('.auction-item a::attr(href)').getall()
        
        for link in auction_links:
            if link:
                full_url = response.urljoin(link)
                yield scrapy.Request(
                    full_url,
                    meta={
                        'playwright': True,
                        'playwright_page_methods': [
                            PageMethod('wait_for_selector', '.auction-details', timeout=30000),
                        ],
                    },
                    callback=self.parse_auction,
                    dont_filter=True,
                )
        
        # Follow pagination
        next_page = response.css('.pagination .next::attr(href)').get()
        if next_page:
            yield scrapy.Request(
                response.urljoin(next_page),
                meta={
                    'playwright': True,
                    'playwright_page_methods': [
                        PageMethod('wait_for_selector', '.auction-item', timeout=30000),
                    ],
                },
                callback=self.parse_category,
                dont_filter=True,
            )
    
    def parse_auction(self, response):
        """Parse individual auction listing"""
        self.logger.info(f'Parsing auction: {response.url}')
        
        # Check if this is laser equipment
        if not self._is_laser_equipment(response):
            return
        
        # Extract auction details
        title = response.css('h1.auction-title::text').get()
        description = response.css('.auction-description::text').getall()
        description_text = ' '.join(description).strip()
        
        # Extract pricing information
        current_bid = self._extract_price(response.css('.current-bid .amount::text').get())
        reserve_price = self._extract_price(response.css('.reserve-price .amount::text').get())
        buy_now_price = self._extract_price(response.css('.buy-now-price .amount::text').get())
        
        # Extract auction timing
        auction_end = self._extract_auction_end(response.css('.auction-end-time::text').get())
        
        # Extract seller information
        seller_name = response.css('.seller-info .seller-name::text').get()
        seller_contact = response.css('.seller-info .contact-info::text').get()
        
        # Extract location
        location = response.css('.location-info::text').get()
        location_parts = self._parse_location(location)
        
        # Extract images
        images = response.css('.auction-images img::attr(src)').getall()
        
        # Extract equipment details
        brand, model = self._extract_brand_model(title, description_text)
        condition = self._extract_condition(description_text)
        serial_number = self._extract_serial_number(description_text)
        year = self._extract_year(description_text)
        hours = self._extract_hours(description_text)
        accessories = self._extract_accessories(description_text)
        
        # Create item
        item = LaserListingItem()
        item['source_url'] = response.url
        item['source_listing_id'] = self._extract_listing_id(response.url)
        item['title_raw'] = title
        item['description_raw'] = description_text
        item['images'] = images
        item['brand'] = brand
        item['model'] = model
        item['condition'] = condition
        item['serial_number'] = serial_number
        item['year'] = year
        item['hours'] = hours
        item['accessories'] = accessories
        item['asking_price'] = current_bid
        item['reserve_price'] = reserve_price
        item['buy_now_price'] = buy_now_price
        item['auction_end_ts'] = auction_end
        item['seller_name'] = seller_name
        item['seller_contact'] = seller_contact
        item['location_city'] = location_parts.get('city')
        item['location_state'] = location_parts.get('state')
        item['location_country'] = location_parts.get('country', 'USA')
        
        yield item
    
    def _is_laser_equipment(self, response) -> bool:
        """Check if auction is for laser equipment"""
        text_content = ' '.join(response.css('*::text').getall()).lower()
        
        # Check for laser-related keywords
        laser_matches = sum(1 for keyword in self.laser_keywords if keyword in text_content)
        
        # Require at least 2 laser-related keywords for positive match
        return laser_matches >= 2
    
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
    
    def _extract_auction_end(self, end_text: str) -> float:
        """Extract auction end timestamp"""
        if not end_text:
            return None
        
        # TODO: Parse auction end time and convert to timestamp
        # For now, return placeholder
        return time.time() + (24 * 3600)  # 24 hours from now
    
    def _extract_listing_id(self, url: str) -> str:
        """Extract listing ID from URL"""
        # Extract ID from URL pattern like /auction/item/12345
        match = re.search(r'/auction/item/(\d+)', url)
        return match.group(1) if match else None
    
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
