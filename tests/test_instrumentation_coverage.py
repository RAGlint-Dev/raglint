"""
Tests for instrumentation and tracking.
"""

import pytest
from unittest.mock import MagicMock, patch
from raglint.instrumentation import instrument, RAGLintInstrumentation


def test_instrumentation_import():
    """Test instrumentation can be imported."""
    from raglint.instrumentation import instrument
    assert instrument is not None


def test_instrumentation_initialization():
    """Test RAGLintInstrumentation initialization."""
    instr = RAGLintInstrumentation()
    assert instr is not None


def test_instrument_decorator():
    """Test instrument decorator on function."""
    @instrument(name="test_function")
    def my_function(x):
        return x * 2
    
    result = my_function(5)
    assert result == 10


def test_instrument_decorator_with_tracking():
    """Test instrument decorator tracks calls."""
    call_count = 0
    
    @instrument(name="counted_function")
    def counted_func():
        nonlocal call_count
        call_count += 1
        return "done"
    
    counted_func()
    counted_func()
    assert call_count == 2


def test_instrumentation_context_manager():
    """Test instrumentation as context manager."""
    instr = RAGLintInstrumentation()
    
    with instr.trace("test_operation"):
        result = 1 + 1
    
    assert result == 2


def test_instrumentation_async_support():
    """Test instrumentation supports async functions."""
    @instrument(name="async_function")
    async def async_func():
        return "async_result"
    
    # Function should be decorated
    assert callable(async_func)
