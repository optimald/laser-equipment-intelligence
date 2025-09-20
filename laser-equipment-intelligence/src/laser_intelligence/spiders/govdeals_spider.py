"""
GovDeals spider - Government surplus equipment (low risk)
"""

import scrapy
import time
import re
from scrapy_playwright.page import PageMethod
from laser_intelligence.pipelines.normalization import LaserListingItem


class GovdealsSpider(scrapy.Spider):
    """Spider for GovDeals government surplus listings"""
    
    name = 'govdeals'
    allowed_domains = ['govdeals.com']
    
    # Low-risk source configuration
    custom_settings = {
        'DOWNLOAD_DELAY': (1, 3),  # Minimal delays for government data
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 8,  # Higher concurrency for low-risk source
        'CONCURRENT_REQUESTS_PER_DOMAIN': 4,
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 30000,
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            'headless': True,
            'args': ['--disable-blink-features=AutomationControlled']
        },
    }
    
    def __init__(self):
        self.start_urls = [
            'https://www.govdeals.com/index.cfm?fa=Main.CatSearch&catid=1',  # Medical Equipment
            'https://www.govdeals.com/index.cfm?fa=Main.CatSearch&catid=2',  # Healthcare Equipment
            'https://www.govdeals.com/index.cfm?fa=Main.CatSearch&catid=3',  # Laboratory Equipment
        ]
        
        # Laser equipment keywords
        self.laser_keywords = [
            'laser', 'ipl', 'rf', 'hifu', 'cryolipolysis',
            'sciton', 'cynosure', 'cutera', 'candela', 'lumenis',
            'alma', 'inmode', 'btl', 'lutronic', 'bison',
            'joule', 'picosure', 'picoway', 'gentlemax',
            'm22', 'bbl', 'secret rf', 'morpheus8', 'emsculpt',
            'excel v', 'xeo', 'harmony', 'soprano', 'opus',
            'aesthetic', 'cosmetic', 'dermatology', 'hair removal',
            'skin treatment', 'body contouring', 'tattoo removal'
        ]
    
    def start_requests(self):
        """Generate initial requests"""
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    'playwright': True,
                    'playwright_page_methods': [
                        PageMethod('wait_for_selector', '.searchResults', timeout=30000),
                    ],
                },
                callback=self.parse_category,
                dont_filter=True,
            )
    
    def parse_category(self, response):
        """Parse category page for listings"""
        self.logger.info(f'Parsing GovDeals category: {response.url}')
        
        # Extract listing links
        listing_links = response.css('.searchResults a::attr(href)').getall()
        
        for link in listing_links:
            if link and '/index.cfm?fa=Main.Item&itemid=' in link:
                yield scrapy.Request(
                    response.urljoin(link),
                    meta={
                        'playwright': True,
                        'playwright_page_methods': [
                            PageMethod('wait_for_selector', '.itemDetails', timeout=30000),
                        ],
                    },
                    callback=self.parse_listing,
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
                        PageMethod('wait_for_selector', '.searchResults', timeout=30000),
                    ],
                },
                callback=self.parse_category,
                dont_filter=True,
            )
    
    def parse_listing(self, response):
        """Parse individual GovDeals listing"""
        self.logger.info(f'Parsing GovDeals listing: {response.url}')
        
        # Check if this is laser equipment
        if not self._is_laser_equipment(response):
            return
        
        # Extract listing details
        title = response.css('h1.itemTitle::text').get()
        description = response.css('.itemDescription::text').getall()
        description_text = ' '.join(description).strip()
        
        # Extract pricing
        current_bid = self._extract_price(response.css('.currentBid .amount::text').get())
        minimum_bid = self._extract_price(response.css('.minimumBid .amount::text').get())
        buy_now_price = self._extract_price(response.css('.buyNowPrice .amount::text').get())
        
        # Extract auction timing
        auction_end = self._extract_auction_end(response.css('.auctionEnd::text').get())
        
        # Extract seller information
        seller_name = response.css('.sellerInfo .sellerName::text').get()
        seller_contact = response.css('.sellerInfo .contactInfo::text').get()
        
        # Extract location
        location = response.css('.locationInfo::text').get()
        location_parts = self._parse_location(location)
        
        # Extract images
        images = response.css('.itemImages img::attr(src)').getall()
        
        # Extract item details
        item_details = {}
        for detail in response.css('.itemDetails .detailRow'):
            label = detail.css('.detailLabel::text').get()
            value = detail.css('.detailValue::text').get()
            if label and value:
                item_details[label.strip()] = value.strip()
        
        # Extract brand and model
        brand, model = self._extract_brand_model(title, description_text, item_details)
        
        # Extract additional details
        condition = self._extract_condition(description_text, item_details)
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
        item['asking_price'] = current_bid or minimum_bid
        item['reserve_price'] = minimum_bid
        item['buy_now_price'] = buy_now_price
        item['auction_end_ts'] = auction_end
        item['seller_name'] = seller_name
        item['seller_contact'] = seller_contact
        item['location_city'] = location_parts.get('city')
        item['location_state'] = location_parts.get('state')
        item['location_country'] = 'USA'
        
        yield item
    
    def _is_laser_equipment(self, response) -> bool:
        """Check if listing is for laser equipment"""
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
        match = re.search(r'itemid=(\d+)', url)
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
        
        return result
    
    def _extract_brand_model(self, title: str, description: str, item_details: dict = None) -> tuple:
        """Extract brand and model from title, description, and item details"""
        text = f"{title} {description}".lower()
        
        # Check item details first (if provided)
        brand = ''
        model = ''
        if item_details:
            brand = item_details.get('Brand', '').lower()
            model = item_details.get('Model', '').lower()
        
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
            'bison': 'Bison',
            'deka': 'DEKA',
            'quanta': 'Quanta',
        }
        
        # Find brand if not in item details
        if not brand:
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
            'harmony': 'Harmony',
            'soprano': 'Soprano',
            'opus': 'OPUS',
        }
        
        # Find model if not in item details
        if not model:
            for keyword, mapped_model in model_mapping.items():
                if keyword in text:
                    model = mapped_model
                    break
        
        return brand, model
    
    def _extract_condition(self, description: str, item_details: dict = None) -> str:
        """Extract equipment condition"""
        # Check item details first (if provided)
        condition = ''
        if item_details:
            condition = item_details.get('Condition', '').lower()
        
        if not condition:
            text_lower = description.lower()
            
            if 'new' in text_lower:
                condition = 'new'
            elif 'excellent' in text_lower:
                condition = 'excellent'
            elif 'good' in text_lower:
                condition = 'good'
            elif 'fair' in text_lower:
                condition = 'fair'
            elif 'poor' in text_lower:
                condition = 'poor'
            elif 'used' in text_lower:
                condition = 'used'
            elif 'refurbished' in text_lower or 'refurb' in text_lower:
                condition = 'refurbished'
            elif 'as-is' in text_lower or 'as is' in text_lower:
                condition = 'as-is'
            else:
                condition = 'unknown'
        
        return condition
    
    def _extract_serial_number(self, text: str) -> str:
        """Extract serial number"""
        patterns = [
            r's/n[:\s]+([a-zA-Z0-9]+)',
            r'serial[:\s]+([a-zA-Z0-9]+)',
            r'ser[:\s]+([a-zA-Z0-9]+)',
            r'serial number[:\s]+([a-zA-Z0-9]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_year(self, text: str) -> int:
        """Extract equipment year"""
        years = re.findall(r'\b(19|20)\d{2}\b', text)
        if years:
            year = int(years[0])
            if 1990 <= year <= 2025:
                return year
        
        return None
    
    def _extract_hours(self, text: str) -> int:
        """Extract usage hours"""
        patterns = [
            r'(\d+)\s*hours?',
            r'(\d+)\s*hrs?',
            r'(\d+)\s*h',
            r'(\d+)\s*hours?\s*used',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))
        
        return None
    
    def _extract_accessories(self, text: str) -> list:
        """Extract accessories list"""
        accessories = []
        
        accessory_keywords = [
            'handpiece', 'handpieces', 'tip', 'tips', 'filter', 'filters',
            'cart', 'carts', 'chair', 'chairs', 'chiller', 'chillers',
            'foot pedal', 'foot pedals', 'control panel', 'power supply',
            'cooling system', 'protective eyewear', 'treatment guide',
            'applicator', 'applicators', 'wand', 'wands'
        ]
        
        text_lower = text.lower()
        for keyword in accessory_keywords:
            if keyword in text_lower:
                accessories.append(keyword.title())
        
        return accessories
