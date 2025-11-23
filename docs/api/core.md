# Core API

Core analysis classes and result models.

## RAGPipelineAnalyzer

```{eval-rst}
.. autoclass:: raglint.core.RAGPipelineAnalyzer
   :members:
   :undoc-members:
   :show-inheritance:
```

## AnalysisResult

```{eval-rst}
.. autoclass:: raglint.core.AnalysisResult
   :members:
   :undoc-members:
   :show-inheritance:
```

## Example

```python
from raglint import RAGPipelineAnalyzer

analyzer = RAGPipelineAnalyzer(
    use_smart_metrics=True,
    enable_plugins=True
)

results = analyzer.analyze(data, show_progress=True)

# Access results
print(results.chunk_stats)
print(results.retrieval_stats)
print(results.detailed_results)
```
