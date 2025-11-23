"""
Example: Running RAGLint benchmarks
"""

from raglint.benchmarks import SQUADBenchmark, BenchmarkRegistry
from raglint import RAGPipelineAnalyzer


def run_squad_benchmark():
    """Run SQUAD benchmark evaluation."""
    print("="*60)
    print("RAGLint SQUAD Benchmark")
    print("="*60)
    
    # 1. Load benchmark data
    print("\n1. Loading SQUAD benchmark (50 examples)...")
    benchmark = SQUADBenchmark(subset_size=5)  # Small subset for demo
    test_data = benchmark.load()
    
    print(f"   Loaded {len(test_data)} test cases")
    
    # 2. Create analyzer
    print("\n2. Creating RAGLint analyzer...")
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)
    
    # 3. Run evaluation
    print("\n3. Running evaluation...")
    results = analyzer.analyze(test_data, show_progress=True)
    
    # 4. Display results
    print("\n" + "="*60)
    print("BENCHMARK RESULTS")
    print("="*60)
    
    print(f"\nSummary Metrics:")
    
    # Calculate summary metrics from results
    avg_faithfulness = sum(results.faithfulness_scores) / len(results.faithfulness_scores) if results.faithfulness_scores else 0
    avg_semantic = sum(results.semantic_scores) / len(results.semantic_scores) if results.semantic_scores else 0
    
    print(f"  avg_faithfulness: {avg_faithfulness:.3f}")
    print(f"  avg_semantic_score: {avg_semantic:.3f}")
    print(f"  retrieval_stats:")
    for k, v in results.retrieval_stats.items():
        print(f"    {k}: {v:.3f}" if isinstance(v, float) else f"    {k}: {v}")
    
    # Compare to baseline (example values)
    print("\nComparison to Baseline:")
    baseline = {
        "avg_faithfulness": 0.85,
        "avg_semantic_score": 0.80,
    }
    
    current_metrics = {
        "avg_faithfulness": avg_faithfulness,
        "avg_semantic_score": avg_semantic,
    }
    
    for metric, baseline_value in baseline.items():
        if metric in current_metrics:
            current = current_metrics[metric]
            diff = current - baseline_value
            emoji = "✅" if diff >= 0 else "❌"
            print(f"  {emoji} {metric}: {current:.3f} (baseline: {baseline_value:.3f}, Δ {diff:+.3f})")
    
    return results


def list_available_benchmarks():
    """List all available benchmarks."""
    print("\nAvailable Benchmarks:")
    for name in BenchmarkRegistry.list_benchmarks():
        print(f"  - {name}")


if __name__ == "__main__":
    # List available benchmarks
    list_available_benchmarks()
    
    # Run SQUAD benchmark
    results = run_squad_benchmark()
    
    print("\n" + "="*60)
    print("Benchmark complete!")
    print("="*60)
