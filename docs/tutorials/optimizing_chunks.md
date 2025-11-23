# Optimizing RAG Chunking - Step-by-Step Tutorial

## Introduction

Chunk size is one of the most critical parameters in RAG systems. Too small, and you lose context. Too large, and you get noisy, irrelevant information. This tutorial shows you how to find the optimal chunk size for your use case using RAGlint.

## Prerequisites

- RAGlint installed (`pip install raglint`)
- Sample documents to test
- OpenAI API key (for smart metrics)

## Step 1: Prepare Test Data (15 minutes)

### Create Baseline Chunks

We'll test 4 different chunk sizes: 256, 512, 1024, and 2048 tokens.

```python
# chunk_optimizer.py
from pathlib import Path
import json

def chunk_text(text, chunk_size, overlap=0.1):
    """Simple chunking with overlap."""
    words = text.split()
    chunks = []
    step = int(chunk_size * (1 - overlap))
    
    for i in range(0, len(words), step):
        chunk = ' '.join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
   return chunks[:10]  # Limit for testing

# Load your document
with open("your_document.txt") as f:
    document = f.read()

# Create test datasets for each chunk size
chunk_sizes = [256, 512, 1024, 2048]

for size in chunk_sizes:
    chunks = chunk_text(document, size)
    
    # Create test queries (you provide these)
    test_data = [
        {
            "query": "What is the return policy?",
            "retrieved_contexts": chunks[:3],  # Top 3 chunks
            "response": "Generated response here...",  # From your RAG
            "ground_truth": "Expected answer..."
        },
        # Add more test queries
    ]
    
    # Save to file
    Path(f"chunks_{size}").mkdir(exist_ok=True)
    with open(f"chunks_{size}/test_data.json", "w") as f:
        json.dump(test_data, f, indent=2)
```

## Step 2: Run RAGlint on Each Configuration (10 minutes)

```bash
# Analyze each chunk size
for size in 256 512 1024 2048; do
    echo "Testing chunk size: $size"
    raglint analyze chunks_$size/test_data.json \
        --smart \
        --output-dir=results/chunks_$size
done
```

## Step 3: Compare Results (10 minutes)

### Manual Comparison

```bash
# Compare all results
raglint compare \
    results/chunks_256/results.json \
    results/chunks_512/results.json \
    results/chunks_1024/results.json \
    results/chunks_2048/results.json
```

### Python Analysis

```python
# analyze_chunks.py
import json
from pathlib import Path
import matplotlib.pyplot as plt

chunk_sizes = [256, 512, 1024, 2048]
results = {}

# Load all results
for size in chunk_sizes:
    with open(f"results/chunks_{size}/results.json") as f:
        results[size] = json.load(f)

# Extract metrics
faithfulness = [results[s]['faithfulness_score'] for s in chunk_sizes]
context_relevance = [results[s]['metrics']['context_relevance'] for s in chunk_sizes]
retrieval_time = [results[s]['metrics'].get('retrieval_time', 0) for s in chunk_sizes]

# Plot
fig, axes = plt.subplots(1, 3, figsize=(15, 4))

axes[0].plot(chunk_sizes, faithfulness, marker='o')
axes[0].set_title('Faithfulness vs Chunk Size')
axes[0].set_xlabel('Chunk Size (tokens)')
axes[0].set_ylabel('Faithfulness')
axes[0].grid(True)

axes[1].plot(chunk_sizes, context_relevance, marker='o')
axes[1].set_title('Context Relevance vs Chunk Size')
axes[1].set_xlabel('Chunk Size (tokens)')
axes[1].set_ylabel('Context Relevance')
axes[1].grid(True)

axes[2].plot(chunk_sizes, retrieval_time, marker='o')
axes[2].set_title('Retrieval Time vs Chunk Size')
axes[2].set_xlabel('Chunk Size (tokens)')
axes[2].set_ylabel('Time (seconds)')
axes[2].grid(True)

plt.tight_layout()
plt.savefig('chunk_optimization.png')
print("📊 Saved visualization to chunk_optimization.png")
```

## Step 4: Interpret Results

### Key Metrics to Watch

1. **Faithfulness**: Higher is better
   - If it decreases with larger chunks → too much noise
   - If it decreases with smaller chunks →missing context

2. **Context Relevance**: Balance is key
   - Too small: Precision high, but may miss information
   - Too large: More information, but less relevant

3. **Retrieval Time**: Smaller chunks = faster (usually)

### Decision Matrix

| Chunk Size | Faithfulness | Context Rel | Speed | Use Case |
|------------|--------------|-------------|-------|----------|
| 256 | Medium | High | Fast | FAQ, simple queries |
| 512 | **High** | **High** | **Fast** | **Most use cases** ✅ |
| 1024 | High | Medium | Medium | Complex technical docs |
| 2048 | Medium | Medium-Low | Slow | Legal documents, contracts |

## Step 5: Fine-Tune Your Winner (20 minutes)

Let's say 512 tokens performed best. Now optimize overlap:

```python
# Test overlaps: 0%, 10%, 20%, 30%
overlaps = [0.0, 0.1, 0.2, 0.3]

for overlap in overlaps:
    chunks = chunk_text(document, chunk_size=512, overlap=overlap)
    # ... create test_data and run RAGlint
```

**Typical finding**: 10-20% overlap is optimal for most cases.

## Step 6: Validate on Real Queries (30 minutes)

Don't just test on synthetic data!

```python
# real_world_test.py
import asyncio
from raglint import RAGPipelineAnalyzer

async def validate_production():
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)
    
    # Use real user queries from production logs
    real_queries = load_production_queries()  # Your function
    
    results = await analyzer.analyze_async(real_queries)
    
    print(f"Faithfulness: {results['faithfulness_score']}")
    print(f"Context Relevance: {results['metrics']['context_relevance']}")
    
    # Check if it meets your thresholds
    if results['faithfulness_score'] < 0.85:
        print("⚠️ WARNING: Faithfulness below threshold!")
        print("Consider increasing chunk size or improving retrieval")

asyncio.run(validate_production())
```

## Step 7: Deploy and Monitor

### Update Your RAG Pipeline

```python
# config.py
OPTIMAL_CHUNK_SIZE = 512  # From your testing
CHUNK_OVERLAP =  0.15      # 15% overlap
```

### Monitor in Production

```python
from raglint.tracking import get_tracker

async def generate_response(query, contexts):
    tracker = get_tracker()
    
    # Your RAG logic here
    response = your_rag_pipeline.generate(query, contexts)
    
    # Quick quality check
    if tracker.get_summary()['avg_faithfulness'] < 0.85:
        send_alert("RAG quality degrading - review chunks")
    
    return response
```

## Common Issues & Solutions

### Issue 1: All Chunk Sizes Perform Poorly
**Cause**: Problem isn't chunk size, it's retrieval or prompting  
**Solution**: 
- Improve embeddings (try `text-embedding-3-large`)
- Use hybrid search (BM25 + vector)
- Better system prompts

### Issue 2: Large Variation Across Queries
**Cause**: Different query types need different chunks  
**Solution**:
- Classify queries first
- Use dynamic chunking (small for simple, large for complex)

### Issue 3: Good Metrics But Poor User Feedback
**Cause**: Metrics don't perfectly align with user satisfaction  
**Solution**:
- Add custom plugins for your domain
- Collect user ratings and correlate with metrics
- A/B test in production

## Checklist

- [ ] Created test data for 4 chunk sizes
- [ ] Ran RAGlint on all configurations
- [ ] Compared results visually
- [ ] Selected optimal chunk size
- [ ] Fine-tuned overlap
- [ ] Validated on real queries
- [ ] Deployed to production
- [ ] Set up monitoring

## Next Steps

1. **Optimize other parameters**: top-k, temperature, retrieval method
2. **Try semantic chunking**: Chunk by topics, not just size
3. **A/B test**: Deploy both configs and compare real metrics

## Resources

- [RAGlint Best Practices](../BEST_PRACTICES.md)
- [Chunking Analysis Example](../../examples/chunking/)
- [Production Monitoring Guide](./production_deployment.md)

**Estimated time**: 2-3 hours for complete optimization
