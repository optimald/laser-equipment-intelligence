"""
Scrapy Impersonate middleware for advanced TLS/HTTP2 fingerprinting
"""

import random
from typing import Dict, Any, Optional
from scrapy import Request
from scrapy.http import Response
from scrapy.downloadermiddlewares.retry import RetryMiddleware


class ImpersonateMiddleware:
    """Advanced TLS/HTTP2 fingerprinting middleware using Scrapy Impersonate"""
    
    def __init__(self):
        # Browser fingerprints to impersonate
        self.browser_fingerprints = [
            'chrome120',  # Chrome 120
            'chrome119',  # Chrome 119
            'chrome118',  # Chrome 118
            'firefox120', # Firefox 120
            'firefox119', # Firefox 119
            'safari17',   # Safari 17
            'safari16',   # Safari 16
        ]
        
        # Cloudflare bypass fingerprints
        self.cloudflare_fingerprints = [
            'chrome120',
            'chrome119',
            'firefox120',
        ]
        
        # Current fingerprint being used
        self.current_fingerprint = None
        self.fingerprint_rotation_count = 0
        self.max_requests_per_fingerprint = 50
    
    def process_request(self, request: Request, spider) -> Optional[Request]:
        """Add impersonation headers to request"""
        try:
            # Select fingerprint based on target site
            fingerprint = self._select_fingerprint(request.url, spider)
            
            # Add impersonation headers
            request.meta['impersonate'] = fingerprint
            request.meta['impersonate_headers'] = self._get_impersonate_headers(fingerprint)
            
            # Add TLS fingerprinting
            request.meta['tls_fingerprint'] = self._get_tls_fingerprint(fingerprint)
            
            # Add HTTP/2 fingerprinting
            request.meta['http2_fingerprint'] = self._get_http2_fingerprint(fingerprint)
            
            # Rotate fingerprint if needed
            self._rotate_fingerprint_if_needed()
            
            spider.logger.debug(f'Applied impersonation fingerprint: {fingerprint} to {request.url}')
            
        except Exception as e:
            spider.logger.error(f'Error in ImpersonateMiddleware: {e}')
        
        return request
    
    def process_response(self, request: Request, response: Response, spider) -> Response:
        """Process response and handle fingerprint rotation"""
        try:
            # Check for Cloudflare detection
            if self._is_cloudflare_blocked(response):
                spider.logger.warning(f'Cloudflare block detected on {request.url}')
                
                # Switch to Cloudflare bypass fingerprint
                new_fingerprint = random.choice(self.cloudflare_fingerprints)
                request.meta['impersonate'] = new_fingerprint
                
                # Retry with new fingerprint
                return request.replace(meta=request.meta)
            
            # Check for other anti-bot measures
            if self._is_anti_bot_detected(response):
                spider.logger.warning(f'Anti-bot detection on {request.url}')
                
                # Rotate fingerprint
                self._force_fingerprint_rotation()
                new_fingerprint = random.choice(self.browser_fingerprints)
                request.meta['impersonate'] = new_fingerprint
                
                # Retry with new fingerprint
                return request.replace(meta=request.meta)
            
        except Exception as e:
            spider.logger.error(f'Error processing response in ImpersonateMiddleware: {e}')
        
        return response
    
    def _select_fingerprint(self, url: str, spider) -> str:
        """Select appropriate fingerprint based on target site"""
        # Check if we have a site-specific fingerprint
        site_fingerprint = self._get_site_specific_fingerprint(url)
        if site_fingerprint:
            return site_fingerprint
        
        # Use current fingerprint or select new one
        if not self.current_fingerprint:
            self.current_fingerprint = random.choice(self.browser_fingerprints)
        
        return self.current_fingerprint
    
    def _get_site_specific_fingerprint(self, url: str) -> Optional[str]:
        """Get site-specific fingerprint configuration"""
        site_configs = {
            'dotmed.com': 'chrome120',  # DOTmed works best with Chrome 120
            'bidspotter.com': 'firefox120',  # BidSpotter prefers Firefox
            'proxibid.com': 'chrome119',  # Proxibid works with Chrome 119
            'govdeals.com': 'chrome120',  # GovDeals standard Chrome
            'ebay.com': 'chrome120',  # eBay standard Chrome
            'thelaseragent.com': 'chrome120',  # Standard Chrome
        }
        
        for domain, fingerprint in site_configs.items():
            if domain in url:
                return fingerprint
        
        return None
    
    def _get_impersonate_headers(self, fingerprint: str) -> Dict[str, str]:
        """Get headers for specific browser fingerprint"""
        header_templates = {
            'chrome120': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                'Sec-Ch-Ua-Mobile': '?0',
                'Sec-Ch-Ua-Platform': '"Windows"',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
            },
            'firefox120': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            },
            'safari17': {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
            }
        }
        
        return header_templates.get(fingerprint, header_templates['chrome120'])
    
    def _get_tls_fingerprint(self, fingerprint: str) -> Dict[str, Any]:
        """Get TLS fingerprint configuration"""
        tls_configs = {
            'chrome120': {
                'cipher_suites': [
                    'TLS_AES_128_GCM_SHA256',
                    'TLS_AES_256_GCM_SHA384',
                    'TLS_CHACHA20_POLY1305_SHA256',
                    'TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256',
                    'TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256',
                    'TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384',
                    'TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384',
                ],
                'supported_versions': ['TLSv1.3', 'TLSv1.2'],
                'signature_algorithms': [
                    'rsa_pss_rsae_sha256',
                    'rsa_pkcs1_sha256',
                    'ecdsa_secp256r1_sha256',
                    'rsa_pss_rsae_sha384',
                    'rsa_pkcs1_sha384',
                ]
            },
            'firefox120': {
                'cipher_suites': [
                    'TLS_AES_128_GCM_SHA256',
                    'TLS_CHACHA20_POLY1305_SHA256',
                    'TLS_AES_256_GCM_SHA384',
                    'TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256',
                    'TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256',
                    'TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384',
                    'TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384',
                ],
                'supported_versions': ['TLSv1.3', 'TLSv1.2'],
                'signature_algorithms': [
                    'rsa_pss_rsae_sha256',
                    'rsa_pkcs1_sha256',
                    'ecdsa_secp256r1_sha256',
                ]
            }
        }
        
        return tls_configs.get(fingerprint, tls_configs['chrome120'])
    
    def _get_http2_fingerprint(self, fingerprint: str) -> Dict[str, Any]:
        """Get HTTP/2 fingerprint configuration"""
        http2_configs = {
            'chrome120': {
                'settings': {
                    'HEADER_TABLE_SIZE': 65536,
                    'ENABLE_PUSH': 0,
                    'MAX_CONCURRENT_STREAMS': 1000,
                    'INITIAL_WINDOW_SIZE': 6291456,
                    'MAX_HEADER_LIST_SIZE': 262144,
                },
                'connection_flow_control_window': 6291456,
                'stream_flow_control_window': 6291456,
            },
            'firefox120': {
                'settings': {
                    'HEADER_TABLE_SIZE': 65536,
                    'ENABLE_PUSH': 0,
                    'MAX_CONCURRENT_STREAMS': 100,
                    'INITIAL_WINDOW_SIZE': 131072,
                    'MAX_HEADER_LIST_SIZE': 262144,
                },
                'connection_flow_control_window': 131072,
                'stream_flow_control_window': 131072,
            }
        }
        
        return http2_configs.get(fingerprint, http2_configs['chrome120'])
    
    def _is_cloudflare_blocked(self, response: Response) -> bool:
        """Check if response indicates Cloudflare blocking"""
        cloudflare_indicators = [
            'cloudflare',
            'checking your browser',
            'please wait',
            'ddos protection',
            'ray id',
            'cf-ray',
        ]
        
        response_text = response.text.lower()
        response_headers = {k.lower(): v.lower() for k, v in response.headers.items()}
        
        # Check response text
        for indicator in cloudflare_indicators:
            if indicator in response_text:
                return True
        
        # Check headers
        if 'cf-ray' in response_headers or 'cloudflare' in response_headers.get('server', ''):
            return True
        
        # Check status code
        if response.status in [403, 429, 503]:
            return True
        
        return False
    
    def _is_anti_bot_detected(self, response: Response) -> bool:
        """Check if response indicates anti-bot detection"""
        anti_bot_indicators = [
            'access denied',
            'blocked',
            'captcha',
            'robot',
            'bot detection',
            'suspicious activity',
            'rate limit',
            'too many requests',
        ]
        
        response_text = response.text.lower()
        
        for indicator in anti_bot_indicators:
            if indicator in response_text:
                return True
        
        return False
    
    def _rotate_fingerprint_if_needed(self):
        """Rotate fingerprint if request count exceeds limit"""
        self.fingerprint_rotation_count += 1
        
        if self.fingerprint_rotation_count >= self.max_requests_per_fingerprint:
            self._force_fingerprint_rotation()
    
    def _force_fingerprint_rotation(self):
        """Force fingerprint rotation"""
        old_fingerprint = self.current_fingerprint
        
        # Select new fingerprint (different from current)
        available_fingerprints = [f for f in self.browser_fingerprints if f != old_fingerprint]
        self.current_fingerprint = random.choice(available_fingerprints)
        
        # Reset rotation count
        self.fingerprint_rotation_count = 0
        
        return self.current_fingerprint
    
    def get_fingerprint_stats(self) -> Dict[str, Any]:
        """Get fingerprint usage statistics"""
        return {
            'current_fingerprint': self.current_fingerprint,
            'requests_with_current_fingerprint': self.fingerprint_rotation_count,
            'max_requests_per_fingerprint': self.max_requests_per_fingerprint,
            'available_fingerprints': len(self.browser_fingerprints),
            'cloudflare_bypass_fingerprints': len(self.cloudflare_fingerprints),
        }
