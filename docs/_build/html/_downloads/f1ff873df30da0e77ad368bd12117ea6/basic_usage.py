"""
Basic RAGLint usage example.

This script demonstrates how to use RAGLint to analyze RAG pipeline data.
"""

import json

from raglint import RAGPipelineAnalyzer
from raglint.reporting import generate_html_report


def main():
    print("=" * 70)
    print("RAGLint Basic Usage Example")
    print("=" * 70)

    # Load sample data
    print("\n📂 Loading sample data...")
    with open("sample_data.json") as f:
        data = json.load(f)
    
    print(f"   ✓ Loaded {len(data)} RAG interactions")

    # Example 1: Basic Analysis (fast, no LLM)
    print("\n🔍 Example 1: Basic Analysis")
    print("-" * 70)
    
    analyzer_basic = RAGPipelineAnalyzer(use_smart_metrics=False)
    results_basic = analyzer_basic.analyze(data)

    print(f"✓ Analysis complete!")
    print(f"\n📊 Basic Metrics:")
    print(f"   • Chunk Size Mean: {results_basic.chunk_stats['mean']:.2f}")
    print(f"   • Chunk Size Std: {results_basic.chunk_stats['std']:.2f}")
    print(f"   • Retrieval Precision: {results_basic.retrieval_stats['precision']:.2f}")
    print(f"   • Retrieval Recall: {results_basic.retrieval_stats['recall']:.2f}")
    print(f"   • MRR: {results_basic.retrieval_stats['mrr']:.2f}")

    # Example 2: Smart Analysis (LLM-based, using mock mode)
    print("\n\n🧠 Example 2: Smart Analysis (Mock Mode)")
    print("-" * 70)
    
    config = {"provider": "mock"}  # Use "openai" for real analysis
    analyzer_smart = RAGPipelineAnalyzer(use_smart_metrics=True, config=config)
    results_smart = analyzer_smart.analyze(data, show_progress=True)

    print(f"\n✓ Smart analysis complete!")
    print(f"\n📊 Smart Metrics:")
    
    if results_smart.semantic_scores:
        avg_semantic = sum(results_smart.semantic_scores) / len(results_smart.semantic_scores)
        print(f"   • Semantic Similarity: {avg_semantic:.2f}")
    
    if results_smart.faithfulness_scores:
        avg_faithfulness = sum(results_smart.faithfulness_scores) / len(results_smart.faithfulness_scores)
        print(f"   • Faithfulness Score: {avg_faithfulness:.2f}")

    # Example 3: Generate HTML Report
    print("\n\n📝 Example 3: Generate HTML Report")
    print("-" * 70)
    
    output_file = "raglint_report.html"
    generate_html_report(results_smart, output_file)
    print(f"   ✓ Report saved to: {output_file}")
    print(f"   → Open in your browser to view interactive visualizations!")

    # Example 4: Accessing Detailed Results
    print("\n\n📋 Example 4: Accessing Detailed Results")
    print("-" * 70)
    
    print(f"\nDetailed results for first interaction:")
    first_result = results_smart.detailed_results[0]
    print(f"   • Query: {first_result['query']}")
    print(f"   • Precision: {first_result['metrics']['precision']:.2f}")
    print(f"   • Recall: {first_result['metrics']['recall']:.2f}")
    
    if first_result.get('semantic_score'):
        print(f"   • Semantic Score: {first_result['semantic_score']:.2f}")
    
    if first_result.get('faithfulness_score'):
        print(f"   • Faithfulness: {first_result['faithfulness_score']:.2f}")

    print("\n" + "=" * 70)
    print("✅ Examples completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
