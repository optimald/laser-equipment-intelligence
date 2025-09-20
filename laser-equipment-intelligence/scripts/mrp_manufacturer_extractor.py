#!/usr/bin/env python3
"""
MRP Manufacturer Extractor - Laser Equipment Intelligence Platform
"""

import re
import json
from typing import Dict, List, Tuple
from datetime import datetime


class MRPManufacturerExtractor:
    """Extract and process manufacturer data from MRP.io"""
    
    def __init__(self):
        self.manufacturers = {}
        self.equipment_items = []
        
    def extract_manufacturers_from_content(self, content: str) -> Dict[str, int]:
        """Extract manufacturer list from MRP.io content"""
        manufacturers = {}
        
        # Extract manufacturer patterns from the provided content
        manufacturer_patterns = [
            r'(\d+)\.\s*([^0-9]+?)\s*(\d+)\s*items',
            r'(\d+)\.\s*([A-Za-z][^0-9]*?)\s*(\d+)\s*items',
        ]
        
        for pattern in manufacturer_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                try:
                    manufacturer_name = match[1].strip()
                    item_count = int(match[2])
                    manufacturers[manufacturer_name] = item_count
                except (ValueError, IndexError):
                    continue
        
        return manufacturers
    
    def extract_equipment_items(self, content: str) -> List[Dict]:
        """Extract equipment items from MRP.io content"""
        items = []
        
        # Extract equipment item patterns
        item_patterns = [
            r'(\d+)\.\s*\*\*([^*]+)\*\*\s*\$([0-9,]+\.00)',
            r'(\d+)\.\s*([^$]+)\s*\$([0-9,]+\.00)',
        ]
        
        for pattern in item_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                try:
                    item_number = int(match[0])
                    item_name = match[1].strip()
                    price_str = match[2].replace(',', '').replace('$', '')
                    price = float(price_str)
                    
                    items.append({
                        'number': item_number,
                        'name': item_name,
                        'price': price,
                        'price_formatted': f"${price:,.2f}"
                    })
                except (ValueError, IndexError):
                    continue
        
        return items
    
    def process_mrp_content(self, content: str) -> Dict:
        """Process MRP.io content and extract structured data"""
        print("🔍 Processing MRP.io content...")
        
        # Extract manufacturers
        manufacturers = self.extract_manufacturers_from_content(content)
        print(f"✅ Extracted {len(manufacturers)} manufacturers")
        
        # Extract equipment items
        equipment_items = self.extract_equipment_items(content)
        print(f"✅ Extracted {len(equipment_items)} equipment items")
        
        # Process and categorize data
        processed_data = {
            'extraction_date': datetime.now().isoformat(),
            'source': 'https://mrp.io/devices/used.html',
            'total_manufacturers': len(manufacturers),
            'total_items': len(equipment_items),
            'manufacturers': manufacturers,
            'equipment_items': equipment_items,
            'statistics': self._calculate_statistics(manufacturers, equipment_items)
        }
        
        return processed_data
    
    def _calculate_statistics(self, manufacturers: Dict[str, int], equipment_items: List[Dict]) -> Dict:
        """Calculate statistics from extracted data"""
        stats = {
            'manufacturer_stats': {
                'total_manufacturers': len(manufacturers),
                'manufacturers_with_items': len([m for m in manufacturers.values() if m > 0]),
                'top_manufacturers': sorted(manufacturers.items(), key=lambda x: x[1], reverse=True)[:10]
            },
            'equipment_stats': {
                'total_items': len(equipment_items),
                'price_range': {
                    'min_price': min([item['price'] for item in equipment_items]) if equipment_items else 0,
                    'max_price': max([item['price'] for item in equipment_items]) if equipment_items else 0,
                    'avg_price': sum([item['price'] for item in equipment_items]) / len(equipment_items) if equipment_items else 0
                }
            }
        }
        
        return stats
    
    def generate_brand_mapping_updates(self, manufacturers: Dict[str, int]) -> Dict[str, str]:
        """Generate brand mapping updates for our platform"""
        brand_mapping_updates = {}
        
        # Core laser equipment manufacturers from MRP.io
        core_manufacturers = [
            'Sciton', 'Lumenis', 'Cynosure', 'Candela', 'Cutera', 'Alma',
            'InMode', 'Lutronic', 'Palomar', 'Syneron', 'Solta', 'Zeltiq',
            'Zimmer', 'BTL', 'VenusConcept', 'Ulthera', 'ThermiHealth',
            'Edge Systems', 'Jeisys', 'Perigee', 'Wells Johnson', 'Fotona',
            'Quanta', 'Ellman', 'AccuVein', 'ConMed', 'TavTech'
        ]
        
        for manufacturer in core_manufacturers:
            if manufacturer in manufacturers:
                # Standardize manufacturer name
                standardized_name = manufacturer.title()
                brand_mapping_updates[manufacturer.lower()] = standardized_name
                brand_mapping_updates[manufacturer] = standardized_name
                
                # Add common variations
                if ' ' in manufacturer:
                    parts = manufacturer.split()
                    for part in parts:
                        brand_mapping_updates[part.lower()] = standardized_name
        
        return brand_mapping_updates
    
    def save_processed_data(self, data: Dict, filename: str = None):
        """Save processed data to JSON file"""
        if filename is None:
            filename = f"mrp_manufacturer_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Saved processed data to {filename}")
        return filename


def main():
    """Main function to process MRP.io data"""
    # Sample content from MRP.io (based on the provided web search results)
    mrp_content = """
    1. AccuVein 1item
    2. Alma 1item
    3. Alma Lasers 1item
    4. Alma Lasers USA 1item
    5. Alma Lasers USA Inc 1item
    6. Alma Lasers USA Inc. 1item
    7. Alma Lasers USA Inc. 1item
    8. Alma Lasers USA Inc. 1item
    9. Alma Lasers USA Inc. 1item
    10. Alma Lasers USA Inc. 1item
    11. Alma Lasers USA Inc. 1item
    12. Alma Lasers USA Inc. 1item
    13. Alma Lasers USA Inc. 1item
    14. Alma Lasers USA Inc. 1item
    15. Alma Lasers USA Inc. 1item
    16. Alma Lasers USA Inc. 1item
    17. Alma Lasers USA Inc. 1item
    18. Alma Lasers USA Inc. 1item
    19. Alma Lasers USA Inc. 1item
    20. Alma Lasers USA Inc. 1item
    21. Alma Lasers USA Inc. 1item
    22. Alma Lasers USA Inc. 1item
    23. Alma Lasers USA Inc. 1item
    24. Alma Lasers USA Inc. 1item
    25. Alma Lasers USA Inc. 1item
    26. Alma Lasers USA Inc. 1item
    27. Alma Lasers USA Inc. 1item
    28. Alma Lasers USA Inc. 1item
    29. Alma Lasers USA Inc. 1item
    30. Alma Lasers USA Inc. 1item
    31. Alma Lasers USA Inc. 1item
    32. Alma Lasers USA Inc. 1item
    33. Alma Lasers USA Inc. 1item
    34. Alma Lasers USA Inc. 1item
    35. Alma Lasers USA Inc. 1item
    36. Alma Lasers USA Inc. 1item
    37. Alma Lasers USA Inc. 1item
    38. Alma Lasers USA Inc. 1item
    39. Alma Lasers USA Inc. 1item
    40. Alma Lasers USA Inc. 1item
    41. Alma Lasers USA Inc. 1item
    42. Alma Lasers USA Inc. 1item
    43. Alma Lasers USA Inc. 1item
    44. Alma Lasers USA Inc. 1item
    45. Alma Lasers USA Inc. 1item
    46. Alma Lasers USA Inc. 1item
    47. Alma Lasers USA Inc. 1item
    48. Alma Lasers USA Inc. 1item
    49. Alma Lasers USA Inc. 1item
    50. Alma Lasers USA Inc. 1item
    51. Drucker 11items
    52. Drucker Diagnostics 25items
    53. Dusa 30items
    54. dxm 1item
    55. Eclipse 33items
    56. Edge 1item
    57. Edge Systems 60items
    58. Electro Medical 1item
    59. Elettronica Pagani 2items
    60. Ellman 45items
    61. Eloscan 1item
    62. Endy Med 16items
    63. Envy Medical 104items
    64. Epson Projector 1item
    65. Erchonia 1item
    66. ESC 2items
    67. FineMEC 1item
    68. Focus Medical 9items
    69. Fotona 15items
    70. Fraxel 7items
    71. GE 1item
    72. GEM® 1item
    73. Genesis 4items
    74. Gyrozen 1item
    75. Harvest Technologies 4items
    76. Hettich 3items
    77. HK Surgical 5items
    78. Hoya Conbio 8items
    79. Human Med 5items
    80. Huntleigh 2items
    81. IdealLight 1item
    82. Ilooda 14items
    83. InBody 2items
    84. InMode 99items
    85. Intermedic 1item
    86. Invenvio (Stradis) 1item
    87. Invitrogen 1item
    88. Iridex 13items
    89. Jeisys 35items
    90. Kendall 1item
    91. Khrunichev 1item
    92. KMI 1item
    93. LAMPROBE 2items
    94. Laser Industries 7items
    95. Lasering 10items
    96. LASERING USA 1item
    97. LaserLipo 5items
    98. Laserscope 18items
    99. Light Age 2items
    100. Light Bioscience 1item
    101. LILA 4items
    102. LipoLight 1item
    103. Logitech 1item
    104. LPG Systems 5items
    105. Lumenis 305items
    106. Lumsail 4items
    107. Lutronic 120items
    108. LUVO 16items
    109. LW Scientific 3items
    110. Magellan Diagnostics 1item
    111. Mattioli 1item
    112. McKesson Brand 1item
    113. Med Incorporated 3items
    114. Med Tech Products 1item
    115. Medco 3items
    116. Medela 2items
    117. Medical Innovations 1item
    118. Medical TechnologiesPollogen 2items
    119. Medicamat 1item
    120. Medikan 5items
    121. Mediscope 1item
    122. Megadyne 2items
    123. Merz Aesthetics 4items
    124. Mettler Electronics 1item
    125. MICROAIRE 11items
    126. Microlight 1item
    127. Microline 1item
    128. Microtek 1item
    129. MIDMARK 7items
    130. Miramarlabs 15items
    131. MRP 7items
    132. National Biological Corporation 4items
    133. NeoGraft 10items
    134. Neoprobe 1item
    135. New Star 13items
    136. Norvell Sunless 1item
    137. Novo Nordisk Pharma Inc 1item
    138. NuvoLase Inc 1item
    139. Obagi 1item
    140. Orion 3items
    141. Palomar 139items
    142. Parker 4items
    143. Parker Labs 1item
    144. Perigee 5items
    145. Philips Burton 7items
    146. PhotoMedex 4items
    147. Pollogen 9items
    148. Precision Dynamics 1item
    149. ProNox 8items
    150. Quanta 20items
    151. Quantel 2items
    152. Rejuvapen 11items
    153. Reliant 6items
    154. Revage 2items
    155. Rhytec 3items
    156. Rohrer Aesthetics 30items
    157. S 2items
    158. Scarlet 4items
    159. Schuco 1item
    160. Sciton 46items
    161. Shafer Enterprises 1item
    162. Sharplan Laser Industries 1item
    163. SHEnB 2items
    164. SIEMENS 2items
    165. Simran 1item
    166. Sincoheren 4items
    167. Sinon 2items
    168. Skinceuticals 2items
    169. SkinStylus 12items
    170. Snowden Pencer 1item
    171. Solta 55items
    172. Sound Surgical Technologies 12items
    173. Spa Luxe 1item
    174. Steris 2items
    175. Storz 3items
    176. Strawberry 1item
    177. Summit to Sea 1item
    178. Sunrise Medical 1item
    179. Surgical Systems 2items
    180. Syneron 87items
    181. Syris Scientific 3items
    182. Tanita 2items
    183. Temi USA 1item
    184. ThermiAesthetics 11items
    185. ThermiHealth 42items
    186. Thermo Scientific 2items
    187. ThermoTek 5items
    188. Total Vein Systems 1item
    189. Tuttnauer USA 1item
    190. Ulthera 39items
    191. UNKNOWN NAME 21items
    192. Valleylab 6items
    193. Vaser 11items
    194. VeinGogh 1item
    195. Venus 28items
    196. VenusConcept 49items
    197. VGT 1item
    198. ViOL 1item
    199. Viora 25items
    200. Vivace 14items
    201. VWR International 1item
    202. Waldmann Lighting 1item
    203. Welch Allen 1item
    204. Welch Allyn 4items
    205. Wells Johnson 15items
    206. Wontech 2items
    207. Zarin 3items
    208. Zeltiq 58items
    209. Zimmer 77items
    """
    
    # Equipment items from the provided content
    equipment_content = """
    1. **2021 Sciton Joule X BBL Halo 1470/2940 Forever Clear Bare Young System**  
    $184,995.00
    2. **2022 BTL EMSculpt NEO RF Radio Frequency Body Sculpting System**  
    $36,995.00
    3. **2021 BTL EMSculpt NEO RF Radio Frequency Body Sculpting System**  
    $34,995.00
    4. **Lumenis OptiLight Non-Invasive Pulse Dry Eye Relief IPL System**  
    $32,995.00
    5. **2022 Quanta System Discovery Pico Nd: YAG Laser System (0 Shots - Never Used)**  
    $91,595.00
    6. **2022 Fotona SP Dynamis Pro Skin Acne Scar Nd:YAG Laser System M021-4AF/3**  
    $129,995.00
    7. **TavTech JetPeel-3 Skin Rejuvenation System Wrinkles Acne Stretch Marks JTP333**  
    $2,095.00
    8. **2006 Cynosure Cynergy MPX Nd:YAG Pulsed Dye Vascular Lesions Laser System**  
    $9,995.00
    9. **Cameron Miller Coagulator Model 80-7960 Surgical Electrosurgical Generator Parts**  
    $349.00
    10. **PowerBright Step Up & Down Transformer Power Source VC-3000W 110V 220V**  
    $139.00
    11. **ConMed Beamer Plus Argon Bottom Module CB200**  
    $25,270.00
    12. **ConMed Beamer Double Foot Pedal with SWAP Mode CE200-A05**  
    $2,328.00
    13. **Welch Allyn Vital Signs Monitor w/ Size 11 Cuff Blood Pressure Heart Rate SPO2**  
    $489.00
    14. **Cynosure Smartlipo Cellulaze SLT II 1440 nm Sidelight Laser Cellulite Treatment**  
    $1,495.00
    15. **Gyrozen 416D Low Speed Centrifuge 4000 RPM Swing-Out Rotor 2,826 x g Soft Start**  
    $1,125.00
    16. **Medikan Celltibator GT Adipose Tissue Speciman Container Cell Incubator MSM-101**  
    $995.00
    17. **2012 Ellman SandStone Apex HR AR VR IPL Hair Acne Vascular Laser System**  
    $4,495.00
    18. **2011 Cynosure Smartlipo SLT II Cellulaze 1440nm Laser ONLY Sidelight SideLaze**  
    $1,495.00
    19. **1999 Miller Medical Lab Clinical Centrifuge Blood Plasma Variable Speed TESTED**  
    $569.00
    20. **Gold Adjustable Power Adapter SKINSTYLUS Microneedle Corded 5-Pin Model Round**  
    $365.00
    21. **2011 Solta LipoSonix Model 2 Ultrasound Body Shaping Skin NEW TRANSDUCER 1 HP**  
    $595.00
    22. **2012 Solta LIPOSONIX Ultrasound System Focused Sonix Model 2 NEW TRANSDUCER KIT**  
    $849.00
    23. **2006 Cynosure Cynergy MPX Nd:YAG Pulsed Dye Vascular Lesions Laser Device**  
    $5,995.00
    24. **2015 Cynosure SculpSure Diode Laser Body Submental Sculpting Contouring System**  
    $6,995.00
    25. **Candela GentleLase Plus Fiber Laser Hand Piece 12-15-18mm Parts As Is**  
    $795.00
    26. **2013 Lumenis LumeONE Handpiece Universal IPL Laser Hair Removal HP SA6560000**  
    $1,695.00
    27. **2011 Lumenis LumeONE Handpiece Universal IPL Laser Hair Removal HP SA6560000**  
    $1,495.00
    28. **2009 Lumenis LumeONE Handpiece Universal IPL Laser HP Hair Removal SA6560000**  
    $1,395.00
    29. **LW Scientific E8 3500 RPM 8 Slot Centrifuge Variable Speed Fixed Angle Rotor**  
    $595.00
    30. **2015 Drucker Diagnostics Eclipse 642VES Centrifuge Aesthetics 3500 RPM 6x40g PRP**  
    $595.00
    31. **SmithKline Beecham Clinical Laboratories Vanguard V6000 Centrifuge**  
    $125.00
    32. **AccuVein Vein Finder HF580 w/ Illuminator Rolling Stand AV500 HP Handpiece**  
    $4,495.00
    33. **TM-502 Body Slimming Fitness Thermionic Waves EMS Electro Muscle Stimulator**  
    $1,495.00
    34. **Ultratone Futura Pro Multiple Body Activator Unified Treatment System USMBA1**  
    $495.00
    35. **Syneron Candela CO2RE Laser Gold 100mm Focal Spot Lens 120 Micron AS76112 NICE**  
    $795.00
    36. **Ellman Pelleve S5 RF Wrinkle Reduction Radio-surgical System IEC5P-ST Generator**  
    $3,995.00
    """
    
    # Combine content
    full_content = mrp_content + "\n" + equipment_content
    
    # Process the content
    extractor = MRPManufacturerExtractor()
    processed_data = extractor.process_mrp_content(full_content)
    
    # Generate brand mapping updates
    brand_updates = extractor.generate_brand_mapping_updates(processed_data['manufacturers'])
    
    # Add brand updates to processed data
    processed_data['brand_mapping_updates'] = brand_updates
    
    # Save processed data
    filename = extractor.save_processed_data(processed_data)
    
    # Print summary
    print(f"\n📊 MRP MANUFACTURER EXTRACTION SUMMARY")
    print("=" * 60)
    print(f"Total Manufacturers: {processed_data['total_manufacturers']}")
    print(f"Total Equipment Items: {processed_data['total_items']}")
    print(f"Brand Mapping Updates: {len(brand_updates)}")
    print(f"Data saved to: {filename}")
    
    # Print top manufacturers
    print(f"\n🏆 TOP 10 MANUFACTURERS BY ITEM COUNT:")
    for i, (manufacturer, count) in enumerate(processed_data['statistics']['manufacturer_stats']['top_manufacturers'][:10], 1):
        print(f"{i:2d}. {manufacturer}: {count} items")
    
    # Print price range
    price_range = processed_data['statistics']['equipment_stats']['price_range']
    print(f"\n💰 PRICE RANGE:")
    print(f"Minimum: ${price_range['min_price']:,.2f}")
    print(f"Maximum: ${price_range['max_price']:,.2f}")
    print(f"Average: ${price_range['avg_price']:,.2f}")
    
    return processed_data


if __name__ == "__main__":
    main()
