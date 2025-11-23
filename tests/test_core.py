"""
Tests for core RAG pipeline analysis functionality
"""

import pytest
from raglint.core import RAGPipelineAnalyzer, AnalysisResult
from raglint.config import Config

def test_analyzer_initialization(mock_config):
    """Test that analyzer initializes correctly"""
    analyzer = RAGPipelineAnalyzer(mock_config)
    
    # Analyzer is initialized
    assert analyzer is not None

def test_analyze_with_sample_data(sample_data, mock_config):
    """Test basic analysis with sample data"""
    analyzer = RAGPipelineAnalyzer(mock_config)
    
    results = analyzer.analyze(sample_data)
    
    assert results is not None
    assert isinstance(results, AnalysisResult)
    assert hasattr(results, 'detailed_results')
    assert len(results.detailed_results) == 2

def test_chunking_metrics(sample_data, mock_config):
    """Test chunking quality metrics"""
    analyzer = RAGPipelineAnalyzer(mock_config)
    
    # Enable only chunking metrics
    mock_config.metrics = {"chunking": True, "faithfulness": False, "semantic": False, "retrieval": False}
    
    results = analyzer.analyze(sample_data)
    
    # Check that results exist
    assert hasattr(results, 'chunk_stats')
    assert results.chunk_stats is not None

def test_retrieval_metrics(sample_data, mock_config):
    """Test retrieval quality metrics"""
    analyzer = RAGPipelineAnalyzer(mock_config)
    
    # Enable only retrieval metrics
    mock_config.metrics = {"chunking": False, "faithfulness": False, "semantic": False, "retrieval": True}
    
    results = analyzer.analyze(sample_data)
    
    # Check retrieval stats exist
    assert hasattr(results, 'retrieval_stats')
    assert results.retrieval_stats is not None

def test_empty_data():
    """Test handling of empty data"""
    analyzer = RAGPipelineAnalyzer(Config())
    
    results = analyzer.analyze([])
    
    assert results is not None
    assert hasattr(results, 'detailed_results')
    assert len(results.detailed_results) == 0

def test_invalid_data_structure():
    """Test handling of invalid data structure"""
    analyzer = RAGPipelineAnalyzer(Config())
    
    # Missing required fields
    invalid_data = [{"query": "test"}]  # No response
    
    # Should not crash
    results = analyzer.analyze(invalid_data)
    assert results is not None

@pytest.mark.skip(reason="Requires OpenAI API key")
def test_faithfulness_with_real_api(sample_data):
    """Test faithfulness metric with real OpenAI API"""
    config = Config()
    config.metrics["faithfulness"] = True
    
    analyzer = RAGPipelineAnalyzer(config)
    results = analyzer.analyze(sample_data[:1])  # Test with one item
    
    assert len(results.detailed_results) > 0
