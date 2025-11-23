"""
RAGAS-style Context Precision and Recall metrics.

Context Precision: What % of retrieved chunks were actually relevant/used?
Context Recall: Did we retrieve all necessary information from ground truth?
"""

from typing import List, Optional
from raglint.llm import BaseLLM


class ContextPrecisionScorer:
    """
    Measures precision of retrieved contexts.
    
    For each retrieved chunk, asks LLM: "Is this chunk relevant to answering the query?"
    Score = (relevant chunks) / (total retrieved chunks)
    
    Higher is better (fewer irrelevant chunks retrieved).
    """
    
    def __init__(self, llm: BaseLLM, prompt_template: Optional[str] = None):
        self.llm = llm
        self.prompt_template = prompt_template or """
        Query: {query}
        
        Context Chunk:
        {chunk}
        
        Task: Is this context chunk relevant for answering the query?
        
        Respond with JSON:
        {{
            "relevant": true/false,
            "reasoning": "brief explanation"
        }}
        """
    
    async def ascore(
        self, 
        query: str, 
        retrieved_contexts: List[str], 
        response: Optional[str] = None
    ) -> float:
        """
        Calculate context precision asynchronously.
        
        Args:
            query: The user's query
            retrieved_contexts: List of retrieved context chunks
            response: Optional generated response (for better precision)
            
        Returns:
            Float between 0.0 and 1.0
        """
        if not retrieved_contexts:
            return 0.0
        
        relevant_count = 0
        
        for chunk in retrieved_contexts:
            prompt = self.prompt_template.format(query=query, chunk=chunk)
            
            try:
                result = await self.llm.generate_json(prompt)
                if result.get("relevant", False):
                    relevant_count += 1
            except Exception as e:
                print(f"Context Precision error: {e}")
                # Assume relevant on error (conservative)
                relevant_count += 1
        
        return relevant_count / len(retrieved_contexts)
    
    def score(
        self, 
        query: str, 
        retrieved_contexts: List[str], 
        response: Optional[str] = None
    ) -> float:
        """Sync version of ascore."""
        import asyncio
        return asyncio.run(self.ascore(query, retrieved_contexts, response))


class ContextRecallScorer:
    """
    Measures recall of retrieved contexts.
    
    Checks if ground truth information was retrieved.
    Score = (ground truth sentences found in retrieved) / (total ground truth sentences)
    
    Higher is better (we didn't miss important information).
    """
    
    def __init__(self, llm: Optional[BaseLLM] = None, prompt_template: Optional[str] = None):
        self.llm = llm
        self.prompt_template = prompt_template or """
        Ground Truth Statement:
        {statement}
        
        Retrieved Contexts:
        {contexts}
        
        Task: Is the information from the ground truth statement present in the retrieved contexts?
        
        Respond with JSON:
        {{
            "present": true/false,
            "reasoning": "brief explanation"
        }}
        """
    
    async def ascore(
        self,
        query: str,
        retrieved_contexts: List[str],
        ground_truth_contexts: List[str]
    ) -> float:
        """
        Calculate context recall asynchronously.
        
        Args:
            query: The user's query
            retrieved_contexts: List of retrieved context chunks
            ground_truth_contexts: Ground truth contexts that should be retrieved
            
        Returns:
            Float between 0.0 and 1.0
        """
        if not ground_truth_contexts:
            return 1.0  # No ground truth to check against
        
        if not retrieved_contexts:
            return 0.0  # Retrieved nothing
        
        # If no LLM, fall back to simple string matching
        if not self.llm:
            return self._simple_recall(retrieved_contexts, ground_truth_contexts)
        
        # LLM-based recall (more accurate)
        retrieved_text = "\n\n".join(retrieved_contexts)
        statements_covered = 0
        
        # Split ground truth into sentences/statements
        statements = []
        for gt in ground_truth_contexts:
            statements.extend(self._split_sentences(gt))
        
        for statement in statements:
            prompt = self.prompt_template.format(
                statement=statement,
                contexts=retrieved_text
            )
            
            try:
                result = await self.llm.generate_json(prompt)
                if result.get("present", False):
                    statements_covered += 1
            except Exception as e:
                print(f"Context Recall error: {e}")
                # Conservative: assume not covered
                pass
        
        return statements_covered / len(statements) if statements else 1.0
    
    def score(
        self,
        query: str,
        retrieved_contexts: List[str],
        ground_truth_contexts: List[str]
    ) -> float:
        """Sync version of ascore."""
        import asyncio
        return asyncio.run(self.ascore(query, retrieved_contexts, ground_truth_contexts))
    
    def _simple_recall(
        self, 
        retrieved_contexts: List[str], 
        ground_truth_contexts: List[str]
    ) -> float:
        """Fallback: simple substring matching."""
        retrieved_text = " ".join(retrieved_contexts).lower()
        covered = 0
        
        for gt in ground_truth_contexts:
            gt_words = set(gt.lower().split())
            # If >50% of GT words appear in retrieved, consider covered
            overlap = sum(1 for w in gt_words if w in retrieved_text)
            if overlap / len(gt_words) > 0.5:
                covered += 1
        
        return covered / len(ground_truth_contexts) if ground_truth_contexts else 1.0
    
    def _split_sentences(self, text: str) -> List[str]:
        """Simple sentence splitter."""
        import re
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
