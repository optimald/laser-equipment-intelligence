"""
Anti-detection and evasion middleware for Scrapy
"""

import random
import time
from scrapy import signals
from scrapy.http import HtmlResponse
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from fake_useragent import UserAgent
from laser_intelligence.utils.evasion_scoring import EvasionScorer


class EvasionMiddleware:
    """Anti-detection middleware implementing human-like behavior simulation"""
    
    def __init__(self):
        self.ua = UserAgent()
        self.evasion_scorer = EvasionScorer()
        self.session_durations = {}
        
    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware
    
    def spider_opened(self, spider):
        spider.logger.info('EvasionMiddleware opened')
    
    def spider_closed(self, spider):
        spider.logger.info('EvasionMiddleware closed')
    
    def process_request(self, request, spider):
        """Add evasion headers and simulate human behavior"""
        # Generate random headers
        request.headers.update(self._generate_stealth_headers())
        
        # Add random delays for human-like behavior
        delay = random.uniform(2, 10)
        time.sleep(delay)
        
        # Track session duration
        domain = request.url.split('/')[2]
        if domain not in self.session_durations:
            self.session_durations[domain] = time.time()
        
        # Add evasion metadata
        request.meta['evasion_start_time'] = time.time()
        request.meta['session_duration'] = time.time() - self.session_durations[domain]
        
        return request
    
    def process_response(self, request, response, spider):
        """Calculate evasion score and handle detection"""
        # Calculate evasion effectiveness
        evasion_score = self.evasion_scorer.calculate_score(response, request)
        response.meta['evasion_score'] = evasion_score
        
        # Check for anti-bot indicators
        if self._detect_blocking(response):
            spider.logger.warning(f'Potential blocking detected on {request.url}')
            # Trigger proxy rotation or other evasion measures
            return self._handle_blocking(request, response, spider)
        
        return response
    
    def _generate_stealth_headers(self):
        """Generate human-like headers"""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': random.choice([
                'en-US,en;q=0.5',
                'en-GB,en;q=0.5',
                'en-CA,en;q=0.5'
            ]),
            'Accept-Encoding': 'gzip, deflate',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': random.choice([
                'https://www.google.com/',
                'https://www.bing.com/',
                'https://duckduckgo.com/'
            ]),
            'Cache-Control': 'max-age=0',
        }
    
    def _detect_blocking(self, response):
        """Detect potential blocking or anti-bot measures"""
        server_header = response.headers.get('Server', '').lower()
        if isinstance(server_header, bytes):
            server_header = server_header.decode('utf-8', errors='ignore').lower()
        blocking_indicators = [
            'cloudflare' in server_header,
            'captcha' in response.text.lower(),
            'access denied' in response.text.lower(),
            'blocked' in response.text.lower(),
            response.status in [403, 429, 503],
            len(response.text) < 1000,  # Suspiciously short response
        ]
        
        return any(blocking_indicators)
    
    def _handle_blocking(self, request, response, spider):
        """Handle detected blocking"""
        spider.logger.warning(f'Handling blocking for {request.url}')
        
        # For now, just log the issue
        # In production, this would trigger proxy rotation, CAPTCHA solving, etc.
        return response


class HumanBehaviorSimulator:
    """Simulate human-like browsing behavior"""
    
    @staticmethod
    def simulate_mouse_movement():
        """Simulate mouse movement patterns"""
        # This would integrate with Playwright for actual mouse simulation
        pass
    
    @staticmethod
    def simulate_scroll_pattern():
        """Simulate natural scrolling behavior"""
        # Gradual scrolling with pauses
        scroll_delays = [0.5, 1.0, 0.3, 0.8, 1.2]
        return random.choice(scroll_delays)
    
    @staticmethod
    def simulate_click_pattern():
        """Simulate natural click timing"""
        # Random delays between clicks
        return random.uniform(0.1, 0.5)
    
    @staticmethod
    def get_session_duration():
        """Get realistic session duration"""
        # Variable browsing time per session (30s-5min)
        return random.uniform(30, 300)
