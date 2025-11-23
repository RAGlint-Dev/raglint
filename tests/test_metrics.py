import pytest

from raglint.llm import MockLLM
from raglint.metrics.faithfulness import FaithfulnessScorer
from raglint.metrics.retrieval import calculate_retrieval_metrics


def test_retrieval_metrics():
    retrieved = ["apple", "banana", "cherry"]
    ground_truth = ["apple", "date"]

    metrics = calculate_retrieval_metrics(retrieved, ground_truth)

    # Precision: 1/3 (apple is relevant, banana/cherry are not)
    assert metrics["precision"] == pytest.approx(1 / 3)

    # Recall: 1/2 (apple found, date missing)
    assert metrics["recall"] == pytest.approx(1 / 2)


def test_faithfulness_scorer_mock():
    scorer = FaithfulnessScorer(llm=MockLLM())
    score, reasoning = scorer.score("query", ["context"], "response")

    assert score == 1.0
    assert "[MOCK]" in reasoning


def test_faithfulness_scorer_custom_prompt():
    template = "Custom prompt: {query} {context} {response}"
    scorer = FaithfulnessScorer(llm=MockLLM(), prompt_template=template)

    # MockLLM ignores the prompt content but we can check if it runs without error
    score, reasoning = scorer.score("q", ["c"], "r")
    assert score == 1.0
