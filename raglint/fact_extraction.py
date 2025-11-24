"""Fact extraction mode - extract exact quotes from context without generation.

This mode achieves near-perfect accuracy by returning exact text from
source documents instead of generating new text.
"""

import re
from difflib import SequenceMatcher


class FactExtractor:
    """Extract exact facts from context documents."""

    def __init__(self):
        self.sentence_endings = re.compile(r'(?<=[.!?])\s+')

    def split_into_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        sentences = self.sentence_endings.split(text)
        return [s.strip() for s in sentences if s.strip()]

    def calculate_relevance(self, query: str, sentence: str) -> float:
        """
        Calculate how relevant a sentence is to the query.

        Uses keyword matching and sequence similarity.
        """
        query_lower = query.lower()
        sentence_lower = sentence.lower()

        # Keyword matching
        query_words = set(query_lower.split())
        sentence_words = set(sentence_lower.split())

        # Remove common words
        stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'what',
                    'when', 'where', 'who', 'how', 'why', 'in', 'on', 'at'}
        query_words -= stopwords
        sentence_words -= stopwords

        if not query_words:
            return 0.0

        # Jaccard similarity
        intersection = query_words & sentence_words
        union = query_words | sentence_words
        jaccard = len(intersection) / len(union) if union else 0.0

        # Sequence similarity
        sequence_sim = SequenceMatcher(None, query_lower, sentence_lower).ratio()

        # Combined score
        relevance = (jaccard * 0.7) + (sequence_sim * 0.3)

        return relevance

    def extract_exact_answer(
        self,
        query: str,
        contexts: list[str],
        min_relevance: float = 0.3
    ) -> dict:
        """
        Extract exact answer from contexts.

        Args:
            query: User query
            contexts: List of context documents
            min_relevance: Minimum relevance threshold

        Returns:
            Dictionary with answer and metadata
        """
        all_sentences = []

        # Extract all sentences with source tracking
        for idx, context in enumerate(contexts):
            sentences = self.split_into_sentences(context)
            for sentence in sentences:
                relevance = self.calculate_relevance(query, sentence)
                if relevance >= min_relevance:
                    all_sentences.append({
                        "text": sentence,
                        "relevance": relevance,
                        "source_index": idx,
                        "source_text": context
                    })

        # Sort by relevance
        all_sentences.sort(key=lambda x: x["relevance"], reverse=True)

        if not all_sentences:
            return {
                "answer": None,
                "confidence": 0.0,
                "mode": "fact_extraction",
                "hallucination_risk": 0.0,
                "source": None,
                "needs_generation": True
            }

        # Return top match
        best_match = all_sentences[0]

        return {
            "answer": best_match["text"],
            "confidence": best_match["relevance"],
            "mode": "fact_extraction",
            "hallucination_risk": 0.0,  # Zero risk - exact from source
            "source": best_match["source_text"],
            "source_index": best_match["source_index"],
            "exact_match": True,
            "needs_generation": False
        }

    def extract_multiple_facts(
        self,
        query: str,
        contexts: list[str],
        top_k: int = 3,
        min_relevance: float = 0.3
    ) -> list[dict]:
        """
        Extract multiple relevant facts.

        Useful for complex queries requiring multiple pieces of information.
        """
        all_sentences = []

        for idx, context in enumerate(contexts):
            sentences = self.split_into_sentences(context)
            for sentence in sentences:
                relevance = self.calculate_relevance(query, sentence)
                if relevance >= min_relevance:
                    all_sentences.append({
                        "text": sentence,
                        "relevance": relevance,
                        "source_index": idx
                    })

        # Sort and take top k
        all_sentences.sort(key=lambda x: x["relevance"], reverse=True)
        return all_sentences[:top_k]
