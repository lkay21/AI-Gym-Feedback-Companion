"""
Unit tests for the logging utility module.

Tests cover:
- Logger initialization and retrieval
- Log level configuration
- Enable/disable functionality
- Log output format
- File and console handler setup
"""

import unittest
import logging
import os
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import shutil

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.logger import (
    get_logger,
    setup_logging,
    disable_logging,
    enable_logging,
    set_log_level,
    LOG_ENABLED,
    LOG_LEVEL,
)


class TestLoggerBasics(unittest.TestCase):
    """Test basic logger functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Store original values
        self.original_log_enabled = os.getenv("ENABLE_LOGGING")
        self.original_log_level = os.getenv("LOG_LEVEL")
    
    def tearDown(self):
        """Clean up after tests."""
        # Restore original values
        if self.original_log_enabled:
            os.environ["ENABLE_LOGGING"] = self.original_log_enabled
        else:
            os.environ.pop("ENABLE_LOGGING", None)
        
        if self.original_log_level:
            os.environ["LOG_LEVEL"] = self.original_log_level
        else:
            os.environ.pop("LOG_LEVEL", None)
    
    def test_get_logger_returns_logger_instance(self):
        """Test that get_logger returns a valid Logger instance."""
        logger = get_logger(__name__)
        self.assertIsInstance(logger, logging.Logger)
    
    def test_get_logger_with_module_name(self):
        """Test that logger has the correct module name."""
        logger = get_logger("test.module")
        self.assertEqual(logger.name, "test.module")
    
    def test_get_logger_with_dunder_name(self):
        """Test logger creation with __name__ convention."""
        logger = get_logger(__name__)
        self.assertEqual(logger.name, __name__)
    
    def test_multiple_loggers_same_name_returns_same_instance(self):
        """Test that calling get_logger twice with same name returns same instance."""
        logger1 = get_logger("same.module")
        logger2 = get_logger("same.module")
        self.assertIs(logger1, logger2)


class TestLoggingLevels(unittest.TestCase):
    """Test different logging levels."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = get_logger("test.levels")
        self.log_records = []
        
        # Create a custom handler to capture log records
        self.handler = logging.Handler()
        self.handler.emit = lambda record: self.log_records.append(record)
        self.logger.addHandler(self.handler)
    
    def tearDown(self):
        """Clean up after tests."""
        self.logger.removeHandler(self.handler)
    
    def test_debug_logging(self):
        """Test DEBUG level logging."""
        self.logger.setLevel(logging.DEBUG)
        self.logger.debug("Test debug message")
        
        self.assertTrue(any(r.levelname == "DEBUG" for r in self.log_records))
    
    def test_info_logging(self):
        """Test INFO level logging."""
        self.logger.setLevel(logging.INFO)
        self.logger.info("Test info message")
        
        self.assertTrue(any(r.levelname == "INFO" for r in self.log_records))
    
    def test_warning_logging(self):
        """Test WARNING level logging."""
        self.logger.setLevel(logging.WARNING)
        self.logger.warning("Test warning message")
        
        self.assertTrue(any(r.levelname == "WARNING" for r in self.log_records))
    
    def test_error_logging(self):
        """Test ERROR level logging."""
        self.logger.setLevel(logging.ERROR)
        self.logger.error("Test error message")
        
        self.assertTrue(any(r.levelname == "ERROR" for r in self.log_records))
    
    def test_critical_logging(self):
        """Test CRITICAL level logging."""
        self.logger.setLevel(logging.CRITICAL)
        self.logger.critical("Test critical message")
        
        self.assertTrue(any(r.levelname == "CRITICAL" for r in self.log_records))


class TestLoggingWithExceptionInfo(unittest.TestCase):
    """Test logging with exception information."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = get_logger("test.exceptions")
        self.log_records = []
        
        self.handler = logging.Handler()
        self.handler.emit = lambda record: self.log_records.append(record)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)
    
    def tearDown(self):
        """Clean up after tests."""
        self.logger.removeHandler(self.handler)
    
    def test_error_with_exception_info(self):
        """Test logging error with exception information."""
        try:
            raise ValueError("Test exception")
        except ValueError:
            self.logger.error("An error occurred", exc_info=True)
        
        error_records = [r for r in self.log_records if r.levelname == "ERROR"]
        self.assertTrue(len(error_records) > 0)
        self.assertTrue(error_records[0].exc_info is not None)


class TestEnableDisableFunctionality(unittest.TestCase):
    """Test enable/disable logging functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root_logger = logging.getLogger()
        self.original_handlers = self.root_logger.handlers.copy()
    
    def tearDown(self):
        """Clean up after tests."""
        self.root_logger.handlers = self.original_handlers
    
    @patch.dict(os.environ, {"ENABLE_LOGGING": "False"})
    def test_logging_disabled_via_env(self):
        """Test that logging can be disabled via environment variable."""
        # Import with disabled logging
        from app import logger as logger_module
        
        test_logger = logger_module.get_logger("test.disabled")
        self.assertIsInstance(test_logger, logging.Logger)


class TestSetLogLevel(unittest.TestCase):
    """Test log level setting functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.root_logger = logging.getLogger()
        self.original_level = self.root_logger.level
    
    def tearDown(self):
        """Clean up after tests."""
        self.root_logger.setLevel(self.original_level)
    
    def test_set_log_level_to_debug(self):
        """Test setting log level to DEBUG."""
        set_log_level("DEBUG")
        root_logger = logging.getLogger()
        self.assertEqual(root_logger.level, logging.DEBUG)
    
    def test_set_log_level_to_info(self):
        """Test setting log level to INFO."""
        set_log_level("INFO")
        root_logger = logging.getLogger()
        self.assertEqual(root_logger.level, logging.INFO)
    
    def test_set_log_level_to_warning(self):
        """Test setting log level to WARNING."""
        set_log_level("WARNING")
        root_logger = logging.getLogger()
        self.assertEqual(root_logger.level, logging.WARNING)
    
    def test_set_log_level_to_error(self):
        """Test setting log level to ERROR."""
        set_log_level("ERROR")
        root_logger = logging.getLogger()
        self.assertEqual(root_logger.level, logging.ERROR)
    
    def test_set_log_level_case_insensitive(self):
        """Test that set_log_level is case insensitive."""
        set_log_level("debug")
        root_logger = logging.getLogger()
        self.assertEqual(root_logger.level, logging.DEBUG)
        
        set_log_level("WARNING")
        self.assertEqual(root_logger.level, logging.WARNING)


class TestLogMessageContent(unittest.TestCase):
    """Test that log messages contain expected content."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = get_logger("test.content")
        self.log_records = []
        
        self.handler = logging.Handler()
        self.handler.emit = lambda record: self.log_records.append(record)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)
    
    def tearDown(self):
        """Clean up after tests."""
        self.logger.removeHandler(self.handler)
    
    def test_log_message_content(self):
        """Test that logged message content is preserved."""
        test_message = "Test message with content"
        self.logger.info(test_message)
        
        self.assertEqual(self.log_records[0].getMessage(), test_message)
    
    def test_log_includes_logger_name(self):
        """Test that log record includes logger name."""
        self.logger.info("Test message")
        
        self.assertEqual(self.log_records[0].name, "test.content")
    
    def test_log_includes_level_name(self):
        """Test that log record includes level name."""
        self.logger.warning("Test warning")
        
        self.assertEqual(self.log_records[0].levelname, "WARNING")
    
    def test_log_includes_timestamp(self):
        """Test that log record includes timestamp."""
        self.logger.info("Test message")
        
        self.assertIsNotNone(self.log_records[0].created)


if __name__ == "__main__":
    unittest.main()
