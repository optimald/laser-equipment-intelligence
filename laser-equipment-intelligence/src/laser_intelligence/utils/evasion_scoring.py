"""
Evasion effectiveness scoring and monitoring
"""

import time
import re
from typing import Dict, Any


class EvasionScorer:
    """Calculate evasion effectiveness scores"""
    
    def __init__(self):
        self.base_score = 100
        self.penalty_factors = {
            'cloudflare': -20,
            'captcha': -30,
            'blocked': -50,
            'short_response': -15,
            'suspicious_headers': -10,
            'rate_limited': -25,
        }
    
    def calculate_score(self, response, request) -> int:
        """Calculate evasion score based on response analysis"""
        score = self.base_score
        
        # Check for anti-bot indicators
        score += self._check_cloudflare(response)
        score += self._check_captcha(response)
        score += self._check_blocking(response)
        score += self._check_response_length(response)
        score += self._check_headers(response)
        score += self._check_rate_limiting(response)
        
        # Bonus for successful evasion
        if response.status == 200 and len(response.text) > 1000:
            score += 10
        
        return max(0, min(100, score))
    
    def _check_cloudflare(self, response) -> int:
        """Check for Cloudflare protection"""
        server_header = response.headers.get('Server', b'').decode('utf-8', errors='ignore').lower()
        if 'cloudflare' in server_header:
            return self.penalty_factors['cloudflare']
        return 0
    
    def _check_captcha(self, response) -> int:
        """Check for CAPTCHA presence"""
        text_lower = response.text.lower()
        captcha_indicators = ['captcha', 'recaptcha', 'hcaptcha', 'challenge']
        
        if any(indicator in text_lower for indicator in captcha_indicators):
            return self.penalty_factors['captcha']
        return 0
    
    def _check_blocking(self, response) -> int:
        """Check for blocking indicators"""
        if response.status in [403, 503]:
            return self.penalty_factors['blocked']
        
        text_lower = response.text.lower()
        blocking_indicators = ['access denied', 'blocked', 'forbidden']
        
        # Don't trigger blocking penalty for rate limit text if status is 429
        if response.status != 429:
            blocking_indicators.append('rate limit')
        
        if any(indicator in text_lower for indicator in blocking_indicators):
            return self.penalty_factors['blocked']
        return 0
    
    def _check_response_length(self, response) -> int:
        """Check for suspiciously short responses"""
        if len(response.text) < 1000:
            return self.penalty_factors['short_response']
        return 0
    
    def _check_headers(self, response) -> int:
        """Check for suspicious response headers"""
        suspicious_headers = [
            'cf-ray',
            'cf-cache-status',
            'x-ratelimit-remaining',
            'x-ratelimit-reset'
        ]
        
        if any(header in response.headers for header in suspicious_headers):
            return self.penalty_factors['suspicious_headers']
        return 0
    
    def _check_rate_limiting(self, response) -> int:
        """Check for rate limiting indicators"""
        if response.status == 429:
            return self.penalty_factors['rate_limited']
        
        # Check for rate limit headers
        rate_limit_headers = [
            'x-ratelimit-remaining',
            'x-ratelimit-limit',
            'retry-after'
        ]
        
        if any(header in response.headers for header in rate_limit_headers):
            return self.penalty_factors['rate_limited']
        return 0
    
    def get_evasion_report(self, response, request) -> Dict[str, Any]:
        """Generate detailed evasion report"""
        score = self.calculate_score(response, request)
        
        return {
            'evasion_score': score,
            'status_code': response.status,
            'response_length': len(response.text),
            'headers_analyzed': len(response.headers),
            'timestamp': time.time(),
            'url': request.url,
            'proxy_used': request.meta.get('proxy'),
            'user_agent': request.headers.get('User-Agent', b'').decode('utf-8', errors='ignore'),
            'recommendations': self._get_recommendations(score)
        }
    
    def _get_recommendations(self, score: int) -> list:
        """Get recommendations based on evasion score"""
        recommendations = []
        
        if score < 50:
            recommendations.append('Consider switching to residential proxies')
            recommendations.append('Increase delay between requests')
            recommendations.append('Rotate user agents more frequently')
        
        if score < 30:
            recommendations.append('Implement CAPTCHA solving')
            recommendations.append('Use stealth browser automation')
            recommendations.append('Consider using different proxy provider')
        
        if score < 20:
            recommendations.append('Pause scraping for this source')
            recommendations.append('Review and update evasion strategies')
            recommendations.append('Consider manual intervention')
        
        return recommendations
