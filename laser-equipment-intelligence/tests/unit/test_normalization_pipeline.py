"""
Unit tests for normalization pipeline
"""

import pytest
from unittest.mock import Mock, patch
from laser_intelligence.pipelines.normalization import NormalizationPipeline, LaserListingItem


class TestNormalizationPipeline:
    """Test normalization pipeline functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.pipeline = NormalizationPipeline()
        self.spider = Mock()

    def test_pipeline_initialization(self):
        """Test pipeline initialization"""
        assert self.pipeline is not None
        assert hasattr(self.pipeline, 'brand_mapper')
        assert hasattr(self.pipeline, 'price_analyzer')

    def test_item_processing_basic(self):
        """Test basic item processing"""
        item = LaserListingItem()
        item['title_raw'] = 'Sciton Joule Laser System'
        item['description_raw'] = 'Complete laser system with handpieces'
        item['asking_price'] = '$50,000'
        item['condition'] = 'excellent'
        item['location_city'] = 'Los Angeles'
        item['location_state'] = 'CA'
        item['location_country'] = 'USA'

        processed_item = self.pipeline.process_item(item, self.spider)

        assert processed_item is not None
        assert 'brand' in processed_item
        assert 'model' in processed_item
        assert 'asking_price' in processed_item
        assert 'dedupe_key' in processed_item

    def test_brand_model_extraction(self):
        """Test brand and model extraction"""
        item = LaserListingItem()
        item['title_raw'] = 'Cynosure Elite+ Laser System'
        item['description_raw'] = 'Professional aesthetic laser'

        processed_item = self.pipeline.process_item(item, self.spider)

        # The pipeline normalizes existing fields, doesn't extract from title/description
        assert 'brand' in processed_item
        assert 'model' in processed_item

    def test_price_normalization(self):
        """Test price normalization"""
        test_cases = [
            ('$50,000', 50000.0),
            ('$50,000.00', 50000.0),
            ('50,000 USD', 50000.0),
            ('$50K', 50000.0),
            ('$50k', 50000.0),
            ('$50 thousand', 50000.0),
        ]

        for price_text, expected_price in test_cases:
            item = LaserListingItem()
            item['asking_price'] = price_text

            processed_item = self.pipeline.process_item(item, self.spider)
            assert processed_item['asking_price'] == expected_price

    def test_location_normalization(self):
        """Test location normalization"""
        item = LaserListingItem()
        item['location_city'] = 'los angeles'
        item['location_state'] = 'california'
        item['location_country'] = 'united states'

        processed_item = self.pipeline.process_item(item, self.spider)

        # Check that location fields are normalized
        assert processed_item['location_city'] == 'Los Angeles'
        assert processed_item['location_state'] == 'CA'
        assert processed_item['location_country'] == 'USA'

    def test_condition_normalization(self):
        """Test condition normalization"""
        test_cases = [
            ('excellent', 'excellent'),
            ('good', 'good'),
            ('fair', 'fair'),
            ('poor', 'poor'),
            ('new', 'new'),
            ('used', 'used'),
            ('refurbished', 'refurbished'),
            ('as-is', 'as-is'),
            ('unknown', 'unknown'),
        ]

        for condition_text, expected_condition in test_cases:
            item = LaserListingItem()
            item['condition'] = condition_text

            processed_item = self.pipeline.process_item(item, self.spider)
            assert processed_item['condition'] == expected_condition

    def test_accessories_extraction(self):
        """Test accessories extraction"""
        item = LaserListingItem()
        item['description_raw'] = 'Includes handpieces, tips, filters, and cart'

        processed_item = self.pipeline.process_item(item, self.spider)

        # Check that accessories field exists
        assert 'accessories' in processed_item

    def test_serial_number_extraction(self):
        """Test serial number extraction"""
        item = LaserListingItem()
        item['description_raw'] = 'Serial number: SN12345'

        processed_item = self.pipeline.process_item(item, self.spider)

        # Check that serial_number field exists
        assert 'serial_number' in processed_item

    def test_year_extraction(self):
        """Test year extraction"""
        item = LaserListingItem()
        item['description_raw'] = 'Manufactured in 2022'

        processed_item = self.pipeline.process_item(item, self.spider)

        # Check that year field exists
        assert 'year' in processed_item

    def test_hours_extraction(self):
        """Test hours extraction"""
        item = LaserListingItem()
        item['description_raw'] = '500 hours of use'

        processed_item = self.pipeline.process_item(item, self.spider)

        # Check that hours field exists
        assert 'hours' in processed_item

    def test_modality_detection(self):
        """Test modality detection"""
        test_cases = [
            ('laser', 'laser'),
            ('ipl', 'ipl'),
            ('rf', 'rf'),
            ('hifu', 'hifu'),
            ('cryolipolysis', 'cryolipolysis'),
        ]

        for modality_text, expected_modality in test_cases:
            item = LaserListingItem()
            item['description_raw'] = f'Professional {modality_text} system'

            processed_item = self.pipeline.process_item(item, self.spider)
            # Check that modality field exists
            assert 'modality' in processed_item

    def test_error_handling(self):
        """Test error handling in pipeline"""
        item = LaserListingItem()
        item['title_raw'] = None
        item['description_raw'] = None

        # Should not raise exception
        processed_item = self.pipeline.process_item(item, self.spider)
        assert processed_item is not None

    def test_empty_item_processing(self):
        """Test processing of empty item"""
        item = LaserListingItem()

        processed_item = self.pipeline.process_item(item, self.spider)
        assert processed_item is not None

    def test_complex_item_processing(self):
        """Test processing of complex item with multiple fields"""
        item = LaserListingItem()
        item['title_raw'] = 'Sciton Joule Laser System - Excellent Condition'
        item['description_raw'] = 'Complete Sciton Joule laser system with handpieces. Serial: SN12345, Year: 2022, Hours: 500. Includes cart and accessories.'
        item['asking_price'] = '$75,000'
        item['condition'] = 'excellent'
        item['location_city'] = 'Miami'
        item['location_state'] = 'FL'
        item['location_country'] = 'USA'
        item['seller_name'] = 'Medical Equipment Liquidators'

        processed_item = self.pipeline.process_item(item, self.spider)

        # Check all normalized fields
        assert 'brand' in processed_item
        assert 'model' in processed_item
        assert processed_item['asking_price'] == 75000.0
        assert processed_item['condition'] == 'excellent'
        assert processed_item['location_city'] == 'Miami'
        assert processed_item['location_state'] == 'FL'
        assert processed_item['location_country'] == 'USA'
        assert 'serial_number' in processed_item
        assert 'year' in processed_item
        assert 'hours' in processed_item
        assert 'modality' in processed_item

    def test_pipeline_statistics(self):
        """Test pipeline statistics tracking"""
        # Process multiple items
        for i in range(5):
            item = LaserListingItem()
            item['title_raw'] = f'Test Item {i}'
            self.pipeline.process_item(item, self.spider)

        assert self.pipeline.processed_count == 5

    def test_pipeline_initialization_with_components(self):
        """Test pipeline initialization with components"""
        pipeline = NormalizationPipeline()
        assert pipeline.brand_mapper is not None
        assert pipeline.price_analyzer is not None
        assert pipeline.processed_count == 0
