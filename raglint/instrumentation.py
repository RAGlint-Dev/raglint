"""
Auto-instrumentation for RAG pipelines.
Allows developers to wrap their functions with @raglint.watch to automatically capture
inputs, outputs, and latency.
"""

import asyncio
import functools
import inspect
import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Optional


class Monitor:
    """
    Singleton monitor to manage tracing and logging.
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.trace_file = Path("raglint_events.jsonl")
            cls._instance.enabled = True
        return cls._instance

    def log_event(self, event_type: str, data: dict[str, Any]):
        """Log an event to the JSONL file."""
        if not self.enabled:
            return

        event = {
            "event_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "type": event_type,
            **data,
        }

        with open(self.trace_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

        # Check for alerts
        if event_type == "end" and data.get("status") == "error":
            from raglint.alerting import AlertManager

            AlertManager().send_alert_sync(
                title="Operation Failed",
                message=f"Operation '{data.get('operation')}' failed.",
                level="error",
                details={"Error": data.get("error"), "Trace ID": data.get("trace_id")},
            )
        elif (
            event_type == "end" and data.get("latency_seconds", 0) > 5.0
        ):  # Latency threshold example
            from raglint.alerting import AlertManager

            AlertManager().send_alert_sync(
                title="High Latency Detected",
                message=f"Operation '{data.get('operation')}' took {data.get('latency_seconds'):.2f}s.",
                level="warning",
                details={
                    "Latency": f"{data.get('latency_seconds'):.2f}s",
                    "Trace ID": data.get("trace_id"),
                },
            )

    def disable(self):

        self.enabled = False

    def enable(self):
        self.enabled = True


def watch(
    name: Optional[str] = None,
    log_inputs: bool = True,
    log_outputs: bool = True,
    tags: Optional[list[str]] = None,
):
    """
    Decorator to automatically log function calls.

    Usage:
        @raglint.watch(tags=["retrieval"])
        def retrieve(query):
            ...
    """

    def decorator(func: Callable):
        operation_name = name or func.__name__
        monitor = Monitor()

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            trace_id = str(uuid.uuid4())

            # Capture inputs
            inputs = {}
            if log_inputs:
                # Simple binding of args to names if possible, otherwise just list
                try:
                    sig = inspect.signature(func)
                    bound = sig.bind(*args, **kwargs)
                    bound.apply_defaults()
                    inputs = dict(bound.arguments)
                except Exception:
                    inputs = {
                        "args": [str(a) for a in args],
                        "kwargs": {k: str(v) for k, v in kwargs.items()},
                    }

            monitor.log_event(
                "start",
                {
                    "trace_id": trace_id,
                    "operation": operation_name,
                    "inputs": inputs if log_inputs else None,
                    "tags": tags or [],
                },
            )

            try:
                result = await func(*args, **kwargs)
                status = "success"
                error = None
            except Exception as e:
                result = None
                status = "error"
                error = str(e)
                raise e
            finally:
                latency = time.time() - start_time
                monitor.log_event(
                    "end",
                    {
                        "trace_id": trace_id,
                        "operation": operation_name,
                        "outputs": result if log_outputs and status == "success" else None,
                        "latency_seconds": latency,
                        "status": status,
                        "error": error,
                    },
                )

            return result

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            trace_id = str(uuid.uuid4())

            # Capture inputs
            inputs = {}
            if log_inputs:
                try:
                    sig = inspect.signature(func)
                    bound = sig.bind(*args, **kwargs)
                    bound.apply_defaults()
                    inputs = dict(bound.arguments)
                except Exception:
                    inputs = {
                        "args": [str(a) for a in args],
                        "kwargs": {k: str(v) for k, v in kwargs.items()},
                    }

            monitor.log_event(
                "start",
                {
                    "trace_id": trace_id,
                    "operation": operation_name,
                    "inputs": inputs if log_inputs else None,
                    "tags": tags or [],
                },
            )

            try:
                result = func(*args, **kwargs)
                status = "success"
                error = None
            except Exception as e:
                result = None
                status = "error"
                error = str(e)
                raise e
            finally:
                latency = time.time() - start_time
                monitor.log_event(
                    "end",
                    {
                        "trace_id": trace_id,
                        "operation": operation_name,
                        "outputs": result if log_outputs and status == "success" else None,
                        "latency_seconds": latency,
                        "status": status,
                        "error": error,
                    },
                )

            return result

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator
