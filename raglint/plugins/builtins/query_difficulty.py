"""
Query Difficulty Metric Plugin.
"""

from raglint.plugins.interface import MetricPlugin


class QueryDifficultyPlugin(MetricPlugin):
    """
    Estimates the difficulty of a query based on length and specificity.
    """

    @property
    def name(self) -> str:
        return "query_difficulty"

    @property
    def description(self) -> str:
        return "Estimates query difficulty (0.0 = easy, 1.0 = hard)."

    @property
    def metric_type(self) -> str:
        return "pre_retrieval"

    def score(self, **kwargs) -> float:
        """
        Calculate query difficulty.
        
        Args:
            query (str): The user query
        """
        query = kwargs.get("query", "")
        if not query:
            return 0.0

        # Heuristics for difficulty
        score = 0.0
        
        # Length factor: Very short or very long queries are harder
        words = query.split()
        if len(words) < 3:
            score += 0.3
        elif len(words) > 20:
            score += 0.4
            
        # Specificity factor: Check for named entities (capitalized words in middle of sentence)
        # Lack of specific entities might make it vague/hard
        has_entities = any(w[0].isupper() for w in words[1:])
        if not has_entities:
            score += 0.2
            
        # Question type
        lower_q = query.lower()
        if "why" in lower_q or "how" in lower_q:
            # Reasoning questions are harder than "what" or "who"
            score += 0.2
            
        return min(1.0, score)
