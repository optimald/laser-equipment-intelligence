import scrapy
import re
from urllib.parse import urlencode, quote_plus


class EbayLaserSpider(scrapy.Spider):
    name = "ebay_laser"
    allowed_domains = ["ebay.com"]
    
    def __init__(self, query=None, *args, **kwargs):
        super(EbayLaserSpider, self).__init__(*args, **kwargs)
        self.query = query or "laser equipment medical aesthetic"
        
    def start_requests(self):
        # Search for laser equipment on eBay
        search_url = f"https://www.ebay.com/sch/i.html?_nkw={quote_plus(self.query)}"
        yield scrapy.Request(
            url=search_url,
            callback=self.parse_search_results,
            meta={'query': self.query}
        )
    
    def parse_search_results(self, response):
        """Parse eBay search results page"""
        # Debug: Print response info
        self.logger.info(f"Response URL: {response.url}")
        self.logger.info(f"Response status: {response.status}")
        
        # Use the working approach: find meaningful divs with links and content
        all_divs = response.css('div')
        meaningful_items = []
        
        for div in all_divs:
            try:
                # Get text content
                text = div.css('::text').getall()
                text_content = ' '.join(text).strip()
                
                # Get links
                links = div.css('a::attr(href)').getall()
                
                # Look for divs with reasonable content and eBay item links
                if (links and 
                    len(text_content) > 20 and 
                    len(text_content) < 500 and
                    not text_content.lower().startswith(('skip', 'sign in', 'daily deals', 'help', 'sell', 'my ebay'))):
                    
                    # Check if any link looks like an item link
                    for link in links:
                        if '/itm/' in link:
                            meaningful_items.append(div)
                            break
            except:
                continue
        
        items = meaningful_items
        self.logger.info(f"Found {len(items)} meaningful product items")
        
        # Debug: Print first few item structures
        for i, item in enumerate(items[:3]):
            self.logger.info(f"Item {i} HTML: {item.get()[:200]}...")
        
        for item in items:
                
            # Extract title from the meaningful div content
            # Get all text and find the longest meaningful line
            all_text = item.css('::text').getall()
            text_content = ' '.join(all_text).strip()
            
            # Split into lines and find the title (longest meaningful line)
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            title = None
            
            for line in sorted(lines, key=len, reverse=True):
                if (len(line) > 20 and 
                    len(line) < 200 and
                    not line.lower().startswith(('$', 'free', 'shipping', 'skip', 'sign', 'brand new', 'used', 'or best offer')) and
                    not line.lower().endswith(('free shipping', 'buy it now', 'or best offer', 'opens in a new window'))):
                    title = line
                    break
            
            if not title:
                continue
                
            # Extract price from text content
            price = None
            price_match = re.search(r'\$([0-9,]+\.?[0-9]*)', text_content)
            if price_match:
                try:
                    price = float(price_match.group(1).replace(',', ''))
                except ValueError:
                    pass
            
            # Extract URL from links
            url = None
            links = item.css('a::attr(href)').getall()
            for link in links:
                if '/itm/' in link:
                    url = link
                    break
            
            if not url:
                continue
                
            # Extract condition from text content
            condition = "Used - Unknown"
            if 'brand new' in text_content.lower():
                condition = "New"
            elif 'used' in text_content.lower():
                condition = "Used"
            elif 'refurbished' in text_content.lower():
                condition = "Refurbished"
                
            # Extract location and image
            location = "eBay"
            image = item.css('img::attr(src)').get() or item.css('img::attr(data-src)').get()
                
            # Extract brand and model from title using real equipment data
            brand = "Unknown"
            model = "Unknown"
            if title:
                title_lower = title.lower()
                # Real laser brands from actual equipment data (57 brands)
                brands = [
                    'aerolase', 'aesthetic', 'agnes', 'allergan', 'alma', 'apyx', 'btl', 'bluecore', 'buffalo', 
                    'candela', 'canfield', 'cocoon', 'cutera', 'cynosure', 'cytrellis', 'deka', 'dusa', 'edge', 
                    'ellman', 'energist', 'envy', 'fotona', 'hk', 'ilooda', 'inmode', 'iridex', 'jeisys', 
                    'laseroptek', 'lumenis', 'lutronic', 'luvo', 'merz', 'microaire', 'mixto', 'mrp', 'new', 
                    'novoxel', 'ohmeda', 'perigee', 'pronox', 'quanta', 'quantel', 'rohrer', 'sandstone', 
                    'sciton', 'she', 'sinclair', 'solta', 'syl', 'syneron', 'thermi', 'venus', 'wells', 
                    'wontech', 'zimmer'
                ]
                
                # Enhanced brand detection with better matching
                for brand_name in brands:
                    if brand_name in title_lower:
                        brand = brand_name.title()
                        # Try to extract model with improved regex patterns
                        model_patterns = [
                            rf'{brand_name}\s+([a-zA-Z0-9\s\-\.]+?)(?:\s|$|,|\.)',
                            rf'{brand_name}:\s*([a-zA-Z0-9\s\-\.]+?)(?:\s|$|,|\.)',
                            rf'{brand_name}\s+([a-zA-Z0-9\s\-\.]+?)(?:\s+laser|\s+system|\s+device)',
                        ]
                        
                        for pattern in model_patterns:
                            model_match = re.search(pattern, title_lower)
                            if model_match:
                                model = model_match.group(1).strip().title()
                                break
                        
                        # Clean up model name
                        if model and len(model) > 50:  # Prevent overly long model names
                            model = model[:50].strip()
                        break
                        
            # Calculate realistic score based on brand and price
            score_overall = 60  # Base score
            
            # Brand-specific scoring (based on real equipment data)
            premium_brands = ['aerolase', 'candela', 'cynosure', 'lumenis', 'sciton', 'cutera', 'syneron']
            if brand.lower() in premium_brands:
                score_overall += 15
            
            # Price-based scoring (realistic ranges based on actual data)
            if price:
                if price < 10000:  # Very good deal
                    score_overall += 25
                elif price < 25000:  # Good deal
                    score_overall += 15
                elif price < 50000:  # Fair price
                    score_overall += 10
                elif price > 100000:  # Expensive
                    score_overall -= 10
            
            # Condition bonus
            if 'excellent' in condition.lower() or 'new' in condition.lower():
                score_overall += 10
            elif 'good' in condition.lower():
                score_overall += 5
            
            yield {
                'id': f"ebay_{hash(url)}",
                'title': title.strip() if title else "Unknown Title",
                'brand': brand,
                'model': model,
                'condition': condition,
                'price': price,
                'location': location,
                'description': f"eBay listing: {title.strip() if title else 'Unknown'}",
                'url': url,
                'images': [image] if image else [],
                'source': 'eBay',
                'discovered_at': self.get_timestamp(),
                'score_overall': min(100, max(0, score_overall))  # Clamp between 0-100
            }
    
    def get_timestamp(self):
        from datetime import datetime
        return datetime.now().isoformat()
