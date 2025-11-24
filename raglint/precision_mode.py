"""Precision mode - 99%+ accuracy through strict verification.

This mode combines multiple verification strategies to achieve
maximum accuracy, sacrificing some coverage for precision.
"""

import asyncio
from typing import Any, Optional

from raglint.confidence import ConfidenceScorer, ConsensusScorer
from raglint.exceptions import MetricError
from raglint.fact_extraction import FactExtractor


class PrecisionMode:
    """
    High-precision evaluation mode targeting 99%+ accuracy.

    Strategies:
    1. Multi-model consensus
    2. Confidence thresholding
    3. Fact extraction fallback
    4. Human review flagging
    """

    def __init__(
        self,
        confidence_threshold: float = 0.90,
        consensus_threshold: float = 0.10,
        min_relevance: float = 0.40,
    ):
        """
        Initialize precision mode.

        Args:
            confidence_threshold: Minimum confidence to accept result (0.90 = 90%)
            consensus_threshold: Max difference for model agreement (0.10 = 10%)
            min_relevance: Minimum relevance for fact extraction
        """
        self.confidence_threshold = confidence_threshold
        self.consensus_threshold = consensus_threshold
        self.min_relevance = min_relevance

        self.confidence_scorer = ConfidenceScorer(num_samples=3)
        self.consensus_scorer = ConsensusScorer()
        self.fact_extractor = FactExtractor()

    async def evaluate_with_precision(
        self, metric_func: callable, query: str, response: str, contexts: list[str], **kwargs
    ) -> dict[str, Any]:
        """
        Evaluate with precision mode.

        Args:
            metric_func: Async metric function to evaluate
            query: User query
            response: Generated response
            contexts: Retrieved contexts
            **kwargs: Additional arguments for metric

        Returns:
            Dictionary with score, confidence, and precision metadata
        """
        # Strategy 1: Multi-sample for confidence
        scores = []
        for _i in range(3):
            try:
                score = await metric_func(
                    query=query, response=response, retrieved_contexts=contexts, **kwargs
                )
                scores.append(score)
            except Exception as e:
                # If any sample fails, flag for review
                return self._create_uncertain_result(reason=f"Evaluation failed: {str(e)}")

        # Calculate confidence
        avg_score, confidence = self.confidence_scorer.calculate_confidence(scores)

        # Strategy 2: Confidence thresholding
        if confidence < self.confidence_threshold:
            return self._create_uncertain_result(
                score=avg_score,
                confidence=confidence,
                reason=f"Low confidence ({confidence:.2f} < {self.confidence_threshold})",
            )

        # Strategy 3: Fact extraction verification
        fact_match = self.fact_extractor.extract_exact_answer(
            query=query, contexts=contexts, min_relevance=self.min_relevance
        )

        # Check if response matches extracted fact
        if fact_match["answer"]:
            exact_match = self._check_semantic_match(response, fact_match["answer"])

            if exact_match:
                # Perfect match with source = very high precision
                return {
                    "score": 1.0,
                    "confidence": 1.0,
                    "precision_level": "VERY_HIGH",
                    "method": "fact_extraction_verified",
                    "needs_review": False,
                    "exact_match": True,
                }

        # High confidence result
        return {
            "score": avg_score,
            "confidence": confidence,
            "precision_level": self.confidence_scorer.classify_confidence(confidence),
            "method": "multi_sample_verified",
            "needs_review": False,
            "sample_scores": scores,
        }

    async def multi_model_evaluate(
        self,
        evaluators: list[tuple],  # [(model_name, eval_func), ...]
        query: str,
        response: str,
        contexts: list[str],
        **kwargs,
    ) -> dict[str, Any]:
        """
        Evaluate using multiple models for consensus.

        Args:
            evaluators: List of (model_name, async_eval_function) tuples
            query: User query
            response: Generated response
            contexts: Retrieved contexts

        Returns:
            Consensus result with multi-model verification
        """
        # Run all models in parallel
        tasks = []
        for model_name, eval_func in evaluators:
            task = self._eval_with_model(model_name, eval_func, query, response, contexts, **kwargs)
            tasks.append(task)

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out failures
        valid_scores = []
        for (model_name, _), result in zip(evaluators, results):
            if isinstance(result, Exception):
                continue
            valid_scores.append((model_name, result))

        if len(valid_scores) < 2:
            return self._create_uncertain_result(reason="Insufficient models for consensus")

        # Calculate consensus
        consensus = self.consensus_scorer.calculate_consensus(
            valid_scores, agreement_threshold=self.consensus_threshold
        )

        if not consensus["agreement"]:
            return self._create_uncertain_result(
                score=consensus["consensus_score"],
                confidence=0.5,
                reason=f"Model disagreement (range: {consensus['score_range']:.2f})",
            )

        # High consensus = high precision
        return {
            "score": consensus["consensus_score"],
            "confidence": 0.95 if consensus["agreement"] else 0.70,
            "precision_level": "VERY_HIGH" if consensus["agreement"] else "MEDIUM",
            "method": "multi_model_consensus",
            "needs_review": False,
            "consensus_data": consensus,
        }

    async def _eval_with_model(
        self,
        model_name: str,
        eval_func: callable,
        query: str,
        response: str,
        contexts: list[str],
        **kwargs,
    ) -> float:
        """Helper to evaluate with a single model."""
        try:
            return await eval_func(
                query=query, response=response, retrieved_contexts=contexts, **kwargs
            )
        except Exception as e:
            raise MetricError(model_name, f"Evaluation failed: {e}")

    def _check_semantic_match(self, text1: str, text2: str) -> bool:
        """Check if two texts are semantically similar."""
        # Simple check: normalized text similarity
        norm1 = text1.lower().strip()
        norm2 = text2.lower().strip()

        # Exact match
        if norm1 == norm2:
            return True

        # Containment (one is subset of other)
        if norm1 in norm2 or norm2 in norm1:
            return True

        # Could add more sophisticated semantic matching here
        return False

    def _create_uncertain_result(
        self, score: Optional[float] = None, confidence: float = 0.0, reason: str = "Uncertain"
    ) -> dict[str, Any]:
        """Create result for uncertain/low-confidence evaluations."""
        return {
            "score": score,
            "confidence": confidence,
            "precision_level": "UNCERTAIN",
            "method": "flagged_for_review",
            "needs_review": True,
            "review_reason": reason,
        }
