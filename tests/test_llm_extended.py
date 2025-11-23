"""
Extended tests for LLM module to improve coverage.
Tests Ollama integration, Mock LLM, and error handling.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from raglint.llm import MockLLM, OpenAI_LLM, OllamaLLM


class TestMockLLM:
    """Tests for MockLLM class."""
    
    def test_generate_json(self):
        """Test synchronous JSON generation."""
        llm = MockLLM()
        result = llm.generate_json("test prompt")
        
        assert isinstance(result, dict)
        assert "score" in result
        assert "reasoning" in result
        assert result["score"] == 0.1
        
    @pytest.mark.asyncio
    async def test_agenerate_json(self):
        """Test async JSON generation."""
        llm = MockLLM()
        result = await llm.agenerate_json("test prompt")
        
        assert isinstance(result, dict)
        assert "score" in result
        assert "reasoning" in result
        assert "[MOCK]" in result["reasoning"]


class TestOpenAIJSON:
    """Tests for OpenAI_LLM JSON generation."""
    
    @pytest.mark.asyncio
    async def test_generate_json_success(self):
        """Test successful JSON generation with tracking."""
        # We'll mock at the point where it's imported in the __init__ method
        llm = OpenAI_LLM(api_key="test-key")
        
        # Now patch the async_client that was set up
        with patch.object(llm, 'async_client') as mock_client:
            # Mock the response
            mock_response = Mock()
            mock_response.choices = [Mock(message=Mock(content='{"result": "success"}'))]
            mock_response.usage = Mock(
                prompt_tokens=10,
                completion_tokens=5
            )
            
            mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
            
            result = await llm.generate_json("test prompt")
            
            assert isinstance(result, dict)
            assert result["result"] == "success"
            
    @pytest.mark.asyncio
    async def test_generate_json_error(self):
        """Test JSON generation error handling."""
        llm = OpenAI_LLM(api_key="test-key")
        
        with patch.object(llm, 'async_client') as mock_client:
            mock_client.chat.completions.create = AsyncMock(
                side_effect=Exception("API Error")
            )
            
            result = await llm.generate_json("test prompt")
            
            # Should return empty dict on error
            assert result == {}


class TestOllamaIntegration:
    """Tests for OllamaLLM integration."""
    
    @pytest.mark.asyncio
    async def test_agenerate_success(self):
        """Test successful async generation with Ollama."""
        with patch("aiohttp.ClientSession") as mock_session:
            # Mock the response
            mock_resp = AsyncMock()
            mock_resp.json = AsyncMock(return_value={"response": "test response"})
            mock_resp.raise_for_status = Mock()
            
            mock_post = AsyncMock()
            mock_post.__aenter__ = AsyncMock(return_value=mock_resp)
            mock_post.__aexit__ = AsyncMock()
            
            mock_session_inst = AsyncMock()
            mock_session_inst.post = Mock(return_value=mock_post)
            mock_session_inst.__aenter__ = AsyncMock(return_value=mock_session_inst)
            mock_session_inst.__aexit__ = AsyncMock()
            
            mock_session.return_value = mock_session_inst
            
            llm = OllamaLLM(model="llama2")
            result = await llm.agenerate("test prompt")
            
            assert result == "test response"
            
    @pytest.mark.asyncio
    async def test_agenerate_error(self):
        """Test async generation error handling."""
        with patch("aiohttp.ClientSession") as mock_session:
            mock_session.side_effect = Exception("Connection error")
            
            llm = OllamaLLM(model="llama2")
            result = await llm.agenerate("test prompt")
            
            # Should return "Error" on failure
            assert result == "Error"
            
    @pytest.mark.asyncio
    async def test_generate_json_success(self):
        """Test successful JSON generation with Ollama."""
        with patch("aiohttp.ClientSession") as mock_session:
            # Mock the response
            mock_resp = AsyncMock()
            mock_resp.json = AsyncMock(return_value={
                "response": '{"score": 0.95, "reasoning": "test"}'
            })
            mock_resp.raise_for_status = Mock()
            
            mock_post = AsyncMock()
            mock_post.__aenter__ = AsyncMock(return_value=mock_resp)
            mock_post.__aexit__ = AsyncMock()
            
            mock_session_inst = AsyncMock()
            mock_session_inst.post = Mock(return_value=mock_post)
            mock_session_inst.__aenter__ = AsyncMock(return_value=mock_session_inst)
            mock_session_inst.__aexit__ = AsyncMock()
            
            mock_session.return_value = mock_session_inst
            
            llm = OllamaLLM(model="llama2")
            result = await llm.generate_json("test prompt")
            
            assert isinstance(result, dict)
            assert result["score"] == 0.95
            assert result["reasoning"] == "test"
            
    @pytest.mark.asyncio
    async def test_generate_json_error(self):
        """Test JSON generation error handling."""
        with patch("aiohttp.ClientSession") as mock_session:
            mock_session.side_effect = Exception("API Error")
            
            llm = OllamaLLM(model="llama2")
            result = await llm.generate_json("test prompt")
            
            # Should return error dict
            assert isinstance(result, dict)
            assert result["score"] == 0.0
            assert "Error" in result["reasoning"]
            
    @pytest.mark.asyncio
    async def test_generate_json_parse_error(self):
        """Test JSON parse error handling."""
        with patch("aiohttp.ClientSession") as mock_session:
            # Mock response with invalid JSON
            mock_resp = AsyncMock()
            mock_resp.json = AsyncMock(return_value={"response": "not valid json"})
            mock_resp.raise_for_status = Mock()
            
            mock_post = AsyncMock()
            mock_post.__aenter__ = AsyncMock(return_value=mock_resp)
            mock_post.__aexit__ = AsyncMock()
            
            mock_session_inst = AsyncMock()
            mock_session_inst.post = Mock(return_value=mock_post)
            mock_session_inst.__aenter__ = AsyncMock(return_value=mock_session_inst)
            mock_session_inst.__aexit__ = AsyncMock()
            
            mock_session.return_value = mock_session_inst
            
            llm = OllamaLLM(model="llama2")
            result = await llm.generate_json("test prompt")
            
            # Should return error dict on parse failure
            # Note: actual implementation might return None or error dict
            assert result is None or (isinstance(result, dict) and result.get("score") == 0.0)
