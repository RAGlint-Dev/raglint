"""
User Intent Classifier - Classifies query intent and validates response alignment.

Helps ensure responses match what the user is actually asking for.
"""
from typing import Dict, Any, List
from raglint.plugins.interface import PluginInterface


class UserIntentPlugin(PluginInterface):
    """
    Classifies user intent and checks response alignment.
    
    Intent categories:
    - Factual (seeking information)
    - Instructional (how-to)
    - Comparison (comparing options)
    - Troubleshooting (solving problems)
    - Transactional (taking action)
    """
    
    name = "user_intent"
    version = "1.0.0"
    description = "Classifies query intent and validates response alignment"
    
    # Intent detection patterns
    INTENT_PATTERNS = {
        'factual': ['what is', 'who is', 'when', 'where', 'define', 'explain'],
        'instructional': ['how to', 'how do', 'how can', 'steps', 'guide', 'tutorial'],
        'comparison': ['compare', 'vs', 'versus', 'better', 'difference', 'which'],
        'troubleshooting': ['error', 'problem', 'issue', 'fix', 'not working', 'broken'],
        'transactional': ['buy', 'purchase', 'order', 'subscribe', 'cancel', 'refund'],
    }
    
    # Expected response characteristics
    EXPECTED_FEATURES = {
        'factual': ['definitional', 'numbers', 'dates'],
        'instructional': ['steps', 'numbered list', 'first', 'then', 'finally'],
        'comparison': ['whereas', 'while', 'but', 'however', 'better', 'worse'],
        'troubleshooting': ['try', 'check', 'ensure', 'verify', 'solution'],
        'transactional': ['click', 'go to', 'button', 'link', 'form'],
    }
    
    async def calculate_async(
        self,
        query: str,
        response: str,
        contexts: List[str],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Classify intent and check alignment."""
        
        # Detect query intent
        intent = self._classify_intent(query)
        
        # Check if response aligns with intent
        alignment = self._check_alignment(intent, response)
        
        return {
            "score": round(alignment, 3),
            "detected_intent": intent,
            "alignment_quality": "excellent" if alignment >= 0.8 else "good" if alignment >= 0.6 else "poor",
            "recommendation": self._get_recommendation(intent, alignment),
            "query_type": intent if intent != 'unclear' else "Unable to determine"
        }
    
    def _classify_intent(self, query: str) -> str:
        """Classify query intent."""
        query_lower = query.lower()
        
        # Count matches for each intent
        scores = {}
        for intent, patterns in self.INTENT_PATTERNS.items():
            score = sum(1 for pattern in patterns if pattern in query_lower)
            if score > 0:
                scores[intent] = score
        
        if not scores:
            return 'unclear'
        
        # Return intent with highest score
        return max(scores, key=scores.get)
    
    def _check_alignment(self, intent: str, response: str) -> float:
        """Check if response aligns with detected intent."""
        if intent == 'unclear':
            return 0.7  # Neutral score
        
        response_lower = response.lower()
        
        # Get expected features for this intent
        expected = self.EXPECTED_FEATURES.get(intent, [])
        
        # Count how many expected features are present
        matches = sum(1 for feature in expected if feature in response_lower)
        
        if not expected:
            return 0.7  # Neutral if no expectations
        
        # Base alignment
        base_alignment = matches / len(expected)
        
        # Boost for instructional if numbered/bullet points
        if intent == 'instructional':
            import re
            has_numbers = bool(re.search(r'\d+\.|\d+\)', response))
            if has_numbers:
                base_alignment = min(1.0, base_alignment + 0.2)
        
        # Boost for comparison if contrasting words
        if intent == 'comparison':
            contrast_words = ['but', 'however', 'while', 'whereas', 'although']
            has_contrast = any(word in response_lower for word in contrast_words)
            if has_contrast:
                base_alignment = min(1.0, base_alignment + 0.2)
        
        return min(1.0, base_alignment)
    
    def _get_recommendation(self, intent: str, alignment: float) -> str:
        """Get recommendation based on intent and alignment."""
        if alignment >= 0.8:
            return f"✅ Excellent alignment with {intent} intent"
        elif alignment >= 0.6:
            return f"👍 Good alignment with {intent} intent"
        elif alignment >= 0.4:
            if intent == 'instructional':
                return "⚠️ Add step-by-step instructions for how-to query"
            elif intent == 'comparison':
                return "⚠️ Add comparison language (better/worse, whereas, etc.)"
            elif intent == 'troubleshooting':
                return "⚠️ Provide actionable solutions and steps"
            else:
                return f"⚠️ Response doesn't align well with {intent} query"
        else:
            return f"❌ Poor alignment - response doesn't match {intent} intent"


# Example usage
if __name__ == "__main__":
    import asyncio
    
    async def test():
        plugin = UserIntentPlugin()
        
        # Test 1: Instructional query with good response
        result1 = await plugin.calculate_async(
            query="How do I reset my password?",
            response="1. Click 'Forgot Password'. 2. Enter your email. 3. Check your inbox for reset link.",
            contexts=[]
        )
        print(f"\nInstructional query:")
        print(f"  Intent: {result1['detected_intent']}")
        print(f"  Score: {result1['score']}")
        print(f"  Quality: {result1['alignment_quality']}")
        
        # Test 2: Comparison query with poor response
        result2 = await plugin.calculate_async(
            query="What's the difference between Plan A and Plan B?",
            response="Plan A is good.",
            contexts=[]
        )
        print(f"\nComparison query (poor response):")
        print(f"  Intent: {result2['detected_intent']}")
        print(f"  Score: {result2['score']}")
        print(f"  Recommendation: {result2['recommendation']}")
        
        # Test 3: Factual query
        result3 = await plugin.calculate_async(
            query="What is the capital of France?",
            response="The capital of France is Paris, established as the capital in 987 AD.",
            contexts=[]
        )
        print(f"\nFactual query:")
        print(f"  Intent: {result3['detected_intent']}")
        print(f"  Score: {result3['score']}")
    
    asyncio.run(test())
