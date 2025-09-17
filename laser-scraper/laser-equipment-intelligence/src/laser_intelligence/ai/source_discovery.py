"""
LLM-driven source discovery system
Automatically finds new auction sites, marketplaces, and dealers
"""

import json
import time
import requests
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime, timedelta


@dataclass
class DiscoveredSource:
    """Information about a discovered source"""
    url: str
    name: str
    source_type: str  # 'auction', 'marketplace', 'dealer', 'classified', 'rss'
    risk_level: str   # 'low', 'medium', 'high'
    estimated_listings: int
    last_checked: str
    extraction_method: str  # 'scraper', 'api', 'rss', 'llm', 'playwright'
    confidence: float
    geographic_scope: str
    specialties: List[str]
    contact_info: Dict[str, str]
    notes: str


class LLMSourceDiscovery:
    """LLM-driven system for discovering new laser equipment sources"""
    
    def __init__(self, api_key: str = None, api_url: str = None):
        self.api_key = api_key or self._get_api_key()
        self.api_url = api_url or "https://api.groq.com/openai/v1/chat/completions"
        self.max_retries = 3
        self.retry_delay = 1
        
        # Known source patterns for validation
        self.known_patterns = {
            'auction': ['auction', 'bid', 'surplus', 'liquidation', 'govdeals', 'gsa'],
            'marketplace': ['marketplace', 'classified', 'craigslist', 'facebook', 'ebay'],
            'dealer': ['dealer', 'equipment', 'medical', 'laser', 'aesthetic', 'beauty'],
            'rss': ['rss', 'feed', 'xml', 'atom']
        }
        
        # Geographic regions to search
        self.geographic_regions = [
            'United States', 'Canada', 'United Kingdom', 'Australia',
            'Germany', 'France', 'Italy', 'Spain', 'Netherlands',
            'Mexico', 'Brazil', 'Argentina', 'Japan', 'South Korea'
        ]
    
    def discover_new_sources(self, 
                           search_depth: str = "comprehensive",
                           geographic_focus: List[str] = None,
                           source_types: List[str] = None) -> List[DiscoveredSource]:
        """
        Discover new sources for laser equipment using LLM web search
        """
        if geographic_focus is None:
            geographic_focus = ['United States']
        
        if source_types is None:
            source_types = ['auction', 'marketplace', 'dealer', 'classified']
        
        discovered_sources = []
        
        # Search for each source type in each geographic region
        for source_type in source_types:
            for region in geographic_focus:
                sources = self._discover_sources_by_type_and_region(source_type, region, search_depth)
                discovered_sources.extend(sources)
        
        # Remove duplicates and validate sources
        unique_sources = self._deduplicate_sources(discovered_sources)
        validated_sources = self._validate_sources(unique_sources)
        
        return validated_sources
    
    def _discover_sources_by_type_and_region(self, 
                                           source_type: str, 
                                           region: str, 
                                           search_depth: str) -> List[DiscoveredSource]:
        """Discover sources for specific type and region"""
        
        discovery_prompt = f"""
        You are an expert at finding websites that sell or auction laser equipment.
        
        Find {source_type} websites in {region} that deal with:
        - Medical laser equipment
        - Aesthetic laser equipment  
        - Laser systems and devices
        - Used laser equipment
        - Laser equipment auctions
        - Medical equipment resale
        
        Search for websites that might have listings for brands like:
        - Sciton, Cynosure, Cutera, Candela, Lumenis, Alma
        - InMode, BTL, Lutronic, Bison, DEKA, Quanta
        - Models: Joule, PicoSure, PicoWay, GentleMax, M22, BBL, Secret RF, Morpheus8
        
        For each website you find, provide:
        - URL (must be valid and accessible)
        - Website name
        - Source type: {source_type}
        - Risk level: low/medium/high (based on anti-bot measures)
        - Estimated number of laser equipment listings
        - Last checked date
        - Recommended extraction method: scraper/api/rss/llm/playwright
        - Confidence score: 0.0-1.0
        - Geographic scope: {region}
        - Specialties: array of equipment types they specialize in
        - Contact info: phone/email if available
        - Notes: any relevant information about the site
        
        Search depth: {search_depth}
        Focus on active, legitimate websites with recent listings.
        
        Return as JSON array of objects.
        """
        
        try:
            response = self._call_llm_api(discovery_prompt, "")
            sources_data = self._parse_llm_response(response)
            
            discovered_sources = []
            for source_data in sources_data:
                if isinstance(source_data, dict) and 'url' in source_data:
                    discovered_sources.append(DiscoveredSource(
                        url=source_data['url'],
                        name=source_data.get('name', 'Unknown'),
                        source_type=source_type,
                        risk_level=source_data.get('risk_level', 'medium'),
                        estimated_listings=source_data.get('estimated_listings', 0),
                        last_checked=datetime.now().isoformat(),
                        extraction_method=source_data.get('extraction_method', 'llm'),
                        confidence=source_data.get('confidence', 0.5),
                        geographic_scope=region,
                        specialties=source_data.get('specialties', []),
                        contact_info=source_data.get('contact_info', {}),
                        notes=source_data.get('notes', '')
                    ))
            
            return discovered_sources
            
        except Exception as e:
            print(f"Error discovering sources for {source_type} in {region}: {e}")
            return []
    
    def discover_auction_sites(self, region: str = "United States") -> List[DiscoveredSource]:
        """Specifically discover auction websites"""
        return self._discover_sources_by_type_and_region('auction', region, 'comprehensive')
    
    def discover_marketplace_sites(self, region: str = "United States") -> List[DiscoveredSource]:
        """Specifically discover marketplace websites"""
        return self._discover_sources_by_type_and_region('marketplace', region, 'comprehensive')
    
    def discover_dealer_sites(self, region: str = "United States") -> List[DiscoveredSource]:
        """Specifically discover dealer websites"""
        return self._discover_sources_by_type_and_region('dealer', region, 'comprehensive')
    
    def discover_rss_feeds(self, region: str = "United States") -> List[DiscoveredSource]:
        """Discover RSS feeds for laser equipment"""
        return self._discover_sources_by_type_and_region('rss', region, 'comprehensive')
    
    def discover_government_sources(self) -> List[DiscoveredSource]:
        """Discover government surplus and auction sources"""
        
        discovery_prompt = """
        Find government websites that auction or sell surplus laser equipment.
        
        Look for:
        - Government surplus websites
        - Federal auction sites
        - State auction sites
        - Military surplus sites
        - Hospital liquidation sites
        - University surplus sites
        - Municipal equipment sales
        
        Focus on sites that might have medical or scientific laser equipment.
        
        For each site, provide:
        - URL
        - Website name
        - Source type: auction
        - Risk level: low (government sites are usually low risk)
        - Estimated listings
        - Last checked date
        - Extraction method: scraper/rss/api
        - Confidence score
        - Geographic scope
        - Specialties: government surplus, medical equipment, scientific equipment
        - Contact info
        - Notes
        
        Return as JSON array.
        """
        
        try:
            response = self._call_llm_api(discovery_prompt, "")
            sources_data = self._parse_llm_response(response)
            
            discovered_sources = []
            for source_data in sources_data:
                if isinstance(source_data, dict) and 'url' in source_data:
                    discovered_sources.append(DiscoveredSource(
                        url=source_data['url'],
                        name=source_data.get('name', 'Unknown Government Source'),
                        source_type='auction',
                        risk_level='low',
                        estimated_listings=source_data.get('estimated_listings', 0),
                        last_checked=datetime.now().isoformat(),
                        extraction_method=source_data.get('extraction_method', 'scraper'),
                        confidence=source_data.get('confidence', 0.7),
                        geographic_scope=source_data.get('geographic_scope', 'United States'),
                        specialties=['government surplus', 'medical equipment', 'scientific equipment'],
                        contact_info=source_data.get('contact_info', {}),
                        notes=source_data.get('notes', 'Government surplus source')
                    ))
            
            return discovered_sources
            
        except Exception as e:
            print(f"Error discovering government sources: {e}")
            return []
    
    def discover_international_sources(self) -> List[DiscoveredSource]:
        """Discover international sources for laser equipment"""
        
        international_regions = [
            'Canada', 'United Kingdom', 'Australia', 'Germany', 
            'France', 'Italy', 'Spain', 'Netherlands', 'Japan'
        ]
        
        all_sources = []
        for region in international_regions:
            # Discover all types for each region
            for source_type in ['auction', 'marketplace', 'dealer']:
                sources = self._discover_sources_by_type_and_region(source_type, region, 'moderate')
                all_sources.extend(sources)
        
        return all_sources
    
    def discover_specialized_sources(self) -> List[DiscoveredSource]:
        """Discover specialized sources for specific equipment types"""
        
        specialized_prompts = {
            'aesthetic_equipment': """
            Find websites specializing in aesthetic laser equipment:
            - Dermatology lasers
            - Cosmetic laser systems
            - IPL devices
            - RF devices
            - HIFU devices
            - CoolSculpting equipment
            """,
            'medical_equipment': """
            Find websites specializing in medical laser equipment:
            - Surgical lasers
            - Therapeutic lasers
            - Diagnostic lasers
            - Medical device resale
            - Hospital equipment auctions
            """,
            'scientific_equipment': """
            Find websites specializing in scientific laser equipment:
            - Research lasers
            - Laboratory equipment
            - Industrial lasers
            - Scientific instrument resale
            - University surplus
            """
        }
        
        all_sources = []
        for specialty, prompt in specialized_prompts.items():
            try:
                response = self._call_llm_api(prompt, "")
                sources_data = self._parse_llm_response(response)
                
                for source_data in sources_data:
                    if isinstance(source_data, dict) and 'url' in source_data:
                        all_sources.append(DiscoveredSource(
                            url=source_data['url'],
                            name=source_data.get('name', f'Unknown {specialty} source'),
                            source_type=source_data.get('source_type', 'dealer'),
                            risk_level=source_data.get('risk_level', 'medium'),
                            estimated_listings=source_data.get('estimated_listings', 0),
                            last_checked=datetime.now().isoformat(),
                            extraction_method=source_data.get('extraction_method', 'llm'),
                            confidence=source_data.get('confidence', 0.6),
                            geographic_scope=source_data.get('geographic_scope', 'International'),
                            specialties=[specialty],
                            contact_info=source_data.get('contact_info', {}),
                            notes=source_data.get('notes', f'Specialized in {specialty}')
                        ))
            except Exception as e:
                print(f"Error discovering {specialty} sources: {e}")
        
        return all_sources
    
    def _deduplicate_sources(self, sources: List[DiscoveredSource]) -> List[DiscoveredSource]:
        """Remove duplicate sources based on URL"""
        seen_urls = set()
        unique_sources = []
        
        for source in sources:
            if source.url not in seen_urls:
                seen_urls.add(source.url)
                unique_sources.append(source)
        
        return unique_sources
    
    def _validate_sources(self, sources: List[DiscoveredSource]) -> List[DiscoveredSource]:
        """Validate discovered sources by checking accessibility"""
        validated_sources = []
        
        for source in sources:
            try:
                # Quick HEAD request to check if site is accessible
                response = requests.head(source.url, timeout=10, allow_redirects=True)
                if response.status_code < 400:
                    validated_sources.append(source)
                else:
                    print(f"Source validation failed for {source.url}: {response.status_code}")
            except Exception as e:
                print(f"Source validation error for {source.url}: {e}")
                # Still include the source but mark as unvalidated
                source.notes += f" [Validation failed: {str(e)}]"
                validated_sources.append(source)
        
        return validated_sources
    
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
                            'content': 'You are an expert at finding websites and online sources. Always return valid JSON arrays.'
                        },
                        {
                            'role': 'user',
                            'content': f"{prompt}\n\nContent to analyze:\n{content[:4000]}"
                        }
                    ],
                    'temperature': 0.2,
                    'max_tokens': 3000
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
    
    def get_discovery_summary(self, sources: List[DiscoveredSource]) -> Dict[str, Any]:
        """Generate summary of discovered sources"""
        if not sources:
            return {'total_sources': 0}
        
        summary = {
            'total_sources': len(sources),
            'by_type': {},
            'by_risk_level': {},
            'by_region': {},
            'by_extraction_method': {},
            'total_estimated_listings': 0,
            'average_confidence': 0.0,
            'high_confidence_sources': 0
        }
        
        total_confidence = 0
        for source in sources:
            # Count by type
            source_type = source.source_type
            summary['by_type'][source_type] = summary['by_type'].get(source_type, 0) + 1
            
            # Count by risk level
            risk_level = source.risk_level
            summary['by_risk_level'][risk_level] = summary['by_risk_level'].get(risk_level, 0) + 1
            
            # Count by region
            region = source.geographic_scope
            summary['by_region'][region] = summary['by_region'].get(region, 0) + 1
            
            # Count by extraction method
            method = source.extraction_method
            summary['by_extraction_method'][method] = summary['by_extraction_method'].get(method, 0) + 1
            
            # Sum estimated listings
            summary['total_estimated_listings'] += source.estimated_listings
            
            # Track confidence
            total_confidence += source.confidence
            if source.confidence >= 0.8:
                summary['high_confidence_sources'] += 1
        
        summary['average_confidence'] = total_confidence / len(sources)
        
        return summary
