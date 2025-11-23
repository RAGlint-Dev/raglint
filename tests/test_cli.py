"""
Tests for the CLI module.
"""

import json
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from raglint.cli import cli


@pytest.fixture
def runner():
    """Create a CLI runner."""
    return CliRunner()


@pytest.fixture
def sample_data_file(tmp_path):
    """Create a temporary JSON file with sample data."""
    data = [
        {
            "query": "Test query",
            "retrieved_contexts": ["Context 1", "Context 2"],
            "response": "Test response",
            "ground_truth_contexts": ["Context 1"],
        }
    ]
    file_path = tmp_path / "test_data.json"
    with open(file_path, "w") as f:
        json.dump(data, f)
    return file_path


def test_cli_help(runner):
    """Test CLI help command."""
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "RAG Pipeline Quality Checker" in result.output


def test_analyze_command_basic(runner, sample_data_file):
    """Test basic analyze command."""
    result = runner.invoke(cli, ["analyze", str(sample_data_file)])
    assert result.exit_code == 0
    assert "Analysis complete" in result.output or "Chunk Size Mean" in result.output


def test_analyze_command_with_smart_flag(runner, sample_data_file):
    """Test analyze command with --smart flag."""
    result = runner.invoke(cli, ["analyze", str(sample_data_file), "--smart"])
    assert result.exit_code == 0
    # In mock mode, should complete successfully


def test_analyze_command_nonexistent_file(runner):
    """Test analyze command with non-existent file."""
    result = runner.invoke(cli, ["analyze", "nonexistent.json"])
    assert result.exit_code != 0


def test_analyze_command_invalid_json(runner, tmp_path):
    """Test analyze command with invalid JSON file."""
    invalid_file = tmp_path / "invalid.json"
    with open(invalid_file, "w") as f:
        f.write("{ invalid json }")

    result = runner.invoke(cli, ["analyze", str(invalid_file)])
    assert result.exit_code != 0


def test_analyze_command_with_output(runner, sample_data_file, tmp_path):
    """Test analyze command with custom output path."""
    output_file = tmp_path / "custom_report.html"
    result = runner.invoke(cli, ["analyze", str(sample_data_file), "--output", str(output_file)])
    assert result.exit_code == 0
    assert output_file.exists()


@patch("raglint.cli.RAGPipelineAnalyzer")
def test_analyze_handles_analyzer_error(mock_analyzer, runner, sample_data_file):
    """Test that CLI handles analyzer errors gracefully."""
    mock_analyzer.return_value.analyze.side_effect = Exception("Test error")

    result = runner.invoke(cli, ["analyze", str(sample_data_file)])
    assert result.exit_code != 0
    assert "error" in result.output.lower() or "Error" in result.output
