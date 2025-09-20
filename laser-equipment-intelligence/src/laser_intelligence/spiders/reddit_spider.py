"""
Reddit spider for laser equipment discovery in medical/equipment subreddits
"""

import scrapy
import time
import random
import re
from urllib.parse import urljoin
from laser_intelligence.pipelines.normalization import LaserListingItem


class RedditSpider(scrapy.Spider):
    name = 'reddit'
    allowed_domains = ['reddit.com', 'www.reddit.com', 'old.reddit.com']
    
    # Target subreddits for laser equipment
    subreddits = [
        'medicaldevices',
        'UsedGear', 
        'Flipping',
        'laser',
        'aesthetic',
        'dermatology',
        'cosmeticsurgery',
        'medicalequipment',
        'usedmedical',
        'equipmentforsale'
    ]
    
    start_urls = []

    custom_settings = {
        'DOWNLOAD_DELAY': (3, 8),  # Moderate delays for Reddit
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 4,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'DOWNLOADER_MIDDLEWARES': {
            'laser_intelligence.middleware.evasion.EvasionMiddleware': 543,
            'laser_intelligence.middleware.proxy.ProxyMiddleware': 544,
        },
        'ITEM_PIPELINES': {
            'laser_intelligence.pipelines.normalization.NormalizationPipeline': 300,
            'laser_intelligence.pipelines.scoring.ScoringPipeline': 400,
            'laser_intelligence.pipelines.alerts.AlertsPipeline': 500,
        },
        'USER_AGENT': 'LaserEquipmentBot/1.0 (Educational Research)',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.processed_posts = set()
        self.laser_keywords = [
            'sciton', 'cynosure', 'cutera', 'candela', 'lumenis', 'alma',
            'inmode', 'btl', 'lutronic', 'bison', 'deka', 'quanta',
            'joule', 'picosure', 'picoway', 'gentlemax', 'm22', 'bbl',
            'secret rf', 'morpheus8', 'emsculpt', 'excel v', 'xeo',
            'laser', 'ipl', 'rf', 'hifu', 'cryolipolysis', 'aesthetic',
            'cosmetic', 'dermatology', 'hair removal', 'skin resurfacing'
        ]
        
        # Build start URLs for each subreddit
        self.start_urls = []
        for subreddit in self.subreddits:
            # Search for laser equipment posts
            search_url = f"https://old.reddit.com/r/{subreddit}/search/?q=laser%20equipment&restrict_sr=1&sort=new&t=all"
            self.start_urls.append(search_url)
            
            # Also check recent posts
            recent_url = f"https://old.reddit.com/r/{subreddit}/new/"
            self.start_urls.append(recent_url)

    def start_requests(self):
        """Generate initial requests for each subreddit"""
        for url in self.start_urls:
            yield scrapy.Request(
                url,
                headers=self.get_reddit_headers(),
                callback=self.parse_subreddit,
                meta={'subreddit': self.extract_subreddit_from_url(url)},
                dont_filter=True,
            )

    def parse_subreddit(self, response):
        """Parse subreddit page for laser equipment posts"""
        subreddit = response.meta.get('subreddit', 'unknown')
        self.logger.info(f'Parsing subreddit: r/{subreddit}')
        
        # Extract post links
        post_links = response.css('.thing[data-type="link"] .title a::attr(href)').getall()
        
        for link in post_links:
            if link and link not in self.processed_posts:
                self.processed_posts.add(link)
                
                # Convert relative URLs to absolute
                if link.startswith('/'):
                    full_url = response.urljoin(link)
                else:
                    full_url = link
                
                yield scrapy.Request(
                    full_url,
                    headers=self.get_reddit_headers(),
                    callback=self.parse_post,
                    meta={'subreddit': subreddit},
                    dont_filter=True,
                )

    def parse_post(self, response):
        """Parse individual Reddit post for laser equipment"""
        subreddit = response.meta.get('subreddit', 'unknown')
        
        try:
            # Extract post content
            title = response.css('.title .title::text').get() or response.css('h1::text').get()
            content = response.css('.usertext-body .md p::text').getall()
            content_text = ' '.join(content) if content else ''
            
            # Check if this post is about laser equipment
            if not self.is_laser_equipment_post(title, content_text):
                return
            
            # Extract additional information
            author = response.css('.author::text').get()
            post_time = response.css('.live-timestamp::attr(title)').get()
            score = response.css('.score .number::text').get()
            comments_count = response.css('.comments::text').re_first(r'(\d+)')
            
            # Look for contact information or links
            contact_info = self.extract_contact_info(content_text)
            external_links = response.css('.usertext-body .md a::attr(href)').getall()
            
            # Create item
            item = LaserListingItem()
            item['source_url'] = response.url
            item['title_raw'] = title
            item['description_raw'] = content_text
            item['source_name'] = f'Reddit r/{subreddit}'
            item['discovered_at'] = time.time()
            item['evasion_score'] = 100  # Reddit is generally permissive
            item['scraped_legally'] = True
            
            # Reddit-specific fields
            item['seller_name'] = author
            item['reddit_subreddit'] = subreddit
            item['reddit_score'] = self.parse_score(score)
            item['reddit_comments'] = self.parse_comments_count(comments_count)
            item['contact_info'] = contact_info
            item['external_links'] = external_links
            
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
            self.logger.error(f'Error parsing Reddit post {response.url}: {e}')

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
        ]
        
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0].strip()
        
        return None

    def parse_score(self, score_text):
        """Parse Reddit score to integer"""
        if not score_text:
            return 0
        
        try:
            return int(score_text.replace(',', ''))
        except (ValueError, TypeError):
            return 0

    def parse_comments_count(self, comments_text):
        """Parse comments count to integer"""
        if not comments_text:
            return 0
        
        try:
            return int(comments_text.replace(',', ''))
        except (ValueError, TypeError):
            return 0

    def get_reddit_headers(self):
        """Generate appropriate headers for Reddit"""
        return {
            'User-Agent': 'LaserEquipmentBot/1.0 (Educational Research)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }

    def closed(self, reason):
        """Called when spider closes"""
        self.logger.info(f'Reddit spider closed: {reason}')
        self.logger.info(f'Processed {len(self.processed_posts)} unique posts')

    def extract_subreddit_from_url(self, url):
        """Extract subreddit name from URL"""
        match = re.search(r'/r/([^/]+)', url)
        return match.group(1) if match else 'unknown'
