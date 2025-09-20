"""
eBay spider - High volume marketplace with CAPTCHA risk
"""

import scrapy
import time
import re
from scrapy_playwright.page import PageMethod
from laser_intelligence.pipelines.normalization import LaserListingItem


class EbaySpider(scrapy.Spider):
    """Spider for eBay laser equipment listings"""
    
    name = 'ebay_laser'
    allowed_domains = ['ebay.com']
    
    # Evasion configuration for high-risk source
    custom_settings = {
        'DOWNLOAD_DELAY': (5, 15),  # Longer delays for eBay
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 2,  # Very conservative
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT': 90000,
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            'headless': True,
            'args': [
                '--disable-blink-features=AutomationControlled',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu'
            ]
        },
    }
    
    def __init__(self):
        # Laser equipment search terms
        self.search_terms = [
            'sciton joule',
            'cynosure picosure',
            'cutera excel v',
            'candela gentlemax',
            'lumenis m22',
            'alma harmony',
            'inmode secret rf',
            'btl emsculpt',
            'lutronic picoway',
            'laser hair removal',
            'ipl laser',
            'aesthetic laser',
            'medical laser',
            'cosmetic laser',
            'laser equipment',
            'used laser',
            'laser system',
            'laser machine',
            'laser device',
            'laser handpiece'
        ]
        
        # Category IDs for medical/beauty equipment
        self.categories = [
            '11815',  # Beauty & Personal Care > Health & Beauty > Professional Beauty Equipment
            '92084',  # Business & Industrial > Healthcare, Lab & Life Science > Medical Equipment
            '11815',  # Health & Beauty > Professional Beauty Equipment
        ]
    
    def start_requests(self):
        """Generate search requests for laser equipment"""
        for search_term in self.search_terms:
            for category in self.categories:
                url = self._build_search_url(search_term, category)
                yield scrapy.Request(
                    url,
                    meta={
                        'playwright': True,
                        'playwright_page_methods': [
                            PageMethod('wait_for_selector', '.s-item', timeout=30000),
                            PageMethod('evaluate', 'window.scrollTo(0, document.body.scrollHeight)'),
                            PageMethod('wait_for_timeout', 3000),  # Wait for dynamic content
                        ],
                        'search_term': search_term,
                        'category': category,
                    },
                    callback=self.parse_search_results,
                    dont_filter=True,
                )
    
    def parse_search_results(self, response):
        """Parse eBay search results page"""
        search_term = response.meta.get('search_term')
        self.logger.info(f'Parsing eBay search results for: {search_term}')
        
        # Extract listing links
        listing_links = response.css('.s-item a::attr(href)').getall()
        
        for link in listing_links:
            if link and '/itm/' in link:  # eBay item pages
                yield scrapy.Request(
                    link,
                    meta={
                        'playwright': True,
                        'playwright_page_methods': [
                            PageMethod('wait_for_selector', '#x-price-primary', timeout=30000),
                        ],
                        'search_term': search_term,
                    },
                    callback=self.parse_listing,
                    dont_filter=True,
                )
        
        # Follow pagination
        next_page = response.css('.pagination__next::attr(href)').get()
        if next_page:
            yield scrapy.Request(
                next_page,
                meta={
                    'playwright': True,
                    'playwright_page_methods': [
                        PageMethod('wait_for_selector', '.s-item', timeout=30000),
                    ],
                    'search_term': search_term,
                },
                callback=self.parse_search_results,
                dont_filter=True,
            )
    
    def parse_listing(self, response):
        """Parse individual eBay listing"""
        search_term = response.meta.get('search_term')
        self.logger.info(f'Parsing eBay listing: {response.url}')
        
        # Check if this is laser equipment
        if not self._is_laser_equipment(response):
            return
        
        # Extract listing details
        title = response.css('h1#x-title-label-lbl::text').get()
        if not title:
            title = response.css('h1::text').get()
        
        description = response.css('#desc_div::text').getall()
        description_text = ' '.join(description).strip()
        
        # Extract pricing
        price_text = response.css('#x-price-primary .notranslate::text').get()
        if not price_text:
            price_text = response.css('.u-flL.condText::text').get()
        
        price = self._extract_price(price_text)
        
        # Extract condition
        condition = response.css('.u-flL.condText::text').get()
        if not condition:
            condition = response.css('.u-flL.condText span::text').get()
        
        # Extract seller information
        seller_name = response.css('.mbg-nw::text').get()
        seller_feedback = response.css('.mbg-l::text').get()
        
        # Extract location
        location = response.css('.u-flL.condText .u-flL.condText::text').get()
        if not location:
            location = response.css('.u-flL.condText span::text').get()
        
        # Extract images
        images = response.css('#mainImg::attr(src)').getall()
        if not images:
            images = response.css('.img img::attr(src)').getall()
        
        # Extract item specifics
        item_specifics = {}
        for spec in response.css('.u-flL.condText'):
            label = spec.css('.u-flL.condText::text').get()
            value = spec.css('.u-flL.condText span::text').get()
            if label and value:
                item_specifics[label.strip()] = value.strip()
        
        # Extract brand and model
        brand, model = self._extract_brand_model(title, description_text, item_specifics)
        
        # Extract additional details
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
        item['condition'] = self._normalize_condition(condition)
        item['serial_number'] = serial_number
        item['year'] = year
        item['hours'] = hours
        item['accessories'] = accessories
        item['asking_price'] = price
        item['seller_name'] = seller_name
        item['location_city'] = self._parse_location(location)
        item['search_term'] = search_term
        
        yield item
    
    def _build_search_url(self, search_term: str, category: str) -> str:
        """Build eBay search URL"""
        base_url = "https://www.ebay.com/sch/i.html"
        params = {
            '_nkw': search_term,
            '_sacat': category,
            '_sop': '10',  # Sort by newly listed
            'LH_BIN': '1',  # Buy it now only
            'LH_Complete': '1',  # Completed listings
            'LH_Sold': '1',  # Sold listings
            'rt': 'nc',  # No category
            '_pgn': '1',  # Page 1
        }
        
        param_string = '&'.join([f'{k}={v}' for k, v in params.items()])
        return f"{base_url}?{param_string}"
    
    def _is_laser_equipment(self, response) -> bool:
        """Check if listing is for laser equipment"""
        text_content = ' '.join(response.css('*::text').getall()).lower()
        
        laser_keywords = [
            'laser', 'ipl', 'rf', 'hifu', 'cryolipolysis',
            'sciton', 'cynosure', 'cutera', 'candela', 'lumenis',
            'alma', 'inmode', 'btl', 'lutronic', 'bison',
            'joule', 'picosure', 'picoway', 'gentlemax',
            'm22', 'bbl', 'secret rf', 'morpheus8', 'emsculpt',
            'excel v', 'xeo', 'harmony', 'soprano', 'opus'
        ]
        
        # Require at least 2 laser-related keywords
        laser_matches = sum(1 for keyword in laser_keywords if keyword in text_content)
        return laser_matches >= 2
    
    def _extract_price(self, price_text: str) -> float:
        """Extract numeric price from eBay price text"""
        if not price_text:
            return None
        
        # Remove currency symbols and commas
        cleaned = re.sub(r'[^\d.,]', '', price_text)
        cleaned = cleaned.replace(',', '')
        
        try:
            return float(cleaned)
        except (ValueError, TypeError):
            return None
    
    def _extract_listing_id(self, url: str) -> str:
        """Extract eBay item ID from URL"""
        match = re.search(r'/itm/(\d+)', url)
        return match.group(1) if match else None
    
    def _extract_brand_model(self, title: str, description: str, item_specifics: dict = None) -> tuple:
        """Extract brand and model from title, description, and item specifics"""
        text = f"{title} {description}".lower()
        
        # Check item specifics first (if provided)
        brand = ''
        model = ''
        if item_specifics:
            brand = item_specifics.get('Brand', '').lower()
            model = item_specifics.get('Model', '').lower()
        
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
        
        # Find brand if not in item specifics
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
        
        # Find model if not in item specifics
        if not model:
            for keyword, mapped_model in model_mapping.items():
                if keyword in text:
                    model = mapped_model
                    break
        
        return brand, model
    
    def _normalize_condition(self, condition: str) -> str:
        """Normalize eBay condition to standard format"""
        if not condition:
            return 'unknown'
        
        condition_mapping = {
            'new': 'new',
            'new (other)': 'new',
            'new with tags': 'new',
            'new without tags': 'new',
            'like new': 'excellent',
            'excellent': 'excellent',
            'very good': 'good',
            'good': 'good',
            'acceptable': 'fair',
            'fair': 'fair',
            'poor': 'poor',
            'for parts or not working': 'as-is',
            'for parts': 'as-is',
            'not working': 'as-is',
        }
        
        return condition_mapping.get(condition.lower(), 'unknown')
    
    def _extract_serial_number(self, text: str) -> str:
        """Extract serial number from text"""
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
    
    def _parse_location(self, location_text: str) -> str:
        """Parse location text to extract city"""
        if not location_text:
            return None
        
        # Simple parsing - extract first part before comma
        parts = location_text.split(',')
        return parts[0].strip() if parts else None
