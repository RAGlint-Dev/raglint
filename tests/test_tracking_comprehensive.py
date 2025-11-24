"""
Tests for tracking module.
"""

import pytest
import time
from raglint.tracking import PerformanceTracker, get_tracker, reset_tracker


def test_performance_tracker_initialization():
    """Test PerformanceTracker initialization."""
    tracker = PerformanceTracker()
    assert tracker is not None
    assert tracker.latency_stats is not None
    assert tracker.cost_stats is not None


def test_record_llm_call():
    """Test recording an LLM call."""
    tracker = PerformanceTracker()
    
    tracker.record_llm_call(
        input_tokens=100,
        output_tokens=50,
        model="gpt-3.5-turbo",
        latency=0.5,
        operation="generation"
    )
    
    summary = tracker.get_summary()
    assert summary["cost"]["num_llm_calls"] == 1
    assert summary["cost"]["total_tokens"] == 150
    assert summary["latency"]["num_operations"] == 1
    assert summary["latency"]["total_time_seconds"] == 0.5


def test_operation_timing():
    """Test timing operations."""
    tracker = PerformanceTracker()
    
    tracker.start_operation("op1")
    time.sleep(0.1)
    tracker.end_operation("op1", operation_type="retrieval")
    
    summary = tracker.get_summary()
    assert summary["latency"]["num_operations"] == 1
    assert summary["operations"]["retrieval"]["num_calls"] == 1
    assert summary["latency"]["total_time_seconds"] >= 0.1


def test_global_tracker():
    """Test global tracker singleton."""
    reset_tracker()
    t1 = get_tracker()
    t2 = get_tracker()
    
    assert t1 is t2
    
    t1.record_llm_call(10, 10, "gpt-3.5-turbo", 0.1)
    summary = t2.get_summary()
    assert summary["cost"]["num_llm_calls"] == 1


def test_estimate_cost():
    """Test cost estimation."""
    tracker = PerformanceTracker()
    
    # Add some data
    tracker.record_llm_call(1000, 500, "gpt-3.5-turbo", 1.0)
    
    estimate = tracker.estimate_cost(num_queries=100, model="gpt-3.5-turbo")
    
    assert "estimated_cost_usd" in estimate
    assert estimate["num_queries"] == 100
    assert estimate["estimated_tokens"] == 150000
