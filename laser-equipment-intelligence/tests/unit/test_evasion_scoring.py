"""
Unit tests for evasion scoring utility
"""

import pytest
from scrapy.http import HtmlResponse, Request
from laser_intelligence.utils.evasion_scoring import EvasionScorer


class TestEvasionScorer:
    """Test cases for EvasionScorer class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.scorer = EvasionScorer()
    
    def test_calculate_score_perfect_response(self):
        """Test evasion score calculation for perfect response"""
        request = Request(url="https://example.com")
        response = HtmlResponse(
            url="https://example.com",
            request=request,
            body=b"<html><body>" + b"x" * 2000 + b"</body></html>",
            status=200
        )
        
        score = self.scorer.calculate_score(response, request)
        assert score == 100  # Base score + bonus for successful response (capped at 100)
    
    def test_calculate_score_cloudflare_detection(self):
        """Test evasion score with Cloudflare detection"""
        request = Request(url="https://example.com")
        response = HtmlResponse(
            url="https://example.com",
            request=request,
            body=b"<html><body>" + b"x" * 2000 + b"</body></html>",
            status=200,
            headers={'Server': 'cloudflare'}
        )
        
        score = self.scorer.calculate_score(response, request)
        assert score == 90  # Base score - Cloudflare penalty
    
    def test_calculate_score_captcha_detection(self):
        """Test evasion score with CAPTCHA detection"""
        request = Request(url="https://example.com")
        response = HtmlResponse(
            url="https://example.com",
            request=request,
            body=b"<html><body>" + b"x" * 2000 + b"Please solve this captcha</body></html>",
            status=200
        )
        
        score = self.scorer.calculate_score(response, request)
        assert score == 80  # Base score - CAPTCHA penalty
    
    def test_calculate_score_blocked_response(self):
        """Test evasion score with blocked response"""
        request = Request(url="https://example.com")
        response = HtmlResponse(
            url="https://example.com",
            request=request,
            body=b"<html><body>" + b"x" * 2000 + b"Access denied</body></html>",
            status=403
        )
        
        score = self.scorer.calculate_score(response, request)
        assert score == 50  # Base score - blocked penalty
    
    def test_calculate_score_short_response(self):
        """Test evasion score with suspiciously short response"""
        request = Request(url="https://example.com")
        response = HtmlResponse(
            url="https://example.com",
            request=request,
            body=b"<html><body>Short</body></html>",
            status=200
        )
        
        score = self.scorer.calculate_score(response, request)
        assert score == 85  # Base score - short response penalty
    
    def test_calculate_score_rate_limited(self):
        """Test evasion score with rate limiting"""
        request = Request(url="https://example.com")
        response = HtmlResponse(
            url="https://example.com",
            request=request,
            body=b"<html><body>" + b"x" * 2000 + b"Rate limited</body></html>",
            status=429
        )
        
        score = self.scorer.calculate_score(response, request)
        assert score == 75  # Base score - rate limit penalty
    
    def test_calculate_score_minimum_score(self):
        """Test that evasion score never goes below 0"""
        request = Request(url="https://example.com")
        response = HtmlResponse(
            url="https://example.com",
            request=request,
            body=b"<html><body>Multiple issues</body></html>",
            status=403,
            headers={'Server': 'cloudflare', 'X-RateLimit-Remaining': '0'}
        )
        
        score = self.scorer.calculate_score(response, request)
        assert score >= 0  # Should never be negative
    
    def test_calculate_score_maximum_score(self):
        """Test that evasion score never exceeds 100"""
        request = Request(url="https://example.com")
        response = HtmlResponse(
            url="https://example.com",
            request=request,
            body=b"<html><body>" + b"x" * 2000 + b"</body></html>",
            status=200
        )
        
        score = self.scorer.calculate_score(response, request)
        assert score <= 100  # Should never exceed 100
    
    def test_get_evasion_report(self):
        """Test evasion report generation"""
        request = Request(
            url="https://example.com",
            meta={'proxy': 'http://proxy.example.com:8080'},
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        response = HtmlResponse(
            url="https://example.com",
            request=request,
            body=b"<html><body>Content</body></html>",
            status=200
        )
        
        report = self.scorer.get_evasion_report(response, request)
        
        assert 'evasion_score' in report
        assert 'status_code' in report
        assert 'response_length' in report
        assert 'headers_analyzed' in report
        assert 'timestamp' in report
        assert 'url' in report
        assert 'proxy_used' in report
        assert 'user_agent' in report
        assert 'recommendations' in report
        
        assert report['status_code'] == 200
        assert report['url'] == 'https://example.com'
        assert report['proxy_used'] == 'http://proxy.example.com:8080'
        assert report['user_agent'] == 'Mozilla/5.0'
    
    def test_get_recommendations_high_score(self):
        """Test recommendations for high evasion score"""
        recommendations = self.scorer._get_recommendations(80)
        assert len(recommendations) == 0  # No recommendations for good score
    
    def test_get_recommendations_medium_score(self):
        """Test recommendations for medium evasion score"""
        recommendations = self.scorer._get_recommendations(40)
        assert len(recommendations) > 0
        assert any('proxies' in rec.lower() for rec in recommendations)
        assert any('delay' in rec.lower() for rec in recommendations)
    
    def test_get_recommendations_low_score(self):
        """Test recommendations for low evasion score"""
        recommendations = self.scorer._get_recommendations(25)
        assert len(recommendations) > 0
        assert any('captcha' in rec.lower() for rec in recommendations)
        assert any('stealth' in rec.lower() for rec in recommendations)
    
    def test_get_recommendations_critical_score(self):
        """Test recommendations for critical evasion score"""
        recommendations = self.scorer._get_recommendations(10)
        assert len(recommendations) > 0
        assert any('pause' in rec.lower() for rec in recommendations)
        assert any('manual' in rec.lower() for rec in recommendations)
    
    def test_check_cloudflare(self):
        """Test Cloudflare detection"""
        response = HtmlResponse(
            url="https://example.com",
            request=Request(url="https://example.com"),
            body=b"<html><body>Content</body></html>",
            headers={'Server': 'cloudflare'}
        )
        
        penalty = self.scorer._check_cloudflare(response)
        assert penalty == -20
        
        # Test without Cloudflare
        response_no_cf = HtmlResponse(
            url="https://example.com",
            request=Request(url="https://example.com"),
            body=b"<html><body>Content</body></html>",
            headers={'Server': 'nginx'}
        )
        
        penalty_no_cf = self.scorer._check_cloudflare(response_no_cf)
        assert penalty_no_cf == 0
    
    def test_check_captcha(self):
        """Test CAPTCHA detection"""
        response_with_captcha = HtmlResponse(
            url="https://example.com",
            request=Request(url="https://example.com"),
            body=b"<html><body>Please solve this captcha</body></html>"
        )
        
        penalty = self.scorer._check_captcha(response_with_captcha)
        assert penalty == -30
        
        # Test without CAPTCHA
        response_no_captcha = HtmlResponse(
            url="https://example.com",
            request=Request(url="https://example.com"),
            body=b"<html><body>Normal content</body></html>"
        )
        
        penalty_no_captcha = self.scorer._check_captcha(response_no_captcha)
        assert penalty_no_captcha == 0
    
    def test_check_blocking(self):
        """Test blocking detection"""
        # Test 403 status
        response_403 = HtmlResponse(
            url="https://example.com",
            request=Request(url="https://example.com"),
            body=b"<html><body>Forbidden</body></html>",
            status=403
        )
        
        penalty_403 = self.scorer._check_blocking(response_403)
        assert penalty_403 == -50
        
        # Test access denied text
        response_text = HtmlResponse(
            url="https://example.com",
            request=Request(url="https://example.com"),
            body=b"<html><body>Access denied</body></html>",
            status=200
        )
        
        penalty_text = self.scorer._check_blocking(response_text)
        assert penalty_text == -50
        
        # Test normal response
        response_normal = HtmlResponse(
            url="https://example.com",
            request=Request(url="https://example.com"),
            body=b"<html><body>Normal content</body></html>",
            status=200
        )
        
        penalty_normal = self.scorer._check_blocking(response_normal)
        assert penalty_normal == 0
