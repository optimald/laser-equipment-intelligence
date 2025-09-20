#!/usr/bin/env python3
"""
Unit tests for proxy middleware
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from scrapy.http import Request, HtmlResponse
from laser_intelligence.middleware.proxy import ProxyMiddleware


class TestProxyMiddleware:
    """Test proxy middleware functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.middleware = ProxyMiddleware()

    def test_proxy_assignment(self):
        """Test proxy assignment to requests"""
        request = Request(url='https://example.com/test')
        spider = Mock()
        
        # Mock proxy manager
        with patch.object(self.middleware, '_get_healthy_proxy', return_value='http://proxy.example.com:8080'):
            processed_request = self.middleware.process_request(request, spider)
        
        # Check that proxy was assigned
        assert 'proxy' in processed_request.meta
        assert processed_request.meta['proxy'] == 'http://proxy.example.com:8080'
        assert 'proxy_ip' in processed_request.meta
        assert processed_request.meta['proxy_ip'] == 'proxy.example.com'

    def test_proxy_rotation(self):
        """Test proxy rotation functionality"""
        request = Request(url='https://example.com/test')
        spider = Mock()
        
        # Mock proxy manager to return different proxies
        proxies = ['http://proxy1.example.com:8080', 'http://proxy2.example.com:8080']
        proxy_call_count = 0
        
        def mock_get_proxy():
            nonlocal proxy_call_count
            proxy = proxies[proxy_call_count % len(proxies)]
            proxy_call_count += 1
            return proxy
        
        with patch.object(self.middleware, '_get_healthy_proxy', side_effect=mock_get_proxy):
            # Process multiple requests (create new requests each time)
            request1 = Request(url='https://example.com/test1')
            request2 = Request(url='https://example.com/test2')
            processed_request1 = self.middleware.process_request(request1, spider)
            processed_request2 = self.middleware.process_request(request2, spider)
        
        # Check that different proxies were assigned
        assert processed_request1.meta['proxy'] == 'http://proxy1.example.com:8080'
        assert processed_request2.meta['proxy'] == 'http://proxy2.example.com:8080'

    def test_proxy_health_monitoring(self):
        """Test proxy health monitoring"""
        request = Request(url='https://example.com/test')
        request.meta['proxy'] = 'http://proxy.example.com:8080'  # Add proxy to request
        response = HtmlResponse(
            url='https://example.com/test',
            request=request,
            body=b'<html><body>Success</body></html>',
            status=200
        )
        spider = Mock()
        
        # Mock proxy manager
        with patch.object(self.middleware, '_track_proxy_performance') as mock_track:
            processed_response = self.middleware.process_response(request, response, spider)
            
            # Check that performance was tracked
            mock_track.assert_called_once()

    def test_proxy_failure_handling(self):
        """Test proxy failure handling"""
        request = Request(url='https://example.com/test')
        request.meta['proxy'] = 'http://proxy.example.com:8080'  # Add proxy to request
        response = HtmlResponse(
            url='https://example.com/test',
            request=request,
            body=b'<html><body>Error</body></html>',
            status=403
        )
        spider = Mock()
        
        # Mock proxy manager
        with patch.object(self.middleware, '_mark_proxy_failed') as mock_failure:
            processed_response = self.middleware.process_response(request, response, spider)
            
            # Check that failure was reported
            mock_failure.assert_called_once()

    def test_proxy_statistics_tracking(self):
        """Test proxy statistics tracking"""
        spider = Mock()
        
        # Mock proxy manager
        with patch.object(self.middleware, '_log_proxy_stats') as mock_log:
            self.middleware.spider_closed(spider)
            
            # Check that statistics were logged
            spider.logger.info.assert_called()

    def test_proxy_middleware_initialization(self):
        """Test proxy middleware initialization"""
        middleware = ProxyMiddleware()
        
        assert middleware.proxy_manager is not None
        assert middleware.failed_proxies == set()
        assert middleware.proxy_stats == {}

    def test_spider_signals(self):
        """Test spider signal handling"""
        spider = Mock()
        
        # Mock proxy manager
        with patch.object(self.middleware.proxy_manager, 'initialize_proxy_pool'):
            # Test spider opened signal
            self.middleware.spider_opened(spider)
            spider.logger.info.assert_called_with('ProxyMiddleware opened')
            
            # Test spider closed signal
            self.middleware.spider_closed(spider)
            spider.logger.info.assert_called_with('Proxy Performance Statistics:')

    def test_existing_proxy_preservation(self):
        """Test that existing proxy is preserved"""
        request = Request(url='https://example.com/test')
        request.meta['proxy'] = 'http://existing-proxy.example.com:8080'
        spider = Mock()
        
        # Mock proxy manager
        with patch.object(self.middleware, '_get_healthy_proxy', return_value='http://new-proxy.example.com:8080'):
            processed_request = self.middleware.process_request(request, spider)
        
        # Check that existing proxy was preserved
        assert processed_request.meta['proxy'] == 'http://existing-proxy.example.com:8080'

    def test_proxy_ip_extraction(self):
        """Test proxy IP extraction"""
        request = Request(url='https://example.com/test')
        spider = Mock()
        
        # Mock proxy manager
        with patch.object(self.middleware, '_get_healthy_proxy', return_value='http://user:pass@192.168.1.100:8080'):
            processed_request = self.middleware.process_request(request, spider)
        
        # Check that proxy IP was extracted correctly
        assert processed_request.meta['proxy_ip'] == '192.168.1.100'

    def test_proxy_statistics_logging(self):
        """Test proxy statistics logging"""
        spider = Mock()
        
        # Mock proxy manager with statistics
        mock_stats = {
            'proxy1:8080': {'requests': 10, 'successes': 9, 'failures': 1},
            'proxy2:8080': {'requests': 5, 'successes': 5, 'failures': 0}
        }
        
        with patch.object(self.middleware, 'proxy_stats', mock_stats):
            self.middleware._log_proxy_stats(spider)
            
            # Check that statistics were logged
            assert spider.logger.info.call_count >= 2  # At least one log per proxy

    def test_proxy_health_check_integration(self):
        """Test proxy health check integration"""
        request = Request(url='https://example.com/test')
        request.meta['proxy'] = 'http://proxy.example.com:8080'  # Add proxy to request
        response = HtmlResponse(
            url='https://example.com/test',
            request=request,
            body=b'<html><body>Success</body></html>',
            status=200
        )
        spider = Mock()
        
        # Mock proxy manager
        with patch.object(self.middleware, '_track_proxy_performance') as mock_track:
            processed_response = self.middleware.process_response(request, response, spider)
            
            # Check that performance was tracked
            mock_track.assert_called_once()
            call_args = mock_track.call_args[0]
            assert len(call_args) >= 1  # At least proxy URL
            assert len(call_args) >= 2  # Response time if provided

    def test_proxy_failure_detection(self):
        """Test proxy failure detection"""
        request = Request(url='https://example.com/test')
        request.meta['proxy'] = 'http://proxy.example.com:8080'  # Add proxy to request
        response = HtmlResponse(
            url='https://example.com/test',
            request=request,
            body=b'<html><body>Error</body></html>',
            status=503
        )
        spider = Mock()
        
        # Mock proxy manager
        with patch.object(self.middleware, '_mark_proxy_failed') as mock_failure:
            processed_response = self.middleware.process_response(request, response, spider)
            
            # Check that failure was reported
            mock_failure.assert_called_once()

    def test_proxy_middleware_from_crawler(self):
        """Test proxy middleware creation from crawler"""
        crawler = Mock()
        crawler.signals = Mock()
        
        middleware = ProxyMiddleware.from_crawler(crawler)
        
        assert isinstance(middleware, ProxyMiddleware)
        # Check that signals were connected
        assert crawler.signals.connect.call_count == 2

    def test_proxy_statistics_accuracy(self):
        """Test proxy statistics accuracy"""
        spider = Mock()
        
        # Mock proxy manager with specific statistics
        mock_stats = {
            'proxy1:8080': {'requests': 100, 'successes': 95, 'failures': 5},
            'proxy2:8080': {'requests': 50, 'successes': 48, 'failures': 2}
        }
        
        with patch.object(self.middleware, 'proxy_stats', mock_stats):
            self.middleware._log_proxy_stats(spider)
            
            # Check that statistics were logged correctly
            log_calls = spider.logger.info.call_args_list
            
            # Find the log call for proxy1
            proxy1_log = None
            for call in log_calls:
                if 'proxy1:8080' in str(call):
                    proxy1_log = call
                    break
            
            assert proxy1_log is not None
            assert '95.0%' in str(proxy1_log)  # 95/100 = 95%

    def test_proxy_rotation_efficiency(self):
        """Test proxy rotation efficiency"""
        request = Request(url='https://example.com/test')
        spider = Mock()
        
        # Mock proxy manager to return different proxies
        proxies = ['http://proxy1.example.com:8080', 'http://proxy2.example.com:8080', 'http://proxy3.example.com:8080']
        proxy_call_count = 0
        
        def mock_get_proxy():
            nonlocal proxy_call_count
            proxy = proxies[proxy_call_count % len(proxies)]
            proxy_call_count += 1
            return proxy
        
        with patch.object(self.middleware, '_get_healthy_proxy', side_effect=mock_get_proxy):
            # Process multiple requests (create new requests each time)
            processed_requests = []
            for i in range(6):
                new_request = Request(url=f'https://example.com/test{i}')
                processed_request = self.middleware.process_request(new_request, spider)
                processed_requests.append(processed_request)
        
        # Check that proxies were rotated efficiently
        assigned_proxies = [req.meta['proxy'] for req in processed_requests]
        
        # Should have used all proxies
        assert len(set(assigned_proxies)) == 3
        
        # Should have balanced usage
        proxy_counts = {}
        for proxy in assigned_proxies:
            proxy_counts[proxy] = proxy_counts.get(proxy, 0) + 1
        
        # Each proxy should have been used at least once
        for proxy in proxies:
            assert proxy_counts[proxy] >= 1
