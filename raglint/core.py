import asyncio
from dataclasses import dataclass, field
from typing import Any, Optional

from tqdm.asyncio import tqdm as atqdm

from .llm import LLMFactory
from .logging import get_logger
from .metrics import (
    AnswerRelevanceScorer,
    ContextRelevanceScorer,
    FaithfulnessScorer,
    SemanticMatcher,
    ToxicityScorer,
    calculate_chunk_size_distribution,
    calculate_retrieval_metrics,
    estimate_semantic_coherence,
)

logger = get_logger(__name__)


@dataclass
class AnalysisResult:
    chunk_stats: dict[str, float]
    retrieval_stats: dict[str, float]
    detailed_results: list[dict[str, Any]]
    semantic_scores: list[float] = field(default_factory=list)
    faithfulness_scores: list[float] = field(default_factory=list)
    is_mock: bool = False


class RAGPipelineAnalyzer:
    """
    RAG Pipeline Analyzer with async support for parallel LLM processing.
    """

    def __init__(self, use_smart_metrics: bool = False, config: Optional[dict] = None):
        self.use_smart_metrics = use_smart_metrics
        self.config = config or {}

        if self.use_smart_metrics:
            logger.info("Initializing Smart Metrics...")
            print("Initializing Smart Metrics (this may take a moment)...")
            # Initialize LLM
            self.llm = LLMFactory.create(self.config)

            prompts = self.config.get("prompts", {})

            self.semantic_matcher = SemanticMatcher()
            self.faithfulness_scorer = FaithfulnessScorer(
                llm=self.llm, prompt_template=prompts.get("faithfulness")
            )
            self.context_relevance_scorer = ContextRelevanceScorer(
                llm=self.llm, prompt_template=prompts.get("context_relevance")
            )
            self.answer_relevance_scorer = AnswerRelevanceScorer(
                llm=self.llm, prompt_template=prompts.get("answer_relevance")
            )
            self.toxicity_scorer = ToxicityScorer(
                llm=self.llm, prompt_template=prompts.get("toxicity")
            )

            # Import context metrics
            from raglint.metrics.context_metrics import ContextPrecisionScorer, ContextRecallScorer

            self.context_precision_scorer = ContextPrecisionScorer(llm=self.llm)
            self.context_recall_scorer = ContextRecallScorer(llm=self.llm)
        else:
            self.semantic_matcher = None
            self.faithfulness_scorer = None
            self.context_precision_scorer = None
            self.context_recall_scorer = None

    def analyze(self, data: list[dict[str, Any]], show_progress: bool = True) -> AnalysisResult:
        """
        Synchronous analysis (for backwards compatibility).
        For better performance with smart metrics, use analyze_async().
        """
        if self.use_smart_metrics and len(data) > 5:
            logger.info("Using async analysis for better performance with %d items", len(data))
            # For larger datasets with smart metrics, use async
            return asyncio.run(self.analyze_async(data, show_progress=show_progress))
        else:
            return self._analyze_sync(data)

    def _analyze_sync(self, data: list[dict[str, Any]]) -> AnalysisResult:
        """Synchronous analysis implementation."""
        all_chunks = []
        all_retrieval_metrics = {"precision": [], "recall": [], "mrr": [], "ndcg": []}
        coherence_scores = []
        semantic_scores = []
        faithfulness_scores = []
        detailed_results = []

        for item in data:
            retrieved = item.get("retrieved_contexts", [])
            ground_truth = item.get("ground_truth_contexts", [])
            response = item.get("response", "")
            query = item.get("query", "")

            # Chunking Analysis
            all_chunks.extend(retrieved)
            item_coherence = [estimate_semantic_coherence(c) for c in retrieved]
            coherence_scores.extend(item_coherence)

            # Retrieval Analysis (Basic)
            basic_metrics = None
            if ground_truth:
                basic_metrics = calculate_retrieval_metrics(retrieved, ground_truth)
                all_retrieval_metrics["precision"].append(basic_metrics["precision"])
                all_retrieval_metrics["recall"].append(basic_metrics["recall"])
                all_retrieval_metrics["mrr"].append(basic_metrics["mrr"])
                all_retrieval_metrics["ndcg"].append(basic_metrics["ndcg"])

            # Smart Metrics
            semantic_score = None
            faithfulness_score = None

            if self.use_smart_metrics:
                if ground_truth:
                    semantic_score = self.semantic_matcher.calculate_similarity(
                        retrieved, ground_truth
                    )
                    semantic_scores.append(semantic_score)

                if response:
                    f_score, f_reasoning = self.faithfulness_scorer.score(
                        query, retrieved, response
                    )
                    faithfulness_scores.append(f_score)
                    faithfulness_score = f_score

            detailed_results.append(
                {
                    "query": query,
                    "metrics": basic_metrics,
                    "coherence": item_coherence,
                    "semantic_score": semantic_score,
                    "faithfulness_score": (
                        faithfulness_score if self.use_smart_metrics and response else None
                    ),
                }
            )

        chunk_stats = calculate_chunk_size_distribution(all_chunks)

        avg_retrieval_stats = {
            "precision": (
                sum(all_retrieval_metrics["precision"]) / len(all_retrieval_metrics["precision"])
                if all_retrieval_metrics["precision"]
                else 0.0
            ),
            "recall": (
                sum(all_retrieval_metrics["recall"]) / len(all_retrieval_metrics["recall"])
                if all_retrieval_metrics["recall"]
                else 0.0
            ),
            "mrr": (
                sum(all_retrieval_metrics["mrr"]) / len(all_retrieval_metrics["mrr"])
                if all_retrieval_metrics["mrr"]
                else 0.0
            ),
            "ndcg": (
                sum(all_retrieval_metrics["ndcg"]) / len(all_retrieval_metrics["ndcg"])
                if all_retrieval_metrics["ndcg"]
                else 0.0
            ),
        }

        return AnalysisResult(
            chunk_stats=chunk_stats,
            retrieval_stats=avg_retrieval_stats,
            detailed_results=detailed_results,
            semantic_scores=semantic_scores,
            faithfulness_scores=faithfulness_scores,
            is_mock=self.config.get("provider") == "mock",
        )

    async def analyze_async(
        self, data: list[dict[str, Any]], show_progress: bool = True
    ) -> AnalysisResult:
        """
        Async analysis with parallel LLM processing.
        Much faster for large datasets with smart metrics.
        """
        logger.info("Starting async analysis of %d items", len(data))

        all_chunks = []
        all_retrieval_metrics = {"precision": [], "recall": [], "mrr": [], "ndcg": []}
        coherence_scores = []
        semantic_scores = []
        faithfulness_scores = []
        detailed_results = []

        # Process items in parallel with progress bar
        if show_progress:
            tasks = [self._process_item_async(item) for item in data]
            results = await atqdm.gather(*tasks, desc="Analyzing", unit="item")
        else:
            tasks = [self._process_item_async(item) for item in data]
            results = await asyncio.gather(*tasks)

        # Aggregate results
        for result in results:
            if result["chunks"]:
                all_chunks.extend(result["chunks"])
            if result["coherence"]:
                coherence_scores.extend(result["coherence"])
            if result["basic_metrics"]:
                for key in ["precision", "recall", "mrr", "ndcg"]:
                    all_retrieval_metrics[key].append(result["basic_metrics"][key])
            if result["semantic_score"] is not None:
                semantic_scores.append(result["semantic_score"])
            if result["faithfulness_score"] is not None:
                faithfulness_scores.append(result["faithfulness_score"])

            detailed_results.append(result["detailed"])

        chunk_stats = calculate_chunk_size_distribution(all_chunks)

        avg_retrieval_stats = {
            "precision": (
                sum(all_retrieval_metrics["precision"]) / len(all_retrieval_metrics["precision"])
                if all_retrieval_metrics["precision"]
                else 0.0
            ),
            "recall": (
                sum(all_retrieval_metrics["recall"]) / len(all_retrieval_metrics["recall"])
                if all_retrieval_metrics["recall"]
                else 0.0
            ),
            "mrr": (
                sum(all_retrieval_metrics["mrr"]) / len(all_retrieval_metrics["mrr"])
                if all_retrieval_metrics["mrr"]
                else 0.0
            ),
            "ndcg": (
                sum(all_retrieval_metrics["ndcg"]) / len(all_retrieval_metrics["ndcg"])
                if all_retrieval_metrics["ndcg"]
                else 0.0
            ),
        }

        logger.info("Async analysis completed successfully")

        return AnalysisResult(
            chunk_stats=chunk_stats,
            retrieval_stats=avg_retrieval_stats,
            detailed_results=detailed_results,
            semantic_scores=semantic_scores,
            faithfulness_scores=faithfulness_scores,
            is_mock=self.config.get("provider") == "mock",
        )

    async def _process_item_async(self, item: dict[str, Any]) -> dict[str, Any]:
        """Process a single item asynchronously."""
        retrieved = item.get("retrieved_contexts", [])
        ground_truth = item.get("ground_truth_contexts", [])
        response = item.get("response", "")
        query = item.get("query", "")

        # Chunking Analysis (sync, fast)
        item_coherence = [estimate_semantic_coherence(c) for c in retrieved]

        # Retrieval Analysis (sync, fast)
        basic_metrics = None
        if ground_truth:
            basic_metrics = calculate_retrieval_metrics(retrieved, ground_truth)

        # Smart Metrics (async, can be slow)
        semantic_score = None
        faithfulness_score = None
        answer_relevance_score = None
        toxicity_score = None
        context_precision = None
        context_recall = None
        plugin_metrics = {}

        if self.use_smart_metrics:
            # Semantic similarity (embedding-based, relatively fast)
            if ground_truth:
                semantic_score = self.semantic_matcher.calculate_similarity(retrieved, ground_truth)

            # Faithfulness (LLM-based, can be slow - make it async)
            if response:
                try:
                    f_score, f_reasoning = await self.faithfulness_scorer.ascore(
                        query, retrieved, response
                    )
                    faithfulness_score = f_score
                except Exception as e:
                    logger.error(f"Error calculating faithfulness: {e}")
                    faithfulness_score = 0.0

            # Answer Relevance
            if response:
                try:
                    ar_score, ar_reasoning = await self.answer_relevance_scorer.ascore(
                        query, response
                    )
                    answer_relevance_score = ar_score
                except Exception as e:
                    logger.error(f"Error calculating answer relevance: {e}")
                    answer_relevance_score = 0.0

            # Toxicity
            if response:
                try:
                    tox_score, tox_reasoning = await self.toxicity_scorer.ascore(response)
                    toxicity_score = tox_score
                except Exception as e:
                    logger.error(f"Error calculating toxicity: {e}")
                    toxicity_score = 1.0  # Default to safe

            # Context Precision (RAGAS-style)
            if retrieved and response:
                try:
                    context_precision = await self.context_precision_scorer.ascore(
                        query, retrieved, response
                    )
                except Exception as e:
                    logger.error(f"Error calculating context precision: {e}")
                    context_precision = None

            # Context Recall (RAGAS-style)
            if retrieved and ground_truth:
                try:
                    context_recall = await self.context_recall_scorer.ascore(
                        query, retrieved, ground_truth
                    )
                except Exception as e:
                    logger.error(f"Error calculating context recall: {e}")
                    context_recall = None

            # Calculate Plugin Metrics
            plugin_metrics = {}
            from raglint.plugins.loader import PluginLoader

            loader = PluginLoader.get_instance()
            loader.load_plugins()  # Ensure loaded

            for name, plugin in loader.metric_plugins.items():
                try:
                    # Check if plugin has calculate_async (most do)
                    if hasattr(plugin, "calculate_async"):
                        result = await plugin.calculate_async(
                            query=query,
                            response=response,
                            contexts=retrieved,
                            ground_truth_contexts=ground_truth,
                        )
                        # Extract score from result dict
                        if isinstance(result, dict):
                            plugin_metrics[name] = result.get("score", 0.0)
                        else:
                            plugin_metrics[name] = float(result)
                    else:
                        # Fallback to sync score
                        score = plugin.score(
                            query=query,
                            response=response,
                            retrieved_contexts=retrieved,
                            ground_truth_contexts=ground_truth,
                        )
                        plugin_metrics[name] = score
                except Exception as e:
                    logger.error(f"Error running plugin {name}: {e}")
                    plugin_metrics[name] = 0.0

        return {
            "chunks": retrieved,
            "coherence": item_coherence,
            "basic_metrics": basic_metrics,
            "semantic_score": semantic_score,
            "faithfulness_score": faithfulness_score,
            "plugin_metrics": plugin_metrics,  # Include plugin metrics
            "detailed": {
                "query": query,
                "metrics": basic_metrics,
                "coherence": item_coherence,
                "semantic_score": semantic_score,
                "faithfulness_score": (
                    faithfulness_score if self.use_smart_metrics and response else None
                ),
                "context_precision": context_precision,
                "context_recall": context_recall,
                "plugin_metrics": plugin_metrics,  # Include plugin metrics in detailed
                "answer_relevance_score": answer_relevance_score,
                "toxicity_score": toxicity_score,
            },
        }
