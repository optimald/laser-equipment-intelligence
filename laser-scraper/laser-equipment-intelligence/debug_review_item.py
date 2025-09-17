#!/usr/bin/env python3
"""
Debug script for REVIEW item scoring
"""

import sys
import time
sys.path.insert(0, 'src')

from laser_intelligence.pipelines.scoring import ScoringPipeline
from laser_intelligence.pipelines.normalization import LaserListingItem
from unittest.mock import Mock

def debug_review_item():
    """Debug the REVIEW item scoring"""
    pipeline = ScoringPipeline()
    spider = Mock()
    spider.logger = Mock()
    
    item = LaserListingItem()
    item['brand'] = 'Cynosure'
    item['model'] = 'Picosure'
    item['asking_price'] = 15000  # Lower asking price for better margin
    item['condition'] = 'good'
    item['auction_end_ts'] = time.time() + 1800  # 30 minutes from now
    item['hours'] = 500  # Low usage for bonus
    item['seller_name'] = 'Equipment Dealer'
    
    print("Item data:")
    print(f"Brand: {item['brand']}")
    print(f"Model: {item['model']}")
    print(f"Asking price: {item['asking_price']}")
    print(f"Condition: {item['condition']}")
    print(f"Auction end: {item['auction_end_ts']}")
    
    # Test individual scores
    margin_score = pipeline._calculate_margin_score(item)
    urgency_score = pipeline._calculate_urgency_score(item)
    condition_score = pipeline._calculate_condition_score(item)
    reputation_score = pipeline._calculate_reputation_score(item)
    
    print(f"\nIndividual scores:")
    print(f"Margin score: {margin_score}")
    print(f"Urgency score: {urgency_score}")
    print(f"Condition score: {condition_score}")
    print(f"Reputation score: {reputation_score}")
    
    # Calculate overall score
    overall_score = pipeline._calculate_overall_score(item)
    print(f"Overall score: {overall_score}")
    
    # Get qualification level
    qualification_level = pipeline._get_qualification_level(overall_score)
    print(f"Qualification level: {qualification_level}")
    
    # Test margin estimates
    pipeline._calculate_margin_estimates(item)
    print(f"\nMargin estimates:")
    print(f"Wholesale estimate: {item.get('est_wholesale')}")
    print(f"Resale estimate: {item.get('est_resale')}")
    print(f"Refurb cost: {item.get('refurb_cost_estimate')}")
    print(f"Freight cost: {item.get('freight_estimate')}")
    print(f"Margin estimate: {item.get('margin_estimate')}")
    print(f"Margin %: {item.get('margin_pct')}")

if __name__ == '__main__':
    debug_review_item()
