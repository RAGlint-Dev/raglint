import pytest
from unittest.mock import MagicMock, patch
from raglint.core import RAGPipelineAnalyzer

@pytest.fixture
def mock_config():
    return {
        "provider": "mock",
        "metrics": ["faithfulness", "relevance"],
        "thresholds": {"faithfulness": 0.5}
    }

def test_analyzer_initialization(mock_config):
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=True, config=mock_config)
    assert analyzer.use_smart_metrics is True
    assert analyzer.config == mock_config

def test_analyze_empty_data():
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=False)
    results = analyzer.analyze([])
    assert len(results.detailed_results) == 0

def test_analyze_basic_flow():
    data = [
        {
            "query": "test query",
            "retrieved_contexts": ["context 1", "context 2"],
            "response": "test response"
        }
    ]
    
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=False)
    results = analyzer.analyze(data)
    
    assert len(results.detailed_results) == 1
    assert results.retrieval_stats['recall'] == 0.0 # No ground truth

@patch("raglint.metrics.faithfulness.FaithfulnessScorer.score")
def test_analyze_smart_metrics(mock_score):
    mock_score.return_value = (0.9, "Good")
    
    data = [
        {
            "query": "test query",
            "retrieved_contexts": ["context 1"],
            "response": "test response"
        }
    ]
    
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)
    results = analyzer.analyze(data)
    
    assert len(results.faithfulness_scores) == 1
    assert results.faithfulness_scores[0] == 0.9
