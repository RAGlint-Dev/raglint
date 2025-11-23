# LangChain Integration

RAGLint provides seamless integration with LangChain to evaluate your RAG chains.

## Installation

Install RAGLint with LangChain support:

```bash
pip install raglint[integrations]
```

Or install LangChain separately:

```bash
pip install raglint
pip install langchain langchain-community
```

## Quick Start

### 1. Evaluate a RetrievalQA Chain

```python
from langchain.chains import RetrievalQA
from langchain_openai import OpenAI
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from raglint.integrations.langchain import LangChainEvaluator

# Your existing LangChain setup
llm = OpenAI(temperature=0)
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_texts(documents, embeddings)

chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectorstore.as_retriever()
)

# Evaluate with RAGLint
evaluator = LangChainEvaluator(chain, use_smart_metrics=True)

test_cases = [
    {
        "query": "What is Python?",
        "ground_truth": "Python is a programming language"
    }
]

# Run evaluation
results = await evaluator.evaluate(test_cases)

# View results
print(f"Average Faithfulness: {results.summary_metrics['avg_faithfulness']:.2f}")
print(f"Average Relevance: {results.summary_metrics['avg_context_relevance']:.2f}")
```

### 2. Synchronous Evaluation

For non-async code:

```python
results = evaluator.evaluate_sync(test_cases)
```

### 3. Helper Functions

```python
from raglint.integrations import from_retrieval_qa, from_conversational_retrieval

# For RetrievalQA chains
evaluator = from_retrieval_qa(my_chain, use_smart_metrics=True)

# For ConversationalRetrievalChain
evaluator = from_conversational_retrieval(my_conv_chain)
```

## Supported Chain Types

RAGLint currently supports:

- ✅ `RetrievalQA`
- ✅ `ConversationalRetrievalChain`
- ✅ Custom chains (with `retrieve` method)

## Metrics Available

All RAGLint metrics work with LangChain chains:

- **Faithfulness**: Does the answer come from retrieved contexts?
- **Context Relevance**: Are retrieved chunks relevant to the query?
- **Answer Relevance**: Does the answer address the query?
- **Context Precision**: What % of retrieved chunks were used?
- **Context Recall**: Was all necessary information retrieved?
- **Semantic Similarity**: Cosine similarity with ground truth

Plus all custom plugin metrics!

## Configuration

Pass RAGLint config to the evaluator:

```python
config = {
    "provider": "openai",
    "model_name": "gpt-4",
    "metrics": {
        "faithfulness": True,
        "semantic": True,
    }
}

evaluator = LangChainEvaluator(chain, config=config)
```

## Example Output

```
EVALUATION RESULTS
==================================================
Summary Metrics:
  avg_faithfulness: 0.923
  avg_context_relevance: 0.856
  avg_context_precision: 0.750
  retrieval_stats:
    precision: 0.833
    recall: 0.800

Detailed Results:

--- Test Case 1 ---
Query: What is Python?
Response: Python is a high-level programming language...
Retrieved Contexts: 2 chunks
Metrics:
  faithfulness_score: 0.950
  context_precision: 0.800
  context_recall: 0.900
```

## Advanced Usage

### Custom Test Data Format

```python
test_cases = [
    {
        "query": "User question",
        "ground_truth": "Expected answer or context",  # Optional
        "metadata": {"category": "general"}  # Optional
    }
]
```

### Batch Evaluation

```python
import json

# Load test set
with open("test_set.json") as f:
    test_cases = json.load(f)

# Evaluate (with progress bar)
results = await evaluator.evaluate(test_cases, show_progress=True)

# Save results
with open("evaluation_results.json", "w") as f:
    json.dump(results.to_dict(), f, indent=2)
```

### Integration with Dashboard

After evaluation, upload results to the RAGLint dashboard:

```python
import requests

response = requests.post(
    "http://localhost:8000/analyze",
    json={
        "data": results.to_raglint_format(),
        "config": {"provider": "openai"}
    }
)

run_id = response.json()["id"]
print(f"View results at: http://localhost:8000/runs/{run_id}/ui")
```

## Performance Tips

1. **Use async evaluation** for faster processing:
   ```python
   results = await evaluator.evaluate(test_cases)
   ```

2. **Batch similar queries** to reuse retrieved contexts

3. **Limit test set size** during development (use sampling)

4. **Cache embeddings** in your vector store

## Troubleshooting

### "Module 'langchain' not found"

Install LangChain:
```bash
pip install raglint[integrations]
```

### Chain not supported

If your chain type isn't directly supported, you can manually convert:

```python
# Run your chain
result = my_chain.invoke({"query": query})

# Convert to RAGLint format
raglint_data = [{
    "query": query,
    "retrieved_contexts": extract_contexts(result),
    "response": result["answer"]
}]

# Analyze with RAGLint
from raglint import RAGPipelineAnalyzer
analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)
results = await analyzer.analyze_async(raglint_data)
```

## See Also

- [Full Example](../examples/langchain_integration.py)
- [RAGLint Core Documentation](../README.md)
- [LangChain Documentation](https://python.langchain.com/)
