"""
Adaptive LLM-based extraction system
Can extract data from any website without pre-built scrapers
"""

import json
import time
import requests
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import re
from bs4 import BeautifulSoup
from laser_intelligence.utils.brand_mapping import BrandMapper
from laser_intelligence.utils.price_analysis import PriceAnalyzer


@dataclass
class ExtractionResult:
    """Result of adaptive extraction"""
    success: bool
    extracted_listings: List[Dict[str, Any]]
    extraction_method: str
    confidence_score: float
    processing_time: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class SiteAnalysis:
    """Analysis of a website's structure and content"""
    site_type: str  # 'auction', 'marketplace', 'dealer', 'classified', 'unknown'
    has_pagination: bool
    has_search: bool
    has_filters: bool
    content_structure: str  # 'list', 'grid', 'table', 'mixed'
    js_heavy: bool
    anti_bot_measures: List[str]
    recommended_approach: str
    confidence: float


class AdaptiveExtractor:
    """LLM-based adaptive extraction system for any website"""
    
    def __init__(self, api_key: str = None, api_url: str = None):
        self.api_key = api_key or self._get_api_key()
        self.api_url = api_url or "https://api.groq.com/openai/v1/chat/completions"
        self.brand_mapper = BrandMapper()
        self.price_analyzer = PriceAnalyzer()
        self.max_retries = 3
        self.retry_delay = 1
        
        # Extraction strategies based on site analysis
        self.extraction_strategies = {
            'auction': self._extract_auction_listings,
            'marketplace': self._extract_marketplace_listings,
            'dealer': self._extract_dealer_listings,
            'classified': self._extract_classified_listings,
            'unknown': self._extract_generic_listings
        }
    
    def extract_from_url(self, url: str, max_pages: int = 5) -> ExtractionResult:
        """
        Extract laser equipment listings from any URL using adaptive approach
        """
        start_time = time.time()
        
        try:
            # Step 1: Analyze the website structure
            site_analysis = self._analyze_website(url)
            
            # Step 2: Choose appropriate extraction strategy
            extraction_method = site_analysis.recommended_approach
            extractor_func = self.extraction_strategies.get(site_analysis.site_type, self._extract_generic_listings)
            
            # Step 3: Extract listings using chosen strategy
            extracted_listings = extractor_func(url, site_analysis, max_pages)
            
            # Step 4: Process and normalize extracted data
            processed_listings = self._process_extracted_listings(extracted_listings, url)
            
            # Step 5: Calculate confidence score
            confidence_score = self._calculate_extraction_confidence(processed_listings, site_analysis)
            
            processing_time = time.time() - start_time
            
            return ExtractionResult(
                success=True,
                extracted_listings=processed_listings,
                extraction_method=extraction_method,
                confidence_score=confidence_score,
                processing_time=processing_time,
                metadata={
                    'site_analysis': site_analysis.__dict__,
                    'total_pages_scraped': min(max_pages, len(extracted_listings)),
                    'url': url
                }
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return ExtractionResult(
                success=False,
                extracted_listings=[],
                extraction_method='failed',
                confidence_score=0.0,
                processing_time=processing_time,
                error_message=str(e),
                metadata={'url': url}
            )
    
    def _analyze_website(self, url: str) -> SiteAnalysis:
        """Analyze website structure and determine extraction approach"""
        
        try:
            # Get page content
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                raise Exception(f"Failed to fetch URL: {response.status_code}")
            
            content = response.text
            soup = BeautifulSoup(content, 'html.parser')
            
            # Analyze page structure
            analysis_prompt = f"""
            Analyze this website to determine the best approach for extracting laser equipment listings.
            
            URL: {url}
            Content: {content[:5000]}
            
            Determine:
            1. Site type: auction/marketplace/dealer/classified/unknown
            2. Has pagination: true/false
            3. Has search functionality: true/false
            4. Has filters: true/false
            5. Content structure: list/grid/table/mixed
            6. JavaScript heavy: true/false
            7. Anti-bot measures: list of detected measures
            8. Recommended approach: scraper/playwright/llm/api/rss
            9. Confidence: 0.0-1.0
            
            Look for:
            - Listing containers (divs, articles, items)
            - Pagination elements (next, page numbers)
            - Search forms
            - Filter options
            - JavaScript frameworks
            - Anti-bot protection (Cloudflare, CAPTCHA, etc.)
            - Data attributes or structured data
            
            Return as JSON object.
            """
            
            response = self._call_llm_api(analysis_prompt, content)
            analysis_data = self._parse_llm_response(response)
            
            if isinstance(analysis_data, dict):
                return SiteAnalysis(
                    site_type=analysis_data.get('site_type', 'unknown'),
                    has_pagination=analysis_data.get('has_pagination', False),
                    has_search=analysis_data.get('has_search', False),
                    has_filters=analysis_data.get('has_filters', False),
                    content_structure=analysis_data.get('content_structure', 'mixed'),
                    js_heavy=analysis_data.get('javascript_heavy', False),
                    anti_bot_measures=analysis_data.get('anti_bot_measures', []),
                    recommended_approach=analysis_data.get('recommended_approach', 'llm'),
                    confidence=analysis_data.get('confidence', 0.5)
                )
            else:
                # Fallback analysis
                return self._fallback_analysis(soup, url)
                
        except Exception as e:
            print(f"Error analyzing website {url}: {e}")
            return SiteAnalysis(
                site_type='unknown',
                has_pagination=False,
                has_search=False,
                has_filters=False,
                content_structure='mixed',
                js_heavy=True,
                anti_bot_measures=['unknown'],
                recommended_approach='llm',
                confidence=0.3
            )
    
    def _fallback_analysis(self, soup: BeautifulSoup, url: str) -> SiteAnalysis:
        """Fallback analysis when LLM analysis fails"""
        
        # Basic heuristics
        has_pagination = bool(soup.find(['a', 'button'], string=re.compile(r'next|more|page', re.I)))
        has_search = bool(soup.find('input', {'type': 'search'}) or soup.find('form', {'role': 'search'}))
        has_filters = bool(soup.find(['select', 'input'], {'type': 'checkbox'}) or soup.find('div', class_=re.compile(r'filter', re.I)))
        
        # Check for common patterns
        listing_containers = soup.find_all(['div', 'article', 'li'], class_=re.compile(r'item|listing|product|card', re.I))
        content_structure = 'list' if len(listing_containers) > 0 else 'unknown'
        
        # Check for JavaScript
        scripts = soup.find_all('script')
        js_heavy = len(scripts) > 10
        
        # Determine site type based on URL and content
        url_lower = url.lower()
        if any(word in url_lower for word in ['auction', 'bid', 'surplus']):
            site_type = 'auction'
        elif any(word in url_lower for word in ['marketplace', 'classified', 'craigslist']):
            site_type = 'marketplace'
        elif any(word in url_lower for word in ['dealer', 'equipment', 'medical']):
            site_type = 'dealer'
        else:
            site_type = 'unknown'
        
        return SiteAnalysis(
            site_type=site_type,
            has_pagination=has_pagination,
            has_search=has_search,
            has_filters=has_filters,
            content_structure=content_structure,
            js_heavy=js_heavy,
            anti_bot_measures=[],
            recommended_approach='llm',
            confidence=0.4
        )
    
    def _extract_auction_listings(self, url: str, analysis: SiteAnalysis, max_pages: int) -> List[Dict[str, Any]]:
        """Extract listings from auction websites"""
        
        extraction_prompt = f"""
        Extract laser equipment auction listings from this website.
        
        URL: {url}
        
        Look for auction-specific data:
        - Lot numbers
        - Current bid amounts
        - Starting bid amounts
        - Buy-it-now prices
        - Auction end times
        - Bid increments
        - Reserve prices
        - Seller information
        - Auction house details
        
        For each listing, extract:
        - title_raw
        - description_raw
        - brand (normalized)
        - model (normalized)
        - asking_price (current bid or starting bid)
        - condition
        - location_city
        - location_state
        - location_country
        - serial_number
        - year
        - hours
        - accessories
        - auction_end_ts (timestamp)
        - seller_name
        - lot_number
        - reserve_price
        - bid_increment
        - source_url
        - source_listing_id
        
        Focus on laser equipment brands: Sciton, Cynosure, Cutera, Candela, Lumenis, Alma, InMode, BTL, Lutronic, Bison, DEKA, Quanta
        
        Return as JSON array of objects.
        """
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                return []
            
            content = response.text
            response = self._call_llm_api(extraction_prompt, content)
            listings = self._parse_llm_response(response)
            
            return listings if isinstance(listings, list) else []
            
        except Exception as e:
            print(f"Error extracting auction listings from {url}: {e}")
            return []
    
    def _extract_marketplace_listings(self, url: str, analysis: SiteAnalysis, max_pages: int) -> List[Dict[str, Any]]:
        """Extract listings from marketplace websites"""
        
        extraction_prompt = f"""
        Extract laser equipment marketplace listings from this website.
        
        URL: {url}
        
        Look for marketplace-specific data:
        - Item titles
        - Descriptions
        - Prices (asking price, negotiable)
        - Seller contact information
        - Item condition
        - Location details
        - Posting dates
        - Item IDs
        - Seller ratings/reviews
        
        For each listing, extract:
        - title_raw
        - description_raw
        - brand (normalized)
        - model (normalized)
        - asking_price
        - condition
        - location_city
        - location_state
        - location_country
        - serial_number
        - year
        - hours
        - accessories
        - seller_name
        - seller_contact
        - posting_date
        - source_url
        - source_listing_id
        
        Focus on laser equipment brands: Sciton, Cynosure, Cutera, Candela, Lumenis, Alma, InMode, BTL, Lutronic, Bison, DEKA, Quanta
        
        Return as JSON array of objects.
        """
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                return []
            
            content = response.text
            response = self._call_llm_api(extraction_prompt, content)
            listings = self._parse_llm_response(response)
            
            return listings if isinstance(listings, list) else []
            
        except Exception as e:
            print(f"Error extracting marketplace listings from {url}: {e}")
            return []
    
    def _extract_dealer_listings(self, url: str, analysis: SiteAnalysis, max_pages: int) -> List[Dict[str, Any]]:
        """Extract listings from dealer websites"""
        
        extraction_prompt = f"""
        Extract laser equipment dealer listings from this website.
        
        URL: {url}
        
        Look for dealer-specific data:
        - Product titles
        - Detailed specifications
        - Pricing information
        - Availability status
        - Warranty information
        - Service information
        - Contact details
        - Product categories
        
        For each listing, extract:
        - title_raw
        - description_raw
        - brand (normalized)
        - model (normalized)
        - asking_price
        - condition (usually new or refurbished)
        - location_city
        - location_state
        - location_country
        - serial_number
        - year
        - hours
        - accessories
        - warranty_info
        - availability
        - dealer_name
        - dealer_contact
        - source_url
        - source_listing_id
        
        Focus on laser equipment brands: Sciton, Cynosure, Cutera, Candela, Lumenis, Alma, InMode, BTL, Lutronic, Bison, DEKA, Quanta
        
        Return as JSON array of objects.
        """
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                return []
            
            content = response.text
            response = self._call_llm_api(extraction_prompt, content)
            listings = self._parse_llm_response(response)
            
            return listings if isinstance(listings, list) else []
            
        except Exception as e:
            print(f"Error extracting dealer listings from {url}: {e}")
            return []
    
    def _extract_classified_listings(self, url: str, analysis: SiteAnalysis, max_pages: int) -> List[Dict[str, Any]]:
        """Extract listings from classified ad websites"""
        
        extraction_prompt = f"""
        Extract laser equipment classified listings from this website.
        
        URL: {url}
        
        Look for classified-specific data:
        - Ad titles
        - Descriptions
        - Contact information
        - Location details
        - Posting dates
        - Ad IDs
        - Price negotiations
        
        For each listing, extract:
        - title_raw
        - description_raw
        - brand (normalized)
        - model (normalized)
        - asking_price
        - condition
        - location_city
        - location_state
        - location_country
        - serial_number
        - year
        - hours
        - accessories
        - seller_name
        - seller_contact
        - posting_date
        - source_url
        - source_listing_id
        
        Focus on laser equipment brands: Sciton, Cynosure, Cutera, Candela, Lumenis, Alma, InMode, BTL, Lutronic, Bison, DEKA, Quanta
        
        Return as JSON array of objects.
        """
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                return []
            
            content = response.text
            response = self._call_llm_api(extraction_prompt, content)
            listings = self._parse_llm_response(response)
            
            return listings if isinstance(listings, list) else []
            
        except Exception as e:
            print(f"Error extracting classified listings from {url}: {e}")
            return []
    
    def _extract_generic_listings(self, url: str, analysis: SiteAnalysis, max_pages: int) -> List[Dict[str, Any]]:
        """Generic extraction for unknown website types"""
        
        extraction_prompt = f"""
        Extract laser equipment listings from this website.
        
        URL: {url}
        
        Look for any laser equipment information:
        - Product titles
        - Descriptions
        - Prices
        - Contact information
        - Location details
        - Equipment specifications
        
        For each listing, extract:
        - title_raw
        - description_raw
        - brand (normalized)
        - model (normalized)
        - asking_price
        - condition
        - location_city
        - location_state
        - location_country
        - serial_number
        - year
        - hours
        - accessories
        - seller_name
        - source_url
        - source_listing_id
        
        Focus on laser equipment brands: Sciton, Cynosure, Cutera, Candela, Lumenis, Alma, InMode, BTL, Lutronic, Bison, DEKA, Quanta
        
        Return as JSON array of objects.
        """
        
        try:
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                return []
            
            content = response.text
            response = self._call_llm_api(extraction_prompt, content)
            listings = self._parse_llm_response(response)
            
            return listings if isinstance(listings, list) else []
            
        except Exception as e:
            print(f"Error extracting generic listings from {url}: {e}")
            return []
    
    def _process_extracted_listings(self, listings: List[Dict[str, Any]], source_url: str) -> List[Dict[str, Any]]:
        """Process and normalize extracted listings"""
        
        processed_listings = []
        
        for listing in listings:
            if not isinstance(listing, dict):
                continue
            
            # Normalize brand and model
            raw_brand = listing.get('brand', '')
            raw_model = listing.get('model', '')
            
            if raw_brand:
                normalized_brand = self.brand_mapper.normalize_brand(raw_brand)
                listing['brand'] = normalized_brand
            else:
                listing['brand'] = 'Unknown_brand'
            
            if raw_model and raw_brand:
                normalized_model = self.brand_mapper.normalize_model(raw_model, raw_brand)
                listing['model'] = normalized_model
            else:
                listing['model'] = 'Unknown_model'
            
            # Normalize price
            asking_price = listing.get('asking_price', 0)
            if isinstance(asking_price, str):
                # Extract numeric value from price string
                price_match = re.search(r'[\d,]+\.?\d*', asking_price.replace(',', ''))
                if price_match:
                    asking_price = float(price_match.group())
                else:
                    asking_price = 0
            
            listing['asking_price'] = asking_price
            
            # Add source metadata
            listing['source_url'] = source_url
            listing['extraction_method'] = 'llm_adaptive'
            listing['extraction_timestamp'] = time.time()
            
            # Ensure required fields exist
            required_fields = [
                'title_raw', 'description_raw', 'brand', 'model', 'asking_price',
                'condition', 'location_city', 'location_state', 'location_country',
                'serial_number', 'year', 'hours', 'accessories', 'seller_name'
            ]
            
            for field in required_fields:
                if field not in listing:
                    listing[field] = None
            
            processed_listings.append(listing)
        
        return processed_listings
    
    def _calculate_extraction_confidence(self, listings: List[Dict[str, Any]], analysis: SiteAnalysis) -> float:
        """Calculate confidence score for extraction results"""
        
        if not listings:
            return 0.0
        
        # Base confidence from site analysis
        base_confidence = analysis.confidence
        
        # Adjust based on number of listings found
        listing_count_factor = min(1.0, len(listings) / 10.0)  # Cap at 1.0 for 10+ listings
        
        # Adjust based on data completeness
        completeness_scores = []
        for listing in listings:
            non_null_fields = sum(1 for v in listing.values() if v is not None and v != '')
            total_fields = len(listing)
            completeness_scores.append(non_null_fields / total_fields)
        
        avg_completeness = sum(completeness_scores) / len(completeness_scores) if completeness_scores else 0.0
        
        # Calculate final confidence
        final_confidence = (base_confidence * 0.4 + listing_count_factor * 0.3 + avg_completeness * 0.3)
        
        return min(1.0, max(0.0, final_confidence))
    
    def _call_llm_api(self, prompt: str, content: str) -> str:
        """Call LLM API with retry logic"""
        for attempt in range(self.max_retries):
            try:
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                
                data = {
                    'model': 'llama-3.1-70b-versatile',
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'You are an expert at extracting structured data from websites. Always return valid JSON arrays.'
                        },
                        {
                            'role': 'user',
                            'content': f"{prompt}\n\nContent to analyze:\n{content[:6000]}"
                        }
                    ],
                    'temperature': 0.1,
                    'max_tokens': 4000
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
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return []
    
    def _get_api_key(self) -> str:
        """Get API key from environment"""
        import os
        return os.getenv('GROQ_API_KEY', '')
