"""
Extended CLI tests for verbose mode, logging, and error scenarios.
"""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from raglint.cli import cli


def test_analyze_verbose_mode(tmp_path):
    """Test CLI with verbose mode enabled."""
    # Create test data
    data_file = tmp_path / "data.json"
    data = [
        {
            "query": "Test",
            "retrieved_contexts": ["Context"],
            "ground_truth_contexts": ["Truth"],
            "response": "Response",
        }
    ]
    data_file.write_text(json.dumps(data))

    runner = CliRunner()
    result = runner.invoke(cli, ["analyze", str(data_file), "--verbose"])

    assert result.exit_code == 0
    # Verbose mode should show more output
    assert "INFO" in result.output or "Analysis" in result.output


def test_analyze_with_log_file(tmp_path):
    """Test CLI with log file creation."""
    data_file = tmp_path / "data.json"
    log_file = tmp_path / "test.log"

    data = [
        {
            "query": "Test",
            "retrieved_contexts": ["Context"],
            "ground_truth_contexts": ["Truth"],
            "response": "Response",
        }
    ]
    data_file.write_text(json.dumps(data))

    runner = CliRunner()
    result = runner.invoke(
        cli, ["analyze", str(data_file), "--log-file", str(log_file)]
    )

    assert result.exit_code == 0
    assert log_file.exists()
    log_content = log_file.read_text()
    assert len(log_content) > 0


def test_analyze_with_custom_config(tmp_path):
    """Test CLI with custom config file."""
    data_file = tmp_path / "data.json"
    config_file = tmp_path / "config.yml"

    data = [
        {
            "query": "Test",
            "retrieved_contexts": ["Context"],
            "ground_truth_contexts": ["Truth"],
            "response": "Response",
        }
    ]
    data_file.write_text(json.dumps(data))

    config_file.write_text(
        """
provider: mock
model_name: custom-model
"""
    )

    runner = CliRunner()
    result = runner.invoke(
        cli, ["analyze", str(data_file), "--config", str(config_file)]
    )

    assert result.exit_code == 0


def test_analyze_file_not_found():
    """Test CLI with non-existent file."""
    runner = CliRunner()
    result = runner.invoke(cli, ["analyze", "nonexistent.json"])

    # Click returns exit code 2 for usage errors (file not found)
    assert result.exit_code == 2
    assert "Error" in result.output or "does not exist" in result.output.lower()


def test_analyze_invalid_json_format(tmp_path):
    """Test CLI with malformed JSON."""
    data_file = tmp_path / "bad.json"
    data_file.write_text("{ invalid json }")

    runner = CliRunner()
    result = runner.invoke(cli, ["analyze", str(data_file)])

    assert result.exit_code == 1
    assert "JSON" in result.output or "Error" in result.output


def test_analyze_with_custom_output(tmp_path):
    """Test CLI with custom output path."""
    data_file = tmp_path / "data.json"
    output_file = tmp_path / "custom_report.html"

    data = [
        {
            "query": "Test",
            "retrieved_contexts": ["Context"],
            "ground_truth_contexts": ["Truth"],
            "response": "Response",
        }
    ]
    data_file.write_text(json.dumps(data))

    runner = CliRunner()
    result = runner.invoke(
        cli, ["analyze", str(data_file), "--output", str(output_file)]
    )

    assert result.exit_code == 0
    assert output_file.exists()
    content = output_file.read_text()
    assert "html" in content.lower()


def test_analyze_with_api_key_flag(tmp_path):
    """Test CLI with API key provided via flag."""
    data_file = tmp_path / "data.json"
    data = [
        {
            "query": "Test",
            "retrieved_contexts": ["Context"],
            "ground_truth_contexts": ["Truth"],
            "response": "Response",
        }
    ]
    data_file.write_text(json.dumps(data))

    runner = CliRunner()
    result = runner.invoke(
        cli, ["analyze", str(data_file), "--api-key", "test-key-123"]
    )

    # Should work (will use mock if OpenAI fails)
    assert result.exit_code == 0


def test_analyze_empty_data_file(tmp_path):
    """Test CLI with empty data array."""
    data_file = tmp_path / "empty.json"
    data_file.write_text("[]")

    runner = CliRunner()
    result = runner.invoke(cli, ["analyze", str(data_file)])

    assert result.exit_code == 0


def test_analyze_with_progress_disabled(tmp_path):
    """Test that progress bars can be controlled."""
    data_file = tmp_path / "data.json"
    data = [
        {
            "query": f"Test {i}",
            "retrieved_contexts": ["Context"],
            "ground_truth_contexts": ["Truth"],
            "response": "Response",
        }
        for i in range(5)
    ]
    data_file.write_text(json.dumps(data))

    runner = CliRunner()
    result = runner.invoke(cli, ["analyze", str(data_file), "--smart"])

    assert result.exit_code == 0


def test_cli_help_command():
    """Test that help command works."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "RAGLint" in result.output or "analyze" in result.output


def test_analyze_subcommand_help():
    """Test analyze subcommand help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["analyze", "--help"])

    assert result.exit_code == 0
    assert "analyze" in result.output.lower()
    assert "--smart" in result.output or "smart" in result.output.lower()


def test_config_snapshot():
    """Test the config snapshot command."""
    from click.testing import CliRunner
    from raglint.cli import cli
    from unittest.mock import patch, AsyncMock, MagicMock
    
    runner = CliRunner()
    
    # Mock database interactions
    with patch("raglint.dashboard.database.init_db", new_callable=AsyncMock) as mock_init:
        with patch("raglint.dashboard.database.SessionLocal") as mock_session_cls:
            mock_session = AsyncMock()
            mock_session.add = MagicMock()
            mock_session_cls.return_value.__aenter__.return_value = mock_session
            
            # Mock existing version check (return None)
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result
            
            # Create a dummy config file
            with runner.isolated_filesystem():
                with open("raglint.yaml", "w") as f:
                    f.write("provider: openai\n")
                
                result = runner.invoke(cli, ["config", "snapshot", "-m", "Test commit"])
                
                # Debug output if failed
                if result.exit_code != 0:
                    print(result.output)
                    print(result.exception)
                
                assert result.exit_code == 0
                assert "Created new configuration version" in result.output
                
                # Verify DB calls
                assert mock_init.called
                assert mock_session.add.called
                assert mock_session.commit.called
