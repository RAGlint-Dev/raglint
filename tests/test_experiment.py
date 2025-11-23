"""
Tests for A/B testing framework.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from raglint.experiment import ExperimentRunner, ComparisonResult
from raglint.core import AnalysisResult
from raglint.config import Config

class TestExperimentRunner:
    """Test ExperimentRunner."""
    
    @pytest.mark.asyncio
    async def test_run_experiment(self):
        """Test running an experiment."""
        # Mock configs
        config_a = Config()
        config_b = Config()
        
        runner = ExperimentRunner(config_a, config_b)
        
        # Mock analyzer
        with patch("raglint.experiment.RAGPipelineAnalyzer") as MockAnalyzer:
            mock_instance = MockAnalyzer.return_value
            
            # Mock results
            result_a = AnalysisResult(
                chunk_stats={"mean": 100}, 
                retrieval_stats={"precision": 0.8}, 
                detailed_results=[],
                semantic_scores=[0.8],
                faithfulness_scores=[0.8]
            )
            result_b = AnalysisResult(
                chunk_stats={"mean": 100}, 
                retrieval_stats={"precision": 0.9}, 
                detailed_results=[],
                semantic_scores=[0.9],
                faithfulness_scores=[0.9]
            )
            
            mock_instance.analyze_async = AsyncMock(side_effect=[result_a, result_b])
            
            data = [{"query": "test"}]
            result = await runner.run(data)
            
            assert isinstance(result, ComparisonResult)
            assert result.control_result == result_a
            assert result.treatment_result == result_b
            assert MockAnalyzer.call_count == 2

    def test_comparison_result_diff(self):
        """Test metric difference calculation."""
        result_a = AnalysisResult(
            chunk_stats={}, 
            retrieval_stats={"precision": 0.5, "recall": 1.0}, 
            detailed_results=[]
        )
        result_b = AnalysisResult(
            chunk_stats={}, 
            retrieval_stats={"precision": 0.75, "recall": 0.5}, 
            detailed_results=[]
        )
        
        comp = ComparisonResult(result_a, result_b)
        diffs = comp.metrics_diff
        
        # Precision: (0.75 - 0.5) / 0.5 = 0.5 -> 50%
        assert diffs["precision"] == 50.0
        
        # Recall: (0.5 - 1.0) / 1.0 = -0.5 -> -50%
        assert diffs["recall"] == -50.0

    def test_comparison_result_verdict(self):
        """Test verdict logic (visual check mostly, but ensure no errors)."""
        result_a = AnalysisResult(
            chunk_stats={}, 
            retrieval_stats={"overall_score": 0.5}, 
            detailed_results=[]
        )
        result_b = AnalysisResult(
            chunk_stats={}, 
            retrieval_stats={"overall_score": 0.8}, 
            detailed_results=[]
        )
        
        comp = ComparisonResult(result_a, result_b)
        
        # Just ensure it runs without error
        with patch("rich.console.Console.print") as mock_print:
            comp.print_summary()
            assert mock_print.called
