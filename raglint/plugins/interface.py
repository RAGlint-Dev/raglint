"""
Plugin Interfaces.

Defines the abstract base classes that all plugins must implement.
"""

from abc import ABC, abstractmethod


class BasePlugin(ABC):
    """Base class for all RAGLint plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name of the plugin."""
        pass

    @property
    def version(self) -> str:
        """Plugin version."""
        return "0.1.0"

    @property
    def description(self) -> str:
        """Brief description of what the plugin does."""
        return ""


class LLMPlugin(BasePlugin):
    """
    Interface for custom LLM providers.

    Plugins implementing this interface can be used as LLM backends
    by setting `provider: <plugin_name>` in the config.
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Synchronous generation."""
        pass

    @abstractmethod
    async def agenerate(self, prompt: str) -> str:
        """Asynchronous generation."""
        pass


class MetricPlugin(BasePlugin):
    """
    Interface for custom evaluation metrics.
    """

    @abstractmethod
    def score(self, **kwargs) -> float:
        """Calculate the metric score."""
        pass

    @property
    @abstractmethod
    def metric_type(self) -> str:
        """Type of metric (e.g., 'retrieval', 'generation', 'e2e')."""
        pass

class PluginInterface(MetricPlugin):
    """
    Adapter for plugins using the async-first interface.
    Provides default implementations for synchronous MetricPlugin methods.
    """

    @property
    def metric_type(self) -> str:
        return "quality"

    def score(self, **kwargs) -> float:
        """
        Default sync implementation.
        Real implementation is in calculate_async().
        """
        return 0.0
