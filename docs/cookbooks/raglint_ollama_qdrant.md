# RAGLint with Ollama and Qdrant

This cookbook demonstrates how to use RAGLint to evaluate a local RAG pipeline built with **Ollama** (for LLM/Embeddings) and **Qdrant** (for Vector Database).

## Prerequisites

-   Python 3.10+
-   [Ollama](https://ollama.com/) installed and running (e.g., `ollama serve`)
-   [Qdrant](https://qdrant.tech/) running (e.g., via Docker: `docker run -p 6333:6333 qdrant/qdrant`)
-   `raglint` installed (`pip install raglint`)
-   `langchain`, `langchain-community`, `qdrant-client` installed

## 1. Setup the RAG Pipeline

First, let's build a simple RAG pipeline using LangChain.

```python
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Qdrant
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.document_loaders import TextLoader
from langchain.chains import RetrievalQA

# 1. Initialize Ollama
llm = Ollama(model="llama3")
embeddings = OllamaEmbeddings(model="llama3")

# 2. Load and Index Data
# Create a dummy file for demonstration
with open("knowledge.txt", "w") as f:
    f.write("RAGLint is an observability tool for RAG pipelines. It helps you evaluate and monitor your LLM applications.")

loader = TextLoader("knowledge.txt")
documents = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = text_splitter.split_documents(documents)

# 3. Setup Qdrant
qdrant = Qdrant.from_documents(
    chunks,
    embeddings,
    url="http://localhost:6333",
    collection_name="raglint_demo",
    force_recreate=True
)
retriever = qdrant.as_retriever()

# 4. Create Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever
)
```

## 2. Instrument with RAGLint

Now, let's add RAGLint to trace the execution and evaluate the results.

```python
import raglint
from raglint.integrations.langchain import RAGLintCallbackHandler

# Initialize RAGLint
# This will start the background monitor
raglint.init(project_name="ollama-qdrant-demo")

# Create the callback handler
raglint_callback = RAGLintCallbackHandler()

# Run the chain with the callback
query = "What is RAGLint?"
response = qa_chain.invoke(
    {"query": query},
    config={"callbacks": [raglint_callback]}
)

print(f"Response: {response['result']}")
```

## 3. View Traces and Metrics

1.  Start the RAGLint dashboard:
    ```bash
    raglint dashboard
    ```
2.  Open `http://localhost:8000` in your browser.
3.  Go to **Traces** to see the execution tree (Chain -> Retriever -> LLM).
4.  Go to **Home** to see the metrics (Latency, Token usage, etc.).

## 4. Advanced Evaluation

To run a more comprehensive evaluation, you can use the `RAGPipelineAnalyzer`.

```python
from raglint import RAGPipelineAnalyzer

# Prepare data for analysis
data = [{
    "query": query,
    "response": response['result'],
    "retrieved_contexts": [doc.page_content for doc in retriever.get_relevant_documents(query)],
    # Optional: Ground truth if you have it
    # "ground_truth_contexts": [...] 
}]

# Initialize Analyzer
analyzer = RAGPipelineAnalyzer(use_smart_metrics=True)

# Run Analysis
results = analyzer.analyze(data)

print(f"Faithfulness: {results.faithfulness_scores}")
print(f"Answer Relevance: {results.detailed_results[0]['answer_relevance_score']}")
```
