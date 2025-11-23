"""
Performance demo: Async vs Sync analysis.

Run this script to see the speed improvement of async processing.
"""

import json
import time

from raglint.core import RAGPipelineAnalyzer

# Create sample data
def create_sample_data(n_items=20):
    """Create sample RAG data for testing."""
    data = []
    for i in range(n_items):
        data.append(
            {
                "query": f"What is concept {i}?",
                "retrieved_contexts": [
                    f"Concept {i} is about topic A.",
                    f"It relates to subject B in area {i}.",
                    f"The key idea is understanding principle {i}.",
                ],
                "ground_truth_contexts": [
                    f"Concept {i} refers to topic A and B.",
                ],
                "response": f"Concept {i} is related to topics A and B, focusing on principle {i}.",
            }
        )
    return data


def main():
    print("=" * 70)
    print("RAGLint Performance Demo: Async vs Sync")
    print("=" * 70)

    # Create test data
    data = create_sample_data(n_items=20)
    print(f"\n📊 Analyzing {len(data)} RAG interactions with smart metrics (MOCK mode)")

    config = {"provider": "mock"}

    # Test 1: Synchronous (old way)
    print("\n🐢 Running SYNCHRONOUS analysis...")
    analyzer_sync = RAGPipelineAnalyzer(use_smart_metrics=True, config=config)
    
    start = time.time()
    # Force sync by using _analyze_sync directly
    result_sync = analyzer_sync._analyze_sync(data)
    sync_time = time.time() - start

    print(f"   ✓ Completed in {sync_time:.2f}s")
    print(f"   • Faithfulness scores: {len(result_sync.faithfulness_scores)}")
    print(f"   • Semantic scores: {len(result_sync.semantic_scores)}")

    # Test 2: Asynchronous (new way)
    print("\n🚀 Running ASYNCHRONOUS analysis...")
    analyzer_async = RAGPipelineAnalyzer(use_smart_metrics=True, config=config)

    start = time.time()
    result_async = analyzer_async.analyze(data, show_progress=True)
    async_time = time.time() - start

    print(f"   ✓ Completed in {async_time:.2f}s")
    print(f"   • Faithfulness scores: {len(result_async.faithfulness_scores)}")
    print(f"   • Semantic scores: {len(result_async.semantic_scores)}")

    # Show improvement
    speedup = sync_time / async_time if async_time > 0 else 1.0
    improvement = ((sync_time - async_time) / sync_time * 100) if sync_time > 0 else 0

    print("\n" + "=" * 70)
    print("📈 RESULTS")
    print("=" * 70)
    print(f"Synchronous:  {sync_time:.2f}s")
    print(f"Asynchronous: {async_time:.2f}s")
    print(f"\n🎯 Speedup: {speedup:.2f}x faster ({improvement:.1f}% improvement)")
    print("\n💡 Note: With real LLM APIs (OpenAI/Ollama), the speedup would be even more dramatic!")
    print("   Async processing allows multiple LLM calls to run in parallel.")
    print("=" * 70)


if __name__ == "__main__":
    main()
