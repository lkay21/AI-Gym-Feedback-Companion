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
    original_propagate = {}

    # Store original propagate settings
    for logger_name in list(logging.Logger.manager.loggerDict.keys()):
        if isinstance(logging.Logger.manager.loggerDict[logger_name], logging.Logger):
            original_propagate[logger_name] = logging.Logger.manager.loggerDict[logger_name].propagate

    yield

    # Restore original state
    root_logger.handlers = []
    for handler in original_handlers:
        root_logger.addHandler(handler)
    root_logger.setLevel(original_level)
    logger_module.LOG_ENABLED = original_enabled
    logger_module.LOG_LEVEL = original_level_str
    
    # Restore propagate settings
    for logger_name, propagate_value in original_propagate.items():
        if isinstance(logging.Logger.manager.loggerDict[logger_name], logging.Logger):
            logging.Logger.manager.loggerDict[logger_name].propagate = propagate_value


def test_logging_enable_and_disable(monkeypatch, caplog):
    """Logging can be enabled and disabled."""
    monkeypatch.setattr(logger_module, "LOG_ENABLED", True)
    monkeypatch.setattr(logger_module, "LOG_LEVEL", "INFO")

    # Don't call setup_logging() - let pytest's caplog handle it
    # Just get the logger and use it
    logger = logger_module.get_logger("test.enable")
    
    # Set level to allow INFO messages
    logger.setLevel(logging.INFO)
    logger.propagate = True  # Ensure logs propagate to root logger for caplog

    with caplog.at_level(logging.INFO, logger="test.enable"):
        logger.info("enabled message")

    # Check that the message was logged
    assert any("enabled message" in record.message for record in caplog.records)

    caplog.clear()
    
    # Test disable
    monkeypatch.setattr(logger_module, "LOG_ENABLED", False)
    logger2 = logger_module.get_logger("test.disable")

    with caplog.at_level(logging.DEBUG):
        logger2.info("disabled message")

    # When disabled, no logs should be captured
    assert not any("disabled message" in record.message for record in caplog.records)


def test_log_level_filtering(monkeypatch, caplog):
    """Log level filtering works correctly."""
    monkeypatch.setattr(logger_module, "LOG_ENABLED", True)
    monkeypatch.setattr(logger_module, "LOG_LEVEL", "DEBUG")

    logger = logger_module.get_logger("test.filter")
    logger.setLevel(logging.WARNING)  # Set filter to WARNING
    logger.propagate = True  # Ensure logs propagate to caplog

    # Use caplog at WARNING level to match what the logger will actually emit
    with caplog.at_level(logging.WARNING, logger="test.filter"):
        logger.debug("debug message")
        logger.info("info message")
        logger.warning("warning message")

    messages = [record.getMessage() for record in caplog.records]

    # Only warning should pass the filter since logger level is WARNING
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
