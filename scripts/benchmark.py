#!/usr/bin/env python3
"""
Benchmark script to compare RAGlint performance against other tools.

This script measures:
- Analysis speed (queries per second)
- Memory usage
- Accuracy metrics

Run with: python scripts/benchmark.py --help
"""
import argparse
import asyncio
import time
import json
from pathlib import Path
from typing import Dict, Any
import sys

# Add raglint to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from raglint import RAGPipelineAnalyzer


async def benchmark_raglint(data_file: str, smart: bool = False) -> Dict[str, Any]:
    """
    Benchmark RAGlint on given dataset.
    
    Returns timing and performance metrics.
    """
    print(f"\n🔬 Benchmarking RAGlint...")
    print(f"Dataset: {data_file}")
    print(f"Smart metrics: {smart}")
    
    # Load data
    with open(data_file) as f:
        data = json.load(f)
    
    num_queries = len(data)
    print(f"Queries: {num_queries}")
    
    # Initialize analyzer
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=smart)
    
    # Benchmark
    start_time = time.time()
    start_mem = get_memory_usage()
    
    results = await analyzer.analyze_async(data)
    
    end_time = time.time()
    end_mem = get_memory_usage()
    
    # Calculate metrics
    total_time = end_time - start_time
    qps = num_queries / total_time
    avg_latency = total_time / num_queries
    mem_delta = end_mem - start_mem
    
    return {
        "tool": "RAGlint",
        "dataset": data_file,
        "num_queries": num_queries,
        "total_time_sec": round(total_time, 2),
        "queries_per_sec": round(qps, 2),
        "avg_latency_ms": round(avg_latency * 1000, 2),
        "memory_mb": round(mem_delta, 2),
        "smart_metrics": smart,
        "faithfulness": round(results.get('faithfulness_score', 0), 3),
        "semantic_similarity": round(results.get('semantic_score', 0), 3),
    }


def get_memory_usage() -> float:
    """Get current memory usage in MB."""
    try:
        import psutil
        import os
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    except ImportError:
        return 0


def print_results(results: Dict[str, Any]):
    """Print benchmark results in a nice format."""
    print("\n" + "="*60)
    print("📊 BENCHMARK RESULTS")
    print("="*60)
    print(f"\nDataset: {results['dataset']}")
    print(f"Queries: {results['num_queries']}")
    print(f"\n⏱️  Performance:")
    print(f"  Total time: {results['total_time_sec']}s")
    print(f"  Throughput: {results['queries_per_sec']} queries/sec")
    print(f"  Avg latency: {results['avg_latency_ms']}ms")
    print(f"  Memory: {results['memory_mb']}MB")
    print(f"\n📈 Quality Metrics:")
    print(f"  Faithfulness: {results['faithfulness']}")
    print(f"  Semantic Sim: {results['semantic_similarity']}")
    print("="*60)


def generate_comparison_table(raglint_results: Dict[str, Any]):
    """
    Generate markdown comparison table.
    
    This is a placeholder - actual comparison would require running RAGAS, etc.
    """
    print("\n" + "="*60)
    print("📋 COMPARISON TABLE (Add other tools for full comparison)")
    print("="*60)
    
    table = f"""
| Tool | Queries/sec | Avg Latency | Memory | Faithfulness |
|------|-------------|-------------|--------|--------------|
| RAGlint (async) | {raglint_results['queries_per_sec']} | {raglint_results['avg_latency_ms']}ms | {raglint_results['memory_mb']}MB | {raglint_results['faithfulness']} |
| RAGAS | ? | ? | ? | ? |
| DeepEval | ? | ? | ? | ? |

*To get comparison data, run RAGAS/DeepEval on the same dataset*
"""
    print(table)
    
    # Save to file
    output_file = Path("benchmark_results.md")
    with open(output_file, "w") as f:
        f.write(f"# RAGlint Benchmark Results\n\n")
        f.write(f"**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(table)
    
    print(f"\n💾 Results saved to: {output_file}")


async def main():
    parser = argparse.ArgumentParser(description="Benchmark RAGlint performance")
    parser.add_argument(
        "dataset",
        nargs="?",
        default="examples/sample_data.json",
        help="Path to dataset JSON file (default: examples/sample_data.json)"
    )
    parser.add_argument(
        "--smart",
        action="store_true",
        help="Use smart metrics (LLM-powered, slower but more accurate)"
    )
    parser.add_argument(
        "--output",
        default="benchmark_results.json",
        help="Output file for results (default: benchmark_results.json)"
    )
    
    args = parser.parse_args()
    
    # Check if dataset exists
    if not Path(args.dataset).exists():
        print(f"❌ Error: Dataset not found: {args.dataset}")
        print(f"   Try: python scripts/benchmark.py examples/ecommerce/product_qa.json")
        return 1
    
    # Run benchmark
    try:
        results = await benchmark_raglint(args.dataset, smart=args.smart)
        
        # Print results
        print_results(results)
        
        # Generate comparison table
        generate_comparison_table(results)
        
        # Save to JSON
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"💾 Full results saved to: {args.output}")
        
        # Success
        print("\n✅ Benchmark complete!")
        return 0
        
    except Exception as e:
        print(f"\n❌ Benchmark failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
