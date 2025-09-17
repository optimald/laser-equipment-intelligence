#!/usr/bin/env python3
"""
Update Brand Mapping with MRP.io Data - Laser Equipment Intelligence Platform
"""

import sys
import os
import json
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

try:
    from laser_intelligence.utils.brand_mapping import BrandMapper
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)


class BrandMappingUpdater:
    """Update brand mapping with MRP.io manufacturer data"""
    
    def __init__(self):
        self.brand_mapper = BrandMapper()
        self.mrp_data = None
        self.updates_applied = 0
        
    def load_mrp_data(self, filename: str):
        """Load MRP.io manufacturer data"""
        try:
            with open(filename, 'r') as f:
                self.mrp_data = json.load(f)
            print(f"✅ Loaded MRP data: {self.mrp_data['total_manufacturers']} manufacturers")
            return True
        except Exception as e:
            print(f"❌ Error loading MRP data: {e}")
            return False
    
    def generate_brand_mapping_updates(self) -> dict:
        """Generate comprehensive brand mapping updates from MRP data"""
        if not self.mrp_data:
            print("❌ No MRP data loaded")
            return {}
        
        updates = {}
        manufacturers = self.mrp_data['manufacturers']
        
        # Core laser equipment manufacturers from MRP.io
        core_manufacturers = [
            'Sciton', 'Lumenis', 'Cynosure', 'Candela', 'Cutera', 'Alma',
            'InMode', 'Lutronic', 'Palomar', 'Syneron', 'Solta', 'Zeltiq',
            'Zimmer', 'BTL', 'VenusConcept', 'Ulthera', 'ThermiHealth',
            'Edge Systems', 'Jeisys', 'Perigee', 'Wells Johnson', 'Fotona',
            'Quanta', 'Ellman', 'AccuVein', 'ConMed', 'TavTech', 'Envy Medical',
            'Iridex', 'Laserscope', 'Light Age', 'LILA', 'LPG Systems',
            'Lumsail', 'LUVO', 'LW Scientific', 'Med Incorporated', 'Medco',
            'Medela', 'Medical TechnologiesPollogen', 'Medikan', 'Megadyne',
            'Merz Aesthetics', 'Mettler Electronics', 'MICROAIRE', 'Microlight',
            'Microline', 'Microtek', 'MIDMARK', 'Miramarlabs', 'MRP',
            'National Biological Corporation', 'NeoGraft', 'Neoprobe',
            'New Star', 'Norvell Sunless', 'Novo Nordisk Pharma Inc',
            'NuvoLase Inc', 'Obagi', 'Orion', 'Parker', 'Parker Labs',
            'Philips Burton', 'PhotoMedex', 'Pollogen', 'Precision Dynamics',
            'ProNox', 'Quantel', 'Rejuvapen', 'Reliant', 'Revage', 'Rhytec',
            'Rohrer Aesthetics', 'Scarlet', 'Schuco', 'Shafer Enterprises',
            'Sharplan Laser Industries', 'SHEnB', 'SIEMENS', 'Simran',
            'Sincoheren', 'Sinon', 'Skinceuticals', 'SkinStylus',
            'Snowden Pencer', 'Sound Surgical Technologies', 'Spa Luxe',
            'Steris', 'Storz', 'Strawberry', 'Summit to Sea', 'Sunrise Medical',
            'Surgical Systems', 'Syris Scientific', 'Tanita', 'Temi USA',
            'ThermiAesthetics', 'Thermo Scientific', 'ThermoTek',
            'Total Vein Systems', 'Tuttnauer USA', 'UNKNOWN NAME',
            'Valleylab', 'Vaser', 'VeinGogh', 'Venus', 'VGT', 'ViOL',
            'Viora', 'Vivace', 'VWR International', 'Waldmann Lighting',
            'Welch Allen', 'Welch Allyn', 'Wontech', 'Zarin'
        ]
        
        for manufacturer in core_manufacturers:
            if manufacturer in manufacturers:
                # Standardize manufacturer name
                standardized_name = manufacturer.title()
                
                # Add various forms of the manufacturer name
                updates[manufacturer.lower()] = standardized_name
                updates[manufacturer] = standardized_name
                
                # Add common variations
                if ' ' in manufacturer:
                    parts = manufacturer.split()
                    for part in parts:
                        if len(part) > 2:  # Skip short words
                            updates[part.lower()] = standardized_name
                
                # Add common suffixes/prefixes
                if manufacturer.endswith(' Inc'):
                    base_name = manufacturer[:-4].strip()
                    updates[base_name.lower()] = standardized_name
                    updates[base_name] = standardized_name
                
                if manufacturer.endswith(' Inc.'):
                    base_name = manufacturer[:-5].strip()
                    updates[base_name.lower()] = standardized_name
                    updates[base_name] = standardized_name
        
        return updates
    
    def test_brand_mapping_updates(self, updates: dict) -> dict:
        """Test brand mapping updates"""
        test_results = {
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'test_details': []
        }
        
        # Test with sample manufacturer names
        test_cases = [
            'sciton', 'lumenis', 'cynosure', 'candela', 'cutera', 'alma',
            'inmode', 'lutronic', 'palomar', 'syneron', 'solta', 'zeltiq',
            'zimmer', 'btl', 'venusconcept', 'ulthera', 'thermihealth',
            'edge systems', 'jeisys', 'perigee', 'wells johnson', 'fotona',
            'quanta', 'ellman', 'accuvein', 'conmed', 'tavtech'
        ]
        
        for test_case in test_cases:
            test_results['total_tests'] += 1
            
            # Test current brand mapper
            current_result = self.brand_mapper.normalize_brand(test_case)
            
            # Test with updates
            expected_result = updates.get(test_case.lower(), current_result)
            
            if current_result == expected_result:
                test_results['passed_tests'] += 1
                test_results['test_details'].append({
                    'input': test_case,
                    'current': current_result,
                    'expected': expected_result,
                    'status': 'PASS'
                })
            else:
                test_results['failed_tests'] += 1
                test_results['test_details'].append({
                    'input': test_case,
                    'current': current_result,
                    'expected': expected_result,
                    'status': 'FAIL'
                })
        
        return test_results
    
    def apply_brand_mapping_updates(self, updates: dict):
        """Apply brand mapping updates to the brand mapper"""
        print(f"🔄 Applying {len(updates)} brand mapping updates...")
        
        # Update the brand mapping dictionary
        for key, value in updates.items():
            if key not in self.brand_mapper.brand_mapping:
                self.brand_mapper.brand_mapping[key] = value
                self.updates_applied += 1
        
        print(f"✅ Applied {self.updates_applied} brand mapping updates")
    
    def generate_update_report(self, updates: dict, test_results: dict) -> dict:
        """Generate comprehensive update report"""
        report = {
            'update_date': datetime.now().isoformat(),
            'source': 'MRP.io Manufacturer Data',
            'total_updates': len(updates),
            'updates_applied': self.updates_applied,
            'test_results': test_results,
            'mrp_statistics': {
                'total_manufacturers': self.mrp_data['total_manufacturers'],
                'total_items': self.mrp_data['total_items'],
                'top_manufacturers': list(self.mrp_data['statistics']['manufacturer_stats']['top_manufacturers'][:10])
            },
            'brand_mapping_summary': {
                'total_brands': len(self.brand_mapper.brand_mapping),
                'new_brands_added': self.updates_applied,
                'coverage_improvement': f"{(self.updates_applied / len(self.brand_mapper.brand_mapping)) * 100:.1f}%"
            }
        }
        
        return report
    
    def save_update_report(self, report: dict, filename: str = None):
        """Save update report to JSON file"""
        if filename is None:
            filename = f"brand_mapping_update_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"💾 Saved update report to {filename}")
        return filename


def main():
    """Main function to update brand mapping with MRP data"""
    print("🚀 Brand Mapping Update with MRP.io Data")
    print("=" * 60)
    
    # Initialize updater
    updater = BrandMappingUpdater()
    
    # Load MRP data
    mrp_files = [f for f in os.listdir('.') if f.startswith('mrp_manufacturer_data_') and f.endswith('.json')]
    if not mrp_files:
        print("❌ No MRP data files found")
        return
    
    latest_file = sorted(mrp_files)[-1]
    print(f"📁 Using MRP data file: {latest_file}")
    
    if not updater.load_mrp_data(latest_file):
        return
    
    # Generate brand mapping updates
    print("\n🔧 Generating brand mapping updates...")
    updates = updater.generate_brand_mapping_updates()
    print(f"✅ Generated {len(updates)} brand mapping updates")
    
    # Test brand mapping updates
    print("\n🧪 Testing brand mapping updates...")
    test_results = updater.test_brand_mapping_updates(updates)
    print(f"✅ Test Results: {test_results['passed_tests']}/{test_results['total_tests']} passed")
    
    # Apply updates
    print("\n🔄 Applying brand mapping updates...")
    updater.apply_brand_mapping_updates(updates)
    
    # Generate and save report
    print("\n📊 Generating update report...")
    report = updater.generate_update_report(updates, test_results)
    report_filename = updater.save_update_report(report)
    
    # Print summary
    print(f"\n📊 BRAND MAPPING UPDATE SUMMARY")
    print("=" * 60)
    print(f"MRP Manufacturers: {report['mrp_statistics']['total_manufacturers']}")
    print(f"MRP Equipment Items: {report['mrp_statistics']['total_items']}")
    print(f"Brand Updates Generated: {report['total_updates']}")
    print(f"Updates Applied: {report['updates_applied']}")
    print(f"Test Success Rate: {(test_results['passed_tests']/test_results['total_tests'])*100:.1f}%")
    print(f"Coverage Improvement: {report['brand_mapping_summary']['coverage_improvement']}")
    print(f"Report saved to: {report_filename}")
    
    # Print top manufacturers
    print(f"\n🏆 TOP 10 MANUFACTURERS FROM MRP:")
    for i, (manufacturer, count) in enumerate(report['mrp_statistics']['top_manufacturers'], 1):
        print(f"{i:2d}. {manufacturer}: {count} items")
    
    return report


if __name__ == "__main__":
    main()
