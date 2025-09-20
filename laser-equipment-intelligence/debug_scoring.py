#!/usr/bin/env python3
"""
Debug script for scoring pipeline
"""

import sys
sys.path.insert(0, 'src')

from laser_intelligence.pipelines.scoring import ScoringPipeline
from laser_intelligence.pipelines.normalization import LaserListingItem
from unittest.mock import Mock

def debug_scoring():
    """Debug the scoring pipeline"""
    pipeline = ScoringPipeline()
    spider = Mock()
    spider.logger = Mock()
    
    item = LaserListingItem()
    item['brand'] = 'Sciton'
    item['model'] = 'Joule'
    item['asking_price'] = 50000
    item['condition'] = 'excellent'
    item['auction_end_ts'] = 1234567890
    item['seller_name'] = 'Medical Equipment Liquidators'
    
    print("Before processing:")
    print(f"Item keys: {list(item.keys())}")
    print(f"Score overall: {item.get('score_overall', 'NOT SET')}")
    print(f"Qualification level: {item.get('qualification_level', 'NOT SET')}")
    
    try:
        print("Calling process_item...")
        processed_item = pipeline.process_item(item, spider)
        print("process_item completed successfully")
    except Exception as e:
        print(f"Exception in process_item: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\nAfter processing:")
    print(f"Item keys: {list(processed_item.keys())}")
    print(f"Score overall: {processed_item.get('score_overall', 'NOT SET')}")
    print(f"Qualification level: {processed_item.get('qualification_level', 'NOT SET')}")
    print(f"Scored count: {pipeline.scored_count}")
    
    # Check if the original item was modified
    print(f"\nOriginal item keys: {list(item.keys())}")
    print(f"Original item qualification_level: {item.get('qualification_level', 'NOT SET')}")
    print(f"Are they the same object? {item is processed_item}")
    
    # Test individual methods
    print("\nIndividual method tests:")
    margin_score = pipeline._calculate_margin_score(item)
    urgency_score = pipeline._calculate_urgency_score(item)
    condition_score = pipeline._calculate_condition_score(item)
    reputation_score = pipeline._calculate_reputation_score(item)
    overall_score = pipeline._calculate_overall_score(item)
    qualification_level = pipeline._get_qualification_level(overall_score)
    
    print(f"Margin score: {margin_score}")
    print(f"Urgency score: {urgency_score}")
    print(f"Condition score: {condition_score}")
    print(f"Reputation score: {reputation_score}")
    print(f"Overall score: {overall_score}")
    print(f"Qualification level: {qualification_level}")

if __name__ == '__main__':
    debug_scoring()
