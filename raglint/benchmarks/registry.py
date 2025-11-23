"""
Benchmark registry for RAGLint.

Manages available benchmarks and lazy loading.
"""

from typing import List, Dict, Any

class BenchmarkRegistry:
    """Registry of available benchmarks."""
    
    @staticmethod
    def list_benchmarks() -> List[str]:
        """List all available benchmarks."""
        return ["squad", "coqa", "hotpotqa"]
    
    @staticmethod
    def load(name: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Load a benchmark by name.
        
        Args:
            name: Benchmark name ("squad", "coqa", etc.)
            **kwargs: Additional arguments for the benchmark
            
        Returns:
            List of test cases
        """
        name = name.lower()
        
        if name == "squad":
            from .squad import SQUADBenchmark
            benchmark = SQUADBenchmark(**kwargs)
            return benchmark.load()
            
        elif name == "coqa":
            from .coqa import CoQABenchmark
            benchmark = CoQABenchmark(**kwargs)
            return benchmark.load()
            
        elif name == "hotpotqa":
            from .hotpotqa import HotpotQABenchmark
            benchmark = HotpotQABenchmark(**kwargs)
            return benchmark.load()
            
        else:
            raise ValueError(f"Unknown benchmark: {name}. Available: {BenchmarkRegistry.list_benchmarks()}")
