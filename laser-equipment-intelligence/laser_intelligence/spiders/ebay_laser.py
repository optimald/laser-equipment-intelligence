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
        
        # Try multiple selectors for modern eBay
        items = (response.css('div.s-item') or 
                response.css('div[data-view*="item"]') or
                response.css('div.srp-river-answer') or
                response.css('div[data-testid="item"]') or
                response.css('div.item'))
        
        self.logger.info(f"Found {len(items)} potential items")
        
        # If no items found, try alternative approach
        if not items:
            # Look for any divs that might contain listings
            items = response.css('div[class*="item"], div[class*="listing"], div[class*="product"]')
            self.logger.info(f"Alternative search found {len(items)} potential items")
        
        # Debug: Print first few item structures
        for i, item in enumerate(items[:3]):
            self.logger.info(f"Item {i} HTML: {item.get()[:200]}...")
        
        for item in items:
            # Skip sponsored items and non-product items
            if item.css('div.s-item__ads').get() or item.css('[data-testid="ad-indicator"]').get():
                continue
                
            # Try multiple title selectors - more comprehensive
            title = (item.css('h3.s-item__title::text').get() or 
                    item.css('h3.s-item__title a::text').get() or
                    item.css('a.s-item__link::text').get() or
                    item.css('[data-testid="listing-title"]::text').get() or
                    item.css('h3::text').get() or
                    item.css('h2::text').get() or
                    item.css('a[class*="title"]::text').get())
            
            if not title or 'Shop on eBay' in title or not title.strip():
                continue
                
            # Extract price - try multiple selectors
            price_text = (item.css('span.s-item__price::text').get() or
                         item.css('span.s-item__price span::text').get() or
                         item.css('[data-testid="price"]::text').get() or
                         item.css('span[class*="price"]::text').get() or
                         item.css('span[class*="cost"]::text').get())
            
            price = None
            if price_text:
                price_match = re.search(r'[\$£€]\s*([0-9,]+\.?[0-9]*)', price_text)
                if price_match:
                    price = float(price_match.group(1).replace(',', ''))
            
            # Extract URL
            url = (item.css('a.s-item__link::attr(href)').get() or
                   item.css('[data-testid="listing-link"]::attr(href)').get() or
                   item.css('a[class*="link"]::attr(href)').get() or
                   item.css('a::attr(href)').get())
            if not url:
                continue
                
            # Extract condition
            condition = (item.css('span.s-item__condition::text').get() or
                        item.css('[data-testid="condition"]::text').get() or
                        item.css('span[class*="condition"]::text').get())
            if condition:
                condition = condition.strip()
            else:
                condition = "Used - Unknown"
                
            # Extract location
            location = (item.css('span.s-item__location::text').get() or
                       item.css('[data-testid="location"]::text').get() or
                       item.css('span[class*="location"]::text').get())
            if location:
                location = location.strip()
            else:
                location = "Unknown"
                
            # Extract image
            image = (item.css('img.s-item__image::attr(src)').get() or
                    item.css('img.s-item__image::attr(data-src)').get() or
                    item.css('[data-testid="listing-image"]::attr(src)').get() or
                    item.css('img::attr(src)').get())
                
            # Extract brand and model from title
            brand = "Unknown"
            model = "Unknown"
            if title:
                title_lower = title.lower()
                # Common laser brands
                brands = ['aerolase', 'candela', 'cynosure', 'lumenis', 'syneron', 'alma', 'cutera', 'sciton', 'palomar', 'cooltouch', 'allergan', 'btl', 'apyx']
                for brand_name in brands:
                    if brand_name in title_lower:
                        brand = brand_name.title()
                        # Try to extract model
                        model_match = re.search(rf'{brand_name}\s+([a-zA-Z0-9\s\-]+)', title_lower)
                        if model_match:
                            model = model_match.group(1).strip().title()
                        break
                        
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
                'score_overall': 75 + (20 if price and price < 50000 else 0)  # Higher score for good deals
            }
    
    def get_timestamp(self):
        from datetime import datetime
        return datetime.now().isoformat()
