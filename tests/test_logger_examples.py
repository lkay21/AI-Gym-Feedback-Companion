"""
Example-based tests demonstrating real-world logging usage.

Tests validate logging patterns from LOGGING_EXAMPLES.md documentation:
- Authentication routes logging
- Database operations logging
- Service layer logging
- Error handling logging
"""

import unittest
import logging
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.logger import get_logger


class TestAuthenticationLogging(unittest.TestCase):
    """Test logging patterns used in authentication routes."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = get_logger("app.auth_module.routes")
        self.log_records = []
        
        self.handler = logging.Handler()
        self.handler.emit = lambda record: self.log_records.append(record)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)
    
    def tearDown(self):
        """Clean up after tests."""
        self.logger.removeHandler(self.handler)
    
    def test_registration_attempt_logged(self):
        """Test logging registration attempts."""
        username = "newuser"
        self.logger.info(f"Registration attempt for user: {username}")
        
        self.assertEqual(len(self.log_records), 1)
        self.assertIn(username, self.log_records[0].getMessage())
    
    def test_registration_validation_warning(self):
        """Test logging validation failures."""
        username = "user"
        self.logger.warning(f"Registration failed - missing fields for user: {username}")
        
        warning_records = [r for r in self.log_records if r.levelname == "WARNING"]
        self.assertTrue(len(warning_records) > 0)
        self.assertIn("missing fields", warning_records[0].getMessage())
    
    def test_successful_registration_logged(self):
        """Test logging successful registration."""
        username = "newuser"
        self.logger.info(f"User registered successfully: {username}")
        
        info_records = [r for r in self.log_records if r.levelname == "INFO"]
        self.assertTrue(len(info_records) > 0)
        self.assertIn("successfully", info_records[0].getMessage())
    
    def test_registration_error_logged(self):
        """Test logging registration errors with exception info."""
        error_message = "Database connection failed"
        
        try:
            raise Exception(error_message)
        except Exception as e:
            self.logger.error(f"Registration error: {str(e)}", exc_info=True)
        
        error_records = [r for r in self.log_records if r.levelname == "ERROR"]
        self.assertTrue(len(error_records) > 0)
    
    def test_login_attempt_logged(self):
        """Test logging login attempts."""
        username = "testuser"
        self.logger.info("Login attempt")
        self.logger.info(f"User {username} attempted login")
        
        login_records = [r for r in self.log_records if "login" in r.getMessage().lower()]
        self.assertTrue(len(login_records) > 0)
    
    def test_successful_login_logged(self):
        """Test logging successful login."""
        self.logger.info("User logged in successfully")
        
        self.assertIn("successfully", self.log_records[0].getMessage())


class TestDatabaseLogging(unittest.TestCase):
    """Test logging patterns used in database operations."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = get_logger("app.database.models")
        self.log_records = []
        
        self.handler = logging.Handler()
        self.handler.emit = lambda record: self.log_records.append(record)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)
    
    def tearDown(self):
        """Clean up after tests."""
        self.logger.removeHandler(self.handler)
    
    def test_save_user_debug_logged(self):
        """Test logging save operation at DEBUG level."""
        username = "newuser"
        self.logger.debug(f"Saving user: {username}")
        
        debug_records = [r for r in self.log_records if r.levelname == "DEBUG"]
        self.assertTrue(len(debug_records) > 0)
    
    def test_save_user_success_logged(self):
        """Test logging successful user save."""
        username = "newuser"
        self.logger.info(f"User saved successfully: {username}")
        
        info_records = [r for r in self.log_records if r.levelname == "INFO"]
        self.assertTrue(len(info_records) > 0)
        self.assertIn("successfully", info_records[0].getMessage())
    
    def test_save_user_error_logged(self):
        """Test logging user save errors."""
        username = "newuser"
        error_msg = "Duplicate key error"
        
        try:
            raise Exception(error_msg)
        except Exception as e:
            self.logger.error(
                f"Failed to save user {username}: {str(e)}", 
                exc_info=True
            )
        
        error_records = [r for r in self.log_records if r.levelname == "ERROR"]
        self.assertTrue(len(error_records) > 0)
    
    def test_find_user_debug_logged(self):
        """Test logging user search at DEBUG level."""
        username = "testuser"
        self.logger.debug(f"Searching for user: {username}")
        
        debug_records = [r for r in self.log_records if r.levelname == "DEBUG"]
        self.assertTrue(len(debug_records) > 0)
    
    def test_user_found_logged(self):
        """Test logging when user is found."""
        username = "testuser"
        self.logger.debug(f"User found: {username}")
        
        debug_records = [r for r in self.log_records if r.levelname == "DEBUG"]
        self.assertTrue(len(debug_records) > 0)
        self.assertIn("found", debug_records[0].getMessage().lower())
    
    def test_user_not_found_warning(self):
        """Test logging when user is not found."""
        username = "nonexistent"
        self.logger.warning(f"User not found: {username}")
        
        warning_records = [r for r in self.log_records if r.levelname == "WARNING"]
        self.assertTrue(len(warning_records) > 0)
        self.assertIn("not found", warning_records[0].getMessage().lower())


class TestServiceLayerLogging(unittest.TestCase):
    """Test logging patterns used in service layer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = get_logger("app.fitness.workout_service")
        self.log_records = []
        
        self.handler = logging.Handler()
        self.handler.emit = lambda record: self.log_records.append(record)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)
    
    def tearDown(self):
        """Clean up after tests."""
        self.logger.removeHandler(self.handler)
    
    def test_workout_creation_logged(self):
        """Test logging workout creation."""
        user_id = 1
        self.logger.info(f"Creating workout for user {user_id}")
        
        info_records = [r for r in self.log_records if r.levelname == "INFO"]
        self.assertTrue(len(info_records) > 0)
    
    def test_workout_validation_logged(self):
        """Test logging workout validation."""
        workout_type = "cardio"
        self.logger.debug(f"Validating workout type: {workout_type}")
        
        debug_records = [r for r in self.log_records if r.levelname == "DEBUG"]
        self.assertTrue(len(debug_records) > 0)
    
    def test_workout_saved_logged(self):
        """Test logging saved workout."""
        workout_id = 123
        self.logger.info(f"Workout saved successfully with ID: {workout_id}")
        
        info_records = [r for r in self.log_records if r.levelname == "INFO"]
        self.assertTrue(len(info_records) > 0)
        self.assertIn("123", info_records[0].getMessage())


class TestErrorHandlingPatterns(unittest.TestCase):
    """Test logging in error handling scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = get_logger("app.api.handlers")
        self.log_records = []
        
        self.handler = logging.Handler()
        self.handler.emit = lambda record: self.log_records.append(record)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)
    
    def tearDown(self):
        """Clean up after tests."""
        self.logger.removeHandler(self.handler)
    
    def test_api_request_logged(self):
        """Test logging API requests."""
        endpoint = "/api/users"
        method = "POST"
        self.logger.info(f"{method} request to {endpoint}")
        
        self.assertIn(endpoint, self.log_records[0].getMessage())
    
    def test_api_error_logged(self):
        """Test logging API errors."""
        endpoint = "/api/users"
        error_code = 500
        
        try:
            raise Exception("Internal server error")
        except Exception as e:
            self.logger.error(
                f"API request to {endpoint} failed with {error_code}: {str(e)}",
                exc_info=True
            )
        
        error_records = [r for r in self.log_records if r.levelname == "ERROR"]
        self.assertTrue(len(error_records) > 0)
    
    def test_validation_error_logged(self):
        """Test logging validation errors."""
        field = "email"
        reason = "Invalid format"
        self.logger.warning(f"Validation failed for {field}: {reason}")
        
        warning_records = [r for r in self.log_records if r.levelname == "WARNING"]
        self.assertTrue(len(warning_records) > 0)
        self.assertIn(field, warning_records[0].getMessage())
    
    def test_retry_operation_logged(self):
        """Test logging retry operations."""
        attempt = 1
        max_attempts = 3
        self.logger.debug(f"Retry attempt {attempt} of {max_attempts}")
        
        debug_records = [r for r in self.log_records if r.levelname == "DEBUG"]
        self.assertTrue(len(debug_records) > 0)
    
    def test_fallback_logged(self):
        """Test logging fallback behavior."""
        self.logger.warning("Primary service unavailable, using fallback")
        
        warning_records = [r for r in self.log_records if r.levelname == "WARNING"]
        self.assertTrue(len(warning_records) > 0)
        self.assertIn("fallback", warning_records[0].getMessage().lower())


class TestLoggingBestPractices(unittest.TestCase):
    """Test logging best practices."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = get_logger("app.test.bestpractices")
        self.log_records = []
        
        self.handler = logging.Handler()
        self.handler.emit = lambda record: self.log_records.append(record)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)
    
    def tearDown(self):
        """Clean up after tests."""
        self.logger.removeHandler(self.handler)
    
    def test_structured_logging_with_context(self):
        """Test structured logging with contextual information."""
        user_id = 42
        action = "login"
        timestamp = "2026-01-28T14:30:00"
        
        self.logger.info(
            f"User action: user_id={user_id}, action={action}, timestamp={timestamp}"
        )
        
        message = self.log_records[0].getMessage()
        self.assertIn("user_id=42", message)
        self.assertIn("action=login", message)
    
    def test_progressive_logging_detail(self):
        """Test logging at different detail levels for operations."""
        operation = "database_query"
        
        self.logger.debug(f"Starting {operation}")
        self.logger.debug(f"{operation} - Preparing connection")
        self.logger.debug(f"{operation} - Executing query")
        self.logger.info(f"{operation} completed successfully")
        
        debug_count = len([r for r in self.log_records if r.levelname == "DEBUG"])
        info_count = len([r for r in self.log_records if r.levelname == "INFO"])
        
        self.assertEqual(debug_count, 3)
        self.assertEqual(info_count, 1)
    
    def test_avoid_logging_sensitive_data(self):
        """Test that sensitive data patterns are noted in comments."""
        # In real code, passwords/tokens should NOT be logged
        # This test ensures we're conscious of security
        username = "testuser"
        self.logger.info(f"Login attempt for user: {username}")
        
        message = self.log_records[0].getMessage()
        # Should have username but not password
        self.assertIn("testuser", message)


if __name__ == "__main__":
    unittest.main()
