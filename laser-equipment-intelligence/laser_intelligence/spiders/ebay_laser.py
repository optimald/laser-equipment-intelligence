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
        items = response.css('div.s-item')
        
        for item in items:
            # Skip sponsored items and non-product items
            if item.css('div.s-item__ads').get():
                continue
                
            title = item.css('h3.s-item__title::text').get()
            if not title or 'Shop on eBay' in title:
                continue
                
            # Extract price
            price_text = item.css('span.s-item__price::text').get()
            price = None
            if price_text:
                price_match = re.search(r'[\$£€]\s*([0-9,]+\.?[0-9]*)', price_text)
                if price_match:
                    price = float(price_match.group(1).replace(',', ''))
            
            # Extract URL
            url = item.css('a.s-item__link::attr(href)').get()
            if not url:
                continue
                
            # Extract condition
            condition = item.css('span.s-item__condition::text').get()
            if condition:
                condition = condition.strip()
            else:
                condition = "Used - Unknown"
                
            # Extract location
            location = item.css('span.s-item__location::text').get()
            if location:
                location = location.strip()
            else:
                location = "Unknown"
                
            # Extract image
            image = item.css('img.s-item__image::attr(src)').get()
            if not image:
                image = item.css('img.s-item__image::attr(data-src)').get()
                
            # Extract brand and model from title
            brand = "Unknown"
            model = "Unknown"
            if title:
                title_lower = title.lower()
                # Common laser brands
                brands = ['aerolase', 'candela', 'cynosure', 'lumenis', 'syneron', 'alma', 'cutera', 'sciton', 'palomar', 'cooltouch']
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
