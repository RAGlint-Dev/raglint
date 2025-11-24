"""
Chunk Coverage Metric Plugin.
"""

from raglint.plugins.interface import MetricPlugin


class ChunkCoveragePlugin(MetricPlugin):
    """
    Calculates the percentage of retrieved tokens that are relevant to the answer.
    """

    @property
    def name(self) -> str:
        return "chunk_coverage"

    @property
    def description(self) -> str:
        return "Calculates the percentage of retrieved tokens relevant to the answer."

    @property
    def metric_type(self) -> str:
        return "retrieval"

    def score(self, **kwargs) -> float:
        """
        Calculate chunk coverage score.

        Args:
            retrieved_contexts (List[str]): list of retrieved chunks
            response (str): the generated answer
        """
        contexts = kwargs.get("retrieved_contexts", [])
        answer = kwargs.get("response", "")

        if not contexts or not answer:
            return 0.0

        # Simple n-gram overlap approximation for speed
        # In a real scenario, we might use embeddings or LLM

        answer_tokens = set(answer.lower().split())
        if not answer_tokens:
            return 0.0

        total_overlap = 0
        total_tokens = 0

        for ctx in contexts:
            ctx_tokens = ctx.lower().split()
            total_tokens += len(ctx_tokens)
            overlap = len(set(ctx_tokens).intersection(answer_tokens))
            total_overlap += overlap

        if total_tokens == 0:
            return 0.0

        # Normalize score
        # This is a heuristic: ratio of overlap to total context length
        # Higher means more of the context was useful
        return min(1.0, (total_overlap / total_tokens) * 5)  # Scale up a bit as exact match is rare
