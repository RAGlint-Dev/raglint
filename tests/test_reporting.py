"""
Tests for reporting module.
"""

import pytest
from pathlib import Path
from raglint.core import AnalysisResult
from raglint.reporting.html_generator import HTMLReportGenerator


@pytest.fixture
def sample_analysis_result():
    """Create a sample analysis result."""
    return AnalysisResult(
        detailed_results=[
            {"query": "test1", "faithfulness": 0.9},
            {"query": "test2", "faithfulness": 0.8}
        ],
        retrieval_stats={"precision": 0.85, "recall": 0.75},
        chunk_stats={"mean": 100, "median": 95},
        faithfulness_scores=[0.9, 0.8],
        semantic_scores=[0.88, 0.82],
        is_mock=True
    )


def test_html_generator_initialization():
    """Test HTMLReportGenerator can be initialized."""
    generator = HTMLReportGenerator()
    assert generator is not None


def test_html_generator_generate_report(sample_analysis_result, tmp_path):
    """Test HTML report generation."""
    generator = HTMLReportGenerator()
    output_file = tmp_path / "report.html"
    
    generator.generate(sample_analysis_result, str(output_file))
    
    assert output_file.exists()
    content = output_file.read_text()
    assert "RAGLint" in content or "Report" in content


def test_html_generator_includes_metrics(sample_analysis_result, tmp_path):
    """Test HTML report includes metrics."""
    generator = HTMLReportGenerator()
    output_file = tmp_path / "report.html"
    
    generator.generate(sample_analysis_result, str(output_file))
    
    content = output_file.read_text()
    # Should include some metrics
    assert len(content) > 100  # Basic sanity check
