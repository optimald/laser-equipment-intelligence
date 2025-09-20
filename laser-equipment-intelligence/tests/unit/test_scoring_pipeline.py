"""
Unit tests for scoring pipeline
"""

import pytest
import time
from unittest.mock import Mock, patch
from laser_intelligence.pipelines.scoring import ScoringPipeline
from laser_intelligence.pipelines.normalization import LaserListingItem


class TestScoringPipeline:
    """Test scoring pipeline functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.pipeline = ScoringPipeline()
        self.spider = Mock()

    def test_pipeline_initialization(self):
        """Test pipeline initialization"""
        assert self.pipeline is not None
        assert self.pipeline.scored_count == 0
        assert self.pipeline.hot_items == 0
        assert self.pipeline.review_items == 0
        assert self.pipeline.archive_items == 0

    def test_margin_score_calculation(self):
        """Test margin score calculation"""
        item = LaserListingItem()
        item['asking_price'] = 50000
        item['est_wholesale'] = 70000
        item['refurb_cost_estimate'] = 5000
        item['freight_estimate'] = 2000

        score = self.pipeline._calculate_margin_score(item)
        assert score is not None
        assert 0 <= score <= 100

    def test_urgency_score_calculation(self):
        """Test urgency score calculation"""
        item = LaserListingItem()
        item['auction_end_ts'] = 1234567890  # Mock timestamp

        score = self.pipeline._calculate_urgency_score(item)
        assert score is not None
        assert 0 <= score <= 100

    def test_condition_score_calculation(self):
        """Test condition score calculation"""
        test_cases = [
            ('new', 100),
            ('excellent', 90),
            ('good', 70),
            ('fair', 50),
            ('poor', 30),
            ('as-is', 20),
            ('unknown', 50),
        ]

        for condition, expected_score in test_cases:
            item = LaserListingItem()
            item['condition'] = condition

            score = self.pipeline._calculate_condition_score(item)
            assert score == expected_score

    def test_reputation_score_calculation(self):
        """Test reputation score calculation"""
        item = LaserListingItem()
        item['seller_name'] = 'Medical Equipment Liquidators'

        score = self.pipeline._calculate_reputation_score(item)
        assert score is not None
        assert 0 <= score <= 100

    def test_overall_score_calculation(self):
        """Test overall score calculation"""
        item = LaserListingItem()
        item['score_margin'] = 80
        item['score_urgency'] = 70
        item['score_condition'] = 90
        item['score_reputation'] = 60

        score = self.pipeline._calculate_overall_score(item)
        assert score is not None
        assert 0 <= score <= 100
        # Should be weighted average
        expected_score = (80 * 0.4 + 70 * 0.3 + 90 * 0.2 + 60 * 0.1)
        assert abs(score - expected_score) < 0.1

    def test_qualification_level_assignment(self):
        """Test qualification level assignment"""
        test_cases = [
            (85, 'HOT'),
            (70, 'HOT'),
            (69, 'REVIEW'),
            (50, 'REVIEW'),
            (49, 'ARCHIVE'),
            (30, 'ARCHIVE'),
        ]

        for score, expected_level in test_cases:
            level = self.pipeline._get_qualification_level(score)
            assert level == expected_level

    def test_margin_estimates_calculation(self):
        """Test margin estimates calculation"""
        item = LaserListingItem()
        item['asking_price'] = 50000
        item['brand'] = 'Sciton'
        item['model'] = 'Joule'
        item['condition'] = 'excellent'

        self.pipeline._calculate_margin_estimates(item)

        assert 'est_wholesale' in item
        assert 'est_resale' in item
        assert 'margin_estimate' in item
        assert 'margin_pct' in item

    def test_complete_item_scoring(self):
        """Test complete item scoring process"""
        item = LaserListingItem()
        item['brand'] = 'Sciton'
        item['model'] = 'Joule'
        item['asking_price'] = 50000
        item['condition'] = 'excellent'
        item['auction_end_ts'] = 1234567890
        item['seller_name'] = 'Medical Equipment Liquidators'

        processed_item = self.pipeline.process_item(item, self.spider)

        # Check all scores are calculated
        assert 'score_margin' in processed_item
        assert 'score_urgency' in processed_item
        assert 'score_condition' in processed_item
        assert 'score_reputation' in processed_item
        assert 'score_overall' in processed_item
        assert 'qualification_level' in processed_item

        # Check statistics are updated
        assert self.pipeline.scored_count == 1

    def test_hot_item_tracking(self):
        """Test HOT item tracking"""
        item = LaserListingItem()
        item['brand'] = 'Sciton'
        item['model'] = 'Joule'
        item['asking_price'] = 5000  # Very low asking price for excellent margin
        item['condition'] = 'new'
        item['auction_end_ts'] = time.time() + 1800  # 30 minutes from now
        item['hours'] = 500  # Low usage for bonus
        item['seller_name'] = 'Medical Equipment Liquidators'

        processed_item = self.pipeline.process_item(item, self.spider)

        assert processed_item['qualification_level'] == 'HOT'
        assert self.pipeline.hot_items == 1
        assert self.pipeline.review_items == 0
        assert self.pipeline.archive_items == 0

    def test_review_item_tracking(self):
        """Test REVIEW item tracking"""
        item = LaserListingItem()
        item['brand'] = 'Cynosure'
        item['model'] = 'Picosure'
        item['asking_price'] = 15000  # Lower asking price for better margin
        item['condition'] = 'good'
        item['auction_end_ts'] = time.time() + 1800  # 30 minutes from now
        item['hours'] = 500  # Low usage for bonus
        item['seller_name'] = 'Equipment Dealer'

        processed_item = self.pipeline.process_item(item, self.spider)

        assert processed_item['qualification_level'] == 'REVIEW'
        assert self.pipeline.hot_items == 0
        assert self.pipeline.review_items == 1
        assert self.pipeline.archive_items == 0

    def test_archive_item_tracking(self):
        """Test ARCHIVE item tracking"""
        item = LaserListingItem()
        item['brand'] = 'Unknown'
        item['model'] = 'Unknown'
        item['asking_price'] = 50000  # High asking price for poor margin
        item['condition'] = 'poor'
        item['auction_end_ts'] = time.time() + 86400  # 1 day from now
        item['seller_name'] = 'Unknown Seller'

        processed_item = self.pipeline.process_item(item, self.spider)

        assert processed_item['qualification_level'] == 'ARCHIVE'
        assert self.pipeline.hot_items == 0
        assert self.pipeline.review_items == 0
        assert self.pipeline.archive_items == 1

    def test_error_handling(self):
        """Test error handling in scoring"""
        item = LaserListingItem()
        # Missing required fields

        # Should not raise exception
        processed_item = self.pipeline.process_item(item, self.spider)
        assert processed_item is not None

    def test_empty_item_scoring(self):
        """Test scoring of empty item"""
        item = LaserListingItem()

        processed_item = self.pipeline.process_item(item, self.spider)
        assert processed_item is not None
        assert 'score_overall' in processed_item

    def test_high_value_item_scoring(self):
        """Test scoring of high-value item"""
        item = LaserListingItem()
        item['brand'] = 'Sciton'
        item['model'] = 'Joule'
        item['asking_price'] = 5000  # Very low asking price for excellent margin
        item['condition'] = 'new'
        item['auction_end_ts'] = time.time() + 1800  # 30 minutes from now (high urgency)
        item['hours'] = 500  # Low usage for bonus
        item['seller_name'] = 'Medical Equipment Liquidators'

        processed_item = self.pipeline.process_item(item, self.spider)

        # Should be high score due to good margin and urgency
        assert processed_item['score_overall'] >= 70
        assert processed_item['qualification_level'] == 'HOT'

    def test_low_value_item_scoring(self):
        """Test scoring of low-value item"""
        item = LaserListingItem()
        item['brand'] = 'Unknown'
        item['model'] = 'Unknown'
        item['asking_price'] = 100000  # High asking price
        item['condition'] = 'poor'
        item['auction_end_ts'] = 1234567890
        item['seller_name'] = 'Unknown Seller'

        processed_item = self.pipeline.process_item(item, self.spider)

        # Should be low score
        assert processed_item['score_overall'] < 50
        assert processed_item['qualification_level'] == 'ARCHIVE'

    def test_pipeline_statistics(self):
        """Test pipeline statistics tracking"""
        # Process multiple items with different characteristics
        items = [
            # HOT item
            {
                'brand': 'Sciton', 'model': 'Joule', 'asking_price': 5000,
                'condition': 'new', 'auction_end_ts': time.time() + 1800,
                'hours': 500, 'seller_name': 'Medical Equipment Liquidators'
            },
            # REVIEW item
            {
                'brand': 'Cynosure', 'model': 'Picosure', 'asking_price': 15000,
                'condition': 'good', 'auction_end_ts': time.time() + 1800,
                'hours': 500, 'seller_name': 'Equipment Dealer'
            },
            # ARCHIVE item
            {
                'brand': 'Unknown', 'model': 'Unknown', 'asking_price': 50000,
                'condition': 'poor', 'auction_end_ts': time.time() + 86400,
                'seller_name': 'Unknown Seller'
            }
        ]

        for item_data in items:
            item = LaserListingItem()
            item.update(item_data)
            self.pipeline.process_item(item, self.spider)

        assert self.pipeline.scored_count == 3
        assert self.pipeline.hot_items == 1
        assert self.pipeline.review_items == 1
        assert self.pipeline.archive_items == 1

    def test_pipeline_initialization_with_components(self):
        """Test pipeline initialization with components"""
        pipeline = ScoringPipeline()
        assert pipeline.scored_count == 0
        assert pipeline.hot_items == 0
        assert pipeline.review_items == 0
        assert pipeline.archive_items == 0
