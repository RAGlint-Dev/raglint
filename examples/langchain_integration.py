"""
Example: Using RAGLint with LangChain
"""

import asyncio
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains import RetrievalQA
from langchain_community.llms import FakeListLLM

from raglint.integrations.langchain import LangChainEvaluator


async def main():
    # 1. Create a simple LangChain RAG setup
    print("Setting up LangChain RAG chain...")
    
    # Sample documents
    documents = [
        "Python is a high-level programming language known for its simplicity.",
        "Python was created by Guido van Rossum and first released in 1991.",
        "Python supports multiple programming paradigms including procedural, object-oriented, and functional.",
        "RAG stands for Retrieval-Augmented Generation, a technique combining retrieval and generation.",
        "RAG improves LLM outputs by grounding them in retrieved relevant documents."
    ]
    
    # Create embeddings and vector store
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = FAISS.from_texts(documents, embeddings)
    
    # Create a fake LLM for demo (replace with OpenAI("gpt-3.5-turbo") in production)
    llm = FakeListLLM(responses=[
        "Python is a high-level programming language created by Guido van Rossum.",
        "RAG combines retrieval and generation to improve LLM outputs."
    ])
    
    # Create RetrievalQA chain
    chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 2})
    )
    
    # 2. Create RAGLint evaluator
    print("\nCreating RAGLint evaluator...")
    evaluator = LangChainEvaluator(chain, use_smart_metrics=True)
    
    # 3. Define test cases
    test_cases = [
        {
            "query": "What is Python?",
            "ground_truth": "Python is a high-level programming language"
        },
        {
            "query": "What does RAG stand for?",
            "ground_truth": "RAG stands for Retrieval-Augmented Generation"
        }
    ]
    
    # 4. Evaluate
    print("\nEvaluating LangChain chain with RAGLint...")
    results = await evaluator.evaluate(test_cases, show_progress=True)
    
    # 5. Print results
    print("\n" + "="*60)
    print("EVALUATION RESULTS")
    print("="*60)
    
    print(f"\nSummary Metrics:")
    for metric, value in results.summary_metrics.items():
        if isinstance(value, dict):
            print(f"  {metric}:")
            for k, v in value.items():
                print(f"    {k}: {v:.3f}" if isinstance(v, float) else f"    {k}: {v}")
        else:
            print(f"  {metric}: {value:.3f}" if isinstance(value, float) else f"  {metric}: {value}")
    
    print(f"\nDetailed Results:")
    for i, item in enumerate(results.detailed_results, 1):
        print(f"\n--- Test Case {i} ---")
        print(f"Query: {item['query']}")
        print(f"Response: {item['response']}")
        print(f"Retrieved Contexts: {len(item['retrieved_contexts'])} chunks")
        print(f"Metrics:")
        for metric, value in item.items():
            if metric not in ['query', 'response', 'retrieved_contexts', 'ground_truth_contexts']:
                if isinstance(value, float):
                    print(f"  {metric}: {value:.3f}")
                elif isinstance(value, dict):
                    print(f"  {metric}: {value}")


if __name__ == "__main__":
    # Run the async example
    asyncio.run(main())
    
    print("\n" + "="*60)
    print("Example completed! You can now use RAGLint with LangChain.")
    print("="*60)
