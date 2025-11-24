"""
Benchmark datasets for RAGLint.
"""

from .coqa import CoQABenchmark
from .hotpotqa import HotpotQABenchmark
from .registry import BenchmarkRegistry
from .squad import SQUADBenchmark, download_squad

__all__ = [
    "SQUADBenchmark",
    "CoQABenchmark",
    "HotpotQABenchmark",
    "BenchmarkRegistry",
    "download_squad"
]
