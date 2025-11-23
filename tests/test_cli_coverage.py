"""
Tests for CLI coverage.
"""

import pytest
from click.testing import CliRunner
from unittest.mock import patch, Mock
from raglint.cli import cli

runner = CliRunner()


class TestCLI:
    """Test CLI commands."""
    
    def test_help(self):
        """Test help command."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "RAG Pipeline Quality Checker" in result.output
    
    def test_analyze_help(self):
        """Test analyze command help."""
        result = runner.invoke(cli, ["analyze", "--help"])
        assert result.exit_code == 0
        assert "Analyze a RAG pipeline" in result.output
    
    def test_dashboard_help(self):
        """Test dashboard command help."""
        result = runner.invoke(cli, ["dashboard", "--help"])
        assert result.exit_code == 0
        assert "Start the RAGLint Web Dashboard" in result.output
    
    def test_benchmark_help(self):
        """Test benchmark command help."""
        result = runner.invoke(cli, ["benchmark", "--help"])
        assert result.exit_code == 0
        assert "Run RAGLint on a standard benchmark dataset" in result.output
    
    def test_list_plugins_empty(self):
        """Test listing plugins when empty."""
        with patch('raglint.plugins.loader.PluginLoader.get_instance') as mock_get:
            mock_loader = Mock()
            mock_loader.get_all_plugins.return_value = []
            mock_get.return_value = mock_loader
            
            result = runner.invoke(cli, ["plugins", "list"])
            assert result.exit_code == 0
            assert "No plugins found" in result.output

    def test_list_plugins_found(self):
        """Test listing plugins when found."""
        with patch('raglint.plugins.loader.PluginLoader.get_instance') as mock_get:
            mock_loader = Mock()
            mock_loader.get_all_plugins.return_value = [{
                "name": "test-plugin",
                "version": "1.0",
                "type": "metric",
                "description": "Test plugin"
            }]
            mock_get.return_value = mock_loader
            
            result = runner.invoke(cli, ["plugins", "list"])
            assert result.exit_code == 0
            assert "Found 1 plugins" in result.output
            assert "test-plugin" in result.output
