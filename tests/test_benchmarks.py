"""
Tests for benchmark datasets.
"""

import pytest
import os
import shutil
from unittest.mock import Mock, patch
from raglint.benchmarks import BenchmarkRegistry, SQUADBenchmark, CoQABenchmark, HotpotQABenchmark

# Fixture to clear cache before tests
@pytest.fixture(autouse=True)
def clear_cache():
    """Clear benchmark cache directory."""
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "raglint", "benchmarks")
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
    yield

class TestBenchmarkRegistry:
    """Test BenchmarkRegistry."""
    
    def test_list_benchmarks(self):
        """Test listing benchmarks."""
        benchmarks = BenchmarkRegistry.list_benchmarks()
        assert "squad" in benchmarks
        assert "coqa" in benchmarks
        assert "hotpotqa" in benchmarks
    
    def test_load_squad(self):
        """Test loading SQUAD."""
        data = BenchmarkRegistry.load("squad", subset_size=5)
        assert len(data) == 5
        assert "query" in data[0]
        assert "response" in data[0]
        
    def test_load_coqa(self):
        """Test loading CoQA."""
        data = BenchmarkRegistry.load("coqa", subset_size=5)
        assert len(data) == 5
        assert "metadata" in data[0]
        assert "history" in data[0]["metadata"]
        
    def test_load_hotpotqa(self):
        """Test loading HotpotQA."""
        data = BenchmarkRegistry.load("hotpotqa", subset_size=5)
        assert len(data) == 5
        assert "metadata" in data[0]
        assert "type" in data[0]["metadata"]
        
    def test_load_case_insensitive(self):
        """Test case insensitive loading."""
        data1 = BenchmarkRegistry.load("SQUAD", subset_size=2)
        data2 = BenchmarkRegistry.load("squad", subset_size=2)
        assert len(data1) == len(data2)

    def test_unknown_benchmark(self):
        """Test unknown benchmark error."""
        with pytest.raises(ValueError):
            BenchmarkRegistry.load("unknown")


class TestCoQABenchmark:
    """Test CoQA benchmark."""
    
    def test_generate_sample(self):
        """Test sample generation."""
        benchmark = CoQABenchmark(subset_size=10)
        data = benchmark.load()
        
        assert len(data) == 10
        # Check conversation history logic
        # First item usually has empty history if it's start of story
        # But our generator flattens them.
        
        # Check structure
        item = data[0]
        assert "query" in item
        assert "retrieved_contexts" in item
        assert "response" in item


class TestHotpotQABenchmark:
    """Test HotpotQA benchmark."""
    
    def test_generate_sample(self):
        """Test sample generation."""
        benchmark = HotpotQABenchmark(subset_size=10)
        data = benchmark.load()
        
        assert len(data) == 10
        
        # Check structure
        item = data[0]
        assert len(item["retrieved_contexts"]) >= 1
        assert item["metadata"]["source"] == "hotpotqa"

    def test_download_squad(self):
        """Test download_squad function (mocked)."""
        from raglint.benchmarks.squad import download_squad
        from unittest.mock import patch
        import os
        
        # Mock os.path.exists to return True (simulate cached file)
        with patch('os.path.exists', return_value=True):
            path = download_squad(split="dev", version="v2.0")
            assert "dev-v2.0.json" in path
            
        # Mock os.path.exists to return False, then True (simulate download)
        # We need to mock print to avoid clutter and verify it's called
        with patch('os.path.exists', side_effect=[False, False]), \
             patch('builtins.print') as mock_print, \
             patch('os.makedirs'):
            
            path = download_squad(split="train", version="v1.1")
            assert "train-v1.1.json" in path
            assert mock_print.called
