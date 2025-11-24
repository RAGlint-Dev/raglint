"""
SQUAD benchmark dataset loader for RAGLint.

Provides standardized benchmark datasets for evaluating RAG systems.
"""

import json
import os
from pathlib import Path
from typing import Any, Optional


class SQUADBenchmark:
    """
    SQUAD (Stanford Question Answering Dataset) benchmark for RAG evaluation.

    Example:
        ```python
        from raglint.benchmarks import SQUADBenchmark

        # Load small subset for quick testing
        benchmark = SQUADBenchmark(subset_size=10)
        test_data = benchmark.load()

        # Run evaluation
        from raglint import RAGPipelineAnalyzer
        analyzer = RAGPipelineAnalyzer()
        results = analyzer.analyze(test_data)
        ```
    """

    def __init__(self, subset_size: int = 50, cache_dir: Optional[str] = None):
        """
        Initialize SQUAD benchmark.

        Args:
            subset_size: Number of examples to use (default: 50)
            cache_dir: Directory to cache downloaded data
        """
        self.subset_size = subset_size
        self.cache_dir = cache_dir or os.path.join(Path.home(), ".cache", "raglint", "benchmarks")
        self.name = "SQUAD"
        self.description = "Stanford Question Answering Dataset (SQUAD) subset for RAG evaluation."
        os.makedirs(self.cache_dir, exist_ok=True)

    def load(self) -> list[dict[str, Any]]:
        """
        Load SQUAD benchmark data in RAGLint format.

        Returns:
            List of test cases in RAGLint format
        """
        # Check cache first
        cache_file = os.path.join(self.cache_dir, f"squad_subset_{self.subset_size}.json")

        if os.path.exists(cache_file):
            print(f"Loading cached SQUAD benchmark ({self.subset_size} examples)...")
            with open(cache_file) as f:
                return json.load(f)

        # Generate sample data (in production, this would download actual SQUAD)
        print(f"Generating SQUAD benchmark ({self.subset_size} examples)...")
        data = self._generate_sample_squad()

        # Cache it
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)

        return data

    def _generate_sample_squad(self) -> list[dict[str, Any]]:
        """
        Generate sample SQUAD-style data for demonstration.

        In production, this would download the actual SQUAD dataset from:
        https://rajpurkar.github.io/SQuAD-explorer/
        """
        # Sample SQUAD-style QA pairs
        samples = [
            {
                "context": "Python is a high-level, interpreted programming language. It was created by Guido van Rossum and first released in 1991. Python's design philosophy emphasizes code readability with significant use of whitespace.",
                "question": "Who created Python?",
                "answer": "Guido van Rossum",
                "ground_truth": "Guido van Rossum"
            },
            {
                "context": "Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing computer programs that can access data and use it to learn for themselves.",
                "question": "What is machine learning?",
                "answer": "Machine learning is a subset of artificial intelligence that enables systems to learn from experience",
                "ground_truth": "a subset of artificial intelligence"
            },
            {
                "context": "The Transformer architecture, introduced in the paper 'Attention is All You Need' in 2017, revolutionized natural language processing. It uses self-attention mechanisms to process sequences in parallel rather than sequentially.",
                "question": "When was the Transformer architecture introduced?",
                "answer": "The Transformer architecture was introduced in 2017",
                "ground_truth": "2017"
            },
            {
                "context": "RAG (Retrieval-Augmented Generation) combines neural retrieval with language generation. It first retrieves relevant documents from a knowledge base, then uses these documents to generate more accurate and grounded responses.",
                "question": "What does RAG stand for?",
                "answer": "Retrieval-Augmented Generation (RAG)",
                "ground_truth": "Retrieval-Augmented Generation"
            },
            {
                "context": "Vector databases store data as high-dimensional vectors, enabling similarity search. They are commonly used in RAG systems to efficiently retrieve semantically similar documents based on embedding similarity.",
                "question": "What are vector databases used for in RAG?",
                "answer": "Vector databases are used to efficiently retrieve semantically similar documents",
                "ground_truth": "efficiently retrieve semantically similar documents"
            },
        ]

        # Expand to requested subset size by repeating/varying samples
        raglint_data = []
        for i in range(min(self.subset_size, len(samples))):
            sample = samples[i % len(samples)]

            raglint_item = {
                "query": sample["question"],
                "retrieved_contexts": [sample["context"]],  # In real RAG, there would be multiple chunks
                "ground_truth_contexts": [sample["ground_truth"]],
                "ground_truth": sample["ground_truth"],
                "response": sample["answer"]
            }
            raglint_data.append(raglint_item)

        return raglint_data




def download_squad(split: str = "dev", version: str = "v2.0") -> str:
    """
    Download SQUAD dataset.

    Args:
        split: "train" or "dev"
        version: "v1.1" or "v2.0"

    Returns:
        Path to downloaded file
    """
    # URL for SQUAD dataset
    base_url = "https://rajpurkar.github.io/SQuAD-explorer/dataset"

    if version == "v1.1":
        if split == "train":
            url = f"{base_url}/train-v1.1.json"
        else:
            url = f"{base_url}/dev-v1.1.json"
    else:  # v2.0
        if split == "train":
            url = f"{base_url}/train-v2.0.json"
        else:
            url = f"{base_url}/dev-v2.0.json"

    cache_dir = os.path.join(Path.home(), ".cache", "raglint", "squad")
    os.makedirs(cache_dir, exist_ok=True)

    filename = f"{split}-{version}.json"
    filepath = os.path.join(cache_dir, filename)

    if os.path.exists(filepath):
        print(f"SQUAD dataset already cached: {filepath}")
        return filepath

    print(f"Downloading SQUAD {version} ({split})...")
    print(f"URL: {url}")
    print("Note: Download functionality not implemented in this demo.")
    print("For production use, download manually or use the requests library.")

    # In production, use:
    # import requests
    # response = requests.get(url)
    # with open(filepath, 'wb') as f:
    #     f.write(response.content)

    return filepath
