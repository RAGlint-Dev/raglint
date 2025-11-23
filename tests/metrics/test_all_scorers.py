"""
Comprehensive tests for all metric scorers.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from raglint.metrics import (
    BiasScorer,
    ToneScorer,
    ConcisenessScorer,
    FaithfulnessScorer,
    ToxicityScorer
)
from raglint.llm import MockLLM


@pytest.fixture
def mock_llm():
    """Create a mock LLM for testing."""
    return MockLLM()


# BiasScorer Tests
@pytest.mark.asyncio
async def test_bias_scorer_initialization(mock_llm):
    """Test BiasScorer can be initialized."""
    scorer = BiasScorer(llm=mock_llm)
    assert scorer.llm is not None


@pytest.mark.asyncio
async def test_bias_scorer_async(mock_llm):
    """Test BiasScorer async scoring."""
    scorer = BiasScorer(llm=mock_llm)
    score, reason = await scorer.ascore(
        query="Test query",
        response="Test response"
    )
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0
    assert isinstance(reason, str)


def test_bias_scorer_sync(mock_llm):
    """Test BiasScorer synchronous scoring."""
    scorer = BiasScorer(llm=mock_llm)
    score, reason = scorer.score(
        query="Test query",
        response="Test response"
    )
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0
    assert "MOCK" in reason


# ToneScorer Tests
@pytest.mark.asyncio
async def test_tone_scorer_initialization(mock_llm):
    """Test ToneScorer initialization with desired_tone."""
    scorer = ToneScorer(llm=mock_llm, desired_tone="professional")
    assert scorer.desired_tone == "professional"


@pytest.mark.asyncio
async def test_tone_scorer_async(mock_llm):
    """Test ToneScorer async scoring."""
    scorer = ToneScorer(llm=mock_llm, desired_tone="friendly")
    score, reason = await scorer.ascore(
        query="How are you?",
        response="I'm doing great, thanks for asking!"
    )
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_tone_scorer_sync(mock_llm):
    """Test ToneScorer synchronous scoring."""
    scorer = ToneScorer(llm=mock_llm, desired_tone="professional")
    score, reason = scorer.score(
        query="What is your status?",
        response="Everything is operating normally."
    )
    assert isinstance(score, float)
    assert "MOCK" in reason


# ConcisenessScorer Tests
@pytest.mark.asyncio
async def test_conciseness_scorer_initialization(mock_llm):
    """Test ConcisenessScorer initialization."""
    scorer = ConcisenessScorer(llm=mock_llm)
    assert scorer.llm is not None


@pytest.mark.asyncio
async def test_conciseness_scorer_async(mock_llm):
    """Test ConcisenessScorer async scoring."""
    scorer = ConcisenessScorer(llm=mock_llm)
    score, reason = await scorer.ascore(
        query="What is AI?",
        response="AI is artificial intelligence."
    )
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_conciseness_scorer_sync(mock_llm):
    """Test ConcisenessScorer synchronous scoring."""
    scorer = ConcisenessScorer(llm=mock_llm)
    score, reason = scorer.score(
        query="Explain ML",
        response="Machine learning is a subset of AI that enables systems to learn from data."
    )
    assert isinstance(score, float)
    assert "MOCK" in reason


# FaithfulnessScorer Tests
@pytest.mark.asyncio
async def test_faithfulness_scorer_async(mock_llm):
    """Test FaithfulnessScorer async scoring."""
    scorer = FaithfulnessScorer(llm=mock_llm)
    score, reason = await scorer.ascore(
        query="What is the capital of France?",
        retrieved_contexts=["Paris is the capital of France."],
        response="The capital of France is Paris."
    )
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_faithfulness_scorer_sync(mock_llm):
    """Test FaithfulnessScorer synchronous scoring."""
    scorer = FaithfulnessScorer(llm=mock_llm)
    score, reason = scorer.score(
        query="What is Python?",
        retrieved_contexts=["Python is a programming language."],
        response="Python is a programming language."
    )
    assert isinstance(score, float)
    assert "MOCK" in reason


# ToxicityScorer Tests
@pytest.mark.asyncio
async def test_toxicity_scorer_async(mock_llm):
    """Test ToxicityScorer async scoring."""
    scorer = ToxicityScorer(llm=mock_llm)
    score, reason = await scorer.ascore(
        response="This is a polite and respectful response."
    )
    assert isinstance(score, float)
    assert 0.0 <= score <= 1.0


def test_toxicity_scorer_sync(mock_llm):
    """Test ToxicityScorer synchronous scoring."""
    scorer = ToxicityScorer(llm=mock_llm)
    score, reason = scorer.score(
        response="Thank you for your question."
    )
    assert isinstance(score, float)
    assert "MOCK" in reason


# Parsing Tests
@pytest.mark.asyncio
async def test_scorer_parsing_resilience():
    """Test that scorers handle malformed LLM output gracefully."""
    llm = MagicMock()
    llm.agenerate = AsyncMock(return_value="Malformed output with no score")
    
    scorer = BiasScorer(llm=llm)
    score, reason = await scorer.ascore("q", "r")
    
    # Should default to 0.0 or handle gracefully
    assert isinstance(score, float)
    assert isinstance(reason, str)


@pytest.mark.asyncio
async def test_scorer_with_custom_prompt():
    """Test scorer with custom prompt template."""
    custom_prompt = "Custom: {query} {response}"
    scorer = BiasScorer(llm=MockLLM(), prompt_template=custom_prompt)
    
    score, reason = await scorer.ascore("test", "response")
    assert isinstance(score, float)
