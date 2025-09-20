"""
Unit tests for Price Analysis utility
"""
import pytest
from laser_intelligence.utils.price_analysis import PriceAnalyzer


class TestPriceAnalyzer:
    """Test cases for PriceAnalyzer"""

    def setup_method(self):
        """Set up test fixtures"""
        self.analyzer = PriceAnalyzer()

    def test_estimate_wholesale_value(self):
        """Test wholesale value estimation"""
        # Test high-value brand
        wholesale = self.analyzer.estimate_wholesale_value('Sciton', 'Joule', 'excellent', 100000)
        assert wholesale is not None
        assert wholesale > 100000  # Should be higher than asking price

        # Test unknown brand
        wholesale_unknown = self.analyzer.estimate_wholesale_value('UnknownBrand', 'UnknownModel', 'good', 50000)
        assert wholesale_unknown is not None
        assert wholesale_unknown > 0

    def test_estimate_resale_value(self):
        """Test resale value estimation"""
        # Test high-value brand
        resale = self.analyzer.estimate_resale_value('Sciton', 'Joule', 'excellent', 100000)
        assert resale is not None
        assert resale > 100000  # Should be higher than asking price

        # Test unknown brand
        resale_unknown = self.analyzer.estimate_resale_value('UnknownBrand', 'UnknownModel', 'good', 50000)
        assert resale_unknown is not None
        assert resale_unknown > 0

    def test_calculate_margin_estimate(self):
        """Test margin calculation"""
        asking_price = 50000
        wholesale_value = 75000
        refurb_cost = 5000
        freight_cost = 2000

        margin, margin_pct = self.analyzer.calculate_margin_estimate(
            asking_price, wholesale_value, refurb_cost, freight_cost
        )

        assert margin is not None
        assert margin_pct is not None
        assert margin > 0  # Should be positive margin
        assert margin_pct > 0  # Should be positive percentage

        # Calculate expected values
        total_cost = asking_price + refurb_cost + freight_cost
        expected_margin = wholesale_value - total_cost
        expected_margin_pct = (expected_margin / total_cost) * 100

        assert abs(margin - expected_margin) < 0.01
        assert abs(margin_pct - expected_margin_pct) < 0.1

    def test_calculate_margin_estimate_zero_costs(self):
        """Test margin calculation with zero costs"""
        asking_price = 50000
        wholesale_value = 75000

        margin, margin_pct = self.analyzer.calculate_margin_estimate(asking_price, wholesale_value)

        assert margin is not None
        assert margin_pct is not None
        assert margin > 0
        assert margin_pct > 0

    def test_calculate_margin_estimate_negative_margin(self):
        """Test margin calculation with negative margin"""
        asking_price = 100000
        wholesale_value = 50000  # Lower than asking price

        margin, margin_pct = self.analyzer.calculate_margin_estimate(asking_price, wholesale_value)

        assert margin is not None
        assert margin_pct is not None
        assert margin < 0  # Should be negative margin
        assert margin_pct < 0  # Should be negative percentage

    def test_add_price_comparison(self):
        """Test price comparison addition"""
        # Test with correct method signature
        result = self.analyzer.add_price_comparison(
            brand='Sciton',
            model='Joule', 
            condition='excellent',
            sold_price=75000,
            sold_date='2024-01-15',
            source='auction',
            url='https://example.com/auction/123'
        )

        # The method returns None but adds to internal list
        assert result is None
        # Check that the comparison was added to the internal list
        assert len(self.analyzer.price_comps) > 0

    def test_get_market_trends(self):
        """Test market trend retrieval"""
        trends = self.analyzer.get_market_trends('Sciton', 'Joule')

        assert trends is not None
        assert isinstance(trends, dict)
        assert 'price_trend' in trends
        assert 'volume_trend' in trends
        assert 'avg_price' in trends

    def test_heuristic_wholesale_estimate(self):
        """Test heuristic wholesale estimation"""
        # Test high-value brand
        wholesale = self.analyzer._heuristic_wholesale_estimate('sciton', 100000)
        assert wholesale > 100000

        # Test regular brand
        wholesale_regular = self.analyzer._heuristic_wholesale_estimate('unknown_brand', 50000)
        assert wholesale_regular > 0
        assert wholesale_regular < 100000

    def test_heuristic_resale_estimate(self):
        """Test heuristic resale estimation"""
        # Test high-value brand
        resale = self.analyzer._heuristic_resale_estimate('sciton', 100000)
        assert resale > 100000

        # Test regular brand
        resale_regular = self.analyzer._heuristic_resale_estimate('unknown_brand', 50000)
        assert resale_regular > 0
        assert resale_regular < 100000

    def test_resale_greater_than_wholesale(self):
        """Test that resale estimate is greater than wholesale estimate"""
        asking_price = 100000
        
        wholesale = self.analyzer._heuristic_wholesale_estimate('sciton', asking_price)
        resale = self.analyzer._heuristic_resale_estimate('sciton', asking_price)
        
        assert resale > wholesale, f"Resale ({resale}) should be greater than wholesale ({wholesale})"

    def test_error_handling(self):
        """Test error handling in price analysis"""
        # Test with invalid inputs
        result = self.analyzer.calculate_margin_estimate(None, None)
        assert result == (0.0, 0.0)

        result = self.analyzer.calculate_margin_estimate(-1000, 50000)
        assert result[0] is not None  # Should handle negative prices gracefully
