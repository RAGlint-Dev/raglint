"""
Tests for CLI edge cases and error handling.
"""

import json
import sys
from unittest.mock import patch, MagicMock
from click.testing import CliRunner
from raglint.cli import cli, setup_logging


def test_setup_logging_verbose():
    """Test logging setup with verbose flag."""
    with patch("raglint.logging.logging") as mock_logging:
        # Mock the root logger to verify handlers are added
        mock_root = MagicMock()
        mock_logging.getLogger.return_value = mock_root
        
        setup_logging(level="DEBUG", verbose=True)
        
        # Check that handlers were added to the logger
        assert mock_root.addHandler.called


def test_setup_logging_file():
    """Test logging setup with file output."""
    with patch("raglint.logging.logging") as mock_logging:
        mock_root = MagicMock()
        mock_logging.getLogger.return_value = mock_root
        mock_handler = MagicMock()
        mock_logging.FileHandler.return_value = mock_handler
        
        setup_logging(level="INFO", log_file="test.log")
        
        mock_logging.FileHandler.assert_called_with("test.log")
        mock_root.addHandler.assert_called_with(mock_handler)


def test_cli_compare_command(tmp_path):
    """Test the compare command."""
    # Create two dummy report files
    file1 = tmp_path / "report1.json"
    file2 = tmp_path / "report2.json"
    
    data1 = [{"query": "q", "retrieved_contexts": ["c"], "response": "r", "ground_truth_contexts": ["g"]}]
    data2 = [{"query": "q", "retrieved_contexts": ["c"], "response": "r", "ground_truth_contexts": ["g"]}]
    
    file1.write_text(json.dumps(data1))
    file2.write_text(json.dumps(data2))
    
    runner = CliRunner()
    with patch("raglint.cli.RAGPipelineAnalyzer") as MockAnalyzer:
        # Mock analyzer to return results with stats
        mock_instance = MockAnalyzer.return_value
        mock_instance.analyze.return_value = MagicMock(
            retrieval_stats={"precision": 0.8, "recall": 0.8}
        )
        
        result = runner.invoke(cli, ["compare", str(file1), str(file2)])
        
        assert result.exit_code == 0
        assert "Comparison Report" in result.output
        assert "No Regressions" in result.output


def test_cli_compare_regression(tmp_path):
    """Test the compare command with regression."""
    file1 = tmp_path / "report1.json"
    file2 = tmp_path / "report2.json"
    
    file1.write_text(json.dumps([]))
    file2.write_text(json.dumps([]))
    
    runner = CliRunner()
    with patch("raglint.cli.RAGPipelineAnalyzer") as MockAnalyzer:
        mock_instance = MockAnalyzer.return_value
        # First call returns high stats, second call returns low stats
        mock_instance.analyze.side_effect = [
            MagicMock(retrieval_stats={"precision": 0.9, "recall": 0.9}),
            MagicMock(retrieval_stats={"precision": 0.5, "recall": 0.5})
        ]
        
        result = runner.invoke(cli, ["compare", str(file1), str(file2)])
        
        assert result.exit_code == 0
        assert "Regression Detected" in result.output


def test_analyze_with_invalid_json_structure(tmp_path):
    """Test analyze with JSON that is not a list."""
    data_file = tmp_path / "invalid_struct.json"
    data_file.write_text('{"not": "a list"}')
    
    runner = CliRunner()
    result = runner.invoke(cli, ["analyze", str(data_file)])
    
    assert result.exit_code == 1
    assert "must be a list" in result.output or "Error" in result.output


def test_analyze_with_mock_warning(tmp_path):
    """Test that mock warning is displayed when smart metrics enabled with mock provider."""
    data_file = tmp_path / "data.json"
    data_file.write_text('[{"query": "q", "response": "r"}]')
    
    runner = CliRunner()
    result = runner.invoke(cli, ["analyze", str(data_file), "--smart"])
    
    assert result.exit_code == 0
    assert "WARNING: Running in MOCK MODE" in result.output
