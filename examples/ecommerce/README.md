# E-commerce Product Q&A - RAGlint Example

## Overview

This example demonstrates using RAGlint to evaluate a product Q&A system for an e-commerce website. Product Q&A is a common RAG use case where customers ask questions about products and need accurate, grounded answers.

## Use Case

**Scenario**: Online electronics store with a RAG-powered Q&A chatbot
**Goal**: Ensure answers are factually accurate and don't hallucinate product features

## Dataset

`product_qa.json` contains 5 realistic product questions:
- Return policy questions
- Product feature inquiries
- Availability/options questions
- Suitability questions
- Compatibility questions

Each entry includes:
- `query`: Customer's question
- `retrieved_contexts`: Retrieved product information
- `response`: Generated answer
- `ground_truth`: Expected answer

## Running the Analysis

### Quick Analysis (Mock LLM)

```bash
cd examples/ecommerce
raglint analyze product_qa.json --output-dir=results/
```

### Smart Analysis (Real LLM)

```bash
export OPENAI_API_KEY="your-key-here"
raglint analyze product_qa.json --smart --output-dir=results/
```

### Expected Results

**Good Performance:**
- Faithfulness: > 0.85 (answers grounded in product info)
- Context Relevance: > 0.80 (retrieval works well)
- Answer Relevance: > 0.85 (answers the question)

**Warning Signs:**
- Faithfulness < 0.70: Bot is making up product features! 🚨
- Context Relevance < 0.60: Search isn't finding relevant products
- Answer Relevance < 0.70: Bot is going off-topic

## Common Issues & Fixes

### Issue 1: Low Faithfulness (Hallucinations)

**Symptom**: Answers mention features not in the product description

**Example**:
```
Query: "Is it waterproof?"
Context: "Splash-resistant design protects against light moisture"
Bad Answer: "Yes, it's fully waterproof and can be submerged underwater"
Good Answer: "It's splash-resistant, protecting against light moisture, but not fully waterproof"
```

**Fixes**:
1. Strengthen system prompt: "Only use information from the product description"
2. Use structured output to enforce grounding
3. Add a confidence score to the response

### Issue 2: Low Context Relevance

**Symptom**: Retrieved contexts don't match the query

**Example**:
```
Query: "What colors is the SmartWatch available in?"
Retrieved: [warranty policy, battery specs, shipping info]  # ❌ Wrong!
Should Retrieve: [color options, design features]  # ✅ Correct
```

**Fixes**:
1. Improve product metadata (add color, size, features as tags)
2. Use better embeddings (try `text-embedding-3-large`)
3. Implement hybrid search (BM25 + vector)

### Issue 3: Overly Verbose Answers

**Symptom**: Customer asks simple question, gets a paragraph

**Example**:
```
Query: "What colors?"
Bad: "We offer this product in several beautiful color options designed to match any style. The Midnight Black provides a sleek, professional look..." (200 words)
Good: "Available in Midnight Black, Space Gray, and Rose Gold"
```

**Fixes**:
1. Add length limits to generation
2. Prompt for conciseness: "Answer in 1-2 sentences"
3. Use temperature=0 for factual queries

##Python Example

```python
import asyncio
from raglint import RAGPipelineAnalyzer

async def analyze_ecommerce():
    analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)
    
    results = await analyzer.analyze_async("product_qa.json")
    
    # Check for issues
    if results['faithfulness_score'] < 0.85:
        print("⚠️ WARNING: Possible hallucinations detected!")
        print("Review responses for made-up features")
    
    if results['metrics']['context_relevance'] < 0.70:
        print("⚠️ WARNING: Retrieval quality is low!")
        print("Consider improving search or embeddings")
    
    if results['metrics']['answer_relevance'] < 0.80:
        print("⚠️ WARNING: Answers may be off-topic!")
        print("Review generation prompts")
    
    return results

# Run analysis
results = asyncio.run(analyze_ecommerce())
```

## Optimization Tips

1. **Chunk Product Info Wisely**
   - Separate features, specs, policies into distinct chunks
   - Use headers/metadata for better retrieval

2. **Test Edge Cases**
   - Ambiguous questions ("Is it good?")
   - Multi-part questions ("What's the price and warranty?")
   - Comparison questions ("X vs Y?")

3. **Monitor in Production**
   - Track faithfulness scores over time
   - Alert if scores drop below threshold
   - Log low-confidence answers for review

## Next Steps

1. Try running this example
2. Modify `product_qa.json` with your own products
3. Adjust thresholds in `raglint.yml`
4. Set up monitoring in production

## Resources

- [BEST_PRACTICES.md](../../docs/BEST_PRACTICES.md) - Metric interpretation
- [QUICKSTART.md](../../docs/QUICKSTART.md) - Getting started guide
- [Customer Support Example](../support/) - Similar use case

---

**Expected Analysis Time**: 30 seconds (mock LLM) or 2-3 minutes (real LLM)
