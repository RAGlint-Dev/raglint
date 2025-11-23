# Advanced Haystack Integration with RAGLint

This cookbook covers advanced evaluation patterns for [Haystack](https://haystack.deepset.ai/) pipelines.

## Prerequisites

```bash
pip install raglint haystack-ai sentence-transformers
```

## 1. Build Haystack Pipeline

```python
from haystack import Pipeline, Document
from haystack.components.retrievers import InMemoryEmbeddingRetriever
from haystack.components.embedders import SentenceTransformersTextEmbedder, SentenceTransformersDocumentEmbedder
from haystack.components.generators import OpenAIGenerator
from haystack.components.builders import PromptBuilder
from haystack.document_stores.in_memory import InMemoryDocumentStore

# Initialize document store
document_store = InMemoryDocumentStore()

# Prepare documents
documents = [
    Document(content="Haystack is an open-source framework for building search systems."),
    Document(content="You can use Haystack to build RAG pipelines with various LLMs."),
    Document(content="Haystack supports multiple vector databases like Qdrant and Weaviate.")
]

# Embed and write
doc_embedder = SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
doc_embedder.warm_up()
docs_with_embeddings = doc_embedder.run(documents)
document_store.write_documents(docs_with_embeddings["documents"])

# Build RAG pipeline
template = """
Given the following context, answer the question.

Context:
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Question: {{question}}
Answer:
"""

pipe = Pipeline()
pipe.add_component("text_embedder", SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2"))
pipe.add_component("retriever", InMemoryEmbeddingRetriever(document_store=document_store))
pipe.add_component("prompt_builder", PromptBuilder(template=template))
pipe.add_component("llm", OpenAIGenerator(model="gpt-3.5-turbo"))

pipe.connect("text_embedder.embedding", "retriever.query_embedding")
pipe.connect("retriever", "prompt_builder.documents")
pipe.connect("prompt_builder", "llm")
```

## 2. Extract Results for RAGLint

```python
def query_haystack_rag(question: str):
    result = pipe.run({
        "text_embedder": {"text": question},
        "prompt_builder": {"question": question}
    })
    
    return {
        "query": question,
        "retrieved_contexts": [doc.content for doc in result["retriever"]["documents"]],
        "response": result["llm"]["replies"][0]
    }
```

## 3. Evaluate with RAGLint

```python
from raglint.core import RAGPipelineAnalyzer

questions = [
    "What is Haystack?",
    "Can I use Haystack for RAG?",
    "Which databases does Haystack support?"
]

dataset = [query_haystack_rag(q) for q in questions]

analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)
results = analyzer.analyze(dataset)

print(f"Average Faithfulness: {sum(results.faithfulness_scores)/len(results.faithfulness_scores):.2f}")
```

## 4. Advanced: Custom Ranking

```python
from haystack.components.rankers import TransformersSimilarityRanker

# Add ranker to pipeline
ranker = TransformersSimilarityRanker(model="cross-encoder/ms-marco-MiniLM-L-6-v2")

pipe_with_ranker = Pipeline()
pipe_with_ranker.add_component("embedder", text_embedder)
pipe_with_ranker.add_component("retriever", retriever)
pipe_with_ranker.add_component("ranker", ranker)
pipe_with_ranker.add_component("prompt_builder", prompt_builder)
pipe_with_ranker.add_component("llm", llm)

pipe_with_ranker.connect("embedder", "retriever")
pipe_with_ranker.connect("retriever", "ranker")
pipe_with_ranker.connect("ranker", "prompt_builder")
pipe_with_ranker.connect("prompt_builder", "llm")
```

## 5. Compare Pipelines

```python
pipelines = {
    "baseline": pipe,
    "with_ranker": pipe_with_ranker
}

comparison_results = {}

for name, pipeline in pipelines.items():
    dataset = []
    for q in questions:
        result = pipeline.run({
            "text_embedder": {"text": q},
            "prompt_builder": {"question": q}
        })
        dataset.append({
            "query": q,
            "retrieved_contexts": [d.content for d in result["retriever"]["documents"]],
            "response": result["llm"]["replies"][0]
        })
    
    comparison_results[name] = analyzer.analyze(dataset)
    
# Compare
for name, results in comparison_results.items():
    print(f"\n{name}:")
    print(f"  Faithfulness: {sum(results.faithfulness_scores)/len(results.faithfulness_scores):.2f}")
```

## 6. Continuous Evaluation

```python
from raglint.tracking import get_tracker

tracker = get_tracker()

# Monitor production queries
def production_query(question: str):
    result = pipe.run({
        "text_embedder": {"text": question},
        "prompt_builder": {"question": question}
    })
    
    # Log to RAGLint
    tracker.log_single_evaluation(
        query=question,
        contexts=[d.content for d in result["retriever"]["documents"]],
        response=result["llm"]["replies"][0],
        run_name="Production Haystack Pipeline"
    )
    
    return result
```
