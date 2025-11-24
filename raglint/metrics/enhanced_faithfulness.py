"""Enhanced faithfulness metric with confidence scoring.

Extends the standard faithfulness metric with precision features
for 99%+ accuracy targeting.
"""

from typing import Any, Optional

from raglint.confidence import ConfidenceScorer
from raglint.fact_extraction import FactExtractor
from raglint.metrics.context_metrics import FaithfulnessScorer


class EnhancedFaithfulnessScorer(FaithfulnessScorer):
    """
    Faithfulness scorer with confidence and precision features.

    Adds:
    - Multi-sample scoring for confidence
    - Fact extraction verification
    - Uncertainty flagging
    """

    def __init__(self, llm, num_samples: int = 3):
        """
        Initialize enhanced scorer.

        Args:
            llm: LLM provider
            num_samples: Number of samples for confidence calculation
        """
        super().__init__(llm)
        self.num_samples = num_samples
        self.confidence_scorer = ConfidenceScorer(num_samples=num_samples)
        self.fact_extractor = FactExtractor()

    async def score_with_confidence(
        self,
        query: str,
        response: str,
        retrieved_contexts: list[str],
        ground_truth: Optional[str] = None
    ) -> dict[str, Any]:
        """
        Score faithfulness with confidence metrics.

        Returns:
            Dictionary with score, confidence, and metadata
        """
        # Multi-sample scoring
        scores = []
        for _ in range(self.num_samples):
            try:
                score = await self.ascore(
                    query=query,
                    response=response,
                    retrieved_contexts=retrieved_contexts
                )
                scores.append(score)
            except Exception as e:
                # If sampling fails, flag it
                return {
                    "score": 0.0,
                    "confidence": 0.0,
                    "needs_review": True,
                    "error": str(e)
                }

        # Calculate confidence
        avg_score, confidence = self.confidence_scorer.calculate_confidence(scores)
        confidence_level = self.confidence_scorer.classify_confidence(confidence)

        # Fact extraction verification
        fact_match = self.fact_extractor.extract_exact_answer(
            query=query,
            contexts=retrieved_contexts
        )

        # Check if response contains exact quote from source
        exact_match = False
        if fact_match["answer"]:
            response_lower = response.lower()
            fact_lower = fact_match["answer"].lower()
            exact_match = fact_lower in response_lower or response_lower in fact_lower

        result = {
            "score": avg_score,
            "confidence": confidence,
            "confidence_level": confidence_level,
            "exact_match": exact_match,
            "sample_scores": scores,
            "needs_review": confidence < 0.85 or avg_score < 0.7,
            "metric": "enhanced_faithfulness"
        }

        # Add fact match info if found
        if fact_match["answer"]:
            result["extracted_fact"] = fact_match["answer"]
            result["fact_relevance"] = fact_match["confidence"]

        return result

    async def precision_score(
        self,
        query: str,
        response: str,
        retrieved_contexts: list[str],
        confidence_threshold: float = 0.90
    ) -> dict[str, Any]:
        """
        Precision mode scoring - only return high-confidence results.

        Args:
            query: User query
            response: Generated response
            retrieved_contexts: Retrieved context documents
            confidence_threshold: Minimum confidence to accept

        Returns:
            High-precision result or flagged for review
        """
        result = await self.score_with_confidence(
            query, response, retrieved_contexts
        )

        # Check if meets precision threshold
        if result["confidence"] >= confidence_threshold and result["score"] >= 0.85:
            result["precision_level"] = "VERY_HIGH"
            result["approved"] = True
        else:
            result["precision_level"] = "UNCERTAIN"
            result["approved"] = False
            result["needs_review"] = True
            result["review_reason"] = (
                f"Confidence {result['confidence']:.2f} < {confidence_threshold} "
                f"or score {result['score']:.2f} < 0.85"
            )

        return result
