"""
Example custom plugin: Response Latency Tracker

Tracks how long it takes to generate responses and provides insights
into performance bottlenecks. Useful for production monitoring.
"""
import time
from typing import Dict, Any
from raglint.plugins.interface import PluginInterface


class ResponseLatencyPlugin(PluginInterface):
    """
    Tracks response generation latency and identifies slow queries.
    
    Helps identify:
    - Which queries are slowest
    - Retrieval vs generation time
    - Performance degradation over time
    """
    
    name = "response_latency"
    version = "1.0.0"
    description = "Tracks and analyzes response generation latency"
    
    def __init__(self):
        """Initialize latency tracker."""
        self.latency_history = []
    
    async def calculate_async(
        self,
        query: str,
        response: str,
        contexts: list,
        metadata: dict = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate latency metrics.
        
        Expects metadata with timing information:
        {
            "retrieval_time": float,  # seconds
            "generation_time": float,  # seconds
            "total_time": float  # seconds
        }
        """
        if not metadata:
            metadata = {}
        
        retrieval_time = metadata.get("retrieval_time", 0)
        generation_time = metadata.get("generation_time", 0)
        total_time = metadata.get("total_time", retrieval_time + generation_time)
        
        # Calculate metrics
        retrieval_pct = (retrieval_time / total_time * 100) if total_time > 0 else 0
        generation_pct = (generation_time / total_time * 100) if total_time > 0 else 0
        
        # Store in history
        self.latency_history.append({
            "query": query,
            "total_time": total_time,
            "retrieval_time": retrieval_time,
            "generation_time": generation_time,
        })
        
        # Determine if slow
        is_slow = total_time > 3.0  # 3 second threshold
        
        # Calculate percentiles if we have history
        percentile_90 = self._calculate_percentile(90)
        
        return {
            "total_latency_ms": total_time * 1000,
            "retrieval_latency_ms": retrieval_time * 1000,
            "generation_latency_ms": generation_time * 1000,
            "retrieval_percentage": round(retrieval_pct, 1),
            "generation_percentage": round(generation_pct, 1),
            "is_slow": is_slow,
            "p90_latency_ms": percentile_90 * 1000 if percentile_90 else None,
            "recommendation": self._get_recommendation(retrieval_pct, total_time)
        }
    
    def _calculate_percentile(self, percentile: int) -> float:
        """Calculate percentile from latency history."""
        if not self.latency_history:
            return None
        
        times = sorted([h["total_time"] for h in self.latency_history])
        idx = int(len(times) * percentile / 100)
        return times[min(idx, len(times) - 1)]
    
    def _get_recommendation(self, retrieval_pct: float, total_time: float) -> str:
        """Get optimization recommendation based on latency profile."""
        if total_time < 1.0:
            return "✅ Performance is good"
        elif retrieval_pct > 70:
            return "⚠️ Retrieval is slow - consider optimizing vector search or reducing top-k"
        elif retrieval_pct < 30:
            return "⚠️ Generation is slow - consider using faster model or reducing max_tokens"
        else:
            return "⚠️ Both retrieval and generation are slow - optimize holistically"
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics across all queries."""
        if not self.latency_history:
            return {"error": "No latency data collected"}
        
        times = [h["total_time"] for h in self.latency_history]
        retrieval_times = [h["retrieval_time"] for h in self.latency_history]
        generation_times = [h["generation_time"] for h in self.latency_history]
        
        return {
            "total_queries": len(self.latency_history),
            "avg_latency_ms": sum(times) / len(times) * 1000,
            "p50_latency_ms": self._calculate_percentile(50) * 1000,
            "p90_latency_ms": self._calculate_percentile(90) * 1000,
            "p99_latency_ms": self._calculate_percentile(99) * 1000,
            "avg_retrieval_ms": sum(retrieval_times) / len(retrieval_times) * 1000,
            "avg_generation_ms": sum(generation_times) / len(generation_times) * 1000,
            "slow_queries_count": sum(1 for t in times if t > 3.0),
        }


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_plugin():
        plugin = ResponseLatencyPlugin()
        
        # Simulate some queries with different latency profiles
        test_cases = [
            {"retrieval": 0.5, "generation": 0.3},  # Fast
            {"retrieval": 2.0, "generation": 0.5},  # Slow retrieval
            {"retrieval": 0.3, "generation": 2.5},  # Slow generation
            {"retrieval": 1.5, "generation": 1.5},  # Both slow
        ]
        
        for i, case in enumerate(test_cases):
            result = await plugin.calculate_async(
                query=f"Test query {i}",
                response="Test response",
                contexts=[],
                metadata={
                    "retrieval_time": case["retrieval"],
                    "generation_time": case["generation"],
                    "total_time": case["retrieval"] + case["generation"]
                }
            )
            print(f"\nQuery {i}:")
            print(f"  Total: {result['total_latency_ms']:.0f}ms")
            print(f"  Recommendation: {result['recommendation']}")
        
        # Print summary
        print("\n=== Summary ===")
        summary = plugin.get_summary()
        print(f"Avg latency: {summary['avg_latency_ms']:.0f}ms")
        print(f"P90 latency: {summary['p90_latency_ms']:.0f}ms")
        print(f"Slow queries: {summary['slow_queries_count']}/{summary['total_queries']}")
    
    asyncio.run(test_plugin())
