# Quick Start

Get started with RAGLint in 5 minutes.

## Installation

```bash
pip install raglint
```

## Basic Usage

### 1. Prepare Your Data

```python
data = [
    {
        "query": "What is Python?",
        "retrieved_contexts": ["Python is a programming language."],
        "response": "Python is a high-level programming language.",
    }
]
```

### 2. Run Analysis

```python
from raglint import RAGPipelineAnalyzer

analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)
results = analyzer.analyze(data, show_progress=True)

print(f"Faithfulness: {results.chunk_stats['avg_faithfulness']:.2f}")
print(f"Semantic: {results.chunk_stats['avg_semantic_score']:.2f}")
```

### 3. View in Dashboard

```bash
raglint dashboard
```

Navigate to http://localhost:8000 to view results.

## What's Next?

- [API Reference](api/index.md) - Explore the full API
- [Configuration](guides/configuration.md) - Configure RAGLint
- [Plugins](guides/plugins.md) - Create custom metrics
- [Benchmarks](guides/benchmarks.md) - Run standard benchmarks
