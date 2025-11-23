# Tracking API

Cost and latency tracking.

## PerformanceTracker

```{eval-rst}
.. autoclass:: raglint.tracking.PerformanceTracker
   :members:
   :undoc-members:
   :show-inheritance:
```

## Helper Functions

```{eval-rst}
.. autofunction:: raglint.tracking.get_tracker
.. autofunction:: raglint.tracking.reset_tracker
```

## Example

```python
from raglint import RAGPipelineAnalyzer
from raglint.tracking import get_tracker, reset_tracker

# Reset tracker
reset_tracker()

# Run analysis
analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)
results = analyzer.analyze(data)

# Get stats
tracker = get_tracker()
stats = tracker.get_summary()

print(f"Cost: ${stats['cost']['total_cost_usd']:.4f}")
print(f"Latency: {stats['latency']['avg_latency_ms']:.2f}ms")

# Estimate costs
estimate = tracker.estimate_cost(1000, "gpt-3.5-turbo")
print(f"Est. 1000 queries: ${estimate['estimated_cost_usd']:.2f}")
```
