"""
Tests for LLM module and providers.
"""


from raglint.llm import LLMFactory, MockLLM, OllamaLLM, OpenAI_LLM


def test_mock_llm_score():
    """Test MockLLM generates expected scores."""
    llm = MockLLM()
    result = llm.generate("Test prompt")

    assert "MOCK" in result
    assert "1.0" in result


def test_mock_llm_consistency():
    """Test MockLLM returns consistent results."""
    llm = MockLLM()
    result1 = llm.generate("Test")
    result2 = llm.generate("Test")

    assert result1 == result2


def test_llm_factory_mock():
    """Test LLM factory creates mock provider."""
    config = {"provider": "mock"}
    llm = LLMFactory.create(config)

    assert isinstance(llm, MockLLM)


def test_llm_factory_openai():
    """Test LLM factory creates OpenAI provider."""
    config = {
        "provider": "openai",
        "openai_api_key": "test-key",
        "model_name": "gpt-4o",
    }
    llm = LLMFactory.create(config)

    assert isinstance(llm, OpenAI_LLM)
    assert llm.model == "gpt-4o"


def test_llm_factory_ollama():
    """Test LLM factory creates Ollama provider."""
    config = {
        "provider": "ollama",
        "model_name": "llama2",
    }
    llm = LLMFactory.create(config)

    assert isinstance(llm, OllamaLLM)
    assert llm.model == "llama2"


def test_llm_factory_default():
    """Test LLM factory defaults to mock."""
    config = {}
    llm = LLMFactory.create(config)

    assert isinstance(llm, MockLLM)


def test_llm_factory_invalid_provider():
    """Test LLM factory returns mock for invalid provider."""
    config = {"provider": "invalid"}
    llm = LLMFactory.create(config)

    # Should default to mock
    assert isinstance(llm, MockLLM)


def test_openai_llm_missing_api_key():
    """Test OpenAI LLM handles missing API key."""
    config = {"provider": "openai"}  # No API key
    llm = LLMFactory.create(config)

    # Should fallback to mock
    assert isinstance(llm, MockLLM)


def test_ollama_llm_initialization():
    """Test Ollama LLM initialization."""
    llm = OllamaLLM(model="llama2")

    assert llm.model == "llama2"
