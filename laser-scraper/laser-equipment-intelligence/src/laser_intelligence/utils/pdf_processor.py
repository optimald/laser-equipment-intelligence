"""
PDF processing with Tesseract OCR for auction catalogs
"""

import os
import re
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import requests
from io import BytesIO
from laser_intelligence.utils.brand_mapping import BrandMapper


@dataclass
class PDFExtractionResult:
    """Result of PDF extraction"""
    text_content: str
    images_extracted: int
    brand_matches: List[str]
    model_matches: List[str]
    price_matches: List[str]
    confidence_score: float
    processing_time: float


class PDFProcessor:
    """Process PDF auction catalogs with OCR and text extraction"""
    
    def __init__(self):
        self.brand_mapper = BrandMapper()
        self.tesseract_config = '--oem 3 --psm 6'  # OCR Engine Mode 3, Page Segmentation Mode 6
        
        # Brand and model patterns for extraction
        self.brand_patterns = [
            r'\b(Sciton|Cynosure|Cutera|Candela|Lumenis|Alma|InMode|BTL|Lutronic|Bison|DEKA|Quanta|Asclepion|Zimmer|Palomar|Ellman|Fotona)\b',
            r'\b(Bluecore|Jeisys|Perigee|Wells Johnson|Aerolase|Candela Medical|Cynosure Hologic|Cutera|Lumenis Baring|Alma Lasers|InMode|BTL Aesthetics|Lutronic|Bison Medical|DEKA|Quanta System|Asclepion|Zimmer MedizinSysteme|Palomar Medical|Ellman International|Fotona)\b'
        ]
        
        self.model_patterns = [
            r'\b(Joule|BBL|M22|Elite\+|GentleMax Pro|PicoSure|PicoWay|Enlighten|Excel V|Xeo|Secret RF|Morpheus8|Emsculpt|Emsella|CoolSculpting|Venus Legacy|Ultraformer|Ulthera)\b',
            r'\b(AviClear|EvolveX|Sylfirm X|PicoSure Pro|Emsculpt NEO|Morpheus8 Pro|Secret RF Pro|GentleMax Pro Plus)\b'
        ]
        
        self.price_patterns = [
            r'\$[\d,]+(?:\.\d{2})?',
            r'USD\s*[\d,]+(?:\.\d{2})?',
            r'Price:\s*\$?[\d,]+(?:\.\d{2})?',
            r'Starting Bid:\s*\$?[\d,]+(?:\.\d{2})?',
            r'Estimate:\s*\$?[\d,]+(?:\.\d{2})?'
        ]
    
    def process_pdf_url(self, pdf_url: str) -> PDFExtractionResult:
        """Process PDF from URL"""
        start_time = time.time()
        
        try:
            # Download PDF
            response = requests.get(pdf_url, timeout=30)
            response.raise_for_status()
            
            # Process PDF content
            result = self.process_pdf_content(response.content)
            result.processing_time = time.time() - start_time
            
            return result
            
        except Exception as e:
            print(f'Error processing PDF URL {pdf_url}: {e}')
            return PDFExtractionResult(
                text_content='',
                images_extracted=0,
                brand_matches=[],
                model_matches=[],
                price_matches=[],
                confidence_score=0.0,
                processing_time=time.time() - start_time
            )
    
    def process_pdf_content(self, pdf_content: bytes) -> PDFExtractionResult:
        """Process PDF content from bytes"""
        start_time = time.time()
        
        try:
            # Open PDF with PyMuPDF
            pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
            
            text_content = ""
            images_extracted = 0
            brand_matches = []
            model_matches = []
            price_matches = []
            
            # Process each page
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                
                # Extract text
                page_text = page.get_text()
                text_content += page_text + "\n"
                
                # Extract images and process with OCR
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    try:
                        # Get image data
                        xref = img[0]
                        pix = fitz.Pixmap(pdf_document, xref)
                        
                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            img_data = pix.tobytes("png")
                            
                            # Process with Tesseract
                            ocr_text = self._process_image_with_ocr(img_data)
                            text_content += ocr_text + "\n"
                            images_extracted += 1
                        
                        pix = None
                        
                    except Exception as e:
                        print(f'Error processing image {img_index} on page {page_num}: {e}')
                        continue
            
            pdf_document.close()
            
            # Extract structured data from text
            brand_matches = self._extract_brands(text_content)
            model_matches = self._extract_models(text_content)
            price_matches = self._extract_prices(text_content)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(
                text_content, brand_matches, model_matches, price_matches
            )
            
            return PDFExtractionResult(
                text_content=text_content,
                images_extracted=images_extracted,
                brand_matches=brand_matches,
                model_matches=model_matches,
                price_matches=price_matches,
                confidence_score=confidence_score,
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            print(f'Error processing PDF content: {e}')
            return PDFExtractionResult(
                text_content='',
                images_extracted=0,
                brand_matches=[],
                model_matches=[],
                price_matches=[],
                confidence_score=0.0,
                processing_time=time.time() - start_time
            )
    
    def _process_image_with_ocr(self, image_data: bytes) -> str:
        """Process image with Tesseract OCR"""
        try:
            # Convert bytes to PIL Image
            image = Image.open(BytesIO(image_data))
            
            # Perform OCR
            ocr_text = pytesseract.image_to_string(
                image, 
                config=self.tesseract_config
            )
            
            return ocr_text
            
        except Exception as e:
            print(f'Error processing image with OCR: {e}')
            return ""
    
    def _extract_brands(self, text: str) -> List[str]:
        """Extract brand names from text"""
        brands = []
        
        for pattern in self.brand_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            brands.extend(matches)
        
        # Normalize brands
        normalized_brands = []
        for brand in brands:
            normalized = self.brand_mapper.normalize_brand(brand)
            if normalized not in normalized_brands:
                normalized_brands.append(normalized)
        
        return normalized_brands
    
    def _extract_models(self, text: str) -> List[str]:
        """Extract model names from text"""
        models = []
        
        for pattern in self.model_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            models.extend(matches)
        
        # Normalize models
        normalized_models = []
        for model in models:
            normalized = self.brand_mapper.normalize_model(model, '')
            if normalized not in normalized_models:
                normalized_models.append(normalized)
        
        return normalized_models
    
    def _extract_prices(self, text: str) -> List[str]:
        """Extract price information from text"""
        prices = []
        
        for pattern in self.price_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            prices.extend(matches)
        
        return prices
    
    def _calculate_confidence_score(self, text: str, brands: List[str], models: List[str], prices: List[str]) -> float:
        """Calculate confidence score for extraction quality"""
        score = 0.0
        
        # Base score from text length
        if len(text) > 1000:
            score += 20
        elif len(text) > 500:
            score += 10
        
        # Brand matches
        score += min(30, len(brands) * 10)
        
        # Model matches
        score += min(25, len(models) * 8)
        
        # Price matches
        score += min(15, len(prices) * 5)
        
        # Text quality indicators
        if 'laser' in text.lower():
            score += 10
        
        if any(keyword in text.lower() for keyword in ['auction', 'lot', 'item', 'equipment']):
            score += 5
        
        return min(100, score)
    
    def extract_listing_data(self, pdf_result: PDFExtractionResult) -> Dict[str, Any]:
        """Extract structured listing data from PDF extraction result"""
        listing_data = {
            'title_raw': '',
            'description_raw': pdf_result.text_content[:500],  # First 500 chars
            'brand': '',
            'model': '',
            'asking_price': None,
            'condition': 'unknown',
            'source_type': 'pdf_catalog',
            'extraction_confidence': pdf_result.confidence_score,
            'images_processed': pdf_result.images_extracted,
            'processing_time': pdf_result.processing_time
        }
        
        # Extract primary brand and model
        if pdf_result.brand_matches:
            listing_data['brand'] = pdf_result.brand_matches[0]
        
        if pdf_result.model_matches:
            listing_data['model'] = pdf_result.model_matches[0]
        
        # Extract price
        if pdf_result.price_matches:
            price_text = pdf_result.price_matches[0]
            price_value = self._parse_price(price_text)
            if price_value:
                listing_data['asking_price'] = price_value
        
        # Generate title
        if listing_data['brand'] and listing_data['model']:
            listing_data['title_raw'] = f"{listing_data['brand']} {listing_data['model']} Laser System"
        elif listing_data['brand']:
            listing_data['title_raw'] = f"{listing_data['brand']} Laser Equipment"
        else:
            listing_data['title_raw'] = "Laser Equipment"
        
        return listing_data
    
    def _parse_price(self, price_text: str) -> Optional[float]:
        """Parse price text to float value"""
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[^\d.]', '', price_text)
            if cleaned:
                return float(cleaned)
        except ValueError:
            pass
        return None
    
    def batch_process_pdfs(self, pdf_urls: List[str]) -> List[PDFExtractionResult]:
        """Process multiple PDFs in batch"""
        results = []
        
        for url in pdf_urls:
            try:
                result = self.process_pdf_url(url)
                results.append(result)
                
                # Add delay to avoid overwhelming servers
                time.sleep(2)
                
            except Exception as e:
                print(f'Error processing PDF {url}: {e}')
                results.append(PDFExtractionResult(
                    text_content='',
                    images_extracted=0,
                    brand_matches=[],
                    model_matches=[],
                    price_matches=[],
                    confidence_score=0.0,
                    processing_time=0.0
                ))
        
        return results
    
    def get_extraction_statistics(self, results: List[PDFExtractionResult]) -> Dict[str, Any]:
        """Get statistics from batch processing results"""
        total_results = len(results)
        successful_results = len([r for r in results if r.confidence_score > 50])
        
        total_brands = sum(len(r.brand_matches) for r in results)
        total_models = sum(len(r.model_matches) for r in results)
        total_prices = sum(len(r.price_matches) for r in results)
        total_images = sum(r.images_extracted for r in results)
        
        avg_confidence = sum(r.confidence_score for r in results) / total_results if total_results > 0 else 0
        avg_processing_time = sum(r.processing_time for r in results) / total_results if total_results > 0 else 0
        
        return {
            'total_pdfs': total_results,
            'successful_extractions': successful_results,
            'success_rate': (successful_results / total_results * 100) if total_results > 0 else 0,
            'total_brands_found': total_brands,
            'total_models_found': total_models,
            'total_prices_found': total_prices,
            'total_images_processed': total_images,
            'average_confidence': avg_confidence,
            'average_processing_time': avg_processing_time
        }


class PDFCatalogSpider:
    """Spider for processing PDF auction catalogs"""
    
    def __init__(self):
        self.pdf_processor = PDFProcessor()
    
    def process_auction_catalog(self, catalog_url: str) -> List[Dict[str, Any]]:
        """Process auction catalog PDF and extract listings"""
        try:
            # Process PDF
            pdf_result = self.pdf_processor.process_pdf_url(catalog_url)
            
            if pdf_result.confidence_score < 30:
                print(f'Low confidence PDF extraction: {catalog_url}')
                return []
            
            # Extract structured data
            listing_data = self.pdf_processor.extract_listing_data(pdf_result)
            
            # If we found multiple brands/models, create separate listings
            listings = []
            
            if len(pdf_result.brand_matches) > 1 or len(pdf_result.model_matches) > 1:
                # Multiple items in catalog
                for i, brand in enumerate(pdf_result.brand_matches):
                    model = pdf_result.model_matches[i] if i < len(pdf_result.model_matches) else ''
                    
                    listing = listing_data.copy()
                    listing['brand'] = brand
                    listing['model'] = model
                    listing['title_raw'] = f"{brand} {model} Laser System" if model else f"{brand} Laser Equipment"
                    
                    listings.append(listing)
            else:
                # Single item
                listings.append(listing_data)
            
            return listings
            
        except Exception as e:
            print(f'Error processing auction catalog {catalog_url}: {e}')
            return []
    
    def discover_catalog_urls(self, auction_site_url: str) -> List[str]:
        """Discover PDF catalog URLs from auction site"""
        try:
            response = requests.get(auction_site_url, timeout=30)
            response.raise_for_status()
            
            # Look for PDF links
            pdf_pattern = r'href=["\']([^"\']*\.pdf[^"\']*)["\']'
            pdf_matches = re.findall(pdf_pattern, response.text, re.IGNORECASE)
            
            # Convert relative URLs to absolute
            catalog_urls = []
            for match in pdf_matches:
                if match.startswith('http'):
                    catalog_urls.append(match)
                else:
                    catalog_urls.append(f"{auction_site_url.rstrip('/')}/{match.lstrip('/')}")
            
            return catalog_urls
            
        except Exception as e:
            print(f'Error discovering catalog URLs from {auction_site_url}: {e}')
            return []
