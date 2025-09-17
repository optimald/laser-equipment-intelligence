"""
Scoring and qualification pipeline for laser equipment opportunities
"""

import time
from typing import Dict, Any, Optional
from laser_intelligence.pipelines.normalization import LaserListingItem


class ScoringPipeline:
    """Score and qualify laser equipment opportunities"""
    
    def __init__(self):
        self.scored_count = 0
        self.hot_items = 0
        self.review_items = 0
        self.archive_items = 0
        
    def process_item(self, item: LaserListingItem, spider) -> LaserListingItem:
        """Score and qualify item"""
        try:
            # Calculate individual scores
            item['score_margin'] = self._calculate_margin_score(item)
            item['score_urgency'] = self._calculate_urgency_score(item)
            item['score_condition'] = self._calculate_condition_score(item)
            item['score_reputation'] = self._calculate_reputation_score(item)
            
            # Calculate overall score
            item['score_overall'] = self._calculate_overall_score(item)
            
            # Calculate margin estimates
            self._calculate_margin_estimates(item)
            
            # Set qualification level
            item['qualification_level'] = self._get_qualification_level(item['score_overall'])
            
            self.scored_count += 1
            
            # Track statistics
            if item['qualification_level'] == 'HOT':
                self.hot_items += 1
            elif item['qualification_level'] == 'REVIEW':
                self.review_items += 1
            else:
                self.archive_items += 1
            
            spider.logger.info(f'Scored item {self.scored_count}: {item.get("brand")} {item.get("model")} - Score: {item["score_overall"]:.1f}')
            
            return item
            
        except Exception as e:
            spider.logger.error(f'Error scoring item: {e}')
            return item
    
    def _calculate_margin_score(self, item: LaserListingItem) -> float:
        """Calculate margin-based score (0-60 points)"""
        asking_price = item.get('asking_price')
        if not asking_price or asking_price <= 0:
            return 0
        
        # Estimate wholesale and resale values
        est_wholesale = self._estimate_wholesale_value(item)
        est_resale = self._estimate_resale_value(item)
        refurb_cost = self._estimate_refurb_cost(item)
        freight_cost = self._estimate_freight_cost(item)
        
        if not est_wholesale or not est_resale:
            return 0
        
        # Calculate total cost (consistent with margin estimates)
        total_cost = asking_price + (refurb_cost or 0) + (freight_cost or 0)
        margin_estimate = est_resale - total_cost
        
        # Calculate margin percentage
        margin_pct = margin_estimate / est_resale if est_resale > 0 else 0
        
        # Score based on margin percentage (target: 40%+ for full score)
        if margin_pct >= 0.8:
            return 100.0  # Excellent margin (80%+)
        elif margin_pct >= 0.6:
            return 80.0 + (margin_pct - 0.6) * 100  # Scale 60-80% to 80-100 points
        elif margin_pct >= 0.4:
            return 60.0 + (margin_pct - 0.4) * 100  # Scale 40-60% to 60-80 points
        elif margin_pct >= 0.2:
            return 30.0 + (margin_pct - 0.2) * 150  # Scale 20-40% to 30-60 points
        elif margin_pct >= 0.1:
            return 15.0 + (margin_pct - 0.1) * 150  # Scale 10-20% to 15-30 points
        else:
            return max(0, margin_pct * 150)  # Scale 0-10% to 0-15 points
    
    def _calculate_urgency_score(self, item: LaserListingItem) -> float:
        """Calculate urgency score (0-25 points)"""
        score = 0
        
        # Auction ending soon (0-15 points)
        auction_end = item.get('auction_end_ts')
        if auction_end:
            time_remaining = auction_end - time.time()
            if time_remaining < 24 * 3600:  # Less than 24 hours
                score += 15
            elif time_remaining < 72 * 3600:  # Less than 72 hours
                score += 10
            elif time_remaining < 168 * 3600:  # Less than 1 week
                score += 5
        
        # High-value brand bonus (0-5 points)
        if self._is_high_value_brand(item.get('brand')):
            score += 5
        
        # Low usage bonus (0-5 points)
        hours = item.get('hours')
        if hours and hours < 1000:
            score += 5
        
        return min(25, score)
    
    def _calculate_condition_score(self, item: LaserListingItem) -> float:
        """Calculate condition score (0-100 points)"""
        condition_mapping = {
            'new': 100,
            'excellent': 90,
            'good': 70,
            'fair': 50,
            'poor': 30,
            'used': 60,
            'refurbished': 80,
            'as-is': 20,
            'unknown': 50,
        }
        
        condition = item.get('condition', 'unknown')
        return condition_mapping.get(condition, 50)
    
    def _calculate_reputation_score(self, item: LaserListingItem) -> float:
        """Calculate seller reputation score (0-100 points)"""
        # TODO: Implement seller reputation tracking
        # For now, return neutral score
        return 25.0
    
    def _calculate_overall_score(self, item: LaserListingItem) -> float:
        """Calculate weighted overall score"""
        # Get scores from item if they exist, otherwise calculate them
        margin_score = item.get('score_margin', self._calculate_margin_score(item))
        urgency_score = item.get('score_urgency', self._calculate_urgency_score(item))
        condition_score = item.get('score_condition', self._calculate_condition_score(item))
        reputation_score = item.get('score_reputation', self._calculate_reputation_score(item))
        
        # Weighted combination
        overall_score = (
            margin_score * 0.4 +      # 40% weight on margin
            urgency_score * 0.3 +      # 30% weight on urgency
            condition_score * 0.2 +    # 20% weight on condition
            reputation_score * 0.1     # 10% weight on reputation
        )
        
        return round(overall_score, 1)
    
    def _calculate_margin_estimates(self, item: LaserListingItem):
        """Calculate margin estimates for item"""
        asking_price = item.get('asking_price', 0)
        
        # Estimate wholesale value
        est_wholesale = self._estimate_wholesale_value(item)
        item['est_wholesale'] = est_wholesale
        
        # Estimate resale value
        est_resale = self._estimate_resale_value(item)
        item['est_resale'] = est_resale
        
        # Estimate refurbishment cost
        refurb_cost = self._estimate_refurb_cost(item)
        item['refurb_cost_estimate'] = refurb_cost
        
        # Estimate freight cost
        freight_cost = self._estimate_freight_cost(item)
        item['freight_estimate'] = freight_cost
        
        # Calculate margin
        if est_wholesale and est_resale and asking_price:
            total_cost = asking_price + (refurb_cost or 0) + (freight_cost or 0)
            margin_estimate = est_resale - total_cost
            margin_pct = (margin_estimate / est_resale) * 100 if est_resale > 0 else 0
            
            item['margin_estimate'] = margin_estimate
            item['margin_pct'] = round(margin_pct, 1)
    
    def _estimate_wholesale_value(self, item: LaserListingItem) -> Optional[float]:
        """Estimate wholesale value based on brand/model/condition"""
        # TODO: Implement comprehensive price analysis
        # For now, use simple heuristics
        
        brand = item.get('brand', '').lower()
        model = item.get('model', '').lower()
        condition = item.get('condition', 'unknown')
        asking_price = item.get('asking_price', 0)
        
        # High-value brands typically have higher wholesale values
        high_value_brands = ['sciton', 'cynosure', 'cutera', 'candela', 'lumenis']
        
        if any(brand_name in brand for brand_name in high_value_brands):
            # For high-value brands, use fixed ranges based on typical market values
            if 'sciton' in brand and 'joule' in model:
                return 35000  # Typical wholesale value for Sciton Joule
            elif 'cynosure' in brand and 'picosure' in model:
                return 25000  # Typical wholesale value for Cynosure Picosure
            else:
                return asking_price * 0.8  # 80% of asking price for other high-value brands
        else:
            # Estimate 50-70% of asking price for other brands
            return asking_price * 0.6
    
    def _estimate_resale_value(self, item: LaserListingItem) -> Optional[float]:
        """Estimate resale value based on market data"""
        # TODO: Implement comprehensive market analysis
        # For now, use simple heuristics
        
        brand = item.get('brand', '').lower()
        model = item.get('model', '').lower()
        condition = item.get('condition', 'unknown')
        asking_price = item.get('asking_price', 0)
        
        # Condition multipliers
        condition_multipliers = {
            'new': 1.0,
            'excellent': 0.9,
            'good': 0.8,
            'fair': 0.7,
            'poor': 0.6,
            'used': 0.75,
            'refurbished': 0.85,
            'as-is': 0.5,
            'unknown': 0.7,
        }
        
        multiplier = condition_multipliers.get(condition, 0.7)
        
        # High-value brands typically have higher resale values
        high_value_brands = ['sciton', 'cynosure', 'cutera', 'candela', 'lumenis']
        
        if any(brand_name in brand for brand_name in high_value_brands):
            # For high-value brands, use fixed ranges based on typical market values
            if 'sciton' in brand and 'joule' in model:
                return 60000 * multiplier  # Typical resale value for Sciton Joule
            elif 'cynosure' in brand and 'picosure' in model:
                return 45000 * multiplier  # Typical resale value for Cynosure Picosure
            else:
                return asking_price * 1.35 * multiplier  # 135% of asking price for other high-value brands
        else:
            # Estimate 100-130% of asking price for other brands
            return asking_price * 1.15 * multiplier
    
    def _estimate_refurb_cost(self, item: LaserListingItem) -> Optional[float]:
        """Estimate refurbishment cost"""
        condition = item.get('condition', 'unknown')
        asking_price = item.get('asking_price', 0)
        
        # Refurbishment cost as percentage of asking price
        refurb_percentages = {
            'new': 0.0,
            'excellent': 0.05,
            'good': 0.1,
            'fair': 0.2,
            'poor': 0.4,
            'used': 0.15,
            'refurbished': 0.0,
            'as-is': 0.5,
            'unknown': 0.2,
        }
        
        percentage = refurb_percentages.get(condition, 0.2)
        return asking_price * percentage
    
    def _estimate_freight_cost(self, item: LaserListingItem) -> Optional[float]:
        """Estimate freight/shipping cost"""
        # TODO: Implement location-based freight calculation
        # For now, use fixed estimate based on equipment type
        
        brand = item.get('brand', '').lower()
        
        # High-value equipment typically costs more to ship
        high_value_brands = ['sciton', 'cynosure', 'cutera', 'candela', 'lumenis']
        
        if any(brand_name in brand for brand_name in high_value_brands):
            return 2000  # $2000 for high-value equipment
        else:
            return 1000  # $1000 for other equipment
    
    def _is_high_value_brand(self, brand: str) -> bool:
        """Check if brand is considered high-value"""
        if not brand:
            return False
        
        high_value_brands = [
            'sciton', 'cynosure', 'cutera', 'candela', 'lumenis',
            'alma', 'inmode', 'btl', 'lutronic'
        ]
        
        return brand.lower() in high_value_brands
    
    def _get_qualification_level(self, overall_score: float) -> str:
        """Get qualification level based on overall score"""
        if overall_score >= 70:
            return 'HOT'
        elif overall_score >= 50:
            return 'REVIEW'
        else:
            return 'ARCHIVE'
    
    def close_spider(self, spider):
        """Called when spider closes"""
        spider.logger.info(f'ScoringPipeline statistics:')
        spider.logger.info(f'  Total scored: {self.scored_count}')
        spider.logger.info(f'  HOT items: {self.hot_items}')
        spider.logger.info(f'  REVIEW items: {self.review_items}')
        spider.logger.info(f'  ARCHIVE items: {self.archive_items}')
