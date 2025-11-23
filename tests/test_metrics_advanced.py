import pytest
from unittest.mock import MagicMock, AsyncMock
from raglint.metrics.relevance import AnswerRelevanceScorer
from raglint.metrics.toxicity import ToxicityScorer

class TestAdvancedMetrics:
    
    @pytest.mark.asyncio
    async def test_answer_relevance_scorer(self):
        mock_llm = MagicMock()
        mock_llm.agenerate = AsyncMock(return_value="Reasoning: It answers directly.\nScore: 1.0")
        
        scorer = AnswerRelevanceScorer(llm=mock_llm)
        score, reasoning = await scorer.ascore("What is RAG?", "RAG stands for Retrieval Augmented Generation.")
        
        assert score == 1.0
        assert "It answers directly" in reasoning
        
    @pytest.mark.asyncio
    async def test_toxicity_scorer_safe(self):
        mock_llm = MagicMock()
        mock_llm.agenerate = AsyncMock(return_value="Reasoning: No harmful content.\nScore: 1.0")
        
        scorer = ToxicityScorer(llm=mock_llm)
        score, reasoning = await scorer.ascore("Hello world")
        
        assert score == 1.0
        assert "No harmful content" in reasoning

    @pytest.mark.asyncio
    async def test_toxicity_scorer_toxic(self):
        mock_llm = MagicMock()
        mock_llm.agenerate = AsyncMock(return_value="Reasoning: Contains hate speech.\nScore: 0.0")
        
        scorer = ToxicityScorer(llm=mock_llm)
        score, reasoning = await scorer.ascore("I hate you")
        
        assert score == 0.0
        assert "Contains hate speech" in reasoning
