"""Confidence scoring system for RAGLint metrics.

This module provides confidence calculation for metric scores,
helping identify when results are uncertain and may need human review.
"""

import statistics


class ConfidenceScorer:
    """Calculate confidence scores for metric evaluations."""

    def __init__(self, num_samples: int = 3):
        """
        Initialize confidence scorer.

        Args:
            num_samples: Number of repeated evaluations for consistency check
        """
        self.num_samples = num_samples

    def calculate_confidence(self, scores: list[float]) -> tuple[float, float]:
        """
        Calculate confidence from multiple score samples.

        Args:
            scores: List of scores from repeated evaluations

        Returns:
            Tuple of (average_score, confidence_score)
            confidence_score: 0.0-1.0 where 1.0 = very confident
        """
        if not scores:
            return 0.0, 0.0

        # Calculate average
        avg_score = statistics.mean(scores)

        # Calculate variance (low variance = high confidence)
        if len(scores) == 1:
            variance = 0.0
        else:
            variance = statistics.variance(scores)

        # Convert variance to confidence (inverse relationship)
        # Low variance (< 0.01) = high confidence (> 0.9)
        confidence = max(0.0, min(1.0, 1.0 - (variance * 10)))

        return avg_score, confidence

    def is_high_confidence(self, confidence: float, threshold: float = 0.85) -> bool:
        """
        Check if confidence meets threshold.

        Args:
            confidence: Confidence score 0.0-1.0
            threshold: Minimum confidence required

        Returns:
            True if confidence >= threshold
        """
        return confidence >= threshold

    def classify_confidence(self, confidence: float) -> str:
        """
        Classify confidence level.

        Args:
            confidence: Confidence score 0.0-1.0

        Returns:
            String classification: "VERY_HIGH", "HIGH", "MEDIUM", "LOW", "VERY_LOW"
        """
        if confidence >= 0.95:
            return "VERY_HIGH"
        elif confidence >= 0.85:
            return "HIGH"
        elif confidence >= 0.70:
            return "MEDIUM"
        elif confidence >= 0.50:
            return "LOW"
        else:
            return "VERY_LOW"


class ConsensusScorer:
    """Calculate consensus between multiple models or evaluations."""

    def calculate_consensus(
        self, scores: list[tuple[str, float]], agreement_threshold: float = 0.1
    ) -> dict:
        """
        Calculate consensus from multiple model scores.

        Args:
            scores: List of (model_name, score) tuples
            agreement_threshold: Max difference for agreement (default 0.1 = 10%)

        Returns:
            Dictionary with consensus information
        """
        if len(scores) < 2:
            return {
                "consensus_score": scores[0][1] if scores else 0.0,
                "agreement": True,
                "confidence": "SINGLE_MODEL",
                "models": [s[0] for s in scores],
            }

        # Extract scores
        score_values = [s[1] for s in scores]

        # Calculate range
        min_score = min(score_values)
        max_score = max(score_values)
        score_range = max_score - min_score

        # Check agreement
        agreement = score_range <= agreement_threshold

        # Calculate consensus score (average if agreement, min if not)
        if agreement:
            consensus_score = statistics.mean(score_values)
            confidence = "HIGH"
        else:
            # Use minimum score when models disagree (conservative)
            consensus_score = min_score
            confidence = "LOW"

        return {
            "consensus_score": consensus_score,
            "agreement": agreement,
            "confidence": confidence,
            "score_range": score_range,
            "models": [s[0] for s in scores],
            "individual_scores": {s[0]: s[1] for s in scores},
        }
