# RAGLint Benchmarks

RAGLint provides standardized benchmark datasets for evaluating RAG systems.

## Available Benchmarks

- **SQUAD** - Stanford Question Answering Dataset
- **CoQA** - Conversational Question Answering (coming soon)
- **HotpotQA** - Multi-hop reasoning (coming soon)

## Quick Start

### CLI

```bash
# Run SQUAD benchmark (default 50 examples)
raglint benchmark --dataset squad

# Specify subset size
raglint benchmark --dataset squad --subset-size 100

# Save results
raglint benchmark --dataset squad --output results.json
```

### Python API

```python
from raglint.benchmarks import SQUADBenchmark
from raglint import RAGPipelineAnalyzer

# Load benchmark
benchmark = SQUADBenchmark(subset_size=50)
test_data = benchmark.load()

# Run evaluation
analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)
results = analyzer.analyze(test_data)

# View results
print(f"Average Faithfulness: {results.summary_metrics['avg_faithfulness']:.2f}")
```

## SQUAD Benchmark

The Stanford Question Answering Dataset (SQUAD) is a widely-used benchmark for question answering systems.

### Features

- **Question-Answer Pairs**: 100,000+ QA pairs
- **Contexts**: Wikipedia paragraphs
- **Ground Truth**: Exact answer spans

### Usage

```python
from raglint.benchmarks import SQUADBenchmark

# Load small subset for quick testing
benchmark = SQUADBenchmark(subset_size=10)
data = benchmark.load()

# Each item contains:
# - query: The question
# - retrieved_contexts: Context paragraphs
# - ground_truth_contexts: Ground truth answer
# - response: Generated answer (in this case, same as ground truth)
```

### Custom Subset Size

```python
# Quick test (5 examples)
quick_test = SQUADBenchmark(subset_size=5)

# Standard evaluation (50 examples)
standard = SQUADBenchmark(subset_size=50)

# Full evaluation (500 examples)
full = SQUADBenchmark(subset_size=500)
```

## Benchmark Registry

Use the registry to access benchmarks by name:

```python
from raglint.benchmarks import BenchmarkRegistry

# List available benchmarks
benchmarks = BenchmarkRegistry.list_benchmarks()
print(benchmarks)  # ['squad', 'coqa', 'hotpotqa']

# Load by name
data = BenchmarkRegistry.load("squad", subset_size=50)
```

## Comparing Results

### Baseline Scores

RAGLint provides baseline scores for comparison:

| Metric | SQUAD Baseline | Your Score | Δ |
|--------|----------------|------------|---|
| Faithfulness | 0.85 | ? | ? |
| Semantic Score | 0.80 | ? | ? |
| Context Relevance | 0.90 | ? | ? |

### Example Comparison

```python
from raglint.benchmarks import SQUADBenchmark
from raglint import RAGPipelineAnalyzer

benchmark = SQUADBenchmark(subset_size=50)
data = benchmark.load()

analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)
results = analyzer.analyze(data)

# Compare to baseline
baseline = {
    "avg_faithfulness": 0.85,
    "avg_semantic_score": 0.80,
}

for metric, baseline_value in baseline.items():
    current = results.summary_metrics[metric]
    diff = current - baseline_value
    status = "✅" if diff >= 0 else "❌"
    print(f"{status} {metric}: {current:.3f} (Δ {diff:+.3f})")
```

## Creating Custom Benchmarks

You can create custom benchmarks by implementing the benchmark interface:

```python
class CustomBenchmark:
    def __init__(self, subset_size: int = 50):
        self.subset_size = subset_size
    
    def load(self) -> List[Dict[str, Any]]:
        # Return list of test cases in RAGLint format
        return [
            {
                "query": "Question?",
                "retrieved_contexts": ["Context..."],
                "ground_truth_contexts": ["Ground truth..."],
                "response": "Answer..."
            }
        ]

# Use it
benchmark = CustomBenchmark(subset_size=10)
data = benchmark.load()
```

## Caching

Benchmarks are automatically cached in `~/.cache/raglint/benchmarks/` to avoid re-downloading.

Clear cache:
```bash
rm -rf ~/.cache/raglint/benchmarks/
```

## Full Example

See [examples/run_benchmark.py](../examples/run_benchmark.py) for a complete example.

```python
from raglint.benchmarks import SQUADBenchmark
from raglint import RAGPipelineAnalyzer

# Load benchmark
benchmark = SQUADBenchmark(subset_size=5)
test_data = benchmark.load()

# Run evaluation
analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)
results = analyzer.analyze(test_data, show_progress=True)

# Display results
print("BENCHMARK RESULTS")
print("="*60)
for metric, value in results.summary_metrics.items():
    if isinstance(value, float):
        print(f"{metric}: {value:.3f}")
```

## Production Use

For production use with full SQUAD dataset:

1. Download SQUAD manually:
   ```bash
   wget https://rajpurkar.github.io/SQuAD-explorer/dataset/dev-v2.0.json
   ```

2. Load in RAGLint:
   ```python
   import json
   from raglint import RAGPipelineAnalyzer
   
   # Load SQUAD
   with open("dev-v2.0.json") as f:
       squad_data = json.load(f)
   
   # Convert to RAGLint format
   raglint_data = convert_squad_to_raglint(squad_data)
   
   # Evaluate
   analyzer = RAGPipelineAnalyzer()
   results = analyzer.analyze(raglint_data)
   ```

## See Also

- [SQUAD Homepage](https://rajpurkar.github.io/SQuAD-explorer/)
- [RAGLint Documentation](../README.md)
