"""
RAGLint Plugin System.

This module provides the infrastructure for extending RAGLint with custom
LLM providers, metrics, and other components.
"""

from .interface import BasePlugin, LLMPlugin, MetricPlugin
from .loader import PluginLoader

__all__ = ["BasePlugin", "LLMPlugin", "MetricPlugin", "PluginLoader"]
