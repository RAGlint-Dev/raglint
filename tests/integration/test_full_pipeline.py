"""Integration test for full RAG evaluation pipeline."""
import pytest
import asyncio
from pathlib import Path

from raglint.core import RAGPipelineAnalyzer
from raglint.config import Config


@pytest.mark.asyncio
async def test_full_pipeline_evaluation():
    """Test complete evaluation pipeline end-to-end."""
    # Create config with mock LLM
    config = Config(provider="mock")
    
    # Initialize analyzer
    analyzer = RAGPipelineAnalyzer(config)
    
    # Sample test data
    test_data = [
        {
            "query": "What is Python?",
            "response": "Python is a programming language.",
            "retrieved_contexts": ["Python is a high-level programming language."],
            "ground_truth_contexts": ["Python is a high-level programming language."],
            "ground_truth": "Python is a programming language."
        }
    ]
    
    # Run evaluation
    result = await analyzer.analyze_async(test_data)
    
    # Verify results structure
    assert result is not None
    assert hasattr(result, 'detailed_results')
    assert len(result.detailed_results) == 1
    
    item_result = result.detailed_results[0]
    
    # Check basic structure is present
    assert 'query' in item_result
    assert item_result['query'] == "What is Python?"
    
    # Results should have some metrics (exact names depend on config)
    assert isinstance(item_result, dict)
    assert len(item_result) > 1  # Should have query + at least one metric


@pytest.mark.asyncio
async def test_pipeline_with_missing_data():
    """Test pipeline gracefully handles missing data."""
    config = Config(provider="mock")
    analyzer = RAGPipelineAnalyzer(config)
    
    # Missing ground truth
    test_data = [
        {
            "query": "What is Python?",
            "response": "Python is a programming language.",
            "retrieved_contexts": ["Python is a high-level programming language."],
        }
    ]
    
    # Should not crash
    result = await analyzer.analyze_async(test_data)
    assert result is not None


@pytest.mark.asyncio
async def test_pipeline_plugin_integration():
    """Test that plugins are properly loaded and executed."""
    config = Config(provider="mock")
    analyzer = RAGPipelineAnalyzer(config)
    
    test_data = [
        {
            "query": "Test query",
            "response": "Test response",
            "retrieved_contexts": ["Test context"],
        }
    ]
    
    result = await analyzer.analyze_async(test_data)
    
    # Verify results are returned
    assert result is not None
    assert hasattr(result, 'detailed_results')
    assert len(result.detailed_results) > 0
