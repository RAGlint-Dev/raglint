"""
Tests for chunking metrics.
"""

import pytest
from raglint.metrics.chunking import calculate_chunk_size_distribution


def test_calculate_chunk_stats_basic():
    """Test basic chunk statistics calculation."""
    chunks = ["short", "medium length text", "a much longer piece of text here"]
    
    stats = calculate_chunk_size_distribution(chunks)
    
    assert 'mean' in stats
    assert 'median' in stats
    assert 'std' in stats
    assert stats['mean'] > 0
    assert stats['count'] == 3


def test_calculate_chunk_stats_empty():
    """Test chunk stats with empty list."""
    stats = calculate_chunk_size_distribution([])
    
    assert stats['mean'] == 0
    assert stats['count'] == 0


def test_calculate_chunk_stats_single():
    """Test chunk stats with single chunk."""
    stats = calculate_chunk_size_distribution(["single chunk"])
    
    assert stats['count'] == 1
    assert stats['mean'] > 0


def test_chunk_stats_realistic_data():
    """Test with realistic RAG chunk data."""
    chunks = [
        "Machine learning is a subset of artificial intelligence.",
        "Neural networks are inspired by biological neural networks in the brain.",
        "Deep learning uses multiple layers to progressively extract higher-level features."
    ]
    
    stats = calculate_chunk_size_distribution(chunks)
    
    assert stats['count'] == 3
    assert stats['mean'] > 50  # Reasonable average for sentences
    assert stats['mean'] < 200
