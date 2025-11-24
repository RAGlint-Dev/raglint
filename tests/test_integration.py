"""
Integration tests for the full RAG pipeline analysis.
"""

import json

import pytest

from raglint.core import RAGPipelineAnalyzer


@pytest.fixture
def sample_data():
    """Sample RAG data for testing."""
    return [
        {
            "query": "What is RAG?",
            "retrieved_contexts": [
                "RAG stands for Retrieval-Augmented Generation.",
                "It combines retrieval with generation.",
            ],
            "response": "RAG is a technique that combines retrieval and generation.",
            "ground_truth_contexts": ["RAG stands for Retrieval-Augmented Generation."],
        },
        {
            "query": "How does it work?",
            "retrieved_contexts": [
                "First, relevant documents are retrieved.",
                "Then, the LLM generates a response.",
            ],
            "response": "It retrieves documents and generates responses.",
            "ground_truth_contexts": ["First, relevant documents are retrieved."],
        },
    ]


@pytest.fixture
def sample_data_file(sample_data, tmp_path):
    """Create a temporary JSON file with sample data."""
    file_path = tmp_path / "test_data.json"
    with open(file_path, "w") as f:
        json.dump(sample_data, f)
    return file_path


def test_basic_analysis(sample_data):
    """Test basic analysis without smart metrics."""
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=False)
    results = analyzer.analyze(sample_data)

    assert results is not None
    assert hasattr(results, "chunk_stats")
    assert hasattr(results, "retrieval_stats")
    assert hasattr(results, "detailed_results")

    # Check chunk stats
    assert "mean" in results.chunk_stats
    assert results.chunk_stats["mean"] > 0

    # Check retrieval stats
    assert "precision" in results.retrieval_stats
    assert "recall" in results.retrieval_stats
    assert "mrr" in results.retrieval_stats
    assert "ndcg" in results.retrieval_stats

    # Check detailed results
    assert len(results.detailed_results) == 2


def test_smart_analysis_mock_mode(sample_data):
    """Test analysis with smart metrics in mock mode."""
    config = {"provider": "mock"}
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=True, config=config)
    results = analyzer.analyze(sample_data)

    assert results is not None
    assert results.is_mock is True

    # Mock mode should return high scores for smart metrics
    # Note: Semantic matcher uses real embeddings, so scores may not be exactly 1.0
    assert len(results.semantic_scores) == 2
    assert all(score >= 0.8 for score in results.semantic_scores), f"Semantic scores too low: {results.semantic_scores}"
    assert len(results.faithfulness_scores) == 2
    assert all(score == 1.0 for score in results.faithfulness_scores)


def test_empty_data():
    """Test handling of empty data."""
    analyzer = RAGPipelineAnalyzer()
    results = analyzer.analyze([])

    assert results is not None
    assert len(results.detailed_results) == 0


def test_missing_ground_truth(sample_data):
    """Test analysis when ground truth is missing."""
    data_without_gt = [
        {
            "query": "Test query",
            "retrieved_contexts": ["Context 1"],
            "response": "Response 1",
        }
    ]

    analyzer = RAGPipelineAnalyzer()
    results = analyzer.analyze(data_without_gt)

    assert results is not None
    # Should still complete without errors


def test_malformed_data():
    """Test handling of malformed data."""
    malformed = [
        {
            "query": "Test",
            # Missing retrieved_contexts
            "response": "Test response",
        }
    ]

    analyzer = RAGPipelineAnalyzer()
    # Should not crash, may return partial results
    results = analyzer.analyze(malformed)
    assert results is not None


@pytest.mark.asyncio
async def test_async_compatibility():
    """Test that the analyzer can be used in async context."""
    # This is a placeholder for future async support
    pass
