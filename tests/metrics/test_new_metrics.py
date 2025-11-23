import pytest
from unittest.mock import MagicMock
from raglint.metrics import BiasScorer, ToneScorer, ConcisenessScorer

class MockLLM:
    def generate(self, prompt):
        return "Reasoning: Test reasoning\nScore: 1.0"
    
    async def agenerate(self, prompt):
        return "Reasoning: Test reasoning\nScore: 1.0"

@pytest.mark.asyncio
async def test_bias_scorer():
    scorer = BiasScorer(llm=MockLLM())
    score, reason = scorer.score("query", "response")
    assert score == 1.0
    assert reason == "Test reasoning"
    
    score, reason = await scorer.ascore("query", "response")
    assert score == 1.0

@pytest.mark.asyncio
async def test_tone_scorer():
    scorer = ToneScorer(llm=MockLLM(), desired_tone="professional")
    score, reason = scorer.score("query", "response")
    assert score == 1.0
    
@pytest.mark.asyncio
async def test_conciseness_scorer():
    scorer = ConcisenessScorer(llm=MockLLM())
    score, reason = scorer.score("query", "response")
    assert score == 1.0
