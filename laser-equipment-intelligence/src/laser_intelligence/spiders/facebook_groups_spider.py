"""
Facebook Groups spider for laser equipment discovery in medical/equipment groups
"""

import scrapy
import time
import random
import re
from urllib.parse import urljoin
from laser_intelligence.pipelines.normalization import LaserListingItem


class FacebookGroupsSpider(scrapy.Spider):
    name = 'facebook_groups'
    allowed_domains = ['facebook.com', 'www.facebook.com', 'm.facebook.com']
    
    # Target Facebook groups for laser equipment
    groups = [
        'MedicalEquipmentForSale',
        'UsedMedicalEquipment',
        'AestheticEquipment',
        'LaserEquipmentSales',
        'MedicalDeviceTrading',
        'CosmeticEquipment',
        'DermatologyEquipment',
        'MedicalAuction',
        'EquipmentLiquidation',
        'MedicalSurplus'
    ]
    
    start_urls = []

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
        'DOWNLOAD_DELAY': (120, 180),  # Very heavy throttling: 2-3 minutes between requests
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
        self.processed_posts = set()
        self.request_count = 0
        self.max_requests_per_session = 5  # Very limited for groups
        self.laser_keywords = [
            'sciton', 'cynosure', 'cutera', 'candela', 'lumenis', 'alma',
            'inmode', 'btl', 'lutronic', 'bison', 'deka', 'quanta',
            'joule', 'picosure', 'picoway', 'gentlemax', 'm22', 'bbl',
            'secret rf', 'morpheus8', 'emsculpt', 'excel v', 'xeo',
            'laser', 'ipl', 'rf', 'hifu', 'cryolipolysis', 'aesthetic',
            'cosmetic', 'dermatology', 'hair removal', 'skin resurfacing'
        ]
        
        # Build start URLs for each group
        self.start_urls = []
        for group in self.groups:
            # Search for laser equipment posts in group
            search_url = f"https://www.facebook.com/groups/{group}/search/?query=laser%20equipment"
            self.start_urls.append(search_url)

    def start_requests(self):
        """Generate initial requests for each Facebook group"""
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                meta={
                    'playwright': True,
                    'playwright_page_methods': [
                        PageMethod('wait_for_selector', '[data-testid="group_posts"]', timeout=60000),
                        PageMethod('wait_for_timeout', 5000),
                    ],
                    'playwright_include_page': True,
                    'group': self.extract_group_from_url(url),
                },
                headers=self.get_facebook_headers(),
                callback=self.parse_group_posts,
                dont_filter=True,
            )

    def parse_group_posts(self, response):
        """Parse Facebook group posts for laser equipment"""
        group = response.meta.get('group', 'unknown')
        self.logger.info(f'Parsing Facebook group: {group}')
        
        # Check if we've hit request limit
        if self.request_count >= self.max_requests_per_session:
            self.logger.info('Hit request limit for Facebook Groups session')
            return
        
        # Extract post links
        post_links = response.css('[data-testid="group_posts"] a[href*="/posts/"]::attr(href)').getall()
        
        for link in post_links:
            if link and link not in self.processed_posts:
                self.processed_posts.add(link)
                
                # Convert relative URLs to absolute
                if link.startswith('/'):
                    full_url = response.urljoin(link)
                else:
                    full_url = link
                
                # Very heavy delay between requests
                time.sleep(random.randint(120, 180))
                
                yield scrapy.Request(
                    full_url,
                    meta={
                        'playwright': True,
                        'playwright_page_methods': [
                            PageMethod('wait_for_selector', '[data-testid="post_content"]', timeout=60000),
                            PageMethod('wait_for_timeout', 3000),
                        ],
                        'group': group,
                    },
                    headers=self.get_facebook_headers(),
                    callback=self.parse_group_post,
                    dont_filter=True,
                )
                
                self.request_count += 1
                
                # Break if we've hit the limit
                if self.request_count >= self.max_requests_per_session:
                    break

    def parse_group_post(self, response):
        """Parse individual Facebook group post for laser equipment"""
        group = response.meta.get('group', 'unknown')
        
        try:
            # Extract post content
            title = response.css('[data-testid="post_content"] h1::text').get() or response.css('.post_title::text').get()
            content = response.css('[data-testid="post_content"] .userContent::text').getall()
            content_text = ' '.join(content) if content else ''
            
            # Check if this post is about laser equipment
            if not self.is_laser_equipment_post(title, content_text):
                return
            
            # Extract additional information
            author = response.css('[data-testid="post_author"]::text').get() or response.css('.author::text').get()
            post_time = response.css('[data-testid="post_time"]::attr(title)').get() or response.css('.timestamp::attr(title)').get()
            
            # Look for contact information
            contact_info = self.extract_contact_info(content_text)
            
            # Look for images
            images = response.css('[data-testid="post_content"] img::attr(src)').getall()
            
            # Create item
            item = LaserListingItem()
            item['source_url'] = response.url
            item['title_raw'] = title
            item['description_raw'] = content_text
            item['source_name'] = f'Facebook Group: {group}'
            item['discovered_at'] = time.time()
            item['evasion_score'] = 100  # Placeholder
            item['scraped_legally'] = True
            
            # Facebook-specific fields
            item['seller_name'] = author
            item['facebook_group'] = group
            item['contact_info'] = contact_info
            item['images'] = [response.urljoin(img) for img in images if img]
            
            # Try to extract price information
            price = self.extract_price_from_text(f"{title} {content_text}")
            if price:
                item['asking_price'] = price
            
            # Try to extract location
            location = self.extract_location_from_text(content_text)
            if location:
                item['location_city'] = location
            
            yield item
            
        except Exception as e:
            self.logger.error(f'Error parsing Facebook group post {response.url}: {e}')

    def is_laser_equipment_post(self, title, content):
        """Check if post is about laser equipment"""
        if not title and not content:
            return False
        
        text_to_check = f"{title or ''} {content or ''}".lower()
        
        # Check for laser equipment keywords
        keyword_matches = sum(1 for keyword in self.laser_keywords if keyword in text_to_check)
        
        # Require at least 2 keyword matches for positive identification
        return keyword_matches >= 2

    def extract_contact_info(self, text):
        """Extract contact information from post text"""
        if not text:
            return None
        
        # Look for email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        
        # Look for phone numbers
        phone_pattern = r'(\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}'
        phones = re.findall(phone_pattern, text)
        
        contact_info = {}
        if emails:
            contact_info['emails'] = emails
        if phones:
            contact_info['phones'] = phones
            
        return contact_info if contact_info else None

    def extract_price_from_text(self, text):
        """Extract price information from text"""
        if not text:
            return None
        
        # Look for price patterns
        price_patterns = [
            r'\$[\d,]+(?:\.\d{2})?',
            r'USD\s*[\d,]+(?:\.\d{2})?',
            r'[\d,]+(?:\.\d{2})?\s*dollars?',
            r'asking\s*[\$]?[\d,]+(?:\.\d{2})?',
            r'price\s*[\$]?[\d,]+(?:\.\d{2})?',
            r'for\s*sale\s*[\$]?[\d,]+(?:\.\d{2})?',
        ]
        
        for pattern in price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    # Clean and convert to float
                    price_str = re.sub(r'[^\d.]', '', matches[0])
                    return float(price_str)
                except (ValueError, TypeError):
                    continue
        
        return None

    def extract_location_from_text(self, text):
        """Extract location information from text"""
        if not text:
            return None
        
        # Look for common location patterns
        location_patterns = [
            r'in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'located\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*[A-Z]{2}',
            r'pickup\s+in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0].strip()
        
        return None

    def get_facebook_headers(self):
        """Generate appropriate headers for Facebook"""
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
        self.logger.info(f'Facebook Groups spider closed: {reason}')
        self.logger.info(f'Processed {len(self.processed_posts)} unique posts')
        self.logger.info(f'Made {self.request_count} requests in this session')

    def extract_group_from_url(self, url):
        """Extract group name from URL"""
        match = re.search(r'/groups/([^/]+)', url)
        return match.group(1) if match else 'unknown'
