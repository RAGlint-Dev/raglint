"""Built-in plugins for RAGlint."""

from .chunk_coverage import ChunkCoveragePlugin
from .hallucination import HallucinationPlugin
from .query_difficulty import QueryDifficultyPlugin
from .citation_accuracy import CitationAccuracyPlugin
from .readability import ReadabilityPlugin
from .completeness import CompletenessPlugin
from .conciseness import ConcisenessPlugin
from .bias_detector import BiasDetectorPlugin
from .multilingual import MultilingualSupportPlugin
from .pii_detector import PIIDetectorPlugin
from .sql_injection import SQLInjectionDetectorPlugin
from .hallucination_confidence import HallucinationConfidencePlugin
from .context_compression import ContextCompressionPlugin
from .diversity import ResponseDiversityPlugin
from .intent_classifier import UserIntentPlugin

__all__ = [
    "ChunkCoveragePlugin",
    "HallucinationPlugin",
    "QueryDifficultyPlugin",
    "CitationAccuracyPlugin",
    "ReadabilityPlugin",
    "CompletenessPlugin",
    "ConcisenessPlugin",
    "BiasDetectorPlugin",
    "MultilingualSupportPlugin",
    "PIIDetectorPlugin",
    "SQLInjectionDetectorPlugin",
    "HallucinationConfidencePlugin",
    "ContextCompressionPlugin",
    "ResponseDiversityPlugin",
    "UserIntentPlugin",
]
