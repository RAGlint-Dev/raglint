import pytest
from unittest.mock import MagicMock
from raglint.integrations.openai import wrap_openai
from raglint.instrumentation import Monitor

def test_wrap_openai_sync():
    # Mock OpenAI Client
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Hello world"))]
    mock_response.usage = MagicMock(model_dump=lambda: {"total_tokens": 10})
    mock_client.chat.completions.create.return_value = mock_response
    
    # Mock Monitor
    mock_monitor = MagicMock()
    
    # Wrap
    wrapped_client = wrap_openai(mock_client, monitor=mock_monitor)
    
    # Call
    messages = [{"role": "user", "content": "Hi"}]
    wrapped_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    
    # Verify Monitor called
    mock_monitor.log_event.assert_called_once()
    call_args = mock_monitor.log_event.call_args[1]
    assert call_args["type"] == "llm"
    assert call_args["model"] == "gpt-3.5-turbo"
    assert call_args["output"] == "Hello world"
    assert call_args["metadata"]["provider"] == "openai"

def test_wrap_openai_error():
    # Mock OpenAI Client raising error
    mock_client = MagicMock()
    mock_client.chat.completions.create.side_effect = Exception("API Error")
    
    # Mock Monitor
    mock_monitor = MagicMock()
    
    # Wrap
    wrapped_client = wrap_openai(mock_client, monitor=mock_monitor)
    
    # Call and expect error
    with pytest.raises(Exception):
        wrapped_client.chat.completions.create(model="gpt-4", messages=[])
        
    # Verify Error Logged
    mock_monitor.log_event.assert_called_once()
    call_args = mock_monitor.log_event.call_args[1]
    assert call_args["status"] == "error"
    assert "API Error" in call_args["error"]
