# Evaluating Pinecone + OpenAI RAG Pipeline

This cookbook demonstrates how to evaluate a RAG pipeline built with [Pinecone](https://pinecone.io/) vector database and OpenAI embeddings.

## Prerequisites

```bash
pip install raglint pinecone-client openai tiktoken
```

## 1. Setup Pinecone Vector Store

```python
import os
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI

# Initialize Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# Create index
index_name = "raglint-demo"
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=1536,  # OpenAI ada-002 dimensions
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

index = pc.Index(index_name)

# Initialize OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

## 2. Index Your Documents

```python
documents = [
    "Paris is the capital and most populous city of France.",
    "The Eiffel Tower is a wrought-iron lattice tower in Paris.",
    "France is a country in Western Europe.",
    "The Louvre is the world's most visited museum, located in Paris."
]

# Generate embeddings and upsert
vectors = []
for i, doc in enumerate(documents):
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=doc
    )
    embedding = response.data[0].embedding
    
    vectors.append({
        "id": f"doc_{i}",
        "values": embedding,
        "metadata": {"text": doc}
    })

index.upsert(vectors=vectors)
```

## 3. Build RAG Query Function

```python
def query_rag(question: str, top_k: int = 3):
    # Embed the question
    response = client.embeddings.create(
        model="text-embedding-ada-002",
        input=question
    )
    query_embedding = response.data[0].embedding
    
    # Search Pinecone
    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )
    
    # Extract contexts
    contexts = [match['metadata']['text'] for match in results['matches']]
    
    # Generate answer with GPT
    context_str = "\n".join(contexts)
    prompt = f"Context:\n{context_str}\n\nQuestion: {question}\n\nAnswer:"
    
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    
    answer = completion.choices[0].message.content
    
    return {
        "query": question,
        "retrieved_contexts": contexts,
        "response": answer
    }
```

## 4. Collect Evaluation Dataset

```python
eval_questions = [
    "What is the capital of France?",
    "Tell me about the Eiffel Tower",
    "Where is the Louvre museum?"
]

dataset = [query_rag(q) for q in eval_questions]

# Save for RAGLint
import json
with open("pinecone_eval.json", "w") as f:
    json.dump(dataset, f, indent=2)
```

## 5. Evaluate with RAGLint

```bash
raglint analyze pinecone_eval.json --smart --provider openai
```

## 6. Programmatic Evaluation

```python
from raglint.core import RAGPipelineAnalyzer

analyzer = RAGPipelineAnalyzer(
    use_smart_metrics=True,
    config={
        "provider": "openai",
        "model_name": "gpt-3.5-turbo"
    }
)

results = analyzer.analyze(dataset)

print(f"Average Faithfulness: {sum(results.faithfulness_scores) / len(results.faithfulness_scores):.2f}")
print(f"Retrieval Precision: {results.retrieval_stats['precision']:.2f}")
```

## 7. Track Results Over Time

```python
from raglint.tracking import get_tracker

tracker = get_tracker()
run_id = tracker.log_run(
    name="Pinecone RAG Evaluation",
    config={"index": index_name, "model": "gpt-3.5-turbo"},
    results=results,
    tags=["pinecone", "production"]
)

print(f"Run ID: {run_id}")
```

## 8. View in Dashboard

```bash
raglint dashboard
# Open http://localhost:8000
```
