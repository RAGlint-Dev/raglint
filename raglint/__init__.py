"""RAGLint - RAG Pipeline Evaluation Framework.

This package provides a comprehensive framework for evaluating
Retrieval-Augmented Generation (RAG) systems.
"""

from raglint.config import Config
from raglint.core import RAGPipelineAnalyzer
from raglint.instrumentation import watch, Monitor
from raglint.integrations.langchain import RAGLintCallbackHandler
from raglint.exceptions import (
    RAGLintError,
    ConfigError,
    MetricError,
    LLMError,
    PluginError,
    DataValidationError,
    DashboardError,
    GenerationError,
)
from raglint.llm import LLMFactory, BaseLLM, MockLLM, OpenAI_LLM, OllamaLLM

__version__ = "0.2.0"

__all__ = [
    # Core classes
    "Config",
    "RAGPipelineAnalyzer",
    "LLMFactory",
    "watch",
    "Monitor",
    "RAGLintCallbackHandler",
    # LLM providers

    "BaseLLM",
    "MockLLM",
    "OpenAI_LLM",
    "OllamaLLM",
    # Exceptions
    "RAGLintError",
    "ConfigError",
    "MetricError",
    "LLMError",
    "PluginError",
    "DataValidationError",
    "DashboardError",
    "GenerationError",
]
