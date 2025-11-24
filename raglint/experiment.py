"""
Experiment runner for A/B testing RAG configurations.
"""

from dataclasses import dataclass
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from raglint.config import Config
from raglint.core import AnalysisResult, RAGPipelineAnalyzer


@dataclass
class ComparisonResult:
    """Result of comparing two RAG configurations."""

    control_result: AnalysisResult
    treatment_result: AnalysisResult
    control_name: str = "Control"
    treatment_name: str = "Treatment"

    def metrics(self, result: AnalysisResult) -> dict[str, float]:
        """Aggregate all metrics into a single dict."""
        metrics = {}
        metrics.update(result.retrieval_stats)
        metrics.update(result.chunk_stats)

        # Add averages for list metrics
        if result.semantic_scores:
            metrics["semantic_similarity"] = sum(result.semantic_scores) / len(
                result.semantic_scores
            )
        if result.faithfulness_scores:
            metrics["faithfulness"] = sum(result.faithfulness_scores) / len(
                result.faithfulness_scores
            )

        return metrics

    @property
    def metrics_diff(self) -> dict[str, float]:
        """Calculate percentage difference for each metric (Treatment - Control)."""
        diffs = {}
        control_metrics = self.metrics(self.control_result)
        treatment_metrics = self.metrics(self.treatment_result)

        all_keys = set(control_metrics.keys()) | set(treatment_metrics.keys())

        for key in all_keys:
            c_val = control_metrics.get(key, 0.0)
            t_val = treatment_metrics.get(key, 0.0)

            if c_val == 0:
                diffs[key] = 0.0 if t_val == 0 else 100.0
            else:
                diffs[key] = ((t_val - c_val) / c_val) * 100.0

        return diffs

    def print_summary(self):
        """Print comparison summary to console."""
        console = Console()

        # Create table
        table = Table(title=f"A/B Test Results: {self.control_name} vs {self.treatment_name}")

        table.add_column("Metric", style="cyan")
        table.add_column(self.control_name, justify="right")
        table.add_column(self.treatment_name, justify="right")
        table.add_column("Diff", justify="right")

        diffs = self.metrics_diff
        control_metrics = self.metrics(self.control_result)
        treatment_metrics = self.metrics(self.treatment_result)

        # Sort keys for consistent output
        sorted_keys = sorted(set(control_metrics.keys()) | set(treatment_metrics.keys()))

        for key in sorted_keys:
            c_val = control_metrics.get(key, 0.0)
            t_val = treatment_metrics.get(key, 0.0)
            diff = diffs.get(key, 0.0)

            # Format diff with color
            if diff > 0:
                diff_str = f"[green]+{diff:.1f}%[/green]"
            elif diff < 0:
                diff_str = f"[red]{diff:.1f}%[/red]"
            else:
                diff_str = "0.0%"

            table.add_row(key.replace("_", " ").title(), f"{c_val:.4f}", f"{t_val:.4f}", diff_str)

        console.print(table)

        # Overall verdict
        # Simple heuristic: Count wins
        wins = sum(1 for k, v in diffs.items() if v > 0)
        losses = sum(1 for k, v in diffs.items() if v < 0)

        if wins > losses:
            console.print(
                Panel(
                    f"[bold green]WINNER: {self.treatment_name}[/bold green]\nTreatment improved {wins} metrics.",
                    title="Verdict",
                )
            )
        elif losses > wins:
            console.print(
                Panel(
                    f"[bold yellow]WINNER: {self.control_name}[/bold yellow]\nControl was better on {losses} metrics.",
                    title="Verdict",
                )
            )
        else:
            console.print(Panel("[bold blue]TIE[/bold blue]\nNo clear winner.", title="Verdict"))


class ExperimentRunner:
    """Runs A/B tests."""

    def __init__(self, control_config: Config, treatment_config: Config):
        self.control_config = control_config
        self.treatment_config = treatment_config

    async def run(
        self,
        data: list[dict[str, Any]],
        control_name: str = "Control",
        treatment_name: str = "Treatment",
    ) -> ComparisonResult:
        """
        Run experiment on dataset.

        Args:
            data: List of test cases
            control_name: Name for control group
            treatment_name: Name for treatment group

        Returns:
            ComparisonResult
        """
        print(f"Running analysis for {control_name}...")
        control_analyzer = RAGPipelineAnalyzer(
            use_smart_metrics=True,  # Assuming we want smart metrics for comparison
            config=self._config_to_dict(self.control_config),
        )
        control_result = await control_analyzer.analyze_async(data)

        print(f"Running analysis for {treatment_name}...")
        treatment_analyzer = RAGPipelineAnalyzer(
            use_smart_metrics=True, config=self._config_to_dict(self.treatment_config)
        )
        treatment_result = await treatment_analyzer.analyze_async(data)

        return ComparisonResult(
            control_result=control_result,
            treatment_result=treatment_result,
            control_name=control_name,
            treatment_name=treatment_name,
        )

    def _config_to_dict(self, config: Config) -> dict:
        """Convert Config object to dict for analyzer."""
        return {
            "provider": config.provider,
            "openai_api_key": config.openai_api_key,
            "model_name": config.model_name,
            "metrics": config.metrics,
            "thresholds": config.thresholds,
        }
