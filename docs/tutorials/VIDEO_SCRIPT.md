# RAGlint Video Tutorial Script (10 minutes)

## Introduction (1 minute)

**[SCREEN: RAGlint logo/README]**

**Narrator**:
"Hi, I'm going to show you RAGlint - a comprehensive, security-focused RAG evaluation platform. If you're building retrieval-augmented generation systems and need professional qual quality assessment with 15 built-in plugins, this is for you."

**[SCREEN: Show problem - hallucinated responses]**

"The challenge with RAG systems: they can hallucinate, retrieve irrelevant context, or give off-topic answers. RAGlint helps you catch these issues before they reach production."

---

## Installation & Setup (2 minutes)

**[SCREEN: Terminal]**

"Let's get started. Installation is simple:"

```bash
pip install raglint
```

"That's it! RAGlint works with mock LLMs for testing, or real LLMs for production evaluation."

**[SCREEN: Show raglint.yml file]**

"Optional: create a config file for custom settings:"

```bash
raglint init
```

"This creates `raglint.yml` where you can set your LLM provider, thresholds, and which metrics to use."

---

## First Analysis (3 minutes)

**[SCREEN: Show sample_data.json]**

"RAGlint expects JSON data with this format:"

```json
[
  {
    "query": "What's the return policy?",
    "retrieved_contexts": ["30-day money-back..."],
    "response": "You can return items within 30 days...",
    "ground_truth": "30-day money-back"
  }
]
```

**[SCREEN: Terminal]**

"Run your first analysis:"

```bash
raglint analyze examples/sample_data.json --smart
```

"The `--smart` flag uses LLM-powered metrics for deeper evaluation."

**[SCREEN: Show output - metrics displayed]**

"RAGlint shows you:"
- Faithfulness: 0.92 (no hallucinations!)
- Context Relevance: 0.88 (good retrieval)
- Answer Relevance: 0.90 (on-topic)
- Semantic Similarity: 0.85

**[SCREEN: Show HTML report]**

"And generates a beautiful HTML report:"

```bash
open raglint_report.html
```

"This includes visualizations, detailed metrics, and recommendations."

---

## Dashboard Tour (2 minutes)

**[SCREEN: Terminal]**

"For ongoing work, use the web dashboard:"

```bash
raglint dashboard
```

**[SCREEN: Browser - localhost:8000]**

"Visit localhost:8000, create an account, and you're in!"

**[SHOW:
- Homepage with recent analyses
- Click "New Analysis" button
- Upload JSON file or paste data
- Click "Analyze" - show progress
- Results page with charts]**

"The dashboard tracks all your experiments, lets you compare runs, and export results."

**[SHOW: Playground tab]**

"There's even a playground for quick tests - paste a query and response, get instant metrics."

---

## Advanced Features (2 minutes)

**[SCREEN: Code editor - Python]**

"RAGlint integrates with your code:"

```python
from raglint import RAGPipelineAnalyzer

analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)
results = await analyzer.analyze_async(test_data)

if results['faithfulness_score'] < 0.85:
    print("⚠️ Hallucination detected!")
```

**[SCREEN: Show plugin system]**

"It's also extensible. We have 8 built-in plugins:"
- Citation accuracy (for legal/research)
- Readability scoring
- Bias detection (for fairness)
- Answer completeness
- Response conciseness

"And you can build your own!"

**[SCREEN: Show config file]**

"Set production thresholds:"

```yaml
thresholds:
  faithfulness: 0.85  # Alert if lower
  context_relevance: 0.70
```

**[SCREEN: Show monitoring code]**

"In production, monitor quality:"

```python
if faithfulness < 0.85:
    send_alert("Possible hallucination")
    escalate_to_human()
```

---

## Wrap-up (30 seconds)

**[SCREEN: RAGlint features summary]**

"To recap, RAGlint gives you:"
- ✅ Async evaluation support for concurrent processing
- ✅ Local-first (your data stays private)
- ✅ 8 built-in plugins + extensible
- ✅ Beautiful dashboard
- ✅ Production-ready monitoring

**[SCREEN: Links]**

"Get started:"
- Docs: raglint.readthedocs.io
- GitHub: github.com/raglint/raglint
- Examples: Check the docs for e-commerce, support, legal use cases

"Thanks for watching! If RAGlint helps your project, star us on GitHub!"

**[END]**

---

## Video Production Notes

### Visuals Needed
1. Clean terminal font (14-16pt, dark theme)
2. Browser at 1280x720 (for recording)
3. Code editor with syntax highlighting
4. Smooth transitions between scenes

### Timing
- Keep pace brisk but clear
- Pause 1-2 seconds after showing each command output
- Use zooms for important parts (metrics, charts)

### Audio
- Clear, enthusiastic tone
- Emphasize key benefits ("15 plugins", "security-scanned", "privacy-first")
- Slow down for technical commands

### Follow-up Videos
- **Part 2**: Deep dive into plugins
- **Part 3**: Production deployment
- **Part 4**: Custom plugin development
- **Part 5**: Optimization strategies

---

## Script Variations

### 5-Minute Version
Skip sections: 
- Detailed JSON format
- Dashboard (mention briefly)
- Python integration

### Social Media (60 seconds)
Hook: "RAG systems hallucinate. Here's how to catch it."
- 15s: Problem
- 30s: Demo (install → analyze → results)
- 15s: CTA

### Conference Talk (20 minutes)
Add:
- Competitor comparison
- Benchmark results
- Architecture deep-dive
- Live coding session
- Q&A

---

**Total Duration**: ~10 minutes  
**Target Audience**: ML engineers, LLM developers, RAG practitioners  
**Skill Level**: Intermediate (familiar with RAG concepts)
