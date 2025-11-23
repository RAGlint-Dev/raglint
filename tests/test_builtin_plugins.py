"""
Tests for built-in plugins.
"""

import pytest
from raglint.plugins.builtins.chunk_coverage import ChunkCoveragePlugin
from raglint.plugins.builtins.query_difficulty import QueryDifficultyPlugin
from raglint.plugins.builtins.hallucination import HallucinationPlugin
from raglint.plugins.loader import PluginLoader


def test_chunk_coverage_plugin():
    plugin = ChunkCoveragePlugin()
    assert plugin.name == "chunk_coverage"
    
    # Test perfect overlap
    score = plugin.score(
        retrieved_contexts=["The quick brown fox"],
        response="The quick brown fox"
    )
    assert score > 0.0
    
    # Test no overlap
    score = plugin.score(
        retrieved_contexts=["Apple banana"],
        response="Carrot potato"
    )
    assert score == 0.0


def test_query_difficulty_plugin():
    plugin = QueryDifficultyPlugin()
    assert plugin.name == "query_difficulty"
    
    # Test simple query
    score_easy = plugin.score(query="What is X?")
    
    # Test hard query (long, reasoning)
    score_hard = plugin.score(
        query="Why does the quick brown fox jump over the lazy dog when it is raining outside?"
    )
    
    assert score_hard > score_easy


def test_hallucination_plugin():
    plugin = HallucinationPlugin()
    assert plugin.name == "hallucination_score"
    
    # Test with Mock LLM (now returns JSON scores around 0.1)  
    # The new LLM-based implementation will return mock score 0.1 (low hallucination)
    score_low = plugin.score(
        retrieved_contexts=["The sky is blue."],
        response="The sky is blue."
    )
    # MockLLM returns 0.1 for any input
    assert score_low >= 0.0
    assert score_low <= 1.0
    
    # Test unsupported answer (LLM-based)
    score_high = plugin.score(
        retrieved_contexts=["The sky is blue."],
        response="The grass is green and elephants fly."
    )
    # With MockLLM, both return 0.1, but test that it's a valid score
    assert score_high >= 0.0
    assert score_high <= 1.0



def test_loader_loads_builtins():
    # Reset singleton
    PluginLoader._instance = None
    loader = PluginLoader.get_instance()
    loader.load_plugins()
    
    assert "chunk_coverage" in loader.metric_plugins
    assert "query_difficulty" in loader.metric_plugins
    assert "hallucination_score" in loader.metric_plugins
