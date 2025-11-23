"""
Benchmark datasets for RAGLint.
"""

from .squad import SQUADBenchmark, download_squad
from .coqa import CoQABenchmark
from .hotpotqa import HotpotQABenchmark
from .registry import BenchmarkRegistry

__all__ = [
    "SQUADBenchmark", 
    "CoQABenchmark", 
    "HotpotQABenchmark", 
    "BenchmarkRegistry", 
    "download_squad"
]
