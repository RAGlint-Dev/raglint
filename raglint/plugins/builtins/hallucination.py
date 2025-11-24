"""
Hallucination Detector Plugin.
"""

from raglint.config import Config
from raglint.llm import LLMFactory
from raglint.plugins.interface import MetricPlugin


class HallucinationPlugin(MetricPlugin):
    """
    Detects hallucinations by checking if the answer is supported by context using an LLM.
    """

    def __init__(self):
        # Load config to get LLM settings
        config = Config.load()
        self.llm = LLMFactory.create(config.as_dict())
        self.prompt_template = """
        You are a strict fact-checking assistant.

        Context:
        {context}

        Answer:
        {answer}

        Task:
        Determine if the Answer is fully supported by the Context.
        If the Answer contains information NOT present in the Context, it is a hallucination.

        Respond with a JSON object:
        {{
            "score": <float between 0.0 and 1.0, where 1.0 means HIGH hallucination / unsupported, and 0.0 means fully supported>,
            "reasoning": "<brief explanation>"
        }}
        """

    @property
    def name(self) -> str:
        return "hallucination_score"

    @property
    def description(self) -> str:
        return (
            "Score representing probability of hallucination (0.0 = Supported, 1.0 = Hallucinated)."
        )

    @property
    def metric_type(self) -> str:
        return "generation"

    async def ascore(self, **kwargs) -> float:
        """
        Async calculation of hallucination score.
        """
        return await self._calculate_score(**kwargs)

    def score(self, **kwargs) -> float:
        """
        Sync calculation of hallucination score.
        """
        import asyncio

        return asyncio.run(self._calculate_score(**kwargs))

    async def _calculate_score(self, **kwargs) -> float:
        response = kwargs.get("response", "")
        contexts = kwargs.get("retrieved_contexts", [])

        if not response or not contexts:
            return 0.0

        context_text = "\n".join(contexts)
        prompt = self.prompt_template.format(context=context_text, answer=response)

        try:
            result = await self.llm.generate_json(prompt)
            return float(result.get("score", 0.0))
        except Exception as e:
            print(f"Error in Hallucination Plugin: {e}")
            return 0.0

    async def calculate_async(
        self, query: str, response: str, contexts: list[str], **kwargs
    ) -> dict:
        """Calculate hallucination score - wrapper for test compatibility."""
        from typing import Any

        score = await self._calculate_score(
            response=response, retrieved_contexts=contexts, **kwargs
        )
        return {
            "score": score,
            "hallucination_risk": "high" if score > 0.7 else "medium" if score > 0.4 else "low",
            "supported": score < 0.5,
        }
