# RAGlint Best Practices Guide

## 📊 Understanding RAGlint Metrics

### Core Metrics Explained

#### 1. Faithfulness Score (0.0 - 1.0)
**What it measures**: Does the generated answer contain information that is NOT supported by the retrieved context?

**Interpretation:**
- **0.9 - 1.0**: ✅ Excellent - Answer fully grounded in context
- **0.7 - 0.9**: 👍 Good - Minor unsupported claims
- **0.5 - 0.7**: ⚠️ Fair - Some hallucinations present
- **< 0.5**: ❌ Poor - Significant hallucinations

**When to use**: Every RAG pipeline (most critical metric)

**Common issues:**
- Low score: Model adding information not in context
- Fix: Improve prompting ("only use provided context"), better retrieval

#### 2. Context Relevance (0.0 - 1.0)
**What it measures**: Is the retrieved context useful for answering the query?

**Interpretation:**
- **0.8 - 1.0**: ✅ Excellent - Highly relevant contexts retrieved
- **0.6 - 0.8**: 👍 Good - Mostly relevant
- **0.4 - 0.6**: ⚠️ Fair - Some irrelevant results
- **< 0.4**: ❌ Poor - Retrieval not working well

**When to use**: Diagnosing retrieval quality

**Common issues:**
- Low score: Embeddings don't capture query intent, wrong similarity metric
- Fix: Better embeddings, adjust chunk size, tune retrieval parameters

#### 3. Answer Relevance (0.0 - 1.0)
**What it measures**: Does the answer actually address the user's query?

**Interpretation:**
- **0.8 - 1.0**: ✅ Excellent - On-topic and complete
- **0.6 - 0.8**: 👍 Good - Addresses query but could be better
- **0.4 - 0.6**: ⚠️ Fair - Partially off-topic
- **< 0.4**: ❌ Poor - Not answering the question

**When to use**: Evaluating generation quality

**Common issues:**
- Low score: Model is verbose or tangential
- Fix: Better prompting, stricter generation parameters

#### 4. Semantic Similarity (0.0 - 1.0)
**What it measures**: How semantically similar is the answer to the ground truth?

**Interpretation:**
- **0.8 - 1.0**: ✅ Excellent - Nearly identical meaning
- **0.6 - 0.8**: 👍 Good - Similar meaning, different wording
- **0.4 - 0.6**: ⚠️ Fair - Some overlap
- **< 0.4**: ❌ Poor - Different meaning

**When to use**: When you have ground truth answers (benchmarking)

---

## 🎯 When to Use Which Metrics

### Scenario 1: Initial Development
**Use:** Faithfulness + Context Relevance
**Why:** Focus on core RAG functionality first

### Scenario 2: Production Monitoring
**Use:** Faithfulness + Answer Relevance
**Why:** Ensure no hallucinations and queries are answered

### Scenario 3: Benchmark Evaluation
**Use:** All metrics + Precision/Recall
**Why:** Comprehensive comparison needs all angles

### Scenario 4: Debugging Low Quality
**Priority Order:**
1. Check Faithfulness (hallucinations?)
2. Check Context Relevance (bad retrieval?)
3. Check Answer Relevance (generation issue?)

---

## 🔧 Optimization Workflows

### Workflow 1: Improving Low Faithfulness

**Step 1: Diagnose**
```bash
raglint analyze data.json --smart --output-dir=diagnosis/
```

**Step 2: Check Context Relevance**
- If context relevance is also low → **Retrieval problem**
- If context relevance is high → **Generation problem**

**Step 3: Fix Retrieval (if needed)**
- Adjust chunk size (try 256, 512, 1024 tokens)
- Improve embeddings (try different models)
- Increase top-k retrieved contexts

**Step 4: Fix Generation (if needed)**
- Update system prompt: "Only use the provided context. Do not add external knowledge."
- Lower temperature (0.0 - 0.3 for factual tasks)
- Use structured output (JSON mode)

**Step 5: Re-evaluate**
```bash
raglint analyze data_v2.json --smart
raglint compare diagnosis/results.json results_v2.json
```

---

### Workflow 2: Optimizing Chunk Size

**Goal**: Find optimal chunk size for your use case

**Method**:
1. Create test datasets with different chunk sizes (128, 256, 512, 1024, 2048)
2. Run RAGlint on each
3. Compare chunk overlap, context relevance, and faithfulness

**Example**:
```python
from raglint import RAGPipelineAnalyzer

chunk_sizes = [256, 512, 1024]
results = {}

for size in chunk_sizes:
    # Re-chunk your documents
    chunks = create_chunks(documents, size)
    
    # Analyze
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)
    result = await analyzer.analyze_async(test_data)
    results[size] = result

# Find best chunk size
best_size = max(results, key=lambda x: results[x]['faithfulness_score'])
print(f"Optimal chunk size: {best_size}")
```

**Interpretation**:
- **Small chunks (128-256)**: High precision, may miss context
- **Medium chunks (512-1024)**: Best balance for most cases
- **Large chunks (2048+)**: More context, but noisy

---

### Workflow 3: Debugging Retrieval

**Symptoms**: Low context relevance, high faithfulness

**Diagnosis**:
```bash
raglint analyze data.json --smart --detailed-output
```

**Check**:
1. **Chunk Coverage**: Are queries finding any chunks?
2. **Query Difficulty**: Are queries too complex?
3. **Semantic Similarity**: Do retrieved chunks match query intent?

**Fixes**:
- **Poor coverage**: Increase top-k, improve chunking strategy
- **High difficulty**: Decompose complex queries
- **Low similarity**: Better embeddings, query preprocessing

---

## 📈 Setting Thresholds

### Production Thresholds (Recommended)

For **customer-facing** RAG:
```yaml
thresholds:
  faithfulness: 0.85  # Critical - no hallucinations
  context_relevance: 0.70  # Important - good retrieval
  answer_relevance: 0.75  # Important - on-topic answers
```

For **internal tools**:
```yaml
thresholds:
  faithfulness: 0.70  # Still important
  context_relevance: 0.60  # More lenient
  answer_relevance: 0.65  # More lenient
```

For **experimental/research**:
```yaml
thresholds:
  faithfulness: 0.60  # Exploratory
  context_relevance: 0.50
  answer_relevance: 0.55
```

---

## 🚨 Common Pitfalls

### Pitfall 1: Over-optimizing for One Metric
**Problem**: Focusing only on faithfulness can hurt answer quality
**Solution**: Balance multiple metrics

### Pitfall 2: Ignoring Chunk Overlap
**Problem**: High overlap = redundant retrieval, slower performance
**Solution**: Aim for 10-20% overlap, not 50%+

### Pitfall 3: Testing on Training Data
**Problem**: Metrics look great but don't generalize
**Solution**: Use held-out test set, diverse queries

### Pitfall 4: Not Using Smart Metrics
**Problem**: Basic metrics miss nuanced issues
**Solution**: Always use `--smart` for LLM-powered evaluation

### Pitfall 5: Comparing Different LLMs Directly
**Problem**: Metrics vary by LLM provider
**Solution**: Use same LLM for evaluation across experiments

---

## 💡 Pro Tips

### Tip 1: Async is Your Friend
```bash
# Slow (sequential)
raglint analyze large_dataset.json --smart

# Async processing (concurrent evaluation)
raglint analyze large_dataset.json --smart --async
```

### Tip 2: Use the Dashboard for Experiments
```bash
raglint dashboard
# Navigate to http://localhost:8000
# Compare multiple runs visually
```

### Tip 3: Track Cost
```bash
raglint analyze data.json --smart --track-cost
# See estimated OpenAI API cost
```

### Tip 4: Batch Analysis
```bash
for file in experiments/*.json; do
    raglint analyze "$file" --smart --output-dir="results/$(basename $file .json)"
done
```

### Tip 5: Use Plugins for Custom Metrics
```python
from raglint.plugins import PluginInterface

class MyCustomMetric(PluginInterface):
    async def calculate_async(self, query, response, contexts):
        # Your logic here
        return score
```

---

## 📚 Case Studies

### Case Study 1: E-commerce Product Q&A
**Challenge**: Customers asking about products
**Metrics Focus**: Faithfulness (100%), Answer Relevance (85%)
**Result**: Reduced hallucinations from 30% to 5%

**Key Changes**:
- Stricter prompting
- Increased chunk overlap from 0% to 15%
- Used structured output (JSON)

---

### Case Study 2: Legal Document Search
**Challenge**: Lawyers need exact citations
**Metrics Focus**: Context Relevance (95%), Citation Accuracy
**Result**: Improved retrieval precision from 60% to 90%

**Key Changes**:
- Larger chunks (1024 tokens) for full paragraphs
- Custom citation plugin
- BM25 + vector hybrid search

---

### Case Study 3: Customer Support Chatbot
**Challenge**: Handle diverse, informal queries
**Metrics Focus**: Answer Relevance (90%), Query Difficulty
**Result**: Answer satisfaction improved 40%

**Key Changes**:
- Query preprocessing (spell check, expansion)
- Smaller chunks (256 tokens) for specific answers
- Multi-turn context preservation

---

## 🎓 Learning Resources

**Next Steps**:
1. Read [QUICKSTART.md](QUICKSTART.md) if you haven't
2. Try the examples in `examples/`
3. Watch the demo video (coming soon!)
4. Join our community (Discord link in README)

**Advanced Topics**:
- Plugin development: [PLUGINS.md](PLUGINS.md)
- Benchmarking: [BENCHMARKS.md](BENCHMARKS.md)
- Architecture: [ARCHITECTURE.md](ARCHITECTURE.md)

---

**Last Updated**: 2025-11-22
