"""
Comprehensive tests for LLM providers.
"""

import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from raglint.llm import MockLLM, OllamaLLM, OpenAI_LLM, LLMFactory


# MockLLM Tests
def test_mock_llm_initialization():
    """Test MockLLM can be initialized."""
    llm = MockLLM()
    assert llm is not None


def test_mock_llm_generate():
    """Test MockLLM synchronous generation."""
    llm = MockLLM()
    result = llm.generate("Test prompt")
    assert isinstance(result, str)
    assert "MOCK" in result
    assert "Score: 1.0" in result


@pytest.mark.asyncio
async def test_mock_llm_agenerate():
    """Test MockLLM async generation."""
    llm = MockLLM()
    result = await llm.agenerate("Test prompt")
    assert isinstance(result, str)
    assert "MOCK" in result


# OllamaLLM Tests
def test_ollama_llm_initialization():
    """Test OllamaLLM initialization."""
    llm = OllamaLLM(model="llama2", base_url="http://localhost:11434")
    assert llm.model == "llama2"
    assert llm.base_url == "http://localhost:11434"


@patch('requests.post')
def test_ollama_llm_generate_success(mock_post):
    """Test OllamaLLM generation with mocked response."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"response": "This is a test response"}
    mock_post.return_value = mock_response
    
    llm = OllamaLLM()
    result = llm.generate("Test prompt")
    
    assert result == "This is a test response"
    mock_post.assert_called_once()


@patch('httpx.post')
def test_ollama_llm_generate_error(mock_post):
    """Test OllamaLLM handles errors gracefully."""
    mock_post.side_effect = Exception("Connection error")
    
    llm = OllamaLLM()
    result = llm.generate("Test prompt")
    
    assert "Error" in result or "Failed" in result


@pytest.mark.asyncio
@patch('aiohttp.ClientSession.post')
async def test_ollama_llm_agenerate(mock_post):
    """Test OllamaLLM async generation."""
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={"response": "Async response"})
    
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_response
    mock_post.return_value = mock_context
    
    llm = OllamaLLM()
    result = await llm.agenerate("Test prompt")
    
    assert result == "Async response"


# OpenAI_LLM Tests
@patch('openai.OpenAI')
def test_openai_llm_initialization(mock_openai):
    """Test OpenAI_LLM initialization."""
    llm = OpenAI_LLM(api_key="test-key", model="gpt-3.5-turbo")
    assert llm.model == "gpt-3.5-turbo"


@patch('openai.OpenAI')
def test_openai_llm_generate(mock_openai_class):
    """Test OpenAI_LLM generation."""
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock(message=MagicMock(content="OpenAI response"))]
    mock_client.chat.completions.create.return_value = mock_completion
    mock_openai_class.return_value = mock_client
    
    llm = OpenAI_LLM(api_key="test-key")
    result = llm.generate("Test prompt")
    
    assert result == "OpenAI response"


# LLMFactory Tests
def test_llm_factory_create_mock():
    """Test LLMFactory creates MockLLM."""
    llm = LLMFactory.create({"provider": "mock"})
    assert isinstance(llm, MockLLM)


def test_llm_factory_create_ollama():
    """Test LLMFactory creates OllamaLLM."""
    llm = LLMFactory.create({"provider": "ollama", "model_name": "llama2"})
    assert isinstance(llm, OllamaLLM)
    assert llm.model == "llama2"


@patch('openai.OpenAI')
def test_llm_factory_create_openai(mock_openai):
    """Test LLMFactory creates OpenAI_LLM."""
    llm = LLMFactory.create({"provider": "openai", "openai_api_key": "test-key"})
    assert isinstance(llm, OpenAI_LLM)


def test_llm_factory_invalid_provider():
    """Test LLMFactory handles invalid provider."""
    # Invalid provider should fall back to MockLLM, not raise
    llm = LLMFactory.create({"provider": "invalid_provider"})
    assert isinstance(llm, MockLLM)  # Falls back to mock


def test_llm_factory_missing_api_key():
    """Test LLMFactory validates API key for OpenAI."""
    # Missing API key should fall back to MockLLM, not raise
    llm = LLMFactory.create({"provider": "openai"})
    assert isinstance(llm, MockLLM)  # Falls back when no key
