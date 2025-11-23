"""
Tests for HTML report generation.
"""


import pytest

from raglint.core import AnalysisResult
from raglint.reporting.html_generator import generate_html_report


@pytest.fixture
def sample_results():
    """Create sample analysis results."""
    return AnalysisResult(
        chunk_stats={"mean": 50.0, "std": 10.0, "min": 20.0, "max": 100.0},
        retrieval_stats={
            "precision": 0.8,
            "recall": 0.9,
            "mrr": 0.85,
            "ndcg": 0.88,
        },
        detailed_results=[
            {
                "query": "Test query 1",
                "metrics": {"precision": 0.8, "recall": 0.9, "mrr": 0.85, "ndcg": 0.88},
                "coherence": [0.7, 0.8],
                "semantic_score": 0.9,
                "faithfulness_score": 0.95,
            },
            {
                "query": "Test query 2",
                "metrics": {"precision": 0.7, "recall": 0.8, "mrr": 0.75, "ndcg": 0.78},
                "coherence": [0.6, 0.7],
                "semantic_score": 0.85,
                "faithfulness_score": 0.9,
            },
        ],
        semantic_scores=[0.9, 0.85],
        faithfulness_scores=[0.95, 0.9],
        is_mock=False,
    )


def test_generate_html_report_basic(sample_results, tmp_path):
    """Test basic HTML report generation."""
    output_path = tmp_path / "test_report.html"

    generate_html_report(sample_results, str(output_path))

    assert output_path.exists()
    assert output_path.stat().st_size > 0


def test_generate_html_report_content(sample_results, tmp_path):
    """Test HTML report contains expected content."""
    output_path = tmp_path / "test_report.html"

    generate_html_report(sample_results, str(output_path))

    with open(output_path) as f:
        content = f.read()

    # Check for key elements
    assert "RAGLint" in content
    assert "Chunk Size Mean" in content or "50" in content
    assert "Precision" in content
    assert "chart.js" in content.lower()  # Charts should be included
    assert "radarChart" in content
    assert "barChart" in content


def test_generate_html_report_mock_mode(sample_results, tmp_path):
    """Test HTML  report shows mock mode indicator."""
    sample_results.is_mock = True
    output_path = tmp_path / "test_report.html"

    generate_html_report(sample_results, str(output_path))

    with open(output_path) as f:
        content = f.read()

    assert "MOCK" in content or "mock" in content


def test_generate_html_report_empty_scores(tmp_path):
    """Test HTML report generation with empty scores."""
    empty_results = AnalysisResult(
        chunk_stats={"mean": 0.0, "std": 0.0, "min": 0.0, "max": 0.0},
        retrieval_stats={"precision": 0.0, "recall": 0.0, "mrr": 0.0, "ndcg": 0.0},
        detailed_results=[],
        semantic_scores=[],
        faithfulness_scores=[],
        is_mock=False,
    )

    output_path = tmp_path / "test_report_empty.html"
    generate_html_report(empty_results, str(output_path))

    assert output_path.exists()
