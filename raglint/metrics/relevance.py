from typing import Optional, Union

from ..llm import BaseLLM, MockLLM


class AnswerRelevanceScorer:
    def __init__(self, llm: Optional[BaseLLM] = None, prompt_template: Optional[str] = None):
        self.llm = llm if llm else MockLLM()
        self.prompt_template = prompt_template

    def score(self, query: str, response: str) -> tuple[float, str]:
        """
        Scores answer relevance: Is the response relevant to the query?
        Returns (score, reasoning).
        """
        prompt = self._build_prompt(query, response)
        result = self.llm.generate(prompt)
        return self._parse_response(result)

    async def ascore(self, query: str, response: str) -> tuple[float, str]:
        """
        Async version of score().
        Returns (score, reasoning).
        """
        prompt = self._build_prompt(query, response)
        result = await self.llm.agenerate(prompt)
        return self._parse_response(result)

    def _build_prompt(self, query: str, response: str) -> str:
        if self.prompt_template:
            return self.prompt_template.format(query=query, response=response)

        return f"""
        You are a judge evaluating a RAG system.

        Query: {query}

        System Response:
        {response}

        Task:
        Does the System Response directly answer the Query?
        Ignore whether the answer is factually correct based on context. Focus ONLY on relevance.

        1. Think step-by-step.
        2. Assign a score:
           - 1.0: Directly answers the question.
           - 0.5: Partially answers or is vague.
           - 0.0: Irrelevant or refuses to answer.

        Output format:
        Reasoning: <step-by-step reasoning>
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
                    score = float(score_str)
                if "Reasoning:" in line:
                    reasoning = line.split("Reasoning:")[1].strip()
            return score, reasoning
        except:
            return 0.0, "Failed to parse LLM response"


class ContextRelevanceScorer:
    def __init__(self, llm: Optional[BaseLLM] = None, prompt_template: Optional[str] = None):
        self.llm = llm if llm else MockLLM()
        self.prompt_template = prompt_template

    def score(self, query: str, context: Union[str, list[str]]) -> tuple[float, str]:
        """
        Scores context relevance: Is the retrieved context relevant to the query?
        Returns (score, reasoning).
        """
        if isinstance(context, list):
            context = "\n".join(context)

        prompt = self._build_prompt(query, context)
        result = self.llm.generate(prompt)
        return self._parse_response(result)

    async def ascore(self, query: str, context: Union[str, list[str]]) -> tuple[float, str]:
        """
        Async version of score().
        Returns (score, reasoning).
        """
        if isinstance(context, list):
            context = "\n".join(context)

        prompt = self._build_prompt(query, context)
        result = await self.llm.agenerate(prompt)
        return self._parse_response(result)

    def _build_prompt(self, query: str, context: str) -> str:
        if self.prompt_template:
            return self.prompt_template.format(query=query, context=context)

        return f"""
        You are a judge evaluating a RAG system.

        Query: {query}

        Retrieved Context:
        {context}

        Task:
        Does the Retrieved Context contain information relevant to answering the Query?

        1. Think step-by-step.
        2. Assign a score:
           - 1.0: Highly relevant.
           - 0.5: Somewhat relevant.
           - 0.0: Irrelevant.

        Output format:
        Reasoning: <step-by-step reasoning>
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
                    score = float(score_str)
                if "Reasoning:" in line:
                    reasoning = line.split("Reasoning:")[1].strip()
            return score, reasoning
        except:
            return 0.0, "Failed to parse LLM response"
