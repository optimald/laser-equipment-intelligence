"""
Asset Dictionary Management System for laser equipment classification
"""

import json
import time
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import re
from pathlib import Path


@dataclass
class Brand:
    """Brand information"""
    name: str
    aliases: List[str]
    country: str
    established_year: Optional[int]
    website: Optional[str]
    parent_company: Optional[str]
    market_share: Optional[float]
    reputation_score: float


@dataclass
class Model:
    """Model information"""
    name: str
    brand: str
    aliases: List[str]
    release_year: Optional[int]
    technology: str
    modality: str
    price_range: Tuple[float, float]
    condition_scores: Dict[str, float]
    popularity_score: float


@dataclass
class Technology:
    """Technology category"""
    name: str
    aliases: List[str]
    description: str
    applications: List[str]
    market_demand: float
    innovation_level: float


@dataclass
class Accessory:
    """Accessory/part information"""
    name: str
    compatible_models: List[str]
    category: str
    price_range: Tuple[float, float]
    availability_score: float


@dataclass
class AssetDictionary:
    """Complete asset dictionary"""
    version: str
    last_updated: str
    brands: Dict[str, Brand]
    models: Dict[str, Model]
    technologies: Dict[str, Technology]
    accessories: Dict[str, Accessory]
    search_qualifiers: Dict[str, List[str]]


class AssetDictionaryManager:
    """Manager for asset dictionary operations"""
    
    def __init__(self, dictionary_path: Optional[str] = None):
        self.dictionary_path = dictionary_path or "data/asset_dictionary.json"
        self.dictionary = self._load_dictionary()
        self.search_cache = {}
    
    def _load_dictionary(self) -> AssetDictionary:
        """Load asset dictionary from file"""
        try:
            if Path(self.dictionary_path).exists():
                with open(self.dictionary_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return self._dict_to_asset_dictionary(data)
            else:
                return self._create_default_dictionary()
        except Exception as e:
            print(f"Error loading dictionary: {e}")
            return self._create_default_dictionary()
    
    def _create_default_dictionary(self) -> AssetDictionary:
        """Create default asset dictionary"""
        return AssetDictionary(
            version="1.0.0",
            last_updated=datetime.now().isoformat(),
            brands=self._get_core_brands(),
            models=self._get_core_models(),
            technologies=self._get_core_technologies(),
            accessories=self._get_core_accessories(),
            search_qualifiers=self._get_search_qualifiers()
        )
    
    def _get_core_brands(self) -> Dict[str, Brand]:
        """Get core laser equipment brands"""
        return {
            "sciton": Brand(
                name="Sciton",
                aliases=["sciton", "sciton inc", "sciton corporation"],
                country="USA",
                established_year=1995,
                website="https://www.sciton.com",
                parent_company=None,
                market_share=0.15,
                reputation_score=0.95
            ),
            "cynosure": Brand(
                name="Cynosure",
                aliases=["cynosure", "cynosure inc", "cynosure corporation"],
                country="USA",
                established_year=1991,
                website="https://www.cynosure.com",
                parent_company="Hologic",
                market_share=0.20,
                reputation_score=0.90
            ),
            "cutera": Brand(
                name="Cutera",
                aliases=["cutera", "cutera inc", "cutera corporation"],
                country="USA",
                established_year=1998,
                website="https://www.cutera.com",
                parent_company=None,
                market_share=0.12,
                reputation_score=0.88
            ),
            "candela": Brand(
                name="Candela",
                aliases=["candela", "candela corporation", "candela medical"],
                country="USA",
                established_year=1970,
                website="https://www.candelamedical.com",
                parent_company="Syneron",
                market_share=0.18,
                reputation_score=0.92
            ),
            "lumenis": Brand(
                name="Lumenis",
                aliases=["lumenis", "lumenis ltd", "lumenis corporation"],
                country="Israel",
                established_year=1967,
                website="https://www.lumenis.com",
                parent_company="XIO Group",
                market_share=0.25,
                reputation_score=0.94
            ),
            "alma": Brand(
                name="Alma",
                aliases=["alma", "alma lasers", "alma laser ltd"],
                country="Israel",
                established_year=1999,
                website="https://www.almalasers.com",
                parent_company="Fosun Pharma",
                market_share=0.10,
                reputation_score=0.85
            ),
            "inmode": Brand(
                name="InMode",
                aliases=["inmode", "inmode ltd", "inmode corporation"],
                country="Israel",
                established_year=2008,
                website="https://www.inmodemd.com",
                parent_company=None,
                market_share=0.08,
                reputation_score=0.87
            ),
            "btl": Brand(
                name="BTL",
                aliases=["btl", "btl industries", "btl corporation"],
                country="Czech Republic",
                established_year=1993,
                website="https://www.btl.com",
                parent_company=None,
                market_share=0.05,
                reputation_score=0.82
            ),
            "lutronic": Brand(
                name="Lutronic",
                aliases=["lutronic", "lutronic corporation", "lutronic inc"],
                country="South Korea",
                established_year=1997,
                website="https://www.lutronic.com",
                parent_company=None,
                market_share=0.07,
                reputation_score=0.84
            ),
            "bison": Brand(
                name="Bison",
                aliases=["bison", "bison medical", "bison corporation"],
                country="South Korea",
                established_year=2000,
                website="https://www.bisonmedical.com",
                parent_company=None,
                market_share=0.03,
                reputation_score=0.80
            )
        }
    
    def _get_core_models(self) -> Dict[str, Model]:
        """Get core laser equipment models"""
        return {
            "sciton_joule": Model(
                name="Joule",
                brand="sciton",
                aliases=["joule", "sciton joule", "joule x", "joule xt"],
                release_year=2015,
                technology="fractional_co2",
                modality="fractional_resurfacing",
                price_range=(80000.0, 120000.0),
                condition_scores={"excellent": 0.95, "good": 0.85, "fair": 0.70, "poor": 0.50},
                popularity_score=0.90
            ),
            "cynosure_picosure": Model(
                name="PicoSure",
                brand="cynosure",
                aliases=["picsure", "cynosure picsure", "picsure pro", "picsure focus"],
                release_year=2012,
                technology="picosecond",
                modality="tattoo_removal",
                price_range=(60000.0, 90000.0),
                condition_scores={"excellent": 0.92, "good": 0.82, "fair": 0.68, "poor": 0.45},
                popularity_score=0.88
            ),
            "cutera_excel_v": Model(
                name="Excel V",
                brand="cutera",
                aliases=["excel v", "cutera excel v", "excel v plus"],
                release_year=2014,
                technology="kpt",
                modality="vascular_treatment",
                price_range=(45000.0, 70000.0),
                condition_scores={"excellent": 0.90, "good": 0.80, "fair": 0.65, "poor": 0.40},
                popularity_score=0.85
            ),
            "candela_gentlemax": Model(
                name="GentleMax Pro",
                brand="candela",
                aliases=["gentlemax pro", "candela gentlemax", "gentlemax", "gentlemax pro plus"],
                release_year=2016,
                technology="dual_wavelength",
                modality="hair_removal",
                price_range=(55000.0, 85000.0),
                condition_scores={"excellent": 0.93, "good": 0.83, "fair": 0.70, "poor": 0.50},
                popularity_score=0.92
            ),
            "lumenis_m22": Model(
                name="M22",
                brand="lumenis",
                aliases=["m22", "lumenis m22", "m22 ipl", "m22 opt"],
                release_year=2013,
                technology="ipl",
                modality="multi_application",
                price_range=(40000.0, 65000.0),
                condition_scores={"excellent": 0.91, "good": 0.81, "fair": 0.67, "poor": 0.42},
                popularity_score=0.89
            ),
            "alma_harmony": Model(
                name="Harmony XL",
                brand="alma",
                aliases=["harmony xl", "alma harmony", "harmony", "harmony xl pro"],
                release_year=2017,
                technology="multi_platform",
                modality="multi_application",
                price_range=(35000.0, 55000.0),
                condition_scores={"excellent": 0.88, "good": 0.78, "fair": 0.63, "poor": 0.38},
                popularity_score=0.83
            ),
            "inmode_secret": Model(
                name="Secret RF",
                brand="inmode",
                aliases=["secret rf", "inmode secret", "secret", "secret rf pro"],
                release_year=2018,
                technology="rf",
                modality="skin_tightening",
                price_range=(25000.0, 40000.0),
                condition_scores={"excellent": 0.86, "good": 0.76, "fair": 0.61, "poor": 0.35},
                popularity_score=0.81
            )
        }
    
    def _get_core_technologies(self) -> Dict[str, Technology]:
        """Get core laser technologies"""
        return {
            "fractional_co2": Technology(
                name="Fractional CO2",
                aliases=["fractional co2", "co2 fractional", "fractional laser", "co2 laser"],
                description="Fractional CO2 laser for skin resurfacing and rejuvenation",
                applications=["skin_resurfacing", "scar_treatment", "wrinkle_reduction", "pigmentation"],
                market_demand=0.85,
                innovation_level=0.80
            ),
            "picosecond": Technology(
                name="Picosecond",
                aliases=["picosecond", "pico", "picosecond laser", "pico laser"],
                description="Ultra-short pulse laser technology for tattoo removal and pigmentation",
                applications=["tattoo_removal", "pigmentation", "skin_rejuvenation", "acne_scars"],
                market_demand=0.90,
                innovation_level=0.95
            ),
            "ipl": Technology(
                name="Intense Pulsed Light",
                aliases=["ipl", "intense pulsed light", "pulsed light", "broadband light"],
                description="Broadband light technology for various aesthetic treatments",
                applications=["hair_removal", "pigmentation", "vascular_treatment", "skin_rejuvenation"],
                market_demand=0.95,
                innovation_level=0.70
            ),
            "rf": Technology(
                name="Radio Frequency",
                aliases=["rf", "radio frequency", "rf energy", "radiofrequency"],
                description="Radio frequency energy for skin tightening and body contouring",
                applications=["skin_tightening", "body_contouring", "cellulite_reduction", "skin_rejuvenation"],
                market_demand=0.80,
                innovation_level=0.85
            ),
            "dual_wavelength": Technology(
                name="Dual Wavelength",
                aliases=["dual wavelength", "dual laser", "two wavelength", "combined laser"],
                description="Combined laser wavelengths for enhanced treatment efficacy",
                applications=["hair_removal", "vascular_treatment", "pigmentation", "skin_rejuvenation"],
                market_demand=0.88,
                innovation_level=0.75
            ),
            "kpt": Technology(
                name="KTP",
                aliases=["ktp", "potassium titanyl phosphate", "ktp laser", "green laser"],
                description="Potassium titanyl phosphate laser for vascular and pigmentation treatment",
                applications=["vascular_treatment", "pigmentation", "skin_rejuvenation", "hair_removal"],
                market_demand=0.75,
                innovation_level=0.65
            )
        }
    
    def _get_core_accessories(self) -> Dict[str, Accessory]:
        """Get core accessories and parts"""
        return {
            "handpiece_co2": Accessory(
                name="CO2 Handpiece",
                compatible_models=["sciton_joule", "lumenis_m22"],
                category="handpiece",
                price_range=(5000.0, 15000.0),
                availability_score=0.85
            ),
            "handpiece_ipl": Accessory(
                name="IPL Handpiece",
                compatible_models=["lumenis_m22", "alma_harmony"],
                category="handpiece",
                price_range=(3000.0, 8000.0),
                availability_score=0.90
            ),
            "cooling_system": Accessory(
                name="Cooling System",
                compatible_models=["cynosure_picosure", "cutera_excel_v"],
                category="cooling",
                price_range=(2000.0, 5000.0),
                availability_score=0.95
            ),
            "foot_pedal": Accessory(
                name="Foot Pedal",
                compatible_models=["sciton_joule", "cynosure_picosure", "cutera_excel_v"],
                category="control",
                price_range=(500.0, 1500.0),
                availability_score=0.98
            ),
            "protective_goggles": Accessory(
                name="Protective Goggles",
                compatible_models=["sciton_joule", "cynosure_picosure", "cutera_excel_v"],
                category="safety",
                price_range=(100.0, 300.0),
                availability_score=0.99
            )
        }
    
    def _get_search_qualifiers(self) -> Dict[str, List[str]]:
        """Get search qualifiers for different categories"""
        return {
            "condition": ["excellent", "good", "fair", "poor", "used", "refurbished", "as-is"],
            "price_range": ["under_10k", "10k_25k", "25k_50k", "50k_100k", "over_100k"],
            "technology": ["co2", "ipl", "rf", "picosecond", "dual_wavelength", "kpt"],
            "modality": ["hair_removal", "tattoo_removal", "skin_resurfacing", "vascular_treatment", "pigmentation"],
            "location": ["usa", "europe", "asia", "canada", "australia"],
            "year": ["2020_plus", "2015_2019", "2010_2014", "pre_2010"]
        }
    
    def _dict_to_asset_dictionary(self, data: Dict[str, Any]) -> AssetDictionary:
        """Convert dictionary data to AssetDictionary object"""
        brands = {k: Brand(**v) for k, v in data.get('brands', {}).items()}
        models = {k: Model(**v) for k, v in data.get('models', {}).items()}
        technologies = {k: Technology(**v) for k, v in data.get('technologies', {}).items()}
        accessories = {k: Accessory(**v) for k, v in data.get('accessories', {}).items()}
        
        return AssetDictionary(
            version=data.get('version', '1.0.0'),
            last_updated=data.get('last_updated', datetime.now().isoformat()),
            brands=brands,
            models=models,
            technologies=technologies,
            accessories=accessories,
            search_qualifiers=data.get('search_qualifiers', {})
        )
    
    def save_dictionary(self):
        """Save dictionary to file"""
        try:
            # Ensure directory exists
            Path(self.dictionary_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to dictionary
            data = {
                'version': self.dictionary.version,
                'last_updated': datetime.now().isoformat(),
                'brands': {k: asdict(v) for k, v in self.dictionary.brands.items()},
                'models': {k: asdict(v) for k, v in self.dictionary.models.items()},
                'technologies': {k: asdict(v) for k, v in self.dictionary.technologies.items()},
                'accessories': {k: asdict(v) for k, v in self.dictionary.accessories.items()},
                'search_qualifiers': self.dictionary.search_qualifiers
            }
            
            with open(self.dictionary_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error saving dictionary: {e}")
            return False
    
    def add_brand(self, brand: Brand):
        """Add a new brand to the dictionary"""
        self.dictionary.brands[brand.name.lower()] = brand
        self.save_dictionary()
    
    def add_model(self, model: Model):
        """Add a new model to the dictionary"""
        self.dictionary.models[model.name.lower()] = model
        self.save_dictionary()
    
    def add_technology(self, technology: Technology):
        """Add a new technology to the dictionary"""
        self.dictionary.technologies[technology.name.lower()] = technology
        self.save_dictionary()
    
    def add_accessory(self, accessory: Accessory):
        """Add a new accessory to the dictionary"""
        self.dictionary.accessories[accessory.name.lower()] = accessory
        self.save_dictionary()
    
    def search_brand(self, query: str) -> List[Brand]:
        """Search for brands by query"""
        query_lower = query.lower()
        results = []
        
        for brand in self.dictionary.brands.values():
            if (query_lower in brand.name.lower() or 
                any(query_lower in alias.lower() for alias in brand.aliases)):
                results.append(brand)
        
        return results
    
    def search_model(self, query: str) -> List[Model]:
        """Search for models by query"""
        query_lower = query.lower()
        results = []
        
        for model in self.dictionary.models.values():
            if (query_lower in model.name.lower() or 
                any(query_lower in alias.lower() for alias in model.aliases)):
                results.append(model)
        
        return results
    
    def search_technology(self, query: str) -> List[Technology]:
        """Search for technologies by query"""
        query_lower = query.lower()
        results = []
        
        for technology in self.dictionary.technologies.values():
            if (query_lower in technology.name.lower() or 
                any(query_lower in alias.lower() for alias in technology.aliases)):
                results.append(technology)
        
        return results
    
    def get_compatible_accessories(self, model_name: str) -> List[Accessory]:
        """Get accessories compatible with a specific model"""
        compatible = []
        
        for accessory in self.dictionary.accessories.values():
            if model_name.lower() in [m.lower() for m in accessory.compatible_models]:
                compatible.append(accessory)
        
        return compatible
    
    def get_models_by_technology(self, technology: str) -> List[Model]:
        """Get models that use a specific technology"""
        results = []
        
        for model in self.dictionary.models.values():
            if model.technology.lower() == technology.lower():
                results.append(model)
        
        return results
    
    def get_models_by_brand(self, brand: str) -> List[Model]:
        """Get models from a specific brand"""
        results = []
        
        for model in self.dictionary.models.values():
            if model.brand.lower() == brand.lower():
                results.append(model)
        
        return results
    
    def get_dictionary_stats(self) -> Dict[str, Any]:
        """Get dictionary statistics"""
        return {
            'version': self.dictionary.version,
            'last_updated': self.dictionary.last_updated,
            'total_brands': len(self.dictionary.brands),
            'total_models': len(self.dictionary.models),
            'total_technologies': len(self.dictionary.technologies),
            'total_accessories': len(self.dictionary.accessories),
            'search_qualifiers': len(self.dictionary.search_qualifiers)
        }
    
    def export_dictionary(self, format: str = 'json') -> str:
        """Export dictionary in specified format"""
        if format == 'json':
            return json.dumps({
                'version': self.dictionary.version,
                'last_updated': self.dictionary.last_updated,
                'brands': {k: asdict(v) for k, v in self.dictionary.brands.items()},
                'models': {k: asdict(v) for k, v in self.dictionary.models.items()},
                'technologies': {k: asdict(v) for k, v in self.dictionary.technologies.items()},
                'accessories': {k: asdict(v) for k, v in self.dictionary.accessories.items()},
                'search_qualifiers': self.dictionary.search_qualifiers
            }, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def import_dictionary(self, data: str, format: str = 'json'):
        """Import dictionary from data"""
        if format == 'json':
            imported_data = json.loads(data)
            self.dictionary = self._dict_to_asset_dictionary(imported_data)
            self.save_dictionary()
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def update_brand_reputation(self, brand_name: str, new_score: float):
        """Update brand reputation score"""
        if brand_name.lower() in self.dictionary.brands:
            self.dictionary.brands[brand_name.lower()].reputation_score = new_score
            self.save_dictionary()
    
    def update_model_popularity(self, model_name: str, new_score: float):
        """Update model popularity score"""
        if model_name.lower() in self.dictionary.models:
            self.dictionary.models[model_name.lower()].popularity_score = new_score
            self.save_dictionary()
    
    def get_emerging_brands_2025(self) -> List[str]:
        """Get emerging brands for 2025"""
        # This would be updated with actual emerging brands
        return [
            "venus_concept",
            "candela_gentlemax",
            "cutera_truesculpt",
            "alma_soprano",
            "inmode_morpheus8"
        ]
    
    def get_international_brands(self) -> List[str]:
        """Get international brands"""
        international = []
        
        for brand in self.dictionary.brands.values():
            if brand.country not in ['USA', 'United States']:
                international.append(brand.name)
        
        return international
    
    def get_2025_releases(self) -> List[str]:
        """Get 2025 product releases"""
        # This would be updated with actual 2025 releases
        return [
            "sciton_joule_xt",
            "cynosure_picosure_focus",
            "cutera_excel_v_plus",
            "candela_gentlemax_pro_plus",
            "lumenis_m22_opt_plus"
        ]
