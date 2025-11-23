import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from raglint.llm import OpenAI_LLM, OllamaLLM

@pytest.mark.asyncio
async def test_openai_llm_generate():
    with patch("openai.OpenAI") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.chat.completions.create.return_value.choices[0].message.content = "Test Response"
        
        llm = OpenAI_LLM(api_key="test")
        response = llm.generate("prompt")
        
        assert response == "Test Response"

@pytest.mark.asyncio
async def test_ollama_llm_generate_json():
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_response = AsyncMock()
        mock_response.json.return_value = {"response": '{"score": 0.8}'}
        mock_post.return_value.__aenter__.return_value = mock_response
        
        llm = OllamaLLM()
        result = await llm.generate_json("prompt")
        
        assert result["score"] == 0.8
