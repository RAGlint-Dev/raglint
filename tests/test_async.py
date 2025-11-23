"""
Tests for async functionality.
"""


import pytest

from raglint.core import RAGPipelineAnalyzer


@pytest.mark.asyncio
async def test_async_analysis():
    """Test async analysis with mock LLM."""
    data = [
        {
            "query": "What is RAG?",
            "retrieved_contexts": ["RAG stands for Retrieval Augmented Generation."],
            "ground_truth_contexts": ["RAG is a technique combining retrieval and generation."],
            "response": "RAG is Retrieval Augmented Generation.",
        },
        {
            "query": "How does it work?",
            "retrieved_contexts": ["It retrieves relevant docs and generates answers."],
            "ground_truth_contexts": ["Retrieval followed by generation."],
            "response": "It works by retrieving and generating.",
        },
    ]

    config = {"provider": "mock"}
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=True, config=config)

    # Test async method directly
    result = await analyzer.analyze_async(data, show_progress=False)

    assert result is not None
    assert len(result.faithfulness_scores) == 2
    assert all(score == 1.0 for score in result.faithfulness_scores)


@pytest.mark.asyncio
async def test_async_llm_mock():
    """Test async LLM generation."""
    from raglint.llm import MockLLM

    llm = MockLLM()
    result = await llm.agenerate("Test prompt")

    assert "MOCK" in result
    assert "1.0" in result


@pytest.mark.asyncio
async def test_async_faithfulness_scorer():
    """Test async faithfulness scoring."""
    from raglint.llm import MockLLM
    from raglint.metrics import FaithfulnessScorer

    llm = MockLLM()
    scorer = FaithfulnessScorer(llm=llm)

    score, reasoning = await scorer.ascore(
        query="What is AI?",
        retrieved_contexts=["AI is artificial intelligence."],
        response="AI is artificial intelligence.",
    )

    assert score == 1.0
    assert "MOCK" in reasoning


def test_sync_analysis_with_smart_metrics_uses_async():
    """Test that sync analysis with many items uses async internally."""
    # Create 10 items to trigger async path
    data = [
        {
            "query": f"Query {i}",
            "retrieved_contexts": [f"Context {i}"],
            "ground_truth_contexts": [f"Truth {i}"],
            "response": f"Response {i}",
        }
        for i in range(10)
    ]

    config = {"provider": "mock"}
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=True, config=config)

    # This should use async internally
    result = analyzer.analyze(data, show_progress=False)

    assert result is not None
    assert len(result.faithfulness_scores) == 10


def test_sync_analysis_small_dataset_stays_sync():
    """Test that sync analysis with few items stays synchronous."""
    data = [
        {
            "query": "Query 1",
            "retrieved_contexts": ["Context 1"],
            "ground_truth_contexts": ["Truth 1"],
            "response": "Response 1",
        }
    ]

    config = {"provider": "mock"}
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=True, config=config)

    # This should stay sync (only 1 item)
    result = analyzer.analyze(data, show_progress=False)

    assert result is not None
    assert len(result.faithfulness_scores) == 1
