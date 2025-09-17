"""
LLM-driven hunting system for discovering and extracting laser equipment listings
Inspired by Clay.com's approach with live internet access and adaptive extraction
"""

import json
import time
import requests
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import re
from laser_intelligence.utils.brand_mapping import BrandMapper
from laser_intelligence.utils.price_analysis import PriceAnalyzer


@dataclass
class HuntingResult:
    """Result of LLM hunting operation"""
    success: bool
    discovered_sources: List[Dict[str, Any]]
    extracted_listings: List[Dict[str, Any]]
    confidence_score: float
    processing_time: float
    error_message: Optional[str] = None


@dataclass
class SourceDiscovery:
    """Discovered source information"""
    url: str
    source_type: str  # 'auction', 'marketplace', 'dealer', 'classified'
    risk_level: str   # 'low', 'medium', 'high'
    estimated_listings: int
    last_updated: str
    extraction_method: str  # 'scraper', 'api', 'rss', 'llm'
    confidence: float


class LLMHunter:
    """LLM-driven hunting system for laser equipment discovery"""
    
    def __init__(self, api_key: str = None, api_url: str = None, provider: str = None):
        # Use multi-LLM provider manager
        from laser_intelligence.ai.llm_providers import get_llm_config, LLMProvider
        
        if provider:
            provider_enum = LLMProvider(provider)
            config = get_llm_config(provider_enum)
        else:
            config = get_llm_config(task_type='source_discovery')
        
        if config:
            self.api_key = api_key or config.api_key
            self.api_url = api_url or config.api_url
            self.model = config.model
            self.max_tokens = config.max_tokens
            self.temperature = config.temperature
            self.timeout = config.timeout
            self.provider = config.provider.value
        else:
            # Fallback to original configuration
            self.api_key = api_key or self._get_api_key()
            self.api_url = api_url or "https://api.groq.com/openai/v1/chat/completions"
            self.model = "llama-3.1-70b-versatile"
            self.max_tokens = 4000
            self.temperature = 0.1
            self.timeout = 60
            self.provider = "groq"
        
        self.brand_mapper = BrandMapper()
        self.price_analyzer = PriceAnalyzer()
        self.max_retries = 3
        self.retry_delay = 1
        
        # Laser equipment keywords for discovery
        self.laser_keywords = [
            'sciton', 'cynosure', 'cutera', 'candela', 'lumenis', 'alma',
            'inmode', 'btl', 'lutronic', 'bison', 'deka', 'quanta',
            'joule', 'picosure', 'picoway', 'gentlemax', 'm22', 'bbl',
            'secret rf', 'morpheus8', 'emsculpt', 'excel v', 'xeo',
            'laser', 'ipl', 'rf', 'hifu', 'cryolipolysis', 'coolsculpting'
        ]
        
        # Known high-value brands for targeted hunting
        self.high_value_brands = [
            'sciton', 'cynosure', 'cutera', 'candela', 'lumenis', 'alma',
            'inmode', 'btl', 'lutronic', 'bison', 'deka', 'quanta'
        ]
    
    def hunt_laser_equipment(self, 
                           search_terms: List[str] = None,
                           geographic_scope: str = "United States",
                           price_range: Tuple[float, float] = None,
                           equipment_types: List[str] = None) -> HuntingResult:
        """
        Main hunting function - discover and extract laser equipment listings
        """
        start_time = time.time()
        
        try:
            # Step 1: Discover new sources using LLM
            discovered_sources = self._discover_sources(
                search_terms or self.laser_keywords,
                geographic_scope,
                price_range,
                equipment_types
            )
            
            # Step 2: Extract listings from discovered sources
            extracted_listings = []
            for source in discovered_sources:
                listings = self._extract_from_source(source)
                extracted_listings.extend(listings)
            
            # Step 3: Score and rank results
            scored_listings = self._score_and_rank_listings(extracted_listings)
            
            processing_time = time.time() - start_time
            
            return HuntingResult(
                success=True,
                discovered_sources=discovered_sources,
                extracted_listings=scored_listings,
                confidence_score=self._calculate_overall_confidence(scored_listings),
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return HuntingResult(
                success=False,
                discovered_sources=[],
                extracted_listings=[],
                confidence_score=0.0,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    def _discover_sources(self, 
                         search_terms: List[str],
                         geographic_scope: str,
                         price_range: Tuple[float, float],
                         equipment_types: List[str]) -> List[Dict[str, Any]]:
        """Use LLM to discover new sources for laser equipment"""
        
        discovery_prompt = f"""
        You are an expert at finding laser equipment auction and marketplace websites.
        
        Search for websites that sell or auction laser equipment with these criteria:
        - Search terms: {', '.join(search_terms)}
        - Geographic scope: {geographic_scope}
        - Price range: ${price_range[0]:,} - ${price_range[1]:,} if specified
        - Equipment types: {', '.join(equipment_types) if equipment_types else 'All laser equipment'}
        
        Focus on:
        1. Auction websites (government surplus, commercial auctions)
        2. Medical equipment marketplaces
        3. Used equipment dealers
        4. Classified ad sites
        5. Equipment resale platforms
        
        For each source you find, provide:
        - URL
        - Source type (auction/marketplace/dealer/classified)
        - Risk level (low/medium/high)
        - Estimated number of listings
        - Last updated date
        - Recommended extraction method (scraper/api/rss/llm)
        - Confidence score (0-1)
        
        Return as JSON array of objects.
        """
        
        response = self._call_llm_api(discovery_prompt, "")
        sources = self._parse_llm_response(response)
        
        # Convert to SourceDiscovery objects
        discovered_sources = []
        for source_data in sources:
            if isinstance(source_data, dict) and 'url' in source_data:
                discovered_sources.append(SourceDiscovery(
                    url=source_data['url'],
                    source_type=source_data.get('source_type', 'unknown'),
                    risk_level=source_data.get('risk_level', 'medium'),
                    estimated_listings=source_data.get('estimated_listings', 0),
                    last_updated=source_data.get('last_updated', 'unknown'),
                    extraction_method=source_data.get('extraction_method', 'llm'),
                    confidence=source_data.get('confidence', 0.5)
                ))
        
        return discovered_sources
    
    def _extract_from_source(self, source: SourceDiscovery) -> List[Dict[str, Any]]:
        """Extract listings from a discovered source using LLM"""
        
        # First, try to get the page content
        try:
            response = requests.get(source.url, timeout=30)
            if response.status_code != 200:
                return []
            
            content = response.text
        except Exception:
            return []
        
        # Use LLM to extract laser equipment listings
        extraction_prompt = f"""
        Extract laser equipment listings from this webpage.
        
        Look for:
        - Equipment titles/names
        - Brand names (Sciton, Cynosure, Cutera, Candela, Lumenis, Alma, InMode, BTL, Lutronic, Bison, DEKA, Quanta)
        - Model names (Joule, PicoSure, PicoWay, GentleMax, M22, BBL, Secret RF, Morpheus8, Emsculpt, Excel V, Xeo)
        - Prices (current bid, asking price, buy-it-now)
        - Condition (new, used, excellent, good, fair, poor, refurbished)
        - Location (city, state, country)
        - Serial numbers
        - Year of manufacture
        - Usage hours
        - Accessories included
        - Auction end time (if applicable)
        - Seller information
        
        For each listing found, extract:
        - title_raw
        - description_raw
        - brand (normalized)
        - model (normalized)
        - asking_price (numeric)
        - condition
        - location_city
        - location_state
        - location_country
        - serial_number
        - year
        - hours
        - accessories (array)
        - auction_end_ts (if applicable)
        - seller_name
        - source_url
        - source_listing_id
        
        Return as JSON array of objects. Only include actual laser equipment listings.
        """
        
        response = self._call_llm_api(extraction_prompt, content)
        listings = self._parse_llm_response(response)
        
        # Add source metadata to each listing
        for listing in listings:
            if isinstance(listing, dict):
                listing['source_url'] = source.url
                listing['source_type'] = source.source_type
                listing['risk_level'] = source.risk_level
                listing['extraction_method'] = source.extraction_method
                listing['discovery_confidence'] = source.confidence
        
        return listings if isinstance(listings, list) else []
    
    def _score_and_rank_listings(self, listings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score and rank discovered listings"""
        
        scored_listings = []
        for listing in listings:
            if not isinstance(listing, dict):
                continue
                
            # Calculate various scores
            brand_score = self._calculate_brand_score(listing)
            price_score = self._calculate_price_score(listing)
            condition_score = self._calculate_condition_score(listing)
            urgency_score = self._calculate_urgency_score(listing)
            location_score = self._calculate_location_score(listing)
            
            # Calculate overall score
            overall_score = (
                brand_score * 0.3 +
                price_score * 0.25 +
                condition_score * 0.2 +
                urgency_score * 0.15 +
                location_score * 0.1
            )
            
            # Add scores to listing
            listing['brand_score'] = brand_score
            listing['price_score'] = price_score
            listing['condition_score'] = condition_score
            listing['urgency_score'] = urgency_score
            listing['location_score'] = location_score
            listing['overall_score'] = overall_score
            
            # Calculate qualification level
            if overall_score >= 70:
                listing['qualification_level'] = 'HOT'
            elif overall_score >= 50:
                listing['qualification_level'] = 'REVIEW'
            else:
                listing['qualification_level'] = 'ARCHIVE'
            
            scored_listings.append(listing)
        
        # Sort by overall score (highest first)
        scored_listings.sort(key=lambda x: x.get('overall_score', 0), reverse=True)
        
        return scored_listings
    
    def _calculate_brand_score(self, listing: Dict[str, Any]) -> float:
        """Calculate brand value score"""
        brand = listing.get('brand', '').lower()
        if not brand:
            return 0.0
        
        # High-value brands get higher scores
        if brand in self.high_value_brands:
            return 90.0
        elif any(keyword in brand for keyword in self.laser_keywords):
            return 70.0
        else:
            return 30.0
    
    def _calculate_price_score(self, listing: Dict[str, Any]) -> float:
        """Calculate price attractiveness score"""
        asking_price = listing.get('asking_price', 0)
        if not asking_price or asking_price <= 0:
            return 0.0
        
        # Estimate wholesale value for comparison
        brand = listing.get('brand', '')
        model = listing.get('model', '')
        condition = listing.get('condition', 'unknown')
        
        try:
            wholesale_value = self.price_analyzer.estimate_wholesale_value(
                brand, model, condition, asking_price
            )
            
            if wholesale_value and wholesale_value > 0:
                margin_pct = ((wholesale_value - asking_price) / asking_price) * 100
                
                # Higher margin = higher score
                if margin_pct >= 50:
                    return 100.0
                elif margin_pct >= 25:
                    return 80.0
                elif margin_pct >= 0:
                    return 60.0
                else:
                    return 20.0
            
        except Exception:
            pass
        
        # Fallback scoring based on price ranges
        if asking_price < 10000:
            return 40.0  # Low price, might be good deal
        elif asking_price < 50000:
            return 60.0  # Medium price range
        elif asking_price < 150000:
            return 80.0  # High-value equipment
        else:
            return 50.0  # Very expensive, harder to flip
    
    def _calculate_condition_score(self, listing: Dict[str, Any]) -> float:
        """Calculate condition score"""
        condition = listing.get('condition', '').lower()
        
        condition_scores = {
            'new': 100.0,
            'excellent': 90.0,
            'good': 70.0,
            'fair': 50.0,
            'used': 60.0,
            'refurbished': 80.0,
            'poor': 20.0,
            'as-is': 10.0
        }
        
        return condition_scores.get(condition, 50.0)
    
    def _calculate_urgency_score(self, listing: Dict[str, Any]) -> float:
        """Calculate urgency score based on auction timing"""
        auction_end_ts = listing.get('auction_end_ts')
        if not auction_end_ts:
            return 50.0  # No urgency if not an auction
        
        current_time = time.time()
        time_remaining = auction_end_ts - current_time
        
        if time_remaining <= 0:
            return 0.0  # Auction ended
        elif time_remaining <= 3600:  # 1 hour
            return 100.0  # Very urgent
        elif time_remaining <= 86400:  # 24 hours
            return 80.0  # Urgent
        elif time_remaining <= 604800:  # 1 week
            return 60.0  # Some urgency
        else:
            return 40.0  # Not urgent
    
    def _calculate_location_score(self, listing: Dict[str, Any]) -> float:
        """Calculate location score based on shipping costs and market"""
        state = listing.get('location_state', '').lower()
        country = listing.get('location_country', '').lower()
        
        # Prefer US locations for easier shipping
        if country == 'usa' or country == 'united states':
            # Prefer major metropolitan areas
            major_cities = ['ca', 'ny', 'tx', 'fl', 'il', 'pa', 'oh', 'ga', 'nc', 'mi']
            if state in major_cities:
                return 90.0
            else:
                return 70.0
        elif country in ['canada', 'mexico']:
            return 60.0  # North America, manageable shipping
        else:
            return 30.0  # International, higher shipping costs
    
    def _calculate_overall_confidence(self, listings: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence in the hunting results"""
        if not listings:
            return 0.0
        
        # Average confidence of all listings
        total_confidence = sum(
            listing.get('discovery_confidence', 0.5) for listing in listings
        )
        
        return total_confidence / len(listings)
    
    def _call_llm_api(self, prompt: str, content: str) -> str:
        """Call LLM API with retry logic"""
        for attempt in range(self.max_retries):
            try:
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                
                data = {
                    'model': self.model,
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'You are an expert at finding and extracting laser equipment listings from websites. Always return valid JSON.'
                        },
                        {
                            'role': 'user',
                            'content': f"{prompt}\n\nContent to analyze:\n{content[:8000]}"  # Limit content size
                        }
                    ],
                    'temperature': self.temperature,
                    'max_tokens': self.max_tokens
                }
                
                response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
                response.raise_for_status()
                
                result = response.json()
                return result['choices'][0]['message']['content']
                
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                    continue
                else:
                    raise e
    
    def _parse_llm_response(self, response: str) -> Any:
        """Parse LLM response as JSON"""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return json.loads(response)
        except json.JSONDecodeError:
            # Fallback: try to parse as single object
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return []
    
    def _get_api_key(self) -> str:
        """Get API key from environment"""
        import os
        return os.getenv('GROQ_API_KEY', '')
    
    def hunt_specific_brand(self, brand: str, model: str = None) -> HuntingResult:
        """Hunt for specific brand/model combinations"""
        search_terms = [brand]
        if model:
            search_terms.append(model)
        
        return self.hunt_laser_equipment(
            search_terms=search_terms,
            geographic_scope="United States",
            price_range=(1000, 500000),
            equipment_types=["laser", "ipl", "rf", "hifu"]
        )
    
    def hunt_auction_sites(self) -> HuntingResult:
        """Hunt specifically on auction websites"""
        auction_keywords = [
            'auction', 'bid', 'surplus', 'government', 'liquidation',
            'bidspotter', 'proxibid', 'govdeals', 'gsa auctions'
        ]
        
        return self.hunt_laser_equipment(
            search_terms=auction_keywords + self.laser_keywords,
            geographic_scope="United States",
            price_range=(5000, 200000),
            equipment_types=["laser", "medical equipment"]
        )
    
    def hunt_high_value_equipment(self) -> HuntingResult:
        """Hunt for high-value laser equipment specifically"""
        high_value_terms = [
            'sciton joule', 'cynosure picosure', 'cutera excel v',
            'candela gentlemax', 'lumenis m22', 'alma secret rf',
            'inmode morpheus8', 'btl emsculpt'
        ]
        
        return self.hunt_laser_equipment(
            search_terms=high_value_terms,
            geographic_scope="United States",
            price_range=(25000, 500000),
            equipment_types=["laser", "aesthetic equipment"]
        )
