"""
AWS Bedrock Integration for RAGLint.
"""

import json
from typing import Optional

from raglint.llm import BaseLLM


class BedrockLLM(BaseLLM):
    """
    AWS Bedrock LLM provider.
    Supports Claude 3 and Titan models.
    """

    def __init__(
        self,
        model_id: str = "anthropic.claude-3-sonnet-20240229-v1:0",
        region_name: str = "us-east-1",
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
    ):
        try:
            import boto3
        except ImportError:
            raise ImportError("Please install boto3 package: pip install boto3")

        self.model_id = model_id
        self.client = boto3.client(
            service_name="bedrock-runtime",
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

    def generate(self, prompt: str) -> str:
        """Generate text using Bedrock."""
        body = json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}],
            }
        )

        try:
            response = self.client.invoke_model(
                body=body,
                modelId=self.model_id,
                accept="application/json",
                contentType="application/json",
            )
            response_body = json.loads(response.get("body").read())
            return response_body.get("content")[0].get("text")
        except Exception as e:
            print(f"Bedrock API Error: {e}")
            return "Error"

    async def agenerate(self, prompt: str) -> str:
        """Async generation (currently synchronous wrapper as boto3 is sync)."""
        # TODO: Use aioboto3 for true async support
        return self.generate(prompt)

    async def generate_json(self, prompt: str) -> dict:
        """Generate JSON response."""
        # Append instruction to force JSON
        json_prompt = f"{prompt}\n\nRespond ONLY with valid JSON."
        response = self.generate(json_prompt)
        try:
            # Attempt to find JSON in response if wrapped in markdown
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "{" in response:
                start = response.find("{")
                end = response.rfind("}") + 1
                response = response[start:end]

            return json.loads(response)
        except Exception as e:
            print(f"Bedrock JSON Parse Error: {e}")
            return {}
