"""
LangChain integration for RAGLint.
Provides a callback handler to automatically trace LangChain executions.
"""

from typing import Any, Optional, Union
from uuid import UUID

try:
    from langchain_core.callbacks import BaseCallbackHandler
    from langchain_core.outputs import LLMResult
except ImportError:
    # Create dummy class if langchain is not installed
    class BaseCallbackHandler:
        pass
    class LLMResult:
        pass

from raglint.instrumentation import Monitor


class RAGLintCallbackHandler(BaseCallbackHandler):
    """
    Callback handler for LangChain to automatically log events to RAGLint.

    Usage:
        from raglint.integrations.langchain import RAGLintCallbackHandler

        chain.invoke(input, config={"callbacks": [RAGLintCallbackHandler()]})
    """

    def __init__(self):
        self.monitor = Monitor()

    def on_chain_start(
        self, serialized: dict[str, Any], inputs: dict[str, Any], *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs: Any
    ) -> Any:
        """Run when chain starts running."""
        self.monitor.log_event("chain_start", {
            "trace_id": str(run_id),
            "parent_id": str(parent_run_id) if parent_run_id else None,
            "inputs": inputs,
            "name": serialized.get("name", "LangChain")
        })

    def on_chain_end(
        self, outputs: dict[str, Any], *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs: Any
    ) -> Any:
        """Run when chain ends running."""
        self.monitor.log_event("chain_end", {
            "trace_id": str(run_id),
            "outputs": outputs
        })

    def on_chain_error(
        self, error: Union[Exception, KeyboardInterrupt], *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs: Any
    ) -> Any:
        """Run when chain errors."""
        self.monitor.log_event("chain_error", {
            "trace_id": str(run_id),
            "error": str(error)
        })

    def on_llm_start(
        self, serialized: dict[str, Any], prompts: list[str], *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs: Any
    ) -> Any:
        """Run when LLM starts running."""
        self.monitor.log_event("llm_start", {
            "trace_id": str(run_id),
            "parent_id": str(parent_run_id) if parent_run_id else None,
            "prompts": prompts,
            "model": serialized.get("kwargs", {}).get("model_name")
        })

    def on_llm_end(
        self, response: LLMResult, *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs: Any
    ) -> Any:
        """Run when LLM ends running."""
        self.monitor.log_event("llm_end", {
            "trace_id": str(run_id),
            "generations": [[g.text for g in gen] for gen in response.generations]
        })

    def on_retriever_start(
        self, serialized: dict[str, Any], query: str, *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs: Any
    ) -> Any:
        """Run when Retriever starts running."""
        self.monitor.log_event("retriever_start", {
            "trace_id": str(run_id),
            "parent_id": str(parent_run_id) if parent_run_id else None,
            "query": query
        })

    def on_retriever_end(
        self, documents: Any, *, run_id: UUID, parent_run_id: Optional[UUID] = None, **kwargs: Any
    ) -> Any:
        """Run when Retriever ends running."""
        # Handle both list of Documents and other formats
        docs_info = []
        try:
            for doc in documents:
                docs_info.append({
                    "content": getattr(doc, "page_content", str(doc))[:200] + "...",
                    "metadata": getattr(doc, "metadata", {})
                })
        except Exception:
            docs_info = str(documents)

        self.monitor.log_event("retriever_end", {
            "trace_id": str(run_id),
            "documents": docs_info
        })
