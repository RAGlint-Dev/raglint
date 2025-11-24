"""
Response Diversity Scorer - Measures response variety and creativity.

Helps detect repetitive or template-like responses that may indicate
poor generation quality.
"""

from typing import Any

from raglint.plugins.interface import PluginInterface


class ResponseDiversityPlugin(PluginInterface):
    """
    Measures linguistic diversity and creativity in responses.

    Metrics:
    - Lexical diversity (unique words / total words)
    - Sentence structure variety
    - Repetition detection
    """

    name = "response_diversity"
    version = "1.0.0"
    description = "Measures response variety and linguistic diversity"

    async def calculate_async(
        self, query: str, response: str, contexts: list[str], **kwargs: Any
    ) -> dict[str, Any]:
        """Calculate diversity score."""

        words = response.split()
        if len(words) < 5:
            return {"score": 0.5, "message": "Response too short to analyze diversity"}

        # Metric 1: Lexical diversity (Type-Token Ratio)
        lexical_diversity = self._calculate_lexical_diversity(words)

        # Metric 2: Sentence variety
        sentence_variety = self._calculate_sentence_variety(response)

        # Metric 3: Repetition penalty
        repetition_score = 1.0 - self._calculate_repetition(words)

        # Combined diversity score
        diversity = lexical_diversity * 0.4 + sentence_variety * 0.3 + repetition_score * 0.3

        return {
            "score": round(diversity, 3),
            "lexical_diversity": round(lexical_diversity, 3),
            "sentence_variety": round(sentence_variety, 3),
            "repetition_detected": repetition_score < 0.7,
            "diversity_level": self._get_diversity_level(diversity),
            "recommendation": self._get_recommendation(diversity),
            "unique_words": len({w.lower() for w in words}),
            "total_words": len(words),
        }

    def _calculate_lexical_diversity(self, words: list[str]) -> float:
        """Calculate Type-Token Ratio (TTR)."""
        if not words:
            return 0.0

        unique_words = len({w.lower() for w in words})
        total_words = len(words)

        # Raw TTR
        ttr = unique_words / total_words

        # Normalize (longer texts naturally have lower TTR)
        # Simple correction: boost longer texts slightly
        if total_words > 50:
            ttr = min(1.0, ttr * 1.2)

        return ttr

    def _calculate_sentence_variety(self, response: str) -> float:
        """Estimate sentence structure variety."""
        import re

        sentences = re.split(r"[.!?]+", response)
        sentences = [s.strip() for s in sentences if s.strip()]

        if len(sentences) < 2:
            return 0.5  # Can't measure variety with 1 sentence

        # Simple heuristic: variation in sentence length
        lengths = [len(s.split()) for s in sentences]
        avg_length = sum(lengths) / len(lengths)

        # Calculate standard deviation (variation)
        variance = sum((length - avg_length) ** 2 for length in lengths) / len(lengths)
        std_dev = variance**0.5

        # Normalize (higher std_dev = more variety, but cap it)
        variety = min(1.0, std_dev / 10)

        return variety

    def _calculate_repetition(self, words: list[str]) -> float:
        """Detect repetitive patterns (n-grams)."""
        if len(words) < 6:
            return 0.0

        # Check 3-gram repetition
        trigrams = []
        for i in range(len(words) - 2):
            trigram = " ".join(words[i : i + 3]).lower()
            trigrams.append(trigram)

        if not trigrams:
            return 0.0

        unique_trigrams = len(set(trigrams))
        total_trigrams = len(trigrams)

        # Repetition ratio (higher = more repetition)
        repetition = 1.0 - (unique_trigrams / total_trigrams)

        return repetition

    def _get_diversity_level(self, score: float) -> str:
        """Convert score to diversity level."""
        if score >= 0.7:
            return "high"
        elif score >= 0.5:
            return "medium"
        elif score >= 0.3:
            return "low"
        else:
            return "very low"

    def _get_recommendation(self, score: float) -> str:
        """Get recommendation based on diversity."""
        if score >= 0.7:
            return "✅ Excellent diversity - varied and engaging response"
        elif score >= 0.5:
            return "👍 Good diversity - acceptable variety"
        elif score >= 0.3:
            return "⚠️ Low diversity - response may be repetitive or template-like"
        else:
            return "❌ Very low diversity - likely template or highly repetitive"


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test():
        plugin = ResponseDiversityPlugin()

        # Test 1: Diverse response
        result1 = await plugin.calculate_async(
            query="Tell me about the product",
            response="This laptop features a stunning display. The processor delivers exceptional performance. Storage capacity meets professional needs. Overall, it's an excellent choice for creative work.",
            contexts=[],
        )
        print("\nDiverse response:")
        print(f"  Score: {result1['score']}")
        print(f"  Level: {result1['diversity_level']}")
        print(f"  Lexical: {result1['lexical_diversity']}")

        # Test 2: Repetitive response
        result2 = await plugin.calculate_async(
            query="",
            response="The product is good. The product is nice. The product is great. The product is excellent.",
            contexts=[],
        )
        print("\nRepetitive response:")
        print(f"  Score: {result2['score']}")
        print(f"  Repetition: {result2['repetition_detected']}")
        print(f"  Recommendation: {result2['recommendation']}")

    asyncio.run(test())
