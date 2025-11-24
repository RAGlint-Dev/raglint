"""
CoQA (Conversational Question Answering) benchmark loader.
"""

import json
import os
from pathlib import Path
from typing import Any, Optional


class CoQABenchmark:
    """
    CoQA benchmark for RAG evaluation.

    Focuses on conversational context and history.
    """

    def __init__(self, subset_size: int = 50, cache_dir: Optional[str] = None):
        """
        Initialize CoQA benchmark.

        Args:
            subset_size: Number of examples to use
            cache_dir: Directory to cache data
        """
        self.subset_size = subset_size
        self.cache_dir = cache_dir or os.path.join(Path.home(), ".cache", "raglint", "benchmarks")
        self.name = "CoQA"
        self.description = "Conversational Question Answering Challenge"
        os.makedirs(self.cache_dir, exist_ok=True)

    def load(self) -> list[dict[str, Any]]:
        """
        Load CoQA benchmark data.

        Returns:
            List of test cases in RAGLint format
        """
        cache_file = os.path.join(self.cache_dir, f"coqa_subset_{self.subset_size}.json")

        if os.path.exists(cache_file):
            with open(cache_file) as f:
                return json.load(f)

        # Generate sample data
        data = self._generate_sample_coqa()

        with open(cache_file, "w") as f:
            json.dump(data, f, indent=2)

        return data

    def _generate_sample_coqa(self) -> list[dict[str, Any]]:
        """Generate sample CoQA-style data."""
        samples = [
            {
                "story": "The Virginia governor's race was held on November 7, 2017. Democrat Ralph Northam defeated Republican Ed Gillespie.",
                "questions": [
                    {"q": "When was the race?", "a": "November 7, 2017"},
                    {"q": "Who won?", "a": "Ralph Northam"},
                    {"q": "Who did he defeat?", "a": "Ed Gillespie"},
                    {"q": "What party is he from?", "a": "Democrat"},
                ],
            },
            {
                "story": "Bill Gates founded Microsoft in 1975. He stepped down as CEO in 2000.",
                "questions": [
                    {"q": "Who founded Microsoft?", "a": "Bill Gates"},
                    {"q": "When?", "a": "1975"},
                    {"q": "When did he step down?", "a": "2000"},
                ],
            },
        ]

        raglint_data = []
        count = 0

        # Flatten conversations into RAG queries
        # In a real CoQA eval, we might pass history.
        # Here we simulate RAG by concatenating history or just treating as independent queries with context.

        while count < self.subset_size:
            for sample in samples:
                history = []
                for turn in sample["questions"]:
                    if count >= self.subset_size:
                        break

                    # Construct query with some context if needed, or just raw
                    # For RAGLint, we'll just use the question and provide the story as context

                    raglint_item = {
                        "query": turn["q"],
                        "retrieved_contexts": [sample["story"]],
                        "ground_truth_contexts": [sample["story"]],
                        "response": turn["a"],
                        "ground_truth": turn["a"],
                        "metadata": {"history": history.copy(), "source": "coqa"},
                    }
                    raglint_data.append(raglint_item)

                    # Update history for next turn metadata
                    history.append({"q": turn["q"], "a": turn["a"]})
                    count += 1

        return raglint_data[: self.subset_size]
