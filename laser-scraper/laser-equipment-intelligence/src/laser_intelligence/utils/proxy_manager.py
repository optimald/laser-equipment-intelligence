"""
Proxy management utility for laser equipment intelligence platform
"""

import random
import time
import requests
from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ProxyInfo:
    """Proxy information container"""
    ip: str
    port: int
    username: str
    password: str
    tier: str
    country: str
    success_rate: float = 0.0
    last_used: float = 0.0
    failure_count: int = 0


class ProxyManager:
    """Manage proxy pool and health monitoring"""
    
    def __init__(self):
        self.proxy_pool: List[ProxyInfo] = []
        self.failed_proxies: set = set()
        self.proxy_stats: Dict[str, Dict] = {}
        self.health_check_interval = 300  # 5 minutes
        self.last_health_check = 0
        
    def initialize_proxy_pool(self):
        """Initialize proxy pool from configuration"""
        # In production, this would load from Bright Data/Oxylabs APIs
        # For now, using example proxy format
        
        # Residential US proxies
        us_proxies = [
            ProxyInfo("192.168.1.100", 8080, "user1", "pass1", "residential_us", "US"),
            ProxyInfo("192.168.1.101", 8080, "user2", "pass2", "residential_us", "US"),
            ProxyInfo("192.168.1.102", 8080, "user3", "pass3", "residential_us", "US"),
        ]
        
        # Residential EU proxies
        eu_proxies = [
            ProxyInfo("192.168.2.100", 8080, "user4", "pass4", "residential_eu", "DE"),
            ProxyInfo("192.168.2.101", 8080, "user5", "pass5", "residential_eu", "UK"),
            ProxyInfo("192.168.2.102", 8080, "user6", "pass6", "residential_eu", "FR"),
        ]
        
        # Datacenter proxies
        dc_proxies = [
            ProxyInfo("192.168.3.100", 8080, "user7", "pass7", "datacenter", "US"),
            ProxyInfo("192.168.3.101", 8080, "user8", "pass8", "datacenter", "US"),
            ProxyInfo("192.168.3.102", 8080, "user9", "pass9", "datacenter", "US"),
        ]
        
        self.proxy_pool = us_proxies + eu_proxies + dc_proxies
        
        # Initialize stats for each proxy
        for proxy in self.proxy_pool:
            proxy_key = f"{proxy.ip}:{proxy.port}"
            self.proxy_stats[proxy_key] = {
                'requests': 0,
                'successes': 0,
                'failures': 0,
                'avg_response_time': 0.0,
                'last_used': 0.0
            }
    
    def get_proxy_pool(self) -> List[str]:
        """Get current proxy pool as URL strings"""
        return [self._proxy_to_url(proxy) for proxy in self.proxy_pool]
    
    def get_proxy_by_tier(self, tier: str) -> Optional[str]:
        """Get proxy from specific tier"""
        tier_proxies = [p for p in self.proxy_pool if p.tier == tier and p.ip not in self.failed_proxies]
        
        if not tier_proxies:
            return None
        
        proxy = random.choice(tier_proxies)
        return self._proxy_to_url(proxy)
    
    def get_healthy_proxy(self, preferred_tier: str = None) -> Optional[str]:
        """Get a healthy proxy from the pool"""
        # Filter out failed proxies
        available_proxies = [
            p for p in self.proxy_pool 
            if p.ip not in self.failed_proxies
        ]
        
        # Filter by preferred tier if specified
        if preferred_tier:
            available_proxies = [p for p in available_proxies if p.tier == preferred_tier]
        
        if not available_proxies:
            # Reset failed proxies if all are marked as failed
            self.failed_proxies.clear()
            available_proxies = self.proxy_pool
        
        # Select proxy with best success rate
        best_proxy = max(available_proxies, key=lambda p: p.success_rate)
        return self._proxy_to_url(best_proxy)
    
    def report_proxy_success(self, proxy_url: str, response_time: float = 0.0):
        """Report successful proxy usage"""
        proxy_key = self._extract_proxy_key(proxy_url)
        
        if proxy_key in self.proxy_stats:
            stats = self.proxy_stats[proxy_key]
            stats['requests'] += 1
            stats['successes'] += 1
            stats['last_used'] = time.time()
            
            # Update average response time
            if response_time > 0:
                if stats['avg_response_time'] == 0:
                    stats['avg_response_time'] = response_time
                else:
                    stats['avg_response_time'] = (stats['avg_response_time'] + response_time) / 2
        
        # Update proxy success rate
        self._update_proxy_success_rate(proxy_key)
    
    def report_proxy_failure(self, proxy_url: str):
        """Report proxy failure for health monitoring"""
        proxy_key = self._extract_proxy_key(proxy_url)
        
        if proxy_key in self.proxy_stats:
            stats = self.proxy_stats[proxy_key]
            stats['requests'] += 1
            stats['failures'] += 1
            stats['last_used'] = time.time()
        
        # Mark proxy as failed if failure rate is too high
        self._update_proxy_success_rate(proxy_key)
        
        # Add to failed proxies if success rate is too low
        proxy_info = self._get_proxy_by_key(proxy_key)
        if proxy_info and proxy_info.success_rate < 0.5:
            self.failed_proxies.add(proxy_info.ip)
    
    def get_proxy_health_score(self, proxy_url: str) -> float:
        """Get health score for proxy (0.0 to 1.0)"""
        proxy_key = self._extract_proxy_key(proxy_url)
        
        if proxy_key not in self.proxy_stats:
            return 0.0
        
        stats = self.proxy_stats[proxy_key]
        
        if stats['requests'] == 0:
            return 1.0
        
        success_rate = stats['successes'] / stats['requests']
        
        # Penalize proxies with high response times
        response_penalty = 0.0
        if stats['avg_response_time'] > 5.0:  # More than 5 seconds
            response_penalty = min(0.3, (stats['avg_response_time'] - 5.0) * 0.1)
        
        # Penalize proxies that haven't been used recently
        recency_penalty = 0.0
        if stats['last_used'] > 0:
            time_since_use = time.time() - stats['last_used']
            if time_since_use > 3600:  # More than 1 hour
                recency_penalty = min(0.2, time_since_use / 3600 * 0.1)
        
        health_score = success_rate - response_penalty - recency_penalty
        return max(0.0, min(1.0, health_score))
    
    def perform_health_check(self):
        """Perform health check on all proxies"""
        current_time = time.time()
        
        if current_time - self.last_health_check < self.health_check_interval:
            return
        
        self.last_health_check = current_time
        
        for proxy in self.proxy_pool:
            proxy_url = self._proxy_to_url(proxy)
            
            try:
                # Test proxy with a simple request
                response = requests.get(
                    'http://httpbin.org/ip',
                    proxies={'http': proxy_url, 'https': proxy_url},
                    timeout=10
                )
                
                if response.status_code == 200:
                    self.report_proxy_success(proxy_url, response.elapsed.total_seconds())
                else:
                    self.report_proxy_failure(proxy_url)
                    
            except Exception as e:
                self.report_proxy_failure(proxy_url)
    
    def get_proxy_statistics(self) -> Dict:
        """Get comprehensive proxy statistics"""
        total_requests = sum(stats['requests'] for stats in self.proxy_stats.values())
        total_successes = sum(stats['successes'] for stats in self.proxy_stats.values())
        total_failures = sum(stats['failures'] for stats in self.proxy_stats.values())
        
        overall_success_rate = total_successes / total_requests if total_requests > 0 else 0.0
        
        tier_stats = {}
        for proxy in self.proxy_pool:
            tier = proxy.tier
            if tier not in tier_stats:
                tier_stats[tier] = {'count': 0, 'success_rate': 0.0, 'avg_response_time': 0.0}
            
            tier_stats[tier]['count'] += 1
            tier_stats[tier]['success_rate'] += proxy.success_rate
            tier_stats[tier]['avg_response_time'] += self.proxy_stats.get(f"{proxy.ip}:{proxy.port}", {}).get('avg_response_time', 0.0)
        
        # Calculate averages
        for tier in tier_stats:
            count = tier_stats[tier]['count']
            if count > 0:
                tier_stats[tier]['success_rate'] /= count
                tier_stats[tier]['avg_response_time'] /= count
        
        return {
            'total_proxies': len(self.proxy_pool),
            'failed_proxies': len(self.failed_proxies),
            'total_requests': total_requests,
            'total_successes': total_successes,
            'total_failures': total_failures,
            'overall_success_rate': overall_success_rate,
            'tier_statistics': tier_stats,
            'last_health_check': self.last_health_check
        }
    
    def _proxy_to_url(self, proxy: ProxyInfo) -> str:
        """Convert ProxyInfo to URL string"""
        return f"http://{proxy.username}:{proxy.password}@{proxy.ip}:{proxy.port}"
    
    def _extract_proxy_key(self, proxy_url: str) -> str:
        """Extract proxy key from URL"""
        # Extract IP:port from proxy URL
        # Format: http://user:pass@ip:port
        try:
            parts = proxy_url.split('@')[1]  # Get ip:port part
            return parts
        except IndexError:
            return proxy_url
    
    def _get_proxy_by_key(self, proxy_key: str) -> Optional[ProxyInfo]:
        """Get ProxyInfo by proxy key"""
        for proxy in self.proxy_pool:
            if f"{proxy.ip}:{proxy.port}" == proxy_key:
                return proxy
        return None
    
    def _update_proxy_success_rate(self, proxy_key: str):
        """Update proxy success rate"""
        proxy_info = self._get_proxy_by_key(proxy_key)
        if not proxy_info:
            return
        
        stats = self.proxy_stats.get(proxy_key, {})
        if stats.get('requests', 0) > 0:
            proxy_info.success_rate = stats['successes'] / stats['requests']
        else:
            proxy_info.success_rate = 1.0
