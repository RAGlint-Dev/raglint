# Evaluating Chroma RAG Pipeline

Learn how to evaluate a RAG system built with [Chroma](https://www.trychroma.com/), the open-source embedding database.

## Prerequisites

```bash
pip install raglint chromadb openai
```

## 1. Initialize Chroma

```python
import chromadb
from chromadb.config import Settings

# Persistent client
client = chromadb.PersistentClient(path="./chroma_db")

# Or in-memory for testing
# client = chromadb.Client()

# Create collection with OpenAI embeddings
collection = client.get_or_create_collection(
    name="documents",
    metadata={"hnsw:space": "cosine"}
)
```

## 2. Add Documents

```python
documents = [
    "Python is a high-level programming language.",
    "JavaScript is primarily used for web development.",
    "SQL is used for database queries.",
    "Docker containers package applications with dependencies."
]

# Chroma handles embedding automatically if you use default function
collection.add(
    documents=documents,
    ids=[f"doc{i}" for i in range(len(documents))],
    metadatas=[{"source": f"doc{i}.txt"} for i in range(len(documents))]
)
```

## 3. RAG Query Function

```python
from openai import OpenAI

client_openai = OpenAI()

def chroma_rag(question: str, n_results: int = 3):
    # Query Chroma
    results = collection.query(
        query_texts=[question],
        n_results=n_results
    )
    
    contexts = results['documents'][0]
    
    # Generate answer
    context_str = "\n".join(contexts)
    response = client_openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{
            "role": "user",
            "content": f"Based on:\n{context_str}\n\nAnswer: {question}"
        }]
    )
    
    return {
        "query": question,
        "retrieved_contexts": contexts,
        "response": response.choices[0].message.content,
        "metadata": results['metadatas'][0]
    }
```

## 4. Evaluate Multiple Queries

```python
from raglint.core import RAGPipelineAnalyzer

questions = [
    "What is Python used for?",
    "Which language is for web development?",
    "How do I query databases?"
]

dataset = [chroma_rag(q) for q in questions]

# Analyze with RAGLint
analyzer = RAGPipelineAnalyzer(
    use_smart_metrics=True,
    config={"provider": "openai"}
)

results = analyzer.analyze(dataset)
```

## 5. Custom Embedding Function

```python
from chromadb.utils import embedding_functions

# Use OpenAI embeddings
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key="YOUR_API_KEY",
    model_name="text-embedding-ada-002"
)

collection_openai = client.create_collection(
    name="openai_docs",
    embedding_function=openai_ef
)
```

## 6. Filter by Metadata

```python
# Query with metadata filtering
filtered_results = collection.query(
    query_texts=["database"],
    n_results=5,
    where={"source": "doc2.txt"}
)
```

## 7. Track Experiments

```python
from raglint.tracking import get_tracker

tracker = get_tracker()
run_id = tracker.log_run(
    name="Chroma RAG Test",
    config={
        "collection": "documents",
        "embedding": "default",
        "n_results": 3
    },
    results=results,
    tags=["chroma", "experiment"]
)
```

## 8. Dashboard Visualization

```bash
raglint dashboard
# Navigate to http://localhost:8000/runs/{run_id}
```
