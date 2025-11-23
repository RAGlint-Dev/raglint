"""
Coverage tests for raglint.tracking
"""
import pytest
from unittest.mock import Mock, patch
from raglint.tracking import PerformanceTracker, LLM_PRICING, get_tracker

class TestTrackingCoverage:
    
    def test_tracker_singleton(self):
        """Test get_tracker returns same instance."""
        t1 = get_tracker()
        t2 = get_tracker()
        assert t1 is t2
        
    def test_record_llm_call(self):
        """Test recording LLM calls with cost and latency."""
        tracker = PerformanceTracker()
        
        tracker.record_llm_call(100, 50, "gpt-4", 1.5, "test_op")
        
        assert tracker.cost_stats.total_input_tokens == 100
        assert tracker.cost_stats.total_output_tokens == 50
        assert tracker.cost_stats.total_cost > 0
        assert tracker.latency_stats.num_calls == 1
        
    def test_operation_timing(self):
        """Test start/end operation timing."""
        tracker = PerformanceTracker()
        
        tracker.start_operation("op1")
        tracker.end_operation("op1", "test_type")
        
        assert tracker.latency_stats.num_calls == 1
        assert "test_type" in tracker.operation_latencies
        
    def test_estimate_cost(self):
        """Test cost estimation."""
        tracker = PerformanceTracker()
        # Populate stats
        tracker.cost_stats.total_input_tokens = 1000
        tracker.cost_stats.total_output_tokens = 1000
        tracker.cost_stats.num_calls = 1
        
        result = tracker.estimate_cost(1000, "gpt-4")
        
        assert "estimated_cost_usd" in result
        assert result["num_queries"] == 1000
        assert result["model"] == "gpt-4"
        
    def test_unknown_model_estimate(self):
        """Test estimation with unknown model."""
        tracker = PerformanceTracker()
        tracker.cost_stats.num_calls = 1
        
        result = tracker.estimate_cost(100, "unknown-model")
        assert "error" in result
        
    def test_get_summary(self):
        """Test getting performance summary."""
        tracker = PerformanceTracker()
        tracker.record_llm_call(100, 50, "gpt-4", 0.5)
        
        summary = tracker.get_summary()
        
        assert "cost" in summary
        assert "latency" in summary
        assert summary["cost"]["total_input_tokens"] == 100
