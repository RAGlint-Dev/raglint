"""
Cost and latency tracking for RAG evaluation.
"""

import time
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


# Pricing per 1K tokens (as of 2024)
LLM_PRICING = {
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "claude-3-opus": {"input": 0.015, "output": 0.075},
    "claude-3-sonnet": {"input": 0.003, "output": 0.015},
    "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
    "claude-3-5-sonnet": {"input": 0.003, "output": 0.015},
    "ollama": {"input": 0.0, "output": 0.0},  # Local models are free
}


@dataclass
class LatencyStats:
    """Statistics for latency tracking."""
    total_time: float = 0.0
    num_calls: int = 0
    min_latency: float = float('inf')
    max_latency: float = 0.0
    p50_latency: float = 0.0
    p95_latency: float = 0.0
    p99_latency: float = 0.0
    latencies: List[float] = field(default_factory=list)
    
    def add_latency(self, latency: float):
        """Add a latency measurement."""
        self.latencies.append(latency)
        self.total_time += latency
        self.num_calls += 1
        self.min_latency = min(self.min_latency, latency)
        self.max_latency = max(self.max_latency, latency)
    
    def calculate_percentiles(self):
        """Calculate percentile latencies."""
        if not self.latencies:
            return
        
        sorted_latencies = sorted(self.latencies)
        n = len(sorted_latencies)
        
        self.p50_latency = sorted_latencies[int(n * 0.5)]
        self.p95_latency = sorted_latencies[int(n * 0.95)] if n > 20 else self.max_latency
        self.p99_latency = sorted_latencies[int(n * 0.99)] if n > 100 else self.max_latency
    
    @property
    def avg_latency(self) -> float:
        """Average latency per call."""
        return self.total_time / self.num_calls if self.num_calls > 0 else 0.0


@dataclass
class CostStats:
    """Statistics for cost tracking."""
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_cost: float = 0.0
    num_calls: int = 0
    costs_by_operation: Dict[str, float] = field(default_factory=dict)
    
    def add_usage(self, input_tokens: int, output_tokens: int, model: str, operation: str = "default"):
        """Add token usage and calculate cost."""
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        self.num_calls += 1
        
        # Calculate cost
        if model in LLM_PRICING:
            pricing = LLM_PRICING[model]
            cost = (input_tokens / 1000 * pricing["input"]) + (output_tokens / 1000 * pricing["output"])
            self.total_cost += cost
            
            # Track by operation
            if operation not in self.costs_by_operation:
                self.costs_by_operation[operation] = 0.0
            self.costs_by_operation[operation] += cost
    
    @property
    def avg_cost_per_call(self) -> float:
        """Average cost per LLM call."""
        return self.total_cost / self.num_calls if self.num_calls > 0 else 0.0


class PerformanceTracker:
    """Track cost and latency for RAG evaluation."""
    
    def __init__(self):
        self.latency_stats = LatencyStats()
        self.cost_stats = CostStats()
        self.operation_latencies: Dict[str, LatencyStats] = {}
        self._start_times: Dict[str, float] = {}
    
    def start_operation(self, operation_id: str):
        """Start timing an operation."""
        self._start_times[operation_id] = time.time()
    
    def end_operation(self, operation_id: str, operation_type: str = "default"):
        """End timing an operation."""
        if operation_id not in self._start_times:
            return
        
        latency = time.time() - self._start_times[operation_id]
        del self._start_times[operation_id]
        
        # Add to global stats
        self.latency_stats.add_latency(latency)
        
        # Add to operation-specific stats
        if operation_type not in self.operation_latencies:
            self.operation_latencies[operation_type] = LatencyStats()
        self.operation_latencies[operation_type].add_latency(latency)
    
    def record_llm_call(self, input_tokens: int, output_tokens: int, model: str, 
                        latency: float, operation: str = "llm_call"):
        """Record an LLM call with cost and latency."""
        # Record cost
        self.cost_stats.add_usage(input_tokens, output_tokens, model, operation)
        
        # Record latency
        self.latency_stats.add_latency(latency)
        
        # Record operation-specific latency
        if operation not in self.operation_latencies:
            self.operation_latencies[operation] = LatencyStats()
        self.operation_latencies[operation].add_latency(latency)
    
    def get_summary(self) -> Dict:
        """Get summary of all stats."""
        # Calculate percentiles
        self.latency_stats.calculate_percentiles()
        for stats in self.operation_latencies.values():
            stats.calculate_percentiles()
        
        return {
            "cost": {
                "total_cost_usd": round(self.cost_stats.total_cost, 4),
                "total_input_tokens": self.cost_stats.total_input_tokens,
                "total_output_tokens": self.cost_stats.total_output_tokens,
                "total_tokens": self.cost_stats.total_input_tokens + self.cost_stats.total_output_tokens,
                "avg_cost_per_call": round(self.cost_stats.avg_cost_per_call, 4),
                "num_llm_calls": self.cost_stats.num_calls,
                "costs_by_operation": {
                    k: round(v, 4) for k, v in self.cost_stats.costs_by_operation.items()
                }
            },
            "latency": {
                "total_time_seconds": round(self.latency_stats.total_time, 2),
                "num_operations": self.latency_stats.num_calls,
                "avg_latency_ms": round(self.latency_stats.avg_latency * 1000, 2),
                "min_latency_ms": round(self.latency_stats.min_latency * 1000, 2) if self.latency_stats.min_latency != float('inf') else 0,
                "max_latency_ms": round(self.latency_stats.max_latency * 1000, 2),
                "p50_latency_ms": round(self.latency_stats.p50_latency * 1000, 2),
                "p95_latency_ms": round(self.latency_stats.p95_latency * 1000, 2),
                "p99_latency_ms": round(self.latency_stats.p99_latency * 1000, 2),
            },
            "operations": {
                op_name: {
                    "avg_latency_ms": round(stats.avg_latency * 1000, 2),
                    "p95_latency_ms": round(stats.p95_latency * 1000, 2) if stats.latencies else 0,
                    "num_calls": stats.num_calls,
                }
                for op_name, stats in self.operation_latencies.items()
            }
        }
    
    def estimate_cost(self, num_queries: int, model: str = "gpt-3.5-turbo") -> Dict:
        """Estimate cost for a number of queries."""
        if self.cost_stats.num_calls == 0:
            return {"error": "No data to estimate from"}
        
        avg_input = self.cost_stats.total_input_tokens / self.cost_stats.num_calls
        avg_output = self.cost_stats.total_output_tokens / self.cost_stats.num_calls
        
        if model in LLM_PRICING:
            pricing = LLM_PRICING[model]
            cost_per_query = (avg_input / 1000 * pricing["input"]) + (avg_output / 1000 * pricing["output"])
            total_cost = cost_per_query * num_queries
            
            return {
                "num_queries": num_queries,
                "model": model,
                "estimated_cost_usd": round(total_cost, 4),
                "avg_cost_per_query": round(cost_per_query, 4),
                "estimated_tokens": int((avg_input + avg_output) * num_queries),
            }
        
        return {"error": f"Unknown model: {model}"}


# Global tracker instance
_global_tracker: Optional[PerformanceTracker] = None


def get_tracker() -> PerformanceTracker:
    """Get or create global performance tracker."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = PerformanceTracker()
    return _global_tracker


def reset_tracker():
    """Reset the global tracker."""
    global _global_tracker
    _global_tracker = PerformanceTracker()
