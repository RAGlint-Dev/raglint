"""
Comprehensive tests for built-in plugins.
"""

import pytest
from raglint.plugins.builtins.citation_accuracy import CitationAccuracyPlugin
from raglint.plugins.builtins.pii_detector import PIIDetectorPlugin
from raglint.plugins.builtins.sql_injection import SQLInjectionDetectorPlugin
from raglint.plugins.builtins.hallucination import HallucinationPlugin
from raglint.plugins.builtins.bias_detector import BiasDetectorPlugin


# Citation Accuracy Tests
def test_citation_accuracy_plugin_init():
    """Test CitationAccuracyPlugin initialization."""
    plugin = CitationAccuracyPlugin()
    assert plugin.name == "citation_accuracy"
    assert plugin.version is not None


def test_citation_accuracy_with_numeric_citations():
    """Test citation accuracy with [1], [2] style citations."""
    plugin = CitationAccuracyPlugin()
    
    response = "According to the study [1], machine learning is powerful. Another source [2] confirms this."
    context = ["Study about ML power", "Confirmation source"]
    
    score = plugin.evaluate("query", context, response)
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_citation_accuracy_no_citations():
    """Test citation accuracy with no citations."""
    plugin = CitationAccuracyPlugin()
    
    response = "Machine learning is a powerful tool."
    context = ["ML description"]
    
    score = plugin.evaluate("query", context, response)
    assert score >= 0.5  # Should be okay if no claims


# PII Detector Tests
def test_pii_detector_plugin_init():
    """Test PIIDetectorPlugin initialization."""
    plugin = PIIDetectorPlugin()
    assert plugin.name == "pii_detector"


@pytest.mark.asyncio
async def test_pii_detector_finds_email():
    """Test PII detector finds email addresses."""
    plugin = PIIDetectorPlugin()
    
    response = "Contact me at john@example.com for more info."
    result = await plugin.calculate_async(query="query", response=response, contexts=[])
    
    assert result["score"] < 1.0  # Should detect PII


@pytest.mark.asyncio
async def test_pii_detector_finds_phone():
    """Test PII detector finds phone numbers."""
    plugin = PIIDetectorPlugin()
    
    response = "Call us at 555-123-4567 for support."
    result = await plugin.calculate_async(query="query", response=response, contexts=[])
    
    assert result["score"] < 1.0  # Should detect PII


@pytest.mark.asyncio
async def test_pii_detector_clean_response():
    """Test PII detector with clean response."""
    plugin = PIIDetectorPlugin()
    
    response = "Machine learning is a subset of artificial intelligence."
    result = await plugin.calculate_async(query="query", response=response, contexts=[])
    
    assert result["score"] == 1.0  # No PII


# SQL Injection Detector Tests
def test_sql_injection_plugin_init():
    """Test SQLInjectionDetectorPlugin initialization."""
    plugin = SQLInjectionDetectorPlugin()
    assert plugin.name == "sql_injection_detector"


def test_sql_injection_detects_select():
    """Test SQL injection detector finds SELECT statements."""
    plugin = SQLInjectionDetectorPlugin()
    
    response = "To find records, use: SELECT * FROM users"
    score = plugin.evaluate("query", [], response)
    
    assert score < 1.0  # Should detect SQL


def test_sql_injection_detects_drop():
    """Test SQL injection detector finds DROP statements."""
    plugin = SQLInjectionDetectorPlugin()
    
    response = "Bobby Tables: '; DROP TABLE students; --"
    score = plugin.evaluate("query", [], response)
    
    assert score == 0.0  # Critical SQL injection


def test_sql_injection_clean_response():
    """Test SQL injection detector with clean response."""
    plugin = SQLInjectionDetectorPlugin()
    
    response = "Database management is important for applications."
    score = plugin.evaluate("query", [], response)
    
    assert score == 1.0  # No SQL injection


# Hallucination Detector Tests
def test_hallucination_detector_init():
    """Test HallucinationDetector initialization."""
    plugin = HallucinationPlugin()
    assert plugin.name == "hallucination_score"


@pytest.mark.asyncio
async def test_hallucination_detector_evaluate():
    """Test hallucination detector evaluation."""
    plugin = HallucinationPlugin()
    
    context = ["Python is a programming language"]
    response = "Python is used for machine learning"
    
    result = await plugin.calculate_async(query="query", response=response, contexts=context)
    assert isinstance(result["score"], float)
    assert 0.0 <= result["score"] <= 1.0


# Bias Detector Tests
def test_bias_detector_init():
    """Test BiasDetectorPlugin initialization."""
    plugin = BiasDetectorPlugin()
    assert plugin.name == "bias_detector"


@pytest.mark.asyncio
async def test_bias_detector_evaluate():
    """Test bias detector evaluation."""
    plugin = BiasDetectorPlugin()
    
    response = "Scientists believe that research is important."
    result = await plugin.calculate_async(query="query", response=response, contexts=[])
    
    assert isinstance(result["score"], float)
    assert 0.0 <= result["score"] <= 1.0
