"""
Brand and model normalization for laser equipment
"""

import re
from typing import Dict, List, Optional, Tuple


class BrandMapper:
    """Normalize brand and model names to canonical forms"""
    
    def __init__(self):
        self.brand_mapping = self._load_brand_mapping()
        self.model_mapping = self._load_model_mapping()
        self.modality_mapping = self._load_modality_mapping()
    
    def _load_brand_mapping(self) -> Dict[str, str]:
        """Load brand normalization mapping"""
        return {
            # Core brands
            'sciton': 'Sciton',
            'cynosure': 'Cynosure',
            'cutera': 'Cutera',
            'candela': 'Candela',
            'syneron': 'Candela',  # Syneron merged with Candela
            'lumenis': 'Lumenis',
            'alma': 'Alma',
            'inmode': 'InMode',
            'btl': 'BTL',
            'lutronic': 'Lutronic',
            'bison': 'Bison',
            'deka': 'DEKA',
            'quanta': 'Quanta',
            'asclepion': 'Asclepion',
            'zimmer': 'Zimmer',
            'palomar': 'Palomar',
            'ellman': 'Ellman',
            'fotona': 'Fotona',
            
            # Emerging brands (2025)
            'bluecore': 'Bluecore',
            'jeisys': 'Jeisys',
            'perigee': 'Perigee',
            'wells johnson': 'Wells Johnson',
            'aerolase': 'Aerolase',
            'candela medical': 'Candela',
            'cynosure hologic': 'Cynosure',
            'lumenis baring': 'Lumenis',
            'alma lasers': 'Alma',
            'btl aesthetics': 'BTL',
            'bison medical': 'Bison',
            'quanta system': 'Quanta',
            'zimmer medizinsysteme': 'Zimmer',
            'palomar medical': 'Palomar',
            'ellman international': 'Ellman',
            
            # Common misspellings and variations
            'sciton inc': 'Sciton',
            'cynosure inc': 'Cynosure',
            'cutera inc': 'Cutera',
            'lumenis ltd': 'Lumenis',
            'alma lasers ltd': 'Alma',
        }
    
    def _load_model_mapping(self) -> Dict[str, Dict[str, str]]:
        """Load model normalization mapping by brand"""
        return {
            'Sciton': {
                'joule': 'Joule',
                'profile': 'Profile',
                'contour': 'Contour',
                'bbl': 'BBL',
                'm22': 'M22',
                'elite+': 'Elite+',
                'elite plus': 'Elite+',
            },
            'Cynosure': {
                'picosure': 'PicoSure',
                'picoway': 'PicoWay',
                'enlighten': 'Enlighten',
                'excel v': 'Excel V',
                'xeo': 'Xeo',
                'gentlemax pro': 'GentleMax Pro',
                'gentlemax': 'GentleMax',
            },
            'Cutera': {
                'excel v': 'Excel V',
                'truesculpt': 'TruSculpt',
                'truesculpt id': 'TruSculpt ID',
                'genesis': 'Genesis',
                'xeo': 'Xeo',
            },
            'Candela': {
                'gentlemax pro': 'GentleMax Pro',
                'gentlemax': 'GentleMax',
                'gentle yag': 'Gentle YAG',
                'gentle pro': 'Gentle Pro',
                'gentlelase': 'GentleLase',
                'gentlelase plus': 'GentleLase Plus',
            },
            'Lumenis': {
                'm22': 'M22',
                'elite+': 'Elite+',
                'elite plus': 'Elite+',
                'lightsheer': 'LightSheer',
                'lightsheer duet': 'LightSheer Duet',
                'slim': 'SLIM',
                'slim duo': 'SLIM Duo',
            },
            'Alma': {
                'harmony xl': 'Harmony XL',
                'harmony': 'Harmony',
                'soprano': 'Soprano',
                'soprano xl': 'Soprano XL',
                'soprano ice': 'Soprano ICE',
                'soprano titanium': 'Soprano Titanium',
                'opus': 'OPUS',
            },
            'InMode': {
                'secret rf': 'Secret RF',
                'morpheus8': 'Morpheus8',
                'emsculpt': 'Emsculpt',
                'emsella': 'Emsella',
                'evolve': 'Evolve',
                'evolve x': 'EvolveX',
            },
            'BTL': {
                'emsculpt': 'Emsculpt',
                'emsella': 'Emsella',
                'exilis': 'Exilis',
                'exilis ultra': 'Exilis Ultra',
                'exilis elite': 'Exilis Elite',
            },
            'Lutronic': {
                'picoway': 'PicoWay',
                'picosure': 'PicoSure',
                'infini': 'Infini',
                'infini ultra': 'Infini Ultra',
                'infini plus': 'Infini Plus',
            },
        }
    
    def _load_modality_mapping(self) -> Dict[str, str]:
        """Load modality mapping for technology categories"""
        return {
            # Platform Systems
            'joule': 'Platform System',
            'bbl': 'IPL Platform',
            'm22': 'IPL Platform',
            'elite+': 'IPL Platform',
            'gentlemax pro': 'Laser Platform',
            'picosure': 'Picosecond Laser',
            'picoway': 'Picosecond Laser',
            'enlighten': 'Picosecond Laser',
            'excel v': 'Laser Platform',
            'xeo': 'Laser Platform',
            'secret rf': 'RF Microneedling',
            'morpheus8': 'RF Microneedling',
            'emsculpt': 'HIFU Body Contouring',
            'emsella': 'EMF Pelvic Floor',
            
            # Technology Categories
            'co2': 'CO2 Laser',
            'er:yag': 'Er:YAG Laser',
            'nd:yag': 'Nd:YAG Laser',
            'alexandrite': 'Alexandrite Laser',
            'diode': 'Diode Laser',
            'ipl': 'Intense Pulsed Light',
            'rf': 'Radio Frequency',
            'hifu': 'High Intensity Focused Ultrasound',
            'cryolipolysis': 'Cryolipolysis',
            'led': 'LED Therapy',
        }
    
    def normalize_brand(self, raw_brand: str) -> str:
        """Normalize brand name to canonical form"""
        if not raw_brand:
            return ''
        
        # Clean and normalize input
        cleaned = self._clean_text(raw_brand)
        
        # Direct mapping lookup
        if cleaned in self.brand_mapping:
            return self.brand_mapping[cleaned]
        
        # Fuzzy matching for partial matches
        for key, value in self.brand_mapping.items():
            if key in cleaned or cleaned in key:
                return value
        
        # Return cleaned version if no match found
        return cleaned.replace('_', ' ').title().replace(' ', '_').replace('_B', '_b').replace('_M', '_m')
    
    def normalize_model(self, raw_model: str, brand: str) -> str:
        """Normalize model name to canonical form"""
        if not raw_model or not brand:
            return raw_model or ''
        
        # Clean and normalize input
        cleaned_model = self._clean_text(raw_model)
        normalized_brand = self.normalize_brand(brand)
        
        # Get model mapping for this brand
        brand_models = self.model_mapping.get(normalized_brand, {})
        
        # Direct mapping lookup
        if cleaned_model in brand_models:
            return brand_models[cleaned_model]
        
        # Fuzzy matching for partial matches
        for key, value in brand_models.items():
            if key in cleaned_model or cleaned_model in key:
                return value
        
        # Return cleaned version if no match found
        return cleaned_model.replace('_', ' ').title().replace(' ', '_').replace('_B', '_b').replace('_M', '_m')
    
    def map_modality(self, brand: str, model: str) -> str:
        """Map brand/model combination to modality"""
        normalized_brand = self.normalize_brand(brand)
        normalized_model = self.normalize_model(model, brand)
        
        # Try model-based mapping first
        model_key = normalized_model.lower()
        if model_key in self.modality_mapping:
            return self.modality_mapping[model_key]
        
        # Try brand-based mapping
        brand_key = normalized_brand.lower()
        if brand_key in self.modality_mapping:
            return self.modality_mapping[brand_key]
        
        # Default to generic laser equipment
        return 'Laser Equipment'
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text for matching"""
        if not text:
            return ''
        
        # Convert to lowercase
        cleaned = text.lower().strip()
        
        # Remove common prefixes/suffixes
        cleaned = re.sub(r'\b(inc|ltd|llc|corp|corporation|company)\b', '', cleaned)
        
        # Remove punctuation but preserve + character
        cleaned = re.sub(r'[^\w\s+]', '', cleaned)
        
        # Remove extra whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned
    
    def get_brand_variants(self, canonical_brand: str) -> List[str]:
        """Get all known variants of a canonical brand"""
        variants = [canonical_brand]
        
        for variant, canonical in self.brand_mapping.items():
            if canonical == canonical_brand:
                variants.append(variant)
        
        return variants
    
    def is_high_value_brand(self, brand: str) -> bool:
        """Check if brand is considered high-value"""
        high_value_brands = [
            'Sciton', 'Cynosure', 'Cutera', 'Candela', 'Lumenis',
            'Alma', 'InMode', 'BTL', 'Lutronic'
        ]
        
        normalized_brand = self.normalize_brand(brand)
        return normalized_brand in high_value_brands
    
    def get_emerging_brands(self) -> List[str]:
        """Get list of emerging brands for 2025"""
        return [
            'Bluecore', 'Jeisys', 'Perigee', 'Wells Johnson', 'Aerolase'
        ]
