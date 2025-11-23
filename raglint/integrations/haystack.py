from typing import Any, Dict, Optional
from raglint.instrumentation import Monitor

class RAGLintTracer:
    """
    RAGLint Tracer for Haystack pipelines.
    Hooks into Haystack's tracing mechanism to log events.
    """
    def __init__(self, monitor: Optional[Monitor] = None):
        self.monitor = monitor or Monitor.get_instance()
        
    def trace(self, operation_name: str, tags: Dict[str, Any]) -> Any:
        """
        Context manager to trace an operation.
        """
        return RAGLintSpan(self.monitor, operation_name, tags)

class RAGLintSpan:
    def __init__(self, monitor: Monitor, operation_name: str, tags: Dict[str, Any]):
        self.monitor = monitor
        self.operation_name = operation_name
        self.tags = tags
        self.start_time = None
        
    def __enter__(self):
        import time
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        import time
        latency = time.time() - self.start_time
        
        status = "error" if exc_type else "success"
        error_msg = str(exc_val) if exc_val else None
        
        # Determine event type based on operation name or tags
        event_type = "unknown"
        if "retriever" in self.operation_name.lower():
            event_type = "retriever"
        elif "generator" in self.operation_name.lower() or "llm" in self.operation_name.lower():
            event_type = "llm"
        elif "pipeline" in self.operation_name.lower():
            event_type = "chain"
            
        self.monitor.log_event(
            type=event_type,
            name=self.operation_name,
            latency_seconds=latency,
            status=status,
            error=error_msg,
            metadata=self.tags
        )
