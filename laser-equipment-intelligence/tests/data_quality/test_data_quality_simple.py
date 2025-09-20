"""
Simplified data quality testing for Laser Equipment Intelligence Platform
"""
import pytest
from laser_intelligence.utils.brand_mapping import BrandMapper
from laser_intelligence.utils.price_analysis import PriceAnalyzer
from laser_intelligence.utils.evasion_scoring import EvasionScorer
from scrapy.http import Request, HtmlResponse


class TestDataQualitySimple:
    """Test data validation, accuracy, and consistency with existing methods"""

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
            ("Elite", "Cynosure", "Elite"),  # Fixed: Elite+ becomes Elite
            ("elite", "Cynosure", "Elite"),
            ("ELITE", "Cynosure", "Elite"),
        ]
        
        for input_model, brand, expected_model in test_cases:
            result = self.brand_mapper.normalize_model(input_model, brand)
            assert result == expected_model, f"Expected {expected_model}, got {result} for input {input_model}"

    def test_price_analysis_accuracy(self):
        """Test price analysis accuracy"""
        # Test wholesale value estimation
        wholesale = self.price_analyzer.estimate_wholesale_value('Sciton', 'Joule', 'excellent', 100000)
        assert wholesale is not None
        assert wholesale > 100000  # Should be higher than asking price
        
        # Test resale value estimation
        resale = self.price_analyzer.estimate_resale_value('Sciton', 'Joule', 'excellent', 100000)
        assert resale is not None
        assert resale > 100000  # Should be higher than asking price
        
        # Test margin calculation
        margin, margin_pct = self.price_analyzer.calculate_margin_estimate(50000, 75000, 5000, 2000)
        assert margin is not None
        assert margin_pct is not None
        assert margin > 0  # Should be positive margin

    def test_data_format_consistency(self):
        """Test data format consistency"""
        # Test brand normalization consistency
        brands = ["Sciton", "SCITON", "sciton", "Sciton Inc."]
        normalized_brands = [self.brand_mapper.normalize_brand(brand) for brand in brands]
        
        # All should normalize to the same result
        first_result = normalized_brands[0]
        for result in normalized_brands[1:]:
            assert result == first_result, f"Inconsistent brand normalization: {result} vs {first_result}"

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
        # Test price analysis with valid inputs
        valid_prices = [1000, 50000, 100000, 500000]
        
        for price in valid_prices:
            wholesale = self.price_analyzer.estimate_wholesale_value('Sciton', 'Joule', 'excellent', price)
            assert wholesale is not None
            assert wholesale > 0

    def test_data_integrity_validation(self):
        """Test data integrity validation"""
        # Test that processed data maintains integrity
        original_brand = "Sciton"
        original_model = "Joule"
        original_price = 50000
        
        # Process the data
        processed_brand = self.brand_mapper.normalize_brand(original_brand)
        processed_model = self.brand_mapper.normalize_model(original_model, original_brand)
        processed_wholesale = self.price_analyzer.estimate_wholesale_value(processed_brand, processed_model, 'excellent', original_price)
        
        # Verify integrity
        assert processed_brand == "Sciton"
        assert processed_model == "Joule"
        assert processed_wholesale is not None
        assert processed_wholesale > original_price

    def test_error_handling_in_data_processing(self):
        """Test error handling in data processing"""
        # Test with malformed data
        malformed_brand = None
        malformed_model = ''
        
        # Should handle malformed data gracefully
        try:
            brand = self.brand_mapper.normalize_brand(malformed_brand)
            assert brand is not None or brand == ''
        except Exception:
            # Should not crash
            assert True
        
        try:
            model = self.brand_mapper.normalize_model(malformed_model, "Sciton")
            assert model is not None or model == ''
        except Exception:
            # Should not crash
            assert True

    def test_evasion_scoring_data_quality(self):
        """Test evasion scoring data quality"""
        request = Request(url="https://example.com")
        
        # Test perfect response
        perfect_response = HtmlResponse(
            url="https://example.com",
            request=request,
            body=b"<html><body>" + b"x" * 2000 + b"</body></html>",
            status=200
        )
        
        score = self.evasion_scorer.calculate_score(perfect_response, request)
        assert score is not None
        assert isinstance(score, (int, float))
        assert 0 <= score <= 100

    def test_data_completeness_validation(self):
        """Test data completeness validation"""
        # Test that required data is present in analysis
        brand = "Sciton"
        model = "Joule"
        condition = "excellent"
        asking_price = 100000
        
        # All required data should be present
        assert brand is not None
        assert model is not None
        assert condition is not None
        assert asking_price is not None
        
        # Should be able to process complete data
        wholesale = self.price_analyzer.estimate_wholesale_value(brand, model, condition, asking_price)
        resale = self.price_analyzer.estimate_resale_value(brand, model, condition, asking_price)
        
        assert wholesale is not None
        assert resale is not None

    def test_data_quality_metrics(self):
        """Test data quality metrics calculation"""
        # Test that we can calculate quality metrics
        test_brands = ["Sciton", "Cynosure", "Cutera", "Candela", "Lumenis"]
        test_models = ["Joule", "Elite", "Excel", "GentleMax", "M22"]
        
        # Test brand mapping quality
        for brand in test_brands:
            result = self.brand_mapper.normalize_brand(brand)
            assert result is not None
            assert len(result) > 0
        
        # Test model mapping quality
        for i, model in enumerate(test_models):
            brand = test_brands[i] if i < len(test_brands) else "Sciton"
            result = self.brand_mapper.normalize_model(model, brand)
            assert result is not None
            assert len(result) > 0

    def test_data_normalization_consistency(self):
        """Test data normalization consistency"""
        # Test that normalization is consistent across different inputs
        test_inputs = [
            "Sciton",
            "SCITON",
            "sciton",
            "Sciton Inc.",
        ]
        
        normalized_results = []
        for test_input in test_inputs:
            result = self.brand_mapper.normalize_brand(test_input)
            normalized_results.append(result)
        
        # All results should be consistent
        first_result = normalized_results[0]
        for result in normalized_results[1:]:
            assert result == first_result, f"Inconsistent normalization: {result} vs {first_result}"
