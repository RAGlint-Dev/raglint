"""
Tests for instrumentation and tracking.
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch
from raglint.instrumentation import watch, Monitor


def test_monitor_singleton():
    """Test Monitor is a singleton."""
    m1 = Monitor()
    m2 = Monitor()
    assert m1 is m2
    assert m1.enabled is True


def test_watch_decorator():
    """Test watch decorator on function."""
    @watch(name="test_function")
    def my_function(x):
        return x * 2
    
    result = my_function(5)
    assert result == 10


def test_watch_decorator_with_tracking():
    """Test watch decorator tracks calls."""
    call_count = 0
    
    @watch(name="counted_function")
    def counted_func():
        nonlocal call_count
        call_count += 1
        return "done"
    
    counted_func()
    counted_func()
    assert call_count == 2


@pytest.mark.asyncio
async def test_watch_async_support():
    """Test watch supports async functions."""
    @watch(name="async_function")
    async def async_func():
        return "async_result"
    
    result = await async_func()
    assert result == "async_result"


def test_monitor_disable_enable():
    """Test disabling and enabling monitor."""
    monitor = Monitor()
    monitor.disable()
    assert monitor.enabled is False
    
    monitor.enable()
    assert monitor.enabled is True

