import scrapy
import re
from urllib.parse import urlencode, quote_plus


class DotmedAuctionsSpider(scrapy.Spider):
    name = "dotmed_auctions"
    allowed_domains = ["dotmed.com"]
    
    def __init__(self, query=None, *args, **kwargs):
        super(DotmedAuctionsSpider, self).__init__(*args, **kwargs)
        self.query = query or "laser equipment"
        
    def start_requests(self):
        # Search for laser equipment on DOTmed
        search_url = f"https://www.dotmed.com/search?q={quote_plus(self.query)}"
        yield scrapy.Request(
            url=search_url,
            callback=self.parse_search_results,
            meta={'query': self.query}
        )
    
    def parse_search_results(self, response):
        """Parse DOTmed search results page"""
        items = response.css('div.listing-item, div.product-item, .search-result-item')
        
        for item in items:
            title = item.css('h3 a::text, .title a::text, h2 a::text').get()
            if not title:
                continue
                
            # Extract price
            price_text = item.css('.price::text, .cost::text, .amount::text').get()
            price = None
            if price_text:
                price_match = re.search(r'[\$£€]\s*([0-9,]+\.?[0-9]*)', price_text)
                if price_match:
                    price = float(price_match.group(1).replace(',', ''))
            
            # Extract URL
            url = item.css('h3 a::attr(href), .title a::attr(href), h2 a::attr(href)').get()
            if not url:
                continue
            if not url.startswith('http'):
                url = f"https://www.dotmed.com{url}"
                
            # Extract condition
            condition = item.css('.condition::text, .status::text').get()
            if condition:
                condition = condition.strip()
            else:
                condition = "Used - Good"
                
            # Extract location
            location = item.css('.location::text, .seller-location::text').get()
            if location:
                location = location.strip()
            else:
                location = "Unknown"
                
            # Extract image
            image = item.css('img::attr(src)').get()
            if image and not image.startswith('http'):
                image = f"https://www.dotmed.com{image}"
                
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
                'id': f"dotmed_{hash(url)}",
                'title': title.strip(),
                'brand': brand,
                'model': model,
                'condition': condition,
                'price': price,
                'location': location,
                'description': f"DOTmed listing: {title.strip()}",
                'url': url,
                'images': [image] if image else [],
                'source': 'DOTmed Auctions',
                'discovered_at': self.get_timestamp(),
                'score_overall': 80 + (15 if price and price < 40000 else 0)  # Higher score for good deals
            }
    
    def get_timestamp(self):
        from datetime import datetime
        return datetime.now().isoformat()
