#!/usr/bin/env python3
"""
Unit tests for evasion middleware
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from scrapy.http import Request, HtmlResponse
from laser_intelligence.middleware.evasion import EvasionMiddleware


class TestEvasionMiddleware:
    """Test evasion middleware functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.middleware = EvasionMiddleware()

    def test_stealth_header_generation(self):
        """Test stealth header generation"""
        headers = self.middleware._generate_stealth_headers()
        
        assert 'User-Agent' in headers
        assert 'Accept' in headers
        assert 'Accept-Language' in headers
        assert 'Accept-Encoding' in headers
        assert 'DNT' in headers
        assert 'Connection' in headers
        assert 'Upgrade-Insecure-Requests' in headers
        assert 'Referer' in headers
        assert 'Cache-Control' in headers
        
        # Check that User-Agent is a valid browser string
        assert 'Mozilla' in headers['User-Agent'] or 'Chrome' in headers['User-Agent'] or 'Firefox' in headers['User-Agent']

    def test_blocking_detection(self):
        """Test blocking detection"""
        # Test Cloudflare detection
        response = Mock()
        response.headers = {'Server': 'cloudflare'}
        response.text = 'normal content'
        response.status = 200
        
        assert self.middleware._detect_blocking(response) == True
        
        # Test CAPTCHA detection
        response.text = 'Please solve this captcha'
        response.headers = {}
        response.status = 200
        
        assert self.middleware._detect_blocking(response) == True
        
        # Test access denied detection
        response.text = 'Access denied'
        response.status = 200
        
        assert self.middleware._detect_blocking(response) == True
        
        # Test blocked detection
        response.text = 'You are blocked'
        response.status = 200
        
        assert self.middleware._detect_blocking(response) == True
        
        # Test status code detection
        response.text = 'normal content'
        response.status = 403
        
        assert self.middleware._detect_blocking(response) == True
        
        # Test short response detection
        response.text = 'short'
        response.status = 200
        
        assert self.middleware._detect_blocking(response) == True
        
        # Test normal response (no blocking)
        response.text = 'This is a normal response with sufficient content length to avoid triggering the short response detection mechanism that requires at least 1000 characters. ' * 10
        response.status = 200
        response.headers = {}
        
        assert self.middleware._detect_blocking(response) == False

    def test_request_processing(self):
        """Test request processing"""
        request = Request(url='https://example.com/test')
        spider = Mock()
        
        # Mock time.sleep to avoid actual delays
        with patch('time.sleep'):
            processed_request = self.middleware.process_request(request, spider)
        
        # Check that headers were added
        assert 'User-Agent' in processed_request.headers
        assert 'Accept' in processed_request.headers
        assert 'Accept-Language' in processed_request.headers
        
        # Check that evasion metadata was added
        assert 'evasion_start_time' in processed_request.meta
        assert 'session_duration' in processed_request.meta

    def test_response_processing(self):
        """Test response processing"""
        request = Request(url='https://example.com/test')
        response = HtmlResponse(
            url='https://example.com/test',
            request=request,
            body=b'<html><body>Normal content</body></html>',
            status=200
        )
        spider = Mock()
        
        processed_response = self.middleware.process_response(request, response, spider)
        
        # Check that evasion score was added
        assert 'evasion_score' in processed_response.meta
        assert isinstance(processed_response.meta['evasion_score'], int)

    def test_blocking_handling(self):
        """Test blocking handling"""
        request = Request(url='https://example.com/test')
        response = HtmlResponse(
            url='https://example.com/test',
            request=request,
            body=b'<html><body>Access denied</body></html>',
            status=403
        )
        spider = Mock()
        
        # Mock the evasion scorer to return a low score
        with patch.object(self.middleware.evasion_scorer, 'calculate_score', return_value=30):
            processed_response = self.middleware.process_response(request, response, spider)
        
        # Check that the response was processed
        assert processed_response is not None
        assert 'evasion_score' in processed_response.meta

    def test_session_duration_tracking(self):
        """Test session duration tracking"""
        request1 = Request(url='https://example.com/page1')
        request2 = Request(url='https://example.com/page2')
        spider = Mock()
        
        # Mock time.sleep to avoid actual delays
        with patch('time.sleep'):
            # Process first request
            processed_request1 = self.middleware.process_request(request1, spider)
            
            # Wait a bit (simulated)
            time.sleep(0.1)
            
            # Process second request
            processed_request2 = self.middleware.process_request(request2, spider)
        
        # Check that session duration was tracked
        assert 'session_duration' in processed_request1.meta
        assert 'session_duration' in processed_request2.meta
        
        # Second request should have a longer session duration
        assert processed_request2.meta['session_duration'] > processed_request1.meta['session_duration']

    def test_evasion_middleware_initialization(self):
        """Test evasion middleware initialization"""
        middleware = EvasionMiddleware()
        
        assert middleware.ua is not None
        assert middleware.evasion_scorer is not None
        assert middleware.session_durations == {}

    def test_spider_signals(self):
        """Test spider signal handling"""
        spider = Mock()
        
        # Test spider opened signal
        self.middleware.spider_opened(spider)
        spider.logger.info.assert_called_with('EvasionMiddleware opened')
        
        # Test spider closed signal
        self.middleware.spider_closed(spider)
        spider.logger.info.assert_called_with('EvasionMiddleware closed')

    def test_evasion_score_calculation(self):
        """Test evasion score calculation integration"""
        request = Request(url='https://example.com/test')
        response = HtmlResponse(
            url='https://example.com/test',
            request=request,
            body=b'<html><body>Normal content</body></html>',
            status=200
        )
        spider = Mock()
        
        # Mock the evasion scorer
        with patch.object(self.middleware.evasion_scorer, 'calculate_score', return_value=85) as mock_calculate:
            processed_response = self.middleware.process_response(request, response, spider)
            
            # Check that calculate_score was called
            mock_calculate.assert_called_once_with(response, request)
            
            # Check that the score was added to response meta
            assert processed_response.meta['evasion_score'] == 85

    def test_human_behavior_simulation(self):
        """Test human behavior simulation"""
        request = Request(url='https://example.com/test')
        spider = Mock()
        
        # Mock time.sleep to avoid actual delays
        with patch('time.sleep') as mock_sleep:
            processed_request = self.middleware.process_request(request, spider)
            
            # Check that a delay was added
            mock_sleep.assert_called_once()
            delay = mock_sleep.call_args[0][0]
            assert 2 <= delay <= 10  # Random delay between 2-10 seconds

    def test_referer_randomization(self):
        """Test referer header randomization"""
        referers = set()
        
        # Generate multiple headers to test randomization
        for _ in range(10):
            headers = self.middleware._generate_stealth_headers()
            referers.add(headers['Referer'])
        
        # Should have multiple different referers
        assert len(referers) > 1
        
        # All referers should be valid search engines
        valid_referers = [
            'https://www.google.com/',
            'https://www.bing.com/',
            'https://duckduckgo.com/'
        ]
        
        for referer in referers:
            assert referer in valid_referers

    def test_accept_language_randomization(self):
        """Test accept language header randomization"""
        languages = set()
        
        # Generate multiple headers to test randomization
        for _ in range(10):
            headers = self.middleware._generate_stealth_headers()
            languages.add(headers['Accept-Language'])
        
        # Should have multiple different languages
        assert len(languages) > 1
        
        # All languages should be valid
        valid_languages = [
            'en-US,en;q=0.5',
            'en-GB,en;q=0.5',
            'en-CA,en;q=0.5'
        ]
        
        for language in languages:
            assert language in valid_languages

    def test_evasion_metadata(self):
        """Test evasion metadata addition"""
        request = Request(url='https://example.com/test')
        spider = Mock()
        
        # Mock time.sleep to avoid actual delays
        with patch('time.sleep'):
            processed_request = self.middleware.process_request(request, spider)
        
        # Check that evasion metadata was added
        assert 'evasion_start_time' in processed_request.meta
        assert 'session_duration' in processed_request.meta
        
        # Check that evasion_start_time is a valid timestamp
        assert isinstance(processed_request.meta['evasion_start_time'], float)
        assert processed_request.meta['evasion_start_time'] > 0
        
        # Check that session_duration is a valid duration
        assert isinstance(processed_request.meta['session_duration'], float)
        assert processed_request.meta['session_duration'] >= 0

    def test_domain_session_tracking(self):
        """Test domain-specific session tracking"""
        request1 = Request(url='https://example1.com/page1')
        request2 = Request(url='https://example2.com/page2')
        request3 = Request(url='https://example1.com/page3')
        spider = Mock()
        
        # Mock time.sleep to avoid actual delays
        with patch('time.sleep'):
            # Process requests from different domains
            processed_request1 = self.middleware.process_request(request1, spider)
            processed_request2 = self.middleware.process_request(request2, spider)
            processed_request3 = self.middleware.process_request(request3, spider)
        
        # Check that session durations are tracked per domain
        assert processed_request1.meta['session_duration'] >= 0  # First request to domain
        assert processed_request2.meta['session_duration'] == 0  # First request to different domain
        assert processed_request3.meta['session_duration'] > 0  # Second request to same domain as request1
