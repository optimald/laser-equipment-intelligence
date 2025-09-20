#!/usr/bin/env python3
"""
Debug script for simple scoring pipeline test
"""

import sys
sys.path.insert(0, 'src')

from laser_intelligence.pipelines.scoring import ScoringPipeline
from laser_intelligence.pipelines.normalization import LaserListingItem
from unittest.mock import Mock

def debug_simple_scoring():
    """Debug the simple scoring test"""
    pipeline = ScoringPipeline()
    spider = Mock()
    spider.logger = Mock()
    
    item = LaserListingItem()
    item['score_overall'] = 75  # HOT threshold
    
    print("Before processing:")
    print(f"Score overall: {item.get('score_overall', 'NOT SET')}")
    
    processed_item = pipeline.process_item(item, spider)
    
    print("\nAfter processing:")
    print(f"Score overall: {processed_item.get('score_overall', 'NOT SET')}")
    print(f"Qualification level: {processed_item.get('qualification_level', 'NOT SET')}")
    print(f"Scored count: {pipeline.scored_count}")
    print(f"Hot items: {pipeline.hot_items}")
    print(f"Review items: {pipeline.review_items}")
    print(f"Archive items: {pipeline.archive_items}")
    
    # Test individual scores for empty item
    print("\nIndividual scores for empty item:")
    margin_score = pipeline._calculate_margin_score(item)
    urgency_score = pipeline._calculate_urgency_score(item)
    condition_score = pipeline._calculate_condition_score(item)
    reputation_score = pipeline._calculate_reputation_score(item)
    overall_score = pipeline._calculate_overall_score(item)
    
    print(f"Margin score: {margin_score}")
    print(f"Urgency score: {urgency_score}")
    print(f"Condition score: {condition_score}")
    print(f"Reputation score: {reputation_score}")
    print(f"Overall score: {overall_score}")

if __name__ == '__main__':
    debug_simple_scoring()
