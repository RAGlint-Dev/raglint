from typing import Any, Dict, List

import numpy as np


def calculate_chunk_size_distribution(chunks: List[str]) -> Dict[str, Any]:
    """
    Calculates statistics about the distribution of chunk sizes (in characters).
    """
    if not chunks:
        return {"min": 0, "max": 0, "mean": 0, "median": 0, "std": 0, "count": 0}

    sizes = [len(c) for c in chunks]
    return {
        "min": int(np.min(sizes)),
        "max": int(np.max(sizes)),
        "mean": float(np.mean(sizes)),
        "median": float(np.median(sizes)),
        "std": float(np.std(sizes)),
        "count": len(chunks),
    }


def estimate_semantic_coherence(chunk: str) -> float:
    """
    A heuristic to estimate semantic coherence.
    Currently, it just checks if the chunk ends with a sentence-ending punctuation.
    In a real implementation, this would use an NLP model.
    """
    chunk = chunk.strip()
    if not chunk:
        return 0.0

    if chunk[-1] in [".", "!", "?"]:
        return 1.0
    return 0.5  # Penalize for cut-off sentences
