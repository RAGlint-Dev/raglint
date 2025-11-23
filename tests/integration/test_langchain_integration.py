"""Integration test for LangChain integration."""
import pytest

try:
    from langchain.chains import RetrievalQA
    from langchain.llms.fake import FakeListLLM
    from langchain.vectorstores import FAISS
    from langchain.embeddings import FakeEmbeddings
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False


@pytest.mark.skipif(not LANGCHAIN_AVAILABLE, reason="LangChain not installed")
@pytest.mark.asyncio
async def test_langchain_integration():
    """Test RAGLint integration with LangChain."""
    from raglint.integrations.langchain import LangChainEvaluator
    
    # Create fake LangChain components
    embeddings = FakeEmbeddings(size=384)
    
    # Create fake vector store
    texts = ["Python is a programming language.", "JavaScript is for web development."]
    vectorstore = FAISS.from_texts(texts, embeddings)
    
    # Create fake LLM
    responses = ["Python is a programming language used for many things."]
    llm = FakeListLLM(responses=responses)
    
    # Create retrieval chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever()
    )
    
    # Create evaluator
    evaluator = LangChainEvaluator(qa_chain)
    
    # Test cases
    test_cases = [
        {
            "query": "What is Python?",
            "ground_truth": "Python is a programming language."
        }
    ]
    
    # Evaluate
    results = await evaluator.evaluate(test_cases)
    
    # Verify results
    assert len(results) == 1
    assert "faithfulness" in results[0]
    assert "answer_relevance" in results[0]


@pytest.mark.skipif(not LANGCHAIN_AVAILABLE, reason="LangChain not installed")
def test_langchain_evaluator_init():
    """Test LangChainEvaluator initialization."""
    from raglint.integrations.langchain import LangChainEvaluator
    
    # Create fake chain
    embeddings = FakeEmbeddings(size=384)
    texts = ["Test text"]
    vectorstore = FAISS.from_texts(texts, embeddings)
    llm = FakeListLLM(responses=["Test response"])
    qa_chain = RetrievalQA.from_chain_type(llm=llm, retriever=vectorstore.as_retriever())
    
    # Initialize evaluator
    evaluator = LangChainEvaluator(qa_chain)
    
    # Verify initialization
    assert evaluator.chain == qa_chain
    assert evaluator.config is not None
