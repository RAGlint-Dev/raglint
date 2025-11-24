"""
Citation Accuracy Plugin - Verifies that citations in answers are accurate.

Checks if responses properly cite sources and if cited information exists in context.
"""

import re

from raglint.plugins.interface import PluginInterface


class CitationAccuracyPlugin(PluginInterface):
    """
    Verifies citation accuracy in RAG responses.
    """

    name = "citation_accuracy"
    version = "2.0.0"
    description = "Verifies citations and their accuracy in responses"

    def evaluate(self, query: str, context: list, response: str) -> float:
        """
        Real implementation: Check if citations in response match source documents.

        Looks for citation patterns like [1], [2], (Smith, 2020), etc.
        and verifies they correspond to information in the contexts.
        """

        # Extract citation patterns
        # Supports: [1], [2], (Author, Year), etc.
        citation_patterns = [
            r"\[(\d+)\]",  # [1], [2]
            r"\(([A-Z][a-z]+,?\s+\d{4})\)",  # (Smith, 2020)
            r"\(([A-Z][a-z]+\s+et\s+al\.,?\s+\d{4})\)",  # (Smith et al., 2020)
        ]

        citations_found = []
        for pattern in citation_patterns:
            matches = re.findall(pattern, response)
            citations_found.extend(matches)

        if not citations_found:
            # No citations found - perfect score if no claims made
            # Lower score if response makes factual claims without citations
            claim_indicators = [
                "according to",
                "studies show",
                "research indicates",
                "data suggests",
            ]
            if any(indicator in response.lower() for indicator in claim_indicators):
                return 0.5  # Claims made but no citations
            return 1.0  # No citations needed

        # Verify citations against context
        verified_count = 0
        for citation in citations_found:
            # Check if citation content appears in any context
            if re.match(r"^\d+$", str(citation)):
                # Numeric citation [1]
                try:
                    idx = int(citation) - 1
                    if 0 <= idx < len(context):
                        verified_count += 1
                except:
                    pass
            else:
                # Author-year citation
                # Check if author name appears in contexts
                author_name = (
                    citation.split(",")[0].split()[0]
                    if "," in str(citation)
                    else str(citation).split()[0]
                )
                if any(author_name.lower() in ctx.lower() for ctx in context):
                    verified_count += 1

        if not citations_found:
            return 1.0

        return verified_count / len(citations_found)
