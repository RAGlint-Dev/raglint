import pytest
from unittest.mock import MagicMock, patch
from uuid import uuid4

from raglint.integrations.llamaindex import RAGLintLlamaIndexCallback, CBEventType, EventPayload

class TestLlamaIndexIntegration:
    
    @pytest.fixture
    def mock_monitor(self):
        with patch("raglint.integrations.llamaindex.Monitor") as MockMonitor:
            monitor_instance = MockMonitor.return_value
            yield monitor_instance

    def test_llm_event(self, mock_monitor):
        callback = RAGLintLlamaIndexCallback()
        event_id = str(uuid4())
        
        # Simulate LLM Start
        payload_start = {
            EventPayload.PROMPT: "Test prompt",
            EventPayload.MESSAGES: ["User: Hello"]
        }
        callback.on_event_start(CBEventType.LLM, payload=payload_start, event_id=event_id)
        
        # Verify start log
        mock_monitor.log_event.assert_called_with("llm_start", {
            "trace_id": event_id,
            "parent_id": None,
            "prompts": ["Test prompt", "User: Hello"],
            "framework": "llamaindex"
        })
        
        # Simulate LLM End
        mock_response = MagicMock()
        mock_response.text = "Test response"
        mock_response.message = None
        payload_end = {
            EventPayload.RESPONSE: mock_response
        }
        callback.on_event_end(CBEventType.LLM, payload=payload_end, event_id=event_id)
        
        # Verify end log
        mock_monitor.log_event.assert_called_with("llm_end", {
            "trace_id": event_id,
            "generations": [["Test response"]]
        })

    def test_retrieve_event(self, mock_monitor):
        callback = RAGLintLlamaIndexCallback()
        event_id = str(uuid4())
        
        # Simulate Retrieve Start
        payload_start = {
            EventPayload.QUERY_STR: "Test query"
        }
        callback.on_event_start(CBEventType.RETRIEVE, payload=payload_start, event_id=event_id)
        
        # Verify start log
        mock_monitor.log_event.assert_called_with("retriever_start", {
            "trace_id": event_id,
            "parent_id": None,
            "query": "Test query"
        })
        
        # Simulate Retrieve End
        mock_node = MagicMock()
        mock_node.get_content.return_value = "Retrieved content"
        mock_node.metadata = {"source": "doc1"}
        
        mock_node_with_score = MagicMock()
        mock_node_with_score.node = mock_node
        mock_node_with_score.score = 0.9
        
        payload_end = {
            EventPayload.NODES: [mock_node_with_score]
        }
        callback.on_event_end(CBEventType.RETRIEVE, payload=payload_end, event_id=event_id)
        
        # Verify end log
        mock_monitor.log_event.assert_called_with("retriever_end", {
            "trace_id": event_id,
            "documents": [{
                "content": "Retrieved content...",
                "score": 0.9,
                "metadata": {"source": "doc1"}
            }]
        })
