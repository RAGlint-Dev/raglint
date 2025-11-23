"""CLI extension for precision mode."""

import click
import asyncio
import json
from pathlib import Path

from raglint.core import RAGPipelineAnalyzer
from raglint.config import Config
from raglint.precision_mode import PrecisionMode
from raglint.metrics.enhanced_faithfulness import EnhancedFaithfulnessScorer


@click.command()
@click.argument('data_file', type=click.Path(exists=True))
@click.option('--precision', is_flag=True, help='Enable 99%+ precision mode')
@click.option('--confidence-threshold', default=0.90, type=float, 
              help='Minimum confidence threshold (0.0-1.0)')
@click.option('--output', '-o', type=click.Path(), help='Output JSON file')
@click.option('--provider', default='mock', help='LLM provider (mock/openai/ollama)')
def analyze_precision(data_file, precision, confidence_threshold, output, provider):
    """
    Analyze RAG pipeline with optional precision mode.
    
    Example:
        raglint-precision data.json --precision --confidence-threshold 0.95
    """
    # Load config
    config = Config(provider=provider)
    
    # Load data
    with open(data_file) as f:
        data = json.load(f)
    
    if not isinstance(data, list):
        data = [data]
    
    # Run analysis
    results = asyncio.run(
        run_precision_analysis(data, config, precision, confidence_threshold)
    )
    
    # Output results
    if output:
        with open(output, 'w') as f:
            json.dump(results, f, indent=2)
        click.echo(f"✅ Results saved to {output}")
    else:
        # Print summary
        print_precision_summary(results, precision)


async def run_precision_analysis(data, config, use_precision, confidence_threshold):
    """Run analysis with optional precision mode."""
    analyzer = RAGPipelineAnalyzer(config)
    
    if not use_precision:
        # Standard analysis
        return await analyzer.evaluate_batch_async(data)
    
    # Precision mode analysis
    precision_mode = PrecisionMode(
        confidence_threshold=confidence_threshold
    )
    
    results = []
    for item in data:
        query = item.get("query", "")
        response = item.get("response", "")
        contexts = item.get("retrieved_contexts", [])
        
        # Use enhanced metrics
        llm = analyzer.llm
        enhanced_faithfulness = EnhancedFaithfulnessScorer(llm)
        
        # Get precision score
        faith_result = await enhanced_faithfulness.precision_score(
            query=query,
            response=response,
            retrieved_contexts=contexts,
            confidence_threshold=confidence_threshold
        )
        
        results.append({
            "query": query,
            "response": response,
            "precision_results": faith_result,
            "approved": faith_result.get("approved", False),
            "needs_review": faith_result.get("needs_review", True)
        })
    
    return results


def print_precision_summary(results, precision_mode):
    """Print summary of precision analysis."""
    click.echo("\n" + "="*60)
    click.echo("RAGLint Precision Analysis Results")
    click.echo("="*60 + "\n")
    
    if not precision_mode:
        click.echo(f"Total items analyzed: {len(results)}")
        return
    
    # Precision mode stats
    total = len(results)
    approved = sum(1 for r in results if r.get("approved", False))
    needs_review = sum(1 for r in results if r.get("needs_review", True))
    
    click.echo(f"Total items analyzed: {total}")
    click.echo(f"High-precision approved: {approved} ({approved/total*100:.1f}%)")
    click.echo(f"Flagged for review: {needs_review} ({needs_review/total*100:.1f}%)")
    click.echo()
    
    # Show flagged items
    if needs_review > 0:
        click.echo("⚠️  Items flagged for human review:")
        for idx, r in enumerate(results):
            if r.get("needs_review"):
                reason = r.get("precision_results", {}).get("review_reason", "Unknown")
                click.echo(f"  {idx+1}. {reason}")


if __name__ == '__main__':
    analyze_precision()
