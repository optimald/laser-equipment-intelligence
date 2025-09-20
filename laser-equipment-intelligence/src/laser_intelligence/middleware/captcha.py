"""
CAPTCHA solving middleware for Scrapy
"""

import time
import requests
from scrapy import signals
from scrapy.http import HtmlResponse
from laser_intelligence.utils.captcha_solver import CaptchaSolver


class CaptchaMiddleware:
    """CAPTCHA solving middleware with 2Captcha integration"""
    
    def __init__(self):
        self.captcha_solver = CaptchaSolver()
        self.solved_captchas = 0
        self.failed_captchas = 0
        
    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware
    
    def spider_opened(self, spider):
        spider.logger.info('CaptchaMiddleware opened')
    
    def spider_closed(self, spider):
        spider.logger.info('CaptchaMiddleware closed')
        spider.logger.info(f'CAPTCHA Statistics: {self.solved_captchas} solved, {self.failed_captchas} failed')
    
    def process_response(self, request, response, spider):
        """Detect and solve CAPTCHAs"""
        if self._detect_captcha(response):
            spider.logger.info(f'CAPTCHA detected on {request.url}')
            
            # Attempt to solve CAPTCHA
            solved_response = self._solve_captcha(request, response, spider)
            if solved_response:
                self.solved_captchas += 1
                return solved_response
            else:
                self.failed_captchas += 1
                spider.logger.error(f'Failed to solve CAPTCHA on {request.url}')
        
        return response
    
    def _detect_captcha(self, response):
        """Detect CAPTCHA presence in response"""
        captcha_indicators = [
            'captcha' in response.text.lower(),
            'recaptcha' in response.text.lower(),
            'hcaptcha' in response.text.lower(),
            'challenge' in response.text.lower(),
            'verification' in response.text.lower(),
            'robot' in response.text.lower(),
            'bot' in response.text.lower(),
        ]
        
        return any(captcha_indicators)
    
    def _solve_captcha(self, request, response, spider):
        """Solve CAPTCHA and return new response"""
        try:
            # Extract CAPTCHA image or challenge
            captcha_data = self._extract_captcha_data(response)
            if not captcha_data:
                return None
            
            # Solve CAPTCHA using 2Captcha service
            solution = self.captcha_solver.solve_captcha(captcha_data)
            if not solution:
                return None
            
            # Submit solution and get new response
            return self._submit_captcha_solution(request, response, solution, spider)
            
        except Exception as e:
            spider.logger.error(f'Error solving CAPTCHA: {e}')
            return None
    
    def _extract_captcha_data(self, response):
        """Extract CAPTCHA image or challenge data"""
        # This would extract CAPTCHA image URLs or challenge data
        # For now, return placeholder data
        return {
            'type': 'image',
            'image_url': 'placeholder_captcha_url',
            'site_key': 'placeholder_site_key'
        }
    
    def _submit_captcha_solution(self, request, response, solution, spider):
        """Submit CAPTCHA solution and return new response"""
        # This would submit the solution and get a new response
        # For now, return the original response
        return response


class CaptchaSolver:
    """CAPTCHA solving service integration"""
    
    def __init__(self):
        self.api_key = None  # Would be loaded from environment
        self.api_url = 'http://2captcha.com'
        self.timeout = 120  # 2 minutes timeout
    
    def solve_captcha(self, captcha_data):
        """Solve CAPTCHA using 2Captcha service"""
        try:
            # Submit CAPTCHA for solving
            task_id = self._submit_captcha(captcha_data)
            if not task_id:
                return None
            
            # Wait for solution
            solution = self._get_solution(task_id)
            return solution
            
        except Exception as e:
            print(f'Error solving CAPTCHA: {e}')
            return None
    
    def _submit_captcha(self, captcha_data):
        """Submit CAPTCHA to 2Captcha service"""
        # This would make actual API call to 2Captcha
        # For now, return placeholder task ID
        return 'placeholder_task_id'
    
    def _get_solution(self, task_id):
        """Get solution from 2Captcha service"""
        # This would poll for solution
        # For now, return placeholder solution
        return 'placeholder_solution'
    
    def get_balance(self):
        """Get account balance from 2Captcha service"""
        # This would check account balance
        return 10.50  # Placeholder balance
