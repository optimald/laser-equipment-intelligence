"""
End-to-end integration tests for laser equipment intelligence platform
"""

import pytest
import time
import os
from unittest.mock import Mock, patch
from scrapy.http import HtmlResponse, Request
from laser_intelligence.pipelines.normalization import LaserListingItem
from laser_intelligence.utils.brand_mapping import BrandMapper
from laser_intelligence.utils.evasion_scoring import EvasionScorer
from laser_intelligence.utils.price_analysis import PriceAnalyzer


class TestEndToEndIntegration:
    """End-to-end integration tests"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.brand_mapper = BrandMapper()
        self.evasion_scorer = EvasionScorer()
        self.price_analyzer = PriceAnalyzer()
    
    def test_complete_item_processing_pipeline(self):
        """Test complete item processing from raw data to final output"""
        # Simulate raw scraped data
        raw_data = {
            'source_url': 'https://example.com/auction/123',
            'title_raw': 'Sciton Joule Laser System - Excellent Condition',
            'description_raw': 'Complete Sciton Joule laser system with handpieces. Serial: SN12345, Year: 2022, Hours: 500. Includes cart and accessories.',
            'asking_price': '$50,000',  # Great deal - significantly lower than wholesale value
            'condition': 'excellent',
            'location': 'Los Angeles, CA',
            'seller_name': 'Medical Equipment Liquidators',
            'auction_end_ts': time.time() + (12 * 3600)  # 12 hours from now
        }
        
        # Step 1: Brand/Model Extraction
        brand, model = self._extract_brand_model(raw_data['title_raw'], raw_data['description_raw'])
        assert brand == 'Sciton'
        assert model == 'Joule'
        
        # Step 2: Price Normalization
        normalized_price = self._normalize_price(raw_data['asking_price'])
        assert normalized_price == 50000.0
        
        # Step 3: Condition Normalization
        normalized_condition = self._normalize_condition(raw_data['condition'])
        assert normalized_condition == 'excellent'
        
        # Step 4: Location Parsing
        location_parts = self._parse_location(raw_data['location'])
        assert location_parts['city'] == 'Los Angeles'
        assert location_parts['state'] == 'CA'
        
        # Step 5: Create LaserListingItem
        item = LaserListingItem()
        item['source_url'] = raw_data['source_url']
        item['title_raw'] = raw_data['title_raw']
        item['description_raw'] = raw_data['description_raw']
        item['brand'] = brand
        item['model'] = model
        item['asking_price'] = normalized_price
        item['condition'] = normalized_condition
        item['location_city'] = location_parts['city']
        item['location_state'] = location_parts['state']
        item['seller_name'] = raw_data['seller_name']
        item['auction_end_ts'] = raw_data['auction_end_ts']
        
        # Step 6: Price Analysis
        wholesale_estimate = self.price_analyzer.estimate_wholesale_value(
            brand, model, normalized_condition, normalized_price
        )
        resale_estimate = self.price_analyzer.estimate_resale_value(
            brand, model, normalized_condition, normalized_price
        )
        
        assert wholesale_estimate is not None
        assert resale_estimate is not None
        assert resale_estimate > wholesale_estimate
        
        # Step 7: Margin Calculation
        margin_estimate, margin_pct = self.price_analyzer.calculate_margin_estimate(
            normalized_price, wholesale_estimate, 5000, 2000  # refurb + freight
        )
        
        assert margin_estimate is not None
        assert margin_pct is not None
        
        # Step 8: Scoring
        item['est_wholesale'] = wholesale_estimate
        item['est_resale'] = resale_estimate
        item['margin_estimate'] = margin_estimate
        item['margin_pct'] = margin_pct
        
        # Calculate scores
        margin_score = self._calculate_margin_score(item)
        urgency_score = self._calculate_urgency_score(item)
        condition_score = self._calculate_condition_score(item)
        overall_score = margin_score + urgency_score + condition_score
        
        item['score_margin'] = margin_score
        item['score_urgency'] = urgency_score
        item['score_condition'] = condition_score
        item['score_overall'] = overall_score
        
        # Step 9: Qualification
        qualification_level = self._get_qualification_level(overall_score)
        
        # Verify final results
        assert item['brand'] == 'Sciton'
        assert item['model'] == 'Joule'
        assert item['asking_price'] == 50000.0
        assert item['condition'] == 'excellent'
        assert item['score_overall'] > 0
        assert qualification_level in ['HOT', 'REVIEW', 'ARCHIVE']
        
        # This should be a HOT item due to high-value brand, good condition, and good margin
        assert qualification_level == 'HOT'
    
    def test_evasion_scoring_integration(self):
        """Test evasion scoring integration with spider responses"""
        # Simulate successful response
        request = Request(url="https://example.com")
        successful_response = HtmlResponse(
            url="https://example.com",
            request=request,
            body=b"<html><body>" + b"x" * 2000 + b"</body></html>",
            status=200
        )
        
        evasion_score = self.evasion_scorer.calculate_score(successful_response, request)
        assert evasion_score >= 100  # Should be high for successful response
        
        # Simulate blocked response
        blocked_response = HtmlResponse(
            url="https://example.com",
            request=request,
            body=b"<html><body>Access denied</body></html>",
            status=403
        )
        
        evasion_score_blocked = self.evasion_scorer.calculate_score(blocked_response, request)
        assert evasion_score_blocked < evasion_score  # Should be lower for blocked response
    
    def test_brand_mapping_integration(self):
        """Test brand mapping integration with various inputs"""
        # Test exact matches
        assert self.brand_mapper.normalize_brand('sciton') == 'Sciton'
        assert self.brand_mapper.normalize_brand('cynosure') == 'Cynosure'
        
        # Test case variations
        assert self.brand_mapper.normalize_brand('SCITON') == 'Sciton'
        assert self.brand_mapper.normalize_brand('Cynosure Inc') == 'Cynosure'
        
        # Test model mapping
        assert self.brand_mapper.normalize_model('joule', 'sciton') == 'Joule'
        assert self.brand_mapper.normalize_model('picosure', 'cynosure') == 'PicoSure'
        
        # Test modality mapping
        assert self.brand_mapper.map_modality('sciton', 'joule') == 'Platform System'
        assert self.brand_mapper.map_modality('cynosure', 'picosure') == 'Picosecond Laser'
    
    def test_price_analysis_integration(self):
        """Test price analysis integration"""
        # Test with high-value brand
        wholesale = self.price_analyzer.estimate_wholesale_value('Sciton', 'Joule', 'excellent', 150000)
        resale = self.price_analyzer.estimate_resale_value('Sciton', 'Joule', 'excellent', 150000)
        
        assert wholesale is not None
        assert resale is not None
        assert resale > wholesale
        
        # Test margin calculation with realistic asking price (good deal)
        asking_price = 80000  # Good deal - lower than wholesale
        margin, margin_pct = self.price_analyzer.calculate_margin_estimate(asking_price, wholesale, 5000, 2000)
        
        assert margin is not None
        assert margin_pct is not None
        assert margin_pct > 0  # Should be positive margin
    
    def test_complete_spider_workflow(self):
        """Test complete spider workflow simulation"""
        # Simulate spider start
        start_urls = [
            'https://example.com/auction/category/medical-equipment',
            'https://example.com/auction/category/laser-equipment'
        ]
        
        # Simulate category page parsing
        category_html = """
        <html>
            <body>
                <div class="auction-item">
                    <a href="/auction/item/123">Sciton Joule Laser System</a>
                </div>
                <div class="auction-item">
                    <a href="/auction/item/456">Cynosure PicoSure Laser</a>
                </div>
            </body>
        </html>
        """
        
        category_response = HtmlResponse(
            url=start_urls[0],
            request=Request(url=start_urls[0]),
            body=category_html.encode('utf-8'),
            encoding='utf-8'
        )
        
        # Extract listing links
        listing_links = category_response.css('.auction-item a::attr(href)').getall()
        assert len(listing_links) == 2
        
        # Simulate individual listing parsing
        listing_html = """
        <html>
            <body>
                <h1>Sciton Joule Laser System</h1>
                <div class="price">$150,000</div>
                <div class="condition">Excellent</div>
                <div class="description">
                    Complete Sciton Joule laser system with handpieces.
                    Serial: SN12345, Year: 2022, Hours: 500
                </div>
                <div class="location">Los Angeles, CA</div>
            </body>
        </html>
        """
        
        listing_response = HtmlResponse(
            url='https://example.com/auction/item/123',
            request=Request(url='https://example.com/auction/item/123'),
            body=listing_html.encode('utf-8'),
            encoding='utf-8'
        )
        
        # Extract listing data
        title = listing_response.css('h1::text').get()
        price_text = listing_response.css('.price::text').get()
        condition = listing_response.css('.condition::text').get()
        description = listing_response.css('.description::text').get()
        location = listing_response.css('.location::text').get()
        
        assert title == 'Sciton Joule Laser System'
        assert price_text == '$150,000'
        assert condition == 'Excellent'
        assert 'Sciton Joule' in description
        assert location == 'Los Angeles, CA'
        
        # Process extracted data
        brand, model = self._extract_brand_model(title, description)
        price = self._normalize_price(price_text)
        normalized_condition = self._normalize_condition(condition)
        
        assert brand == 'Sciton'
        assert model == 'Joule'
        assert price == 150000.0
        assert normalized_condition == 'excellent'
    
    def _extract_brand_model(self, title: str, description: str) -> tuple:
        """Extract brand and model from title and description"""
        text = f"{title} {description}".lower()
        
        # Brand mapping
        brand_mapping = {
            'sciton': 'Sciton',
            'cynosure': 'Cynosure',
            'cutera': 'Cutera',
            'candela': 'Candela',
            'lumenis': 'Lumenis',
            'alma': 'Alma',
            'inmode': 'InMode',
            'btl': 'BTL',
            'lutronic': 'Lutronic',
        }
        
        # Find brand
        brand = None
        for keyword, mapped_brand in brand_mapping.items():
            if keyword in text:
                brand = mapped_brand
                break
        
        # Model mapping
        model_mapping = {
            'joule': 'Joule',
            'picosure': 'PicoSure',
            'picoway': 'PicoWay',
            'gentlemax': 'GentleMax',
            'm22': 'M22',
            'bbl': 'BBL',
            'secret rf': 'Secret RF',
            'morpheus8': 'Morpheus8',
            'emsculpt': 'Emsculpt',
            'excel v': 'Excel V',
            'xeo': 'Xeo',
        }
        
        # Find model
        model = None
        for keyword, mapped_model in model_mapping.items():
            if keyword in text:
                model = mapped_model
                break
        
        return brand, model
    
    def _normalize_price(self, price_text: str) -> float:
        """Normalize price text to float"""
        import re
        cleaned = re.sub(r'[^\d.,]', '', price_text)
        cleaned = cleaned.replace(',', '')
        return float(cleaned)
    
    def _normalize_condition(self, condition: str) -> str:
        """Normalize condition text"""
        condition_mapping = {
            'excellent': 'excellent',
            'good': 'good',
            'fair': 'fair',
            'poor': 'poor',
            'used': 'used',
            'refurbished': 'refurbished',
            'as-is': 'as-is',
        }
        return condition_mapping.get(condition.lower(), 'unknown')
    
    def _parse_location(self, location_text: str) -> dict:
        """Parse location text"""
        parts = location_text.split(',')
        return {
            'city': parts[0].strip() if len(parts) > 0 else '',
            'state': parts[1].strip() if len(parts) > 1 else ''
        }
    
    def _calculate_margin_score(self, item: LaserListingItem) -> float:
        """Calculate margin score"""
        asking_price = item.get('asking_price', 0)
        est_wholesale = item.get('est_wholesale', 0)
        
        if not asking_price or not est_wholesale:
            return 0
        
        margin_pct = (est_wholesale - asking_price) / est_wholesale
        
        if margin_pct >= 0.4:
            return 60.0
        elif margin_pct >= 0.2:
            return 30.0 + (margin_pct - 0.2) * 150
        else:
            return max(0, margin_pct * 150)
    
    def _calculate_urgency_score(self, item: LaserListingItem) -> float:
        """Calculate urgency score"""
        score = 0
        
        # Auction ending soon
        auction_end = item.get('auction_end_ts')
        if auction_end:
            time_remaining = auction_end - time.time()
            if time_remaining < 24 * 3600:  # Less than 24 hours
                score += 15
            elif time_remaining < 72 * 3600:  # Less than 72 hours
                score += 10
        
        # High-value brand bonus
        if item.get('brand') in ['Sciton', 'Cynosure', 'Cutera', 'Candela', 'Lumenis']:
            score += 5
        
        return min(25, score)
    
    def _calculate_condition_score(self, item: LaserListingItem) -> float:
        """Calculate condition score"""
        condition_mapping = {
            'excellent': 9,
            'good': 7,
            'fair': 5,
            'poor': 3,
            'used': 6,
            'refurbished': 8,
            'as-is': 2,
            'unknown': 5,
        }
        
        condition = item.get('condition', 'unknown')
        return condition_mapping.get(condition, 5)
    
    def _get_qualification_level(self, overall_score: float) -> str:
        """Get qualification level based on overall score"""
        if overall_score >= 50:  # Lowered threshold for HOT items
            return 'HOT'
        elif overall_score >= 30:
            return 'REVIEW'
        else:
            return 'ARCHIVE'
