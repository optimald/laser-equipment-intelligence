"""
Source tracking system with evasion levels and performance monitoring
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class SourceMetrics:
    """Track performance metrics for each source"""
    source_name: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    items_found: int = 0
    last_success: Optional[str] = None
    last_failure: Optional[str] = None
    average_response_time: float = 0.0
    evasion_level: int = 1  # 1=low, 2=medium, 3=high
    block_count: int = 0
    success_rate: float = 0.0
    
    def update_success(self, response_time: float, items_count: int = 0):
        """Update metrics for successful request"""
        self.total_requests += 1
        self.successful_requests += 1
        self.items_found += items_count
        self.last_success = datetime.now().isoformat()
        
        # Update average response time
        if self.average_response_time == 0:
            self.average_response_time = response_time
        else:
            self.average_response_time = (self.average_response_time + response_time) / 2
        
        self.success_rate = self.successful_requests / self.total_requests
    
    def update_failure(self, response_time: float = 0.0):
        """Update metrics for failed request"""
        self.total_requests += 1
        self.failed_requests += 1
        self.last_failure = datetime.now().isoformat()
        
        if self.total_requests > 0:
            self.success_rate = self.successful_requests / self.total_requests
    
    def update_block(self):
        """Update metrics for blocked request"""
        self.block_count += 1
        self.evasion_level = min(3, self.evasion_level + 1)  # Increase evasion level
    
    def get_evasion_strategy(self) -> Dict[str, Any]:
        """Get evasion strategy based on current level"""
        strategies = {
            1: {  # Low evasion
                "delay_range": (1, 3),
                "user_agents": ["Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"],
                "headers": {"Accept": "text/html,application/xhtml+xml"},
                "proxy_required": False
            },
            2: {  # Medium evasion
                "delay_range": (3, 8),
                "user_agents": [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
                ],
                "headers": {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1"
                },
                "proxy_required": True
            },
            3: {  # High evasion
                "delay_range": (8, 15),
                "user_agents": [
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0"
                ],
                "headers": {
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "DNT": "1",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                    "Sec-Fetch-Dest": "document",
                    "Sec-Fetch-Mode": "navigate",
                    "Sec-Fetch-Site": "none",
                    "Cache-Control": "max-age=0"
                },
                "proxy_required": True,
                "randomize_session": True
            }
        }
        return strategies.get(self.evasion_level, strategies[1])


class SourceTracker:
    """Track and manage source performance and evasion levels"""
    
    def __init__(self, metrics_file: str = "source_metrics.json"):
        self.metrics_file = metrics_file
        self.metrics: Dict[str, SourceMetrics] = {}
        self.load_metrics()
    
    def load_metrics(self):
        """Load metrics from file"""
        try:
            with open(self.metrics_file, 'r') as f:
                data = json.load(f)
                for source_name, metrics_data in data.items():
                    self.metrics[source_name] = SourceMetrics(**metrics_data)
        except (FileNotFoundError, json.JSONDecodeError):
            # Initialize with default sources
            self.initialize_default_sources()
    
    def save_metrics(self):
        """Save metrics to file"""
        data = {name: asdict(metrics) for name, metrics in self.metrics.items()}
        with open(self.metrics_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def initialize_default_sources(self):
        """Initialize metrics for known sources"""
        sources = {
            "eBay": {"evasion_level": 3, "block_count": 0},  # High evasion needed
            "BidSpotter": {"evasion_level": 2, "block_count": 0},
            "DOTmed": {"evasion_level": 1, "block_count": 0},
            "GovDeals": {"evasion_level": 1, "block_count": 0},
            "Proxibid": {"evasion_level": 2, "block_count": 0},
            "LabX": {"evasion_level": 1, "block_count": 0},
            "Facebook Marketplace": {"evasion_level": 3, "block_count": 0},
            "Craigslist": {"evasion_level": 3, "block_count": 0},
        }
        
        for source_name, config in sources.items():
            self.metrics[source_name] = SourceMetrics(
                source_name=source_name,
                evasion_level=config["evasion_level"],
                block_count=config["block_count"]
            )
    
    def get_source_metrics(self, source_name: str) -> SourceMetrics:
        """Get metrics for a source, create if doesn't exist"""
        if source_name not in self.metrics:
            self.metrics[source_name] = SourceMetrics(source_name=source_name)
        return self.metrics[source_name]
    
    def record_success(self, source_name: str, response_time: float, items_count: int = 0):
        """Record successful request"""
        metrics = self.get_source_metrics(source_name)
        metrics.update_success(response_time, items_count)
        self.save_metrics()
    
    def record_failure(self, source_name: str, response_time: float = 0.0):
        """Record failed request"""
        metrics = self.get_source_metrics(source_name)
        metrics.update_failure(response_time)
        self.save_metrics()
    
    def record_block(self, source_name: str):
        """Record blocked request"""
        metrics = self.get_source_metrics(source_name)
        metrics.update_block()
        self.save_metrics()
    
    def get_evasion_strategy(self, source_name: str) -> Dict[str, Any]:
        """Get evasion strategy for source"""
        metrics = self.get_source_metrics(source_name)
        return metrics.get_evasion_strategy()
    
    def get_source_ranking(self) -> List[Dict[str, Any]]:
        """Get sources ranked by performance"""
        ranking = []
        for metrics in self.metrics.values():
            if metrics.total_requests > 0:
                ranking.append({
                    "source": metrics.source_name,
                    "success_rate": metrics.success_rate,
                    "items_found": metrics.items_found,
                    "evasion_level": metrics.evasion_level,
                    "block_count": metrics.block_count,
                    "average_response_time": metrics.average_response_time
                })
        
        # Sort by success rate, then by items found
        ranking.sort(key=lambda x: (x["success_rate"], x["items_found"]), reverse=True)
        return ranking
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get overall performance summary"""
        total_requests = sum(m.total_requests for m in self.metrics.values())
        total_successful = sum(m.successful_requests for m in self.metrics.values())
        total_items = sum(m.items_found for m in self.metrics.values())
        total_blocks = sum(m.block_count for m in self.metrics.values())
        
        return {
            "total_sources": len(self.metrics),
            "total_requests": total_requests,
            "total_successful": total_successful,
            "total_items_found": total_items,
            "total_blocks": total_blocks,
            "overall_success_rate": total_successful / total_requests if total_requests > 0 else 0,
            "sources_by_evasion_level": {
                "low": len([m for m in self.metrics.values() if m.evasion_level == 1]),
                "medium": len([m for m in self.metrics.values() if m.evasion_level == 2]),
                "high": len([m for m in self.metrics.values() if m.evasion_level == 3])
            }
        }


# Global instance
source_tracker = SourceTracker()
