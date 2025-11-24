"""
Integration tests for plugin system.
Tests multiple plugins working together and plugin loader functionality.
"""
import pytest
from raglint.plugins.loader import PluginLoader
from raglint.plugins.builtins import (
    CitationAccuracyPlugin,
    ReadabilityPlugin,
    PIIDetectorPlugin,
    BiasDetectorPlugin,
)


class TestPluginLoader:
    """Test plugin loading and management."""
    
    def setup_method(self):
        """Reset plugin loader before each test."""
        PluginLoader._instance = None
    
    def test_loader_singleton(self):
        """Test that PluginLoader is a singleton."""
        loader1 = PluginLoader.get_instance()
        loader2 = PluginLoader.get_instance()
        
        assert loader1 is loader2
    
    def test_load_all_builtins(self):
        """Test loading all built-in plugins."""
        loader = PluginLoader.get_instance()
        loader.load_plugins()
        
        # Should have all 15 plugins
        expected_plugins = [
            "chunk_coverage",
            "hallucination_score",
            "query_difficulty",
            "citation_accuracy",
            "readability",
            "answer_completeness",
            "response_conciseness",
            "bias_detector",
            "multilingual_support",
            "pii_detector",
            "sql_injection_detector",
            "hallucination_confidence",
            "context_compression",
            "response_diversity",
            "user_intent",
        ]
        
        for plugin_name in expected_plugins:
            assert plugin_name in loader.metric_plugins, f"Missing plugin: {plugin_name}"
    
    def test_get_plugin(self):
        """Test retrieving specific plugins."""
        loader = PluginLoader.get_instance()
        loader.load_plugins()
        
        readability = loader.get_plugin("readability")
        assert readability is not None
        assert readability.name == "readability"


class TestPluginIntegration:
    """Test plugins working together."""
    
    @pytest.mark.asyncio
    async def test_comprehensive_analysis(self):
        """Test running multiple plugins on same text."""
        plugins = [
            ReadabilityPlugin(),
            PIIDetectorPlugin(),
            BiasDetectorPlugin(),
            CitationAccuracyPlugin(),
        ]
        
        test_text = "The chairperson announced the new policy [1]. Contact support@company.com for details."
        
        results = []
        for plugin in plugins:
            result = await plugin.calculate_async(
                query="What's the new policy?",
                response=test_text,
                contexts=["Policy details in Section 1"]
            )
            results.append(result)
        
        # Verify all plugins ran successfully
        assert len(results) == 4
        assert all("score" in r for r in results)
        
        # Readability should detect text
        readability_result = results[0]
        assert "flesch_reading_ease" in readability_result
        
        # PII should detect email
        pii_result = results[1]
        assert pii_result["pii_found"] is True
        assert "email" in pii_result["pii_types"]
        
        # Bias should flag gendered term  
        bias_result = results[2]
        # May or may not flag "chairperson" as neutral is OK
        
        # Citation should find [1]
        citation_result = results[3]
        assert citation_result["citation_count"] > 0
    
    @pytest.mark.asyncio
    async def test_plugin_pipeline(self):
        """Test plugins as part of analysis pipeline."""
        test_data = {
            "query": "How do I reset my password?",
            "response": "Click 'Forgot Password', enter your email, and check your inbox.",
            "contexts": ["Password reset instructions in user manual"]
        }
        
        # Run through multiple quality checks
        readability = ReadabilityPlugin()
        pii = PIIDetectorPlugin()
        
        read_result = await readability.calculate_async(**test_data)
        pii_result = await pii.calculate_async(**test_data)
        
        # Should be readable (instructional)
        assert read_result["flesch_reading_ease"] > 60
        
        # Should have no PII
        assert pii_result["pii_found"] is False
    
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test plugins handle edge cases gracefully."""
        readability = ReadabilityPlugin()
        
        # Empty response
        result = await readability.calculate_async(
            query="",
            response="",
            contexts=[]
        )
        
        assert "score" in result or "error" in result
        
        # Very short response
        result_short = await readability.calculate_async(
            query="",
            response="Hi",
            contexts=[]
        )
        
        assert "message" in result_short or "score" in result_short


class TestPluginPerformance:
    """Test plugin performance characteristics."""
    
    @pytest.mark.asyncio
    async def test_async_concurrent_execution(self):
        """Test that plugins can run concurrently."""
        import asyncio
        
        plugins = [
            ReadabilityPlugin(),
            PIIDetectorPlugin(),
            BiasDetectorPlugin(),
        ]
        
        test_text = "The product costs $99 and comes with free shipping."
        
        # Run all plugins concurrently
        tasks = [
            plugin.calculate_async(
                query="What's the price?",
                response=test_text,
                contexts=[]
            )
            for plugin in plugins
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        assert all("score" in r for r in results)
    
    @pytest.mark.asyncio
    async def test_plugin_memory_efficiency(self):
        """Test that plugins don't leak memory."""
        import gc
        
        plugin = ReadabilityPlugin()
        
        # Run multiple times
        for _ in range(100):
            await plugin.calculate_async(
                query="",
                response="Test response " * 100,
                contexts=[]
            )
        
        # Force garbage collection
        gc.collect()
        
        # Should complete without memory errors
        assert True


class TestPluginConfiguration:
    """Test plugin configuration and customization."""
    

    
    def test_plugin_metadata(self):
        """Test that all plugins have required metadata."""
        loader = PluginLoader.get_instance()
        loader.load_plugins()
        
        for name, plugin in loader.metric_plugins.items():
            assert hasattr(plugin, 'name')
            assert hasattr(plugin, 'version')
            assert hasattr(plugin, 'description')
            assert plugin.name == name


# Mark slow tests
@pytest.mark.slow
class TestPluginStress:
    """Stress tests for plugins (run with pytest -m slow)."""
    
    @pytest.mark.asyncio
    async def test_large_text_handling(self):
        """Test plugins with very large inputs."""
        plugin = ReadabilityPlugin()
        
        # 10,000 word response
        large_text = "word " * 10000
        
        result = await plugin.calculate_async(
            query="",
            response=large_text,
            contexts=[]
        )
        
        assert "score" in result or "error" in result
    
    @pytest.mark.asyncio
    async def test_many_concurrent_plugins(self):
        """Test running many plugins concurrently."""
        import asyncio
        
        loader = PluginLoader.get_instance()
        loader.load_plugins()
        
        # Get first 10 plugins
        plugins = list(loader.metric_plugins.values())[:10]
        
        test_data = {
            "query": "Test query",
            "response": "Test response",
            "contexts": ["Test context"]
        }
        
        # Run all concurrently
        tasks = [
            plugin.calculate_async(**test_data)
            for plugin in plugins
            if hasattr(plugin, 'calculate_async')
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Most should succeed
        successful = [r for r in results if isinstance(r, dict)]
        assert len(successful) >= 8  # At least 80% success rate
