"""
Enhanced CLI for RAGLint with better UX
"""

import json
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

console = Console()

@click.group()
@click.version_option(version="0.1.0")
def cli():
    """RAGLint - Production-ready RAG evaluation & observability"""
    pass

# === EVAL COMMAND ===
@cli.command()
@click.argument('pipeline_file', type=click.Path(exists=True))
@click.option('--config', '-c', type=click.Path(exists=True), help='Config file (raglint.yml)')
@click.option('--output', '-o', type=click.Path(), help='Output report path')
@click.option('--format', '-f', type=click.Choice(['html', 'json', 'pdf']), default='html', help='Report format')
def eval(pipeline_file, config, output, format):
    """Evaluate a RAG pipeline (shorthand for 'analyze')"""
    console.print(f"[bold blue]Evaluating pipeline:[/] {pipeline_file}")

    from raglint.config import Config
    from raglint.core import RAGPipelineAnalyzer

    # Load config
    cfg = Config.load(config) if config else Config()

    # Load data
    with open(pipeline_file) as f:
        data = json.load(f)

    # Analyze
    analyzer = RAGPipelineAnalyzer(cfg)
    results = analyzer.analyze(data)

    # Generate report
    if format == 'html':
        from raglint.reporting.html import generate_report
        output_path = output or 'raglint_report.html'
        generate_report(results, str(output_path))
        console.print(f"[green]✓[/] Report saved to: {output_path}")

    elif format == 'json':
        output_path = output or 'raglint_report.json'
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        console.print(f"[green]✓[/] Report saved to: {output_path}")

    elif format == 'pdf':
        console.print("[yellow]PDF export requires dashboard. Use: /runs/{id}/export/pdf[/]")


# === WATCH COMMAND ===
@cli.group()
def watch():
    """Manage auto-instrumentation monitoring"""
    pass

@watch.command('start')
@click.option('--file', '-f', default='raglint_events.jsonl', help='Output file for events')
def watch_start(file):
    """Start monitoring (creates trace file)"""
    from raglint.instrumentation import Monitor

    monitor = Monitor()
    monitor.trace_file = Path(file)
    monitor.enable()

    console.print(f"[green]✓[/] Monitoring started. Events → {file}")
    console.print("[dim]Use @raglint.watch decorator in your code[/]")

@watch.command('stop')
def watch_stop():
    """Stop monitoring"""
    from raglint.instrumentation import Monitor

    monitor = Monitor()
    monitor.disable()

    console.print("[green]✓[/] Monitoring stopped")

@watch.command('status')
def watch_status():
    """Check monitoring status"""
    from raglint.instrumentation import Monitor

    monitor = Monitor()
    status = "enabled" if monitor.enabled else "disabled"

    table = Table(title="Monitoring Status")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Status", status.upper())
    table.add_row("Trace File", str(monitor.trace_file))

    console.print(table)


# === REPORT COMMAND ===
@cli.command()
@click.argument('run_id', required=False)
@click.option('--format', '-f', type=click.Choice(['html', 'json', 'pdf']), default='html')
@click.option('--output', '-o', type=click.Path())
def report(run_id, format, output):
    """Generate report from a run (default: latest)"""

    if not run_id:
        run_id = "latest"
        console.print("[dim]Using latest run...[/]")

    # TODO: Fetch from database
    console.print(f"[yellow]Generating {format.upper()} report for run: {run_id}[/]")
    console.print("[dim]Tip: Use dashboard UI for better reports[/]")


# === DASHBOARD COMMAND ===
@cli.command()
@click.option('--port', '-p', default=8000, help='Port to run on')
@click.option('--host', '-h', default='0.0.0.0', help='Host to bind to')
def dashboard(port, host):
    """Launch the web dashboard"""
    console.print("[bold blue]Starting RAGLint Dashboard...[/]")
    console.print(f"[dim]URL: http://localhost:{port}[/]")

    import uvicorn
    uvicorn.run(
        "raglint.dashboard.app:app",
        host=host,
        port=port,
        reload=True
    )


# === PLUGIN COMMAND ===
@cli.group()
def plugin():
    """Manage evaluation plugins"""
    pass

@plugin.command('list')
def plugin_list():
    """List installed plugins"""
    from raglint.plugins.loader import PluginLoader

    loader = PluginLoader()
    plugins = loader.list_plugins()

    table = Table(title="Installed Plugins")
    table.add_column("Name", style="cyan")
    table.add_column("Type", style="green")
    table.add_column("Description", style="dim")

    for p in plugins:
        table.add_row(p['name'], p['type'], p.get('description', ''))

    console.print(table)

@plugin.command('install')
@click.argument('plugin_name')
def plugin_install(plugin_name):
    """Install a plugin from marketplace"""
    console.print(f"[yellow]Installing plugin: {plugin_name}[/]")

    # Download from registry
    import requests
    registry_url = f"https://raglint.io/api/plugins/{plugin_name}"

    try:
        resp = requests.get(registry_url)
        if resp.status_code == 200:
            plugin_code = resp.text

            # Save to plugins dir
            plugin_dir = Path.home() / '.raglint' / 'plugins'
            plugin_dir.mkdir(parents=True, exist_ok=True)

            plugin_file = plugin_dir / f"{plugin_name}.py"
            plugin_file.write_text(plugin_code)

            console.print(f"[green]✓[/] Plugin installed: {plugin_file}")
        else:
            console.print("[red]✗[/] Plugin not found in marketplace")
    except Exception as e:
        console.print(f"[red]✗[/] Error: {e}")


if __name__ == "__main__":
    cli()
