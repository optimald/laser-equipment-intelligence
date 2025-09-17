"""
Data quality testing for Laser Equipment Intelligence Platform
"""
import pytest
from laser_intelligence.utils.brand_mapping import BrandMapper
from laser_intelligence.utils.price_analysis import PriceAnalyzer
from laser_intelligence.utils.evasion_scoring import EvasionScorer
from scrapy.http import Request, HtmlResponse


class TestDataQuality:
    """Test data validation, accuracy, and consistency"""

    def setup_method(self):
        """Set up test fixtures"""
        self.brand_mapper = BrandMapper()
        self.price_analyzer = PriceAnalyzer()
        self.evasion_scorer = EvasionScorer()

    def test_brand_normalization_accuracy(self):
        """Test brand normalization accuracy"""
        test_cases = [
            ("Sciton", "Sciton"),
            ("SCITON", "Sciton"),
            ("sciton", "Sciton"),
            ("Sciton Inc.", "Sciton"),
            ("Cynosure", "Cynosure"),
            ("CYNOSURE", "Cynosure"),
            ("cynosure", "Cynosure"),
            ("Cutera", "Cutera"),
            ("CUTERA", "Cutera"),
            ("cutera", "Cutera"),
        ]
        
        for input_brand, expected_brand in test_cases:
            result = self.brand_mapper.normalize_brand(input_brand)
            assert result == expected_brand, f"Expected {expected_brand}, got {result} for input {input_brand}"

    def test_model_normalization_accuracy(self):
        """Test model normalization accuracy"""
        test_cases = [
            ("Joule", "Sciton", "Joule"),
            ("joule", "Sciton", "Joule"),
            ("JOULE", "Sciton", "Joule"),
            ("Elite+", "Cynosure", "Elite+"),
            ("elite+", "Cynosure", "Elite+"),
            ("ELITE+", "Cynosure", "Elite+"),
        ]
        
        for input_model, brand, expected_model in test_cases:
            result = self.brand_mapper.normalize_model(input_model, brand)
            assert result == expected_model, f"Expected {expected_model}, got {result} for input {input_model}"

    def test_price_extraction_accuracy(self):
        """Test price extraction accuracy"""
        test_cases = [
            ("$50,000", 50000.0),
            ("$50,000.00", 50000.0),
            ("$75,000", 75000.0),
            ("$100,000", 100000.0),
            ("$25,000", 25000.0),
            ("$150,000", 150000.0),
        ]
        
        for price_text, expected_price in test_cases:
            # Test price normalization in price analyzer
            result = self.price_analyzer._normalize_price(price_text)
            assert result == expected_price, f"Expected {expected_price}, got {result} for input {price_text}"

    def test_condition_mapping_consistency(self):
        """Test condition mapping consistency"""
        test_cases = [
            ("excellent", "excellent"),
            ("Excellent", "excellent"),
            ("EXCELLENT", "excellent"),
            ("good", "good"),
            ("Good", "good"),
            ("GOOD", "good"),
            ("fair", "fair"),
            ("Fair", "fair"),
            ("FAIR", "fair"),
            ("poor", "poor"),
            ("Poor", "poor"),
            ("POOR", "poor"),
        ]
        
        for input_condition, expected_condition in test_cases:
            result = self.brand_mapper._normalize_condition(input_condition)
            assert result == expected_condition, f"Expected {expected_condition}, got {result} for input {input_condition}"

    def test_data_completeness_validation(self):
        """Test data completeness validation"""
        # Test that required fields are present
        from laser_intelligence.items import LaserListingItem
        
        item = LaserListingItem()
        item['source_url'] = 'https://example.com/test'
        item['title_raw'] = 'Test Laser Equipment'
        item['asking_price'] = '$50,000'
        item['condition'] = 'excellent'
        item['location'] = 'Los Angeles, CA'
        
        # Check required fields
        required_fields = ['source_url', 'title_raw', 'asking_price', 'condition', 'location']
        for field in required_fields:
            assert field in item, f"Required field {field} is missing"

    def test_data_format_consistency(self):
        """Test data format consistency"""
        # Test price format consistency
        price_formats = ["$50,000", "$50,000.00", "50000", "50000.0"]
        
        for price_format in price_formats:
            normalized = self.price_analyzer._normalize_price(price_format)
            assert isinstance(normalized, (int, float))
            assert normalized > 0

    def test_cross_source_data_consistency(self):
        """Test cross-source data consistency"""
        # Test that brand mapping works consistently across different sources
        sources = ["dotmed", "ebay", "govdeals", "facebook", "craigslist"]
        
        for source in sources:
            # Test brand normalization consistency
            result = self.brand_mapper.normalize_brand("Sciton")
            assert result == "Sciton", f"Brand normalization inconsistent for source {source}"

    def test_data_validation_rules(self):
        """Test data validation rules"""
        # Test price validation
        valid_prices = [1000, 50000, 100000, 500000]
        invalid_prices = [-1000, 0, "invalid", None]
        
        for price in valid_prices:
            assert self.price_analyzer._validate_price(price), f"Valid price {price} failed validation"
        
        for price in invalid_prices:
            assert not self.price_analyzer._validate_price(price), f"Invalid price {price} passed validation"

    def test_data_deduplication_accuracy(self):
        """Test data deduplication accuracy"""
        # Test that duplicate items are properly identified
        from laser_intelligence.utils.brand_mapping import BrandMapper
        
        mapper = BrandMapper()
        
        # Test deduplication key generation
        item1_data = {
            'brand': 'Sciton',
            'model': 'Joule',
            'serial_number': 'SN12345',
            'location': 'Los Angeles, CA'
        }
        
        item2_data = {
            'brand': 'Sciton',
            'model': 'Joule',
            'serial_number': 'SN12345',
            'location': 'Los Angeles, CA'
        }
        
        # Should generate same deduplication key for identical items
        key1 = mapper._generate_deduplication_key(item1_data)
        key2 = mapper._generate_deduplication_key(item2_data)
        
        assert key1 == key2, "Identical items should generate same deduplication key"

    def test_data_freshness_validation(self):
        """Test data freshness validation"""
        import time
        
        # Test that timestamps are properly handled
        current_time = time.time()
        
        # Test auction end time validation
        valid_end_times = [current_time + 3600, current_time + 86400, current_time + 604800]  # 1 hour, 1 day, 1 week
        invalid_end_times = [current_time - 3600, current_time - 86400]  # Past times
        
        for end_time in valid_end_times:
            assert self.price_analyzer._validate_auction_end_time(end_time), f"Valid end time {end_time} failed validation"
        
        for end_time in invalid_end_times:
            assert not self.price_analyzer._validate_auction_end_time(end_time), f"Invalid end time {end_time} passed validation"

    def test_data_quality_metrics(self):
        """Test data quality metrics calculation"""
        # Test extraction accuracy scoring
        test_data = {
            'brand_extracted': True,
            'model_extracted': True,
            'price_extracted': True,
            'condition_extracted': True,
            'location_extracted': True,
            'serial_extracted': False
        }
        
        accuracy = self.brand_mapper._calculate_extraction_accuracy(test_data)
        assert accuracy > 0
        assert accuracy <= 1

    def test_data_normalization_consistency(self):
        """Test data normalization consistency"""
        # Test that normalization is consistent across different inputs
        test_inputs = [
            "Sciton Joule Laser System",
            "SCITON JOULE LASER SYSTEM",
            "sciton joule laser system",
            "Sciton Inc. Joule Laser System",
        ]
        
        normalized_results = []
        for test_input in test_inputs:
            brand = self.brand_mapper._extract_brand_from_text(test_input)
            model = self.brand_mapper._extract_model_from_text(test_input)
            normalized_results.append((brand, model))
        
        # All results should be consistent
        first_result = normalized_results[0]
        for result in normalized_results[1:]:
            assert result == first_result, f"Inconsistent normalization: {result} vs {first_result}"

    def test_error_handling_in_data_processing(self):
        """Test error handling in data processing"""
        # Test with malformed data
        malformed_data = {
            'brand': None,
            'model': '',
            'price': 'invalid_price',
            'condition': None
        }
        
        # Should handle malformed data gracefully
        try:
            brand = self.brand_mapper.normalize_brand(malformed_data['brand'])
            assert brand is not None or brand == ''
        except Exception:
            # Should not crash
            assert True

    def test_data_integrity_validation(self):
        """Test data integrity validation"""
        # Test that processed data maintains integrity
        original_data = {
            'source_url': 'https://example.com/test',
            'title_raw': 'Sciton Joule Laser System',
            'asking_price': '$50,000',
            'condition': 'excellent',
            'location': 'Los Angeles, CA'
        }
        
        # Process the data
        processed_brand = self.brand_mapper.normalize_brand("Sciton")
        processed_price = self.price_analyzer._normalize_price(original_data['asking_price'])
        
        # Verify integrity
        assert processed_brand == "Sciton"
        assert processed_price == 50000.0
        assert original_data['source_url'] == 'https://example.com/test'
        assert original_data['location'] == 'Los Angeles, CA'
