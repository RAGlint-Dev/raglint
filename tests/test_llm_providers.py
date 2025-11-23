"""
Comprehensive tests for LLM providers with mocked API calls.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from raglint.llm import LLMFactory, MockLLM, OllamaLLM, OpenAI_LLM


# ==================== MockLLM Tests ====================


def test_mock_llm_generate():
    """Test MockLLM synchronous generation."""
    llm = MockLLM()
    result = llm.generate("test prompt")
    assert "MOCK" in result
    assert "1.0" in result


@pytest.mark.asyncio
async def test_mock_llm_agenerate():
    """Test MockLLM async generation."""
    llm = MockLLM()
    result = await llm.agenerate("test prompt")
    assert "MOCK" in result
    assert "1.0" in result


# ==================== OpenAI_LLM Tests ====================


@pytest.mark.asyncio
async def test_openai_llm_agenerate_success():
    """Test OpenAI async generation with mocked API."""
    with patch("openai.AsyncOpenAI") as mock_async_openai:
        # Setup mock
        mock_client = MagicMock()
        mock_async_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"

        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)

        # Test
        llm = OpenAI_LLM(api_key="test-key", model="gpt-4")
        result = await llm.agenerate("test prompt")

        assert result == "Test response"
        mock_client.chat.completions.create.assert_called_once()


@pytest.mark.asyncio
async def test_openai_llm_agenerate_error():
    """Test OpenAI async generation error handling."""
    with patch("openai.AsyncOpenAI") as mock_async_openai:
        mock_client = MagicMock()
        mock_async_openai.return_value = mock_client
        mock_client.chat.completions.create = AsyncMock(
            side_effect=Exception("API Error")
        )

        llm = OpenAI_LLM(api_key="test-key")
        result = await llm.agenerate("test prompt")

        assert result == "Error"


def test_openai_llm_generate_success():
    """Test OpenAI sync generation with mocked API."""
    with patch("openai.OpenAI") as mock_openai:
        # Setup mock
        mock_client = MagicMock()
        mock_openai.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Sync response"

        mock_client.chat.completions.create.return_value = mock_response

        # Test
        llm = OpenAI_LLM(api_key="test-key", model="gpt-3.5-turbo")
        result = llm.generate("test prompt")

        assert result == "Sync response"


def test_openai_llm_generate_error():
    """Test OpenAI sync generation error handling."""
    with patch("openai.OpenAI") as mock_openai:
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_client.chat.completions.create.side_effect = Exception("Sync API Error")

        llm = OpenAI_LLM(api_key="test-key")
        result = llm.generate("test prompt")

        assert result == "Error"


# ==================== OllamaLLM Tests ====================


@pytest.mark.asyncio
async def test_ollama_llm_agenerate_success():
    """Test Ollama async generation with mocked API."""
    with patch("aiohttp.ClientSession") as mock_session_cls:
        # Mock the session context manager
        mock_session = MagicMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        
        mock_session_cls.return_value = mock_session

        # Mock the post context manager
        mock_response = MagicMock()
        mock_response.json = AsyncMock(return_value={"response": "Ollama response"})
        mock_response.raise_for_status = MagicMock()
        
        mock_post_ctx = MagicMock()
        mock_post_ctx.__aenter__.return_value = mock_response
        mock_post_ctx.__aexit__.return_value = None
        
        mock_session.post.return_value = mock_post_ctx

        # Test
        llm = OllamaLLM(model="llama3")
        result = await llm.agenerate("test prompt")

        assert result == "Ollama response"


@pytest.mark.asyncio
async def test_ollama_llm_agenerate_error():
    """Test Ollama async generation error handling."""
    with patch("aiohttp.ClientSession") as mock_session_cls:
        # Mock the session context manager
        mock_session = MagicMock()
        mock_session.__aenter__.return_value = mock_session
        mock_session.__aexit__.return_value = None
        
        mock_session_cls.return_value = mock_session

        # Mock post to raise exception
        mock_session.post.side_effect = Exception("Connection error")

        llm = OllamaLLM(model="llama3")
        result = await llm.agenerate("test prompt")

        assert result == "Error"


def test_ollama_llm_generate_success():
    """Test Ollama sync generation with mocked API."""
    with patch("requests.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "Sync Ollama response"}
        mock_response.raise_for_status = MagicMock()
        mock_post.return_value = mock_response

        llm = OllamaLLM(model="llama3", base_url="http://localhost:11434")
        result = llm.generate("test prompt")

        assert result == "Sync Ollama response"
        mock_post.assert_called_once()


def test_ollama_llm_generate_error():
    """Test Ollama sync generation error handling."""
    with patch("requests.post") as mock_post:
        mock_post.side_effect = Exception("Connection failed")

        llm = OllamaLLM(model="llama3")
        result = llm.generate("test prompt")

        assert result == "Error"


def test_ollama_llm_custom_base_url():
    """Test Ollama with custom base URL."""
    llm = OllamaLLM(model="mistral", base_url="http://custom:8080")
    assert llm.base_url == "http://custom:8080"
    assert llm.model == "mistral"


# ==================== LLMFactory Tests ====================


def test_llm_factory_create_openai_without_key():
    """Test factory fallback to mock when OpenAI key missing."""
    config = {"provider": "openai"}
    llm = LLMFactory.create(config)
    assert isinstance(llm, MockLLM)


def test_llm_factory_create_openai_with_env_key():
    """Test factory with OpenAI key from environment."""
    import os

    os.environ["OPENAI_API_KEY"] = "test-env-key"
    config = {"provider": "openai"}

    llm = LLMFactory.create(config)
    assert isinstance(llm, OpenAI_LLM)

    del os.environ["OPENAI_API_KEY"]


def test_llm_factory_create_openai_with_config_key():
    """Test factory with OpenAI key from config."""
    config = {"provider": "openai", "openai_api_key": "test-config-key"}
    llm = LLMFactory.create(config)
    assert isinstance(llm, OpenAI_LLM)


def test_llm_factory_create_ollama():
    """Test factory creates Ollama LLM."""
    config = {"provider": "ollama", "model_name": "llama3"}
    llm = LLMFactory.create(config)
    assert isinstance(llm, OllamaLLM)
    assert llm.model == "llama3"


def test_llm_factory_create_unknown_provider():
    """Test factory defaults to mock for unknown provider."""
    config = {"provider": "unknown"}
    llm = LLMFactory.create(config)
    assert isinstance(llm, MockLLM)
