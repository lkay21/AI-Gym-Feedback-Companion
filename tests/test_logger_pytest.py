"""
Pytest tests for logging utility behavior.

Covers:
- Enable/disable logging
- Level filtering
- No logs when disabled
"""

import logging
import pytest

import app.logger as logger_module


@pytest.fixture(autouse=True)
def reset_logging_state():
    """Reset logging state before and after each test."""
    root_logger = logging.getLogger()
    original_handlers = list(root_logger.handlers)
    original_level = root_logger.level
    original_enabled = logger_module.LOG_ENABLED
    original_level_str = logger_module.LOG_LEVEL

    root_logger.handlers = []

    yield

    root_logger.handlers = []
    for handler in original_handlers:
        root_logger.addHandler(handler)
    root_logger.setLevel(original_level)
    logger_module.LOG_ENABLED = original_enabled
    logger_module.LOG_LEVEL = original_level_str


def test_logging_enable_and_disable(monkeypatch, caplog):
    """Logging can be enabled and disabled."""
    monkeypatch.setattr(logger_module, "LOG_ENABLED", True)
    monkeypatch.setattr(logger_module, "LOG_LEVEL", "DEBUG")

    logger_module.setup_logging()
    logger = logger_module.get_logger("test.enable")

    with caplog.at_level(logging.DEBUG):
        logger.info("enabled message")

    assert "enabled message" in caplog.text

    caplog.clear()
    logger_module.disable_logging()
    logger = logger_module.get_logger("test.disable")

    with caplog.at_level(logging.DEBUG):
        logger.info("disabled message")

    assert caplog.records == []


def test_log_level_filtering(monkeypatch, caplog):
    """Log level filtering works correctly."""
    monkeypatch.setattr(logger_module, "LOG_ENABLED", True)
    monkeypatch.setattr(logger_module, "LOG_LEVEL", "DEBUG")

    logger_module.setup_logging()
    logger_module.set_log_level("WARNING")
    logger = logger_module.get_logger("test.filter")

    with caplog.at_level(logging.DEBUG):
        logger.debug("debug message")
        logger.info("info message")
        logger.warning("warning message")

    messages = [record.getMessage() for record in caplog.records]

    assert "warning message" in messages
    assert "debug message" not in messages
    assert "info message" not in messages


def test_no_logs_emitted_when_disabled(monkeypatch, caplog):
    """No logs are emitted when logging is disabled."""
    monkeypatch.setattr(logger_module, "LOG_ENABLED", False)

    logger_module.disable_logging()
    logger = logger_module.get_logger("test.disabled")

    with caplog.at_level(logging.DEBUG):
        logger.error("should not appear")

    assert caplog.records == []
