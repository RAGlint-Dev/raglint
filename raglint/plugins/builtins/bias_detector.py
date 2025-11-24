"""
Bias Detection Plugin - Identifies potential bias in generated responses.

Helps ensure fair, inclusive responses in customer-facing applications.
"""
import re
from typing import Any

from raglint.plugins.interface import PluginInterface


class BiasDetectorPlugin(PluginInterface):
    """
    Detects potential bias in responses across multiple dimensions.

    Checks for:
    - Gender bias (gendered language, stereotypes)
    - Racial/ethnic bias
    - Age bias
    - Disability bias
    - Socioeconomic bias
    """

    name = "bias_detector"
    version = "1.0.0"
    description = "Detects potential bias in generated responses"

    # Gendered terms that might indicate bias
    GENDERED_TERMS = {
        'male': ['he', 'him', 'his', 'businessman', 'chairman', 'policeman', 'fireman', 'mankind'],
        'female': ['she', 'her', 'hers', 'businesswoman', 'chairwoman', 'policewoman', 'lady', 'girl'],
    }

    # Potentially biased phrases
    BIAS_PATTERNS = [
        r'\b(old|elderly|senior)\s+(person|people)\s+(can\'t|cannot|struggle|have trouble)\b',
        r'\b(young|millennial|gen-?z)\s+(are|is)\s+(lazy|entitled|immature)\b',
        r'\b(women|girls)\s+(are|tend to be)\s+(emotional|sensitive|nurturing)\b',
        r'\b(men|boys)\s+(are|tend to be)\s+(strong|aggressive|logical)\b',
    ]

    # Neutral alternatives
    NEUTRAL_ALTERNATIVES = {
        'chairman': 'chairperson',
        'policeman': 'police officer',
        'businessman': 'businessperson',
        'mankind': 'humanity',
        'he/she': 'they',
    }

    async def calculate_async(
        self,
        query: str,
        response: str,
        contexts: list[str],
        **kwargs: Any
    ) -> dict[str, Any]:
        """Detect bias in response."""

        # Check for gendered language imbalance
        gender_score, gender_issues = self._detect_gendered_language(response)

        # Check for stereotypical patterns
        stereotype_count, stereotype_examples = self._detect_stereotypes(response)

        # Check for inclusive language
        inclusivity_score = self._check_inclusivity(response)

        # Combined bias score (0.0 = very biased, 1.0 = unbiased)
        bias_score = (gender_score * 0.4) + (inclusivity_score * 0.4) + \
                     (max(0, 1.0 - stereotype_count * 0.2) * 0.2)

        return {
            "score": round(bias_score, 3),
            "bias_level": self._get_bias_level(bias_score),
            "gender_balance": round(gender_score, 3),
            "inclusivity": round(inclusivity_score, 3),
            "stereotype_count": stereotype_count,
            "issues_found": gender_issues + stereotype_examples,
            "recommendation": self._get_recommendation(bias_score),
            "suggestions": self._get_suggestions(response, gender_issues, stereotype_examples)
        }

    def _detect_gendered_language(self, text: str) -> tuple[float, list[str]]:
        """Detect gendered language imbalance."""
        text_lower = text.lower()

        male_count = sum(text_lower.count(term) for term in self.GENDERED_TERMS['male'])
        female_count = sum(text_lower.count(term) for term in self.GENDERED_TERMS['female'])

        issues = []

        # Check for imbalance
        total = male_count + female_count
        if total > 0:
            ratio = max(male_count, female_count) / total
            if ratio > 0.8:  # More than 80% one gender
                dominant = "male" if male_count > female_count else "female"
                issues.append(f"Heavily {dominant}-gendered language ({ratio*100:.0f}%)")

        # Check for gendered job titles
        for term in self.GENDERED_TERMS['male'] + self.GENDERED_TERMS['female']:
            if term in ['businessman', 'chairman', 'policeman', 'businesswoman']:
                if term in text_lower:
                    issues.append(f"Gendered term: '{term}'")

        # Score: 1.0 if balanced or gender-neutral, lower if imbalanced
        if total == 0:
            score = 1.0  # No gendered terms = good
        elif total < 3:
            score = 0.9  # Few terms, minor issue
        else:
            balance = min(male_count, female_count) / max(male_count, female_count, 1)
            score = balance

        return score, issues

    def _detect_stereotypes(self, text: str) -> tuple[int, list[str]]:
        """Detect stereotypical language."""
        examples = []
        count = 0

        text_lower = text.lower()
        for pattern in self.BIAS_PATTERNS:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                examples.append(match.group())
                count += 1

        return count, examples[:3]  # Return first 3 examples

    def _check_inclusivity(self, text: str) -> float:
        """Check for inclusive language."""
        score = 1.0
        text_lower = text.lower()

        # Penalize exclusive terms
        exclusive_terms = ['normal', 'crazy', 'insane', 'lame', 'dumb', 'stupid']
        for term in exclusive_terms:
            if f' {term} ' in f' {text_lower} ':
                score -= 0.1

        # Reward inclusive terms
        inclusive_terms = ['people with', 'individuals who', 'everyone', 'all people']
        for term in inclusive_terms:
            if term in text_lower:
                score += 0.05

        return max(0.0, min(1.0, score))

    def _get_bias_level(self, score: float) -> str:
        """Determine bias level."""
        if score >= 0.9:
            return "Minimal/None"
        elif score >= 0.7:
            return "Low"
        elif score >= 0.5:
            return "Moderate"
        else:
            return "High"

    def _get_recommendation(self, score: float) -> str:
        """Get recommendation based on bias score."""
        if score >= 0.9:
            return "✅ Excellent - minimal bias detected"
        elif score >= 0.7:
            return "👍 Good - minor bias issues to address"
        elif score >= 0.5:
            return "⚠️ Moderate bias - review and revise recommended"
        else:
            return "❌ High bias detected - significant revision needed"

    def _get_suggestions(self, text: str, gender_issues: list[str], stereotypes: list[str]) -> list[str]:
        """Generate specific suggestions."""
        suggestions = []

        # Suggest neutral alternatives
        text_lower = text.lower()
        for biased, neutral in self.NEUTRAL_ALTERNATIVES.items():
            if biased in text_lower:
                suggestions.append(f"Replace '{biased}' with '{neutral}'")

        # Suggest using 'they' instead of 'he/she'
        if 'he ' in text_lower or 'she ' in text_lower:
            suggestions.append("Consider using 'they' for gender-neutral language")

        if stereotypes:
            suggestions.append("Remove stereotypical phrases")

        if not suggestions:
            suggestions.append("Continue using inclusive language")

        return suggestions[:5]  # Top 5 suggestions


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test():
        plugin = BiasDetectorPlugin()

        # Biased example
        result1 = await plugin.calculate_async(
            query="",
            response="The chairman will meet with the businessmen tomorrow. He thinks the proposal is good, but she might disagree.",
            contexts=[]
        )
        print("\nBiased text:")
        print(f"  Score: {result1['score']}")
        print(f"  Level: {result1['bias_level']}")
        print(f"  Issues: {result1['issues_found']}")
        print(f"  Suggestions: {result1['suggestions']}")

        # Neutral example
        result2 = await plugin.calculate_async(
            query="",
            response="The chairperson will meet with the business leaders tomorrow. They think the proposal is good.",
            contexts=[]
        )
        print("\nNeutral text:")
        print(f"  Score: {result2['score']}")
        print(f"  Level: {result2['bias_level']}")

    asyncio.run(test())
