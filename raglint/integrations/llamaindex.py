"""
LlamaIndex integration for RAGLint.
Provides a callback handler to automatically trace LlamaIndex executions.
"""

from typing import Any, Optional

try:
    from llama_index.core.callbacks.base_handler import BaseCallbackHandler
    from llama_index.core.callbacks.schema import CBEventType, EventPayload
except ImportError:
    # Create dummy classes if llama-index is not installed
    class BaseCallbackHandler:
        def __init__(self, event_starts_to_ignore: list[Any], event_ends_to_ignore: list[Any]):
            pass

    class CBEventType:
        LLM = "llm"
        RETRIEVE = "retrieve"
        EMBEDDING = "embedding"
        TREE = "tree"
        SUB_QUESTION = "sub_question"
        TEMPLATING = "templating"
        FUNCTION_CALL = "function_call"
        EXCEPTION = "exception"
        AGENT_STEP = "agent_step"

    class EventPayload:
        PROMPT = "prompt"
        MESSAGES = "messages"
        RESPONSE = "response"
        QUERY_STR = "query_str"
        NODES = "nodes"
        EXCEPTION = "exception"
        TOOL = "tool"

from raglint.instrumentation import Monitor
from raglint.logging import get_logger

logger = get_logger(__name__)

class RAGLintLlamaIndexCallback(BaseCallbackHandler):
    """
    Callback handler for LlamaIndex to automatically log events to RAGLint.

    Usage:
        from llama_index.core.callbacks import CallbackManager
        from raglint.integrations.llamaindex import RAGLintLlamaIndexCallback

        raglint_callback = RAGLintLlamaIndexCallback()
        callback_manager = CallbackManager([raglint_callback])

        # Pass callback_manager to your index/query engine
        service_context = ServiceContext.from_defaults(callback_manager=callback_manager)
    """

    def __init__(self, event_starts_to_ignore: Optional[list[CBEventType]] = None,
                 event_ends_to_ignore: Optional[list[CBEventType]] = None):
        super().__init__(
            event_starts_to_ignore=event_starts_to_ignore or [],
            event_ends_to_ignore=event_ends_to_ignore or []
        )
        self.monitor = Monitor()
        self._event_pairs = {} # Track start/end pairs if needed

    def on_event_start(
        self,
        event_type: CBEventType,
        payload: Optional[dict[str, Any]] = None,
        event_id: str = "",
        parent_id: str = "",
        **kwargs: Any,
    ) -> str:
        """Run when an event starts."""
        payload = payload or {}

        if event_type == CBEventType.LLM:
            self._handle_llm_start(payload, event_id, parent_id)
        elif event_type == CBEventType.RETRIEVE:
            self._handle_retrieve_start(payload, event_id, parent_id)
        elif event_type == CBEventType.QUERY: # Note: QUERY might not be in standard schema but often used
            self._handle_query_start(payload, event_id, parent_id)

        return event_id

    def on_event_end(
        self,
        event_type: CBEventType,
        payload: Optional[dict[str, Any]] = None,
        event_id: str = "",
        **kwargs: Any,
    ) -> None:
        """Run when an event ends."""
        payload = payload or {}

        if event_type == CBEventType.LLM:
            self._handle_llm_end(payload, event_id)
        elif event_type == CBEventType.RETRIEVE:
            self._handle_retrieve_end(payload, event_id)
        elif event_type == CBEventType.EXCEPTION:
            self._handle_exception(payload, event_id)

    def start_trace(self, trace_id: Optional[str] = None) -> None:
        """Run when an overall trace starts."""
        # LlamaIndex doesn't always have a clear "start trace" hook in the same way,
        # but we can rely on the first event or manual triggers.
        pass

    def end_trace(
        self,
        trace_id: Optional[str] = None,
        trace_map: Optional[dict[str, list[str]]] = None,
    ) -> None:
        """Run when an overall trace ends."""
        pass

    # --- Event Handlers ---

    def _handle_llm_start(self, payload: dict[str, Any], event_id: str, parent_id: str):
        prompts = []
        if EventPayload.PROMPT in payload:
            prompts.append(payload[EventPayload.PROMPT])
        if EventPayload.MESSAGES in payload:
            # Convert chat messages to string representation
            prompts.extend([str(m) for m in payload[EventPayload.MESSAGES]])

        self.monitor.log_event("llm_start", {
            "trace_id": event_id,
            "parent_id": parent_id if parent_id else None,
            "prompts": prompts,
            # Model info isn't always directly in payload start, might need to extract from context if available
            "framework": "llamaindex"
        })

    def _handle_llm_end(self, payload: dict[str, Any], event_id: str):
        response = payload.get(EventPayload.RESPONSE)
        generations = []

        if response:
            # Handle different response types (CompletionResponse, ChatResponse)
            text = str(response)
            if hasattr(response, "message") and response.message:
                text = response.message.content
            elif hasattr(response, "text"):
                text = response.text
            generations.append([text])

        self.monitor.log_event("llm_end", {
            "trace_id": event_id,
            "generations": generations
        })

    def _handle_retrieve_start(self, payload: dict[str, Any], event_id: str, parent_id: str):
        query_str = payload.get(EventPayload.QUERY_STR, "")
        self.monitor.log_event("retriever_start", {
            "trace_id": event_id,
            "parent_id": parent_id if parent_id else None,
            "query": query_str
        })

    def _handle_retrieve_end(self, payload: dict[str, Any], event_id: str):
        nodes = payload.get(EventPayload.NODES, [])
        docs_info = []

        for node_with_score in nodes:
            # Handle NodeWithScore objects
            try:
                node = node_with_score.node
                content = node.get_content()
                score = node_with_score.score
                metadata = node.metadata

                docs_info.append({
                    "content": content[:200] + "...", # Truncate for logging
                    "score": score,
                    "metadata": metadata
                })
            except Exception:
                continue

        self.monitor.log_event("retriever_end", {
            "trace_id": event_id,
            "documents": docs_info
        })

    def _handle_query_start(self, payload: dict[str, Any], event_id: str, parent_id: str):
        # Sometimes high-level query start
        query_str = payload.get(EventPayload.QUERY_STR, "")
        self.monitor.log_event("chain_start", {
            "trace_id": event_id,
            "name": "LlamaIndexQuery",
            "inputs": {"query": query_str}
        })

    def _handle_exception(self, payload: dict[str, Any], event_id: str):
        exception = payload.get(EventPayload.EXCEPTION)
        self.monitor.log_event("chain_error", {
            "trace_id": event_id,
            "error": str(exception)
        })
