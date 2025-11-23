"""
Tests for auto-instrumentation (@watch decorator)
"""

import pytest
import asyncio
import json
from pathlib import Path
from raglint.instrumentation import Monitor, watch

def test_monitor_singleton():
    """Test that Monitor is a singleton"""
    m1 = Monitor()
    m2 = Monitor()
    
    assert m1 is m2

def test_monitor_enable_disable():
    """Test enabling and disabling monitoring"""
    monitor = Monitor()
    
    # Test enable
    monitor.enable()
    assert monitor.enabled is True
    
    # Test disable
    monitor.disable()
    assert monitor.enabled is False

def test_watch_decorator(temp_dir):
    """Test @watch decorator captures function calls"""
    monitor = Monitor()
    monitor.trace_file = temp_dir / "test_events.jsonl"
    monitor.enable()
    
    @watch(tags=["test"])
    def test_function(x, y):
        return x + y
    
    # Call function
    result = test_function(2, 3)
    
    # Check result
    assert result == 5
    
    # Check trace file
    assert monitor.trace_file.exists()
    
    # Read events
    with open(monitor.trace_file) as f:
        lines = f.readlines()
    
    # Should have start and end events
    assert len(lines) >= 2
    
    # Parse events
    start_event = json.loads(lines[0])
    end_event = json.loads(lines[1])
    
    assert start_event["type"] == "start"
    assert end_event["type"] == "end"
    assert "test_function" in start_event["operation"]
    assert end_event.get("status") == "success"

def test_watch_decorator_with_error(temp_dir):
    """Test @watch captures errors"""
    monitor = Monitor()
    monitor.trace_file = temp_dir / "test_errors.jsonl"
    monitor.enable()
    
    @watch(tags=["test"])
    def failing_function():
        raise ValueError("Test error")
    
    # Call and expect error
    with pytest.raises(ValueError):
        failing_function()
    
    # Read events
    with open(monitor.trace_file) as f:
        lines = f.readlines()
    
    # Check error event
    end_event = json.loads(lines[-1])
    assert end_event["type"] == "end"
    assert end_event.get("status") == "error"
    assert "Test error" in end_event.get("error", "")

@pytest.mark.asyncio
async def test_watch_async_function(temp_dir):
    """Test @watch with async functions"""
    monitor = Monitor()
    monitor.trace_file = temp_dir / "test_async.jsonl"
    monitor.enable()
    
    @watch(tags=["async"])
    async def async_function(x):
        await asyncio.sleep(0.01)
        return x * 2
    
    result = await async_function(5)
    
    assert result == 10
    
    # Check trace file
    with open(monitor.trace_file) as f:
        lines = f.readlines()
    
    assert len(lines) >= 2
    
    end_event = json.loads(lines[-1])
    assert "latency_seconds" in end_event
    assert end_event["latency_seconds"] >= 0.01

def test_log_event(temp_dir):
    """Test direct log_event method"""
    monitor = Monitor()
    monitor.trace_file = temp_dir / "test_log.jsonl"
    monitor.enable()
    
    monitor.log_event("custom", {"key": "value", "number": 42})
    
    # Read event
    with open(monitor.trace_file) as f:
        event = json.loads(f.readline())
    
    assert event["type"] == "custom"
    assert event["key"] == "value"
    assert event["number"] == 42
    assert "event_id" in event
    assert "timestamp" in event

def test_monitor_disabled_no_logging(temp_dir):
    """Test that disabled monitor doesn't log"""
    monitor = Monitor()
    monitor.trace_file = temp_dir / "test_disabled.jsonl"
    monitor.disable()
    
    @watch()
    def test_func():
        return "result"
    
    test_func()
    
    # File should not exist
    assert not monitor.trace_file.exists()
