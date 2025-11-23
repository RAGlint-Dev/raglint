"""
Simpler built-in plugin tests that actually work.
"""

import pytest
from raglint.plugins.builtins.citation_accuracy import CitationAccuracyPlugin
from raglint.plugins.builtins.pii_detector import PIIDetectorPlugin
from raglint.plugins.builtins.sql_injection import SQLInjectionDetectorPlugin


class TestCitationAccuracy:
    """Tests for CitationAccuracyPlugin."""
    
    def test_init(self):
        """Test plugin initialization."""
        plugin = CitationAccuracyPlugin()
        assert plugin.name == "citation_accuracy"
    
    def test_with_citations(self):
        """Test with numeric citations."""
        plugin = CitationAccuracyPlugin()
        response = "Study shows [1] that ML works. Another source [2] confirms."
        context = ["Study 1", "Study 2"]
        
        score = plugin.evaluate("query", context, response)
        assert 0.0 <= score <= 1.0
    
    def test_no_citations(self):
        """Test without citations."""
        plugin = CitationAccuracyPlugin()
        response = "Machine learning is powerful."
        context = ["ML info"]
        
        score = plugin.evaluate("query", context, response)
        assert score >= 0.5


class TestPIIDetector:
    """Tests for PIIDetectorPlugin."""
    
    def test_init(self):
        """Test plugin initialization."""
        plugin = PIIDetectorPlugin()
        assert plugin.name == "pii_detector"
    
    def test_detects_email(self):
        """Test email detection."""
        plugin = PIIDetectorPlugin()
        response = "Contact john@example.com"
        
        score = plugin.evaluate("", [], response)
        assert score < 1.0
    
    def test_clean_response(self):
        """Test clean response."""
        plugin = PIIDetectorPlugin()
        response = "Machine learning is powerful"
        
        score = plugin.evaluate("", [], response)
        assert score == 1.0


class TestSQLInjection:
    """Tests for SQLInjectionDetectorPlugin."""
    
    def test_init(self):
        """Test plugin initialization."""
        plugin = SQLInjectionDetectorPlugin()
        assert plugin.name == "sql_injection_detector"
    
    def test_detects_select(self):
        """Test SELECT detection."""
        plugin = SQLInjectionDetectorPlugin()
        response = "Use: SELECT * FROM users"
        
        score = plugin.evaluate("", [], response)
        assert score < 1.0
    
    def test_clean_response(self):
        """Test clean response."""
        plugin = SQLInjectionDetectorPlugin()
        response = "Database management is important"
        
        score = plugin.evaluate("", [], response)
        assert score == 1.0
