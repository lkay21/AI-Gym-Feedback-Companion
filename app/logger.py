"""
Logging utility for the AI Fitness Planner application.

This module provides a centralized logging configuration that supports:
- Timestamps for all log messages
- Module names to identify log sources
- Multiple log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Enable/disable logging via configuration
- File and console output

Usage:
    from app.logger import get_logger
    
    logger = get_logger(__name__)
    logger.info("Application started")
    logger.warning("Missing API key")
    logger.error("Database connection failed")
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


# Configuration
LOG_ENABLED = os.getenv("ENABLE_LOGGING", "True").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_DIR = Path(__file__).parent.parent / "logs"
LOG_FILE = LOG_DIR / "app.log"
MAX_LOG_SIZE = 5 * 1024 * 1024  # 5MB
BACKUP_COUNT = 5  # Keep 5 backup log files


class NullHandler(logging.Handler):
    """Handler that does nothing - used when logging is disabled."""
    def emit(self, record):
        pass


def setup_logging():
    """
    Configure logging for the application.
    
    Creates:
    - Console handler for info and above
    - File handler with rotation for detailed logging
    - Timestamps in ISO format
    - Module names in all messages
    """
    if not LOG_ENABLED:
        return
    
    # Create logs directory if it doesn't exist
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, LOG_LEVEL))
    
    # Clear any existing handlers to avoid duplicates
    root_logger.handlers = []
    
    # Log format: timestamp | level | module | message
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    formatter = logging.Formatter(
        log_format,
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Console handler (INFO level and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler with rotation (DEBUG level and above)
    try:
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    except Exception as e:
        # If file handler fails, log to console only
        console_handler.setLevel(logging.DEBUG)
        root_logger.warning(
            f"Could not set up file logging: {e}. Using console only."
        )


def get_logger(name):
    """
    Get a logger instance for a module.
    
    Args:
        name: The module name (usually __name__)
    
    Returns:
        logging.Logger: Configured logger instance
    
    Example:
        logger = get_logger(__name__)
        logger.info("Processing user request")
    """
    logger = logging.getLogger(name)
    
    if not LOG_ENABLED:
        # If logging is disabled, use a null handler
        logger.addHandler(NullHandler())
        logger.setLevel(logging.CRITICAL + 1)  # Suppress all logs
    
    return logger


def disable_logging():
    """Disable all logging output."""
    global LOG_ENABLED
    LOG_ENABLED = False
    root_logger = logging.getLogger()
    root_logger.handlers = []
    root_logger.addHandler(NullHandler())


def enable_logging():
    """Enable logging with current configuration."""
    global LOG_ENABLED
    LOG_ENABLED = True
    setup_logging()


def set_log_level(level):
    """
    Set the logging level at runtime.
    
    Args:
        level: String level name ('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')
    
    Example:
        set_log_level('DEBUG')  # Enable verbose logging
    """
    level_value = getattr(logging, level.upper(), logging.INFO)
    root_logger = logging.getLogger()
    root_logger.setLevel(level_value)
    
    for handler in root_logger.handlers:
        if not isinstance(handler, NullHandler):
            handler.setLevel(level_value)
