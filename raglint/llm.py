"""
Async LLM providers for parallel processing.
"""

import asyncio
import os

import requests


class BaseLLM:
    """Base class for LLM providers."""

    def generate(self, prompt: str) -> str:
        """Synchronous generation (for backwards compatibility)."""
        raise NotImplementedError

    async def agenerate(self, prompt: str) -> str:
        """Async generation."""
        raise NotImplementedError


class MockLLM(BaseLLM):
    """Mock LLM for testing."""

    def generate(self, prompt: str) -> str:
        return "Reasoning: [MOCK] The response is fully supported by the context.\nScore: 1.0"

    async def agenerate(self, prompt: str) -> str:
        # Simulate async work
        await asyncio.sleep(0.01)
        return self.generate(prompt)

    async def generate_json(self, prompt: str) -> dict:
        """Generate JSON response for mock testing."""
        # Simulate async work
        await asyncio.sleep(0.01)
        return {"score": 0.1, "reasoning": "[MOCK] Low hallucination score"}


class OpenAI_LLM(BaseLLM):
    """OpenAI LLM provider with async support."""

    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo"):
        from openai import AsyncOpenAI, OpenAI

        self.client = OpenAI(api_key=api_key)
        self.async_client = AsyncOpenAI(api_key=api_key)
        self.model = model

    def generate(self, prompt: str) -> str:
        """Synchronous generation using OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return "Error"

    async def agenerate(self, prompt: str) -> str:
        """Generate text asynchronously with tracking and caching."""
        import time

        from raglint.cache import get_cache
        from raglint.tracking import get_tracker

        # Check cache first
        cache = get_cache()
        cached_response = cache.get(prompt, self.model)
        if cached_response:
            return cached_response

        try:
            start_time = time.time()

            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
            )

            latency = time.time() - start_time

            # Track cost and latency
            if hasattr(response, 'usage') and response.usage:
                tracker = get_tracker()
                tracker.record_llm_call(
                    input_tokens=response.usage.prompt_tokens,
                    output_tokens=response.usage.completion_tokens,
                    model=self.model,
                    latency=latency,
                    operation="text_generation"
                )

            result = response.choices[0].message.content.strip()

            # Cache the result
            cache.set(prompt, result, self.model)

            return result
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return "Error"

    async def generate_json(self, prompt: str) -> dict:
        """Generate JSON asynchronously with tracking."""
        import json
        import time

        from raglint.tracking import get_tracker

        try:
            start_time = time.time()

            response = await self.async_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                response_format={"type": "json_object"},
            )

            latency = time.time() - start_time

            # Track cost and latency
            if hasattr(response, 'usage') and response.usage:
                tracker = get_tracker()
                tracker.record_llm_call(
                    input_tokens=response.usage.prompt_tokens,
                    output_tokens=response.usage.completion_tokens,
                    model=self.model,
                    latency=latency,
                    operation="json_generation"
                )

            content = response.choices[0].message.content.strip()
            return json.loads(content)
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            return {}


class OllamaLLM(BaseLLM):
    """Ollama LLM provider with async support."""

    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        self.model = model
        self.base_url = base_url

    def generate(self, prompt: str) -> str:
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False},
                timeout=30  # Security: Add timeout to prevent hanging indefinitely
            )
            response.raise_for_status()
            return response.json().get("response", "").strip()
        except Exception as e:
            print(f"Ollama API Error: {e}")
            return "Error"

    async def agenerate(self, prompt: str) -> str:
        """Async generation using aiohttp."""
        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={"model": self.model, "prompt": prompt, "stream": False},
                ) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    return data.get("response", "").strip()
        except Exception as e:
            print(f"Ollama API Error: {e}")
            return "Error"

    async def generate_json(self, prompt: str) -> dict:
        """Generate JSON response using Ollama."""
        import json

        import aiohttp

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "stream": False,
                        "format": "json",
                        "options": {"temperature": 0}
                    },
                    timeout=60 # Increased timeout for local inference
                ) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
                    response_text = data.get("response", "").strip()

                    try:
                        return json.loads(response_text)
                    except json.JSONDecodeError:
                        # Fallback: try to find JSON in the text if strict mode failed
                        start = response_text.find("{")
                        end = response_text.rfind("}") + 1
                        if start != -1 and end != -1:
                            return json.loads(response_text[start:end])
                        raise

        except Exception as e:
            print(f"Ollama JSON API Error: {e}")
            return {"score": 0.0, "reasoning": f"Error: {str(e)}"}



class LLMFactory:
    """Factory for creating LLM providers."""

    @staticmethod
    def create(config_dict: dict) -> BaseLLM:
        provider = config_dict.get("provider", "mock")

        # 1. Check for built-in providers
        if provider == "openai":
            api_key = config_dict.get("openai_api_key") or os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("Warning: OpenAI provider selected but no API key found. Falling back to Mock.")
                return MockLLM()
            return OpenAI_LLM(api_key=api_key, model=config_dict.get("model_name", "gpt-3.5-turbo"))

        elif provider == "ollama":
            return OllamaLLM(
                model=config_dict.get("model_name", "llama3"),
                base_url=config_dict.get("base_url", "http://localhost:11434")
            )

        elif provider == "mock":
            return MockLLM()

        elif provider == "azure":
            from raglint.integrations.azure import AzureOpenAI_LLM
            return AzureOpenAI_LLM(
                api_key=config_dict.get("azure_api_key") or os.getenv("AZURE_OPENAI_API_KEY"),
                azure_endpoint=config_dict.get("azure_endpoint") or os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_version=config_dict.get("azure_api_version", "2023-05-15"),
                deployment_name=config_dict.get("model_name", "gpt-35-turbo")
            )

        elif provider == "bedrock":
            from raglint.integrations.bedrock import BedrockLLM
            return BedrockLLM(
                model_id=config_dict.get("model_name", "anthropic.claude-3-sonnet-20240229-v1:0"),
                region_name=config_dict.get("aws_region", "us-east-1"),
                aws_access_key_id=config_dict.get("aws_access_key_id") or os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=config_dict.get("aws_secret_access_key") or os.getenv("AWS_SECRET_ACCESS_KEY"),
            )

        # 2. Check for plugin providers
        from raglint.plugins.loader import PluginLoader
        loader = PluginLoader.get_instance()
        # Ensure plugins are loaded (lazy load if not already)
        loader.load_plugins()

        plugin = loader.get_llm_plugin(provider)
        if plugin:
            # We assume the plugin instance is ready to use
            # If plugins need config, we might need a configure() method in the interface later
            return plugin

        # 3. Fallback
        print(f"Warning: Unknown provider '{provider}'. Falling back to MockLLM.")
        return MockLLM()
