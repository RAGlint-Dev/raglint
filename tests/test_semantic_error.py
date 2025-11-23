"""
Tests for semantic metrics error handling (missing dependencies).
"""

from unittest.mock import patch
from raglint.metrics.semantic import SemanticMatcher


def test_semantic_matcher_import_error():
    """Test that SemanticMatcher handles missing sentence-transformers gracefully."""
    # Patch the module-level constant to simulate missing dependency
    with patch("raglint.metrics.semantic.HAS_SENTENCE_TRANSFORMERS", False):
        matcher = SemanticMatcher()
        assert matcher.model is None
        assert matcher.enabled is False
        
        # Test calculate_similarity returns 0.0 when model is missing
        score = matcher.calculate_similarity(["context"], ["ground_truth"])
        assert score == 0.0
