"""
Comprehensive tests for RAGPipelineAnalyzer in core.py
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from raglint.core import RAGPipelineAnalyzer, AnalysisResult


@pytest.fixture
def sample_data():
    return [
        {
            "query": "What is machine learning?",
            "retrieved_contexts": ["ML is a subset of AI", "ML uses statistical models"],
            "ground_truth_contexts": ["ML is a subset of AI"],
            "response": "Machine learning is a subset of artificial intelligence."
        },
        {
            "query": "Explain neural networks",
            "retrieved_contexts": ["Neural networks are computing systems"],
            "response": "Neural networks are inspired by biological neural networks."
        }
    ]


def test_analyzer_initialization_no_smart_metrics():
    """Test analyzer can be initialized without smart metrics."""
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=False)
    assert analyzer.use_smart_metrics is False
    assert analyzer.semantic_matcher is None
    assert analyzer.faithfulness_scorer is None


def test_analyzer_initialization_with_config():
    """Test analyzer initialization with configuration."""
    config = {"provider": "mock", "metrics": ["faithfulness"]}
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=False, config=config)
    assert analyzer.config == config


def test_analyze_empty_dataset():
    """Test analyzing empty dataset returns valid results."""
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=False)
    result = analyzer.analyze([])
    
    assert isinstance(result, AnalysisResult)
    assert len(result.detailed_results) == 0
    assert result.retrieval_stats['precision'] == 0.0


def test_analyze_without_smart_metrics(sample_data):
    """Test basic analysis without smart metrics."""
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=False)
    result = analyzer.analyze(sample_data)
    
    assert isinstance(result, AnalysisResult)
    assert len(result.detailed_results) == 2
    assert result.chunk_stats is not None
    assert 'precision' in result.retrieval_stats


def test_analyze_with_ground_truth(sample_data):
    """Test analysis calculates retrieval metrics when ground truth provided."""
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=False)
    result = analyzer.analyze(sample_data[:1])  # First item has ground truth
    
    assert result.retrieval_stats['precision'] > 0.0
    assert result.retrieval_stats['recall'] > 0.0


@pytest.mark.asyncio
async def test_analyze_async_without_smart_metrics(sample_data):
    """Test async analysis without smart metrics."""
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=False)
    result = await analyzer.analyze_async(sample_data, show_progress=False)
    
    assert isinstance(result, AnalysisResult)
    assert len(result.detailed_results) == 2


@patch('raglint.core.FaithfulnessScorer')
@patch('raglint.core.SemanticMatcher')
def test_analyze_with_smart_metrics_mock(mock_matcher, mock_faithfulness, sample_data):
    """Test analysis with mocked smart metrics."""
    # Mock the scorer
    mock_scorer_instance = MagicMock()
    mock_scorer_instance.score.return_value = (0.9, "Good faithfulness")
    mock_faithfulness.return_value = mock_scorer_instance
    
    # Mock semantic matcher
    mock_matcher_instance = MagicMock()
    mock_matcher_instance.calculate_similarity.return_value = 0.8
    mock_matcher.return_value = mock_matcher_instance
    
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=True, config={"provider": "mock"})
    result = analyzer.analyze(sample_data[:1])  # Analyze one item
    
    assert len(result.faithfulness_scores) > 0
    assert len(result.semantic_scores) > 0


@pytest.mark.asyncio
@patch('raglint.core.FaithfulnessScorer')
async def test_analyze_async_with_smart_metrics(mock_faithfulness, sample_data):
    """Test async analysis with smart metrics."""
    # Mock the async scorer
    mock_scorer_instance = MagicMock()
    mock_scorer_instance.ascore = AsyncMock(return_value=(0.9, "Good"))
    mock_faithfulness.return_value = mock_scorer_instance
    
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=True, config={"provider": "mock"})
    result = await analyzer.analyze_async(sample_data[:1], show_progress=False)
    
    assert isinstance(result, AnalysisResult)
    assert len(result.faithfulness_scores) > 0


def test_analyze_handles_missing_fields():
    """Test analyzer handles items with missing fields gracefully."""
    incomplete_data = [
        {"query": "test"},  # Missing contexts and response
        {"response": "answer"},  # Missing query
    ]
    
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=False)
    result = analyzer.analyze(incomplete_data)
    
    assert isinstance(result, AnalysisResult)
    assert len(result.detailed_results) == 2


def test_analyze_calculates_chunk_stats():
    """Test chunk statistics are calculated correctly."""
    data = [
        {
            "query": "test",
            "retrieved_contexts": ["short", "medium length text", "a very long piece of text here"],
            "response": "answer"
        }
    ]
    
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=False)
    result = analyzer.analyze(data)
    
    assert 'mean' in result.chunk_stats
    assert 'median' in result.chunk_stats
    assert result.chunk_stats['mean'] > 0


def test_is_mock_flag():
    """Test is_mock flag is set correctly based on config."""
    analyzer_mock = RAGPipelineAnalyzer(use_smart_metrics=False, config={"provider": "mock"})
    result_mock = analyzer_mock.analyze([{"query": "test", "retrieved_contexts": [], "response": "test"}])
    assert result_mock.is_mock is True
    
    analyzer_openai = RAGPipelineAnalyzer(use_smart_metrics=False, config={"provider": "openai"})
    result_openai = analyzer_openai.analyze([{"query": "test", "retrieved_contexts": [], "response": "test"}])
    assert result_openai.is_mock is False
