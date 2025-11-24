"""
Context Compression Analyzer - Evaluates context efficiency and redundancy.

Helps optimize RAG systems by identifying redundant or unnecessary context.
"""

from typing import Any

from raglint.plugins.interface import PluginInterface


class ContextCompressionPlugin(PluginInterface):
    """
    Analyzes context compression opportunities.

    Metrics:
    - Redundancy between contexts
    - Context utilization (how much is actually used)
    - Compression ratio potential
    """

    name = "context_compression"
    version = "1.0.0"
    description = "Analyzes context efficiency and compression opportunities"

    async def calculate_async(
        self, query: str, response: str, contexts: list[str], **kwargs: Any
    ) -> dict[str, Any]:
        """Analyze context compression potential."""

        if not contexts:
            return {"score": 1.0, "message": "No contexts to analyze"}

        # Calculate redundancy between contexts
        redundancy = self._calculate_redundancy(contexts)

        # Calculate utilization (how much context was used in response)
        utilization = self._calculate_utilization(response, contexts)

        # Calculate compression score (1.0 = optimal, 0.0 = very inefficient)
        # High utilization + low redundancy = high score
        compression_score = (utilization * 0.6) + ((1.0 - redundancy) * 0.4)

        # Estimate potential savings
        potential_savings = self._estimate_savings(contexts, redundancy, utilization)

        return {
            "score": round(compression_score, 3),
            "redundancy_ratio": round(redundancy, 3),
            "utilization_ratio": round(utilization, 3),
            "potential_token_savings": potential_savings,
            "efficiency_level": self._get_efficiency_level(compression_score),
            "recommendation": self._get_recommendation(redundancy, utilization),
            "context_count": len(contexts),
            "avg_context_length": sum(len(c.split()) for c in contexts) // len(contexts),
        }

    def _normalize_tokens(self, text: str) -> set[str]:
        """Normalize text and return unique tokens."""
        import string

        # Remove punctuation and convert to lowercase
        text = text.translate(str.maketrans("", "", string.punctuation))
        return set(text.lower().split())

    def _calculate_redundancy(self, contexts: list[str]) -> float:
        """Calculate word redundancy across contexts."""
        if len(contexts) < 2:
            return 0.0

        # Create word sets for each context using normalization
        context_sets = [self._normalize_tokens(c) for c in contexts]

        # Calculate pairwise overlap
        overlaps = []
        for i in range(len(context_sets)):
            for j in range(i + 1, len(context_sets)):
                intersection = len(context_sets[i] & context_sets[j])
                union = len(context_sets[i] | context_sets[j])
                if union > 0:
                    overlaps.append(intersection / union)

        return sum(overlaps) / len(overlaps) if overlaps else 0.0

    def _calculate_utilization(self, response: str, contexts: list[str]) -> float:
        """Calculate how much of contexts was used in response."""
        response_words = self._normalize_tokens(response)

        # Count unique context words that appear in response
        context_words = set()
        used_words = set()

        for context in contexts:
            ctx_words = self._normalize_tokens(context)
            context_words.update(ctx_words)
            used_words.update(ctx_words & response_words)

        if not context_words:
            return 0.0

        return len(used_words) / len(context_words)

    def _estimate_savings(self, contexts: list[str], redundancy: float, utilization: float) -> int:
        """Estimate potential token savings from compression."""
        total_tokens = sum(len(c.split()) for c in contexts)

        # Savings from removing redundancy
        redundancy_savings = int(total_tokens * redundancy * 0.5)

        # Savings from removing unused content
        unused_savings = int(total_tokens * (1.0 - utilization) * 0.7)

        return redundancy_savings + unused_savings

    def _get_efficiency_level(self, score: float) -> str:
        """Convert score to efficiency level."""
        if score >= 0.8:
            return "excellent"
        elif score >= 0.6:
            return "good"
        elif score >= 0.4:
            return "fair"
        else:
            return "poor"

    def _get_recommendation(self, redundancy: float, utilization: float) -> str:
        """Get optimization recommendation."""
        if redundancy > 0.5 and utilization < 0.3:
            return "🚨 High redundancy + low utilization - aggressive compression recommended"
        elif redundancy > 0.5:
            return "⚠️ High context redundancy - consider deduplication"
        elif utilization < 0.3:
            return "⚠️ Low context utilization - reduce context size or improve retrieval"
        elif utilization >= 0.6 and redundancy < 0.3:
            return "✅ Excellent context efficiency"
        else:
            return "👍 Good context efficiency - minor optimization possible"


# Example usage
if __name__ == "__main__":
    import asyncio

    async def test():
        plugin = ContextCompressionPlugin()

        # Test 1: Redundant contexts
        result1 = await plugin.calculate_async(
            query="What is the price?",
            response="The price is $299.",
            contexts=[
                "The product costs $299 and is available now",
                "The item is priced at $299 with free shipping",
                "Price: $299, available in stock",
            ],
        )
        print("\nRedundant contexts:")
        print(f"  Score: {result1['score']}")
        print(f"  Redundancy: {result1['redundancy_ratio']}")
        print(f"  Potential savings: {result1['potential_token_savings']} tokens")
        print(f"  Recommendation: {result1['recommendation']}")

        # Test 2: Efficient contexts
        result2 = await plugin.calculate_async(
            query="Tell me about the product",
            response="The laptop has a 15-inch screen, 16GB RAM, and costs $1299.",
            contexts=["Screen size: 15 inches", "Memory: 16GB RAM", "Price: $1299"],
        )
        print("\nEfficient contexts:")
        print(f"  Score: {result2['score']}")
        print(f"  Utilization: {result2['utilization_ratio']}")
        print(f"  Level: {result2['efficiency_level']}")

    asyncio.run(test())
