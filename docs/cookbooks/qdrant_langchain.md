# Evaluating a Qdrant + LangChain RAG Pipeline

This cookbook demonstrates how to use RAGLint to evaluate a RAG pipeline built with [Qdrant](https://qdrant.tech/) and [LangChain](https://langchain.com/).

## Prerequisites

```bash
pip install raglint langchain qdrant-client openai
```

## 1. Setup the RAG Pipeline

First, let's create a simple RAG pipeline using LangChain and Qdrant.

```python
import os
from langchain.vectorstores import Qdrant
from langchain.embeddings import OpenAIEmbeddings
from langchain.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

# 1. Load and Index Data
loader = TextLoader("state_of_the_union.txt")
documents = loader.load()
text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
docs = text_splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()

qdrant = Qdrant.from_documents(
    docs,
    embeddings,
    location=":memory:",  # Local in-memory mode
    collection_name="my_documents",
)

retriever = qdrant.as_retriever()
llm = ChatOpenAI(model_name="gpt-3.5-turbo")
qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever)
```

## 2. Instrument with RAGLint

Now, we wrap the LangChain components to capture traces automatically.

```python
from raglint.integrations.langchain import RAGLintCallbackHandler
from raglint.tracking import get_tracker

# Initialize RAGLint tracker
tracker = get_tracker()
raglint_callback = RAGLintCallbackHandler(tracker)

# Run a query with the callback
query = "What did the president say about Ketanji Brown Jackson?"
response = qa_chain.run(query, callbacks=[raglint_callback])

print(f"Response: {response}")
```

## 3. Evaluate Offline

Alternatively, you can collect a dataset of (query, context, response) and evaluate it using the RAGLint CLI or SDK.

### Step 3a: Create a Dataset

```python
data = [
    {
        "query": "What is the capital of France?",
        "retrieved_contexts": ["Paris is the capital and most populous city of France."],
        "response": "The capital of France is Paris."
    },
    {
        "query": "Who wrote Hamlet?",
        "retrieved_contexts": ["Hamlet is a tragedy written by William Shakespeare."],
        "response": "William Shakespeare wrote Hamlet."
    }
]

import json
with open("eval_data.json", "w") as f:
    json.dump(data, f)
```

### Step 3b: Run Analysis

```bash
raglint analyze eval_data.json --smart
```

## 4. Using Custom Metrics (Bias & Tone)

RAGLint now supports checking for Bias and Tone. You can enable these in your `raglint.yml` or use them programmatically.

```python
from raglint.metrics import BiasScorer, ToneScorer

bias_scorer = BiasScorer()
tone_scorer = ToneScorer(desired_tone="professional")

score, reason = bias_scorer.score(query, response)
print(f"Bias Score: {score} ({reason})")

score, reason = tone_scorer.score(query, response)
print(f"Tone Score: {score} ({reason})")
```
