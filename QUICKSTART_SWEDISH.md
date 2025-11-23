# 🚀 RAGLint Snabbstart

## Installation

```bash
cd /home/yesir/Dokument/RAGlint

# Aktivera virtual environment
source .venv/bin/activate

# Verifiera installation
python -c "import raglint; print('RAGLint är installerat!')"
```

## 1. Grundläggande CLI Användning

### Exempel 1: Analysera med Mock LLM (Snabbast)

```bash
# Skapa test data
cat > test_data.json << 'EOF'
[
  {
    "query": "Vad är machine learning?",
    "retrieved_contexts": [
      "Machine learning är en gren av AI där datorer lär sig från data.",
      "ML-algoritmer kan förbättra sin prestanda över tid."
    ],
    "response": "Machine learning är en del av artificiell intelligens där system lär sig från data utan att vara explicit programmerade.",
    "ground_truth": "Machine learning är en AI-teknik."
  }
]
EOF

# Analysera med mock LLM (inget API key behövs)
raglint analyze test_data.json --provider mock

# Resultat sparas i ./raglint_results/
ls -la raglint_results/
```

### Exempel 2: Med Smart Metrics

```bash
# Använd LLM-baserade metrics för djupare analys
raglint analyze test_data.json --provider mock --smart

# Se rapporten
cat raglint_results/latest_report.txt
```

### Exempel 3: Med Ollama (Local LLM)

```bash
# Starta Ollama först (i annat terminal)
ollama serve

# Använd Ollama modell
raglint analyze test_data.json --provider ollama --model llama2

# Eller med annan modell
raglint analyze test_data.json --provider ollama --model mistral
```

## 2. Dashboard (Web UI)

### Starta Dashboard

```bash
# Starta dashboard på port 8000
raglint dashboard

# Eller på annan port
raglint dashboard --port 8080
```

**Öppna:** http://localhost:8000

### Dashboard Features

- 📊 **Analytics**: Se drift detection, cohort analysis
- 🔍 **Runs**: Bläddra genom alla analyser
- 🎯 **Playground**: Testa RAG queries interaktivt
- 📦 **Datasets**: Hantera test datasets
- 🔌 **Plugins**: Bläddra marketplace

## 3. Plugin System

### Lista Tillgängliga Plugins

```bash
raglint plugins list
```

### Installera Plugin

```bash
# Installera ett plugin från marketplace
raglint plugins install raglint-pii-advanced

# Installera specifik version
raglint plugins install raglint-citation-checker --version 1.2.0
```

### Se Installerade Plugins

```bash
ls ~/.raglint/plugins/
```

## 4. Python API

### Exempel: Basic Analysis

```python
from raglint.core import RAGPipelineAnalyzer

# Skapa analyzer
analyzer = RAGPipelineAnalyzer(use_smart_metrics=False)

# Din RAG data
data = [
    {
        "query": "Vad är Python?",
        "retrieved_contexts": [
            "Python är ett programmeringsspråk.",
            "Python används för AI och data science."
        ],
        "response": "Python är ett populärt programmeringsspråk för AI.",
        "ground_truth": "Python är ett programmeringsspråk."
    }
]

# Analysera
results = analyzer.analyze(data)

# Se resultat
print(f"Faithfulness: {results.faithfulness_scores[0]:.2f}")
print(f"Semantic Score: {results.semantic_scores[0]:.2f}")
print(f"Retrieval Precision: {results.retrieval_stats['precision']:.2f}")
```

### Exempel: Med LangChain

```python
from raglint.integrations.langchain import RAGLintCallback
from langchain.chains import RetrievalQA

# Skapa callback
callback = RAGLintCallback()

# Använd i din chain
qa_chain = RetrievalQA(..., callbacks=[callback])

# Kör queries - automatiskt tracked!
qa_chain.run("Din query här")

# Se resultat i dashboard
```

## 5. Köra Tester

### Alla Tester

```bash
# Kör alla tester
pytest

# Med coverage rapport
pytest --cov=raglint --cov-report=html

# Öppna coverage rapport
firefox htmlcov/index.html
```

### Specifika Test-Suiter

```bash
# Core functionality
pytest tests/core/

# LLM providers
pytest tests/llm/

# Plugins
pytest tests/plugins/

# Dashboard
pytest tests/dashboard/

# Metrics
pytest tests/test_relevance.py tests/metrics/
```

### Snabba Tester (Inga LLM-anrop)

```bash
# Endast unit tests, skippa integration tests
pytest -m "not integration" -v
```

## 6. Avancerade Exempel

### A/B Testing

```python
from raglint.core import RAGPipelineAnalyzer

# Config A
analyzer_a = RAGPipelineAnalyzer(
    provider="ollama",
    model="llama2"
)

# Config B
analyzer_b = RAGPipelineAnalyzer(
    provider="ollama",
    model="mistral"
)

# Analyzera samma data med båda
results_a = analyzer_a.analyze(test_data)
results_b = analyzer_b.analyze(test_data)

# Jämför i dashboard
```

### Custom Plugins

```python
from raglint.plugins.interface import PluginInterface

class MyCustomPlugin(PluginInterface):
    name = "my_custom_metric"
    version = "1.0.0"
    description = "Min egen metric"
    
    def evaluate(self, query, context, response):
        # Din logik här
        score = len(response) / 100  # Simplistic example
        return min(score, 1.0)

# Registrera plugin
from raglint.plugins.loader import PluginLoader
loader = PluginLoader.get_instance()
loader.register_plugin(MyCustomPlugin())
```

## 7. Felsökning

### Problem: Import Error

```bash
# Verifiera installation
pip list | grep raglint

# Om saknas, installera i development mode
pip install -e .
```

### Problem: Ollama Connection Error

```bash
# Kontrollera att Ollama kör
curl http://localhost:11434/api/tags

# Starta Ollama om inte kör
ollama serve
```

### Problem: Dashboard Startar Inte

```bash
# Kontrollera port är ledig
lsof -i :8000

# Använd annan port
raglint dashboard --port 8080
```

### Debug Mode

```bash
# Kör med verbose logging
raglint analyze test_data.json --provider mock --verbose

# Eller i Python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 8. Exempel Output

### CLI Analysis Output

```
📊 RAGLint Analysis Results
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Queries Analyzed: 10
Provider: ollama (llama2)

Metrics:
  Faithfulness:    0.87 ± 0.12
  Relevance:       0.82 ± 0.09
  Precision:       0.78
  Recall:          0.85
  
Plugin Results:
  ✅ PII Detector:        No issues found
  ✅ Citation Accuracy:   92% verified
  ⚠️  Bias Detection:     2 potential biases
  
Report saved to: ./raglint_results/run_2024-01-15_14-23-45/
```

## 9. Nästa Steg

1. **Utforska Dashboard**: Se dina analyser visuellt
2. **Testa Plugins**: Installera och testa olika plugins
3. **Integrera**: Lägg till RAGLint i din RAG pipeline
4. **Bidra**: Skapa egna plugins eller förbättra koden

## 10. Hjälp & Support

```bash
# CLI help
raglint --help
raglint analyze --help
raglint dashboard --help
raglint plugins --help

# Python help
python -c "from raglint.core import RAGPipelineAnalyzer; help(RAGPipelineAnalyzer)"
```

## Snabba Kommandon Cheat Sheet

```bash
# Installation check
source .venv/bin/activate && python -c "import raglint"

# Quick analysis
echo '[{"query":"test","retrieved_contexts":["ctx"],"response":"ans"}]' | raglint analyze -

# Start dashboard
raglint dashboard &

# Run tests
pytest -v

# Coverage check
pytest --cov=raglint --cov-report=term | grep TOTAL
```

**Lycka till med RAGLint!** 🚀
