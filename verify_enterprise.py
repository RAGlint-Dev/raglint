"""
Verification script for RAGLint Enterprise Features.
Mocks external dependencies to test code paths.
"""

import os
import sys
import asyncio
from unittest.mock import MagicMock, patch

# Mock dependencies that might not be installed
from unittest.mock import MagicMock
import sys
import types

def create_mock_module(name):
    m = MagicMock()
    m.__spec__ = types.ModuleType(name).__spec__
    return m

sys.modules["openai"] = create_mock_module("openai")
sys.modules["boto3"] = create_mock_module("boto3")
sys.modules["sqlalchemy.ext.asyncio"] = create_mock_module("sqlalchemy.ext.asyncio")
sys.modules["sqlalchemy.orm"] = create_mock_module("sqlalchemy.orm")
sys.modules["sentence_transformers"] = create_mock_module("sentence_transformers")
sys.modules["chromadb"] = create_mock_module("chromadb")

# Add project root to path
sys.path.append(os.getcwd())

async def test_instrumentation():
    print("Testing Instrumentation...")
    from raglint.instrumentation import watch, Monitor
    
    monitor = Monitor()
    monitor.trace_file = "test_events.jsonl"
    
    @watch(name="test_func")
    async def my_func(x):
        return x * 2
        
    await my_func(10)
    
    if os.path.exists("test_events.jsonl"):
        print("✅ Instrumentation: Trace file created")
        os.remove("test_events.jsonl")
    else:
        print("❌ Instrumentation: Trace file NOT created")

async def test_azure_integration():
    print("\nTesting Azure Integration...")
    from raglint.integrations.azure import AzureOpenAI_LLM
    
    try:
        llm = AzureOpenAI_LLM(
            api_key="fake",
            azure_endpoint="https://fake.openai.azure.com"
        )
        print("✅ Azure: Class instantiated successfully")
    except Exception as e:
        print(f"❌ Azure: Failed to instantiate ({e})")

async def test_bedrock_integration():
    print("\nTesting Bedrock Integration...")
    from raglint.integrations.bedrock import BedrockLLM
    
    try:
        llm = BedrockLLM(
            aws_access_key_id="fake",
            aws_secret_access_key="fake"
        )
        print("✅ Bedrock: Class instantiated successfully")
    except Exception as e:
        print(f"❌ Bedrock: Failed to instantiate ({e})")

async def test_database_config():
    print("\nTesting Database Config...")
    from raglint.config import Config
    
    config = Config(db_url="postgresql+asyncpg://user:pass@localhost/db")
    if config.db_url == "postgresql+asyncpg://user:pass@localhost/db":
        print("✅ Config: db_url field exists and works")
    else:
        print("❌ Config: db_url field missing or broken")

async def main():
    await test_instrumentation()
    await test_azure_integration()
    await test_bedrock_integration()
    await test_database_config()

if __name__ == "__main__":
    asyncio.run(main())
