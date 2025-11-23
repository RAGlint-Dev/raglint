"""
Tests for retrieval metrics.
"""

import pytest
from raglint.metrics.retrieval import calculate_precision, calculate_recall, calculate_f1


def test_calculate_precision_perfect():
    """Test precision with perfect retrieval."""
    retrieved = ["doc1", "doc2", "doc3"]
    relevant = ["doc1", "doc2", "doc3"]
    
    precision = calculate_precision(retrieved, relevant)
    assert precision == 1.0


def test_calculate_precision_partial():
    """Test precision with partial match."""
    retrieved = ["doc1", "doc2", "doc3", "doc4"]
    relevant = ["doc1", "doc2"]
    
    precision = calculate_precision(retrieved, relevant)
    assert precision == 0.5  # 2 relevant out of 4 retrieved


def test_calculate_precision_zero():
    """Test precision with no relevant docs retrieved."""
    retrieved = ["doc1", "doc2"]
    relevant = ["doc3", "doc4"]
    
    precision = calculate_precision(retrieved, relevant)
    assert precision == 0.0


def test_calculate_recall_perfect():
    """Test recall with perfect retrieval."""
    retrieved = ["doc1", "doc2", "doc3"]
    relevant = ["doc1", "doc2", "doc3"]
    
    recall = calculate_recall(retrieved, relevant)
    assert recall == 1.0


def test_calculate_recall_partial():
    """Test recall with partial retrieval."""
    retrieved = ["doc1", "doc2"]
    relevant = ["doc1", "doc2", "doc3", "doc4"]
    
    recall = calculate_recall(retrieved, relevant)
    assert recall == 0.5  # Found 2 out of 4 relevant


def test_calculate_recall_zero():
    """Test recall when no relevant docs found."""
    retrieved = ["doc1", "doc2"]
    relevant = ["doc3", "doc4"]
    
    recall = calculate_recall(retrieved, relevant)
    assert recall == 0.0


def test_calculate_f1_perfect():
    """Test F1 score with perfect retrieval."""
    retrieved = ["doc1", "doc2"]
    relevant = ["doc1", "doc2"]
    
    f1 = calculate_f1(retrieved, relevant)
    assert f1 == 1.0


def test_calculate_f1_balanced():
    """Test F1 score with balanced precision/recall."""
    retrieved = ["doc1", "doc2", "doc3"]
    relevant = ["doc1", "doc2", "doc4"]
    
    f1 = calculate_f1(retrieved, relevant)
    # Precision = 2/3, Recall = 2/3, F1 = 2/3
    assert 0.65 < f1 < 0.68


def test_empty_lists():
    """Test metrics with empty lists."""
    precision = calculate_precision([], [])
    recall = calculate_recall([], [])
    f1 = calculate_f1([], [])
    
    assert precision == 0.0
    assert recall == 0.0
    assert f1 == 0.0
