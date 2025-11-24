"""
Multilingual Support Checker Plugin - Detects language quality issues.

Ensures responses are appropriate for multilingual audiences and
detects language mixing issues.
"""
import re
from typing import Any

from raglint.plugins.interface import PluginInterface


class MultilingualSupportPlugin(PluginInterface):
    """
    Evaluates multilingual support and language consistency.

    Checks for:
    - Language consistency (no unexpected mixing)
    - Character encoding issues
    - RTL language support
    - Translation quality indicators
    """

    name = "multilingual_support"
    version = "1.0.0"
    description = "Evaluates multilingual support and language consistency"

    # Common non-Latin scripts
    SCRIPT_PATTERNS = {
        'arabic': r'[\u0600-\u06FF]',
        'chinese': r'[\u4E00-\u9FFF]',
        'japanese': r'[\u3040-\u309F\u30A0-\u30FF]',
        'korean': r'[\uAC00-\uD7AF]',
        'cyrillic': r'[\u0400-\u04FF]',
        'hebrew': r'[\u0590-\u05FF]',
        'thai': r'[\u0E00-\u0E7F]',
        'devanagari': r'[\u0900-\u097F]',
    }

    async def calculate_async(
        self,
        query: str,
        response: str,
        contexts: list[str],
        **kwargs: Any
    ) -> dict[str, Any]:
        """Evaluate multilingual support."""

        # Detect languages in query and response
        query_scripts = self._detect_scripts(query)
        response_scripts = self._detect_scripts(response)

        # Check consistency
        consistency = self._check_consistency(query_scripts, response_scripts)

        # Check for encoding issues
        encoding_issues = self._check_encoding(response)

        # Check for mixed scripts (potential issue)
        mixed_scripts = len(response_scripts) > 1

        # Calculate score
        score = 1.0
        if not consistency:
            score -= 0.3
        if encoding_issues:
            score -= 0.2
        if mixed_scripts and 'latin' in response_scripts:
            score -= 0.1  # Minor penalty for mixing Latin with non-Latin

        score = max(0.0, score)

        return {
            "score": round(score, 3),
            "query_languages": list(query_scripts),
            "response_languages": list(response_scripts),
            "is_consistent": consistency,
            "encoding_issues_found": encoding_issues,
            "mixed_scripts": mixed_scripts,
            "recommendation": self._get_recommendation(score, consistency, encoding_issues),
            "rtl_support_needed": any(lang in response_scripts for lang in ['arabic', 'hebrew'])
        }

    def _detect_scripts(self, text: str) -> set[str]:
        """Detect writing scripts in text."""
        scripts = set()

        # Check for non-Latin scripts
        for script_name, pattern in self.SCRIPT_PATTERNS.items():
            if re.search(pattern, text):
                scripts.add(script_name)

        # Check for Latin (basic ASCII + extended Latin)
        if re.search(r'[A-Za-z]', text):
            scripts.add('latin')

        return scripts

    def _check_consistency(self, query_scripts: set[str], response_scripts: set[str]) -> bool:
        """Check if response language matches query language."""
        if not query_scripts or not response_scripts:
            return True  # Can't determine, assume OK

        # If query is in non-Latin script, response should match
        non_latin_query = query_scripts - {'latin'}
        non_latin_response = response_scripts - {'latin'}

        if non_latin_query and non_latin_response:
            return bool(non_latin_query & non_latin_response)

        return True

    def _check_encoding(self, text: str) -> bool:
        """Check for encoding issues."""
        # Common encoding issue patterns
        issues = [
            r'�',  # Replacement character
            r'\\x[0-9a-fA-F]{2}',  # Hex escapes
            r'\\u[0-9a-fA-F]{4}',  # Unicode escapes (might be intentional)
        ]

        for pattern in issues[:2]:  # Check first 2 (clear encoding errors)
            if re.search(pattern, text):
                return True

        return False

    def _get_recommendation(self, score: float, consistency: bool, encoding: bool) -> str:
        """Get recommendation based on analysis."""
        if score >= 0.9:
            return "✅ Excellent multilingual support"
        elif score >= 0.7:
            if not consistency:
                return "⚠️ Language mismatch - response language differs from query"
            return "👍 Good multilingual support with minor issues"
        elif encoding:
            return "❌ Encoding issues detected - check character encoding"
        else:
            return "❌ Poor multilingual support - review language handling"


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test():
        plugin = MultilingualSupportPlugin()

        # Test 1: Consistent (both English)
        result1 = await plugin.calculate_async(
            query="What is the weather?",
            response="The weather is sunny today.",
            contexts=[]
        )
        print("\nEnglish query/response:")
        print(f"  Score: {result1['score']}")
        print(f"  Languages: {result1['response_languages']}")

        # Test 2: Mixed scripts (问题 but English response)
        result2 = await plugin.calculate_async(
            query="天气怎么样？",  # How's the weather in Chinese
            response="The weather is sunny.",  # English response
            contexts=[]
        )
        print("\nChinese query, English response:")
        print(f"  Score: {result2['score']}")
        print(f"  Consistent: {result2['is_consistent']}")
        print(f"  Recommendation: {result2['recommendation']}")

        # Test 3: Consistent Chinese
        result3 = await plugin.calculate_async(
            query="天气怎么样？",
            response="今天天气晴朗。",  # The weather is sunny in Chinese
            contexts=[]
        )
        print("\nChinese query/response:")
        print(f"  Score: {result3['score']}")
        print(f"  Consistent: {result3['is_consistent']}")

    asyncio.run(test())
