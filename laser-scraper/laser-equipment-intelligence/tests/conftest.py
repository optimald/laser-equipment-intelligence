"""
Pytest configuration and fixtures for laser equipment intelligence platform
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch
from scrapy.http import HtmlResponse, Request
from laser_intelligence.pipelines.normalization import LaserListingItem


@pytest.fixture
def sample_html():
    """Sample HTML content for testing"""
    return """
    <html>
        <head><title>Test Auction</title></head>
        <body>
            <div class="auction-item">
                <h2>Sciton Joule Laser System</h2>
                <div class="price">$150,000</div>
                <div class="condition">Excellent</div>
                <div class="description">
                    Complete Sciton Joule laser system with handpieces.
                    Serial: SN12345, Year: 2022, Hours: 500
                </div>
                <div class="location">Los Angeles, CA</div>
            </div>
        </body>
    </html>
    """


@pytest.fixture
def sample_response(sample_html):
    """Sample Scrapy response for testing"""
    request = Request(url="https://example.com/auction/123")
    return HtmlResponse(
        url="https://example.com/auction/123",
        request=request,
        body=sample_html.encode('utf-8'),
        encoding='utf-8'
    )


@pytest.fixture
def sample_item():
    """Sample laser listing item for testing"""
    item = LaserListingItem()
    item['source_url'] = 'https://example.com/auction/123'
    item['title_raw'] = 'Sciton Joule Laser System'
    item['brand'] = 'Sciton'
    item['model'] = 'Joule'
    item['asking_price'] = 150000.0
    item['condition'] = 'excellent'
    item['location_city'] = 'Los Angeles'
    item['location_state'] = 'CA'
    return item


@pytest.fixture
def temp_dir():
    """Temporary directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_proxy_manager():
    """Mock proxy manager for testing"""
    with patch('laser_intelligence.middleware.proxy.ProxyManager') as mock:
        mock_instance = Mock()
        mock_instance.get_proxy_pool.return_value = [
            'http://user:pass@proxy1.example.com:8080',
            'http://user:pass@proxy2.example.com:8080'
        ]
        mock_instance.get_healthy_proxy.return_value = 'http://user:pass@proxy1.example.com:8080'
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_captcha_solver():
    """Mock CAPTCHA solver for testing"""
    with patch('laser_intelligence.middleware.captcha.CaptchaSolver') as mock:
        mock_instance = Mock()
        mock_instance.solve_captcha.return_value = 'SOLVED123'
        mock_instance.get_balance.return_value = 10.50
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_brand_mapper():
    """Mock brand mapper for testing"""
    with patch('laser_intelligence.utils.brand_mapping.BrandMapper') as mock:
        mock_instance = Mock()
        mock_instance.normalize_brand.return_value = 'Sciton'
        mock_instance.normalize_model.return_value = 'Joule'
        mock_instance.map_modality.return_value = 'Platform System'
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_price_analyzer():
    """Mock price analyzer for testing"""
    with patch('laser_intelligence.utils.price_analysis.PriceAnalyzer') as mock:
        mock_instance = Mock()
        mock_instance.estimate_wholesale_value.return_value = 100000.0
        mock_instance.estimate_resale_value.return_value = 180000.0
        mock_instance.calculate_margin_estimate.return_value = (30000.0, 16.7)
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def mock_database():
    """Mock database connection for testing"""
    with patch('psycopg2.connect') as mock:
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock.return_value = mock_conn
        yield mock_conn


@pytest.fixture
def mock_redis():
    """Mock Redis connection for testing"""
    with patch('redis.Redis') as mock:
        mock_instance = Mock()
        mock_instance.ping.return_value = True
        mock_instance.get.return_value = None
        mock_instance.set.return_value = True
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def test_settings():
    """Test settings for Scrapy"""
    return {
        'DOWNLOAD_DELAY': 1,
        'RANDOMIZE_DOWNLOAD_DELAY': False,
        'CONCURRENT_REQUESTS': 1,
        'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
        'ROBOTSTXT_OBEY': False,
        'COOKIES_ENABLED': False,
        'TELNETCONSOLE_ENABLED': False,
        'LOG_LEVEL': 'DEBUG',
        'PLAYWRIGHT_BROWSER_TYPE': 'chromium',
        'PLAYWRIGHT_LAUNCH_OPTIONS': {
            'headless': True,
        },
    }


@pytest.fixture(autouse=True)
def setup_test_env():
    """Set up test environment variables"""
    os.environ.update({
        'DATABASE_URL': 'postgresql://test:test@localhost:5432/test_db',
        'REDIS_URL': 'redis://localhost:6379/1',
        'ENVIRONMENT': 'test',
        'DEBUG': 'true',
        'LOG_LEVEL': 'DEBUG',
    })
    yield
    # Cleanup after test
    for key in ['DATABASE_URL', 'REDIS_URL', 'ENVIRONMENT', 'DEBUG', 'LOG_LEVEL']:
        os.environ.pop(key, None)
