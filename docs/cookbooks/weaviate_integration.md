# Evaluating Weaviate RAG Pipeline

This cookbook shows how to evaluate a RAG system using [Weaviate](https://weaviate.io/) vector database.

## Prerequisites

```bash
pip install raglint weaviate-client openai
```

## 1. Connect to Weaviate

```python
import weaviate
import os

# Connect to Weaviate Cloud
client = weaviate.Client(
    url="https://your-cluster.weaviate.network",
    auth_client_secret=weaviate.AuthApiKey(api_key=os.getenv("WEAVIATE_API_KEY")),
    additional_headers={
        "X-OpenAI-Api-Key": os.getenv("OPENAI_API_KEY")
    }
)

# Or connect to local instance
# client = weaviate.Client("http://localhost:8080")
```

## 2. Create Schema

```python
schema = {
    "class": "Document",
    "description": "A document for RAG",
    "vectorizer": "text2vec-openai",
    "moduleConfig": {
        "text2vec-openai": {
            "model": "ada",
            "modelVersion": "002",
            "type": "text"
        }
    },
    "properties": [
        {
            "name": "content",
            "dataType": ["text"],
            "description": "The document content"
        },
        {
            "name": "title",
            "dataType": ["string"],
            "description": "Document title"
        }
    ]
}

client.schema.create_class(schema)
```

## 3. Import Documents

```python
documents = [
    {"title": "AI Overview", "content": "Artificial Intelligence is the simulation of human intelligence."},
    {"title": "ML Basics", "content": "Machine Learning is a subset of AI that learns from data."},
    {"title": "Neural Networks", "content": "Neural networks are computing systems inspired by biological brains."}
]

with client.batch as batch:
    for doc in documents:
        batch.add_data_object(
            data_object=doc,
            class_name="Document"
        )
```

## 4. Query RAG Pipeline

```python
from openai import OpenAI

openai_client = OpenAI()

def weaviate_rag(question: str, limit: int = 3):
    # Hybrid search (vector + keyword)
    result = client.query.get(
        "Document",
        ["content", "title"]
    ).with_hybrid(
        query=question,
        alpha=0.7  # 0.7 = more vector, 0.3 = more keyword
    ).with_limit(limit).do()
    
    contexts = [doc['content'] for doc in result['data']['Get']['Document']]
    
    # Generate answer
    context_str = "\n\n".join(contexts)
    response = openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Answer based on the provided context."},
            {"role": "user", "content": f"Context:\n{context_str}\n\nQuestion: {question}"}
        ]
    )
    
    return {
        "query": question,
        "retrieved_contexts": contexts,
        "response": response.choices[0].message.content
    }
```

## 5. Evaluate with RAGLint

```python
from raglint.core import RAGPipelineAnalyzer

questions = [
    "What is artificial intelligence?",
    "How does machine learning work?",
    "Explain neural networks"
]

dataset = [weaviate_rag(q) for q in questions]

analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)
results = analyzer.analyze(dataset)

print(f"Faithfulness: {sum(results.faithfulness_scores)/len(results.faithfulness_scores):.2f}")
```

## 6. Advanced: Filter + Vector Search

```python
def filtered_rag(question: str, category: str):
    result = client.query.get(
        "Document",
        ["content"]
    ).with_where({
        "path": ["category"],
        "operator": "Equal",
        "valueString": category
    }).with_near_text({
        "concepts": [question]
    }).with_limit(5).do()
    
    return result
```
