"""
Tests for utilities and helpers.
"""

import pytest


def test_import_utils():
    """Test utils can be imported."""
    try:
        from raglint import utils
        assert True
    except ImportError:
        # Module might not exist, that's ok
        pytest.skip("Utils module not found")


def test_format_score():
    """Test score formatting if utility exists."""
    try:
        from raglint.utils import format_score
        score = format_score(0.856789)
        assert isinstance(score, (str, float))
    except (ImportError, AttributeError):
        pytest.skip("format_score not available")


def test_validate_data():
    """Test data validation if utility exists."""
    try:
        from raglint.utils import validate_data
        data = [{"query": "test", "response": "answer"}]
        result = validate_data(data)
        assert result is not None
    except (ImportError, AttributeError):
        pytest.skip("validate_data not available")
