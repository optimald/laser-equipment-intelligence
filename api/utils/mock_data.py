"""
Intelligent mock data generation for laser equipment searches
"""

from typing import List, Dict, Any
from datetime import datetime
import random


def generate_intelligent_mock_results(query: str, limit: int) -> List[Dict[str, Any]]:
    """Generate intelligent mock results based on actual search patterns and real equipment data"""
    
    query_lower = query.lower()
    
    # Determine brand and model from query
    brand = "Unknown"
    model = "Unknown"
    
    # Real laser brands and models from actual equipment data (174 items, 57 brands)
    brand_models = {
        'aerolase': {
            'brand': 'Aerolase',
            'models': ['Lightpod Neo Elite', 'LightPod Era Elite', 'LightPod Neo', 'LightPod Elite', 'LightPod Pro'],
            'price_range': (20000, 40000)
        },
        'agnes': {
            'brand': 'Agnes',
            'models': ['Agnes RF', 'Agnes RF System', 'Agnes Elite', 'Agnes Pro'],
            'price_range': (25000, 45000)
        },
        'allergan': {
            'brand': 'Allergan',
            'models': ['DiamondGlow', 'CoolSculpting', 'CoolSculpting Elite', 'CoolSculpting Flex'],
            'price_range': (30000, 60000)
        },
        'alma': {
            'brand': 'Alma',
            'models': ['Harmony XL', 'Harmony', 'Soprano', 'Accent'],
            'price_range': (25000, 50000)
        },
        'apyx': {
            'brand': 'Apyx',
            'models': ['Renuvion', 'Renuvion J-Plasma', 'Apyx Medical'],
            'price_range': (35000, 65000)
        },
        'btl': {
            'brand': 'BTL',
            'models': ['Emsculpt', 'Emsculpt NEO', 'Emsella', 'Exilis'],
            'price_range': (40000, 80000)
        },
        'candela': {
            'brand': 'Candela',
            'models': ['GentleMax Pro', 'Nordlys', 'Vbeam Perfecta', 'CoolGlide'],
            'price_range': (35000, 65000)
        },
        'cutera': {
            'brand': 'Cutera',
            'models': ['Excel V+', 'Xeo SA', 'Laser Genesis', 'Titan'],
            'price_range': (30000, 60000)
        },
        'cynosure': {
            'brand': 'Cynosure',
            'models': ['Elite+', 'Icon', 'Starlux 500', 'PicoSure', 'Monolith'],
            'price_range': (40000, 70000)
        },
        'lumenis': {
            'brand': 'Lumenis',
            'models': ['Lightsheer Duet', 'M22', 'OptiLight', 'Splendor X', 'UltraPulse'],
            'price_range': (45000, 80000)
        },
        'sciton': {
            'brand': 'Sciton',
            'models': ['Joule', 'Joule 7', 'Joule X', 'Profile', 'BBLs'],
            'price_range': (50000, 90000)
        },
        'syneron': {
            'brand': 'Syneron',
            'models': ['VelaShape III', 'eTwo', 'eMatrix', 'ReFirme'],
            'price_range': (30000, 60000)
        },
        'solta': {
            'brand': 'Solta',
            'models': ['Clear+Brilliant', 'Fraxel Dual', 'Thermage FLX', 'Vaser'],
            'price_range': (35000, 70000)
        },
        'inmode': {
            'brand': 'Inmode',
            'models': ['BodyTite', 'Ignite RF', 'Lumecca', 'Optimas', 'Morpheus8'],
            'price_range': (40000, 75000)
        },
        'lutronic': {
            'brand': 'Lutronic',
            'models': ['eCo2', 'LaseMD Ultra', 'Spectra', 'Genius RF'],
            'price_range': (30000, 60000)
        },
        'fotona': {
            'brand': 'Fotona',
            'models': ['QX MAX', 'SP Dynamis', 'Starwalker', 'Timewalker'],
            'price_range': (45000, 85000)
        }
    }
    
    # Find matching brand
    for brand_key, brand_info in brand_models.items():
        if brand_key in query_lower:
            brand = brand_info['brand']
            model = random.choice(brand_info['models'])
            price_range = brand_info['price_range']
            break
    
    # If no brand found, use generic
    if brand == "Unknown":
        brand = random.choice(['Aerolase', 'Candela', 'Cynosure', 'Lumenis', 'Syneron', 'Alma', 'Cutera', 'Sciton'])
        model = f"{brand} Professional System"
        price_range = (30000, 60000)
    
    # Realistic sources with actual URLs
    sources = [
        {"name": "eBay", "url": "https://www.ebay.com/itm/", "items": random.randint(2, 5)},
        {"name": "DOTmed Auctions", "url": "https://dotmed.com/auction/item/", "items": random.randint(1, 4)},
        {"name": "BidSpotter", "url": "https://bidspotter.com/en/auctions/", "items": random.randint(1, 3)},
        {"name": "GovDeals", "url": "https://govdeals.com/index.cfm?fa=Main.Item&itemid=", "items": random.randint(1, 3)},
        {"name": "The Laser Warehouse", "url": "https://thelaserwarehouse.com/products/", "items": random.randint(1, 2)},
        {"name": "Laser Agent", "url": "https://thelaseragent.com/equipment/", "items": random.randint(1, 2)},
        {"name": "Medwow", "url": "https://medwow.com/equipment/", "items": random.randint(1, 3)},
        {"name": "Iron Horse Auction", "url": "https://ironhorseauction.com/auction/", "items": random.randint(1, 2)},
        {"name": "Kurtz Auction", "url": "https://kurtzauction.com/auction/", "items": random.randint(1, 2)},
        {"name": "Asset Recovery Services", "url": "https://assetrecovery.com/inventory/", "items": random.randint(1, 2)}
    ]
    
    results = []
    conditions = ["New", "Used - Excellent", "Used - Good", "Used - Fair", "Refurbished"]
    locations = ["California, USA", "Texas, USA", "New York, USA", "Florida, USA", "Illinois, USA", "Nevada, USA", "Pennsylvania, USA"]
    
    for source in sources:
        for i in range(source["items"]):
            if len(results) >= limit:
                break
                
            condition = random.choice(conditions)
            
            # Generate realistic price based on condition and brand
            base_price = random.randint(price_range[0], price_range[1])
            if condition == "New":
                price = base_price
            elif condition == "Used - Excellent":
                price = int(base_price * random.uniform(0.70, 0.85))
            elif condition == "Used - Good":
                price = int(base_price * random.uniform(0.55, 0.70))
            elif condition == "Used - Fair":
                price = int(base_price * random.uniform(0.40, 0.55))
            else:  # Refurbished
                price = int(base_price * random.uniform(0.65, 0.80))
            
            location = random.choice(locations)
            item_id = f"{source['name'].lower().replace(' ', '_')}_{random.randint(1000, 9999)}"
            
            results.append({
                "id": item_id,
                "title": f"{brand} {model} Laser System",
                "brand": brand,
                "model": model,
                "condition": condition,
                "price": float(price),
                "source": source["name"],
                "location": location,
                "description": f"Professional {brand} {model} laser system in {condition.lower()} condition. Perfect for aesthetic treatments and medical procedures.",
                "url": f"{source['url']}{item_id}",
                "images": [f"https://example.com/{brand.lower()}_{model.lower().replace(' ', '_')}_{i+1}.jpg"],
                "discovered_at": datetime.now().isoformat(),
                "score_overall": random.randint(80, 95),
                "status": "active"
            })
    
    # Sort by score and price
    results.sort(key=lambda x: (x['score_overall'], -x['price']), reverse=True)
    return results[:limit]
