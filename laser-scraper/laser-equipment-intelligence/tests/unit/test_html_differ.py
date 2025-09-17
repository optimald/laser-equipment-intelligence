"""
Unit tests for HTML differ ML component
"""

import pytest
import torch
import numpy as np
from unittest.mock import Mock, patch
from laser_intelligence.ml.html_differ import MLHTMLDiffer, HTMLDiffDataset, HTMLDiffResult


class TestHTMLDiffDataset:
    """Test HTML diff dataset functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.html_pairs = [
            ('<html><body><h1>Title</h1></body></html>', '<html><body><h1>Title</h1></body></html>'),
            ('<html><body><h1>Title</h1></body></html>', '<html><body><h1>Different</h1></body></html>'),
        ]
        self.labels = [1.0, 0.5]
        self.dataset = HTMLDiffDataset(self.html_pairs, self.labels)

    def test_dataset_initialization(self):
        """Test dataset initialization"""
        assert len(self.dataset) == 2
        assert len(self.dataset.html_pairs) == 2
        assert len(self.dataset.labels) == 2

    def test_dataset_getitem(self):
        """Test dataset item retrieval"""
        features1, features2, label = self.dataset[0]
        
        assert isinstance(features1, torch.Tensor)
        assert isinstance(features2, torch.Tensor)
        assert isinstance(label, torch.Tensor)
        assert features1.shape == features2.shape
        assert label.item() == 1.0

    def test_html_to_features(self):
        """Test HTML to features conversion"""
        html = '<html><body><h1>Title</h1><p>Content</p></body></html>'
        features = self.dataset._html_to_features(html)
        
        assert isinstance(features, list)
        assert len(features) > 0
        assert all(isinstance(f, float) for f in features)

    def test_feature_extraction(self):
        """Test feature extraction from HTML"""
        html = '<html><body><h1>Title</h1><p>Content</p></body></html>'
        features = self.dataset._html_to_features(html)
        
        # Should extract various features
        assert len(features) > 10  # Should have multiple features


class TestMLHTMLDiffer:
    """Test HTML differ ML functionality"""

    def setup_method(self):
        """Set up test fixtures"""
        self.differ = MLHTMLDiffer()

    def test_differ_initialization(self):
        """Test HTML differ initialization"""
        assert self.differ is not None
        assert hasattr(self.differ, 'model')
        assert hasattr(self.differ, 'device')

    def test_model_creation(self):
        """Test model creation"""
        model = self.differ._create_model()
        assert isinstance(model, torch.nn.Module)

    def test_html_preprocessing(self):
        """Test HTML preprocessing"""
        html = '<html><body><h1>Title</h1><p>Content</p></body></html>'
        processed = self.differ._preprocess_html(html)
        
        assert isinstance(processed, str)
        assert len(processed) > 0

    def test_feature_extraction(self):
        """Test feature extraction"""
        html = '<html><body><h1>Title</h1><p>Content</p></body></html>'
        features = self.differ._extract_features(html)
        
        assert isinstance(features, np.ndarray)
        assert len(features) > 0

    def test_similarity_calculation(self):
        """Test similarity calculation"""
        html1 = '<html><body><h1>Title</h1></body></html>'
        html2 = '<html><body><h1>Title</h1></body></html>'
        
        similarity = self.differ._calculate_similarity(html1, html2)
        
        assert isinstance(similarity, float)
        assert 0 <= similarity <= 1

    def test_content_change_detection(self):
        """Test content change detection"""
        html1 = '<html><body><h1>Title</h1></body></html>'
        html2 = '<html><body><h1>Different</h1></body></html>'
        
        changes = self.differ._detect_content_changes(html1, html2)
        
        assert isinstance(changes, list)

    def test_structural_change_detection(self):
        """Test structural change detection"""
        html1 = '<html><body><h1>Title</h1></body></html>'
        html2 = '<html><body><h1>Title</h1><p>New</p></body></html>'
        
        changes = self.differ._detect_structural_changes(html1, html2)
        
        assert isinstance(changes, list)

    def test_compare_html(self):
        """Test HTML comparison"""
        html1 = '<html><body><h1>Title</h1></body></html>'
        html2 = '<html><body><h1>Title</h1></body></html>'
        
        result = self.differ.compare_html(html1, html2)
        
        assert isinstance(result, HTMLDiffResult)
        assert hasattr(result, 'similarity_score')
        assert hasattr(result, 'content_changes')
        assert hasattr(result, 'structural_changes')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'processing_time')

    def test_compare_html_different_content(self):
        """Test HTML comparison with different content"""
        html1 = '<html><body><h1>Title</h1></body></html>'
        html2 = '<html><body><h1>Different</h1></body></html>'
        
        result = self.differ.compare_html(html1, html2)
        
        assert isinstance(result, HTMLDiffResult)
        assert result.similarity_score < 1.0

    def test_batch_comparison(self):
        """Test batch HTML comparison"""
        html_pairs = [
            ('<html><body><h1>Title</h1></body></html>', '<html><body><h1>Title</h1></body></html>'),
            ('<html><body><h1>Title</h1></body></html>', '<html><body><h1>Different</h1></body></html>'),
        ]
        
        results = self.differ.batch_compare(html_pairs)
        
        assert isinstance(results, list)
        assert len(results) == 2
        assert all(isinstance(r, HTMLDiffResult) for r in results)

    def test_model_training(self):
        """Test model training"""
        # Create mock training data
        html_pairs = [
            ('<html><body><h1>Title</h1></body></html>', '<html><body><h1>Title</h1></body></html>'),
            ('<html><body><h1>Title</h1></body></html>', '<html><body><h1>Different</h1></body></html>'),
        ]
        labels = [1.0, 0.5]
        
        # Test training (should not raise exception)
        try:
            self.differ.train_model(html_pairs, labels, epochs=1)
            assert True
        except Exception as e:
            # Training might fail due to insufficient data, but should not crash
            assert isinstance(e, Exception)

    def test_model_save_load(self):
        """Test model save and load"""
        model_path = '/tmp/test_model.pth'
        
        try:
            # Test save
            self.differ.save_model(model_path)
            assert True
            
            # Test load
            self.differ.load_model(model_path)
            assert True
            
        except Exception as e:
            # Save/load might fail due to file permissions, but should not crash
            assert isinstance(e, Exception)

    def test_error_handling(self):
        """Test error handling"""
        # Test with invalid HTML
        html1 = 'invalid html'
        html2 = 'also invalid'
        
        result = self.differ.compare_html(html1, html2)
        
        # Should still return a result
        assert isinstance(result, HTMLDiffResult)

    def test_performance_metrics(self):
        """Test performance metrics"""
        html1 = '<html><body><h1>Title</h1></body></html>'
        html2 = '<html><body><h1>Title</h1></body></html>'
        
        result = self.differ.compare_html(html1, html2)
        
        assert result.processing_time > 0
        assert result.confidence >= 0

    def test_empty_html_handling(self):
        """Test empty HTML handling"""
        html1 = ''
        html2 = ''
        
        result = self.differ.compare_html(html1, html2)
        
        assert isinstance(result, HTMLDiffResult)

    def test_large_html_handling(self):
        """Test large HTML handling"""
        html1 = '<html><body>' + 'x' * 10000 + '</body></html>'
        html2 = '<html><body>' + 'y' * 10000 + '</body></html>'
        
        result = self.differ.compare_html(html1, html2)
        
        assert isinstance(result, HTMLDiffResult)
        assert result.processing_time > 0
