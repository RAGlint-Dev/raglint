# 🚀 RAGlint Snabbstart - Kom Igång på 5 Minuter

## Snabbaste Vägen (Auto-Demo)

```bash
cd /home/yesir/Dokument/RAGlint
./demo.sh
```

Detta script kommer:
1. ✅ Skapa virtual environment
2. ✅ Installera alla dependencies
3. ✅ Köra tester
4. ✅ Starta web dashboard

**Öppna sedan:** http://localhost:8000

---

## Manuell Installation (Steg-för-Steg)

### 1. Setup Environment

```bash
# Skapa virtual environment
python3 -m venv venv
source venv/bin/activate

# Installera RAGlint
pip install -e .
```

### 2. Kör Tester

```bash
# Alla tester
pytest tests/ -v

# Snabba tester
pytest tests/ -v -k "not slow"

# Med coverage
pytest tests/ --cov=raglint --cov-report=html
# Öppna: htmlcov/index.html
```

### 3. CLI Användning

```bash
# Snabb analys
raglint analyze sample_data.json

# Med HTML rapport
raglint analyze sample_data.json --output report.html

# Med smart metrics (kräver OpenAI API key)
export OPENAI_API_KEY="sk-..."
raglint analyze sample_data.json --smart
```

### 4. Starta Dashboard

```bash
# Enkel start
python -m raglint.dashboard.app

# Med specifik port
uvicorn raglint.dashboard.app:app --port 8000 --reload
```

**Öppna:** http://localhost:8000

---

## 🎨 Dashboard Features

### Tillgängliga Sidor

1. **Home** - http://localhost:8000/
   - Översikt över system
   - Senaste analyser
   - Statistik

2. **Playground** - http://localhost:8000/playground
   - Testa plugins live
   - Experimentera med queries
   - Se resultat direkt

3. **Compare** - http://localhost:8000/compare
   - Jämför olika RAG-pipelines
   - A/B testing
   - Benchmarks

4. **Analytics** - http://localhost:8000/analytics
   - Detaljerad statistik
   - Trender över tid
   - Export data

---

## 💻 Python API Exempel

### Basic Usage

```python
from raglint import RAGPipelineAnalyzer

# Skapa analyzer
analyzer = RAGPipelineAnalyzer()

# Analysera data
data = {
    "query": "What is Python?",
    "retrieved_contexts": [
        "Python is a programming language.",
        "It was created by Guido van Rossum."
    ],
    "response": "Python is a high-level programming language."
}

results = analyzer.analyze(data)
print(f"Chunk coverage: {results.chunk_stats['coverage']}")
print(f"Retrieval precision: {results.retrieval_stats['precision']}")
```

### Med Smart Metrics (LLM-baserat)

```python
import os
os.environ['OPENAI_API_KEY'] = 'sk-...'

# Smart analyzer med LLM
analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)

results = analyzer.analyze(data)
print(f"Faithfulness: {results.faithfulness_scores[0]}")
print(f"Answer relevance: {results.semantic_scores[0]}")
```

### Async för Stora Dataset

```python
import asyncio

async def analyze_many():
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)
    
    dataset = [
        {"query": "...", "contexts": [...], "response": "..."},
        # ... 100+ items
    ]
    
    # Analyse concurrent
    results = await analyzer.analyze_async(dataset)
    return results

results = asyncio.run(analyze_many())
```

---

## 🔌 Plugin System

### Lista Tillgängliga Plugins

```python
from raglint.plugins.loader import PluginLoader

loader = PluginLoader.get_instance()
loader.load_plugins()

print("Available plugins:")
for name in loader.metric_plugins:
    plugin = loader.get_plugin(name)
    print(f"  • {name}: {plugin.description}")
```

### Använd Specifik Plugin

```python
from raglint.plugins.builtins import ReadabilityPlugin

plugin = ReadabilityPlugin()
result = await plugin.calculate_async(
    query="Any query",
    response="Your response text here",
    contexts=[]
)

print(f"Readability score: {result['flesch_reading_ease']}")
print(f"Grade level: {result['flesch_kincaid_grade']}")
```

---

## 🛠️ Troubleshooting

### Problem: `externally-managed-environment`

**Lösning:**
```bash
# Använd alltid virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Problem: `python: command not found`

**Lösning:**
```bash
# Använd python3 istället
python3 -m raglint.dashboard.app
```

### Problem: Port redan används

**Lösning:**
```bash
# Använd annan port
uvicorn raglint.dashboard.app:app --port 8080
```

### Problem: Tests failar

**Lösning:**
```bash
# Installera test dependencies
pip install -e .[dev]

# Kör bara fungerande tester
pytest tests/ -v --tb=short -x
```

---

## 📊 Exempel Output

### CLI Output
```
Analysis Results:
══════════════════════════════════════════
Chunk Statistics:
  Coverage: 0.85
  Size distribution: [512, 489, 501]
  Average size: 500.67 tokens

Retrieval Metrics:
  Precision: 0.90
  Recall: 0.85
  F1 Score: 0.87

✅ Report saved to: demo_report.html
```

### Dashboard Screenshot
![RAGlint Dashboard](dashboard_example.png)

---

## 🎯 Nästa Steg

1. **Testa Dashboard:**
   ```bash
   ./demo.sh
   # Öppna http://localhost:8000
   ```

2. **Kör Dina Data:**
   ```python
   analyzer = RAGPipelineAnalyzer()
   results = analyzer.analyze(your_data)
   ```

3. **Läs Docs:**
   - `docs/API.md` - API reference
   - `docs/BEST_PRACTICES.md` - Best practices
   - `docs/QUICKSTART.md` - Detailed guide

4. **Bygg Custom Plugins:**
   - See `examples/custom_plugin.py`
   - Read `docs/PLUGINS.md`

---

## 💡 Tips

- **Använd async** för stora dataset (>10 items)
- **Smart metrics** ger bättre quality scores (kräver API key)
- **Dashboard** är bäst för explorative analysis
- **CLI** är bäst för automation/CI/CD

**Lycka till! 🚀**
