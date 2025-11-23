from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

# Lazy import to avoid torch issues
_sentence_transformer = None
_util = None

def _ensure_dependencies():
    """Lazy load sentence-transformers to avoid import issues."""
    global _sentence_transformer, _util
    if _sentence_transformer is None:
        try:
            from sentence_transformers import SentenceTransformer, util
            _sentence_transformer = SentenceTransformer
            _util = util
        except ImportError as e:
            logger.warning(f"sentence-transformers not available: {e}")
            raise ImportError(
                "sentence-transformers is required for SemanticMatcher. "
                "Install with: pip install sentence-transformers"
            )
    return _sentence_transformer, _util


class SemanticMatcher:
    """Calculate semantic similarity between texts using embeddings."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """Initialize with a sentence transformer model."""
        SentenceTransformer_cls, _ = _ensure_dependencies()
        self.model = SentenceTransformer_cls(model_name)
    
    def calculate_similarity(
        self, retrieved_contexts: List[str], ground_truth_contexts: List[str]
    ) -> float:
        """
        Calculates the maximum semantic similarity between retrieved contexts and ground truth.
        Returns a score between 0.0 and 1.0.
        """
        if not retrieved_contexts or not ground_truth_contexts:
            return 0.0

        _, util_module = _ensure_dependencies()

        # Encode all contexts
        retrieved_embeddings = self.model.encode(retrieved_contexts, convert_to_tensor=True)
        gt_embeddings = self.model.encode(ground_truth_contexts, convert_to_tensor=True)

        # Calculate cosine similarity matrix
        cosine_scores = util_module.cos_sim(retrieved_embeddings, gt_embeddings)

        # For each ground truth, find the best match in retrieved contexts
        # Max similarity for each ground truth item across all retrieved items
        max_scores_per_gt = cosine_scores.max(dim=0).values

        # Average the best matches
        mean_score = float(max_scores_per_gt.mean())

        return mean_score
