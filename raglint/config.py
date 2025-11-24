import os
from dataclasses import dataclass, field
from typing import Optional

import yaml


@dataclass
class Config:
    provider: str = "mock"  # mock, openai, ollama
    openai_api_key: Optional[str] = None
    model_name: str = "gpt-3.5-turbo"
    db_url: Optional[str] = None  # Database connection string
    slack_webhook_url: Optional[str] = None  # Slack webhook for alerts
    metrics: dict[str, bool] = field(
        default_factory=lambda: {
            "chunking": True,
            "retrieval": True,
            "semantic": True,
            "faithfulness": True,
            "context_relevance": True,
            "answer_relevance": True,
        }
    )
    thresholds: dict[str, float] = field(
        default_factory=lambda: {"faithfulness": 0.7, "relevance": 0.7}
    )
    prompts: dict[str, str] = field(
        default_factory=lambda: {
            "faithfulness": """
        You are a judge evaluating a RAG system.
        Query: {query}
        Retrieved Contexts: {context}
        System Response: {response}
        Task: Does the System Response contain information that is NOT supported by the Retrieved Contexts?
        1. Think step-by-step. Identify claims in the response and check if they exist in the context.
        2. Assign a score: 1.0 (Fully Supported) or 0.0 (Contains Hallucinations).
        Output format:
        Reasoning: <step-by-step reasoning>
        Score: <0.0 or 1.0>
        """,
            "context_relevance": """
        Query: {query}
        Context: {context}
        Task: Evaluate the relevance of the Context to the Query.
        1. Think step-by-step. Does the context contain information needed to answer the query?
        2. Assign a score between 0.0 (Irrelevant) and 1.0 (Highly Relevant).
        Output format:
        Reasoning: <step-by-step reasoning>
        Score: <0.0-1.0>
        """,
            "answer_relevance": """
        Query: {query}
        Response: {response}
        Task: Evaluate if the Response actually answers the Query.
        1. Think step-by-step. Is the response on-topic? Does it address the user's intent?
        2. Assign a score between 0.0 (Irrelevant) and 1.0 (Highly Relevant).
        Output format:
        Reasoning: <step-by-step reasoning>
        Score: <0.0-1.0>
        """,
        }
    )

    def as_dict(self) -> dict:
        """Convert config to dictionary."""
        return {
            "provider": self.provider,
            "openai_api_key": self.openai_api_key,
            "model_name": self.model_name,
            "db_url": self.db_url,
            "slack_webhook_url": self.slack_webhook_url,
            "metrics": self.metrics,
            "thresholds": self.thresholds,
            "prompts": self.prompts,
        }

    @classmethod
    def from_dict(cls, config_dict: dict) -> "Config":
        """
        Create a Config instance from a dictionary.

        Args:
            config_dict: Dictionary containing configuration values

        Returns:
            Config instance with values from the dictionary
        """
        config = cls()
        for key, value in config_dict.items():
            if hasattr(config, key):
                setattr(config, key, value)
        return config

    @classmethod
    def load(cls, path: str = "raglint.yml") -> "Config":
        config = cls()

        # Load from file if exists
        if os.path.exists(path):
            try:
                with open(path) as f:
                    data = yaml.safe_load(f) or {}

                if "provider" in data:
                    config.provider = data["provider"]
                if "openai_api_key" in data:
                    config.openai_api_key = data["openai_api_key"]
                if "model_name" in data:
                    config.model_name = data["model_name"]
                if "db_url" in data:
                    config.db_url = data["db_url"]
                if "slack_webhook_url" in data:
                    config.slack_webhook_url = data["slack_webhook_url"]
                if "metrics" in data:
                    config.metrics.update(data["metrics"])
                if "thresholds" in data:
                    config.thresholds.update(data["thresholds"])
                if "prompts" in data:
                    config.prompts.update(data["prompts"])
            except Exception as e:
                print(f"Warning: Failed to load config from {path}: {e}")

        # Environment variables override file config
        env_key = os.getenv("OPENAI_API_KEY")
        if env_key:
            config.openai_api_key = env_key

        env_slack = os.getenv("SLACK_WEBHOOK_URL")
        if env_slack:
            config.slack_webhook_url = env_slack

        return config
