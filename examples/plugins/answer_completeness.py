"""
Example custom plugin: Answer Completeness Scorer

Evaluates whether the generated answer fully addresses all parts of the query.
Useful for customer support, legal Q&A, and other contexts where partial answers
are insufficient.
"""
from typing import Dict, Any
from raglint.plugins.interface import PluginInterface


class AnswerCompletenessPlugin(PluginInterface):
    """
    Measures whether the answer addresses all parts of a multi-part question.
    
    Example:
        Query: "What's the price and warranty?"
        Good: "Price is $299. Warranty is 2 years."
        Bad: "Price is $299." (missing warranty)
    """
    
    name = "answer_completeness"
    version = "1.0.0"
    description = "Evaluates if answer fully addresses all query components"
    
    def __init__(self, llm=None):
        """Initialize with optional LLM for smart evaluation."""
        self.llm = llm or self._get_default_llm()
    
    def _get_default_llm(self):
        """Get default LLM for evaluation."""
        from raglint.llm import MockLLM
        return MockLLM()
    
    async def calculate_async(
        self,
        query: str,
        response: str,
        contexts: list,
        ground_truth: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate completeness score asynchronously.
        
        Returns:
            dict: {
                "score": float (0.0-1.0),
                "reasoning": str,
                "missing_components": list
            }
        """
        # Use LLM to identify query components
        prompt = f"""
        Analyze this question and answer:
        
        Question: {query}
        Answer: {response}
        
        Task:
        1. Identify all components/sub-questions in the Question
        2. Check if the Answer addresses each component
        3. List any missing components
        4. Assign a completeness score (0.0 = incomplete, 1.0 = fully complete)
        
        Output format (JSON):
        {{
            "components": ["component1", "component2"],
            "addressed": ["component1"],
            "missing": ["component2"],
            "score": 0.5,
            "reasoning": "Missing warranty information"
        }}
        """
        
        try:
            response_text = await self.llm.agenerate(prompt)
            result = self._parse_response(response_text)
            
            return {
                "score": result.get("score", 0.5),
                "reasoning": result.get("reasoning", "Partial answer"),
                "missing_components": result.get("missing", []),
            }
        except Exception as e:
            return {
                "score": 0.5,
                "reasoning": f"Error evaluating completeness: {str(e)}",
                "missing_components": [],
            }
    
    def _parse_response(self, response: str) -> dict:
        """Parse LLM response."""
        import json
        try:
            # Try to extract JSON from response
            start = response.find("{")
            end = response.rfind("}") + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback: parse score from text
        score = 0.5
        if "score:" in response.lower():
            try:
                score_line = [l for l in response.split("\n") if "score:" in l.lower()][0]
                score = float(score_line.split(":")[-1].strip())
            except:
                pass
        
        return {"score": score, "reasoning": response, "missing": []}


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test_plugin():
        plugin = AnswerCompletenessPlugin()
        
        # Test case 1: Complete answer
        result1 = await plugin.calculate_async(
            query="What's the price and warranty?",
            response="The price is $299 and it comes with a 2-year warranty.",
            contexts=["Price: $299", "Warranty: 2 years"]
        )
        print(f"Complete answer score: {result1['score']}")  # Expect ~1.0
        
        # Test case 2: Incomplete answer
        result2 = await plugin.calculate_async(
            query="What's the price and warranty?",
            response="The price is $299.",
            contexts=["Price: $299", "Warranty: 2 years"]
        )
        print(f"Incomplete answer score: {result2['score']}")  # Expect <0.6
        print(f"Missing: {result2['missing_components']}")
    
    asyncio.run(test_plugin())
