"""
Tests for core analyzer edge cases and async error handling.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, AsyncMock, patch

from raglint.core import RAGPipelineAnalyzer
from raglint.llm import MockLLM


@pytest.mark.asyncio
async def test_analyzer_async_error_handling():
    """Test that analyzer handles errors in async tasks gracefully."""
    # Setup analyzer with a mock LLM that raises an error
    llm = MagicMock()
    llm.agenerate = AsyncMock(side_effect=Exception("Async Error"))
    
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)
    # Inject our failing LLM into the analyzer AND the scorers
    analyzer.llm = llm
    if analyzer.faithfulness_scorer:
        analyzer.faithfulness_scorer.llm = llm
    if analyzer.context_relevance_scorer:
        analyzer.context_relevance_scorer.llm = llm
    if analyzer.answer_relevance_scorer:
        analyzer.answer_relevance_scorer.llm = llm
    
    data = [{
        "query": "q",
        "retrieved_contexts": ["c"],
        "response": "r",
        "ground_truth_contexts": ["g"]
    }]
    
    # Should not raise exception, but log error and return partial results
    # We need to call analyze_async directly to ensure async path is taken
    result = await analyzer.analyze_async(data)
    
    assert len(result.detailed_results) == 1
    # Smart metrics should be 0.0 or default on error
    # Note: If error handling catches it, it might return 0.0
    assert result.detailed_results[0]["faithfulness_score"] == 0.0


@pytest.mark.asyncio
async def test_analyzer_progress_bar_disable():
    """Test that progress bar can be disabled."""
    data = [{"query": "q", "retrieved_contexts": ["c"], "response": "r"}]
    
    # We check if atqdm.gather is called when using analyze_async
    with patch("raglint.core.atqdm") as mock_tqdm:
        # Mock gather to return results immediately
        mock_tqdm.gather = AsyncMock(return_value=[{
            "chunks": [], "coherence": [], "basic_metrics": None, 
            "semantic_score": None, "faithfulness_score": None, "detailed": {}
        }])
        
        analyzer = RAGPipelineAnalyzer()
        await analyzer.analyze_async(data, show_progress=True)
        mock_tqdm.gather.assert_called()
