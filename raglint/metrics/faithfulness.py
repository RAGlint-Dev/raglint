from typing import Optional

from ..llm import BaseLLM, MockLLM


class FaithfulnessScorer:
    def __init__(self, llm: Optional[BaseLLM] = None, prompt_template: Optional[str] = None):
        self.llm = llm if llm else MockLLM()
        self.prompt_template = prompt_template

    def score(self, query: str, retrieved_contexts: list[str], response: str) -> tuple[float, str]:
        """
        Scores faithfulness: Is the response supported by the retrieved contexts?
        Returns (score, reasoning).
        """
        prompt = self._build_prompt(query, retrieved_contexts, response)
        result = self.llm.generate(prompt)
        return self._parse_response(result)

    async def ascore(
        self, query: str, retrieved_contexts: list[str], response: str
    ) -> tuple[float, str]:
        """
        Async version of score() for parallel processing.
        Returns (score, reasoning).
        """
        prompt = self._build_prompt(query, retrieved_contexts, response)
        result = await self.llm.agenerate(prompt)
        return self._parse_response(result)

    def _build_prompt(self, query: str, retrieved_contexts: list[str], response: str) -> str:
        """Build the faithfulness evaluation prompt."""
        context_text = "\n".join(retrieved_contexts)

        if self.prompt_template:
            return self.prompt_template.format(query=query, context=context_text, response=response)
        else:
            # Fallback default prompt
            return f"""
            You are a judge evaluating a RAG system.

            Query: {query}

            Retrieved Contexts:
            {context_text}

            System Response:
            {response}

            Task:
            Does the System Response contain information that is NOT supported by the Retrieved Contexts?
            1. Think step-by-step. Identify claims in the response and check if they exist in the context.
            2. Assign a score: 1.0 (Fully Supported) or 0.0 (Contains Hallucinations).

            Output format:
            Reasoning: <step-by-step reasoning>
            Score: <0.0 or 1.0>
            """

    def _parse_response(self, response: str) -> tuple[float, str]:
        try:
            lines = response.strip().split("\n")
            score = 0.0
            reasoning = response
            for line in lines:
                if "Score:" in line:
                    score_str = line.split("Score:")[1].strip()
                    score = float(score_str)
                if "Reasoning:" in line:
                    reasoning = line.split("Reasoning:")[1].strip()
            return score, reasoning
        except:
            return 0.0, "Failed to parse LLM response"
