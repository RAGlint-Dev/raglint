"""
Tests for configuration module.
"""

import pytest
import os
from pathlib import Path
from raglint.config import Config


def test_config_initialization_defaults():
    """Test Config initializes with default values."""
    config = Config()
    assert config.provider == "mock"
    assert config.model_name is not None


def test_config_from_dict():
    """Test Config can be created from dictionary."""
    config_dict = {
        "provider": "openai",
        "model_name": "gpt-4",
        "openai_api_key": "test-key"
    }
    config = Config.from_dict(config_dict)
    assert config.provider == "openai"
    assert config.model_name == "gpt-4"
    assert config.openai_api_key == "test-key"


def test_config_to_dict():
    """Test Config can be converted to dictionary."""
    config = Config(provider="ollama", model_name="llama2")
    config_dict = config.as_dict()
    assert isinstance(config_dict, dict)
    assert config_dict["provider"] == "ollama"
    assert config_dict["model_name"] == "llama2"


def test_config_from_yaml(tmp_path):
    """Test Config can be loaded from YAML file."""
    yaml_content = """
provider: openai
model_name: gpt-3.5-turbo
openai_api_key: test-api-key
"""
    yaml_file = tmp_path / "config.yaml"
    yaml_file.write_text(yaml_content)
    
    config = Config.from_yaml(str(yaml_file))
    assert config.provider == "openai"
    assert config.model_name == "gpt-3.5-turbo"


def test_config_provider_validation():
    """Test Config validates provider."""
    config = Config(provider="openai")
    assert config.provider == "openai"
    
    config2 = Config(provider="ollama")
    assert config2.provider == "ollama"


def test_config_with_environment_variables(monkeypatch):
    """Test Config uses environment variables."""
    monkeypatch.setenv("OPENAI_API_KEY", "env-api-key")
    
    config = Config(provider="openai")
    # Should pick up from environment
    assert os.getenv("OPENAI_API_KEY") == "env-api-key"


def test_config_metrics_list():
    """Test Config can specify metrics list."""
    config = Config(metrics=["faithfulness", "relevance"])
    assert "faithfulness" in config.metrics
    assert "relevance" in config.metrics
