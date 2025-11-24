"""
Hallucination Confidence Scorer - Estimates confidence in response accuracy.

Uses multiple signals to assess how confident we should be that the response
is grounded and not hallucinated.
"""
from typing import Any

from raglint.plugins.interface import PluginInterface


class HallucinationConfidencePlugin(PluginInterface):
    """
    Estimates confidence that response is NOT hallucinated.

    Combines multiple signals:
    - Context overlap (how much response matches contexts)
    - Specificity (vague answers = lower confidence)
    - Hedging language ("maybe", "might" = lower confidence)
    - Citation presence (citations = higher confidence)
    """

    name = "hallucination_confidence"
    version = "1.0.0"
    description = "Estimates confidence that response is grounded, not hallucinated"

    # Hedging words (indicate uncertainty)
    HEDGING_WORDS = [
        'maybe', 'might', 'could', 'possibly', 'perhaps',
        'probably', 'likely', 'seems', 'appears', 'suggests',
        'I think', 'I believe', 'I assume', 'uncertain'
    ]

    async def calculate_async(
        self,
        query: str,
        response: str,
        contexts: list[str],
        **kwargs: Any
    ) -> dict[str, Any]:
        """Calculate hallucination confidence score."""

        # Signal 1: Context overlap
        overlap_score = self._calculate_overlap(response, contexts)

        # Signal 2: Specificity
        specificity_score = self._calculate_specificity(response)

        # Signal 3: Hedging (inverse - less hedging = more confident)
        hedging_score = 1.0 - self._calculate_hedging(response)

        # Signal 4: Citation presence
        citation_score = self._check_citations(response)

        # Combined confidence (weighted average)
        confidence = (
            overlap_score * 0.4 +
            specificity_score * 0.2 +
            hedging_score * 0.2 +
            citation_score * 0.2
        )

        return {
            "score": round(confidence, 3),
            "confidence_level": self._get_confidence_level(confidence),
            "signals": {
                "context_overlap": round(overlap_score, 3),
                "specificity": round(specificity_score, 3),
                "low_hedging": round(hedging_score, 3),
                "has_citations": round(citation_score, 3)
            },
            "recommendation": self._get_recommendation(confidence),
            "hallucination_risk": "low" if confidence >= 0.7 else "medium" if confidence >= 0.5 else "high"
        }

    def _calculate_overlap(self, response: str, contexts: list[str]) -> float:
        """Calculate word overlap between response and contexts."""
        if not contexts:
            return 0.5  # Neutral if no context

        response_words = set(response.lower().split())
        context_words = set()
        for context in contexts:
            context_words.update(context.lower().split())

        if not response_words:
            return 0.0

        overlap = len(response_words & context_words) / len(response_words)
        return min(1.0, overlap * 1.2)  # Boost slightly, cap at 1.0

    def _calculate_specificity(self, response: str) -> float:
        """Calculate specificity (more specific = higher score)."""
        words = response.split()
        word_count = len(words)

        if word_count < 5:
            return 0.3  # Too short, likely vague
        elif word_count > 100:
            return 0.7  # Maybe too long, but specific

        # Check for numbers, dates, names (specific info)
        import re
        numbers = len(re.findall(r'\d+', response))

        # Simple heuristic
        specificity = min(1.0, 0.5 + (numbers * 0.1) + (word_count / 200))
        return specificity

    def _calculate_hedging(self, response: str) -> float:
        """Calculate hedging ratio (higher = more uncertain)."""
        response_lower = response.lower()
        hedge_count = sum(1 for word in self.HEDGING_WORDS if word in response_lower)

        words = response.split()
        if not words:
            return 0.0

        hedging_ratio = hedge_count / len(words)
        return min(1.0, hedging_ratio * 20)  # Scale up, cap at 1.0

    def _check_citations(self, response: str) -> float:
        """Check for citation markers."""
        import re

        # Check for various citation formats
        patterns = [
            r'\[\d+\]',  # [1]
            r'Section \d+',  # Section 5
            r'\(.*?\d{4}.*?\)',  # (Author 2023)
        ]

        has_citations = any(re.search(p, response) for p in patterns)
        return 1.0 if has_citations else 0.0

    def _get_confidence_level(self, score: float) -> str:
        """Convert score to confidence level."""
        if score >= 0.8:
            return "very high"
        elif score >= 0.6:
            return "high"
        elif score >= 0.4:
            return "medium"
        elif score >= 0.2:
            return "low"
        else:
            return "very low"

    def _get_recommendation(self, score: float) -> str:
        """Get recommendation based on confidence."""
        if score >= 0.8:
            return "✅ Very high confidence - response appears well-grounded"
        elif score >= 0.6:
            return "👍 High confidence - likely accurate but verify important facts"
        elif score >= 0.4:
            return "⚠️ Medium confidence - manual review recommended"
        else:
            return "❌ Low confidence - high hallucination risk, verify before use"


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test():
        plugin = HallucinationConfidencePlugin()

        # Test 1: High confidence (specific, from context)
        result1 = await plugin.calculate_async(
            query="What is the return policy?",
            response="According to Section 5.2, the return policy is 30 days with full refund for items in original condition.",
            contexts=["Section 5.2: Return policy is 30 days with full refund for items in original condition."]
        )
        print("\nHigh confidence:")
        print(f"  Score: {result1['score']}")
        print(f"  Level: {result1['confidence_level']}")
        print(f"  Signals: {result1['signals']}")

        # Test 2: Low confidence (hedging, vague)
        result2 = await plugin.calculate_async(
            query="What is the return policy?",
            response="Maybe you can return it. I think it might be possible, but I'm not sure.",
            contexts=["Section 5.2: Return policy is 30 days."]
        )
        print("\nLow confidence:")
        print(f"  Score: {result2['score']}")
        print(f"  Risk: {result2['hallucination_risk']}")
        print(f"  Recommendation: {result2['recommendation']}")

    asyncio.run(test())
