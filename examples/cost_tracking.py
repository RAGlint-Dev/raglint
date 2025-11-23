"""
Example: Cost and latency tracking
"""

from raglint import RAGPipelineAnalyzer
from raglint.tracking import get_tracker, reset_tracker


def main():
    print("="*60)
    print("RAGLint Cost & Latency Tracking Demo")
    print("="*60)
    
    # Reset tracker for clean demo
    reset_tracker()
    
    # Sample data
    test_data = [
        {
            "query": "What is Python?",
            "retrieved_contexts": ["Python is a programming language."],
            "response": "Python is a high-level programming language.",
        },
        {
            "query": "What is machine learning?",
            "retrieved_contexts": ["ML is a subset of AI."],
            "response": "Machine learning is artificial intelligence.",
        },
    ]
    
    # Run analysis
    print("\n1. Running analysis...")
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)
    results = analyzer.analyze(test_data, show_progress=True)
    
    # Get performance stats
    print("\n2. Getting performance statistics...")
    tracker = get_tracker()
    stats = tracker.get_summary()
    
    # Display results
    print("\n" + "="*60)
    print("COST TRACKING")
    print("="*60)
    
    cost = stats["cost"]
    print(f"\n💰 Total Cost: ${cost['total_cost_usd']:.4f}")
    print(f"   Input tokens: {cost['total_input_tokens']:,}")
    print(f"   Output tokens: {cost['total_output_tokens']:,}")
    print(f"   Total tokens: {cost['total_tokens']:,}")
    print(f"   Avg cost/call: ${cost['avg_cost_per_call']:.4f}")
    print(f"   LLM calls: {cost['num_llm_calls']}")
    
    if cost['costs_by_operation']:
        print(f"\n   Costs by operation:")
        for op, op_cost in cost['costs_by_operation'].items():
            print(f"     - {op}: ${op_cost:.4f}")
    
    print("\n" + "="*60)
    print("LATENCY TRACKING")
    print("="*60)
    
    latency = stats["latency"]
    print(f"\n⏱️  Total time: {latency['total_time_seconds']:.2f}s")
    print(f"   Operations: {latency['num_operations']}")
    print(f"   Avg latency: {latency['avg_latency_ms']:.2f}ms")
    print(f"   Min latency: {latency['min_latency_ms']:.2f}ms")
    print(f"   Max latency: {latency['max_latency_ms']:.2f}ms")
    print(f"   P50 latency: {latency['p50_latency_ms']:.2f}ms")
    print(f"   P95 latency: {latency['p95_latency_ms']:.2f}ms")
    print(f"   P99 latency: {latency['p99_latency_ms']:.2f}ms")
    
    if stats['operations']:
        print(f"\n   Latency by operation:")
        for op, op_stats in stats['operations'].items():
            print(f"     - {op}:")
            print(f"         avg: {op_stats['avg_latency_ms']:.2f}ms")
            print(f"         p95: {op_stats['p95_latency_ms']:.2f}ms")
            print(f"         calls: {op_stats['num_calls']}")
    
    # Cost estimation
    print("\n" + "="*60)
    print("COST ESTIMATION")
    print("="*60)
    
    estimates = [
        (100, "gpt-3.5-turbo"),
        (1000, "gpt-3.5-turbo"),
        (100, "gpt-4"),
        (1000, "gpt-4"),
    ]
    
    for num_queries, model in estimates:
        estimate = tracker.estimate_cost(num_queries, model)
        if "error" not in estimate:
            print(f"\n📊 {num_queries:,} queries with {model}:")
            print(f"   Estimated cost: ${estimate['estimated_cost_usd']:.2f}")
            print(f"   Cost per query: ${estimate['avg_cost_per_query']:.4f}")
            print(f"   Estimated tokens: {estimate['estimated_tokens']:,}")
    
    print("\n" + "="*60)
    print("Demo complete!")
    print("="*60)


if __name__ == "__main__":
    main()
