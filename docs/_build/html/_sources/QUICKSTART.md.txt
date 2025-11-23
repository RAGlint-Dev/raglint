# Quick Start Guide

Get up and running with RAGLint in 5 minutes! ⚡

## Installation

```bash
pip install raglint
```

## Your First Analysis in 30 Seconds

### 1. Create Sample Data

```bash
cat > my_rag_data.json << 'EOF'
[
  {
    "query": "What is machine learning?",
    "retrieved_contexts": [
      "Machine learning is a subset of AI that enables systems to learn from data.",
      "It uses algorithms to find patterns and make predictions."
    ],
    "ground_truth_contexts": [
      "Machine learning is a branch of AI focused on learning from data."
    ],
    "response": "Machine learning is a subset of artificial intelligence that allows systems to learn and improve from experience without being explicitly programmed."
  }
]
EOF
```

### 2. Run Basic Analysis

```bash
raglint analyze my_rag_data.json
```

**Output:**
```
📊 Basic Metrics:
   • Chunk Size Mean: 65.50
   • Retrieval Precision: 0.50
   • Retrieval Recall: 1.00
   
✅ Report saved to raglint_report.html
```

### 3. Open the Report

```bash
open raglint_report.html  # macOS
xdg-open raglint_report.html  # Linux
start raglint_report.html  # Windows
```

**That's it!** You've just analyzed your first RAG pipeline! 🎉

---

## Enable Smart Metrics (LLM-based)

### With Mock Mode (for Testing)

```bash
# No API key needed!
raglint analyze my_rag_data.json --smart
```

### With OpenAI

```bash
# Set API key
export OPENAI_API_KEY="sk-..."

# Run analysis
raglint analyze my_rag_data.json --smart
```

**Output:**
```
🧠 Smart Metrics:
   • Semantic Similarity: 0.87
   • Faithfulness Score: 1.00
```

---

## Python Library Usage

```python
from raglint import RAGPipelineAnalyzer

# Your RAG data
data = [{
    "query": "What is RAG?",
    "retrieved_contexts": ["RAG combines retrieval and generation."],
    "response": "RAG is a technique that combines retrieval with generation."
}]

# Analyze
analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)
results = analyzer.analyze(data)

# View results
print(f"Faithfulness: {results.faithfulness_scores[0]:.2f}")
```

---

## Common Use Cases

### Use Case 1: CI/CD Quality Gate

```yaml
# .github/workflows/rag-quality.yml
name: RAG Quality Check

on: [push]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install RAGLint
        run: pip install raglint
      - name: Analyze RAG Quality
        run: raglint analyze test_data.json --smart
```

### Use Case 2: Compare A/B Tests

```bash
# Test two different chunking strategies
raglint compare baseline.json experimental.json
```

**Output:**
```
--- Comparison Report ---
Precision: 0.75 -> 0.85 (+0.10) ✅
Recall:    0.80 -> 0.82 (+0.02) ✅
```

### Use Case 3: Batch Processing

```python
import glob
from raglint import RAGPipelineAnalyzer
from raglint.reporting import generate_html_report

analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)

for file in glob.glob("data/*.json"):
    with open(file) as f:
        data = json.load(f)
    
    results = analyzer.analyze(data)
    generate_html_report(results, f"reports/{file}.html")
```

---

## Configuration

Create `raglint.yml` in your project:

```yaml
# LLM Provider
provider: openai  # or 'ollama', 'mock'
model_name: gpt-4

# Optional: API Key (or use env var)
openai_api_key: "sk-..."

# Metrics to run
metrics:
  chunking: true
  retrieval: true
  semantic: true
  faithfulness: true

# Quality thresholds
thresholds:
  faithfulness: 0.7
  relevance: 0.7
```

Then just run:
```bash
raglint analyze data.json --smart
```

---

## Performance Tips

### 🚀 Async Processing (Automatic!)

RAGLint automatically uses async for better performance:

```python
# Small dataset (≤5 items): Uses sync
results = analyzer.analyze(small_data)

# Large dataset (>5 items): Uses async for concurrent processing!
results = analyzer.analyze(large_data)
```

### 📊 Progress Bars

```python
# See progress for long analyses
results = analyzer.analyze(data, show_progress=True)
```

Output:
```
Analyzing: 100%|███████████| 100/100 [00:05<00:00, 18.23 items/s]
```

---

## What's in the Report?

The HTML report includes:

✅ **Summary Cards** - Key metrics at a glance  
✅ **Interactive Charts** - Visual score distributions  
✅ **Detailed Table** - Per-query breakdown  
✅ **Exportable Data** - Download results as CSV  

---

## Next Steps

### Learn More
- **API Reference**: [docs/API.md](../docs/API.md)
- **Contributing**: [CONTRIBUTING.md](../CONTRIBUTING.md)
- **Troubleshooting**: [docs/TROUBLESHOOTING.md](../docs/TROUBLESHOOTING.md)

### Examples
```bash
cd examples/
python basic_usage.py
python performance_demo.py
```

### Advanced Features
- Custom prompts for evaluation
- Multiple LLM providers
- Batch processing
- CI/CD integration

---

## Need Help?

- 📖 [Full Documentation](../docs/API.md)
- 🐛 [Report Issues](https://github.com/yourusername/raglint/issues)
- 💬 [Discussions](https://github.com/yourusername/raglint/discussions)

**Happy analyzing!** 🎉
