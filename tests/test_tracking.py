"""
Tests for cost and latency tracking.
"""

import pytest
import time
from raglint.tracking import (
    PerformanceTracker,
    LatencyStats,
    CostStats,
    get_tracker,
    reset_tracker,
    LLM_PRICING,
)


class TestLatencyStats:
    """Test LatencyStats class."""
    
    def test_initialization(self):
        """Test LatencyStats initialization."""
        stats = LatencyStats()
        assert stats.total_time == 0.0
        assert stats.num_calls == 0
        assert stats.min_latency == float('inf')
        assert stats.max_latency == 0.0
        assert len(stats.latencies) == 0
    
    def test_add_latency(self):
        """Test adding latency measurements."""
        stats = LatencyStats()
        stats.add_latency(1.5)
        stats.add_latency(2.0)
        stats.add_latency(1.0)
        
        assert stats.num_calls == 3
        assert stats.total_time == 4.5
        assert stats.min_latency == 1.0
        assert stats.max_latency == 2.0
        assert len(stats.latencies) == 3
    
    def test_avg_latency(self):
        """Test average latency calculation."""
        stats = LatencyStats()
        stats.add_latency(1.0)
        stats.add_latency(2.0)
        stats.add_latency(3.0)
        
        assert stats.avg_latency == 2.0
    
    def test_calculate_percentiles(self):
        """Test percentile calculations."""
        stats = LatencyStats()
        for i in range(100):
            stats.add_latency(float(i))
        
        stats.calculate_percentiles()
        
        assert stats.p50_latency == 50.0
        assert stats.p95_latency == 95.0
        assert stats.p99_latency == 99.0
    
    def test_percentiles_small_dataset(self):
        """Test percentiles with small dataset."""
        stats = LatencyStats()
        stats.add_latency(1.0)
        stats.add_latency(2.0)
        stats.add_latency(3.0)
        
        stats.calculate_percentiles()
        
        assert stats.p50_latency == 2.0
        assert stats.p95_latency == 3.0  # Falls back to max for small dataset
        assert stats.p99_latency == 3.0


class TestCostStats:
    """Test CostStats class."""
    
    def test_initialization(self):
        """Test CostStats initialization."""
        stats = CostStats()
        assert stats.total_input_tokens == 0
        assert stats.total_output_tokens == 0
        assert stats.total_cost == 0.0
        assert stats.num_calls == 0
        assert len(stats.costs_by_operation) == 0
    
    def test_add_usage_gpt35(self):
        """Test adding usage for GPT-3.5."""
        stats = CostStats()
        stats.add_usage(1000, 500, "gpt-3.5-turbo", "test_op")
        
        assert stats.total_input_tokens == 1000
        assert stats.total_output_tokens == 500
        assert stats.num_calls == 1
        
        # Cost: (1000/1000 * 0.0005) + (500/1000 * 0.0015) = 0.0005 + 0.00075 = 0.00125
        expected_cost = (1000 / 1000 * 0.0005) + (500 / 1000 * 0.0015)
        assert abs(stats.total_cost - expected_cost) < 0.0001
        assert "test_op" in stats.costs_by_operation
    
    def test_add_usage_gpt4(self):
        """Test adding usage for GPT-4."""
        stats = CostStats()
        stats.add_usage(1000, 1000, "gpt-4", "generation")
        
        # Cost: (1000/1000 * 0.03) + (1000/1000 * 0.06) = 0.03 + 0.06 = 0.09
        expected_cost = (1000 / 1000 * 0.03) + (1000 / 1000 * 0.06)
        assert abs(stats.total_cost - expected_cost) < 0.0001
    
    def test_add_usage_ollama(self):
        """Test adding usage for Ollama (free)."""
        stats = CostStats()
        stats.add_usage(1000, 1000, "ollama", "generation")
        
        assert stats.total_cost == 0.0
        assert stats.total_input_tokens == 1000
        assert stats.total_output_tokens == 1000
    
    def test_avg_cost_per_call(self):
        """Test average cost per call."""
        stats = CostStats()
        stats.add_usage(1000, 500, "gpt-3.5-turbo")
        stats.add_usage(1000, 500, "gpt-3.5-turbo")
        
        expected_total = 2 * ((1000 / 1000 * 0.0005) + (500 / 1000 * 0.0015))
        assert abs(stats.avg_cost_per_call - expected_total / 2) < 0.0001
    
    def test_multiple_operations(self):
        """Test tracking multiple operations."""
        stats = CostStats()
        stats.add_usage(1000, 500, "gpt-3.5-turbo", "op1")
        stats.add_usage(2000, 1000, "gpt-3.5-turbo", "op2")
        
        assert "op1" in stats.costs_by_operation
        assert "op2" in stats.costs_by_operation
        assert len(stats.costs_by_operation) == 2


class TestPerformanceTracker:
    """Test PerformanceTracker class."""
    
    def test_initialization(self):
        """Test tracker initialization."""
        tracker = PerformanceTracker()
        assert tracker.latency_stats.num_calls == 0
        assert tracker.cost_stats.num_calls == 0
        assert len(tracker.operation_latencies) == 0
    
    def test_start_end_operation(self):
        """Test operation timing."""
        tracker = PerformanceTracker()
        
        tracker.start_operation("op1")
        time.sleep(0.1)
        tracker.end_operation("op1", "test_op")
        
        assert tracker.latency_stats.num_calls == 1
        assert tracker.latency_stats.total_time >= 0.1
        assert "test_op" in tracker.operation_latencies
    
    def test_record_llm_call(self):
        """Test recording LLM calls."""
        tracker = PerformanceTracker()
        
        tracker.record_llm_call(
            input_tokens=1000,
            output_tokens=500,
            model="gpt-3.5-turbo",
            latency=0.5,
            operation="generation"
        )
        
        assert tracker.cost_stats.num_calls == 1
        assert tracker.cost_stats.total_input_tokens == 1000
        assert tracker.cost_stats.total_output_tokens == 500
        assert tracker.latency_stats.num_calls == 1
        assert "generation" in tracker.operation_latencies
    
    def test_get_summary(self):
        """Test getting performance summary."""
        tracker = PerformanceTracker()
        
        tracker.record_llm_call(1000, 500, "gpt-3.5-turbo", 0.5, "op1")
        tracker.record_llm_call(2000, 1000, "gpt-4", 1.0, "op2")
        
        summary = tracker.get_summary()
        
        assert "cost" in summary
        assert "latency" in summary
        assert "operations" in summary
        
        assert summary["cost"]["num_llm_calls"] == 2
        assert summary["cost"]["total_input_tokens"] == 3000
        assert summary["cost"]["total_output_tokens"] == 1500
        
        assert summary["latency"]["num_operations"] == 2
        assert "op1" in summary["operations"]
        assert "op2" in summary["operations"]
    
    def test_estimate_cost(self):
        """Test cost estimation."""
        tracker = PerformanceTracker()
        
        # Add some historical data
        tracker.record_llm_call(1000, 500, "gpt-3.5-turbo", 0.5)
        tracker.record_llm_call(1000, 500, "gpt-3.5-turbo", 0.5)
        
        # Estimate for 100 queries
        estimate = tracker.estimate_cost(100, "gpt-3.5-turbo")
        
        assert "estimated_cost_usd" in estimate
        assert "avg_cost_per_query" in estimate
        assert "estimated_tokens" in estimate
        assert estimate["num_queries"] == 100
    
    def test_estimate_cost_no_data(self):
        """Test cost estimation with no historical data."""
        tracker = PerformanceTracker()
        estimate = tracker.estimate_cost(100, "gpt-3.5-turbo")
        
        assert "error" in estimate
    
    def test_estimate_cost_unknown_model(self):
        """Test cost estimation for unknown model."""
        tracker = PerformanceTracker()
        tracker.record_llm_call(1000, 500, "gpt-3.5-turbo", 0.5)
        
        estimate = tracker.estimate_cost(100, "unknown-model")
        assert "error" in estimate


class TestGlobalTracker:
    """Test global tracker functions."""
    
    def test_get_tracker(self):
        """Test getting global tracker."""
        tracker1 = get_tracker()
        tracker2 = get_tracker()
        
        # Should return same instance
        assert tracker1 is tracker2
    
    def test_reset_tracker(self):
        """Test resetting global tracker."""
        tracker1 = get_tracker()
        tracker1.record_llm_call(1000, 500, "gpt-3.5-turbo", 0.5)
        
        reset_tracker()
        
        tracker2 = get_tracker()
        
        # Should be a new instance
        assert tracker1 is not tracker2
        assert tracker2.cost_stats.num_calls == 0


class TestPricing:
    """Test LLM pricing data."""
    
    def test_pricing_data_exists(self):
        """Test that pricing data exists for common models."""
        assert "gpt-4" in LLM_PRICING
        assert "gpt-3.5-turbo" in LLM_PRICING
        assert "ollama" in LLM_PRICING
    
    def test_pricing_structure(self):
        """Test pricing data structure."""
        for model, pricing in LLM_PRICING.items():
            assert "input" in pricing
            assert "output" in pricing
            assert isinstance(pricing["input"], (int, float))
            assert isinstance(pricing["output"], (int, float))
