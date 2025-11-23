"""
Quick demo script to show RAGLint in action.
This demonstrates the typical user experience.
"""

import asyncio
import json
from raglint import RAGPipelineAnalyzer, Config

async def main():
    print("🔍 RAGLint Demo - Python API")
    print("=" * 60)
    print()
    
    # Step 1: Create configuration
    print("📝 Step 1: Creating configuration...")
    config = Config(provider="mock")  # Use mock LLM for demo
    print(f"   Provider: {config.provider}")
    print()
    
    # Step 2: Create analyzer
    print("🔧 Step 2: Initializing analyzer...")
    analyzer = RAGPipelineAnalyzer(config)
    print("   ✓ Analyzer ready!")
    print()
    
    # Step 3: Prepare test data
    print("📊 Step 3: Preparing test data...")
    test_data = [
        {
            "query": "What is RAG?",
            "retrieved_contexts": [
                "Retrieval-Augmented Generation (RAG) is a technique that enhances LLM responses.",
                "It retrieves relevant documents from a knowledge base.",
                "This helps reduce hallucinations."
            ],
            "response": "RAG is a method to improve LLM output by retrieving data."
        },
        {
            "query": "How does chunking work?",
            "retrieved_contexts": [
                "Chunking splits text into smaller pieces.",
                "Fixed-size chunking is common but can break sentences."
            ],
            "response": "Chunking divides text."
        }
    ]
    print(f"   Loaded {len(test_data)} test cases")
    print()
    
    # Step 4: Run evaluation
    print("⚡ Step 4: Running evaluation...")
    print("   (This may take a few seconds...)")
    print()
    
    result = await analyzer.analyze_async(test_data, show_progress=False)
    
    # Step 5: Display results
    print("=" * 60)
    print("📈 RESULTS")
    print("=" * 60)
    print()
    
    # Display detailed results
    for i, item_result in enumerate(result.detailed_results, 1):
        test_case = test_data[i-1]
        print(f"Query {i}: \"{test_case['query']}\"")
        print("-" * 60)
        
        # Extract metrics from detailed section
        detailed = item_result.get("detailed", {})
        
        # Display retrieval metrics
        if detailed.get("metrics"):
            metrics = detailed["metrics"]
            for metric_name, score in metrics.items():
                if isinstance(score, (int, float)):
                    emoji = "✓" if score >= 0.7 else "✗"
                    print(f"   {metric_name:20s}: {score:.2f} {emoji}")
        
        # Display semantic score
        if detailed.get("semantic_score"):
            score = detailed["semantic_score"]
            emoji = "✓" if score >= 0.7 else "✗"
            print(f"   {'semantic':20s}: {score:.2f} {emoji}")
        
        # Display faithfulness
        if detailed.get("faithfulness_score") is not None:
            score = detailed["faithfulness_score"]
            emoji = "✓" if score >= 0.7 else "✗"
            print(f"   {'faithfulness':20s}: {score:.2f} {emoji}")
        
        print()
    
    # Step 6: Calculate overall score
    print("=" * 60)
    print("📊 SUMMARY")
    print("=" * 60)
    
    # Collect scores from semantic and faithfulness
    all_scores = result.semantic_scores + result.faithfulness_scores
    avg_score = sum(all_scores) / len(all_scores) if all_scores else 0
    
    print(f"   Total queries analyzed: {len(test_data)}")
    print(f"   Average score: {avg_score:.2f}")
    print()
    
    if avg_score >= 0.85:
        print("   ✅ EXCELLENT! Your RAG system is performing well!")
    elif avg_score >= 0.70:
        print("   ⚠️  GOOD, but room for improvement")
    else:
        print("   ❌ NEEDS WORK - Consider improving your RAG pipeline")
    
    print()
    print("=" * 60)
    print("🎉 Demo complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
