"""
Facebook Groups API spider using Facebook Graph API for authenticated access
"""

import scrapy
import time
import random
import re
import json
from urllib.parse import urljoin
from laser_intelligence.pipelines.normalization import LaserListingItem


class FacebookGroupsAPISpider(scrapy.Spider):
    name = 'facebook_groups_api'
    allowed_domains = ['graph.facebook.com']
    
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

    custom_settings = {
        'DOWNLOAD_DELAY': (2, 5),  # API rate limiting
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'CONCURRENT_REQUESTS': 2,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 2,
        'ITEM_PIPELINES': {
            'laser_intelligence.pipelines.normalization.NormalizationPipeline': 300,
            'laser_intelligence.pipelines.scoring.ScoringPipeline': 400,
            'laser_intelligence.pipelines.alerts.AlertsPipeline': 500,
        },
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
        
        # Facebook API credentials (set via environment variables)
        self.access_token = self.get_facebook_token()
        self.api_version = 'v18.0'
        self.base_url = f'https://graph.facebook.com/{self.api_version}'

    def start_requests(self):
        """Generate requests for each Facebook group"""
        if not self.access_token:
            self.logger.error('Facebook access token not found. Please set FACEBOOK_ACCESS_TOKEN environment variable.')
            return
        
        for group in self.groups:
            # Search for laser equipment posts in group
            search_url = f"{self.base_url}/search"
            params = {
                'q': 'laser equipment',
                'type': 'post',
                'fields': 'id,message,created_time,from,permalink_url,attachments',
                'access_token': self.access_token,
                'limit': 25
            }
            
            yield scrapy.Request(
                url=search_url,
                method='GET',
                headers=self.get_api_headers(),
                meta={'group': group, 'params': params},
                callback=self.parse_group_search,
                dont_filter=True,
            )

    def parse_group_search(self, response):
        """Parse Facebook Graph API search results"""
        group = response.meta.get('group', 'unknown')
        
        try:
            data = json.loads(response.text)
            posts = data.get('data', [])
            
            self.logger.info(f'Found {len(posts)} posts in group {group}')
            
            for post in posts:
                post_id = post.get('id')
                if post_id and post_id not in self.processed_posts:
                    self.processed_posts.add(post_id)
                    
                    # Get detailed post information
                    post_url = f"{self.base_url}/{post_id}"
                    params = {
                        'fields': 'id,message,created_time,from,permalink_url,attachments,comments.limit(10){message,from}',
                        'access_token': self.access_token
                    }
                    
                    yield scrapy.Request(
                        url=post_url,
                        method='GET',
                        headers=self.get_api_headers(),
                        meta={'group': group, 'post_data': post},
                        callback=self.parse_group_post,
                        dont_filter=True,
                    )
            
            # Handle pagination
            next_page = data.get('paging', {}).get('next')
            if next_page:
                yield scrapy.Request(
                    url=next_page,
                    headers=self.get_api_headers(),
                    meta={'group': group},
                    callback=self.parse_group_search,
                    dont_filter=True,
                )
                
        except Exception as e:
            self.logger.error(f'Error parsing group search for {group}: {e}')

    def parse_group_post(self, response):
        """Parse individual Facebook group post"""
        group = response.meta.get('group', 'unknown')
        post_data = response.meta.get('post_data', {})
        
        try:
            data = json.loads(response.text)
            
            # Extract post content
            message = data.get('message', '')
            created_time = data.get('created_time', '')
            from_info = data.get('from', {})
            permalink_url = data.get('permalink_url', '')
            
            # Check if this post is about laser equipment
            if not self.is_laser_equipment_post(message):
                return
            
            # Extract author information
            author_name = from_info.get('name', 'Unknown')
            author_id = from_info.get('id', '')
            
            # Extract attachments (images, links)
            attachments = data.get('attachments', {}).get('data', [])
            images = []
            for attachment in attachments:
                if attachment.get('type') == 'photo':
                    image_url = attachment.get('media', {}).get('image', {}).get('src', '')
                    if image_url:
                        images.append(image_url)
            
            # Extract comments for additional context
            comments = data.get('comments', {}).get('data', [])
            comment_texts = [comment.get('message', '') for comment in comments]
            all_text = f"{message} {' '.join(comment_texts)}"
            
            # Create item
            item = LaserListingItem()
            item['source_url'] = permalink_url
            item['title_raw'] = message[:100] + '...' if len(message) > 100 else message
            item['description_raw'] = message
            item['source_name'] = f'Facebook Group: {group}'
            item['discovered_at'] = time.time()
            item['evasion_score'] = 100  # API access is compliant
            item['scraped_legally'] = True
            
            # Facebook-specific fields
            item['seller_name'] = author_name
            item['facebook_group'] = group
            item['facebook_author_id'] = author_id
            item['facebook_post_id'] = data.get('id', '')
            item['facebook_created_time'] = created_time
            item['images'] = images
            item['comments_count'] = len(comments)
            
            # Try to extract price information
            price = self.extract_price_from_text(all_text)
            if price:
                item['asking_price'] = price
            
            # Try to extract location
            location = self.extract_location_from_text(all_text)
            if location:
                item['location_city'] = location
            
            # Extract contact information
            contact_info = self.extract_contact_info(all_text)
            if contact_info:
                item['contact_info'] = contact_info
            
            yield item
            
        except Exception as e:
            self.logger.error(f'Error parsing Facebook group post: {e}')

    def is_laser_equipment_post(self, text):
        """Check if post is about laser equipment"""
        if not text:
            return False
        
        text_lower = text.lower()
        keyword_matches = sum(1 for keyword in self.laser_keywords if keyword in text_lower)
        
        # Require at least 2 keyword matches for positive identification
        return keyword_matches >= 2

    def extract_price_from_text(self, text):
        """Extract price information from text"""
        if not text:
            return None
        
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
                    price_str = re.sub(r'[^\d.]', '', matches[0])
                    return float(price_str)
                except (ValueError, TypeError):
                    continue
        
        return None

    def extract_location_from_text(self, text):
        """Extract location information from text"""
        if not text:
            return None
        
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

    def get_api_headers(self):
        """Generate headers for Facebook Graph API"""
        return {
            'User-Agent': 'LaserEquipmentBot/1.0 (Educational Research)',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9',
        }

    def get_facebook_token(self):
        """Get Facebook access token from environment or config"""
        import os
        return os.getenv('FACEBOOK_ACCESS_TOKEN')

    def closed(self, reason):
        """Called when spider closes"""
        self.logger.info(f'Facebook Groups API spider closed: {reason}')
        self.logger.info(f'Processed {len(self.processed_posts)} unique posts')
