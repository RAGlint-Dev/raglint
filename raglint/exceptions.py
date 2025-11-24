"""Custom exceptions for RAGLint.

This module defines the exception hierarchy for RAGLint, providing
clear error types for different failure modes.
"""

from typing import Optional


class RAGLintError(Exception):
    """Base exception for all RAGLint errors."""

    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConfigError(RAGLintError):
    """Configuration-related errors."""
    pass


class MetricError(RAGLintError):
    """Metric calculation errors."""

    def __init__(self, metric_name: str, message: str, details: Optional[dict] = None):
        self.metric_name = metric_name
        super().__init__(f"Metric '{metric_name}': {message}", details)


class LLMError(RAGLintError):
    """LLM provider errors (API failures, timeouts, etc.)."""

    def __init__(self, provider: str, message: str, details: Optional[dict] = None):
        self.provider = provider
        super().__init__(f"LLM Provider '{provider}': {message}", details)


class PluginError(RAGLintError):
    """Plugin loading or execution errors."""

    def __init__(self, plugin_name: str, message: str, details: Optional[dict] = None):
        self.plugin_name = plugin_name
        super().__init__(f"Plugin '{plugin_name}': {message}", details)


class DataValidationError(RAGLintError):
    """Input data validation errors."""
    pass


class DashboardError(RAGLintError):
    """Dashboard/API errors."""
    pass


class GenerationError(RAGLintError):
    """Test generation errors."""
    pass
