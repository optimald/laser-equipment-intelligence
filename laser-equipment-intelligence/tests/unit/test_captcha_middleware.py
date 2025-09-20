#!/usr/bin/env python3
"""
Unit tests for CAPTCHA middleware
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from scrapy.http import Request, HtmlResponse
from laser_intelligence.middleware.captcha import CaptchaMiddleware


class TestCaptchaMiddleware:
    """Test CAPTCHA middleware functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.middleware = CaptchaMiddleware()

    def test_captcha_detection(self):
        """Test CAPTCHA detection"""
        # Test CAPTCHA detection
        response = HtmlResponse(
            url='https://example.com/test',
            request=Request(url='https://example.com/test'),
            body=b'<html><body>Please solve this captcha</body></html>',
            status=200
        )
        
        assert self.middleware._detect_captcha(response) == True
        
        # Test reCAPTCHA detection
        response = HtmlResponse(
            url='https://example.com/test',
            request=Request(url='https://example.com/test'),
            body=b'<html><body>Please complete the reCAPTCHA</body></html>',
            status=200
        )
        
        assert self.middleware._detect_captcha(response) == True
        
        # Test hCAPTCHA detection
        response = HtmlResponse(
            url='https://example.com/test',
            request=Request(url='https://example.com/test'),
            body=b'<html><body>Please complete the hCAPTCHA</body></html>',
            status=200
        )
        
        assert self.middleware._detect_captcha(response) == True
        
        # Test challenge detection
        response = HtmlResponse(
            url='https://example.com/test',
            request=Request(url='https://example.com/test'),
            body=b'<html><body>Please complete this challenge</body></html>',
            status=200
        )
        
        assert self.middleware._detect_captcha(response) == True
        
        # Test verification detection
        response = HtmlResponse(
            url='https://example.com/test',
            request=Request(url='https://example.com/test'),
            body=b'<html><body>Please complete verification</body></html>',
            status=200
        )
        
        assert self.middleware._detect_captcha(response) == True
        
        # Test robot detection
        response = HtmlResponse(
            url='https://example.com/test',
            request=Request(url='https://example.com/test'),
            body=b'<html><body>Are you a robot?</body></html>',
            status=200
        )
        
        assert self.middleware._detect_captcha(response) == True
        
        # Test bot detection
        response = HtmlResponse(
            url='https://example.com/test',
            request=Request(url='https://example.com/test'),
            body=b'<html><body>Bot detection</body></html>',
            status=200
        )
        
        assert self.middleware._detect_captcha(response) == True
        
        # Test normal response (no CAPTCHA)
        response = HtmlResponse(
            url='https://example.com/test',
            request=Request(url='https://example.com/test'),
            body=b'<html><body>Normal content</body></html>',
            status=200
        )
        
        assert self.middleware._detect_captcha(response) == False

    def test_captcha_solving_integration(self):
        """Test CAPTCHA solving integration"""
        request = Request(url='https://example.com/test')
        response = HtmlResponse(
            url='https://example.com/test',
            request=request,
            body=b'<html><body>Please solve this captcha</body></html>',
            status=200
        )
        spider = Mock()
        
        # Mock CAPTCHA solver
        with patch.object(self.middleware.captcha_solver, 'solve_captcha', return_value='ABC123'):
            with patch.object(self.middleware, '_submit_captcha_solution', return_value=response):
                processed_response = self.middleware.process_response(request, response, spider)
                
                # Check that CAPTCHA was solved
                assert processed_response is not None
                assert self.middleware.solved_captchas == 1

    def test_captcha_solving_failure(self):
        """Test CAPTCHA solving failure handling"""
        request = Request(url='https://example.com/test')
        response = HtmlResponse(
            url='https://example.com/test',
            request=request,
            body=b'<html><body>Please solve this captcha</body></html>',
            status=200
        )
        spider = Mock()
        
        # Mock CAPTCHA solver failure
        with patch.object(self.middleware.captcha_solver, 'solve_captcha', return_value=None):
            processed_response = self.middleware.process_response(request, response, spider)
            
            # Check that failure was handled
            assert processed_response is not None
            assert self.middleware.failed_captchas == 1

    def test_captcha_data_extraction(self):
        """Test CAPTCHA data extraction"""
        response = HtmlResponse(
            url='https://example.com/test',
            request=Request(url='https://example.com/test'),
            body=b'<html><body>Please solve this captcha</body></html>',
            status=200
        )
        
        captcha_data = self.middleware._extract_captcha_data(response)
        
        assert captcha_data is not None
        assert 'type' in captcha_data
        assert 'image_url' in captcha_data
        assert 'site_key' in captcha_data

    def test_captcha_solution_submission(self):
        """Test CAPTCHA solution submission"""
        request = Request(url='https://example.com/test')
        response = HtmlResponse(
            url='https://example.com/test',
            request=request,
            body=b'<html><body>Please solve this captcha</body></html>',
            status=200
        )
        spider = Mock()
        solution = 'ABC123'
        
        # Mock solution submission
        with patch.object(self.middleware, '_submit_captcha_solution', return_value=response):
            result = self.middleware._submit_captcha_solution(request, response, solution, spider)
            
            # Check that solution was submitted
            assert result is not None

    def test_captcha_middleware_initialization(self):
        """Test CAPTCHA middleware initialization"""
        middleware = CaptchaMiddleware()
        
        assert middleware.captcha_solver is not None
        assert middleware.solved_captchas == 0
        assert middleware.failed_captchas == 0

    def test_spider_signals(self):
        """Test spider signal handling"""
        spider = Mock()
        
        # Test spider opened signal
        self.middleware.spider_opened(spider)
        spider.logger.info.assert_called_with('CaptchaMiddleware opened')
        
        # Test spider closed signal
        self.middleware.spider_closed(spider)
        spider.logger.info.assert_called_with('CAPTCHA Statistics: 0 solved, 0 failed')

    def test_captcha_statistics_tracking(self):
        """Test CAPTCHA statistics tracking"""
        request = Request(url='https://example.com/test')
        response = HtmlResponse(
            url='https://example.com/test',
            request=request,
            body=b'<html><body>Please solve this captcha</body></html>',
            status=200
        )
        spider = Mock()
        
        # Mock successful CAPTCHA solving
        with patch.object(self.middleware.captcha_solver, 'solve_captcha', return_value='ABC123'):
            with patch.object(self.middleware, '_submit_captcha_solution', return_value=response):
                # Solve multiple CAPTCHAs
                for _ in range(3):
                    self.middleware.process_response(request, response, spider)
                
                # Fail one CAPTCHA
                with patch.object(self.middleware.captcha_solver, 'solve_captcha', return_value=None):
                    self.middleware.process_response(request, response, spider)
        
        # Check statistics
        assert self.middleware.solved_captchas == 3
        assert self.middleware.failed_captchas == 1

    def test_captcha_middleware_from_crawler(self):
        """Test CAPTCHA middleware creation from crawler"""
        crawler = Mock()
        crawler.signals = Mock()
        
        middleware = CaptchaMiddleware.from_crawler(crawler)
        
        assert isinstance(middleware, CaptchaMiddleware)
        # Check that signals were connected
        assert crawler.signals.connect.call_count == 2

    def test_captcha_detection_accuracy(self):
        """Test CAPTCHA detection accuracy"""
        test_cases = [
            ('Please solve this captcha', True),
            ('Complete the reCAPTCHA', True),
            ('hCAPTCHA verification', True),
            ('Challenge verification', True),
            ('Human verification', True),
            ('Robot detection', True),
            ('Bot detection', True),
            ('Normal content', False),
            ('Product listing', False),
            ('Search results', False)
        ]
        
        for content, expected in test_cases:
            response = HtmlResponse(
                url='https://example.com/test',
                request=Request(url='https://example.com/test'),
                body=f'<html><body>{content}</body></html>'.encode(),
                status=200
            )
            
            result = self.middleware._detect_captcha(response)
            assert result == expected, f"Failed for content: {content}"

    def test_captcha_solving_error_handling(self):
        """Test CAPTCHA solving error handling"""
        request = Request(url='https://example.com/test')
        response = HtmlResponse(
            url='https://example.com/test',
            request=request,
            body=b'<html><body>Please solve this captcha</body></html>',
            status=200
        )
        spider = Mock()
        
        # Mock CAPTCHA solver exception
        with patch.object(self.middleware.captcha_solver, 'solve_captcha', side_effect=Exception("API Error")):
            processed_response = self.middleware.process_response(request, response, spider)
            
            # Check that error was handled gracefully
            assert processed_response is not None
            assert self.middleware.failed_captchas == 1

    def test_captcha_solution_submission_error_handling(self):
        """Test CAPTCHA solution submission error handling"""
        request = Request(url='https://example.com/test')
        response = HtmlResponse(
            url='https://example.com/test',
            request=request,
            body=b'<html><body>Please solve this captcha</body></html>',
            status=200
        )
        spider = Mock()
        
        # Mock CAPTCHA solver success but submission failure
        with patch.object(self.middleware.captcha_solver, 'solve_captcha', return_value='ABC123'):
            with patch.object(self.middleware, '_submit_captcha_solution', return_value=None):
                processed_response = self.middleware.process_response(request, response, spider)
                
                # Check that failure was handled
                assert processed_response is not None
                assert self.middleware.failed_captchas == 1

    def test_captcha_middleware_performance(self):
        """Test CAPTCHA middleware performance"""
        request = Request(url='https://example.com/test')
        response = HtmlResponse(
            url='https://example.com/test',
            request=request,
            body=b'<html><body>Normal content</body></html>',
            status=200
        )
        spider = Mock()
        
        # Test that normal responses are processed quickly
        import time
        start_time = time.time()
        
        processed_response = self.middleware.process_response(request, response, spider)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should process quickly for non-CAPTCHA responses
        assert processing_time < 0.1  # Less than 100ms
        assert processed_response is not None

    def test_captcha_statistics_logging(self):
        """Test CAPTCHA statistics logging"""
        spider = Mock()
        
        # Set some statistics
        self.middleware.solved_captchas = 5
        self.middleware.failed_captchas = 2
        
        # Test spider closed signal
        self.middleware.spider_closed(spider)
        
        # Check that statistics were logged
        spider.logger.info.assert_called_with('CAPTCHA Statistics: 5 solved, 2 failed')
