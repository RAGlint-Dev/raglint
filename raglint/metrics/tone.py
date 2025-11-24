from typing import Optional

from ..llm import BaseLLM, MockLLM


class ToneScorer:
    def __init__(self, llm: Optional[BaseLLM] = None, desired_tone: str = "professional and helpful"):
        self.llm = llm if llm else MockLLM()
        self.desired_tone = desired_tone

    def score(self, query: str, response: str) -> tuple[float, str]:
        """
        Scores tone: Does the response match the desired tone?
        Returns (score, reasoning). 1.0 = Matches, 0.0 = Mismatch.
        """
        prompt = self._build_prompt(query, response)
        result = self.llm.generate(prompt)
        return self._parse_response(result)

    async def ascore(self, query: str, response: str) -> tuple[float, str]:
        """
        Async version of score().
        """
        prompt = self._build_prompt(query, response)
        result = await self.llm.agenerate(prompt)
        return self._parse_response(result)

    def _build_prompt(self, query: str, response: str) -> str:
        return f"""
        You are a communication coach evaluating the tone of a system response.

        Query: {query}

        System Response:
        {response}

        Desired Tone: {self.desired_tone}

        Task:
        Does the System Response match the Desired Tone?
        1. Analyze the word choice, formality, and empathy.
        2. Assign a score:
           - 1.0: Perfect match
           - 0.5: Acceptable but could be improved
           - 0.0: Completely inappropriate tone (e.g., rude, too casual, or robotic)

        Output format:
        Reasoning: <analysis>
        Score: <0.0, 0.5, or 1.0>
        """

    def _parse_response(self, response: str) -> tuple[float, str]:
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
