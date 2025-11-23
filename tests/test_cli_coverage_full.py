"""
Full coverage tests for raglint.cli
"""
import pytest
from click.testing import CliRunner
from unittest.mock import patch, Mock, AsyncMock
from raglint.cli import cli

class TestCLICoverage:
    
    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_cost_estimate_missing_file(self, runner):
        """Test cost estimate with missing file."""
        result = runner.invoke(cli, ["cost", "estimate", "nonexistent.json"])
        assert result.exit_code != 0

    def test_cost_estimate_valid(self, runner):
        """Test cost estimate with valid file."""
        with runner.isolated_filesystem():
            with open("data.json", "w") as f:
                f.write('[{"query": "q"}]')
                
            result = runner.invoke(cli, ["cost", "estimate", "data.json"])
            assert result.exit_code == 0
            assert "Cost Estimation" in result.output

    def test_cost_estimate_invalid_json(self, runner):
        """Test cost estimate with invalid json."""
        with runner.isolated_filesystem():
            with open("data.json", "w") as f:
                f.write('invalid')
                
            result = runner.invoke(cli, ["cost", "estimate", "data.json"])
            assert result.exit_code == 1

    def test_generate_missing_file(self, runner):
        """Test generate with missing file."""
        result = runner.invoke(cli, ["generate", "missing.txt"])
        assert result.exit_code != 0

    def test_generate_success(self, runner):
        """Test generate success path."""
        with runner.isolated_filesystem():
            with open("source.txt", "w") as f:
                f.write("content")
                
            with patch("raglint.generation.TestsetGenerator") as MockGen:
                mock_instance = MockGen.return_value
                # Mock async method
                mock_instance.generate_from_file = AsyncMock(return_value=[{"q": "a"}])
                
                result = runner.invoke(cli, ["generate", "source.txt", "--api-key", "sk-test"])
                assert result.exit_code == 0
                assert "Successfully generated" in result.output

    def test_dashboard_command(self, runner):
        """Test dashboard command."""
        with patch("uvicorn.run") as mock_run:
            result = runner.invoke(cli, ["dashboard", "--port", "9000"])
            assert result.exit_code == 0
            mock_run.assert_called_once()
