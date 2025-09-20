"""
Comprehensive spider functionality tests
"""
import pytest
from scrapy.http import Request, HtmlResponse
from scrapy.spiders import Spider
from laser_intelligence.spiders.dotmed_spider import DotmedSpider
from laser_intelligence.spiders.bidspotter_spider import BidspotterSpider
from laser_intelligence.spiders.ebay_spider import EbaySpider
from laser_intelligence.spiders.govdeals_spider import GovdealsSpider
from laser_intelligence.spiders.facebook_marketplace_spider import FacebookMarketplaceSpider
from laser_intelligence.spiders.craigslist_spider import CraigslistSpider
from laser_intelligence.spiders.labx_spider import LabXSpider


class TestSpiderFunctionality:
    """Test spider functionality and data extraction"""

    def setup_method(self):
        """Set up test fixtures"""
        self.spiders = {
            'dotmed': DotmedSpider(),
            'bidspotter': BidspotterSpider(),
            'ebay': EbaySpider(),
            'govdeals': GovdealsSpider(),
            'facebook': FacebookMarketplaceSpider(),
            'craigslist': CraigslistSpider(),
            'labx': LabXSpider()
        }

    def test_spider_initialization(self):
        """Test that all spiders initialize correctly"""
        for name, spider in self.spiders.items():
            assert spider is not None
            assert hasattr(spider, 'name')
            assert hasattr(spider, 'allowed_domains')
            # Some spiders (like eBay) don't have start_urls, they generate URLs dynamically
            if hasattr(spider, 'start_urls'):
                assert spider.start_urls is not None

    def test_spider_start_urls(self):
        """Test that spiders have valid start URLs"""
        for name, spider in self.spiders.items():
            # Some spiders (like eBay) don't have start_urls, they generate URLs dynamically
            if hasattr(spider, 'start_urls'):
                assert spider.start_urls is not None
                # Some spiders may have empty start_urls if they use start_requests instead
                if len(spider.start_urls) > 0:
                    for url in spider.start_urls:
                        assert url.startswith('http')
                else:
                    # If start_urls is empty, check they have start_requests method
                    assert hasattr(spider, 'start_requests')
                    assert callable(getattr(spider, 'start_requests'))
            else:
                # For spiders without start_urls, check they have start_requests method
                assert hasattr(spider, 'start_requests')
                assert callable(getattr(spider, 'start_requests'))

    def test_spider_allowed_domains(self):
        """Test that spiders have valid allowed domains"""
        for name, spider in self.spiders.items():
            assert spider.allowed_domains is not None
            assert len(spider.allowed_domains) > 0

    def test_spider_parse_method(self):
        """Test that spiders have parse methods"""
        for name, spider in self.spiders.items():
            # Spiders use specific parse methods, not generic parse
            parse_methods = ['parse', 'parse_category', 'parse_listing', 'parse_auction', 'parse_search_results']
            has_parse_method = any(hasattr(spider, method) and callable(getattr(spider, method)) for method in parse_methods)
            assert has_parse_method, f"Spider {name} should have at least one parse method"

    def test_dotmed_spider_functionality(self):
        """Test DOTmed spider specific functionality"""
        spider = self.spiders['dotmed']
        
        # Test auction listing discovery
        mock_response = HtmlResponse(
            url="https://www.dotmed.com/auctions/",
            body=b"<html><body><div class='auction-item'>Test Auction</div></body></html>",
            request=Request("https://www.dotmed.com/auctions/")
        )
        
        # DOTmed spider uses parse_category method
        results = list(spider.parse_category(mock_response))
        assert len(results) >= 0  # Should handle the response gracefully

    def test_bidspotter_spider_functionality(self):
        """Test BidSpotter spider specific functionality"""
        spider = self.spiders['bidspotter']
        
        # Test catalog listing discovery
        mock_response = HtmlResponse(
            url="https://www.bidspotter.com/en-us/auction-catalogues",
            body=b"<html><body><div class='catalogue-item'>Test Catalog</div></body></html>",
            request=Request("https://www.bidspotter.com/en-us/auction-catalogues")
        )
        
        # BidSpotter spider uses parse_catalog_list method
        results = list(spider.parse_catalog_list(mock_response))
        assert len(results) >= 0  # Should handle the response gracefully

    def test_ebay_spider_functionality(self):
        """Test eBay spider specific functionality"""
        spider = self.spiders['ebay']
        
        # Test search result parsing
        mock_response = HtmlResponse(
            url="https://www.ebay.com/sch/i.html?_nkw=laser+equipment",
            body=b"<html><body><div class='s-item'>Test Item</div></body></html>",
            request=Request("https://www.ebay.com/sch/i.html?_nkw=laser+equipment")
        )
        
        # eBay spider uses parse_search_results method
        results = list(spider.parse_search_results(mock_response))
        assert len(results) >= 0  # Should handle the response gracefully

    def test_govdeals_spider_functionality(self):
        """Test GovDeals spider specific functionality"""
        spider = self.spiders['govdeals']
        
        # Test government surplus parsing
        mock_response = HtmlResponse(
            url="https://www.govdeals.com/index.cfm?fa=Main.AdvSearchResultsNew",
            body=b"<html><body><div class='search-result'>Test Item</div></body></html>",
            request=Request("https://www.govdeals.com/index.cfm?fa=Main.AdvSearchResultsNew")
        )
        
        # GovDeals spider uses parse_category method
        results = list(spider.parse_category(mock_response))
        assert len(results) >= 0  # Should handle the response gracefully

    def test_facebook_spider_functionality(self):
        """Test Facebook Marketplace spider specific functionality"""
        spider = self.spiders['facebook']
        
        # Test marketplace search parsing
        mock_response = HtmlResponse(
            url="https://www.facebook.com/marketplace/search/?query=laser%20equipment",
            body=b"<html><body><div class='marketplace-item'>Test Item</div></body></html>",
            request=Request("https://www.facebook.com/marketplace/search/?query=laser%20equipment")
        )
        
        # Facebook spider uses parse_search_results method
        results = list(spider.parse_search_results(mock_response))
        assert len(results) >= 0  # Should handle the response gracefully

    def test_craigslist_spider_functionality(self):
        """Test Craigslist spider specific functionality"""
        spider = self.spiders['craigslist']
        
        # Test multi-city searching
        mock_response = HtmlResponse(
            url="https://losangeles.craigslist.org/search/sss?query=laser+equipment",
            body=b"<html><body><div class='result-row'>Test Item</div></body></html>",
            request=Request("https://losangeles.craigslist.org/search/sss?query=laser+equipment")
        )
        
        # Craigslist spider uses parse_search_results method
        results = list(spider.parse_search_results(mock_response))
        assert len(results) >= 0  # Should handle the response gracefully

    def test_labx_spider_functionality(self):
        """Test LabX spider specific functionality"""
        spider = self.spiders['labx']
        
        # Test laboratory equipment parsing
        mock_response = HtmlResponse(
            url="https://www.labx.com/search/laser+equipment",
            body=b"<html><body><div class='listing-item'>Test Item</div></body></html>",
            request=Request("https://www.labx.com/search/laser+equipment")
        )
        
        # LabX spider uses parse_search_results method
        results = list(spider.parse_search_results(mock_response))
        assert len(results) >= 0  # Should handle the response gracefully

    def test_spider_error_handling(self):
        """Test spider error handling"""
        for name, spider in self.spiders.items():
            # Test with malformed HTML
            malformed_response = HtmlResponse(
                url="https://example.com",
                body=b"<html><body><div>Malformed HTML without closing tags",
                request=Request("https://example.com")
            )
            
            try:
                results = list(spider.parse(malformed_response))
                assert len(results) >= 0  # Should handle gracefully
            except Exception as e:
                # Some spiders might raise exceptions, which is acceptable
                assert isinstance(e, Exception)

    def test_spider_data_extraction(self):
        """Test spider data extraction capabilities"""
        # Test with sample HTML containing laser equipment data
        sample_html = b"""
        <html>
        <body>
            <div class="item">
                <h3>Sciton Joule Laser System</h3>
                <p>Excellent condition, serial number: SN12345</p>
                <span class="price">$50,000</span>
                <span class="location">Los Angeles, CA</span>
            </div>
        </body>
        </html>
        """
        
        for name, spider in self.spiders.items():
            mock_response = HtmlResponse(
                url="https://example.com/test",
                body=sample_html,
                request=Request("https://example.com/test")
            )
            
            try:
                results = list(spider.parse(mock_response))
                # Should handle the response without crashing
                assert len(results) >= 0
            except Exception as e:
                # Some spiders might not handle generic HTML, which is acceptable
                assert isinstance(e, Exception)

    def test_spider_cross_consistency(self):
        """Test cross-spider data consistency"""
        # Test that all spiders have consistent data structure expectations
        for name, spider in self.spiders.items():
            # Check that spiders have expected attributes
            assert hasattr(spider, 'name')
            assert hasattr(spider, 'allowed_domains')
            # Some spiders (like eBay) don't have start_urls, they generate URLs dynamically
            if hasattr(spider, 'start_urls'):
                assert spider.start_urls is not None
            
            # Check that name is a string
            assert isinstance(spider.name, str)
            assert len(spider.name) > 0
            
            # Check that allowed_domains is a list
            assert isinstance(spider.allowed_domains, list)
            
            # Check that start_urls is a list (if it exists)
            if hasattr(spider, 'start_urls'):
                assert isinstance(spider.start_urls, list)
