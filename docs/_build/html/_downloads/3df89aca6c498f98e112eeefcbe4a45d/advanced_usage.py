"""
Advanced RAGLint usage example showing all features.

This example demonstrates:
- Multiple analysis modes
- Custom configuration
- Async processing
- Result export
- Comparison
"""

import asyncio
import json
from pathlib import Path

from raglint import RAGPipelineAnalyzer
from raglint.config import Config
from raglint.reporting import generate_html_report


def load_sample_data():
    """Load sample data from file."""
    with open("sample_data.json") as f:
        return json.load(f)


def example_1_basic_analysis():
    """Example 1: Basic analysis without LLM."""
    print("\n" + "=" * 70)
    print("Example 1: Basic Analysis (No LLM)")
    print("=" * 70)

    data = load_sample_data()
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=False)
    results = analyzer.analyze(data)

    print(f"\n📊 Results:")
    print(f"  • Chunks analyzed: {len(results.chunk_stats)}")
    print(f"  • Mean chunk size: {results.chunk_stats['mean']:.2f} chars")
    print(f"  • Retrieval precision: {results.retrieval_stats['precision']:.2f}")
    print(f"  • Retrieval recall: {results.retrieval_stats['recall']:.2f}")

    return results


def example_2_smart_analysis_mock():
    """Example 2: Smart analysis with mock LLM."""
    print("\n" + "=" * 70)
    print("Example 2: Smart Analysis (Mock Mode)")
    print("=" * 70)

    data = load_sample_data()
    config = {"provider": "mock"}
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=True, config=config)
    results = analyzer.analyze(data, show_progress=False)

    print(f"\n🧠 Smart Metrics:")
    if results.semantic_scores:
        avg_semantic = sum(results.semantic_scores) / len(results.semantic_scores)
        print(f"  • Average semantic similarity: {avg_semantic:.2f}")

    if results.faithfulness_scores:
        avg_faith = sum(results.faithfulness_scores) / len(results.faithfulness_scores)
        print(f"  • Average faithfulness: {avg_faith:.2f}")

    print(f"  • Mode: {'MOCK' if results.is_mock else 'REAL'}")

    return results


async def example_3_async_processing():
    """Example 3: Explicit async processing."""
    print("\n" + "=" * 70)
    print("Example 3: Async Processing")
    print("=" * 70)

    data = load_sample_data()
    config = {"provider": "mock"}
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=True, config=config)

    print("\n⚡ Running async analysis...")
    results = await analyzer.analyze_async(data, show_progress=True)

    print(f"\n✅ Async analysis complete!")
    print(f"  • Items processed: {len(results.detailed_results)}")
    print(f"  • Faithfulness scores: {len(results.faithfulness_scores)}")

    return results


def example_4_custom_config():
    """Example 4: Custom configuration."""
    print("\n" + "=" * 70)
    print("Example 4: Custom Configuration")
    print("=" * 70)

    # Create custom config
    config = Config(
        provider="mock",
        model_name="custom-model",
        thresholds={"faithfulness": 0.8, "relevance": 0.75},
    )

    print(f"\n⚙️  Configuration:")
    print(f"  • Provider: {config.provider}")
    print(f"  • Model: {config.model_name}")
    print(f"  • Faithfulness threshold: {config.thresholds['faithfulness']}")

    config_dict = {
        "provider": config.provider,
        "model_name": config.model_name,
        "thresholds": config.thresholds,
    }

    data = load_sample_data()
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=True, config=config_dict)
    results = analyzer.analyze(data, show_progress=False)

    print(f"\n✅ Analysis complete with custom config")

    return results


def example_5_detailed_inspection():
    """Example 5: Detailed result inspection."""
    print("\n" + "=" * 70)
    print("Example 5: Detailed Result Inspection")
    print("=" * 70)

    data = load_sample_data()
    config = {"provider": "mock"}
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=True, config=config)
    results = analyzer.analyze(data, show_progress=False)

    print(f"\n🔍 Detailed Inspection:")
    for i, item_result in enumerate(results.detailed_results, 1):
        print(f"\n  Item {i}: {item_result['query'][:50]}...")
        print(f"    Precision: {item_result['metrics']['precision']:.2f}")
        print(f"    Recall: {item_result['metrics']['recall']:.2f}")

        if item_result.get("semantic_score"):
            print(f"    Semantic: {item_result['semantic_score']:.2f}")

        if item_result.get("faithfulness_score"):
            print(f"    Faithfulness: {item_result['faithfulness_score']:.2f}")


def example_6_export_results():
    """Example 6: Export results to JSON."""
    print("\n" + "=" * 70)
    print("Example 6: Export Results")
    print("=" * 70)

    data = load_sample_data()
    config = {"provider": "mock"}
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=True, config=config)
    results = analyzer.analyze(data, show_progress=False)

    # Export to JSON
    export_data = {
        "chunk_stats": results.chunk_stats,
        "retrieval_stats": results.retrieval_stats,
        "semantic_scores": results.semantic_scores,
        "faithfulness_scores": results.faithfulness_scores,
        "is_mock": results.is_mock,
        "total_items": len(results.detailed_results),
    }

    output_file = "results_export.json"
    with open(output_file, "w") as f:
        json.dump(export_data, f, indent=2)

    print(f"\n💾 Results exported to: {output_file}")
    print(f"  • File size: {Path(output_file).stat().st_size} bytes")


def example_7_generate_reports():
    """Example 7: Generate multiple reports."""
    print("\n" + "=" * 70)
    print("Example 7: Generate Multiple Reports")
    print("=" * 70)

    data = load_sample_data()

    # Generate basic report
    analyzer_basic = RAGPipelineAnalyzer(use_smart_metrics=False)
    results_basic = analyzer_basic.analyze(data, show_progress=False)
    generate_html_report(results_basic, "report_basic.html")
    print(f"\n📄 Generated: report_basic.html")

    # Generate smart report
    config = {"provider": "mock"}
    analyzer_smart = RAGPipelineAnalyzer(use_smart_metrics=True, config=config)
    results_smart = analyzer_smart.analyze(data, show_progress=False)
    generate_html_report(results_smart, "report_smart.html")
    print(f"📄 Generated: report_smart.html")

    print(f"\n✅ All reports generated!")


def main():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("🚀 RAGLint Advanced Usage Examples")
    print("=" * 70)

    # Run synchronous examples
    example_1_basic_analysis()
    example_2_smart_analysis_mock()
    example_4_custom_config()
    example_5_detailed_inspection()
    example_6_export_results()
    example_7_generate_reports()

    # Run async example
    print("\n" + "=" * 70)
    print("Running async example...")
    print("=" * 70)
    asyncio.run(example_3_async_processing())

    print("\n" + "=" * 70)
    print("✅ All Examples Completed!")
    print("=" * 70)
    print("\n📚 Check generated files:")
    print("  • report_basic.html")
    print("  • report_smart.html")
    print("  • results_export.json")
    print("\n🎉 Happy analyzing!")


if __name__ == "__main__":
    main()
