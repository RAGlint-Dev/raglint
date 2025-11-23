"""
Tests for Context Precision and Recall metrics.
"""
import pytest
from raglint.metrics.context_metrics import ContextPrecisionScorer, ContextRecallScorer
from raglint.llm import MockLLM


@pytest.mark.asyncio
async def test_context_precision_basic():
    """Test basic context precision calculation."""
    llm = MockLLM()
    scorer = ContextPrecisionScorer(llm=llm)
    
    # Test with contexts and response
    score = await scorer.ascore(
        query="What is Python?",
        retrieved_contexts=["Python is a programming language.", "Python is easy to learn."],
        response="Python is a programming language that is easy to learn."
    )
    
    # MockLLM returns {"relevant": true} by default, so we expect some relevance
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


@pytest.mark.asyncio
async def test_context_precision_empty_contexts():
    """Test context precision with empty contexts."""
    llm = MockLLM()
    scorer = ContextPrecisionScorer(llm=llm)
    
    score = await scorer.ascore(
        query="What is Python?",
        retrieved_contexts=[],
        response="Python is great."
    )
    
    assert score == 0.0


def test_context_precision_sync():
    """Test sync version of context precision."""
    llm = MockLLM()
    scorer = ContextPrecisionScorer(llm=llm)
    
    score = scorer.score(
        query="What is Python?",
        retrieved_contexts=["Python is a language."],
        response="Python is great."
    )
    
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


@pytest.mark.asyncio
async def test_context_recall_basic():
    """Test basic context recall calculation."""
    llm = MockLLM()
    scorer = ContextRecallScorer(llm=llm)
    
    # Test with ground truth and retrieved contexts
    score = await scorer.ascore(
        query="What is Python?",
        retrieved_contexts=["Python is a programming language.", "It is easy to learn."],
        ground_truth_contexts=["Python is a programming language."]
    )
    
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


@pytest.mark.asyncio
async def test_context_recall_no_ground_truth():
    """Test context recall with no ground truth."""
    llm = MockLLM()
    scorer = ContextRecallScorer(llm=llm)
    
    score = await scorer.ascore(
        query="What is Python?",
        retrieved_contexts=["Python is great."],
        ground_truth_contexts=[]
    )
    
    # No ground truth to check against = perfect recall
    assert score == 1.0


@pytest.mark.asyncio
async def test_context_recall_no_retrieved():
    """Test context recall with no retrieved contexts."""
    llm = MockLLM()
    scorer = ContextRecallScorer(llm=llm)
    
    score = await scorer.ascore(
        query="What is Python?",
        retrieved_contexts=[],
        ground_truth_contexts=["Python is a programming language."]
    )
    
    # Retrieved nothing = zero recall
    assert score == 0.0


def test_context_recall_sync():
    """Test sync version of context recall."""
    llm = MockLLM()
    scorer = ContextRecallScorer(llm=llm)
    
    score = scorer.score(
        query="What is Python?",
        retrieved_contexts=["Python is a language."],
        ground_truth_contexts=["Python is a language."]
    )
    
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_context_recall_simple_fallback():
    """Test simple recall fallback (no LLM)."""
    scorer = ContextRecallScorer(llm=None)
    
    # Should use simple string matching
    score = scorer.score(
        query="Test",
        retrieved_contexts=["Python is a programming language."],
        ground_truth_contexts=["Python is a programming language."]
    )
    
    # High overlap should give high score
    assert score > 0.5


def test_context_recall_sentence_splitting():
    """Test sentence splitting in recall scorer."""
    scorer = ContextRecallScorer(llm=None)
    
    # Test with multiple sentences
    sentences = scorer._split_sentences("First sentence. Second sentence! Third sentence?")
    
    assert len(sentences) == 3
    assert "First sentence" in sentences
    assert "Second sentence" in sentences
    assert "Third sentence" in sentences


@pytest.mark.asyncio
async def test_context_precision_error_handling():
    """Test error handling in context precision."""
    # Create a mock LLM that raises an error
    class ErrorLLM:
        async def generate_json(self, prompt):
            raise Exception("LLM error")
    
    scorer = ContextPrecisionScorer(llm=ErrorLLM())
    
    # Should not crash, should handle error gracefully
    score = await scorer.ascore(
        query="Test",
        retrieved_contexts=["Context"],
        response="Response"
    )
    
    # Error handling should assume relevant (conservative)
    assert score >= 0.0


@pytest.mark.asyncio
async def test_context_recall_error_handling():
    """Test error handling in context recall."""
    # Create a mock LLM that raises an error
    class ErrorLLM:
        async def generate_json(self, prompt):
            raise Exception("LLM error")
    
    scorer = ContextRecallScorer(llm=ErrorLLM())
    
    # Should not crash
    score = await scorer.ascore(
        query="Test",
        retrieved_contexts=["Context"],
        ground_truth_contexts=["Ground truth"]
    )
    
    # Error handling should assume not covered (conservative)
    assert score >= 0.0
