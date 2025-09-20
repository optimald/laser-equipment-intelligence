"""
ML-based HTML diffing using Torch for intelligent content change detection
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import numpy as np
import hashlib
import re
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import json
import time


@dataclass
class HTMLDiffResult:
    """Result of HTML diffing analysis"""
    similarity_score: float
    content_changes: List[Dict[str, Any]]
    structural_changes: List[Dict[str, Any]]
    confidence: float
    processing_time: float


class HTMLDiffDataset(Dataset):
    """Dataset for training HTML diffing model"""
    
    def __init__(self, html_pairs: List[Tuple[str, str]], labels: List[float]):
        self.html_pairs = html_pairs
        self.labels = labels
    
    def __len__(self):
        return len(self.html_pairs)
    
    def __getitem__(self, idx):
        html1, html2 = self.html_pairs[idx]
        label = self.labels[idx]
        
        # Convert HTML to feature vectors
        features1 = self._html_to_features(html1)
        features2 = self._html_to_features(html2)
        
        return torch.tensor(features1, dtype=torch.float32), torch.tensor(features2, dtype=torch.float32), torch.tensor(label, dtype=torch.float32)
    
    def _html_to_features(self, html: str) -> List[float]:
        """Convert HTML to feature vector"""
        features = []
        
        # Basic features
        features.append(len(html))  # Length
        features.append(html.count('<'))  # Tag count
        features.append(html.count('>'))  # Tag count
        features.append(html.count('class='))  # Class count
        features.append(html.count('id='))  # ID count
        
        # Content features
        text_content = re.sub(r'<[^>]+>', '', html)
        features.append(len(text_content))  # Text length
        features.append(len(text_content.split()))  # Word count
        
        # Structural features
        features.append(html.count('<div'))  # Div count
        features.append(html.count('<span'))  # Span count
        features.append(html.count('<p'))  # Paragraph count
        features.append(html.count('<img'))  # Image count
        features.append(html.count('<a'))  # Link count
        
        # Normalize features
        features = [f / 1000.0 for f in features]  # Simple normalization
        
        return features


class HTMLDiffModel(nn.Module):
    """Neural network for HTML diffing"""
    
    def __init__(self, input_size: int = 12, hidden_size: int = 64):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size
        
        # Feature extraction layers
        self.feature_extractor = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
        )
        
        # Similarity computation
        self.similarity_layer = nn.Sequential(
            nn.Linear(hidden_size * 2, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_size, 1),
            nn.Sigmoid()
        )
    
    def forward(self, html1_features: torch.Tensor, html2_features: torch.Tensor) -> torch.Tensor:
        """Forward pass"""
        # Extract features for both HTML documents
        features1 = self.feature_extractor(html1_features)
        features2 = self.feature_extractor(html2_features)
        
        # Compute similarity
        combined_features = torch.cat([features1, features2], dim=1)
        similarity = self.similarity_layer(combined_features)
        
        return similarity


class MLHTMLDiffer:
    """ML-based HTML differ for intelligent content change detection"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.model = HTMLDiffModel()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        if model_path and torch.load(model_path, map_location=self.device):
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.model.eval()
        else:
            # Initialize with random weights
            self._initialize_model()
    
    def _initialize_model(self):
        """Initialize model with random weights"""
        for layer in self.model.modules():
            if isinstance(layer, nn.Linear):
                nn.init.xavier_uniform_(layer.weight)
                nn.init.constant_(layer.bias, 0)
    
    def compare_html(self, html1: str, html2: str) -> HTMLDiffResult:
        """Compare two HTML documents and return diff result"""
        start_time = time.time()
        
        try:
            # Extract features
            features1 = self._html_to_features(html1)
            features2 = self._html_to_features(html2)
            
            # Convert to tensors
            tensor1 = torch.tensor(features1, dtype=torch.float32).unsqueeze(0).to(self.device)
            tensor2 = torch.tensor(features2, dtype=torch.float32).unsqueeze(0).to(self.device)
            
            # Get similarity score
            with torch.no_grad():
                similarity_score = self.model(tensor1, tensor2).item()
            
            # Analyze content changes
            content_changes = self._analyze_content_changes(html1, html2)
            structural_changes = self._analyze_structural_changes(html1, html2)
            
            # Calculate confidence
            confidence = self._calculate_confidence(similarity_score, content_changes, structural_changes)
            
            processing_time = time.time() - start_time
            
            return HTMLDiffResult(
                similarity_score=similarity_score,
                content_changes=content_changes,
                structural_changes=structural_changes,
                confidence=confidence,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = time.time() - start_time
            return HTMLDiffResult(
                similarity_score=0.0,
                content_changes=[],
                structural_changes=[],
                confidence=0.0,
                processing_time=processing_time
            )
    
    def _html_to_features(self, html: str) -> List[float]:
        """Convert HTML to feature vector"""
        features = []
        
        # Basic features
        features.append(len(html))  # Length
        features.append(html.count('<'))  # Tag count
        features.append(html.count('>'))  # Tag count
        features.append(html.count('class='))  # Class count
        features.append(html.count('id='))  # ID count
        
        # Content features
        text_content = re.sub(r'<[^>]+>', '', html)
        features.append(len(text_content))  # Text length
        features.append(len(text_content.split()))  # Word count
        
        # Structural features
        features.append(html.count('<div'))  # Div count
        features.append(html.count('<span'))  # Span count
        features.append(html.count('<p'))  # Paragraph count
        features.append(html.count('<img'))  # Image count
        features.append(html.count('<a'))  # Link count
        
        # Normalize features
        features = [f / 1000.0 for f in features]  # Simple normalization
        
        return features
    
    def _analyze_content_changes(self, html1: str, html2: str) -> List[Dict[str, Any]]:
        """Analyze content changes between HTML documents"""
        changes = []
        
        # Extract text content
        text1 = re.sub(r'<[^>]+>', '', html1)
        text2 = re.sub(r'<[^>]+>', '', html2)
        
        # Simple word-level diff
        words1 = text1.split()
        words2 = text2.split()
        
        # Find added words
        added_words = set(words2) - set(words1)
        if added_words:
            changes.append({
                'type': 'content_added',
                'count': len(added_words),
                'words': list(added_words)[:10]  # Limit to first 10 words
            })
        
        # Find removed words
        removed_words = set(words1) - set(words2)
        if removed_words:
            changes.append({
                'type': 'content_removed',
                'count': len(removed_words),
                'words': list(removed_words)[:10]  # Limit to first 10 words
            })
        
        return changes
    
    def _analyze_structural_changes(self, html1: str, html2: str) -> List[Dict[str, Any]]:
        """Analyze structural changes between HTML documents"""
        changes = []
        
        # Extract tags
        tags1 = re.findall(r'<(\w+)', html1)
        tags2 = re.findall(r'<(\w+)', html2)
        
        # Count tag changes
        tag_counts1 = {}
        tag_counts2 = {}
        
        for tag in tags1:
            tag_counts1[tag] = tag_counts1.get(tag, 0) + 1
        
        for tag in tags2:
            tag_counts2[tag] = tag_counts2.get(tag, 0) + 1
        
        # Find tag changes
        all_tags = set(tag_counts1.keys()) | set(tag_counts2.keys())
        
        for tag in all_tags:
            count1 = tag_counts1.get(tag, 0)
            count2 = tag_counts2.get(tag, 0)
            
            if count1 != count2:
                changes.append({
                    'type': 'tag_count_change',
                    'tag': tag,
                    'old_count': count1,
                    'new_count': count2,
                    'difference': count2 - count1
                })
        
        return changes
    
    def _calculate_confidence(self, similarity_score: float, content_changes: List[Dict[str, Any]], structural_changes: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for the diff result"""
        confidence = similarity_score
        
        # Adjust confidence based on number of changes
        total_changes = len(content_changes) + len(structural_changes)
        if total_changes > 0:
            confidence *= (1.0 - min(0.5, total_changes * 0.1))
        
        return max(0.0, min(1.0, confidence))
    
    def train_model(self, training_data: List[Tuple[str, str, float]], epochs: int = 100, batch_size: int = 32):
        """Train the HTML diffing model"""
        # Prepare dataset
        html_pairs = [(data[0], data[1]) for data in training_data]
        labels = [data[2] for data in training_data]
        
        dataset = HTMLDiffDataset(html_pairs, labels)
        dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
        
        # Setup training
        optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        criterion = nn.MSELoss()
        
        self.model.train()
        
        for epoch in range(epochs):
            total_loss = 0
            for batch_features1, batch_features2, batch_labels in dataloader:
                batch_features1 = batch_features1.to(self.device)
                batch_features2 = batch_features2.to(self.device)
                batch_labels = batch_labels.to(self.device)
                
                optimizer.zero_grad()
                
                predictions = self.model(batch_features1, batch_features2)
                loss = criterion(predictions.squeeze(), batch_labels)
                
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
    
    def _create_model(self) -> HTMLDiffModel:
        """Create a new model instance"""
        return HTMLDiffModel()
    
    def _preprocess_html(self, html: str) -> str:
        """Preprocess HTML for analysis"""
        # Clean up HTML
        html = html.strip()
        
        # Remove extra whitespace
        html = re.sub(r'\s+', ' ', html)
        
        # Remove comments
        html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
        
        return html
    
    def _extract_features(self, html: str) -> np.ndarray:
        """Extract features from HTML"""
        features = self._html_to_features(html)
        return np.array(features, dtype=np.float32)
    
    def _calculate_similarity(self, html1: str, html2: str) -> float:
        """Calculate similarity between two HTML documents"""
        try:
            # Extract features
            features1 = self._html_to_features(html1)
            features2 = self._html_to_features(html2)
            
            # Convert to tensors
            tensor1 = torch.tensor(features1, dtype=torch.float32).unsqueeze(0).to(self.device)
            tensor2 = torch.tensor(features2, dtype=torch.float32).unsqueeze(0).to(self.device)
            
            # Get similarity score
            with torch.no_grad():
                similarity_score = self.model(tensor1, tensor2).item()
            
            return similarity_score
            
        except Exception:
            return 0.0
    
    def _detect_content_changes(self, html1: str, html2: str) -> List[Dict[str, Any]]:
        """Detect content changes between HTML documents"""
        return self._analyze_content_changes(html1, html2)
    
    def _detect_structural_changes(self, html1: str, html2: str) -> List[Dict[str, Any]]:
        """Detect structural changes between HTML documents"""
        return self._analyze_structural_changes(html1, html2)
    
    def batch_compare(self, html_pairs: List[Tuple[str, str]]) -> List[HTMLDiffResult]:
        """Compare multiple pairs of HTML documents"""
        results = []
        
        for html1, html2 in html_pairs:
            result = self.compare_html(html1, html2)
            results.append(result)
        
        return results


class HTMLDiffManager:
    """Manager for HTML diffing operations"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.differ = MLHTMLDiffer(model_path)
        self.diff_history = []
    
    def compare_page_versions(self, url: str, html1: str, html2: str) -> HTMLDiffResult:
        """Compare two versions of a page"""
        result = self.differ.compare_html(html1, html2)
        
        # Store in history
        self.diff_history.append({
            'url': url,
            'timestamp': time.time(),
            'result': result
        })
        
        return result
    
    def detect_significant_changes(self, result: HTMLDiffResult, threshold: float = 0.3) -> bool:
        """Detect if changes are significant enough to warrant attention"""
        return result.similarity_score < threshold or len(result.content_changes) > 5 or len(result.structural_changes) > 3
    
    def get_change_summary(self, result: HTMLDiffResult) -> str:
        """Get a human-readable summary of changes"""
        summary_parts = []
        
        if result.similarity_score < 0.5:
            summary_parts.append("Significant content changes detected")
        
        for change in result.content_changes:
            if change['type'] == 'content_added':
                summary_parts.append(f"Added {change['count']} words")
            elif change['type'] == 'content_removed':
                summary_parts.append(f"Removed {change['count']} words")
        
        for change in result.structural_changes:
            if change['type'] == 'tag_count_change':
                summary_parts.append(f"Changed {change['tag']} count from {change['old_count']} to {change['new_count']}")
        
        return "; ".join(summary_parts) if summary_parts else "No significant changes detected"
    
    def get_diff_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent diff history"""
        return self.diff_history[-limit:]
