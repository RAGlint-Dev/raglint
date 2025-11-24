"""Built-in plugins for RAGlint."""

from .bias_detector import BiasDetectorPlugin
from .chunk_coverage import ChunkCoveragePlugin
from .citation_accuracy import CitationAccuracyPlugin
from .completeness import CompletenessPlugin
from .conciseness import ConcisenessPlugin
from .context_compression import ContextCompressionPlugin
from .diversity import ResponseDiversityPlugin
from .hallucination import HallucinationPlugin
from .hallucination_confidence import HallucinationConfidencePlugin
from .intent_classifier import UserIntentPlugin
from .multilingual import MultilingualSupportPlugin
from .pii_detector import PIIDetectorPlugin
from .query_difficulty import QueryDifficultyPlugin
from .readability import ReadabilityPlugin
from .sql_injection import SQLInjectionDetectorPlugin

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
