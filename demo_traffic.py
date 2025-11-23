"""
Generate demo traffic for RAGLint.
Simulates a RAG pipeline to populate the dashboard and traces.
"""

import time
import random
import asyncio
from raglint import watch

# Simulate a retrieval function
@watch(tags=["retrieval"])
async def retrieve_documents(query: str):
    time.sleep(0.1 + random.random() * 0.5) # Simulate latency
    return [
        f"Document {i} relevant to '{query}'" 
        for i in range(random.randint(1, 3))
    ]

# Simulate an LLM generation
@watch(tags=["llm", "generation"])
async def generate_answer(query: str, context: list):
    time.sleep(0.5 + random.random() * 1.0) # Simulate latency
    if random.random() < 0.1:
        raise Exception("LLM API Timeout")
    return f"Here is the answer to '{query}' based on {len(context)} documents."

# Simulate the full pipeline
@watch(tags=["pipeline"])
async def rag_pipeline(query: str):
    print(f"Processing: {query}")
    try:
        docs = await retrieve_documents(query)
        answer = await generate_answer(query, docs)
        return answer
    except Exception as e:
        print(f"Error processing '{query}': {e}")
        return "I'm sorry, I encountered an error."

async def main():
    queries = [
        "What is RAGLint?",
        "How do I use the watch decorator?",
        "Is Postgres supported?",
        "Tell me about Azure integration.",
        "What is the capital of Sweden?"
    ]
    
    print("Generating demo traffic...")
    for q in queries:
        await rag_pipeline(q)
        time.sleep(1)
    print("Done! Check the dashboard.")

if __name__ == "__main__":
    asyncio.run(main())
