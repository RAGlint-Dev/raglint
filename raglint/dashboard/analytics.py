"""
Advanced Analytics for RAGLint Dashboard.

Provides drift detection, embedding visualization, and cohort analysis.
"""

import logging
from datetime import datetime
from typing import Any, Optional

import numpy as np

logger = logging.getLogger(__name__)


class DriftDetector:
    """Detect metric drift over time."""

    def detect_drift(self, historical_data: list[dict[str, Any]],
                    metric_name: str,
                    threshold: float = 0.15) -> dict[str, Any]:
        """
        Detect if a metric has drifted significantly from baseline.

        Args:
            historical_data: List of run data with timestamps
            metric_name: Name of the metric to check
            threshold: Percentage change threshold (0.15 = 15%)

        Returns:
            Dict with drift analysis
        """
        if len(historical_data) < 2:
            return {"drift_detected": False, "reason": "Insufficient data"}

        # Sort by timestamp
        sorted_data = sorted(historical_data, key=lambda x: x.get('timestamp', datetime.now()))

        # Extract metric values
        values = []
        timestamps = []
        for run in sorted_data:
            if metric_name in run.get('metrics', {}):
                values.append(run['metrics'][metric_name])
                timestamps.append(run.get('timestamp', datetime.now()))

        if len(values) < 2:
            return {"drift_detected": False, "reason": "Insufficient metric data"}

        # Calculate baseline (first 30% of data)
        baseline_size = max(1, len(values) // 3)
        baseline_mean = np.mean(values[:baseline_size])

        # Calculate recent mean (last 30% of data)
        recent_size = max(1, len(values) // 3)
        recent_mean = np.mean(values[-recent_size:])

        # Calculate drift
        if baseline_mean == 0:
            drift_percentage = 0
        else:
            drift_percentage = abs(recent_mean - baseline_mean) / baseline_mean

        drift_detected = drift_percentage > threshold

        return {
            "drift_detected": drift_detected,
            "baseline_mean": float(baseline_mean),
            "recent_mean": float(recent_mean),
            "drift_percentage": float(drift_percentage),
            "threshold": threshold,
            "direction": "increase" if recent_mean > baseline_mean else "decrease",
            "timestamps": [ts.isoformat() if isinstance(ts, datetime) else str(ts) for ts in timestamps],
            "values": [float(v) for v in values]
        }


class EmbeddingVisualizer:
    """Visualize embeddings using UMAP."""

    def __init__(self):
        try:
            import umap
            self.umap_reducer = umap.UMAP(n_components=2, random_state=42)
            self.available = True
        except ImportError:
            logger.warning("UMAP not available. Install umap-learn for embedding visualization.")
            self.available = False

    def reduce_dimensions(self, embeddings: list[list[float]],
                         labels: Optional[list[str]] = None) -> dict[str, Any]:
        """
        Reduce embedding dimensions to 2D for visualization.

        Args:
            embeddings: List of embedding vectors
            labels: Optional labels for each embedding

        Returns:
            Dict with 2D coordinates and labels
        """
        if not self.available:
            return {"error": "UMAP not available"}

        if len(embeddings) < 2:
            return {"error": "Need at least 2 embeddings"}

        # Convert to numpy array
        X = np.array(embeddings)

        # Reduce dimensions
        X_2d = self.umap_reducer.fit_transform(X)

        return {
            "x": X_2d[:, 0].tolist(),
            "y": X_2d[:, 1].tolist(),
            "labels": labels if labels else [f"Point {i}" for i in range(len(embeddings))]
        }


class CohortAnalyzer:
    """Analyze and compare cohorts of runs."""

    def analyze_cohorts(self, runs: list[dict[str, Any]],
                       group_by: str = "config_hash") -> dict[str, Any]:
        """
        Group runs into cohorts and compare metrics.

        Args:
            runs: List of run data
            group_by: Field to group by (config_hash, tags, etc.)

        Returns:
            Dict with cohort comparison
        """
        cohorts = {}

        for run in runs:
            # Get grouping key
            if group_by == "tags":
                key = ",".join(sorted(run.get('tags', [])))
            else:
                key = run.get(group_by, "default")

            if key not in cohorts:
                cohorts[key] = []
            cohorts[key].append(run)

        # Calculate cohort statistics
        cohort_stats = {}
        for cohort_name, cohort_runs in cohorts.items():
            metrics_summary = {}

            # Aggregate metrics across runs
            for run in cohort_runs:
                for metric_name, value in run.get('metrics', {}).items():
                    if metric_name not in metrics_summary:
                        metrics_summary[metric_name] = []
                    metrics_summary[metric_name].append(value)

            # Calculate statistics
            stats = {
                "count": len(cohort_runs),
                "metrics": {}
            }

            for metric_name, values in metrics_summary.items():
                stats["metrics"][metric_name] = {
                    "mean": float(np.mean(values)),
                    "std": float(np.std(values)),
                    "min": float(np.min(values)),
                    "max": float(np.max(values))
                }

            cohort_stats[cohort_name] = stats

        return {
            "cohorts": cohort_stats,
            "total_runs": len(runs),
            "num_cohorts": len(cohorts)
        }
