#!/usr/bin/env python3
"""
Generate LaserMatch demand list data directly without scraping
This creates the 150+ items from the demand list for the frontend
"""

import json
import time
import random
from datetime import datetime

# Demand items from LaserMatch.io
DEMAND_ITEMS = [
    'Aerolase Lightpod Neo Elite', 'Agnes RF', 'Allergan DiamondGlow',
    'Alma Lasers Harmony', 'Alma Lasers Harmony XL', 'Alma Lasers Hybrid',
    'Alma Lasers OPUS', 'Alma Lasers Pixel CO2', 'Alma Lasers Soprano Ice',
    'Alma Lasers SOPRANO TITANIUM', 'Alma Lasers TED', 'Bluecore Iris',
    'Bluecore Iris Pi', 'Bluecore Picore', 'BTL Emface', 'BTL Exion',
    'Candela Alex TriVantage', 'Candela CO2RE', 'Candela Frax Pro',
    'Candela GentleLase Mini', 'Candela GentleLase Pro U',
    'Candela GentleMax Pro Plus', 'Candela GentleYag Mini',
    'Candela GentleYag Pro-U', 'Candela PicoWay', 'Canfield Visia',
    'Cocoon Medical Elysian Pro', 'Cocoon Medical Primelase',
    'Cutera AviClear', 'Cutera Excel V', 'Cutera Genesis Plus',
    'Cutera Secret Pro', 'Cutera Xeo', 'Cynosure Apogee Elite',
    'Cynosure Elite iQ', 'Cynosure Medlite C6', 'Cynosure MonaLisa Touch',
    'Cynosure PicoSure Pro', 'Cynosure Potenza', 'Cynosure RevLite SI',
    'Cynosure Smartskin', 'Deka Motus AX', 'Dusa Blu U',
    'Edge Systems Hydrafacial Elite', 'Energist Neogen PSR',
    'Fotona QX MAX', 'Fotona SP Dynamis', 'Fotona Starwalker',
    'Fotona Starwalker MaQX', 'Fotona Timewalker', 'Ilooda Fraxis Duo',
    'Ilooda Secret RF', 'Inmode EmbraceRF', 'Inmode Evoke',
    'Inmode Evolve', 'Inmode EvolveX', 'Inmode Morpheus8',
    'Inmode Triton', 'Inmode Votiva', 'Iridex VariLite',
    'Jeisys EdgeOne', 'Jeisys Intracel', 'Jeisys Intracel Pro',
    'Jeisys Intragen', 'Jeisys Lipocel', 'Laseroptek PALLAS',
    'Lumenis AcuPulse', 'Lumenis Lightsheer Desire',
    'Lumenis Lightsheer Quattro', 'Lumenis Trilift',
    'Lumenis Ultrapulse Alpha', 'Lutronic Clarity II',
    'Lutronic eCO2 Plus', 'Lutronic Genius RF',
    'Lutronic Hollywood Spectra', 'Lutronic LaseMD Pro',
    'Luvo Bare 808', 'Luvo Bela MD', 'Luvo Darwin',
    'Luvo Lucent IPL', 'Luvo Prolift Dual', 'Mrp MRPEN',
    'New Surg KTP', 'Ohmeda Nitronox', 'Perigee Atom',
    'Perigee Perigee CO2', 'Perigee Perigee HR', 'Perigee Perigee QS',
    'Perigee Prism LED', 'Perigee PRP+ CENTRIFUGE',
    'Quanta Discovery Pico Plus', 'Quanta System Chrome',
    'Quanta System Echo', 'Quanta System EVO Q-Plus',
    'Quanta System LIGHT 4V', 'Quantel Derma MultiFrax',
    'Sciton BBLs', 'Sciton mJoule', 'Sinclair Primelase Excellence',
    'Solta Medical Clear+Brilliant Touch', 'Solta Medical Liposonix',
    'Solta Medical Vaser 2.0', 'Syl Firm Sylfirm X',
    'Syneron VelaShape III', 'Wells Johnson Hercules Pump',
    'Wells Johnson Liposuction Aspirator', 'Zimmer Cryo Mini'
]

# Additional items from the Hot List
HOT_LIST_ITEMS = [
    'Aerolase LightPod Era Elite', 'Aesthetic Management Partners Scarlet SRF',
    'Allergan CoolSculpting', 'Allergan Coolsculpting Elite',
    'Alma Lasers Excimer 308', 'Alma Lasers Harmony XL Pro',
    'BTL Emsculpt', 'BTL Emsculpt NEO', 'BTL Emsella', 'BTL Vanquish ME',
    'Buffalo Filter Smoke Evacuator', 'Candela GentleMax Pro',
    'Candela Nordlys', 'Candela Vbeam Perfecta', 'Cutera Excel V+',
    'Cutera Xeo SA', 'Cynosure Elite+', 'Cynosure Palomar Icon',
    'Cynosure Palomar Starlux 500', 'Cynosure PicoSure', 'Cytrellis ELLACOR',
    'Deka CoolPeel / Tetra', 'Deka DenaVe', 'Deka Helix', 'Deka Motus AY',
    'Deka Smartxide DOT', 'Edge HydraFacial MD Elite', 'Ellman Medley',
    'Envy Medical Silk Peel III', 'HK Surgical Klein Touch Infiltration Pump',
    'Inmode BodyTite', 'Inmode Ignite RF', 'Inmode Lumecca', 'Inmode Optimas',
    'Lumenis Lightsheer Duet', 'Lumenis M22', 'Lumenis OptiLight',
    'Lumenis Splendor X', 'Lumenis Stellar M22', 'Lumenis UltraPulse',
    'Lumenis Ultrapulse Encore', 'Lutronic DermaV', 'Lutronic eCo2',
    'Lutronic LaseMD Ultra', 'Lutronic Spectra', 'Merz Ultherapy',
    'Microaire PAL', 'Mixto MIXTO SX', 'Novoxel Tixel', 'Pronox PRONOX SYSTEM',
    'Rohrer Phoenix', 'Sandstone Ellman Cortex', 'Sciton Joule',
    'Sciton Joule 7', 'Sciton Joule X', 'Sciton Profile',
    'She N B VirtueRF', 'Solta Medical Clear+Brilliant', 'Solta Medical Fraxel Dual',
    'Solta Medical Thermage FLX', 'Solta Medical Vaser', 'Thermi ThermiRF',
    'Venus Concept Legacy', 'Venus Concept VIVA', 'Wontech Picocare 450',
    'Zimmer Cryo6'
]

def generate_lasermatch_items():
    """Generate LaserMatch items for the database"""
    items = []
    all_items = DEMAND_ITEMS + HOT_LIST_ITEMS
    
    for i, item_name in enumerate(all_items):
        # Parse brand and model
        if ':' in item_name:
            brand, model = item_name.split(':', 1)
            brand = brand.strip()
            model = model.strip()
        else:
            brand = item_name.split()[0] if item_name.split() else 'Unknown'
            model = item_name
        
        # Generate realistic data
        item = {
            'id': f"lasermatch_{i+1:03d}",
            'title': f"Looking for {item_name}",
            'brand': brand,
            'model': model,
            'condition': 'any',
            'price': None,  # Demand items don't have prices
            'location': random.choice(['Various', 'United States', 'North America', 'Global']),
            'description': f"High demand item: {item_name}. This item is actively being sought by buyers on LaserMatch.io.",
            'url': f"https://lasermatch.io/demand/{item_name.replace(' ', '-').lower()}",
            'images': [],
            'discovered_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'source': 'LaserMatch.io',
            'status': 'in-demand',
            'category': 'demand-list',
            'availability': 'in-demand'
        }
        
        items.append(item)
    
    return items

def save_to_json(items, filename='lasermatch_items.json'):
    """Save items to JSON file"""
    with open(filename, 'w') as f:
        json.dump(items, f, indent=2)
    print(f"✅ Saved {len(items)} items to {filename}")

def print_summary(items):
    """Print summary of generated items"""
    print(f"🎯 Generated {len(items)} LaserMatch demand items")
    print(f"📊 Breakdown:")
    
    # Count by brand
    brands = {}
    for item in items:
        brand = item['brand']
        brands[brand] = brands.get(brand, 0) + 1
    
    # Show top brands
    top_brands = sorted(brands.items(), key=lambda x: x[1], reverse=True)[:10]
    for brand, count in top_brands:
        print(f"   {brand}: {count} items")
    
    print(f"📅 Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main function"""
    print("🚀 Generating LaserMatch Demand Items")
    print("=" * 50)
    
    # Generate items
    items = generate_lasermatch_items()
    
    # Print summary
    print_summary(items)
    
    # Save to file
    save_to_json(items)
    
    print("✅ Generation complete!")

if __name__ == "__main__":
    main()
