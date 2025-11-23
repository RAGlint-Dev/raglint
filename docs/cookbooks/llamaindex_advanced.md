# Advanced LlamaIndex Integration with RAGLint

This cookbook demonstrates advanced patterns for evaluating [LlamaIndex](https://www.llamaindex.ai/) RAG pipelines.

## Prerequisites

```bash
pip install raglint llama-index openai
```

## 1. Setup LlamaIndex with Custom Retrievers

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

# Configure LLM and embeddings
Settings.llm = OpenAI(model="gpt-4", temperature=0.1)
Settings.embed_model = OpenAIEmbedding(model="text-embedding-ada-002")

# Load documents
documents = SimpleDirectoryReader("./docs").load_data()
index = VectorStoreIndex.from_documents(documents)

# Create query engine
query_engine = index.as_query_engine(
    similarity_top_k=5,
    response_mode="compact"
)
```

## 2. Instrument with RAGLint Callback

```python
from raglint.integrations.llamaindex import RAGLintCallbackHandler
from raglint.tracking import get_tracker

tracker = get_tracker()
callback = RAGLintCallbackHandler(tracker=tracker)

# Add callback to query engine
Settings.callback_manager.add_handler(callback)

# Now queries are automatically tracked
response = query_engine.query("What is the main topic?")
```

## 3. Advanced: Multi-Index Routing

```python
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector

# Create multiple indexes
tech_index = VectorStoreIndex.from_documents(tech_docs)
science_index = VectorStoreIndex.from_documents(science_docs)

# Create tools
tech_tool = QueryEngineTool(
    query_engine=tech_index.as_query_engine(),
    metadata=ToolMetadata(
        name="tech",
        description="Technical documentation about software and programming"
    )
)

science_tool = QueryEngineTool(
    query_engine=science_index.as_query_engine(),
    metadata=ToolMetadata(
        name="science",
        description="Scientific articles and research papers"
    )
)

# Router
router_engine = RouterQueryEngine(
    selector=LLMSingleSelector.from_defaults(),
    query_engine_tools=[tech_tool, science_tool]
)
```

## 4. Evaluate Routing Decisions

```python
from raglint.core import RAGPipelineAnalyzer

queries = [
    {"query": "Explain machine learning", "expected_route": "tech"},
    {"query": "What is photosynthesis?", "expected_route": "science"},
]

results = []
for q in queries:
    response = router_engine.query(q["query"])
    results.append({
        "query": q["query"],
        "retrieved_contexts": [node.text for node in response.source_nodes],
        "response": str(response),
        "metadata": {"expected_route": q["expected_route"]}
    })

analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)
analysis = analyzer.analyze(results)
```

## 5. Advanced: Reranking Pipeline

```python
from llama_index.core.postprocessor import SentenceTransformerRerank

reranker = SentenceTransformerRerank(
    model="cross-encoder/ms-marco-MiniLM-L-6-v2",
    top_n=3
)

query_engine_rerank = index.as_query_engine(
    similarity_top_k=10,
    node_postprocessors=[reranker]
)
```

## 6. Compare Pipelines

```python
# Test multiple configurations
configs = [
    {"name": "baseline", "top_k": 3, "rerank": False},
    {"name": "more_contexts", "top_k": 10, "rerank": False},
    {"name": "reranked", "top_k": 10, "rerank": True}
]

for config in configs:
    engine = index.as_query_engine(
        similarity_top_k=config["top_k"],
        node_postprocessors=[reranker] if config["rerank"] else []
    )
    
    # Collect results
    dataset = []
    for q in test_questions:
        response = engine.query(q)
        dataset.append({
            "query": q,
            "retrieved_contexts": [n.text for n in response.source_nodes],
            "response": str(response)
        })
    
    # Analyze
    results = analyzer.analyze(dataset)
    
    # Log to RAGLint dashboard
    tracker.log_run(
        name=f"LlamaIndex {config['name']}",
        config=config,
        results=results,
        tags=["llamaindex", "comparison"]
    )
```

## 7. Async Batch Evaluation

```python
import asyncio

async def batch_evaluate(questions):
    async def query_async(q):
        response = await query_engine.aquery(q)
        return {
            "query": q,
            "retrieved_contexts": [n.text for n in response.source_nodes],
            "response": str(response)
        }
    
    tasks = [query_async(q) for q in questions]
    return await asyncio.gather(*tasks)

# Run
dataset = asyncio.run(batch_evaluate(test_questions))
results = await analyzer.analyze_async(dataset)
```
