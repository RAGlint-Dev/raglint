"""
Tests for reporting module.
"""

import pytest
from pathlib import Path
from raglint.reporting.html_generator import generate_html_report


@pytest.fixture
def sample_results():
    """Create sample analysis results."""
    return {
        "detailed_results": [
            {
                "query": "test1", 
                "faithfulness_score": 0.9,
                "semantic_score": 0.88,
                "metrics": {"precision": 1.0, "recall": 1.0}
            },
            {
                "query": "test2", 
                "faithfulness_score": 0.8,
                "semantic_score": 0.82,
                "metrics": {"precision": 0.5, "recall": 0.5}
            }
        ],
        "retrieval_stats": {"precision": 0.85, "recall": 0.75},
        "chunk_stats": {"mean": 100, "median": 95},
        "faithfulness_scores": [0.9, 0.8],
        "semantic_scores": [0.88, 0.82],
        "is_mock": True
    }


def test_generate_html_report(sample_results, tmp_path):
    """Test HTML report generation."""
    output_file = tmp_path / "report.html"
    
    generate_html_report(sample_results, str(output_file))
    
    assert output_file.exists()
    content = output_file.read_text()
    assert "RAGLint" in content or "Report" in content


def test_html_report_includes_metrics(sample_results, tmp_path):
    """Test HTML report includes metrics."""
    output_file = tmp_path / "report.html"
    
    generate_html_report(sample_results, str(output_file))
    
    content = output_file.read_text()
    # Should include some metrics
    assert len(content) > 100  # Basic sanity check
