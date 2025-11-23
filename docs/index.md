# RAGLint Documentation

::::{grid} 1 1 2 2
:gutter: 3

:::{grid-item-card} 🚀 Quick Start
:link: quickstart
:link-type: doc

Get started with RAGLint in 5 minutes. Install, configure, and run your first evaluation.
:::

:::{grid-item-card} 📚 API Reference
:link: api/index
:link-type: doc

Complete API documentation for all RAGLint modules, classes, and functions.
:::

:::{grid-item-card} 📖 Guides
:link: guides/index
:link-type: doc

In-depth tutorials and examples for advanced use cases and integrations.
:::

:::{grid-item-card} 💡 GitHub
:link: https://github.com/raglint/raglint

View source code, report issues, and contribute to the project.
:::

::::

---

## What is RAGLint?

**RAGLint** is a comprehensive evaluation framework for Retrieval-Augmented Generation (RAG) systems. It provides production-ready tools to measure, monitor, and improve your RAG pipelines.

::::{grid} 1 1 2 3
:gutter: 2

:::{grid-item-card} 📊 Smart Metrics
:class-header: bg-light

Faithfulness, semantic similarity, context precision/recall, and more.
:::

:::{grid-item-card} 🔌 Plugin System
:class-header: bg-light

Extensible architecture for custom metrics and evaluators.
:::

:::{grid-item-card} 🎨 Dashboard
:class-header: bg-light

Beautiful web UI for visualizing results and debugging queries.
:::

:::{grid-item-card} ⚡ CLI & Python API
:class-header: bg-light

Use from command line or integrate directly into your code.
:::

:::{grid-item-card} 💰 Cost Tracking
:class-header: bg-light

Monitor LLM costs and latency across different providers.
:::

:::{grid-item-card} 🎯 Benchmarks
:class-header: bg-light

Test against SQUAD and other standard datasets.
:::

::::

---

## Installation

```bash
pip install raglint
```

## Quick Example

```python
from raglint import RAGPipelineAnalyzer
from raglint.config import Config

# Initialize analyzer
config = Config.from_yaml("raglint.yaml")
analyzer = RAGPipelineAnalyzer(config)

# Run evaluation
results = await analyzer.analyze_batch([
    {
        "query": "What is RAG?",
        "response": "RAG stands for Retrieval-Augmented Generation...",
        "retrieved_contexts": ["Context 1", "Context 2"],
        "ground_truth_contexts": ["Ground truth context"]
    }
])

# View results
print(f"Faithfulness: {results[0]['faithfulness']:.2f}")
```

---

```{toctree}
:maxdepth: 2
:caption: Contents
:hidden:

quickstart
api/index
guides/index
```

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`
