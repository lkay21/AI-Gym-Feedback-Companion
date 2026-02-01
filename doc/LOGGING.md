# Logging Configuration Guide

## Overview
The AI Fitness Planner project includes a centralized logging utility that tracks system messages, warnings, and errors across all modules.

## Features
- **Timestamps**: All log messages include ISO format timestamps
- **Module Names**: Source module identification for each log message
- **Multiple Levels**: DEBUG, INFO, WARNING, ERROR, and CRITICAL log levels
- **Enable/Disable**: Easy enable/disable functionality via environment variables
- **Log Rotation**: Automatic file rotation to prevent large log files (5MB per file, keeps 5 backups)
- **Dual Output**: Console and file logging simultaneously

## Configuration

### Environment Variables
Add these to your `.env` file in the project root:

```env
# Enable or disable logging (default: True)
ENABLE_LOGGING=True

# Set the minimum log level (default: INFO)
# Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO
```

## Usage

### Basic Logging in a Module

```python
from app.logger import get_logger

# Get logger instance (use __name__ for automatic module identification)
logger = get_logger(__name__)

# Log messages at different levels
logger.debug("Detailed debugging information")
logger.info("Informational message")
logger.warning("Warning message")
logger.error("Error message")
logger.critical("Critical error message")
```

### Example Usage in Routes

```python
from flask import Blueprint
from app.logger import get_logger

auth_bp = Blueprint('auth', __name__)
logger = get_logger(__name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    logger.info("Login attempt")
    try:
        # Your authentication logic
        logger.info("User logged in successfully")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Login failed: {str(e)}", exc_info=True)
        return {"status": "error"}, 400
```

## Log Levels Explained

| Level | Use Case | Example |
|-------|----------|---------|
| **DEBUG** | Detailed information for debugging | Variable values, function calls |
| **INFO** | General informational messages | Application started, user logged in |
| **WARNING** | Warning conditions that should be noted | Missing configuration, deprecated feature use |
| **ERROR** | Error conditions that need attention | Failed API calls, database errors |
| **CRITICAL** | Critical errors that may require immediate action | Fatal system errors |

## Log Output Format

Logs follow this format:
```
YYYY-MM-DD HH:MM:SS | LEVEL    | module.name | message
```

Example:
```
2026-01-28 14:30:45 | INFO     | app.main | Creating Flask application
2026-01-28 14:30:46 | WARNING  | app.main | GEMINI_API_KEY not found in environment variables
2026-01-28 14:30:47 | ERROR    | app.auth_module.routes | Database connection failed
```

## Log Files

Log files are stored in: `logs/app.log`

The logging system maintains 5 backup files automatically when the main log file exceeds 5MB:
- `app.log` (current log file)
- `app.log.1` (newest backup)
- `app.log.2` - `app.log.5` (older backups)

## Runtime Control

You can control logging at runtime using these functions:

### Disable All Logging
```python
from app.logger import disable_logging

disable_logging()  # Suppresses all log output
```

### Enable Logging
```python
from app.logger import enable_logging

enable_logging()  # Re-enables logging
```

### Change Log Level Dynamically
```python
from app.logger import set_log_level

set_log_level('DEBUG')  # Enable verbose logging
set_log_level('WARNING')  # Only warnings and errors
```

## Logging Across Modules

The logging system works seamlessly across all modules. Each module should import the logger at the top:

```python
# In app/auth_module/routes.py
from app.logger import get_logger

logger = get_logger(__name__)
```

```python
# In app/chatbot/module.py
from app.logger import get_logger

logger = get_logger(__name__)
```

The `get_logger(__name__)` pattern automatically captures the module name in log messages.

## Best Practices

1. **Use module-level loggers**: Call `get_logger(__name__)` once per module
2. **Choose appropriate levels**: Use DEBUG for detailed info, INFO for key events
3. **Include context**: Add relevant information in log messages
4. **Use exc_info for exceptions**: 
   ```python
   logger.error(f"Operation failed: {str(e)}", exc_info=True)  # Includes stack trace
   ```
5. **Avoid logging sensitive data**: Don't log passwords, API keys, or personal information

## Disabling Logs in Development

If logs are too verbose during development, adjust in `.env`:

```env
# Only show warnings and errors
ENABLE_LOGGING=True
LOG_LEVEL=WARNING

# Or disable completely
ENABLE_LOGGING=False
```

## Troubleshooting

**No log files are created:**
- Check that the `logs/` directory is writable
- Ensure `ENABLE_LOGGING=True` in your `.env`
- Verify `LOG_LEVEL` is set to a valid value (DEBUG, INFO, WARNING, ERROR, CRITICAL)

**Too many log files:**
- Logs are automatically rotated when `app.log` exceeds 5MB
- Only 5 backup files are kept (configurable in `app/logger.py`)

**Performance impact:**
- Disable logging in production if needed by setting `ENABLE_LOGGING=False`
- Or set `LOG_LEVEL=WARNING` to reduce volume
