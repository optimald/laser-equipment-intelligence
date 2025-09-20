"""
LLM-driven hunting orchestrator
Coordinates source discovery, adaptive extraction, and result processing
"""

import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from laser_intelligence.ai.llm_hunter import LLMHunter, HuntingResult
from laser_intelligence.ai.source_discovery import LLMSourceDiscovery, DiscoveredSource
from laser_intelligence.ai.adaptive_extractor import AdaptiveExtractor, ExtractionResult
from laser_intelligence.utils.brand_mapping import BrandMapper
from laser_intelligence.utils.price_analysis import PriceAnalyzer


@dataclass
class HuntingSession:
    """Complete hunting session results"""
    session_id: str
    start_time: datetime
    end_time: datetime
    discovered_sources: List[DiscoveredSource]
    extracted_listings: List[Dict[str, Any]]
    total_processing_time: float
    success_rate: float
    confidence_score: float
    hunting_strategy: str
    geographic_scope: str
    search_terms: List[str]
    results_summary: Dict[str, Any]


class HuntingOrchestrator:
    """Orchestrates the complete LLM-driven hunting process"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.hunter = LLMHunter(api_key)
        self.source_discovery = LLMSourceDiscovery(api_key)
        self.adaptive_extractor = AdaptiveExtractor(api_key)
        self.brand_mapper = BrandMapper()
        self.price_analyzer = PriceAnalyzer()
        
        # Hunting strategies
        self.hunting_strategies = {
            'comprehensive': self._comprehensive_hunt,
            'targeted': self._targeted_hunt,
            'discovery': self._discovery_hunt,
            'high_value': self._high_value_hunt,
            'auction_focused': self._auction_focused_hunt
        }
    
    def hunt_laser_equipment(self, 
                           strategy: str = 'comprehensive',
                           search_terms: List[str] = None,
                           geographic_scope: List[str] = None,
                           max_sources: int = 50,
                           max_listings_per_source: int = 100,
                           min_confidence: float = 0.6) -> HuntingSession:
        """
        Main hunting function that orchestrates the complete process
        """
        session_id = f"hunt_{int(time.time())}"
        start_time = datetime.now()
        
        try:
            # Choose hunting strategy
            hunt_func = self.hunting_strategies.get(strategy, self._comprehensive_hunt)
            
            # Execute hunting strategy
            results = hunt_func(
                search_terms=search_terms,
                geographic_scope=geographic_scope,
                max_sources=max_sources,
                max_listings_per_source=max_listings_per_source,
                min_confidence=min_confidence
            )
            
            # Process results
            processed_results = self._process_hunting_results(results)
            
            # Calculate session metrics
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()
            
            session = HuntingSession(
                session_id=session_id,
                start_time=start_time,
                end_time=end_time,
                discovered_sources=results.get('discovered_sources', []),
                extracted_listings=processed_results.get('extracted_listings', []),
                total_processing_time=total_time,
                success_rate=processed_results.get('success_rate', 0.0),
                confidence_score=processed_results.get('confidence_score', 0.0),
                hunting_strategy=strategy,
                geographic_scope=', '.join(geographic_scope or ['United States']),
                search_terms=search_terms or [],
                results_summary=processed_results.get('summary', {})
            )
            
            return session
            
        except Exception as e:
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()
            
            return HuntingSession(
                session_id=session_id,
                start_time=start_time,
                end_time=end_time,
                discovered_sources=[],
                extracted_listings=[],
                total_processing_time=total_time,
                success_rate=0.0,
                confidence_score=0.0,
                hunting_strategy=strategy,
                geographic_scope=', '.join(geographic_scope or ['United States']),
                search_terms=search_terms or [],
                results_summary={'error': str(e)}
            )
    
    def _comprehensive_hunt(self, 
                          search_terms: List[str] = None,
                          geographic_scope: List[str] = None,
                          max_sources: int = 50,
                          max_listings_per_source: int = 100,
                          min_confidence: float = 0.6) -> Dict[str, Any]:
        """Comprehensive hunting strategy - discover and extract from all source types"""
        
        if search_terms is None:
            search_terms = [
                'sciton', 'cynosure', 'cutera', 'candela', 'lumenis', 'alma',
                'inmode', 'btl', 'lutronic', 'bison', 'deka', 'quanta',
                'laser', 'ipl', 'rf', 'hifu', 'aesthetic equipment'
            ]
        
        if geographic_scope is None:
            geographic_scope = ['United States']
        
        # Step 1: Discover sources
        print("🔍 Discovering sources...")
        discovered_sources = []
        
        # Discover all types of sources
        for source_type in ['auction', 'marketplace', 'dealer', 'classified']:
            sources = self.source_discovery.discover_new_sources(
                search_depth='comprehensive',
                geographic_focus=geographic_scope,
                source_types=[source_type]
            )
            discovered_sources.extend(sources)
        
        # Discover government sources
        gov_sources = self.source_discovery.discover_government_sources()
        discovered_sources.extend(gov_sources)
        
        # Discover international sources
        intl_sources = self.source_discovery.discover_international_sources()
        discovered_sources.extend(intl_sources)
        
        # Filter by confidence and limit
        filtered_sources = [
            s for s in discovered_sources 
            if s.confidence >= min_confidence
        ][:max_sources]
        
        print(f"✅ Discovered {len(filtered_sources)} sources")
        
        # Step 2: Extract listings from sources
        print("📊 Extracting listings...")
        all_listings = []
        successful_extractions = 0
        
        for source in filtered_sources:
            try:
                extraction_result = self.adaptive_extractor.extract_from_url(
                    source.url, 
                    max_pages=5
                )
                
                if extraction_result.success and extraction_result.extracted_listings:
                    all_listings.extend(extraction_result.extracted_listings)
                    successful_extractions += 1
                    print(f"✅ Extracted {len(extraction_result.extracted_listings)} listings from {source.name}")
                else:
                    print(f"❌ Failed to extract from {source.name}: {extraction_result.error_message}")
                
            except Exception as e:
                print(f"❌ Error extracting from {source.name}: {e}")
        
        success_rate = successful_extractions / len(filtered_sources) if filtered_sources else 0.0
        
        return {
            'discovered_sources': filtered_sources,
            'extracted_listings': all_listings,
            'success_rate': success_rate,
            'total_sources_processed': len(filtered_sources),
            'successful_extractions': successful_extractions
        }
    
    def _targeted_hunt(self, 
                      search_terms: List[str] = None,
                      geographic_scope: List[str] = None,
                      max_sources: int = 20,
                      max_listings_per_source: int = 50,
                      min_confidence: float = 0.7) -> Dict[str, Any]:
        """Targeted hunting strategy - focus on specific search terms"""
        
        if search_terms is None:
            search_terms = ['sciton joule', 'cynosure picosure', 'cutera excel v']
        
        if geographic_scope is None:
            geographic_scope = ['United States']
        
        # Use LLM hunter for targeted search
        hunting_result = self.hunter.hunt_laser_equipment(
            search_terms=search_terms,
            geographic_scope=', '.join(geographic_scope),
            price_range=(10000, 200000),
            equipment_types=['laser', 'ipl', 'rf', 'hifu']
        )
        
        if hunting_result.success:
            return {
                'discovered_sources': hunting_result.discovered_sources,
                'extracted_listings': hunting_result.extracted_listings,
                'success_rate': 1.0 if hunting_result.extracted_listings else 0.0,
                'total_sources_processed': len(hunting_result.discovered_sources),
                'successful_extractions': 1 if hunting_result.extracted_listings else 0
            }
        else:
            return {
                'discovered_sources': [],
                'extracted_listings': [],
                'success_rate': 0.0,
                'total_sources_processed': 0,
                'successful_extractions': 0
            }
    
    def _discovery_hunt(self, 
                       search_terms: List[str] = None,
                       geographic_scope: List[str] = None,
                       max_sources: int = 100,
                       max_listings_per_source: int = 20,
                       min_confidence: float = 0.5) -> Dict[str, Any]:
        """Discovery hunting strategy - focus on finding new sources"""
        
        if geographic_scope is None:
            geographic_scope = ['United States', 'Canada', 'United Kingdom']
        
        # Focus on source discovery
        discovered_sources = self.source_discovery.discover_new_sources(
            search_depth='comprehensive',
            geographic_focus=geographic_scope,
            source_types=['auction', 'marketplace', 'dealer', 'classified']
        )
        
        # Filter and limit sources
        filtered_sources = [
            s for s in discovered_sources 
            if s.confidence >= min_confidence
        ][:max_sources]
        
        # Extract from a subset of sources for validation
        sample_size = min(10, len(filtered_sources))
        sample_sources = filtered_sources[:sample_size]
        
        all_listings = []
        successful_extractions = 0
        
        for source in sample_sources:
            try:
                extraction_result = self.adaptive_extractor.extract_from_url(source.url)
                if extraction_result.success and extraction_result.extracted_listings:
                    all_listings.extend(extraction_result.extracted_listings)
                    successful_extractions += 1
            except Exception:
                pass
        
        return {
            'discovered_sources': filtered_sources,
            'extracted_listings': all_listings,
            'success_rate': successful_extractions / sample_size if sample_size > 0 else 0.0,
            'total_sources_processed': sample_size,
            'successful_extractions': successful_extractions
        }
    
    def _high_value_hunt(self, 
                        search_terms: List[str] = None,
                        geographic_scope: List[str] = None,
                        max_sources: int = 30,
                        max_listings_per_source: int = 50,
                        min_confidence: float = 0.8) -> Dict[str, Any]:
        """High-value hunting strategy - focus on expensive equipment"""
        
        if search_terms is None:
            search_terms = [
                'sciton joule', 'cynosure picosure', 'cutera excel v',
                'candela gentlemax', 'lumenis m22', 'alma secret rf',
                'inmode morpheus8', 'btl emsculpt'
            ]
        
        if geographic_scope is None:
            geographic_scope = ['United States']
        
        # Use high-value specific hunting
        hunting_result = self.hunter.hunt_high_value_equipment()
        
        if hunting_result.success:
            return {
                'discovered_sources': hunting_result.discovered_sources,
                'extracted_listings': hunting_result.extracted_listings,
                'success_rate': 1.0 if hunting_result.extracted_listings else 0.0,
                'total_sources_processed': len(hunting_result.discovered_sources),
                'successful_extractions': 1 if hunting_result.extracted_listings else 0
            }
        else:
            return {
                'discovered_sources': [],
                'extracted_listings': [],
                'success_rate': 0.0,
                'total_sources_processed': 0,
                'successful_extractions': 0
            }
    
    def _auction_focused_hunt(self, 
                             search_terms: List[str] = None,
                             geographic_scope: List[str] = None,
                             max_sources: int = 40,
                             max_listings_per_source: int = 100,
                             min_confidence: float = 0.7) -> Dict[str, Any]:
        """Auction-focused hunting strategy"""
        
        if geographic_scope is None:
            geographic_scope = ['United States']
        
        # Discover auction sources
        auction_sources = self.source_discovery.discover_auction_sites(geographic_scope[0])
        gov_sources = self.source_discovery.discover_government_sources()
        
        all_sources = auction_sources + gov_sources
        filtered_sources = [
            s for s in all_sources 
            if s.confidence >= min_confidence
        ][:max_sources]
        
        # Use auction-specific hunting
        hunting_result = self.hunter.hunt_auction_sites()
        
        if hunting_result.success:
            # Combine discovered sources with hunting results
            combined_sources = list(set(filtered_sources + hunting_result.discovered_sources))
            
            return {
                'discovered_sources': combined_sources,
                'extracted_listings': hunting_result.extracted_listings,
                'success_rate': 1.0 if hunting_result.extracted_listings else 0.0,
                'total_sources_processed': len(combined_sources),
                'successful_extractions': 1 if hunting_result.extracted_listings else 0
            }
        else:
            return {
                'discovered_sources': filtered_sources,
                'extracted_listings': [],
                'success_rate': 0.0,
                'total_sources_processed': len(filtered_sources),
                'successful_extractions': 0
            }
    
    def _process_hunting_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Process and analyze hunting results"""
        
        extracted_listings = results.get('extracted_listings', [])
        discovered_sources = results.get('discovered_sources', [])
        
        if not extracted_listings:
            return {
                'extracted_listings': [],
                'success_rate': results.get('success_rate', 0.0),
                'confidence_score': 0.0,
                'summary': {
                    'total_listings': 0,
                    'total_sources': len(discovered_sources),
                    'by_brand': {},
                    'by_condition': {},
                    'by_price_range': {},
                    'qualification_levels': {}
                }
            }
        
        # Analyze listings
        brand_counts = {}
        condition_counts = {}
        price_ranges = {'under_10k': 0, '10k_50k': 0, '50k_100k': 0, 'over_100k': 0}
        qualification_levels = {'HOT': 0, 'REVIEW': 0, 'ARCHIVE': 0}
        
        total_value = 0
        confidence_scores = []
        
        for listing in extracted_listings:
            # Brand analysis
            brand = listing.get('brand', 'Unknown')
            brand_counts[brand] = brand_counts.get(brand, 0) + 1
            
            # Condition analysis
            condition = listing.get('condition', 'Unknown')
            condition_counts[condition] = condition_counts.get(condition, 0) + 1
            
            # Price analysis
            price = listing.get('asking_price', 0)
            if price > 0:
                total_value += price
                if price < 10000:
                    price_ranges['under_10k'] += 1
                elif price < 50000:
                    price_ranges['10k_50k'] += 1
                elif price < 100000:
                    price_ranges['50k_100k'] += 1
                else:
                    price_ranges['over_100k'] += 1
            
            # Qualification level
            qual_level = listing.get('qualification_level', 'ARCHIVE')
            qualification_levels[qual_level] = qualification_levels.get(qual_level, 0) + 1
            
            # Confidence tracking
            if 'discovery_confidence' in listing:
                confidence_scores.append(listing['discovery_confidence'])
        
        # Calculate metrics
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        avg_price = total_value / len(extracted_listings) if extracted_listings else 0
        
        summary = {
            'total_listings': len(extracted_listings),
            'total_sources': len(discovered_sources),
            'by_brand': dict(sorted(brand_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            'by_condition': condition_counts,
            'by_price_range': price_ranges,
            'qualification_levels': qualification_levels,
            'average_price': avg_price,
            'total_value': total_value,
            'high_value_listings': sum(1 for p in [l.get('asking_price', 0) for l in extracted_listings] if p > 50000)
        }
        
        return {
            'extracted_listings': extracted_listings,
            'success_rate': results.get('success_rate', 0.0),
            'confidence_score': avg_confidence,
            'summary': summary
        }
    
    def get_hunting_strategies(self) -> List[str]:
        """Get available hunting strategies"""
        return list(self.hunting_strategies.keys())
    
    def get_session_summary(self, session: HuntingSession) -> str:
        """Generate human-readable session summary"""
        
        summary = f"""
🎯 Hunting Session Summary
========================
Session ID: {session.session_id}
Strategy: {session.hunting_strategy}
Duration: {session.total_processing_time:.1f} seconds
Geographic Scope: {session.geographic_scope}

📊 Results
----------
Sources Discovered: {len(session.discovered_sources)}
Listings Extracted: {len(session.extracted_listings)}
Success Rate: {session.success_rate:.1%}
Confidence Score: {session.confidence_score:.2f}

🏆 Top Brands
------------
"""
        
        if session.results_summary.get('by_brand'):
            for brand, count in list(session.results_summary['by_brand'].items())[:5]:
                summary += f"{brand}: {count} listings\n"
        
        summary += f"""
💰 Price Analysis
----------------
Average Price: ${session.results_summary.get('average_price', 0):,.0f}
Total Value: ${session.results_summary.get('total_value', 0):,.0f}
High-Value Listings (>$50k): {session.results_summary.get('high_value_listings', 0)}

🎯 Qualification Levels
----------------------
"""
        
        if session.results_summary.get('qualification_levels'):
            for level, count in session.results_summary['qualification_levels'].items():
                summary += f"{level}: {count} listings\n"
        
        return summary
