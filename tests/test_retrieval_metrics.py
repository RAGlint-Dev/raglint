"""
Tests for retrieval metrics.
"""

import pytest
from raglint.metrics.retrieval import calculate_retrieval_metrics


def test_calculate_precision_perfect():
    """Test precision with perfect retrieval."""
    retrieved = ["doc1", "doc2", "doc3"]
    relevant = ["doc1", "doc2", "doc3"]
    
    metrics = calculate_retrieval_metrics(retrieved, relevant)
    assert metrics["precision"] == 1.0


def test_calculate_precision_partial():
    """Test precision with partial match."""
    retrieved = ["doc1", "doc2", "doc3", "doc4"]
    relevant = ["doc1", "doc2"]
    
    metrics = calculate_retrieval_metrics(retrieved, relevant)
    assert metrics["precision"] == 0.5  # 2 relevant out of 4 retrieved


def test_calculate_precision_zero():
    """Test precision with no relevant docs retrieved."""
    retrieved = ["doc1", "doc2"]
    relevant = ["doc3", "doc4"]
    
    metrics = calculate_retrieval_metrics(retrieved, relevant)
    assert metrics["precision"] == 0.0


def test_calculate_recall_perfect():
    """Test recall with perfect retrieval."""
    retrieved = ["doc1", "doc2", "doc3"]
    relevant = ["doc1", "doc2", "doc3"]
    
    metrics = calculate_retrieval_metrics(retrieved, relevant)
    assert metrics["recall"] == 1.0


def test_calculate_recall_partial():
    """Test recall with partial retrieval."""
    retrieved = ["doc1", "doc2"]
    relevant = ["doc1", "doc2", "doc3", "doc4"]
    
    metrics = calculate_retrieval_metrics(retrieved, relevant)
    assert metrics["recall"] == 0.5  # Found 2 out of 4 relevant


def test_calculate_recall_zero():
    """Test recall when no relevant docs found."""
    retrieved = ["doc1", "doc2"]
    relevant = ["doc3", "doc4"]
    
    metrics = calculate_retrieval_metrics(retrieved, relevant)
    assert metrics["recall"] == 0.0


def test_empty_lists():
    """Test metrics with empty lists."""
    metrics = calculate_retrieval_metrics([], [])
    
    assert metrics["precision"] == 0.0
    assert metrics["recall"] == 0.0
    assert metrics["mrr"] == 0.0
    assert metrics["ndcg"] == 0.0
