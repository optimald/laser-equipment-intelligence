"""
Unit tests for alerts pipeline
"""

import pytest
from unittest.mock import Mock, patch
from laser_intelligence.pipelines.alerts import AlertsPipeline
from laser_intelligence.pipelines.normalization import LaserListingItem


class TestAlertsPipeline:
    """Test alerts pipeline functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.pipeline = AlertsPipeline()
        self.spider = Mock()
        # Set up a mock slack manager for testing
        self.pipeline.slack_manager = Mock()

    def test_pipeline_initialization(self):
        """Test pipeline initialization"""
        assert self.pipeline is not None
        assert self.pipeline.alert_count == 0
        assert self.pipeline.hot_alerts == 0
        assert self.pipeline.auction_alerts == 0
        assert self.pipeline.demand_alerts == 0

    def test_hot_listing_alert(self):
        """Test HOT listing alert generation"""
        item = LaserListingItem()
        item['score_overall'] = 75  # HOT threshold
        item['brand'] = 'Sciton'
        item['model'] = 'Joule'
        item['asking_price'] = 50000

        with patch.object(self.pipeline, '_send_hot_listing_alert') as mock_alert:
            processed_item = self.pipeline.process_item(item, self.spider)
            mock_alert.assert_called_once_with(item, self.spider)

        assert self.pipeline.hot_alerts == 1

    def test_auction_ending_alert(self):
        """Test auction ending soon alert"""
        item = LaserListingItem()
        item['score_overall'] = 60
        item['auction_end_ts'] = 1234567890  # Mock timestamp

        with patch.object(self.pipeline, '_is_auction_ending_soon', return_value=True):
            with patch.object(self.pipeline, '_send_auction_ending_alert') as mock_alert:
                processed_item = self.pipeline.process_item(item, self.spider)
                mock_alert.assert_called_once_with(item, self.spider)

        assert self.pipeline.auction_alerts == 1

    def test_demand_match_alert(self):
        """Test demand match alert"""
        item = LaserListingItem()
        item['score_overall'] = 60
        item['brand'] = 'Sciton'
        item['model'] = 'Joule'

        mock_matches = [
            {'demand_id': '123', 'client_name': 'Test Client'},
            {'demand_id': '456', 'client_name': 'Another Client'}
        ]

        with patch.object(self.pipeline, '_check_demand_matches', return_value=mock_matches):
            with patch.object(self.pipeline, '_send_demand_match_alert') as mock_alert:
                processed_item = self.pipeline.process_item(item, self.spider)
                assert mock_alert.call_count == 2

        assert self.pipeline.demand_alerts == 2

    def test_no_alerts_for_low_score(self):
        """Test no alerts for low score items"""
        item = LaserListingItem()
        item['score_overall'] = 40  # Below HOT threshold
        item['auction_end_ts'] = 1234567890

        with patch.object(self.pipeline, '_is_auction_ending_soon', return_value=False):
            with patch.object(self.pipeline, '_check_demand_matches', return_value=[]):
                processed_item = self.pipeline.process_item(item, self.spider)

        assert self.pipeline.hot_alerts == 0
        assert self.pipeline.auction_alerts == 0
        assert self.pipeline.demand_alerts == 0

    def test_auction_ending_soon_detection(self):
        """Test auction ending soon detection"""
        import time
        
        # Test auction ending in 2 hours (should trigger alert)
        current_time = time.time()
        ending_soon = current_time + (2 * 3600)  # 2 hours from now
        
        item = LaserListingItem()
        item['auction_end_ts'] = ending_soon

        is_ending_soon = self.pipeline._is_auction_ending_soon(item)
        assert is_ending_soon == True

        # Test auction ending in 5 hours (should not trigger alert)
        ending_later = current_time + (5 * 3600)  # 5 hours from now
        
        item['auction_end_ts'] = ending_later
        is_ending_soon = self.pipeline._is_auction_ending_soon(item)
        assert is_ending_soon == False

    def test_demand_matches_check(self):
        """Test demand matches checking"""
        item = LaserListingItem()
        item['brand'] = 'Sciton'
        item['model'] = 'Joule'

        matches = self.pipeline._check_demand_matches(item)
        assert isinstance(matches, list)

    def test_slack_webhook_detection(self):
        """Test Slack webhook detection"""
        webhook = self.pipeline._get_slack_webhook()
        # Should return None if no webhook configured
        assert webhook is None

    def test_hot_listing_alert_content(self):
        """Test HOT listing alert content"""
        item = LaserListingItem()
        item['brand'] = 'Sciton'
        item['model'] = 'Joule'
        item['asking_price'] = 50000
        item['score_overall'] = 75
        item['source_url'] = 'https://example.com/auction/123'

        with patch.object(self.pipeline, 'slack_manager') as mock_slack:
            if mock_slack:
                self.pipeline._send_hot_listing_alert(item, self.spider)
                # Should call send_hot_listing_alert method
                mock_slack.send_hot_listing_alert.assert_called_once()

    def test_auction_ending_alert_content(self):
        """Test auction ending alert content"""
        item = LaserListingItem()
        item['brand'] = 'Sciton'
        item['model'] = 'Joule'
        item['auction_end_ts'] = 1234567890
        item['source_url'] = 'https://example.com/auction/123'

        with patch.object(self.pipeline, 'slack_manager') as mock_slack:
            if mock_slack:
                self.pipeline._send_auction_ending_alert(item, self.spider)
                # Should call send_auction_ending_alert method
                mock_slack.send_auction_ending_alert.assert_called_once()

    def test_demand_match_alert_content(self):
        """Test demand match alert content"""
        item = LaserListingItem()
        item['brand'] = 'Sciton'
        item['model'] = 'Joule'
        item['source_url'] = 'https://example.com/auction/123'

        match = {
            'demand_id': '123',
            'client_name': 'Test Client',
            'contact_email': 'test@example.com'
        }

        with patch.object(self.pipeline, 'slack_manager') as mock_slack:
            if mock_slack:
                self.pipeline._send_demand_match_alert(match, item, self.spider)
                # Should call send_demand_match_alert method
                mock_slack.send_demand_match_alert.assert_called_once()

    def test_error_handling(self):
        """Test error handling in alerts pipeline"""
        item = LaserListingItem()
        item['score_overall'] = 75

        with patch.object(self.pipeline, '_send_hot_listing_alert', side_effect=Exception('Test error')):
            # Should not raise exception
            processed_item = self.pipeline.process_item(item, self.spider)
            assert processed_item is not None

    def test_empty_item_processing(self):
        """Test processing of empty item"""
        item = LaserListingItem()

        processed_item = self.pipeline.process_item(item, self.spider)
        assert processed_item is not None

    def test_multiple_alerts_same_item(self):
        """Test multiple alerts for same item"""
        item = LaserListingItem()
        item['score_overall'] = 75  # HOT threshold
        item['auction_end_ts'] = 1234567890  # Ending soon
        item['brand'] = 'Sciton'
        item['model'] = 'Joule'

        with patch.object(self.pipeline, '_is_auction_ending_soon', return_value=True):
            with patch.object(self.pipeline, '_check_demand_matches', return_value=[{'demand_id': '123'}]):
                with patch.object(self.pipeline, '_send_hot_listing_alert'):
                    with patch.object(self.pipeline, '_send_auction_ending_alert'):
                        with patch.object(self.pipeline, '_send_demand_match_alert'):
                            processed_item = self.pipeline.process_item(item, self.spider)

        # Should have generated multiple alerts
        assert self.pipeline.hot_alerts == 1
        assert self.pipeline.auction_alerts == 1
        assert self.pipeline.demand_alerts == 1

    def test_alert_statistics_tracking(self):
        """Test alert statistics tracking"""
        # Process multiple items with different alert types
        items = [
            {'score_overall': 80},  # HOT alert
            {'score_overall': 60, 'auction_end_ts': 1234567890},  # Auction alert
            {'score_overall': 50},  # No alerts
        ]

        for i, item_data in enumerate(items):
            item = LaserListingItem()
            item.update(item_data)
            item['brand'] = 'Test'
            item['model'] = f'Model{i}'

            with patch.object(self.pipeline, '_is_auction_ending_soon', return_value=(i == 1)):
                with patch.object(self.pipeline, '_check_demand_matches', return_value=[]):
                    self.pipeline.process_item(item, self.spider)

        assert self.pipeline.alert_count == 3
        assert self.pipeline.hot_alerts == 1
        assert self.pipeline.auction_alerts == 1
        assert self.pipeline.demand_alerts == 0

    def test_pipeline_initialization_with_components(self):
        """Test pipeline initialization with components"""
        pipeline = AlertsPipeline()
        assert pipeline.alert_count == 0
        assert pipeline.hot_alerts == 0
        assert pipeline.auction_alerts == 0
        assert pipeline.demand_alerts == 0
