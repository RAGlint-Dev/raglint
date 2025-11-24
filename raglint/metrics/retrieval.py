
import numpy as np


def calculate_mrr(retrieved: list[str], ground_truth: list[str]) -> float:
    """Calculates Mean Reciprocal Rank (MRR)."""
    for i, doc in enumerate(retrieved):
        if doc in ground_truth:
            return 1.0 / (i + 1)
    return 0.0


def calculate_ndcg(retrieved: list[str], ground_truth: list[str], k: int = 5) -> float:
    """Calculates Normalized Discounted Cumulative Gain (NDCG) at k."""
    dcg = 0.0
    idcg = 0.0

    # Calculate DCG
    for i, doc in enumerate(retrieved[:k]):
        rel = 1 if doc in ground_truth else 0
        dcg += rel / np.log2(i + 2)

    # Calculate IDCG (Ideal DCG)
    # In ideal ranking, all relevant docs come first
    # But we are limited by min(len(ground_truth), k)
    ideal_relevant_count = min(len(ground_truth), k)

    for i in range(ideal_relevant_count):
        idcg += 1 / np.log2(i + 2)

    if idcg == 0:
        return 0.0
    return dcg / idcg


def calculate_retrieval_metrics(retrieved: list[str], ground_truth: list[str]) -> dict[str, float]:
    """
    Calculates Precision, Recall, MRR, and NDCG@5.
    """
    retrieved_set = set(retrieved)
    ground_truth_set = set(ground_truth)

    if not ground_truth_set:
        return {"precision": 0.0, "recall": 0.0, "mrr": 0.0, "ndcg": 0.0}

    true_positives = len(retrieved_set.intersection(ground_truth_set))

    precision = true_positives / len(retrieved_set) if retrieved_set else 0.0
    recall = true_positives / len(ground_truth_set) if ground_truth_set else 0.0

    mrr = calculate_mrr(retrieved, ground_truth)
    ndcg = calculate_ndcg(retrieved, ground_truth, k=5)

    return {"precision": precision, "recall": recall, "mrr": mrr, "ndcg": ndcg}
