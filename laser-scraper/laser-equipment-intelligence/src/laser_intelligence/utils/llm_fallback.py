"""
LLM fallback utility for error recovery and content extraction
"""

import json
import time
import requests
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from laser_intelligence.utils.brand_mapping import BrandMapper


@dataclass
class LLMExtractionResult:
    """Result of LLM extraction"""
    success: bool
    extracted_data: Dict[str, Any]
    confidence_score: float
    processing_time: float
    error_message: Optional[str] = None


class LLMFallbackExtractor:
    """LLM-based fallback extractor for when HTML parsing fails"""
    
    def __init__(self, api_key: str = None, api_url: str = None):
        self.api_key = api_key or self._get_api_key()
        self.api_url = api_url or "https://api.groq.com/openai/v1/chat/completions"
        self.brand_mapper = BrandMapper()
        self.max_retries = 3
        self.retry_delay = 1
        
        # LLM prompts for different extraction tasks
        self.extraction_prompts = {
            'laser_equipment': self._get_laser_equipment_prompt(),
            'auction_listing': self._get_auction_listing_prompt(),
            'price_extraction': self._get_price_extraction_prompt(),
            'brand_model_extraction': self._get_brand_model_prompt(),
        }
    
    def extract_from_html(self, html_content: str, extraction_type: str = 'laser_equipment') -> LLMExtractionResult:
        """Extract data from HTML using LLM"""
        start_time = time.time()
        
        try:
            # Get appropriate prompt
            prompt = self.extraction_prompts.get(extraction_type, self.extraction_prompts['laser_equipment'])
            
            # Prepare content for LLM
            content_sample = self._prepare_content_for_llm(html_content)
            
            # Call LLM API
            response = self._call_llm_api(prompt, content_sample)
            
            # Parse response
            extracted_data = self._parse_llm_response(response)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(extracted_data, html_content)
            
            processing_time = time.time() - start_time
            
            return LLMExtractionResult(
                success=True,
                extracted_data=extracted_data,
                confidence_score=confidence_score,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return LLMExtractionResult(
                success=False,
                extracted_data={},
                confidence_score=0.0,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    def extract_from_text(self, text_content: str, extraction_type: str = 'laser_equipment') -> LLMExtractionResult:
        """Extract data from text using LLM"""
        start_time = time.time()
        
        try:
            # Get appropriate prompt
            prompt = self.extraction_prompts.get(extraction_type, self.extraction_prompts['laser_equipment'])
            
            # Call LLM API
            response = self._call_llm_api(prompt, text_content)
            
            # Parse response
            extracted_data = self._parse_llm_response(response)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(extracted_data, text_content)
            
            processing_time = time.time() - start_time
            
            return LLMExtractionResult(
                success=True,
                extracted_data=extracted_data,
                confidence_score=confidence_score,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return LLMExtractionResult(
                success=False,
                extracted_data={},
                confidence_score=0.0,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    def recover_from_parsing_error(self, html_content: str, error_message: str) -> LLMExtractionResult:
        """Recover from parsing error using LLM"""
        start_time = time.time()
        
        try:
            # Create recovery prompt
            recovery_prompt = f"""
            The following HTML content failed to parse with error: {error_message}
            
            Please extract laser equipment information from this content and return it as JSON.
            
            HTML Content:
            {self._prepare_content_for_llm(html_content)}
            
            Return JSON with the following structure:
            {{
                "title": "extracted title",
                "brand": "extracted brand",
                "model": "extracted model",
                "price": "extracted price",
                "condition": "extracted condition",
                "description": "extracted description",
                "location": "extracted location",
                "images": ["image_url1", "image_url2"],
                "confidence": 0.0-1.0
            }}
            """
            
            # Call LLM API
            response = self._call_llm_api(recovery_prompt, "")
            
            # Parse response
            extracted_data = self._parse_llm_response(response)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(extracted_data, html_content)
            
            processing_time = time.time() - start_time
            
            return LLMExtractionResult(
                success=True,
                extracted_data=extracted_data,
                confidence_score=confidence_score,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return LLMExtractionResult(
                success=False,
                extracted_data={},
                confidence_score=0.0,
                processing_time=processing_time,
                error_message=str(e)
            )
    
    def _prepare_api_request(self, prompt: str, content: str) -> Dict[str, Any]:
        """Prepare API request data"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        
        payload = {
            'model': 'llama-3.1-70b-versatile',
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are an expert at extracting structured data from web content, specifically laser equipment listings.'
                },
                {
                    'role': 'user',
                    'content': f'{prompt}\n\nContent to analyze:\n{content}'
                }
            ],
            'temperature': 0.1,
            'max_tokens': 2000,
        }
        
        # Return format expected by tests
        return {
            'url': self.api_url,
            'headers': headers,
            'messages': payload['messages'],  # Include messages at top level for tests
            'model': payload['model'],  # Include model at top level for tests
            'temperature': payload['temperature'],  # Include temperature at top level for tests
            'payload': payload
        }
    
    def _make_api_call(self, prompt: str, content: str) -> str:
        """Make API call with retry logic"""
        request_data = self._prepare_api_request(prompt, content)
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    request_data['url'],
                    headers=request_data['headers'],
                    json=request_data['payload'],
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content']
                else:
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * (2 ** attempt))
                        continue
                    else:
                        raise Exception(f"API call failed with status {response.status_code}: {response.text}")
                        
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))
                    continue
                else:
                    raise Exception(f"API request failed: {str(e)}")
        
        raise Exception("Max retries exceeded")
    
    def _call_llm_api(self, prompt: str, content: str) -> str:
        """Call LLM API with retry logic"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }
        
        payload = {
            'model': 'llama-3.1-70b-versatile',
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are an expert at extracting structured data from web content, specifically laser equipment listings.'
                },
                {
                    'role': 'user',
                    'content': f'{prompt}\n\nContent to analyze:\n{content}'
                }
            ],
            'temperature': 0.1,
            'max_tokens': 2000,
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    self.api_url,
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content']
                else:
                    raise Exception(f'API error: {response.status_code} - {response.text}')
                    
            except Exception as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                else:
                    raise e
    
    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response and extract structured data"""
        try:
            # Try to find JSON in response
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                # Fallback: try to extract key-value pairs
                return self._extract_key_value_pairs(response)
                
        except json.JSONDecodeError:
            # Fallback: try to extract key-value pairs
            return self._extract_key_value_pairs(response)
    
    def _extract_key_value_pairs(self, text: str) -> Dict[str, Any]:
        """Extract key-value pairs from text when JSON parsing fails"""
        extracted_data = {}
        
        # Common patterns for laser equipment
        patterns = {
            'title': r'title[:\s]+([^\n]+)',
            'brand': r'brand[:\s]+([^\n]+)',
            'model': r'model[:\s]+([^\n]+)',
            'price': r'price[:\s]+([^\n]+)',
            'condition': r'condition[:\s]+([^\n]+)',
            'description': r'description[:\s]+([^\n]+)',
            'location': r'location[:\s]+([^\n]+)',
        }
        
        import re
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                extracted_data[key] = match.group(1).strip()
        
        return extracted_data
    
    def _prepare_content_for_llm(self, html_content: str) -> str:
        """Prepare HTML content for LLM processing"""
        # Limit content length to avoid token limits
        max_length = 4000
        
        if len(html_content) <= max_length:
            return html_content
        
        # Try to extract the most relevant parts
        import re
        
        # Extract text content
        text_content = re.sub(r'<[^>]+>', ' ', html_content)
        text_content = re.sub(r'\s+', ' ', text_content).strip()
        
        if len(text_content) <= max_length:
            return text_content
        
        # Truncate to max length
        return text_content[:max_length] + "..."
    
    def _calculate_confidence_score(self, extracted_data: Dict[str, Any], original_content: str) -> float:
        """Calculate confidence score for extracted data"""
        score = 0.0
        
        # Check for required fields
        required_fields = ['title', 'brand', 'model']
        for field in required_fields:
            if field in extracted_data and extracted_data[field]:
                score += 0.2
        
        # Check for price
        if 'price' in extracted_data and extracted_data['price']:
            score += 0.2
        
        # Check for description
        if 'description' in extracted_data and extracted_data['description']:
            score += 0.1
        
        # Check for laser-related keywords
        laser_keywords = ['laser', 'ipl', 'rf', 'hifu', 'cryolipolysis']
        content_lower = original_content.lower()
        keyword_matches = sum(1 for keyword in laser_keywords if keyword in content_lower)
        score += min(0.3, keyword_matches * 0.1)
        
        return min(1.0, score)
    
    def _get_laser_equipment_prompt(self) -> str:
        """Get prompt for laser equipment extraction"""
        return """
        Extract laser equipment information from the following content and return it as JSON.
        
        Focus on:
        - Equipment title/name
        - Brand (Sciton, Cynosure, Cutera, Candela, Lumenis, Alma, InMode, BTL, etc.)
        - Model (Joule, PicoSure, PicoWay, GentleMax Pro, M22, etc.)
        - Price (asking price, starting bid, estimate)
        - Condition (excellent, good, fair, poor, used, refurbished)
        - Description
        - Location
        - Images (URLs)
        
        Return JSON with this structure:
        {
            "title": "extracted title",
            "brand": "extracted brand",
            "model": "extracted model",
            "price": "extracted price",
            "condition": "extracted condition",
            "description": "extracted description",
            "location": "extracted location",
            "images": ["image_url1", "image_url2"],
            "confidence": 0.0-1.0
        }
        """
    
    def _get_auction_listing_prompt(self) -> str:
        """Get prompt for auction listing extraction"""
        return """
        Extract auction listing information from the following content and return it as JSON.
        
        Focus on:
        - Lot number/ID
        - Item title
        - Brand and model
        - Starting bid/estimate
        - Current bid
        - Auction end time
        - Condition
        - Description
        - Images
        
        Return JSON with this structure:
        {
            "lot_number": "extracted lot number",
            "title": "extracted title",
            "brand": "extracted brand",
            "model": "extracted model",
            "starting_bid": "extracted starting bid",
            "current_bid": "extracted current bid",
            "auction_end": "extracted auction end time",
            "condition": "extracted condition",
            "description": "extracted description",
            "images": ["image_url1", "image_url2"],
            "confidence": 0.0-1.0
        }
        """
    
    def _get_price_extraction_prompt(self) -> str:
        """Get prompt for price extraction"""
        return """
        Extract price information from the following content and return it as JSON.
        
        Look for:
        - Asking price
        - Starting bid
        - Current bid
        - Reserve price
        - Estimate
        - Buy now price
        
        Return JSON with this structure:
        {
            "asking_price": "extracted asking price",
            "starting_bid": "extracted starting bid",
            "current_bid": "extracted current bid",
            "reserve_price": "extracted reserve price",
            "estimate": "extracted estimate",
            "buy_now_price": "extracted buy now price",
            "currency": "USD",
            "confidence": 0.0-1.0
        }
        """
    
    def _get_brand_model_prompt(self) -> str:
        """Get prompt for brand/model extraction"""
        return """
        Extract brand and model information from the following content and return it as JSON.
        
        Look for laser equipment brands like:
        - Sciton (Joule, Profile, Contour)
        - Cynosure (PicoSure, PicoWay, GentleMax Pro)
        - Cutera (Excel V, TruSculpt, Genesis)
        - Candela (GentleMax Pro, Gentle YAG)
        - Lumenis (M22, Elite+, LightSheer)
        - Alma (Harmony XL, Soprano, OPUS)
        - InMode (Secret RF, Morpheus8, Emsculpt)
        - BTL, Lutronic, Bison, DEKA, Quanta, Asclepion
        
        Return JSON with this structure:
        {
            "brand": "extracted brand",
            "model": "extracted model",
            "modality": "extracted modality/technology",
            "confidence": 0.0-1.0
        }
        """
    
    def _get_api_key(self) -> str:
        """Get API key from environment"""
        import os
        return os.getenv('GROQ_API_KEY', '')
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """Get extraction statistics"""
        return {
            'api_key_configured': bool(self.api_key),
            'api_url': self.api_url,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            'available_prompts': list(self.extraction_prompts.keys()),
        }
    
    def batch_extract(self, html_contents: List[str], extraction_type: str = 'laser_equipment') -> List[LLMExtractionResult]:
        """Extract data from multiple HTML contents"""
        results = []
        
        for html_content in html_contents:
            result = self.extract_from_html(html_content, extraction_type)
            results.append(result)
        
        return results


class ErrorRecoveryManager:
    """Manage error recovery using LLM fallback"""
    
    def __init__(self, llm_extractor: LLMFallbackExtractor):
        self.llm_extractor = llm_extractor
        self.recovery_attempts = 0
        self.max_recovery_attempts = 3
    
    def recover_from_parsing_failure(self, html_content: str, error_message: str) -> LLMExtractionResult:
        """Recover from parsing failure"""
        self.recovery_attempts += 1
        
        if self.recovery_attempts > self.max_recovery_attempts:
            return LLMExtractionResult(
                success=False,
                extracted_data={},
                confidence_score=0.0,
                processing_time=0.0,
                error_message=f'Max recovery attempts ({self.max_recovery_attempts}) exceeded'
            )
        
        return self.llm_extractor.recover_from_parsing_error(html_content, error_message)
    
    def recover_from_selector_failure(self, html_content: str, failed_selectors: List[str]) -> LLMExtractionResult:
        """Recover from selector failure"""
        error_message = f"Failed selectors: {', '.join(failed_selectors)}"
        return self.llm_extractor.recover_from_parsing_error(html_content, error_message)
    
    def reset_recovery_attempts(self):
        """Reset recovery attempts counter"""
        self.recovery_attempts = 0
