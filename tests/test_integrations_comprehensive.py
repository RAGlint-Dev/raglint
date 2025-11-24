"""
Comprehensive tests for integrations modules.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock


# LangChain Integration Tests
def test_langchain_integration_import():
    """Test LangChain integration can be imported."""
    try:
        from raglint.integrations.langchain import RAGLintCallback
        assert RAGLintCallback is not None
    except ImportError:
        pytest.skip("LangChain not installed")


@pytest.mark.skipif(True, reason="LangChain optional dependency")
def test_langchain_callback_initialization():
    """Test LangChain callback initialization."""
    from raglint.integrations.langchain import RAGLintCallback
    callback = RAGLintCallback()
    assert callback is not None


# Haystack Integration Tests  
def test_haystack_integration_import():
    """Test Haystack integration can be imported."""
    try:
        from raglint.integrations.haystack import RAGLintComponent
        assert RAGLintComponent is not None
    except ImportError:
        pytest.skip("Haystack not installed")


# OpenAI Integration Tests
def test_openai_integration_import():
    """Test OpenAI integration can be imported."""
    try:
        from raglint.integrations.openai import track_openai
        assert track_openai is not None
    except ImportError:
        pytest.skip("OpenAI SDK not available")


@patch('openai.OpenAI')
def test_openai_wrapper_basic(mock_openai):
    """Test OpenAI wrapper basic functionality."""
    from raglint.integrations.openai import wrap_openai  # Changed from track_openai
    
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content="Test response"))]
    mock_client.chat.completions.create.return_value = mock_completion
    
    # Wrap client
    tracked_client = wrap_openai(mock_client)
    assert tracked_client is not None


# Azure Integration Tests
def test_azure_integration_import():
    """Test Azure integration can be imported."""
    from raglint.integrations.azure import AzureOpenAI_LLM
    assert AzureOpenAI_LLM is not None


def test_azure_llm_initialization():
    """Test Azure LLM initialization."""
    from raglint.integrations.azure import AzureOpenAI_LLM
    
    llm = AzureOpenAI_LLM(
        api_key="test-key",
        azure_endpoint="https://test.openai.azure.com",  # Changed from endpoint
        deployment_name="gpt-35-turbo"
    )
    assert llm.model == "gpt-35-turbo"  # Changed attribute name


# Bedrock Integration Tests
def test_bedrock_integration_import():
    """Test Bedrock integration can be imported."""
    from raglint.integrations.bedrock import BedrockLLM
    assert BedrockLLM is not None


def test_bedrock_llm_initialization():
    """Test Bedrock LLM initialization."""
    from raglint.integrations.bedrock import BedrockLLM
    
    llm = BedrockLLM(
        model_id="anthropic.claude-v2",
        region_name="us-east-1"  # Changed from region
    )
    assert llm.model_id == "anthropic.claude-v2"
