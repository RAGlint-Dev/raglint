"""
Readability Scorer Plugin - Measures text readability using standard metrics.

Useful for ensuring responses are appropriate for target audience education level.
"""

import re
from typing import Any

from raglint.plugins.interface import PluginInterface


class ReadabilityPlugin(PluginInterface):
    """
    Calculates readability scores using multiple standard formulas.

    Metrics:
    - Flesch Reading Ease (0-100, higher = easier)
    - Flesch-Kincaid Grade Level (grade level required)
    - SMOG Index (Simple Measure of Gobbledygook)
    """

    name = "readability"
    version = "1.0.0"
    description = "Measures text readability for target audience appropriateness"

    async def calculate_async(
        self, query: str, response: str, contexts: list[str], **kwargs: Any
    ) -> dict[str, Any]:
        """Calculate readability metrics."""

        # Parse text
        sentences = self._count_sentences(response)
        words = self._count_words(response)
        syllables = self._count_syllables(response)

        # Avoid division by zero
        if sentences == 0 or words == 0:
            return {
                "error": "Text too short to analyze",
                "flesch_reading_ease": 0,
                "grade_level": 0,
            }

        # Calculate metrics
        flesch = self._flesch_reading_ease(sentences, words, syllables)
        grade_level = self._flesch_kincaid_grade(sentences, words, syllables)
        smog = self._smog_index(sentences, self._count_complex_words(response))

        return {
            "flesch_reading_ease": round(flesch, 1),
            "flesch_kincaid_grade": round(grade_level, 1),
            "smog_index": round(smog, 1),
            "readability_interpretation": self._interpret_flesch(flesch),
            "appropriate_for": self._get_audience(grade_level),
            "recommendation": self._get_recommendation(grade_level, flesch),
            "stats": {
                "sentences": sentences,
                "words": words,
                "syllables": syllables,
                "avg_words_per_sentence": round(words / sentences, 1),
                "avg_syllables_per_word": round(syllables / words, 2),
            },
        }

    def _count_sentences(self, text: str) -> int:
        """Count sentences in text."""
        sentences = re.split(r"[.!?]+", text)
        return len([s for s in sentences if s.strip()])

    def _count_words(self, text: str) -> int:
        """Count words in text."""
        words = re.findall(r"\b\w+\b", text)
        return len(words)

    def _count_syllables(self, text: str) -> int:
        """Estimate syllables using simple heuristic."""
        text = text.lower()
        syllables = 0
        words = re.findall(r"\b\w+\b", text)

        for word in words:
            # Count vowel groups
            vowel_groups = re.findall(r"[aeiouy]+", word)
            count = len(vowel_groups)

            # Adjust for silent e
            if word.endswith("e") and count > 1:
                count -= 1

            # Minimum 1 syllable per word
            syllables += max(1, count)

        return syllables

    def _count_complex_words(self, text: str) -> int:
        """Count words with 3+ syllables."""
        words = re.findall(r"\b\w+\b", text.lower())
        complex_count = 0

        for word in words:
            vowel_groups = re.findall(r"[aeiouy]+", word)
            if len(vowel_groups) >= 3:
                complex_count += 1

        return complex_count

    def _flesch_reading_ease(self, sentences: int, words: int, syllables: int) -> float:
        """
        Flesch Reading Ease: 206.835 - 1.015(words/sentences) - 84.6(syllables/words)

        90-100: Very Easy (5th grade)
        60-70: Standard (8th-9th grade)
        0-30: Very Difficult (college graduate)
        """
        return 206.835 - 1.015 * (words / sentences) - 84.6 * (syllables / words)

    def _flesch_kincaid_grade(self, sentences: int, words: int, syllables: int) -> float:
        """
        Flesch-Kincaid Grade Level: 0.39(words/sentences) + 11.8(syllables/words) - 15.59

        Returns US grade level required to understand text.
        """
        return 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59

    def _smog_index(self, sentences: int, complex_words: int) -> float:
        """
        SMOG (Simple Measure of Gobbledygook): 1.0430 * sqrt(complex_words * 30/sentences) + 3.1291

        Estimates years of education needed.
        """
        import math

        if sentences == 0:
            return 0
        return 1.0430 * math.sqrt(complex_words * 30 / sentences) + 3.1291

    def _interpret_flesch(self, score: float) -> str:
        """Interpret Flesch Reading Ease score."""
        if score >= 90:
            return "Very Easy (5th grade)"
        elif score >= 80:
            return "Easy (6th grade)"
        elif score >= 70:
            return "Fairly Easy (7th grade)"
        elif score >= 60:
            return "Standard (8th-9th grade)"
        elif score >= 50:
            return "Fairly Difficult (10th-12th grade)"
        elif score >= 30:
            return "Difficult (College)"
        else:
            return "Very Difficult (College graduate)"

    def _get_audience(self, grade_level: float) -> str:
        """Get appropriate audience for grade level."""
        if grade_level <= 6:
            return "Elementary school students"
        elif grade_level <= 9:
            return "Middle school students, general public"
        elif grade_level <= 12:
            return "High school students, educated adults"
        elif grade_level <= 16:
            return "College students, professionals"
        else:
            return "Academics, specialists"

    def _get_recommendation(self, grade_level: float, flesch: float) -> str:
        """Get recommendation based on scores."""
        if grade_level <= 8 and flesch >= 60:
            return "✅ Excellent - accessible to general audience"
        elif grade_level <= 12:
            return "👍 Good - appropriate for most users"
        elif grade_level <= 16:
            return "⚠️ Complex - consider simplifying for broader audience"
        else:
            return "❌ Very complex - simplify unless targeting specialists"


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test():
        plugin = ReadabilityPlugin()

        # Simple text
        result1 = await plugin.calculate_async(
            query="", response="The cat sat on the mat. It was warm. The cat liked it.", contexts=[]
        )
        print("\nSimple text:")
        print(f"  Grade level: {result1['flesch_kincaid_grade']}")
        print(f"  Flesch: {result1['flesch_reading_ease']}")
        print(f"  Interpretation: {result1['readability_interpretation']}")

        # Complex text
        result2 = await plugin.calculate_async(
            query="",
            response="The implementation of sophisticated algorithmic methodologies necessitates comprehensive understanding of computational complexity theory and asymptotic analysis.",
            contexts=[],
        )
        print("\nComplex text:")
        print(f"  Grade level: {result2['flesch_kincaid_grade']}")
        print(f"  Recommendation: {result2['recommendation']}")

    asyncio.run(test())
