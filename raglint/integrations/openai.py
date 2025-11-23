import time
import functools
from typing import Any, Callable, Optional
from raglint.instrumentation import Monitor

def wrap_openai(client: Any, monitor: Optional[Monitor] = None) -> Any:
    """
    Wraps an OpenAI client to automatically trace chat completions.
    
    Args:
        client: The OpenAI client instance (sync or async).
        monitor: Optional RAGLint monitor. If None, uses the global instance.
        
    Returns:
        The wrapped client.
    """
    if monitor is None:
        monitor = Monitor.get_instance()
        
    # Wrap chat.completions.create
    if hasattr(client, "chat") and hasattr(client.chat, "completions"):
        original_create = client.chat.completions.create
        
        @functools.wraps(original_create)
        def wrapped_create(*args, **kwargs):
            start_time = time.time()
            try:
                # Call original method
                response = original_create(*args, **kwargs)
                
                # Calculate latency
                latency = time.time() - start_time
                
                # Extract info
                model = kwargs.get("model", "unknown")
                messages = kwargs.get("messages", [])
                
                # Handle response (assuming it's not a stream for MVP)
                # TODO: Handle streaming responses
                if not kwargs.get("stream", False):
                    response_content = response.choices[0].message.content
                    
                    # Log event
                    monitor.log_event(
                        type="llm",
                        name=f"openai_chat_completion_{model}",
                        model=model,
                        input=messages,
                        output=response_content,
                        latency_seconds=latency,
                        metadata={
                            "provider": "openai",
                            "usage": response.usage.model_dump() if response.usage else {}
                        }
                    )
                
                return response
            except Exception as e:
                # Log error
                latency = time.time() - start_time
                monitor.log_event(
                    type="llm",
                    name="openai_chat_completion_error",
                    error=str(e),
                    latency_seconds=latency,
                    status="error"
                )
                raise e
                
        client.chat.completions.create = wrapped_create
        
    return client
