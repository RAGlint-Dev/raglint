"""
Azure OpenAI Integration for RAGLint.
"""

from raglint.llm import OpenAI_LLM


class AzureOpenAI_LLM(OpenAI_LLM):
    """
    Azure OpenAI LLM provider.
    Inherits from OpenAI_LLM but uses Azure-specific client configuration.
    """

    def __init__(
        self,
        api_key: str,
        azure_endpoint: str,
        api_version: str = "2023-05-15",
        deployment_name: str = "gpt-35-turbo",
    ):
        try:
            from openai import AsyncAzureOpenAI, AzureOpenAI
        except ImportError:
            raise ImportError("Please install openai package: pip install openai")

        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint,
        )
        self.async_client = AsyncAzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=azure_endpoint,
        )
        # In Azure, the model parameter is often the deployment name
        self.model = deployment_name

    # We inherit generate, agenerate, and generate_json from OpenAI_LLM
    # as the client interface is identical (chat.completions.create)
