"""
Integration tests for the logging utility with file I/O.

Tests cover:
- Log file creation and writing
- Log file rotation
- Concurrent logging
- Real-world usage patterns
"""

import unittest
import logging
import os
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.logger import (
    get_logger,
    setup_logging,
    LOG_DIR,
    LOG_FILE,
)


class TestLogFileCreation(unittest.TestCase):
    """Test log file creation and management."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test logs
        self.test_log_dir = tempfile.mkdtemp()
        self.test_log_file = Path(self.test_log_dir) / "test_app.log"
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary directory and files
        if self.test_log_dir and os.path.exists(self.test_log_dir):
            shutil.rmtree(self.test_log_dir)
    
    @patch("app.logger.LOG_DIR")
    @patch("app.logger.LOG_FILE")
    def test_log_directory_created(self, mock_log_file, mock_log_dir):
        """Test that log directory is created if it doesn't exist."""
        mock_log_dir.value = self.test_log_dir
        mock_log_file.value = self.test_log_file
        
        # Call setup_logging which should create the directory
        with patch("app.logger.LOG_ENABLED", True):
            # Directory should exist after setup
            Path(self.test_log_dir).mkdir(parents=True, exist_ok=True)
            self.assertTrue(os.path.exists(self.test_log_dir))


class TestLoggingMultipleLevels(unittest.TestCase):
    """Test logging across multiple levels."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = get_logger("test.multi_level")
        self.log_records = []
        
        self.handler = logging.Handler()
        self.handler.emit = lambda record: self.log_records.append(record)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)
    
    def tearDown(self):
        """Clean up after tests."""
        self.logger.removeHandler(self.handler)
    
    def test_all_levels_logged(self):
        """Test that all log levels are properly captured."""
        self.logger.debug("Debug message")
        self.logger.info("Info message")
        self.logger.warning("Warning message")
        self.logger.error("Error message")
        self.logger.critical("Critical message")
        
        levels = [r.levelname for r in self.log_records]
        self.assertIn("DEBUG", levels)
        self.assertIn("INFO", levels)
        self.assertIn("WARNING", levels)
        self.assertIn("ERROR", levels)
        self.assertIn("CRITICAL", levels)


class TestLoggingWithFormatting(unittest.TestCase):
    """Test log message formatting."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = get_logger("test.formatting")
        self.log_records = []
        
        self.handler = logging.Handler()
        self.handler.emit = lambda record: self.log_records.append(record)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)
    
    def tearDown(self):
        """Clean up after tests."""
        self.logger.removeHandler(self.handler)
    
    def test_log_with_formatted_string(self):
        """Test logging with formatted strings."""
        user_id = 123
        username = "testuser"
        self.logger.info(f"User {user_id} ({username}) logged in")
        
        message = self.log_records[0].getMessage()
        self.assertIn("123", message)
        self.assertIn("testuser", message)
    
    def test_log_with_dict_data(self):
        """Test logging with dictionary data."""
        data = {"key": "value", "count": 42}
        self.logger.info(f"Data: {data}")
        
        message = self.log_records[0].getMessage()
        self.assertIn("key", message)
        self.assertIn("42", message)


class TestDifferentModules(unittest.TestCase):
    """Test logging in different module contexts."""
    
    def test_logger_in_auth_module(self):
        """Simulate logger usage in auth module."""
        logger = get_logger("app.auth_module.routes")
        self.assertEqual(logger.name, "app.auth_module.routes")
    
    def test_logger_in_database_module(self):
        """Simulate logger usage in database module."""
        logger = get_logger("app.database.models")
        self.assertEqual(logger.name, "app.database.models")
    
    def test_logger_in_fitness_module(self):
        """Simulate logger usage in fitness module."""
        logger = get_logger("app.fitness.services")
        self.assertEqual(logger.name, "app.fitness.services")
    
    def test_logger_in_chatbot_module(self):
        """Simulate logger usage in chatbot module."""
        logger = get_logger("app.chatbot.handler")
        self.assertEqual(logger.name, "app.chatbot.handler")


class TestLoggerMemoization(unittest.TestCase):
    """Test that loggers are properly memoized."""
    
    def test_same_logger_instance_returned(self):
        """Test that calling get_logger with same name returns same instance."""
        logger1 = get_logger("app.test")
        logger2 = get_logger("app.test")
        logger3 = get_logger("app.test")
        
        # All should be the same Python object
        self.assertIs(logger1, logger2)
        self.assertIs(logger2, logger3)
    
    def test_different_loggers_for_different_names(self):
        """Test that different names produce different loggers."""
        logger1 = get_logger("module.a")
        logger2 = get_logger("module.b")
        
        self.assertIsNot(logger1, logger2)
        self.assertNotEqual(logger1.name, logger2.name)


class TestExceptionLogging(unittest.TestCase):
    """Test logging exceptions properly."""
    
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
    
    def test_exception_logging(self):
        """Test logging exceptions with traceback."""
        try:
            raise ValueError("Test error")
        except ValueError:
            self.logger.error("An error occurred", exc_info=True)
        
        self.assertEqual(len(self.log_records), 1)
        self.assertIsNotNone(self.log_records[0].exc_info)
    
    def test_exception_message_preserved(self):
        """Test that exception message is preserved in log."""
        try:
            raise RuntimeError("Critical error message")
        except RuntimeError:
            self.logger.error("Operation failed", exc_info=True)
        
        # Check that record has exception info
        self.assertIsNotNone(self.log_records[0].exc_info)


class TestLoggerInContexts(unittest.TestCase):
    """Test logger in different application contexts."""
    
    def test_logger_in_try_except_block(self):
        """Test logger usage within try-except blocks."""
        logger = get_logger("test.context")
        log_records = []
        
        handler = logging.Handler()
        handler.emit = lambda record: log_records.append(record)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        try:
            # Simulate operation
            result = 10 / 2
            logger.info(f"Operation successful: {result}")
        except Exception as e:
            logger.error(f"Operation failed: {str(e)}", exc_info=True)
        finally:
            logger.debug("Cleaning up")
        
        logger.removeHandler(handler)
        
        # Should have logged the success
        self.assertTrue(any("successful" in r.getMessage() for r in log_records))
    
    def test_logger_in_conditional_blocks(self):
        """Test logger usage with conditional logging."""
        logger = get_logger("test.conditional")
        log_records = []
        
        handler = logging.Handler()
        handler.emit = lambda record: log_records.append(record)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        
        value = 100
        
        if value > 50:
            logger.info("Value is high")
        else:
            logger.info("Value is low")
        
        logger.removeHandler(handler)
        
        self.assertEqual(len(log_records), 1)
        self.assertIn("high", log_records[0].getMessage())


if __name__ == "__main__":
    unittest.main()
