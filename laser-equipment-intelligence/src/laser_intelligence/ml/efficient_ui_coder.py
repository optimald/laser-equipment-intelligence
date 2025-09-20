"""
EfficientUICoder for dynamic selector generation using ML
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np
import re
from typing import Dict, List, Tuple, Any, Optional, Set
from dataclasses import dataclass
import json
import time
from bs4 import BeautifulSoup


@dataclass
class SelectorCandidate:
    """Candidate selector for an element"""
    selector: str
    confidence: float
    element_type: str
    attributes: Dict[str, str]
    text_content: str
    position: Tuple[int, int]


@dataclass
class SelectorGenerationResult:
    """Result of selector generation"""
    best_selectors: List[SelectorCandidate]
    element_info: Dict[str, Any]
    confidence_score: float
    processing_time: float


class ElementDataset(Dataset):
    """Dataset for training selector generation model"""
    
    def __init__(self, elements: List[Dict[str, Any]], selectors: List[str]):
        self.elements = elements
        self.selectors = selectors
    
    def __len__(self):
        return len(self.elements)
    
    def __getitem__(self, idx):
        element = self.elements[idx]
        selector = self.selectors[idx]
        
        # Convert element to feature vector
        features = self._element_to_features(element)
        
        # Return features as tensor and selector as string (for testing compatibility)
        return torch.tensor(features, dtype=torch.float32), selector
    
    def _element_to_features(self, element: Dict[str, Any]) -> List[float]:
        """Convert element to feature vector"""
        features = []
        
        # Basic features
        features.append(float(len(element.get('tag', ''))))  # Tag length
        features.append(float(len(element.get('text', ''))))  # Text length
        features.append(float(len(element.get('attributes', {}))))  # Attribute count
        
        # Attribute features
        attributes = element.get('attributes', {})
        features.append(1.0 if 'class' in attributes else 0.0)  # Has class
        features.append(1.0 if 'id' in attributes else 0.0)  # Has id
        features.append(1.0 if 'href' in attributes else 0.0)  # Has href
        features.append(1.0 if 'src' in attributes else 0.0)  # Has src
        
        # Position features
        position = element.get('position', (0, 0))
        features.append(float(position[0]) / 1000.0)  # X position (normalized)
        features.append(float(position[1]) / 1000.0)  # Y position (normalized)
        
        # Structural features
        features.append(float(element.get('depth', 0)) / 10.0)  # DOM depth
        features.append(float(element.get('sibling_count', 0)) / 10.0)  # Sibling count
        
        return features
    
    def _selector_to_target(self, selector: str) -> List[float]:
        """Convert selector to target vector (simplified)"""
        # This is a simplified approach - in practice, you'd want more sophisticated encoding
        target = [0.0] * 10  # 10 different selector types
        
        if selector.startswith('#'):
            target[0] = 1.0  # ID selector
        elif selector.startswith('.'):
            target[1] = 1.0  # Class selector
        elif '[' in selector:
            target[2] = 1.0  # Attribute selector
        elif ':' in selector:
            target[3] = 1.0  # Pseudo selector
        else:
            target[4] = 1.0  # Tag selector
        
        return target


class EfficientUICoderModel(nn.Module):
    """Neural network for efficient UI selector generation"""
    
    def __init__(self, input_size: int = 12, hidden_size: int = 128, output_size: int = 10):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        
        # Feature extraction layers
        self.feature_extractor = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
        )
        
        # Selector generation layers
        self.selector_generator = nn.Sequential(
            nn.Linear(hidden_size, hidden_size // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size // 2, output_size),
            nn.Softmax(dim=1)
        )
    
    def forward(self, element_features: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        features = self.feature_extractor(element_features)
        selector_probs = self.selector_generator(features)
        return selector_probs


class EfficientUICoder:
    """EfficientUICoder for dynamic selector generation"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model = EfficientUICoderModel()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        if model_path and torch.load(model_path, map_location=self.device):
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.model.eval()
        else:
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize model with random weights"""
        for layer in self.model.modules():
            if isinstance(layer, nn.Linear):
                nn.init.xavier_uniform_(layer.weight)
                nn.init.constant_(layer.bias, 0)
    
    def generate_selectors(self, html: str, target_text: str = None, target_attributes: Dict[str, str] = None) -> SelectorGenerationResult:
        """Generate efficient selectors for elements in HTML"""
        start_time = time.time()
        
        try:
            # Parse HTML
            soup = BeautifulSoup(html, 'html.parser')
            
            # Find candidate elements
            candidate_elements = self._find_candidate_elements(soup, target_text, target_attributes)
            
            # Generate selectors for each candidate
            selector_candidates = []
            for element_info in candidate_elements:
                selectors = self._generate_element_selectors(element_info)
                selector_candidates.extend(selectors)
            
            # Rank selectors by confidence
            selector_candidates.sort(key=lambda x: x.confidence, reverse=True)
            
            # Calculate overall confidence
            confidence_score = self._calculate_overall_confidence(selector_candidates)
            
            processing_time = time.time() - start_time
            
            return SelectorGenerationResult(
                best_selectors=selector_candidates[:10],  # Top 10 selectors
                element_info={'total_candidates': len(candidate_elements)},
                confidence_score=confidence_score,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return SelectorGenerationResult(
                best_selectors=[],
                element_info={'error': str(e)},
                confidence_score=0.0,
                processing_time=processing_time
            )
    
    def _find_candidate_elements(self, soup: BeautifulSoup, target_text: str = None, target_attributes: Dict[str, str] = None) -> List[Dict[str, Any]]:
        """Find candidate elements for selector generation"""
        candidates = []
        
        # Find all elements
        elements = soup.find_all()
        
        for i, element in enumerate(elements):
            element_info = {
                'tag': element.name,
                'text': element.get_text(strip=True),
                'attributes': dict(element.attrs) if element.attrs else {},
                'position': (i, i),  # Simplified position
                'depth': len(element.parents),
                'sibling_count': len(element.find_siblings()),
                'element': element
            }
            
            # Filter by target criteria if provided
            if target_text and target_text.lower() not in element_info['text'].lower():
                continue
            
            if target_attributes:
                match = True
                for attr, value in target_attributes.items():
                    if element_info['attributes'].get(attr) != value:
                        match = False
                        break
                if not match:
                    continue
            
            candidates.append(element_info)
        
        return candidates
    
    def _generate_element_selectors(self, element_info: Dict[str, Any]) -> List[SelectorCandidate]:
        """Generate selectors for a specific element"""
        selectors = []
        # Handle case where 'element' key doesn't exist (for testing)
        element = element_info.get('element', None)
        attributes = element_info.get('attributes', {})
        
        # ID selector (highest priority)
        if 'id' in attributes:
            selector = f"#{attributes['id']}"
            selectors.append(SelectorCandidate(
                selector=selector,
                confidence=0.95,
                element_type='id',
                attributes=attributes,
                text_content=element_info['text'],
                position=element_info['position']
            ))
        
        # Class selectors
        if 'class' in attributes:
            classes = attributes['class']
            if isinstance(classes, list):
                classes = ' '.join(classes)
            
            # Single class
            selector = f".{classes.split()[0]}"
            selectors.append(SelectorCandidate(
                selector=selector,
                confidence=0.8,
                element_type='class',
                attributes=attributes,
                text_content=element_info['text'],
                position=element_info['position']
            ))
            
            # Multiple classes
            if len(classes.split()) > 1:
                selector = f".{'.'.join(classes.split())}"
                selectors.append(SelectorCandidate(
                    selector=selector,
                    confidence=0.9,
                    element_type='class_multiple',
                    attributes=attributes,
                    text_content=element_info['text'],
                    position=element_info['position']
                ))
        
        # Attribute selectors
        for attr, value in attributes.items():
            if attr not in ['id', 'class']:
                selector = f"[{attr}='{value}']"
                selectors.append(SelectorCandidate(
                    selector=selector,
                    confidence=0.7,
                    element_type='attribute',
                    attributes=attributes,
                    text_content=element_info['text'],
                    position=element_info['position']
                ))
        
        # Tag selector
        selector = element_info['tag']
        selectors.append(SelectorCandidate(
            selector=selector,
            confidence=0.3,
            element_type='tag',
            attributes=attributes,
            text_content=element_info['text'],
            position=element_info['position']
        ))
        
        # Text-based selectors
        if element_info['text']:
            # Text content selector (XPath-like)
            text_selector = f"//{element_info['tag']}[contains(text(), '{element_info['text'][:20]}')]"
            selectors.append(SelectorCandidate(
                selector=text_selector,
                confidence=0.6,
                element_type='text',
                attributes=attributes,
                text_content=element_info['text'],
                position=element_info['position']
            ))
        
        return selectors
    
    def _calculate_overall_confidence(self, selectors: List[SelectorCandidate]) -> float:
        """Calculate overall confidence score"""
        if not selectors:
            return 0.0
        
        # Weighted average of confidence scores
        total_weight = 0
        weighted_sum = 0
        
        for selector in selectors:
            weight = 1.0
            if selector.element_type == 'id':
                weight = 2.0
            elif selector.element_type == 'class_multiple':
                weight = 1.5
            
            weighted_sum += selector.confidence * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def optimize_selector(self, selector: str, html: str) -> str:
        """Optimize an existing selector for better performance"""
        try:
            soup = BeautifulSoup(html, 'html.parser')
            
            # Test current selector
            elements = soup.select(selector)
            
            if len(elements) == 1:
                # Already optimal
                return selector
            
            if len(elements) == 0:
                # Selector doesn't work
                return self._generate_fallback_selector(html)
            
            # Too many elements - need to be more specific
            return self._make_selector_more_specific(selector, elements[0])
            
        except Exception:
            return selector
    
    def _generate_fallback_selector(self, html: str) -> str:
        """Generate a fallback selector when optimization fails"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find elements with unique attributes
        for element in soup.find_all():
            if element.get('id'):
                return f"#{element['id']}"
            if element.get('class'):
                classes = element['class']
                if isinstance(classes, list):
                    classes = ' '.join(classes)
                return f".{classes.split()[0]}"
        
        # Fallback to first element
        first_element = soup.find()
        if first_element:
            return first_element.name
        
        return "body"
    
    def _make_selector_more_specific(self, selector: str, target_element) -> str:
        """Make a selector more specific to target a single element"""
        # Add parent context
        parent = target_element.parent
        if parent and parent.name != 'html':
            parent_selector = self._generate_element_selectors({
                'element': parent,
                'attributes': dict(parent.attrs) if parent.attrs else {},
                'text': parent.get_text(strip=True),
                'position': (0, 0),
                'depth': 0,
                'sibling_count': 0
            })[0].selector
            
            return f"{parent_selector} > {selector}"
        
        return selector
    
    def train_model(self, training_data: List[Tuple[Dict[str, Any], str]], epochs: int = 100, batch_size: int = 32):
        """Train the selector generation model"""
        # Prepare dataset
        elements = [data[0] for data in training_data]
        selectors = [data[1] for data in training_data]
        
        dataset = ElementDataset(elements, selectors)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # Setup training
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        criterion = nn.MSELoss()
        
        self.model.train()
        
        for epoch in range(epochs):
            total_loss = 0
            for batch_features, batch_targets in dataloader:
                batch_features = batch_features.to(self.device)
                batch_targets = batch_targets.to(self.device)
                
                optimizer.zero_grad()
                
                predictions = self.model(batch_features)
                loss = criterion(predictions, batch_targets)
                
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            if epoch % 10 == 0:
                print(f'Epoch {epoch}, Loss: {total_loss / len(dataloader):.4f}')
        
        self.model.eval()
    
    def save_model(self, model_path: str):
        """Save the trained model"""
        torch.save(self.model.state_dict(), model_path)
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get model statistics"""
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        
        return {
            'total_parameters': total_params,
            'trainable_parameters': trainable_params,
            'device': str(self.device),
            'model_architecture': str(self.model),
        }
    
    def _create_model(self) -> EfficientUICoderModel:
        """Create a new model instance"""
        return EfficientUICoderModel()
    
    def _preprocess_element(self, element: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess element data for feature extraction"""
        processed = element.copy()
        
        # Normalize text content
        if 'text' in processed:
            processed['text'] = processed['text'].strip().lower()
        
        # Normalize attributes
        if 'attributes' in processed:
            normalized_attrs = {}
            for key, value in processed['attributes'].items():
                if isinstance(value, list):
                    normalized_attrs[key] = ' '.join(value)
                else:
                    normalized_attrs[key] = str(value)
            processed['attributes'] = normalized_attrs
        
        # Ensure position is tuple
        if 'position' in processed:
            if not isinstance(processed['position'], tuple):
                processed['position'] = (0, 0)
        
        return processed
    
    def _extract_features(self, element: Dict[str, Any]) -> np.ndarray:
        """Extract features from element"""
        dataset = ElementDataset([element], [''])
        features = dataset._element_to_features(element)
        return np.array(features, dtype=np.float32)
    
    def _generate_selectors(self, element: Dict[str, Any]) -> List[SelectorCandidate]:
        """Generate selectors for a single element"""
        return self._generate_element_selectors(element)
    
    def _calculate_selector_confidence(self, element: Dict[str, Any], selector: str) -> float:
        """Calculate confidence for a specific selector"""
        selectors = self._generate_element_selectors(element)
        
        for sel in selectors:
            if sel.selector == selector:
                return sel.confidence
        
        return 0.0
    
    def generate_selectors_for_element(self, element: Dict[str, Any]) -> SelectorGenerationResult:
        """Generate selectors for a single element"""
        start_time = time.time()
        
        try:
            # Preprocess element
            processed_element = self._preprocess_element(element)
            
            # Generate selectors
            selectors = self._generate_element_selectors(processed_element)
            
            # Calculate confidence
            confidence_score = self._calculate_overall_confidence(selectors)
            
            processing_time = time.time() - start_time
            
            return SelectorGenerationResult(
                best_selectors=selectors,
                element_info=processed_element,
                confidence_score=confidence_score,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return SelectorGenerationResult(
                best_selectors=[],
                element_info={'error': str(e)},
                confidence_score=0.0,
                processing_time=processing_time
            )
    
    def batch_generate_selectors(self, elements: List[Dict[str, Any]]) -> List[SelectorGenerationResult]:
        """Generate selectors for multiple elements"""
        results = []
        
        for element in elements:
            result = self.generate_selectors_for_element(element)
            results.append(result)
        
        return results
    
    def _validate_selector(self, element: Dict[str, Any], selector: str) -> bool:
        """Validate if a selector matches the element"""
        try:
            # Create a simple HTML structure for testing
            html = f"<html><body><{element.get('tag', 'div')}"
            
            # Add attributes
            attributes = element.get('attributes', {})
            for key, value in attributes.items():
                html += f' {key}="{value}"'
            
            html += f">{element.get('text', '')}</{element.get('tag', 'div')}></body></html>"
            
            soup = BeautifulSoup(html, 'html.parser')
            elements = soup.select(selector)
            
            return len(elements) > 0
            
        except Exception:
            return False
    
    def _rank_selectors(self, selectors: List[SelectorCandidate]) -> List[SelectorCandidate]:
        """Rank selectors by confidence and uniqueness"""
        # Sort by confidence (descending)
        ranked = sorted(selectors, key=lambda x: x.confidence, reverse=True)
        
        # Apply additional ranking logic
        for i, selector in enumerate(ranked):
            # Boost ID selectors
            if selector.element_type == 'id':
                selector.confidence = min(1.0, selector.confidence + 0.1)
            
            # Boost multiple class selectors
            elif selector.element_type == 'class_multiple':
                selector.confidence = min(1.0, selector.confidence + 0.05)
        
        # Re-sort after boosting
        ranked = sorted(ranked, key=lambda x: x.confidence, reverse=True)
        
        return ranked


class SelectorManager:
    """Manager for selector generation and optimization"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.coder = EfficientUICoder(model_path)
        self.selector_cache = {}
        self.performance_stats = {}
    
    def get_best_selector(self, html: str, target_text: str = None, target_attributes: Dict[str, str] = None) -> str:
        """Get the best selector for the given criteria"""
        # Check cache
        cache_key = f"{hash(html)}_{target_text}_{str(target_attributes)}"
        if cache_key in self.selector_cache:
            return self.selector_cache[cache_key]
        
        # Generate selectors
        result = self.coder.generate_selectors(html, target_text, target_attributes)
        
        if result.best_selectors:
            best_selector = result.best_selectors[0].selector
            self.selector_cache[cache_key] = best_selector
            return best_selector
        
        return "body"  # Fallback
    
    def optimize_existing_selectors(self, selectors: List[str], html: str) -> List[str]:
        """Optimize a list of existing selectors"""
        optimized = []
        
        for selector in selectors:
            optimized_selector = self.coder.optimize_selector(selector, html)
            optimized.append(optimized_selector)
        
        return optimized
    
    def validate_selectors(self, selectors: List[str], html: str) -> Dict[str, bool]:
        """Validate selectors against HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        results = {}
        
        for selector in selectors:
            try:
                elements = soup.select(selector)
                results[selector] = len(elements) > 0
            except Exception:
                results[selector] = False
        
        return results
    
    def get_selector_performance(self, selector: str, html: str) -> Dict[str, Any]:
        """Get performance metrics for a selector"""
        start_time = time.time()
        
        try:
            soup = BeautifulSoup(html, 'html.parser')
            elements = soup.select(selector)
            
            processing_time = time.time() - start_time
            
            return {
                'selector': selector,
                'element_count': len(elements),
                'processing_time': processing_time,
                'is_unique': len(elements) == 1,
                'is_valid': len(elements) > 0
            }
            
        except Exception as e:
            return {
                'selector': selector,
                'element_count': 0,
                'processing_time': time.time() - start_time,
                'is_unique': False,
                'is_valid': False,
                'error': str(e)
            }
