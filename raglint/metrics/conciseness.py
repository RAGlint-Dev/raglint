from typing import List, Optional, Tuple

from ..llm import BaseLLM, MockLLM


class ConcisenessScorer:
    def __init__(self, llm: Optional[BaseLLM] = None):
        self.llm = llm if llm else MockLLM()

    def score(self, query: str, response: str) -> Tuple[float, str]:
        """
        Scores conciseness: Is the response concise and to the point?
        Returns (score, reasoning). 1.0 = Concise, 0.0 = Verbose.
        """
        prompt = self._build_prompt(query, response)
        result = self.llm.generate(prompt)
        return self._parse_response(result)

    async def ascore(self, query: str, response: str) -> Tuple[float, str]:
        """
        Async version of score().
        """
        prompt = self._build_prompt(query, response)
        result = await self.llm.agenerate(prompt)
        return self._parse_response(result)

    def _build_prompt(self, query: str, response: str) -> str:
        return f"""
        You are an editor evaluating the conciseness of a system response.
        
        Query: {query}
        
        System Response:
        {response}
        
        Task:
        Is the System Response concise and to the point?
        1. Check for unnecessary fluff, repetition, or overly long explanations that don't add value.
        2. Assign a score:
           - 1.0: Concise and efficient
           - 0.5: A bit verbose but acceptable
           - 0.0: Excessive fluff or repetition
        
        Output format:
        Reasoning: <analysis>
        Score: <0.0, 0.5, or 1.0>
        """

    def _parse_response(self, response: str) -> Tuple[float, str]:
        try:
            lines = response.strip().split("\n")
            score = 0.0
            reasoning = response
            for line in lines:
                if "Score:" in line:
                    score_str = line.split("Score:")[1].strip()
                    try:
                        score = float(score_str)
                    except ValueError:
                        pass
                if "Reasoning:" in line:
                    reasoning = line.split("Reasoning:")[1].strip()
            return score, reasoning
        except:
            return 0.0, "Failed to parse LLM response"
