"""
Tests for error handling and edge cases.
"""


from raglint.core import RAGPipelineAnalyzer
from raglint.llm import LLMFactory
from raglint.metrics.faithfulness import FaithfulnessScorer
from raglint.metrics.semantic import SemanticMatcher


def test_llm_factory_invalid_provider():
    """Test that LLM factory handles invalid providers."""
    from raglint.llm import MockLLM

    # Should default to mock, not raise an error
    llm = LLMFactory.create({"provider": "invalid_provider"})
    assert llm is not None
    assert isinstance(llm, MockLLM)


def test_llm_factory_missing_provider():
    """Test that LLM factory handles missing provider config."""
    # Should default to mock
    llm = LLMFactory.create({})
    assert llm is not None


def test_analyzer_handles_missing_response():
    """Test analyzer handles data with missing response field."""
    data = [
        {
            "query": "Test",
            "retrieved_contexts": ["Context"],
            "ground_truth_contexts": ["Context"],
            # No response field
        }
    ]

    config = {"provider": "mock"}
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=True, config=config)
    results = analyzer.analyze(data)

    assert results is not None
    # Should handle gracefully


def test_analyzer_handles_empty_contexts():
    """Test analyzer handles empty retrieved contexts."""
    data = [
        {
            "query": "Test",
            "retrieved_contexts": [],
            "response": "Response",
            "ground_truth_contexts": ["Ground truth"],
        }
    ]

    analyzer = RAGPipelineAnalyzer()
    results = analyzer.analyze(data)

    assert results is not None


def test_semantic_matcher_empty_lists():
    """Test semantic matcher with empty lists."""
    matcher = SemanticMatcher()
    score = matcher.calculate_similarity([], [])

    assert score == 0.0


def test_semantic_matcher_one_empty_list():
    """Test semantic matcher with one empty list."""
    matcher = SemanticMatcher()
    score = matcher.calculate_similarity(["Context"], [])

    assert score == 0.0


def test_faithfulness_scorer_empty_context():
    """Test faithfulness scorer with empty context."""
    from raglint.llm import MockLLM

    llm = MockLLM()
    scorer = FaithfulnessScorer(llm)

    score, reasoning = scorer.score("Query", [], "Response")

    # Mock should still return 1.0
    assert score == 1.0


def test_retrieval_metrics_empty_ground_truth():
    """Test retrieval metrics with empty ground truth."""
    from raglint.metrics.retrieval import calculate_retrieval_metrics

    metrics = calculate_retrieval_metrics(["doc1", "doc2"], [])

    assert metrics["precision"] == 0.0
    assert metrics["recall"] == 0.0
    assert metrics["mrr"] == 0.0
    assert metrics["ndcg"] == 0.0


def test_retrieval_metrics_empty_retrieved():
    """Test retrieval metrics with empty retrieved docs."""
    from raglint.metrics.retrieval import calculate_retrieval_metrics

    metrics = calculate_retrieval_metrics([], ["doc1"])

    assert metrics["precision"] == 0.0
    assert metrics["recall"] == 0.0


def test_config_validation():
    """Test config validation."""
    from raglint.config import Config

    # Should not crash with nonexistent config
    config = Config.load("nonexistent_file.yml")
    assert config is not None
    assert config.provider is not None
