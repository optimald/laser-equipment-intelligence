"""
Data normalization pipeline for laser equipment listings
"""

import re
import time
from typing import Dict, Any, Optional
from scrapy import Item, Field
from laser_intelligence.utils.brand_mapping import BrandMapper
from laser_intelligence.utils.price_analysis import PriceAnalyzer


class LaserListingItem(Item):
    """Scrapy item for laser equipment listings"""
    
    # Core identification
    id = Field()
    source_id = Field()
    source_url = Field()
    source_listing_id = Field()
    discovered_at = Field()
    
    # Item details
    brand = Field()
    model = Field()
    modality = Field()
    title_raw = Field()
    description_raw = Field()
    images = Field()
    condition = Field()
    serial_number = Field()
    year = Field()
    hours = Field()
    accessories = Field()
    
    # Location
    location_city = Field()
    location_state = Field()
    location_country = Field()
    lat = Field()
    lng = Field()
    
    # Commercial details
    asking_price = Field()
    reserve_price = Field()
    buy_now_price = Field()
    auction_start_ts = Field()
    auction_end_ts = Field()
    seller_name = Field()
    seller_contact = Field()
    
    # Enrichment
    est_wholesale = Field()
    est_resale = Field()
    refurb_cost_estimate = Field()
    freight_estimate = Field()
    margin_estimate = Field()
    margin_pct = Field()
    
    # Scoring
    score_margin = Field()
    score_urgency = Field()
    score_condition = Field()
    score_reputation = Field()
    score_overall = Field()
    qualification_level = Field()
    
    # Status
    ingest_status = Field()
    dedupe_key = Field()
    pipeline_status = Field()
    notes = Field()
    
    # Scraping metadata
    scraped_with_proxy = Field()
    evasion_score = Field()
    scraped_legally = Field()
    block_warnings = Field()


class NormalizationPipeline:
    """Normalize and clean scraped data"""
    
    def __init__(self):
        self.brand_mapper = BrandMapper()
        self.price_analyzer = PriceAnalyzer()
        self.processed_count = 0
        
    def process_item(self, item: LaserListingItem, spider) -> LaserListingItem:
        """Process and normalize item data"""
        try:
            # Normalize brand and model
            item['brand'] = self._normalize_brand(item.get('brand'))
            item['model'] = self._normalize_model(item.get('model'), item.get('brand'))
            item['modality'] = self._map_modality(item.get('brand'), item.get('model'))
            
            # Normalize condition
            item['condition'] = self._normalize_condition(item.get('condition'))
            
            # Normalize pricing
            item['asking_price'] = self._normalize_price(item.get('asking_price'))
            item['reserve_price'] = self._normalize_price(item.get('reserve_price'))
            item['buy_now_price'] = self._normalize_price(item.get('buy_now_price'))
            
            # Normalize location
            self._normalize_location(item)
            
            # Extract serial number
            self._extract_serial_number(item)
            
            # Normalize accessories
            item['accessories'] = self._normalize_accessories(item.get('accessories'), item.get('description_raw'))
            
            # Normalize usage data
            item['hours'] = self._normalize_hours(item.get('hours'), item.get('description_raw'))
            item['year'] = self._normalize_year(item.get('year'), item.get('description_raw'))
            
            # Generate deduplication key
            item['dedupe_key'] = self._generate_dedupe_key(item)
            
            # Set metadata
            item['discovered_at'] = time.time()
            item['ingest_status'] = 'new'
            item['pipeline_status'] = 'new'
            item['scraped_legally'] = True
            
            self.processed_count += 1
            spider.logger.info(f'Normalized item {self.processed_count}: {item.get("brand")} {item.get("model")}')
            
            return item
            
        except Exception as e:
            spider.logger.error(f'Error normalizing item: {e}')
            return item
    
    def _normalize_brand(self, raw_brand: str) -> str:
        """Normalize brand name"""
        if not raw_brand:
            return ''
        return self.brand_mapper.normalize_brand(raw_brand)
    
    def _normalize_model(self, raw_model: str, brand: str) -> str:
        """Normalize model name"""
        if not raw_model:
            return ''
        return self.brand_mapper.normalize_model(raw_model, brand)
    
    def _map_modality(self, brand: str, model: str) -> str:
        """Map brand/model to modality"""
        if not brand or not model:
            return 'Laser Equipment'
        return self.brand_mapper.map_modality(brand, model)
    
    def _normalize_condition(self, raw_condition: str) -> str:
        """Normalize equipment condition"""
        if not raw_condition:
            return 'unknown'
        
        condition_mapping = {
            'new': 'new',
            'like new': 'new',
            'excellent': 'excellent',
            'very good': 'good',
            'good': 'good',
            'fair': 'fair',
            'poor': 'poor',
            'used': 'used',
            'refurbished': 'refurbished',
            'refurb': 'refurbished',
            'reconditioned': 'refurbished',
            'as-is': 'as-is',
            'as is': 'as-is',
            'for parts': 'as-is',
            'not working': 'as-is',
        }
        
        cleaned = raw_condition.lower().strip()
        return condition_mapping.get(cleaned, 'unknown')
    
    def _normalize_price(self, raw_price: str) -> Optional[float]:
        """Normalize price to USD float"""
        if not raw_price:
            return None
        
        try:
            price_str = str(raw_price).lower().strip()
            
            # Handle K suffix (thousands)
            if 'k' in price_str or 'thousand' in price_str:
                # Extract number and multiply by 1000
                number_match = re.search(r'[\d,]+\.?\d*', price_str)
                if number_match:
                    number = float(number_match.group().replace(',', ''))
                    return number * 1000
            
            # Remove currency symbols and commas
            cleaned = re.sub(r'[^\d.,]', '', price_str)
            cleaned = cleaned.replace(',', '')
            
            # Handle decimal points
            if '.' in cleaned:
                parts = cleaned.split('.')
                if len(parts) == 2 and len(parts[1]) <= 2:
                    # Valid decimal format
                    return float(cleaned)
                else:
                    # Remove all dots except the last one
                    cleaned = cleaned.replace('.', '')
            
            return float(cleaned) if cleaned else None
            
        except (ValueError, TypeError):
            return None
    
    def _normalize_location(self, item: LaserListingItem):
        """Normalize location data"""
        # Clean city, state, country
        if item.get('location_city'):
            item['location_city'] = item['location_city'].strip().title()
        
        if item.get('location_state'):
            state = item['location_state'].strip()
            # Convert full state names to abbreviations
            state_abbreviations = {
                'california': 'CA',
                'florida': 'FL',
                'texas': 'TX',
                'new york': 'NY',
                'illinois': 'IL',
                'pennsylvania': 'PA',
                'ohio': 'OH',
                'georgia': 'GA',
                'north carolina': 'NC',
                'michigan': 'MI',
                'new jersey': 'NJ',
                'virginia': 'VA',
                'washington': 'WA',
                'arizona': 'AZ',
                'massachusetts': 'MA',
                'tennessee': 'TN',
                'indiana': 'IN',
                'missouri': 'MO',
                'maryland': 'MD',
                'wisconsin': 'WI',
                'colorado': 'CO',
                'minnesota': 'MN',
                'south carolina': 'SC',
                'alabama': 'AL',
                'louisiana': 'LA',
                'kentucky': 'KY',
                'oregon': 'OR',
                'oklahoma': 'OK',
                'connecticut': 'CT',
                'utah': 'UT',
                'iowa': 'IA',
                'nevada': 'NV',
                'arkansas': 'AR',
                'mississippi': 'MS',
                'kansas': 'KS',
                'new mexico': 'NM',
                'nebraska': 'NE',
                'west virginia': 'WV',
                'idaho': 'ID',
                'hawaii': 'HI',
                'new hampshire': 'NH',
                'maine': 'ME',
                'montana': 'MT',
                'rhode island': 'RI',
                'delaware': 'DE',
                'south dakota': 'SD',
                'north dakota': 'ND',
                'alaska': 'AK',
                'vermont': 'VT',
                'wyoming': 'WY'
            }
            item['location_state'] = state_abbreviations.get(state.lower(), state.upper())
        
        if item.get('location_country'):
            country = item['location_country'].strip()
            # Convert country names to standard abbreviations
            country_abbreviations = {
                'united states': 'USA',
                'usa': 'USA',
                'us': 'USA',
                'united states of america': 'USA',
                'canada': 'CAN',
                'mexico': 'MEX',
                'united kingdom': 'UK',
                'uk': 'UK',
                'germany': 'DEU',
                'france': 'FRA',
                'italy': 'ITA',
                'spain': 'ESP',
                'australia': 'AUS',
                'japan': 'JPN',
                'china': 'CHN',
                'india': 'IND',
                'brazil': 'BRA',
                'russia': 'RUS'
            }
            item['location_country'] = country_abbreviations.get(country.lower(), country.upper())
        
        # TODO: Add geocoding for lat/lng coordinates
    
    def _extract_serial_number(self, item: LaserListingItem):
        """Extract serial number from description"""
        description = item.get('description_raw', '')
        if not description:
            return
        
        # Look for common serial number patterns
        serial_patterns = [
            r'serial[:\s#]*([A-Z0-9\-]{6,})',
            r'sn[:\s#]*([A-Z0-9\-]{6,})',
            r's/n[:\s#]*([A-Z0-9\-]{6,})',
            r'serial number[:\s#]*([A-Z0-9\-]{6,})',
            r'#([A-Z0-9\-]{6,})',  # Generic number pattern
        ]
        
        for pattern in serial_patterns:
            match = re.search(pattern, description, re.IGNORECASE)
            if match:
                item['serial_number'] = match.group(1).strip()
                break
    
    def _normalize_accessories(self, raw_accessories: str, description: str = None) -> list:
        """Normalize accessories list"""
        # Try raw_accessories first
        if raw_accessories:
            if isinstance(raw_accessories, str):
                # Split by common delimiters
                accessories = re.split(r'[,;|]', raw_accessories)
                return [acc.strip() for acc in accessories if acc.strip()]
            return raw_accessories if isinstance(raw_accessories, list) else []
        
        # If no raw_accessories, try to extract from description
        if description:
            try:
                # Look for accessories patterns
                accessories_patterns = [
                    r'includes?[:\s]*([^.]+)',
                    r'accessories?[:\s]*([^.]+)',
                    r'with[:\s]*([^.]+)',
                    r'handpieces?[:\s]*([^.]+)',
                ]
                
                for pattern in accessories_patterns:
                    match = re.search(pattern, description, re.IGNORECASE)
                    if match:
                        accessories_text = match.group(1)
                        accessories = re.split(r'[,;|]', accessories_text)
                        return [acc.strip() for acc in accessories if acc.strip()]
            except (ValueError, TypeError):
                pass
        
        return []
    
    def _normalize_hours(self, raw_hours: str, description: str = None) -> Optional[int]:
        """Normalize usage hours"""
        # Try raw_hours first
        if raw_hours:
            try:
                # Extract numbers from text
                numbers = re.findall(r'\d+', str(raw_hours))
                if numbers:
                    return int(numbers[0])
            except (ValueError, TypeError):
                pass
        
        # If no raw_hours, try to extract from description
        if description:
            try:
                # Look for hours patterns
                hours_patterns = [
                    r'(\d+)\s*hours?',
                    r'(\d+)\s*hrs?',
                    r'hours?[:\s]*(\d+)',
                    r'usage[:\s]*(\d+)\s*hours?',
                ]
                
                for pattern in hours_patterns:
                    match = re.search(pattern, description, re.IGNORECASE)
                    if match:
                        return int(match.group(1))
            except (ValueError, TypeError):
                pass
        
        return None
    
    def _normalize_year(self, raw_year: str, description: str = None) -> Optional[int]:
        """Normalize equipment year"""
        # Try raw_year first
        if raw_year:
            try:
                # Extract 4-digit year
                years = re.findall(r'\b(19|20)\d{2}\b', str(raw_year))
                if years:
                    year = int(years[0])
                    # Validate reasonable year range
                    if 1990 <= year <= 2025:
                        return year
            except (ValueError, TypeError):
                pass
        
        # If no raw_year, try to extract from description
        if description:
            try:
                # Look for year patterns
                year_patterns = [
                    r'year[:\s]*(\d{4})',
                    r'manufactured[:\s]*(\d{4})',
                    r'model[:\s]*(\d{4})',
                    r'(\d{4})\s*year',
                    r'(\d{4})\s*model',
                ]
                
                for pattern in year_patterns:
                    match = re.search(pattern, description, re.IGNORECASE)
                    if match:
                        year = int(match.group(1))
                        # Validate year range
                        if 1990 <= year <= 2025:
                            return year
            except (ValueError, TypeError):
                pass
        
        return None
    
    def _generate_dedupe_key(self, item: LaserListingItem) -> str:
        """Generate deduplication key"""
        key_parts = [
            item.get('brand', ''),
            item.get('model', ''),
            item.get('serial_number', ''),
            item.get('source_url', ''),
            str(item.get('asking_price', '')),
        ]
        
        # Create hash of key parts
        key_string = '|'.join(str(part) for part in key_parts)
        return str(hash(key_string))
    
    def close_spider(self, spider):
        """Called when spider closes"""
        spider.logger.info(f'NormalizationPipeline processed {self.processed_count} items')
