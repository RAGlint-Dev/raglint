"""
Answer Completeness Plugin - Evaluates multi-part query coverage.

Ensures responses address all components of complex questions.
"""
from typing import Dict, Any, List
from raglint.plugins.interface import PluginInterface


class CompletenessPlugin(PluginInterface):
    """
    Evaluates whether answers fully address all parts of multi-part questions.
    
    Example:
        Query: "What's the price, warranty, and return policy?"
        Complete: Addresses all 3 components
        Incomplete: Only mentions price
    """
    
    name = "answer_completeness"
    version = "1.0.0"
    description = "Evaluates coverage of multi-part questions"
    
    def __init__(self, llm=None):
        self.llm = llm or self._get_mock_llm()
    
    def _get_mock_llm(self):
        from raglint.llm import MockLLM
        return MockLLM()
    
    async def calculate_async(
        self,
        query: str,
        response: str,
        contexts: List[str],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Calculate completeness score using LLM analysis.
        """
        # Use LLM to decompose query and check coverage
        prompt = f"""
Analyze if the answer fully addresses the question:

Question: {query}
Answer: {response}

Task:
1. Break down the question into individual components/sub-questions
2. For each component, check if the answer addresses it
3. Calculate what % of components are addressed

Output JSON format:
{{
    "components": ["component1", "component2", ...],
    "addressed": ["component1", ...],
    "missing": ["component2", ...],
    "coverage_percent": 75.0,
    "reasoning": "explanation"
}}
"""
        
        try:
            llm_response = await self.llm.agenerate(prompt)
            result = self._parse_llm_response(llm_response)
            
            score = result.get("coverage_percent", 50.0) / 100.0
            
            return {
                "score": round(score, 3),
                "coverage_percent": result.get("coverage_percent", 50.0),
                "components_found": len(result.get("components", [])),
                "components_addressed": len(result.get("addressed", [])),
                "missing_components": result.get("missing", []),
                "reasoning": result.get("reasoning", ""),
                "recommendation": self._get_recommendation(score)
            }
        except Exception as e:
            # Fallback: simple heuristic
            return self._fallback_analysis(query, response)
    
    def _parse_llm_response(self, response: str) -> dict:
        """Parse LLM JSON response."""
        import json
        import re
        try:
            # Extract JSON from potential markdown block or raw JSON
            json_match = re.search(r'```json\n(.*?)```', response, re.DOTALL)
            if not json_match:
                # Fallback to find any curly braces if not in markdown
                json_match = re.search(r'\{(.*?)\}', response, re.DOTALL)

            if json_match:
                json_str = json_match.group(0) # group(0) for the whole match including braces
                return json.loads(json_str)
        except (json.JSONDecodeError, AttributeError):
            # Failed to parse LLM response, return default
            return {"components": [], "missing": []}
        
        # Fallback parsing if no valid JSON was found or parsed
        coverage = 50.0
        if "coverage_percent" in response.lower():
            match = re.search(r'coverage[_\s]*percent["\s:]*(\d+\.?\d*)', response, re.IGNORECASE)
            if match:
                coverage = float(match.group(1))
        
        return {"coverage_percent": coverage, "reasoning": response}
    
    def _fallback_analysis(self, query: str, response: str) -> dict:
        """Fallback heuristic when LLM fails."""
        # Count question marks and "and" for multi-part detection
        parts = query.count("?") + query.count(" and ") + query.count(",")
        parts = max(1, parts)
        
        # Simple keyword matching
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())
        overlap = len(query_words & response_words)
        
        score = min(overlap / (len(query_words) * 0.5), 1.0)
        
        return {
            "score": round(score, 3),
            "coverage_percent": round(score * 100, 1),
            "components_found": parts,
            "components_addressed": int(parts * score),
            "missing_components": [],
            "reasoning": "Fallback heuristic based on keyword overlap",
            "recommendation": self._get_recommendation(score)
        }
    
    def _get_recommendation(self, score: float) -> str:
        """Get recommendation based on completeness score."""
        if score >= 0.9:
            return "✅ Complete answer - all components addressed"
        elif score >= 0.7:
            return "👍 Mostly complete - minor components missing"
        elif score >= 0.5:
            return "⚠️ Partially complete - several components missing"
        else:
            return "❌ Incomplete - major components not addressed"


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test():
        plugin = CompletenessPlugin()
        
        # Complete answer
        result1 = await plugin.calculate_async(
            query="What's the price and warranty?",
            response="The price is $299 and it comes with a 2-year warranty.",
            contexts=[]
        )
        print(f"\nComplete answer:")
        print(f"  Score: {result1['score']}")
        print(f"  Coverage: {result1['coverage_percent']}%")
        
        # Incomplete answer
        result2 = await plugin.calculate_async(
            query="What's the price, warranty, and return policy?",
            response="The price is $299.",
            contexts=[]
        )
        print(f"\nIncomplete answer:")
        print(f"  Score: {result2['score']}")
        print(f"  Missing: {result2['missing_components']}")
        print(f"  Recommendation: {result2['recommendation']}")
    
    asyncio.run(test())
