# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import time
import random

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class LaserIntelligenceSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    async def process_start(self, start):
        # Called with an async iterator over the spider start() method or the
        # maching method of an earlier spider middleware.
        async for item_or_request in start:
            yield item_or_request

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class SourceTrackingMiddleware:
    """Middleware to track source performance and implement evasion strategies"""
    
    def __init__(self):
        self.start_times = {}
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls()
    
    def process_request(self, request, spider):
        """Process outgoing request with evasion strategy"""
        # Record start time
        self.start_times[request.url] = time.time()
        
        # Get source name from spider
        source_name = getattr(spider, 'name', 'unknown')
        
        # Simple evasion strategy (can be enhanced with source_tracker)
        delay = random.uniform(1, 3)  # Random delay between 1-3 seconds
        time.sleep(delay)
        
        return None
    
    def process_response(self, request, response, spider):
        """Process response and track metrics"""
        source_name = getattr(spider, 'name', 'unknown')
        start_time = self.start_times.get(request.url, time.time())
        response_time = time.time() - start_time
        
        # Check for blocks/challenges
        if self._is_blocked(response):
            spider.logger.warning(f"Block detected for {source_name}: {response.url}")
        else:
            # Count items found (this is a simplified count)
            items_count = len(response.css('div, article, .item, .listing').getall())
            spider.logger.info(f"Success for {source_name}: {items_count} potential items")
        
        # Clean up
        if request.url in self.start_times:
            del self.start_times[request.url]
        
        return response
    
    def process_exception(self, request, exception, spider):
        """Process exceptions and track failures"""
        source_name = getattr(spider, 'name', 'unknown')
        spider.logger.error(f"Failure for {source_name}: {exception}")
        
        # Clean up
        if request.url in self.start_times:
            del self.start_times[request.url]
    
    def _is_blocked(self, response) -> bool:
        """Check if response indicates blocking"""
        # Common indicators of blocking
        block_indicators = [
            'challenge', 'captcha', 'blocked', 'access denied',
            'robot', 'bot detection', 'verification required',
            'splashui', 'challenge page'
        ]
        
        url_lower = response.url.lower()
        content_lower = response.text.lower() if response.text else ""
        
        for indicator in block_indicators:
            if indicator in url_lower or indicator in content_lower:
                return True
        
        # Check for redirect to challenge pages
        if response.status in [307, 302] and 'challenge' in url_lower:
            return True
        
        return False


class LaserIntelligenceDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class SourceTrackingMiddleware:
    """Middleware to track source performance and implement evasion strategies"""
    
    def __init__(self):
        self.start_times = {}
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls()
    
    def process_request(self, request, spider):
        """Process outgoing request with evasion strategy"""
        # Record start time
        self.start_times[request.url] = time.time()
        
        # Get source name from spider
        source_name = getattr(spider, 'name', 'unknown')
        
        # Simple evasion strategy (can be enhanced with source_tracker)
        delay = random.uniform(1, 3)  # Random delay between 1-3 seconds
        time.sleep(delay)
        
        return None
    
    def process_response(self, request, response, spider):
        """Process response and track metrics"""
        source_name = getattr(spider, 'name', 'unknown')
        start_time = self.start_times.get(request.url, time.time())
        response_time = time.time() - start_time
        
        # Check for blocks/challenges
        if self._is_blocked(response):
            spider.logger.warning(f"Block detected for {source_name}: {response.url}")
        else:
            # Count items found (this is a simplified count)
            items_count = len(response.css('div, article, .item, .listing').getall())
            spider.logger.info(f"Success for {source_name}: {items_count} potential items")
        
        # Clean up
        if request.url in self.start_times:
            del self.start_times[request.url]
        
        return response
    
    def process_exception(self, request, exception, spider):
        """Process exceptions and track failures"""
        source_name = getattr(spider, 'name', 'unknown')
        spider.logger.error(f"Failure for {source_name}: {exception}")
        
        # Clean up
        if request.url in self.start_times:
            del self.start_times[request.url]
    
    def _is_blocked(self, response) -> bool:
        """Check if response indicates blocking"""
        # Common indicators of blocking
        block_indicators = [
            'challenge', 'captcha', 'blocked', 'access denied',
            'robot', 'bot detection', 'verification required',
            'splashui', 'challenge page'
        ]
        
        url_lower = response.url.lower()
        content_lower = response.text.lower() if response.text else ""
        
        for indicator in block_indicators:
            if indicator in url_lower or indicator in content_lower:
                return True
        
        # Check for redirect to challenge pages
        if response.status in [307, 302] and 'challenge' in url_lower:
            return True
        
        return False
