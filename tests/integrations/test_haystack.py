import pytest
from unittest.mock import MagicMock
from raglint.integrations.haystack import RAGLintTracer

def test_haystack_tracer():
    # Mock Monitor
    mock_monitor = MagicMock()
    
    # Initialize Tracer
    tracer = RAGLintTracer(monitor=mock_monitor)
    
    # Simulate Haystack tracing
    with tracer.trace("MyRetriever", tags={"query": "test"}) as span:
        pass
        
    # Verify Log Event
    mock_monitor.log_event.assert_called_once()
    call_args = mock_monitor.log_event.call_args[1]
    assert call_args["type"] == "retriever"
    assert call_args["name"] == "MyRetriever"
    assert call_args["status"] == "success"
    assert call_args["metadata"]["query"] == "test"

def test_haystack_tracer_error():
    # Mock Monitor
    mock_monitor = MagicMock()
    
    # Initialize Tracer
    tracer = RAGLintTracer(monitor=mock_monitor)
    
    # Simulate Error
    with pytest.raises(ValueError):
        with tracer.trace("MyLLM", tags={}) as span:
            raise ValueError("Oops")
            
    # Verify Error Log
    mock_monitor.log_event.assert_called_once()
    call_args = mock_monitor.log_event.call_args[1]
    assert call_args["type"] == "llm"
    assert call_args["status"] == "error"
    assert "Oops" in call_args["error"]
