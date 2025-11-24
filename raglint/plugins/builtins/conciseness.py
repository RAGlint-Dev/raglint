"""
Response Conciseness Plugin - Detects verbose or redundant answers.

Helps ensure responses are efficient and to-the-point, especially important
for mobile and chat interfaces.
"""
import re
from typing import Any

from raglint.plugins.interface import PluginInterface


class ConcisenessPlugin(PluginInterface):
    """
    Measures response conciseness and detects verbosity.

    Metrics:
    - Word efficiency (necessary words / total words)
    - Redundancy detection
    - Filler word ratio
    """

    name = "response_conciseness"
    version = "1.0.0"
    description = "Measures response efficiency and detects verbosity"

    # Common filler phrases
    FILLER_PHRASES = [
        r'\bto be honest\b',
        r'\bbasically\b',
        r'\bactually\b',
        r'\byou know\b',
        r'\bI mean\b',
        r'\bkind of\b',
        r'\bsort of\b',
        r'\bin my opinion\b',
        r'\bI think that\b',
        r'\bit goes without saying\b',
        r'\bneedless to say\b',
        r'\bat the end of the day\b',
    ]

    # Redundant patterns
    REDUNDANT_PATTERNS = [
        r'\b(very|really|extremely|incredibly) (very|really|extremely)\b',  # Double intensifiers
        r'\b(\w+) and \1\b',  # Repeated words
        r'\b(absolutely|completely|totally) (essential|necessary)\b',  # Redundant modifiers
    ]

    async def calculate_async(
        self,
        query: str,
        response: str,
        contexts: list[str],
        **kwargs: Any
    ) -> dict[str, Any]:
        """Calculate conciseness score."""

        word_count = len(response.split())
        char_count = len(response)

        # Detect filler words
        filler_count = self._count_filler_words(response)

        # Detect redundancy
        redundancy_count = self._detect_redundancy(response)

        # Calculate efficiency score
        filler_ratio = filler_count / max(word_count, 1)
        redundancy_ratio = redundancy_count / max(word_count, 1)

        # Penalty for excessive length (optimal: 30-80 words for most queries)
        length_penalty = self._calculate_length_penalty(word_count)

        # Combined score (1.0 = perfect conciseness)
        efficiency = max(0, 1.0 - filler_ratio - redundancy_ratio - length_penalty)

        return {
            "score": round(efficiency, 3),
            "word_count": word_count,
            "character_count": char_count,
            "filler_words": filler_count,
            "redundancies": redundancy_count,
            "filler_ratio": round(filler_ratio * 100, 1),
            "redundancy_ratio": round(redundancy_ratio * 100, 1),
            "verbosity_level": self._get_verbosity_level(word_count, efficiency),
            "recommendation": self._get_recommendation(efficiency, word_count),
            "improvements": self._suggest_improvements(response, filler_count, redundancy_count)
        }

    def _count_filler_words(self, text: str) -> int:
        """Count filler phrases in text."""
        count = 0
        text_lower = text.lower()

        for pattern in self.FILLER_PHRASES:
            matches = re.findall(pattern, text_lower)
            count += len(matches)

        return count

    def _detect_redundancy(self, text: str) -> float:
        """Count redundant patterns."""
        count = 0
        text_lower = text.lower()

        for pattern in self.REDUNDANT_PATTERNS:
            matches = re.findall(pattern, text_lower)
            count += len(matches)

        return count

    def _calculate_length_penalty(self, word_count: int) -> float:
        """Calculate penalty for excessive length."""
        if word_count <= 80:
            return 0.0
        elif word_count <= 120:
            return 0.1
        elif word_count <= 160:
            return 0.2
        else:
            return 0.3

    def _get_verbosity_level(self, word_count: int, efficiency: float) -> str:
        """Determine verbosity level."""
        if efficiency >= 0.8 and word_count <= 80:
            return "Concise"
        elif efficiency >= 0.6:
            return "Moderate"
        elif efficiency >= 0.4:
            return "Verbose"
        else:
            return "Very Verbose"

    def _get_recommendation(self, efficiency: float, word_count: int) -> str:
        """Get recommendation based on conciseness."""
        if efficiency >= 0.8:
            return "✅ Excellent - concise and efficient"
        elif efficiency >= 0.6:
            return "👍 Good - some minor verbosity"
        elif efficiency >= 0.4:
            return f"⚠️ Verbose - consider reducing from {word_count} words"
        else:
            return f"❌ Very verbose - needs significant editing ({word_count} words)"

    def _suggest_improvements(self, response: str, filler_count: int, redundancy_count: int) -> list[str]:
        """Suggest specific improvements."""
        improvements = []

        if filler_count > 0:
            improvements.append(f"Remove {filler_count} filler phrase(s)")

        if redundancy_count > 0:
            improvements.append(f"Eliminate {redundancy_count} redundant pattern(s)")

        word_count = len(response.split())
        if word_count > 100:
            improvements.append(f"Reduce length from {word_count} to ~50-80 words")

        # Check for passive voice (simple heuristic)
        passive_count = len(re.findall(r'\b(is|are|was|were|been|being) \w+ed\b', response))
        if passive_count > 2:
            improvements.append("Use active voice instead of passive")

        if not improvements:
            improvements.append("Response is already concise")

        return improvements


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test():
        plugin = ConcisenessPlugin()

        # Concise response
        result1 = await plugin.calculate_async(
            query="What's the return policy?",
            response="30-day money-back guarantee. Items must be in original condition.",
            contexts=[]
        )
        print("\nConcise response:")
        print(f"  Score: {result1['score']}")
        print(f"  Words: {result1['word_count']}")
        print(f"  Level: {result1['verbosity_level']}")

        # Verbose response
        result2 = await plugin.calculate_async(
            query="What's the return policy?",
            response="Well, basically, to be honest, I think that we have what you could call a very comprehensive and, you know, customer-friendly return policy. Basically, you can return items within a period of 30 days, which is to say, one month from purchase. The items, needless to say, should be in their original condition.",
            contexts=[]
        )
        print("\nVerbose response:")
        print(f"  Score: {result2['score']}")
        print(f"  Words: {result2['word_count']}")
        print(f"  Fillers: {result2['filler_words']}")
        print(f"  Improvements: {result2['improvements']}")

    asyncio.run(test())
