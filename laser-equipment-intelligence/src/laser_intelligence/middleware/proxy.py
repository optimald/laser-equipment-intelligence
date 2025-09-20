"""
Proxy rotation middleware for Scrapy
"""

import random
import time
import requests
from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from laser_intelligence.utils.proxy_manager import ProxyManager


class ProxyMiddleware:
    """Proxy rotation middleware with health monitoring"""
    
    def __init__(self):
        self.proxy_manager = ProxyManager()
        self.failed_proxies = set()
        self.proxy_stats = {}
        
    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(middleware.spider_closed, signal=signals.spider_closed)
        return middleware
    
    def spider_opened(self, spider):
        spider.logger.info('ProxyMiddleware opened')
        # Initialize proxy pool
        self.proxy_manager.initialize_proxy_pool()
    
    def spider_closed(self, spider):
        spider.logger.info('ProxyMiddleware closed')
        # Log proxy statistics
        self._log_proxy_stats(spider)
    
    def process_request(self, request, spider):
        """Add proxy to request"""
        if not request.meta.get('proxy'):
            proxy = self._get_healthy_proxy()
            if proxy:
                request.meta['proxy'] = proxy
                # Extract IP from proxy URL, handling authentication
                proxy_part = proxy.split('://')[1]
                if '@' in proxy_part:
                    proxy_part = proxy_part.split('@')[1]  # Remove auth part
                request.meta['proxy_ip'] = proxy_part.split(':')[0]
                spider.logger.debug(f'Using proxy: {proxy}')
        
        return request
    
    def process_response(self, request, response, spider):
        """Handle proxy failures and rotation"""
        proxy = request.meta.get('proxy')
        if proxy:
            # Track proxy performance
            self._track_proxy_performance(proxy, response.status)
            
            # Handle proxy failures
            if response.status in [403, 429, 503]:
                spider.logger.warning(f'Proxy {proxy} failed with status {response.status}')
                self._mark_proxy_failed(proxy)
                
                # Retry with new proxy
                return request.replace(
                    meta={**request.meta, 'proxy': None},
                    dont_filter=True
                )
        
        return response
    
    def _get_healthy_proxy(self):
        """Get a healthy proxy from the pool"""
        available_proxies = [
            proxy for proxy in self.proxy_manager.get_proxy_pool()
            if proxy not in self.failed_proxies
        ]
        
        if not available_proxies:
            # Reset failed proxies if all are marked as failed
            self.failed_proxies.clear()
            available_proxies = self.proxy_manager.get_proxy_pool()
        
        return random.choice(available_proxies) if available_proxies else None
    
    def _track_proxy_performance(self, proxy, status_code):
        """Track proxy performance statistics"""
        if proxy not in self.proxy_stats:
            self.proxy_stats[proxy] = {
                'requests': 0,
                'successes': 0,
                'failures': 0,
                'last_used': None
            }
        
        stats = self.proxy_stats[proxy]
        stats['requests'] += 1
        stats['last_used'] = time.time()
        
        if status_code == 200:
            stats['successes'] += 1
        else:
            stats['failures'] += 1
    
    def _mark_proxy_failed(self, proxy):
        """Mark proxy as failed"""
        self.failed_proxies.add(proxy)
        self.proxy_manager.report_proxy_failure(proxy)
    
    def _log_proxy_stats(self, spider):
        """Log proxy performance statistics"""
        spider.logger.info('Proxy Performance Statistics:')
        for proxy, stats in self.proxy_stats.items():
            success_rate = (stats['successes'] / stats['requests']) * 100 if stats['requests'] > 0 else 0
            spider.logger.info(f'{proxy}: {stats["requests"]} requests, {success_rate:.1f}% success rate')


class ProxyManager:
    """Manage proxy pool and health monitoring"""
    
    def __init__(self):
        self.proxy_pool = []
        self.proxy_tiers = {
            'residential_us': [],
            'residential_eu': [],
            'datacenter': []
        }
        self.failed_proxies = set()
    
    def initialize_proxy_pool(self):
        """Initialize proxy pool from configuration"""
        # In production, this would load from Bright Data/Oxylabs APIs
        # For now, using example proxy format
        self.proxy_pool = [
            'http://user:pass@proxy1.example.com:8080',
            'http://user:pass@proxy2.example.com:8080',
            'http://user:pass@proxy3.example.com:8080',
        ]
    
    def get_proxy_pool(self):
        """Get current proxy pool"""
        return self.proxy_pool
    
    def get_proxy_by_tier(self, tier):
        """Get proxy from specific tier"""
        return random.choice(self.proxy_tiers.get(tier, []))
    
    def report_proxy_failure(self, proxy):
        """Report proxy failure for health monitoring"""
        self.failed_proxies.add(proxy)
        # In production, this would update proxy health metrics
    
    def get_proxy_health_score(self, proxy):
        """Get health score for proxy"""
        # Calculate health score based on success rate, response time, etc.
        return random.uniform(0.5, 1.0)  # Placeholder
