"""
Tests for plugin loader and registry.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from raglint.plugins.loader import PluginLoader, PluginRegistry


def test_plugin_loader_singleton():
    """Test PluginLoader follows singleton pattern."""
    loader1 = PluginLoader.get_instance()
    loader2 = PluginLoader.get_instance()
    assert loader1 is loader2


def test_plugin_loader_initialization():
    """Test PluginLoader initializes correctly."""
    loader = PluginLoader.get_instance()
    assert loader.plugins is not None
    assert isinstance(loader.plugins, dict)


def test_plugin_loader_load_builtin_plugins():
    """Test loading built-in plugins."""
    loader = PluginLoader.get_instance()
    loader.load_plugins()
    
    # Check some built-in plugins are loaded
    builtin_names = [p.name for p in loader.plugins.values()]
    assert any('hallucination' in name or 'bias' in name for name in builtin_names)


def test_plugin_loader_get_plugin():
    """Test retrieving a loaded plugin."""
    loader = PluginLoader.get_instance()
    loader.load_plugins()
    
    # Try to get a plugin (may or may not exist depending on load)
    plugins_list = list(loader.plugins.keys())
    if plugins_list:
        first_plugin = loader.get_plugin(plugins_list[0])
        assert first_plugin is not None


def test_plugin_loader_list_plugins():
    """Test listing all loaded plugins."""
    loader = PluginLoader.get_instance()
    loader.load_plugins()
    
    plugins = loader.list_plugins()
    assert isinstance(plugins, list)


def test_plugin_loader_validate_safety():
    """Test plugin safety validation with AST."""
    loader = PluginLoader.get_instance()
    
    # Create a temporary safe plugin file
    safe_code = '''
class TestPlugin:
    name = "test"
    def evaluate(self, query, context, response):
        return 1.0
'''
    
    temp_path = Path("/tmp/test_safe_plugin.py")
    temp_path.write_text(safe_code)
    
    # Should pass safety check
    is_safe = loader._validate_plugin_safety(temp_path)
    assert is_safe is True
    
    temp_path.unlink()  # Clean up


def test_plugin_loader_validate_unsafe():
    """Test plugin safety validation rejects dangerous imports."""
    loader = PluginLoader.get_instance()
    
    # Create a temporary unsafe plugin file
    unsafe_code = '''
import os
import subprocess

class TestPlugin:
    def evaluate(self, query, context, response):
        os.system("echo bad")
        return 1.0
'''
    
    temp_path = Path("/tmp/test_unsafe_plugin.py")
    temp_path.write_text(unsafe_code)
    
    # Should fail safety check
    is_safe = loader._validate_plugin_safety(temp_path)
    assert is_safe is False
    
    temp_path.unlink()  # Clean up


# PluginRegistry Tests
def test_plugin_registry_initialization():
    """Test PluginRegistry initializes."""
    registry = PluginRegistry()
    assert registry is not None


def test_plugin_registry_list_available():
    """Test listing available plugins from registry."""
    registry = PluginRegistry()
    plugins = registry.list_available_plugins()
    
    assert isinstance(plugins, list)
    assert len(plugins) > 0
    
    # Check structure
    if plugins:
        plugin = plugins[0]
        assert 'name' in plugin
        assert 'version' in plugin
        assert 'description' in plugin


@patch('httpx.get')
def test_plugin_registry_install_success(mock_get):
    """Test successful plugin installation."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '''
class TestPlugin:
    name = "test_plugin"
    version = "1.0.0"
    def evaluate(self, query, context, response):
        return 1.0
'''
    mock_get.return_value = mock_response
    
    registry = PluginRegistry()
    success = registry.install_plugin("test-plugin", target_dir="/tmp/test_plugins")
    
    assert success is True


@patch('httpx.get')
def test_plugin_registry_install_fallback(mock_get):
    """Test plugin installation falls back to mock generation."""
    mock_get.side_effect = Exception("Network error")
    
    registry = PluginRegistry()
    success = registry.install_plugin("test-plugin", target_dir="/tmp/test_plugins")
    
    # Should still succeed with mock
    assert success is True
