import scrapy
import re
from urllib.parse import urlencode, quote_plus


class GovdealsSpider(scrapy.Spider):
    name = "govdeals"
    allowed_domains = ["govdeals.com"]
    
    def __init__(self, query=None, *args, **kwargs):
        super(GovdealsSpider, self).__init__(*args, **kwargs)
        self.query = query or "laser equipment"
        
    def start_requests(self):
        # Search for laser equipment on GovDeals
        search_url = f"https://www.govdeals.com/index.cfm?fa=Main.Search&searchtype=1&searchterm={quote_plus(self.query)}"
        yield scrapy.Request(
            url=search_url,
            callback=self.parse_search_results,
            meta={'query': self.query}
        )
    
    def parse_search_results(self, response):
        """Parse GovDeals search results page"""
        items = response.css('div.search-result-item, div.listing-item, .auction-item')
        
        for item in items:
            title = item.css('h3 a::text, .title a::text, h2 a::text').get()
            if not title:
                continue
                
            # Extract price (current bid or starting bid)
            price_text = item.css('.current-bid::text, .starting-bid::text, .price::text').get()
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
                url = f"https://www.govdeals.com{url}"
                
            # Extract condition (government equipment is typically used)
            condition = item.css('.condition::text, .status::text').get()
            if condition:
                condition = condition.strip()
            else:
                condition = "Used - Government Surplus"
                
            # Extract location
            location = item.css('.location::text, .agency-location::text').get()
            if location:
                location = location.strip()
            else:
                location = "Government Agency"
                
            # Extract image
            image = item.css('img::attr(src)').get()
            if image and not image.startswith('http'):
                image = f"https://www.govdeals.com{image}"
                
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
            score_overall = 70  # Base score for government surplus
            
            # Brand-specific scoring (based on real equipment data)
            premium_brands = ['aerolase', 'candela', 'cynosure', 'lumenis', 'sciton', 'cutera', 'syneron']
            if brand.lower() in premium_brands:
                score_overall += 15
            
            # Price-based scoring (government surplus often has good deals)
            if price:
                if price < 5000:  # Excellent government deal
                    score_overall += 30
                elif price < 15000:  # Good government deal
                    score_overall += 20
                elif price < 30000:  # Fair government price
                    score_overall += 10
                elif price > 50000:  # Expensive for government surplus
                    score_overall -= 5
            
            yield {
                'id': f"govdeals_{hash(url)}",
                'title': title.strip(),
                'brand': brand,
                'model': model,
                'condition': condition,
                'price': price,
                'location': location,
                'description': f"GovDeals government surplus: {title.strip()}",
                'url': url,
                'images': [image] if image else [],
                'source': 'GovDeals',
                'discovered_at': self.get_timestamp(),
                'score_overall': min(100, max(0, score_overall))  # Clamp between 0-100
            }
    
    def get_timestamp(self):
        from datetime import datetime
        return datetime.now().isoformat()
