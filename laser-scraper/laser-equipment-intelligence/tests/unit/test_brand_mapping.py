"""
Unit tests for brand mapping utility
"""

import pytest
from laser_intelligence.utils.brand_mapping import BrandMapper


class TestBrandMapper:
    """Test cases for BrandMapper class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.brand_mapper = BrandMapper()
    
    def test_normalize_brand_exact_match(self):
        """Test exact brand name matching"""
        assert self.brand_mapper.normalize_brand('sciton') == 'Sciton'
        assert self.brand_mapper.normalize_brand('cynosure') == 'Cynosure'
        assert self.brand_mapper.normalize_brand('cutera') == 'Cutera'
    
    def test_normalize_brand_case_insensitive(self):
        """Test case insensitive brand matching"""
        assert self.brand_mapper.normalize_brand('SCITON') == 'Sciton'
        assert self.brand_mapper.normalize_brand('Cynosure') == 'Cynosure'
        assert self.brand_mapper.normalize_brand('CuTeRa') == 'Cutera'
    
    def test_normalize_brand_with_spaces(self):
        """Test brand names with extra spaces"""
        assert self.brand_mapper.normalize_brand('  sciton  ') == 'Sciton'
        assert self.brand_mapper.normalize_brand('cynosure inc') == 'Cynosure'
        assert self.brand_mapper.normalize_brand('lumenis ltd') == 'Lumenis'
    
    def test_normalize_brand_unknown(self):
        """Test unknown brand names"""
        assert self.brand_mapper.normalize_brand('unknown_brand') == 'Unknown_brand'
        assert self.brand_mapper.normalize_brand('') == ''
        assert self.brand_mapper.normalize_brand(None) == ''
    
    def test_normalize_model_exact_match(self):
        """Test exact model name matching"""
        assert self.brand_mapper.normalize_model('joule', 'sciton') == 'Joule'
        assert self.brand_mapper.normalize_model('picosure', 'cynosure') == 'PicoSure'
        assert self.brand_mapper.normalize_model('gentlemax', 'candela') == 'GentleMax'
    
    def test_normalize_model_case_insensitive(self):
        """Test case insensitive model matching"""
        assert self.brand_mapper.normalize_model('JOULE', 'sciton') == 'Joule'
        assert self.brand_mapper.normalize_model('PicoSure', 'cynosure') == 'PicoSure'
        assert self.brand_mapper.normalize_model('GentleMax', 'candela') == 'GentleMax'
    
    def test_normalize_model_unknown_brand(self):
        """Test model normalization with unknown brand"""
        assert self.brand_mapper.normalize_model('unknown_model', 'unknown_brand') == 'Unknown_model'
        assert self.brand_mapper.normalize_model('joule', 'unknown_brand') == 'Joule'
    
    def test_map_modality_brand_model(self):
        """Test modality mapping by brand and model"""
        assert self.brand_mapper.map_modality('sciton', 'joule') == 'Platform System'
        assert self.brand_mapper.map_modality('cynosure', 'picosure') == 'Picosecond Laser'
        assert self.brand_mapper.map_modality('inmode', 'secret rf') == 'RF Microneedling'
    
    def test_map_modality_brand_only(self):
        """Test modality mapping by brand only"""
        assert self.brand_mapper.map_modality('sciton', 'unknown_model') == 'Laser Equipment'
        assert self.brand_mapper.map_modality('unknown_brand', 'unknown_model') == 'Laser Equipment'
    
    def test_is_high_value_brand(self):
        """Test high value brand detection"""
        assert self.brand_mapper.is_high_value_brand('sciton') == True
        assert self.brand_mapper.is_high_value_brand('cynosure') == True
        assert self.brand_mapper.is_high_value_brand('cutera') == True
        assert self.brand_mapper.is_high_value_brand('unknown_brand') == False
    
    def test_get_emerging_brands(self):
        """Test emerging brands list"""
        emerging_brands = self.brand_mapper.get_emerging_brands()
        assert 'Bluecore' in emerging_brands
        assert 'Jeisys' in emerging_brands
        assert 'Perigee' in emerging_brands
        assert len(emerging_brands) > 0
    
    def test_get_brand_variants(self):
        """Test brand variants retrieval"""
        variants = self.brand_mapper.get_brand_variants('Sciton')
        assert 'Sciton' in variants
        assert 'sciton' in variants
        assert len(variants) > 1
    
    def test_clean_text(self):
        """Test text cleaning functionality"""
        assert self.brand_mapper._clean_text('  SCITON INC  ') == 'sciton'
        assert self.brand_mapper._clean_text('Cynosure Ltd.') == 'cynosure'
        assert self.brand_mapper._clean_text('') == ''
        assert self.brand_mapper._clean_text(None) == ''
    
    def test_model_mapping_comprehensive(self):
        """Test comprehensive model mapping"""
        # Test Sciton models
        assert self.brand_mapper.normalize_model('joule', 'sciton') == 'Joule'
        assert self.brand_mapper.normalize_model('profile', 'sciton') == 'Profile'
        assert self.brand_mapper.normalize_model('bbl', 'sciton') == 'BBL'
        
        # Test Cynosure models
        assert self.brand_mapper.normalize_model('picosure', 'cynosure') == 'PicoSure'
        assert self.brand_mapper.normalize_model('picoway', 'cynosure') == 'PicoWay'
        assert self.brand_mapper.normalize_model('gentlemax pro', 'cynosure') == 'GentleMax Pro'
        
        # Test InMode models
        assert self.brand_mapper.normalize_model('secret rf', 'inmode') == 'Secret RF'
        assert self.brand_mapper.normalize_model('morpheus8', 'inmode') == 'Morpheus8'
        assert self.brand_mapper.normalize_model('emsculpt', 'inmode') == 'Emsculpt'
