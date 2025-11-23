import json
import sys
from pathlib import Path

import click

from .config import Config
from .core import RAGPipelineAnalyzer
from .logging import get_logger, setup_logging
from .reporting import generate_html_report

logger = get_logger(__name__)


@click.group()
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging")
@click.option("--log-file", type=click.Path(), help="Log file path")
@click.pass_context
def cli(ctx, verbose, log_file):
    """RAG Pipeline Quality Checker"""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["log_file"] = log_file

    # Setup logging
    setup_logging(
        level="DEBUG" if verbose else "INFO",
        log_file=Path(log_file) if log_file else None,
        verbose=verbose,
    )


@cli.command()
@click.argument("data_file", type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), default="raglint_report.html")
@click.option("--smart", is_flag=True, help="Enable smart metrics (LLM-based).")
@click.option(
    "--config", type=click.Path(exists=True), help="Path to raglint.yml config file."
)
@click.option("--api-key", help="OpenAI API key (overrides config).")
@click.option("--provider", type=click.Choice(["openai", "ollama", "mock"]), help="LLM provider to use.")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose logging.")
@click.option("--log-file", type=click.Path(), help="Path to log file.")
def analyze(
    data_file, output, smart, config: str | None, api_key: str | None, provider: str | None, verbose, log_file
):
    """Analyze a RAG pipeline from DATA_FILE."""
    # Setup logging
    log_level = "DEBUG" if verbose else "INFO"
    setup_logging(level=log_level, log_file=Path(log_file) if log_file else None, verbose=verbose)
    click.echo(f"Analyzing {data_file}...")
    logger.info(f"Starting analysis of {data_file}")

    try:
        # Load and validate input data
        with open(data_file) as f:
            data = json.load(f)

        if not isinstance(data, list):
            logger.error("Input data must be a list of dictionaries.")
            click.echo("Error: Input data must be a list of dictionaries.", err=True)
            sys.exit(1)

        if len(data) == 0:
            logger.warning("Input data is empty")
            click.echo("Warning: Input data is empty.")

        # Load config
        if config:
            cfg = Config.load(config)
        else:
            cfg = Config.load()

        # CLI overrides
        if api_key:
            cfg.openai_api_key = api_key
            cfg.provider = "openai"  # Assume OpenAI if key provided directly
            
        if provider:
            cfg.provider = provider

        # Prepare config dict
        config_dict = {
            "provider": cfg.provider,
            "openai_api_key": cfg.openai_api_key,
            "model_name": cfg.model_name,
            "metrics": cfg.metrics,
            "thresholds": cfg.thresholds,
        }

        # Initialize analyzer
        use_smart = smart
        analyzer = RAGPipelineAnalyzer(use_smart_metrics=use_smart, config=config_dict)

        # Check if mock mode and warn user
        if use_smart and cfg.provider == "mock":
            click.echo()
            click.echo(
                "⚠️  WARNING: Running in MOCK MODE. Smart metrics will be fake (1.0)."
            )
            click.echo(
                "   Configure 'provider: openai' or 'provider: ollama' in raglint.yml to use real metrics."
            )
            click.echo(
                "   Or use --provider ollama via CLI."
            )
            click.echo()

        results = analyzer.analyze(data)

        click.echo("Analysis complete.")
        click.echo(f"Chunk Size Mean: {results.chunk_stats['mean']:.2f}")
        click.echo(f"Retrieval Precision: {results.retrieval_stats['precision']:.2f}")
        click.echo(f"Retrieval Recall: {results.retrieval_stats['recall']:.2f}")

        if smart:
            avg_semantic = (
                sum(results.semantic_scores) / len(results.semantic_scores)
                if results.semantic_scores
                else 0.0
            )
            avg_faithfulness = (
                sum(results.faithfulness_scores) / len(results.faithfulness_scores)
                if results.faithfulness_scores
                else 0.0
            )
            click.echo(f"Semantic Similarity: {avg_semantic:.2f}")
            click.echo(f"Faithfulness Score: {avg_faithfulness:.2f}")

        generate_html_report(results, output)
        click.echo(f"Report saved to {output}")
        logger.info(f"Analysis completed successfully. Report saved to {output}")

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in input file: {e}")
        click.echo(f"Error: Invalid JSON in input file: {e}", err=True)
        sys.exit(1)
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        click.echo(f"Error: File not found: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        logger.exception("Error during analysis")
        click.echo(f"Error during analysis: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("file1", type=click.Path(exists=True))
@click.argument("file2", type=click.Path(exists=True))
@click.pass_context
def compare(ctx, file1, file2):
    """Compare two RAGLint analysis results (JSON files)."""
    click.echo(f"Comparing {file1} vs {file2}...")
    logger.info(f"Starting comparison: {file1} vs {file2}")

    try:
        with open(file1) as f1, open(file2) as f2:
            data1 = json.load(f1)
            data2 = json.load(f2)

        # Run quick analysis (fast mode for speed)
        analyzer = RAGPipelineAnalyzer(use_smart_metrics=False)
        res1 = analyzer.analyze(data1)
        res2 = analyzer.analyze(data2)

        # Calculate diffs
        prec_diff = res2.retrieval_stats["precision"] - res1.retrieval_stats["precision"]
        recall_diff = res2.retrieval_stats["recall"] - res1.retrieval_stats["recall"]

        click.echo("\n--- Comparison Report ---")
        click.echo(
            f"Precision: {res1.retrieval_stats['precision']:.2f} -> {res2.retrieval_stats['precision']:.2f} ({prec_diff:+.2f})"
        )
        click.echo(
            f"Recall:    {res1.retrieval_stats['recall']:.2f} -> {res2.retrieval_stats['recall']:.2f} ({recall_diff:+.2f})"
        )

        if prec_diff < 0 or recall_diff < 0:
            click.echo("\n⚠️  Regression Detected!")
        else:
            click.echo("\n✅  No Regressions.")

        logger.info("Comparison completed successfully")

    except Exception as e:
        logger.exception("Error during comparison")
        click.echo(f"Error during comparison: {e}", err=True)
        sys.exit(1)


@cli.group()
def plugins():
    """Manage RAGLint plugins."""
    pass


@plugins.command(name="list")
@click.option("--plugins-dir", type=click.Path(exists=True), help="Directory to load plugins from")
def list_plugins(plugins_dir):
    """List all installed and loaded plugins."""
    from raglint.plugins.loader import PluginLoader
    
    loader = PluginLoader.get_instance()
    loader.load_plugins(plugins_dir)
    
    plugins = loader.get_all_plugins()
    
    if not plugins:
        click.echo("No plugins found.")
        return

    click.echo(f"Found {len(plugins)} plugins:")
    for p in plugins:
        click.echo(f"- {p['name']} (v{p['version']}) [{p['type']}]: {p['description']}")


@plugins.command(name="install")
@click.argument("plugin_name")
@click.option("--version", help="Specific version to install")
def install_plugin(plugin_name, version):
    """Install a plugin from the marketplace."""
    from raglint.plugins.loader import PluginRegistry, PluginLoader
    
    click.echo(f"Installing plugin '{plugin_name}'...")
    registry = PluginRegistry()
    
    try:
        success = registry.install_plugin(plugin_name, version=version)
        if success:
            click.echo(f"✅ Successfully installed {plugin_name}")
            # Verify load
            PluginLoader.get_instance().load_plugins()
        else:
            click.echo(f"❌ Failed to install {plugin_name}", err=True)
            sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.group()
def config():
    """Manage RAGLint configuration."""
    pass

@config.command()
@click.option("-m", "--message", help="Description of this configuration version")
@click.option("--config", "config_path", default="raglint.yaml", help="Path to configuration file")
def snapshot(message, config_path):
    """Save the current configuration as a new version."""
    import hashlib
    import json
    import asyncio
    from raglint.config import Config
    from raglint.dashboard.database import init_db, SessionLocal
    from raglint.dashboard.models import PipelineVersion
    
    # Load config
    try:
        cfg = Config.load(config_path)
        from dataclasses import asdict
        config_dict = asdict(cfg)
        # Canonical JSON for hashing
        config_json = json.dumps(config_dict, sort_keys=True)
        config_hash = hashlib.sha256(config_json.encode()).hexdigest()
    except Exception as e:
        click.echo(f"Error loading config: {e}", err=True)
        return

    async def _save_snapshot():
        await init_db()
        async with SessionLocal() as session:
            # Check if exists
            from sqlalchemy import select
            result = await session.execute(select(PipelineVersion).where(PipelineVersion.hash == config_hash))
            existing = result.scalar_one_or_none()
            
            if existing:
                click.echo(f"Configuration version already exists: {existing.id[:8]}")
                if message and not existing.description:
                    existing.description = message
                    await session.commit()
                    click.echo("Updated description.")
                return

            # Create new
            import uuid
            new_id = str(uuid.uuid4())
            version = PipelineVersion(
                id=new_id,
                hash=config_hash,
                config=config_dict,
                description=message
            )
            session.add(version)
            await session.commit()
            click.echo(f"Created new configuration version: {new_id[:8]}")

    asyncio.run(_save_snapshot())

@cli.command()
@click.option("--host", default="127.0.0.1", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
def dashboard(host, port, reload):
    """Start the RAGLint Web Dashboard."""
    import uvicorn
    
    click.echo(f"Starting RAGLint Dashboard at http://{host}:{port}")
    uvicorn.run("raglint.dashboard.app:app", host=host, port=port, reload=reload)


@cli.command("benchmark")
@click.option("--dataset", "-d", type=click.Choice(["squad", "coqa", "hotpotqa"]), default="squad", help="Benchmark dataset to use")
@click.option("--subset-size", "-n", type=int, default=50, help="Number of examples to evaluate")
@click.option("--output", "-o", type=click.Path(dir_okay=False, writable=True), default=None, help="Output file for results")
@click.option("--config-path", "--config", "-c", type=click.Path(exists=True, dir_okay=False), default=None)
@click.option("--show-progress/--no-progress", default=True)
def benchmark(dataset, subset_size, output, config_path, show_progress):
    """Run RAGLint on a standard benchmark dataset."""
    try:
        from raglint.benchmarks import BenchmarkRegistry
        from raglint.config import Config
        from raglint.analyzer import RAGPipelineAnalyzer
        from raglint.benchmarks.utils import create_summary_metrics, display_result, save_result
        
        click.echo(f"Loading {dataset.upper()} benchmark ({subset_size} examples)...")
        test_data = BenchmarkRegistry.load(dataset, subset_size=subset_size)
        
        cfg = Config.load(config_path) if config_path else Config.load()
        analyzer = RAGPipelineAnalyzer(use_smart_metrics=True, config=cfg.as_dict())
        
        click.echo(f"Running evaluation...")
        result = analyzer.analyze(test_data, show_progress=show_progress)
        summary = create_summary_metrics(result)
        
        if output:
            save_result(result, summary, output)
            click.echo(f"Results saved to: {output}")
        else:
            click.echo("\n" + "="*60)
            click.echo("BENCHMARK RESULTS")
            click.echo("="*60)
            display_result(result, summary)
            
    except Exception as e:
        logger.error(f"Error during benchmark: {e}", exc_info=True)
        click.echo(f"Error: {e}", err=True)


@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--count", "-n", default=10, help="Number of QA pairs to generate")
@click.option("--output", "-o", type=click.Path(), default="testset.json", help="Output JSON file")
@click.option("--api-key", help="OpenAI API key")
def generate(input_file, count, output, api_key):
    """
    Generate a synthetic testset from a document (PDF or Text).
    
    INPUT_FILE: Path to the source document.
    """
    from raglint.generation import TestsetGenerator
    from raglint.config import Config
    import asyncio
    import json
    
    # Setup config
    cfg = Config.load()
    if api_key:
        cfg.openai_api_key = api_key
        cfg.provider = "openai"
        
    if not cfg.openai_api_key and cfg.provider == "openai":
        click.echo("Error: OpenAI API key is required for generation. Set OPENAI_API_KEY env var or use --api-key.", err=True)
        sys.exit(1)
        
    click.echo(f"Generating {count} QA pairs from {input_file}...")
    
    generator = TestsetGenerator(config=cfg)
    
    try:
        results = asyncio.run(generator.generate_from_file(input_file, count))
        
        if not results:
            click.echo("Failed to generate any valid QA pairs.", err=True)
            sys.exit(1)
            
        with open(output, 'w') as f:
            json.dump(results, f, indent=2)
            
        click.echo(f"✅ Successfully generated {len(results)} pairs.")
        click.echo(f"Saved to: {output}")
        
    except ImportError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        logger.exception("Generation failed")
        click.echo(f"Error during generation: {e}", err=True)
        sys.exit(1)


@cli.group()
def cost():
    """Manage and estimate costs."""
    pass

@cost.command(name="estimate")
@click.argument("input_file", type=click.Path(exists=True))
@click.option("--model", default="gpt-4o", help="Model to estimate cost for")
def estimate_cost(input_file, model):
    """
    Estimate cost for analyzing a dataset.
    
    INPUT_FILE: Path to the dataset (JSON).
    """
    import json
    from raglint.tracking import LLM_PRICING
    
    if model not in LLM_PRICING:
        click.echo(f"Error: Unknown model '{model}'. Available: {', '.join(LLM_PRICING.keys())}", err=True)
        sys.exit(1)
        
    try:
        with open(input_file) as f:
            data = json.load(f)
            
        if not isinstance(data, list):
            click.echo("Error: Input file must be a list of items.", err=True)
            sys.exit(1)
            
        num_items = len(data)
        
        # Rough estimation: 
        # Input: Query + Contexts + System Prompt (~500 tokens)
        # Output: Evaluation reasoning + Score (~200 tokens)
        # We run multiple metrics per item.
        
        # Let's assume 4 metrics per item (Faithfulness, Context Rel, Answer Rel, Semantic)
        # Semantic is embedding based (cheap), others are LLM based.
        metrics_count = 3 
        
        avg_input_tokens = 1000 # Conservative estimate
        avg_output_tokens = 200 
        
        total_input = num_items * metrics_count * avg_input_tokens
        total_output = num_items * metrics_count * avg_output_tokens
        
        pricing = LLM_PRICING[model]
        cost = (total_input / 1000 * pricing["input"]) + (total_output / 1000 * pricing["output"])
        
        click.echo(f"💰 Cost Estimation for {input_file}")
        click.echo(f"-----------------------------------")
        click.echo(f"Items: {num_items}")
        click.echo(f"Model: {model}")
        click.echo(f"Est. Input Tokens: {total_input:,}")
        click.echo(f"Est. Output Tokens: {total_output:,}")
        click.echo(f"-----------------------------------")
        click.echo(f"Total Estimated Cost: ${cost:.4f}")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

if __name__ == "__main__":
    cli()
