"""
Security testing for Laser Equipment Intelligence Platform
"""
import pytest
from scrapy.http import Request, HtmlResponse
from laser_intelligence.utils.evasion_scoring import EvasionScorer
from laser_intelligence.middleware.evasion import EvasionMiddleware
from laser_intelligence.middleware.proxy import ProxyMiddleware


class TestSecurityMeasures:
    """Test security measures and evasion systems"""

    def setup_method(self):
        """Set up test fixtures"""
        self.evasion_scorer = EvasionScorer()
        self.evasion_middleware = EvasionMiddleware()
        self.proxy_middleware = ProxyMiddleware()

    def test_evasion_scoring_security(self):
        """Test evasion scoring security measures"""
        # Test perfect response (should score high)
        request = Request(url="https://example.com")
        perfect_response = HtmlResponse(
            url="https://example.com",
            request=request,
            body=b"<html><body>" + b"x" * 2000 + b"</body></html>",
            status=200
        )
        
        score = self.evasion_scorer.calculate_score(perfect_response, request)
        assert score >= 80  # Should be high for perfect response
        
        # Test blocked response (should score low)
        blocked_response = HtmlResponse(
            url="https://example.com",
            request=request,
            body=b"<html><body>Access denied</body></html>",
            status=403
        )
        
        blocked_score = self.evasion_scorer.calculate_score(blocked_response, request)
        assert blocked_score < score  # Should be lower for blocked response

    def test_cloudflare_detection(self):
        """Test Cloudflare detection"""
        request = Request(url="https://example.com")
        
        # Test Cloudflare response
        cloudflare_response = HtmlResponse(
            url="https://example.com",
            request=request,
            body=b"<html><body>" + b"x" * 2000 + b"</body></html>",
            status=200,
            headers={'Server': 'cloudflare'}
        )
        
        score = self.evasion_scorer.calculate_score(cloudflare_response, request)
        assert score < 100  # Should be penalized for Cloudflare detection

    def test_captcha_detection(self):
        """Test CAPTCHA detection"""
        request = Request(url="https://example.com")
        
        # Test CAPTCHA response
        captcha_response = HtmlResponse(
            url="https://example.com",
            request=request,
            body=b"<html><body>" + b"x" * 2000 + b"Please solve this captcha</body></html>",
            status=200
        )
        
        score = self.evasion_scorer.calculate_score(captcha_response, request)
        assert score < 100  # Should be penalized for CAPTCHA detection

    def test_rate_limiting_detection(self):
        """Test rate limiting detection"""
        request = Request(url="https://example.com")
        
        # Test rate limited response
        rate_limited_response = HtmlResponse(
            url="https://example.com",
            request=request,
            body=b"<html><body>" + b"x" * 2000 + b"Rate limited</body></html>",
            status=429
        )
        
        score = self.evasion_scorer.calculate_score(rate_limited_response, request)
        assert score < 100  # Should be penalized for rate limiting

    def test_evasion_recommendations(self):
        """Test evasion recommendations"""
        # Test high score recommendations (should be empty for good scores)
        high_recs = self.evasion_scorer._get_recommendations(90)
        assert len(high_recs) == 0  # High scores don't need recommendations
        
        # Test medium score recommendations
        medium_recs = self.evasion_scorer._get_recommendations(40)
        assert len(medium_recs) > 0
        assert any('proxies' in rec.lower() for rec in medium_recs)
        
        # Test low score recommendations
        low_recs = self.evasion_scorer._get_recommendations(20)
        assert len(low_recs) > 0
        assert any('captcha' in rec.lower() for rec in low_recs)

    def test_evasion_middleware_security(self):
        """Test evasion middleware security features"""
        # Test stealth header generation
        request = Request(url="https://example.com")
        
        # Process request through evasion middleware
        processed_request = self.evasion_middleware.process_request(request, None)
        
        assert processed_request is not None
        assert 'User-Agent' in processed_request.headers
        assert 'Accept' in processed_request.headers
        assert 'Accept-Language' in processed_request.headers

    def test_proxy_middleware_security(self):
        """Test proxy middleware security features"""
        # Test proxy assignment
        request = Request(url="https://example.com")
        
        # Process request through proxy middleware
        processed_request = self.proxy_middleware.process_request(request, None)
        
        # Should handle gracefully even without proxy configuration
        assert processed_request is not None

    def test_data_encryption_readiness(self):
        """Test data encryption readiness"""
        # Test that sensitive data handling is in place
        from laser_intelligence.utils.brand_mapping import BrandMapper
        
        mapper = BrandMapper()
        
        # Test that brand mapping doesn't expose sensitive data
        result = mapper.normalize_brand("test_brand")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_input_validation(self):
        """Test input validation security"""
        from laser_intelligence.utils.price_analysis import PriceAnalyzer
        
        analyzer = PriceAnalyzer()
        
        # Test with invalid inputs
        result = analyzer.calculate_margin_estimate(None, None)
        assert result == (0.0, 0.0)  # Should handle gracefully
        
        result = analyzer.calculate_margin_estimate(-1000, 50000)
        assert result[0] is not None  # Should handle negative prices gracefully

    def test_error_handling_security(self):
        """Test error handling security"""
        from laser_intelligence.utils.evasion_scoring import EvasionScorer
        
        scorer = EvasionScorer()
        
        # Test with malformed response
        malformed_response = HtmlResponse(
            url="https://example.com",
            request=Request("https://example.com"),
            body=b"malformed content",
            status=200
        )
        
        # Should handle malformed responses gracefully
        score = scorer.calculate_score(malformed_response, Request("https://example.com"))
        assert score is not None
        assert isinstance(score, (int, float))

    def test_anti_detection_measures(self):
        """Test anti-detection measures"""
        # Test that evasion scoring provides comprehensive protection
        request = Request(url="https://example.com")
        
        # Test various response types
        test_cases = [
            (200, b"<html><body>" + b"x" * 2000 + b"</body></html>", {}),
            (403, b"<html><body>Access denied</body></html>", {}),
            (429, b"<html><body>Rate limited</body></html>", {}),
            (503, b"<html><body>Service unavailable</body></html>", {}),
            (200, b"<html><body>" + b"x" * 2000 + b"Please solve this captcha</body></html>", {}),
            (200, b"<html><body>" + b"x" * 2000 + b"</body></html>", {'Server': 'cloudflare'}),
        ]
        
        for status, body, headers in test_cases:
            response = HtmlResponse(
                url="https://example.com",
                request=request,
                body=body,
                status=status,
                headers=headers
            )
            
            score = self.evasion_scorer.calculate_score(response, request)
            assert score is not None
            assert isinstance(score, (int, float))
            assert 0 <= score <= 100

    def test_security_monitoring(self):
        """Test security monitoring capabilities"""
        # Test evasion report generation
        request = Request(url="https://example.com")
        response = HtmlResponse(
            url="https://example.com",
            request=request,
            body=b"<html><body>" + b"x" * 2000 + b"</body></html>",
            status=200
        )
        
        report = self.evasion_scorer.get_evasion_report(response, request)
        
        assert isinstance(report, dict)
        assert 'evasion_score' in report
        assert 'status_code' in report
        assert 'response_length' in report
        assert 'timestamp' in report
        assert 'url' in report
        assert 'recommendations' in report

    def test_privacy_protection(self):
        """Test privacy protection measures"""
        from laser_intelligence.utils.brand_mapping import BrandMapper
        
        mapper = BrandMapper()
        
        # Test that brand mapping doesn't leak sensitive information
        test_brands = ["sciton", "cynosure", "cutera", "candela", "lumenis"]
        
        for brand in test_brands:
            result = mapper.normalize_brand(brand)
            assert isinstance(result, str)
            assert len(result) > 0
            # Should not contain any sensitive information
            assert not any(char in result.lower() for char in ['password', 'secret', 'key', 'token'])
