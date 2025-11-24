"""
Tests for logging module.
"""

import pytest
import logging
import pytest
import logging
from raglint.logging import get_logger, setup_logging


def test_get_logger():
    """Test get_logger returns logger instance."""
    logger = get_logger("test_module")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "raglint.test_module"


def test_configure_logging_basic():
    """Test basic logging configuration."""
    setup_logging(level="INFO")
    logger = get_logger("test")
    assert logger.level <= logging.INFO or logging.root.level <= logging.INFO


def test_configure_logging_verbose():
    """Test verbose logging configuration."""
    setup_logging(verbose=True)
    logger = get_logger("verbose_test")
    # Should configure successfully
    assert logger is not None


def test_logger_outputs_messages(caplog):
    """Test logger actually outputs messages."""
    logger = get_logger("output_test")
    logger.setLevel(logging.INFO)
    
    with caplog.at_level(logging.INFO):
        logger.info("Test message")
    
    assert "Test message" in caplog.text


def test_multiple_loggers():
    """Test multiple loggers can coexist."""
    logger1 = get_logger("module1")
    logger2 = get_logger("module2")
    
    assert logger1.name != logger2.name
    assert logger1 is not logger2
