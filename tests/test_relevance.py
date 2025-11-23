"""
Tests for relevance metrics (Context Relevance and Answer Relevance).
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from raglint.metrics.relevance import (
    ContextRelevanceScorer,
    AnswerRelevanceScorer,
)
from raglint.llm import MockLLM


@pytest.mark.asyncio
async def test_context_relevance_scorer_mock():
    """Test ContextRelevanceScorer with MockLLM."""
    llm = MockLLM()
    scorer = ContextRelevanceScorer(llm=llm)
    
    score, reasoning = await scorer.ascore(
        query="What is AI?",
        context="AI is artificial intelligence."
    )
    
    assert score == 1.0
    assert "MOCK" in reasoning


@pytest.mark.asyncio
async def test_answer_relevance_scorer_mock():
    """Test AnswerRelevanceScorer with MockLLM."""
    llm = MockLLM()
    scorer = AnswerRelevanceScorer(llm=llm)
    
    score, reasoning = await scorer.ascore(
        query="What is AI?",
        response="AI is artificial intelligence."
    )
    
    assert score == 1.0
    assert "MOCK" in reasoning


@pytest.mark.asyncio
async def test_relevance_parsing_logic():
    """Test parsing of LLM output."""
    llm = MagicMock()
    llm.agenerate = AsyncMock(return_value="Reasoning: Good match.\nScore: 0.8")
    
    scorer = ContextRelevanceScorer(llm=llm)
    score, reasoning = await scorer.ascore("q", "c")
    
    assert score == 0.8
    assert reasoning == "Good match."


@pytest.mark.asyncio
async def test_relevance_parsing_error():
    """Test parsing of invalid LLM output."""
    llm = MagicMock()
    llm.agenerate = AsyncMock(return_value="Invalid output format")
    
    scorer = ContextRelevanceScorer(llm=llm)
    score, reasoning = await scorer.ascore("q", "c")
    
    assert score == 0.0
    assert "Error parsing" in reasoning or "Invalid" in reasoning


def test_context_relevance_scorer_sync():
    """Test ContextRelevanceScorer sync score method."""
    llm = MockLLM()
    scorer = ContextRelevanceScorer(llm=llm)
    
    score, reasoning = scorer.score(
        query="What is AI?",
        context=["AI is artificial intelligence."]
    )
    
    assert score == 1.0
    assert "MOCK" in reasoning


def test_answer_relevance_scorer_sync():
    """Test AnswerRelevanceScorer sync score method."""
    llm = MockLLM()
    scorer = AnswerRelevanceScorer(llm=llm)
    
    score, reasoning = scorer.score(
        query="What is AI?",
        response="AI is artificial intelligence."
    )
    
    assert score == 1.0
    assert "MOCK" in reasoning
