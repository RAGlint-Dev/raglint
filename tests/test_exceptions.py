"""
Tests for custom exceptions.
"""

import pytest
from raglint.exceptions import (
    RAGLintError,
    GenerationError,
    PluginError,
    LLMError
)


def test_raglint_error():
    """Test base RAGLintError exception."""
    with pytest.raises(RAGLintError):
        raise RAGLintError("Test error")


def test_generation_error():
    """Test GenerationError exception."""
    with pytest.raises(GenerationError):
        raise GenerationError("Generation failed")
    
    # Should also catch as RAGLintError
    with pytest.raises(RAGLintError):
        raise GenerationError("Generation failed")


def test_plugin_error():
    """Test PluginError exception."""
    with pytest.raises(PluginError):
        raise PluginError("test-plugin", "Plugin failed")
    
    # Should also catch as RAGLintError
    with pytest.raises(RAGLintError):
        raise PluginError("test-plugin", "Plugin failed")


def test_llm_error():
    """Test LLMError exception."""
    with pytest.raises(LLMError):
        raise LLMError("openai", "LLM call failed")
    
    # Should also catch as RAGLintError
    with pytest.raises(RAGLintError):
        raise LLMError("openai", "LLM call failed")


def test_exception_with_message():
    """Test exceptions carry messages correctly."""
    error_msg = "Custom error message"
    
    try:
        raise GenerationError(error_msg)
    except GenerationError as e:
        assert str(e) == error_msg
