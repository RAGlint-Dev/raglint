# 🔍 RAGLint

**The Honest RAG Evaluation Platform**

[![PyPI version](https://badge.fury.io/py/raglint.svg)](https://badge.fury.io/py/raglint)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code Coverage](https://img.shields.io/badge/coverage-27%25-yellow.svg)](https://github.com/yourusername/raglint)

RAGLint is the **all-in-one evaluation platform** for Retrieval-Augmented Generation (RAG) systems. Built with production in mind, it provides comprehensive metrics, a beautiful dashboard, and enterprise-grade security.

## ✨ Why RAGLint?

| Feature | RAGLint |
|---------|---------|
| **Plugin Marketplace** | ✅ Unique |
| **Local LLM (Ollama)** | ✅ Native |
| **Dashboard** | ✅ Excellent |
| **Real-time Analytics** | ✅ WebSockets |
| **Security** | ✅ High |
| **CI/CD Integration** | ✅ Native Action |
| **Open Source** | ✅ MIT |

## 🚀 Quick Start

```bash
# Install
pip install raglint

# Analyze your RAG pipeline
raglint analyze data.json --smart --provider ollama

# Launch dashboard
raglint dashboard
```

## 📊 Features

### Core Metrics
- **Faithfulness**: Verify answers match source documents
- **Relevance**: Context & answer relevance scoring
- **Precision/Recall**: Retrieval quality metrics
- **Bias Detection**: Identify biased responses
- **Toxicity**: Safety & appropriateness checks
- **PII Detection**: Security & privacy compliance

### Advanced Analytics
- **Drift Detection**: Monitor metric changes over time
- **Cohort Analysis**: Compare configurations
- **Embedding Visualization**: UMAP projections
- **Real-time Updates**: WebSocket-powered dashboard

### Integrations
- ✅ OpenAI, Azure OpenAI, AWS Bedrock
- ✅ Ollama (local LLM)
- ✅ LangChain, LlamaIndex, Haystack
- ✅ Pinecone, Weaviate, Chroma, Qdrant

## 💡 Example

```python
from raglint.core import RAGPipelineAnalyzer

# Your RAG data
data = [
    {
        "query": "What is machine learning?",
        "retrieved_contexts": ["ML is a subset of AI..."],
        "response": "Machine learning is..."
    }
]

# Analyze
analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)
results = analyzer.analyze(data)

print(f"Faithfulness: {results.faithfulness_scores[0]:.2f}")
print(f"Relevance: {results.semantic_scores[0]:.2f}")
```

## 🔌 Plugin Marketplace

Extend RAGLint with custom metrics:

```bash
# Browse plugins
raglint plugins list

# Install a plugin
raglint plugins install raglint-pii-advanced

# Create your own
raglint plugins create my-custom-metric
```

**Built-in Plugins:**
- Citation Accuracy Checker
- PII Detector
- SQL Injection Detector
- Bias Detector
- Hallucination Confidence

## 🎯 CI/CD Integration

```yaml
# .github/workflows/raglint.yml
- name: RAGLint Analysis
  uses: yourusername/raglint-action@v1
  with:
    data-file: 'eval_data.json'
    threshold: 0.7
```

## 📈 Dashboard

Beautiful, real-time analytics dashboard:

- 📊 Interactive charts & visualizations
- 🔍 Drill-down into individual runs
- 📉 Drift detection & alerting
- 🎨 Dark mode & modern UI
- 🚀 WebSocket real-time updates

```bash
raglint dashboard
# Open http://localhost:8000
```

## 🔐 Enterprise-Ready

- **Security**: RestrictedPython sandbox, code signing
- **Scalability**: PostgreSQL support, async processing
- **Privacy**: Self-hosted, local LLM support
- **Compliance**: PII detection, audit logs

## 📚 Documentation

- [Quick Start Guide](docs/QUICKSTART.md)
- [API Reference](docs/API.md)
- [Cookbooks](docs/cookbooks/)
  - [Pinecone Integration](docs/cookbooks/pinecone_integration.md)
  - [LlamaIndex Advanced](docs/cookbooks/llamaindex_advanced.md)
  - [Haystack Integration](docs/cookbooks/haystack_advanced.md)

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## ⭐ Star Us!

If you find RAGLint useful, please consider starring the repo to help others discover it!

---

**Made with ❤️ by the RAGLint team** | [Website](https://raglint.io) | [Discord](https://discord.gg/raglint) | [Twitter](https://twitter.com/raglint)
