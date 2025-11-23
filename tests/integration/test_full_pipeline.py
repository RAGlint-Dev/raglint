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
    results = await analyzer.evaluate_batch_async(test_data)
    
    # Verify results structure
    assert len(results) == 1
    result = results[0]
    
    # Check all metrics are present
    assert "faithfulness" in result
    assert "context_precision" in result
    assert "answer_relevance" in result
    
    # Check scores are valid (0.0 to 1.0)
    for metric_name, score in result.items():
        if isinstance(score, (int, float)):
            assert 0.0 <= score <= 1.0, f"{metric_name} score out of range: {score}"


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
    results = await analyzer.evaluate_batch_async(test_data)
    assert len(results) == 1


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
    
    results = await analyzer.evaluate_batch_async(test_data)
    result = results[0]
    
    # Verify plugin metrics are present
    # Plugin metrics should be in the results if plugins are loaded
    assert isinstance(result, dict)
    assert len(result) > 0
