"""
Price analysis utility for laser equipment intelligence platform
"""

import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from laser_intelligence.utils.brand_mapping import BrandMapper


@dataclass
class PriceComparison:
    """Price comparison data"""
    brand: str
    model: str
    condition: str
    sold_price: float
    sold_date: str
    source: str
    url: str
    location: str


class PriceAnalyzer:
    """Analyze and compare laser equipment prices"""
    
    def __init__(self):
        self.brand_mapper = BrandMapper()
        self.price_comps: List[PriceComparison] = []
        self.market_trends: Dict[str, Dict] = {}
        
    def estimate_wholesale_value(self, brand: str, model: str, condition: str, asking_price: float) -> Optional[float]:
        """Estimate wholesale value based on historical data"""
        try:
            normalized_brand = self.brand_mapper.normalize_brand(brand)
            normalized_model = self.brand_mapper.normalize_model(model, brand)
            
            # Get recent comparable sales
            comps = self._get_comparable_sales(normalized_brand, normalized_model, condition)
            
            if not comps:
                # Fallback to heuristic estimation
                return self._heuristic_wholesale_estimate(normalized_brand, asking_price)
            
            # Calculate average wholesale value from comps
            wholesale_prices = [comp.sold_price * 0.7 for comp in comps]  # Assume 70% of sold price
            avg_wholesale = sum(wholesale_prices) / len(wholesale_prices)
            
            # Apply condition multiplier
            condition_multiplier = self._get_condition_multiplier(condition)
            estimated_wholesale = avg_wholesale * condition_multiplier
            
            return round(estimated_wholesale, 2)
            
        except Exception as e:
            print(f'Error estimating wholesale value: {e}')
            return None
    
    def estimate_resale_value(self, brand: str, model: str, condition: str, asking_price: float) -> Optional[float]:
        """Estimate resale value based on market data"""
        try:
            normalized_brand = self.brand_mapper.normalize_brand(brand)
            normalized_model = self.brand_mapper.normalize_model(model, brand)
            
            # Get recent comparable sales
            comps = self._get_comparable_sales(normalized_brand, normalized_model, condition)
            
            if not comps:
                # Fallback to heuristic estimation
                return self._heuristic_resale_estimate(normalized_brand, asking_price)
            
            # Calculate average resale value from comps
            resale_prices = [comp.sold_price for comp in comps]
            avg_resale = sum(resale_prices) / len(resale_prices)
            
            # Apply condition multiplier
            condition_multiplier = self._get_condition_multiplier(condition)
            estimated_resale = avg_resale * condition_multiplier
            
            # Apply market trend adjustment
            trend_multiplier = self._get_market_trend_multiplier(normalized_brand, normalized_model)
            estimated_resale *= trend_multiplier
            
            return round(estimated_resale, 2)
            
        except Exception as e:
            print(f'Error estimating resale value: {e}')
            return None
    
    def calculate_margin_estimate(self, asking_price: float, wholesale_value: float, 
                                 refurb_cost: float = 0, freight_cost: float = 0) -> Tuple[float, float]:
        """Calculate margin estimate and percentage"""
        try:
            # Margin = wholesale_value - (asking_price + refurb_cost + freight_cost)
            # This represents profit when buying at asking_price and selling at wholesale_value
            total_cost = asking_price + refurb_cost + freight_cost
            margin_estimate = wholesale_value - total_cost
            margin_pct = (margin_estimate / total_cost) * 100 if total_cost > 0 else 0
            
            return round(margin_estimate, 2), round(margin_pct, 1)
            
        except Exception as e:
            print(f'Error calculating margin: {e}')
            return 0.0, 0.0
    
    def add_price_comparison(self, brand: str, model: str, condition: str, 
                           sold_price: float, sold_date: str, source: str, 
                           url: str, location: str = ""):
        """Add new price comparison data"""
        try:
            normalized_brand = self.brand_mapper.normalize_brand(brand)
            normalized_model = self.brand_mapper.normalize_model(model, brand)
            
            comp = PriceComparison(
                brand=normalized_brand,
                model=normalized_model,
                condition=condition,
                sold_price=sold_price,
                sold_date=sold_date,
                source=source,
                url=url,
                location=location
            )
            
            self.price_comps.append(comp)
            
            # Update market trends
            self._update_market_trends(comp)
            
        except Exception as e:
            print(f'Error adding price comparison: {e}')
    
    def get_market_trends(self, brand: str, model: str = None) -> Dict[str, Any]:
        """Get market trends for brand/model"""
        try:
            normalized_brand = self.brand_mapper.normalize_brand(brand)
            normalized_model = self.brand_mapper.normalize_model(model, brand) if model else None
            
            key = f"{normalized_brand}_{normalized_model}" if normalized_model else normalized_brand
            
            return self.market_trends.get(key, {
                'avg_price': 0.0,
                'price_trend': 'stable',
                'volume_trend': 'stable',
                'last_updated': time.time()
            })
            
        except Exception as e:
            print(f'Error getting market trends: {e}')
            return {}
    
    def _get_comparable_sales(self, brand: str, model: str, condition: str) -> List[PriceComparison]:
        """Get comparable sales for brand/model/condition"""
        try:
            # Filter comps by brand and model
            brand_model_comps = [
                comp for comp in self.price_comps
                if comp.brand.lower() == brand.lower() and comp.model.lower() == model.lower()
            ]
            
            if not brand_model_comps:
                # Try just brand if no exact model match
                brand_comps = [
                    comp for comp in self.price_comps
                    if comp.brand.lower() == brand.lower()
                ]
                return brand_comps
            
            # Filter by condition if specified
            if condition and condition != 'any':
                condition_comps = [
                    comp for comp in brand_model_comps
                    if comp.condition.lower() == condition.lower()
                ]
                if condition_comps:
                    return condition_comps
            
            # Return recent sales (last 6 months)
            recent_comps = [
                comp for comp in brand_model_comps
                if self._is_recent_sale(comp.sold_date)
            ]
            
            return recent_comps if recent_comps else brand_model_comps
            
        except Exception as e:
            print(f'Error getting comparable sales: {e}')
            return []
    
    def _heuristic_wholesale_estimate(self, brand: str, asking_price: float) -> float:
        """Heuristic wholesale value estimation"""
        # High-value brands typically have higher wholesale values
        high_value_brands = ['sciton', 'cynosure', 'cutera', 'candela', 'lumenis']
        
        if any(brand_name in brand.lower() for brand_name in high_value_brands):
            # For high-value brands, assume wholesale is 120-150% of asking price
            # This represents the true market value vs. discounted asking price
            return asking_price * 1.35
        else:
            # Estimate 80-100% of asking price for other brands
            return asking_price * 0.9
    
    def _heuristic_resale_estimate(self, brand: str, asking_price: float) -> float:
        """Heuristic resale value estimation"""
        # High-value brands typically have higher resale values
        high_value_brands = ['sciton', 'cynosure', 'cutera', 'candela', 'lumenis']
        
        if any(brand_name in brand.lower() for brand_name in high_value_brands):
            # Estimate 150-200% of asking price for high-value brands (resale > wholesale)
            return asking_price * 1.75
        else:
            # Estimate 130-160% of asking price for other brands
            return asking_price * 1.45
    
    def _get_condition_multiplier(self, condition: str) -> float:
        """Get condition multiplier for price estimation"""
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
        
        return condition_multipliers.get(condition.lower(), 0.7)
    
    def _get_market_trend_multiplier(self, brand: str, model: str) -> float:
        """Get market trend multiplier"""
        trends = self.get_market_trends(brand, model)
        
        trend_multipliers = {
            'rising': 1.1,
            'stable': 1.0,
            'falling': 0.9,
        }
        
        price_trend = trends.get('price_trend', 'stable')
        return trend_multipliers.get(price_trend, 1.0)
    
    def _is_recent_sale(self, sold_date: str) -> bool:
        """Check if sale is recent (within last 6 months)"""
        try:
            # Parse date string (assuming YYYY-MM-DD format)
            from datetime import datetime, timedelta
            
            sale_date = datetime.strptime(sold_date, '%Y-%m-%d')
            six_months_ago = datetime.now() - timedelta(days=180)
            
            return sale_date >= six_months_ago
            
        except Exception:
            return True  # Assume recent if can't parse date
    
    def _update_market_trends(self, comp: PriceComparison):
        """Update market trends based on new comparison data"""
        try:
            key = f"{comp.brand}_{comp.model}"
            
            if key not in self.market_trends:
                self.market_trends[key] = {
                    'prices': [],
                    'dates': [],
                    'avg_price': 0.0,
                    'price_trend': 'stable',
                    'volume_trend': 'stable',
                    'last_updated': time.time()
                }
            
            trends = self.market_trends[key]
            trends['prices'].append(comp.sold_price)
            trends['dates'].append(comp.sold_date)
            
            # Keep only last 12 months of data
            if len(trends['prices']) > 50:
                trends['prices'] = trends['prices'][-50:]
                trends['dates'] = trends['dates'][-50:]
            
            # Calculate average price
            if trends['prices']:
                trends['avg_price'] = sum(trends['prices']) / len(trends['prices'])
            
            # Calculate price trend
            if len(trends['prices']) >= 3:
                recent_avg = sum(trends['prices'][-3:]) / 3
                older_avg = sum(trends['prices'][-6:-3]) / 3 if len(trends['prices']) >= 6 else trends['avg_price']
                
                if recent_avg > older_avg * 1.05:
                    trends['price_trend'] = 'rising'
                elif recent_avg < older_avg * 0.95:
                    trends['price_trend'] = 'falling'
                else:
                    trends['price_trend'] = 'stable'
            
            trends['last_updated'] = time.time()
            
        except Exception as e:
            print(f'Error updating market trends: {e}')
    
    def get_price_statistics(self) -> Dict[str, Any]:
        """Get comprehensive price analysis statistics"""
        try:
            total_comps = len(self.price_comps)
            
            if total_comps == 0:
                return {
                    'total_comparisons': 0,
                    'avg_price': 0.0,
                    'price_range': {'min': 0.0, 'max': 0.0},
                    'brands_covered': 0,
                    'models_covered': 0,
                    'sources_covered': 0
                }
            
            prices = [comp.sold_price for comp in self.price_comps]
            brands = set(comp.brand for comp in self.price_comps)
            models = set(comp.model for comp in self.price_comps)
            sources = set(comp.source for comp in self.price_comps)
            
            return {
                'total_comparisons': total_comps,
                'avg_price': sum(prices) / len(prices),
                'price_range': {'min': min(prices), 'max': max(prices)},
                'brands_covered': len(brands),
                'models_covered': len(models),
                'sources_covered': len(sources),
                'market_trends_count': len(self.market_trends)
            }
            
        except Exception as e:
            print(f'Error getting price statistics: {e}')
            return {}
