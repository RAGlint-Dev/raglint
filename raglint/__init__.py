"""RAGLint - RAG Pipeline Evaluation Framework.

This package provides a comprehensive framework for evaluating
Retrieval-Augmented Generation (RAG) systems.
"""

from raglint.config import Config
from raglint.core import RAGPipelineAnalyzer
from raglint.exceptions import (
    ConfigError,
    DashboardError,
    DataValidationError,
    GenerationError,
    LLMError,
    MetricError,
    PluginError,
    RAGLintError,
)
from raglint.instrumentation import Monitor, watch
from raglint.integrations.langchain import RAGLintCallbackHandler
from raglint.llm import BaseLLM, LLMFactory, MockLLM, OllamaLLM, OpenAI_LLM

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
