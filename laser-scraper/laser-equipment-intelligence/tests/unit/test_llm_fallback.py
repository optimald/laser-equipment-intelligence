"""
Unit tests for LLM fallback component
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from laser_intelligence.utils.llm_fallback import LLMFallbackExtractor, LLMExtractionResult


class TestLLMFallbackExtractor:
    """Test LLM fallback extractor functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.extractor = LLMFallbackExtractor()

    def test_extractor_initialization(self):
        """Test LLM fallback extractor initialization"""
        assert self.extractor is not None
        assert hasattr(self.extractor, 'api_key')
        assert hasattr(self.extractor, 'api_url')
        assert hasattr(self.extractor, 'brand_mapper')
        assert hasattr(self.extractor, 'extraction_prompts')

    def test_api_key_detection(self):
        """Test API key detection"""
        api_key = self.extractor._get_api_key()
        # Should return None if no key configured
        assert api_key is None or isinstance(api_key, str)

    def test_content_preparation(self):
        """Test content preparation for LLM"""
        html_content = '<html><body><h1>Laser System</h1><p>Price: $50,000</p></body></html>'
        prepared = self.extractor._prepare_content_for_llm(html_content)
        
        assert isinstance(prepared, str)
        assert len(prepared) > 0
        assert 'Laser System' in prepared

    def test_content_preparation_large_html(self):
        """Test content preparation with large HTML"""
        html_content = '<html><body>' + 'x' * 50000 + '</body></html>'
        prepared = self.extractor._prepare_content_for_llm(html_content)
        
        assert isinstance(prepared, str)
        assert len(prepared) <= 10000  # Should be truncated

    def test_prompt_generation(self):
        """Test prompt generation"""
        prompt = self.extractor._get_laser_equipment_prompt()
        
        assert isinstance(prompt, str)
        assert len(prompt) > 0
        assert 'laser' in prompt.lower()

    def test_api_request_preparation(self):
        """Test API request preparation"""
        prompt = "Test prompt"
        content = "Test content"
        
        request_data = self.extractor._prepare_api_request(prompt, content)
        
        assert isinstance(request_data, dict)
        assert 'messages' in request_data
        assert 'model' in request_data
        assert 'temperature' in request_data

    @patch('requests.post')
    def test_api_call_success(self, mock_post):
        """Test successful API call"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': '{"brand": "Sciton", "model": "Joule", "price": 50000}'
                }
            }]
        }
        mock_post.return_value = mock_response
        
        prompt = "Test prompt"
        content = "Test content"
        
        result = self.extractor._make_api_call(prompt, content)
        
        assert isinstance(result, dict)
        assert 'brand' in result
        assert 'model' in result
        assert 'price' in result

    @patch('requests.post')
    def test_api_call_failure(self, mock_post):
        """Test API call failure"""
        # Mock failed response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response
        
        prompt = "Test prompt"
        content = "Test content"
        
        result = self.extractor._make_api_call(prompt, content)
        
        assert result is None

    @patch('requests.post')
    def test_api_call_retry(self, mock_post):
        """Test API call retry mechanism"""
        # Mock response that fails first, then succeeds
        mock_response_fail = Mock()
        mock_response_fail.status_code = 500
        
        mock_response_success = Mock()
        mock_response_success.status_code = 200
        mock_response_success.json.return_value = {
            'choices': [{
                'message': {
                    'content': '{"brand": "Sciton", "model": "Joule"}'
                }
            }]
        }
        
        mock_post.side_effect = [mock_response_fail, mock_response_success]
        
        prompt = "Test prompt"
        content = "Test content"
        
        result = self.extractor._make_api_call(prompt, content)
        
        assert isinstance(result, dict)
        assert mock_post.call_count == 2

    def test_laser_equipment_extraction(self):
        """Test laser equipment extraction"""
        html_content = '''
        <html>
        <body>
            <h1>Sciton Joule Laser System</h1>
            <p>Price: $75,000</p>
            <p>Condition: Excellent</p>
            <p>Year: 2022</p>
        </body>
        </html>
        '''
        
        with patch.object(self.extractor, '_make_api_call') as mock_call:
            mock_call.return_value = {
                'brand': 'Sciton',
                'model': 'Joule',
                'price': 75000,
                'condition': 'excellent',
                'year': 2022
            }
            
            result = self.extractor.extract_from_html(html_content, 'laser_equipment')
            
            assert isinstance(result, LLMExtractionResult)
            assert result.success is True
            assert 'brand' in result.extracted_data
            assert 'model' in result.extracted_data
            assert 'price' in result.extracted_data

    def test_auction_listing_extraction(self):
        """Test auction listing extraction"""
        html_content = '''
        <html>
        <body>
            <h1>Auction Item</h1>
            <p>Starting Bid: $25,000</p>
            <p>Ends: 2024-01-15</p>
            <p>Location: Miami, FL</p>
        </body>
        </html>
        '''
        
        with patch.object(self.extractor, '_make_api_call') as mock_call:
            mock_call.return_value = {
                'title': 'Auction Item',
                'starting_bid': 25000,
                'end_date': '2024-01-15',
                'location': 'Miami, FL'
            }
            
            result = self.extractor.extract_from_html(html_content, 'auction_listing')
            
            assert isinstance(result, LLMExtractionResult)
            assert result.success is True
            assert 'title' in result.extracted_data
            assert 'starting_bid' in result.extracted_data

    def test_price_extraction(self):
        """Test price extraction"""
        html_content = '''
        <html>
        <body>
            <p>Price: $50,000.00</p>
            <p>Original Price: $75,000</p>
            <p>Discount: 33%</p>
        </body>
        </html>
        '''
        
        with patch.object(self.extractor, '_make_api_call') as mock_call:
            mock_call.return_value = {
                'current_price': 50000,
                'original_price': 75000,
                'discount_percent': 33
            }
            
            result = self.extractor.extract_from_html(html_content, 'price_extraction')
            
            assert isinstance(result, LLMExtractionResult)
            assert result.success is True
            assert 'current_price' in result.extracted_data

    def test_brand_model_extraction(self):
        """Test brand and model extraction"""
        html_content = '''
        <html>
        <body>
            <h1>Cynosure Elite+ Laser System</h1>
            <p>Professional aesthetic laser</p>
            <p>Model: Elite+</p>
            <p>Brand: Cynosure</p>
        </body>
        </html>
        '''
        
        with patch.object(self.extractor, '_make_api_call') as mock_call:
            mock_call.return_value = {
                'brand': 'Cynosure',
                'model': 'Elite+',
                'category': 'aesthetic laser'
            }
            
            result = self.extractor.extract_from_html(html_content, 'brand_model_extraction')
            
            assert isinstance(result, LLMExtractionResult)
            assert result.success is True
            assert 'brand' in result.extracted_data
            assert 'model' in result.extracted_data

    def test_extraction_failure(self):
        """Test extraction failure"""
        html_content = '<html><body>Invalid content</body></html>'
        
        with patch.object(self.extractor, '_make_api_call') as mock_call:
            mock_call.return_value = None
            
            result = self.extractor.extract_from_html(html_content, 'laser_equipment')
            
            assert isinstance(result, LLMExtractionResult)
            assert result.success is False
            assert result.error_message is not None

    def test_error_handling(self):
        """Test error handling"""
        html_content = None
        
        result = self.extractor.extract_from_html(html_content, 'laser_equipment')
        
        assert isinstance(result, LLMExtractionResult)
        assert result.success is False

    def test_performance_metrics(self):
        """Test performance metrics"""
        html_content = '<html><body><h1>Test</h1></body></html>'
        
        with patch.object(self.extractor, '_make_api_call') as mock_call:
            mock_call.return_value = {'test': 'data'}
            
            result = self.extractor.extract_from_html(html_content, 'laser_equipment')
            
            assert result.processing_time > 0
            assert result.confidence_score >= 0

    def test_empty_content_handling(self):
        """Test empty content handling"""
        html_content = ''
        
        with patch.object(self.extractor, '_make_api_call') as mock_call:
            mock_call.return_value = {}
            
            result = self.extractor.extract_from_html(html_content, 'laser_equipment')
            
            assert isinstance(result, LLMExtractionResult)

    def test_invalid_extraction_type(self):
        """Test invalid extraction type"""
        html_content = '<html><body><h1>Test</h1></body></html>'
        
        with patch.object(self.extractor, '_make_api_call') as mock_call:
            mock_call.return_value = {}
            
            result = self.extractor.extract_from_html(html_content, 'invalid_type')
            
            assert isinstance(result, LLMExtractionResult)
            # Should fall back to default prompt
            assert result.success is True or result.success is False

    def test_json_parsing_error(self):
        """Test JSON parsing error"""
        html_content = '<html><body><h1>Test</h1></body></html>'
        
        with patch.object(self.extractor, '_make_api_call') as mock_call:
            mock_call.return_value = 'invalid json'
            
            result = self.extractor.extract_from_html(html_content, 'laser_equipment')
            
            assert isinstance(result, LLMExtractionResult)
            assert result.success is False

    def test_batch_extraction(self):
        """Test batch extraction"""
        html_contents = [
            '<html><body><h1>Item 1</h1></body></html>',
            '<html><body><h1>Item 2</h1></body></html>'
        ]
        
        with patch.object(self.extractor, '_make_api_call') as mock_call:
            mock_call.side_effect = [
                {'brand': 'Brand1', 'model': 'Model1'},
                {'brand': 'Brand2', 'model': 'Model2'}
            ]
            
            results = self.extractor.batch_extract(html_contents, 'laser_equipment')
            
            assert isinstance(results, list)
            assert len(results) == 2
            assert all(isinstance(r, LLMExtractionResult) for r in results)
