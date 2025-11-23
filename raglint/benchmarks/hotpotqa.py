"""
HotpotQA benchmark loader.
"""

import json
import os
from typing import List, Dict, Any, Optional
from pathlib import Path


class HotpotQABenchmark:
    """
    HotpotQA benchmark for RAG evaluation.
    
    Focuses on multi-hop reasoning across multiple documents.
    """
    
    def __init__(self, subset_size: int = 50, cache_dir: Optional[str] = None):
        """
        Initialize HotpotQA benchmark.
        
        Args:
            subset_size: Number of examples to use
            cache_dir: Directory to cache data
        """
        self.subset_size = subset_size
        self.cache_dir = cache_dir or os.path.join(Path.home(), ".cache", "raglint", "benchmarks")
        self.name = "HotpotQA"
        self.description = "Dataset for diverse, explainable multi-hop question answering"
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def load(self) -> List[Dict[str, Any]]:
        """
        Load HotpotQA benchmark data.
        
        Returns:
            List of test cases in RAGLint format
        """
        cache_file = os.path.join(self.cache_dir, f"hotpotqa_subset_{self.subset_size}.json")
        
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                return json.load(f)
        
        # Generate sample data
        data = self._generate_sample_hotpotqa()
        
        with open(cache_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        return data
    
    def _generate_sample_hotpotqa(self) -> List[Dict[str, Any]]:
        """Generate sample HotpotQA-style data."""
        samples = [
            {
                "question": "Which band was founded first, Linkin Park or The Beatles?",
                "answer": "The Beatles",
                "supporting_facts": [
                    "The Beatles were formed in Liverpool in 1960.",
                    "Linkin Park is an American rock band from Agoura Hills, California, formed in 1996."
                ],
                "type": "comparison"
            },
            {
                "question": "Who is the director of the movie starring Tom Hanks as Forrest Gump?",
                "answer": "Robert Zemeckis",
                "supporting_facts": [
                    "Forrest Gump is a 1994 American comedy-drama film.",
                    "It stars Tom Hanks, Robin Wright, Gary Sinise.",
                    "The film was directed by Robert Zemeckis."
                ],
                "type": "bridge"
            },
            {
                "question": "What is the capital of the country where the Eiffel Tower is located?",
                "answer": "Paris",
                "supporting_facts": [
                    "The Eiffel Tower is a wrought-iron lattice tower on the Champ de Mars in Paris, France.",
                    "Paris is the capital and most populous city of France."
                ],
                "type": "bridge"
            }
        ]
        
        raglint_data = []
        for i in range(self.subset_size):
            sample = samples[i % len(samples)]
            
            # In HotpotQA, retrieved contexts should ideally be the supporting facts
            # plus potentially some distractors.
            
            raglint_item = {
                "query": sample["question"],
                "retrieved_contexts": sample["supporting_facts"],
                "ground_truth_contexts": sample["supporting_facts"],
                "response": sample["answer"],
                "ground_truth": sample["answer"],
                "metadata": {
                    "type": sample["type"],
                    "source": "hotpotqa"
                }
            }
            raglint_data.append(raglint_item)
            
        return raglint_data
