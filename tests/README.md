# Logging Tests

This directory contains comprehensive unit and integration tests for the AI Fitness Planner logging utility.

## Test Files

### `test_logger.py`
Core unit tests for logger functionality:
- Logger initialization and retrieval
- Different logging levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Exception information logging
- Enable/disable functionality
- Log level configuration
- Message content validation

### `test_logger_integration.py`
Integration tests with file I/O and real-world scenarios:
- Log file creation and management
- Logging across multiple levels
- Message formatting
- Different module contexts
- Logger memoization
- Exception logging
- Context-based usage patterns

### `test_logger_examples.py`
Example-based tests validating patterns from documentation:
- Authentication route logging (registration, login)
- Database operation logging (save, find, errors)
- Service layer logging (workout operations)
- Error handling patterns (API errors, validation, retries)
- Logging best practices

## Running Tests

### Run all tests
```bash
python -m pytest tests/
```

### Run specific test file
```bash
python -m pytest tests/test_logger.py
```

### Run specific test class
```bash
python -m pytest tests/test_logger.py::TestLoggerBasics
```

### Run specific test method
```bash
python -m pytest tests/test_logger.py::TestLoggerBasics::test_get_logger_returns_logger_instance
```

### Run with verbose output
```bash
python -m pytest tests/ -v
```

### Run with coverage report
```bash
python -m pytest tests/ --cov=app.logger --cov-report=html
```

## Alternative: Using unittest

If pytest is not installed, you can use unittest:

```bash
# Run all tests
python -m unittest discover tests/

# Run specific test file
python -m unittest tests.test_logger

# Run specific test class
python -m unittest tests.test_logger.TestLoggerBasics

# Run specific test method
python -m unittest tests.test_logger.TestLoggerBasics.test_get_logger_returns_logger_instance
```

## Test Coverage

The test suite covers:

✅ Basic Logger Functionality
- Logger instance creation
- Module name handling
- Logger memoization (same name = same instance)

✅ Logging Levels
- DEBUG, INFO, WARNING, ERROR, CRITICAL levels
- Level filtering and propagation
- Exception information tracking

✅ Enable/Disable Features
- Disabling logging via environment variables
- Enable/disable functionality at runtime
- Log level configuration and changes

✅ Message Formatting
- Message content preservation
- Logger name tracking
- Level name identification
- Timestamp inclusion
- Formatted string logging
- Dictionary data logging

✅ Integration Scenarios
- Multiple modules logging
- Exception logging with tracebacks
- Conditional logging patterns
- Try-except block logging
- Error handling patterns

✅ Real-World Usage Patterns
- Authentication operations
- Database operations
- Service layer operations
- API error handling
- Structured logging with context

## Environment Variables

Tests respect the following environment variables (can be set in .env):

```env
# Enable or disable logging (default: True)
ENABLE_LOGGING=True

# Set the minimum log level (default: INFO)
LOG_LEVEL=INFO
```

## Interpreting Test Results

**Passed Tests**: All assertions in the test method completed successfully.

**Failed Tests**: One or more assertions failed. Check the error message for details.

**Skipped Tests**: Tests marked with `@skip` or `@skipIf` were not executed.

## Adding New Tests

To add new test cases:

1. Choose the appropriate test file based on what you're testing
2. Create a new test class inheriting from `unittest.TestCase`
3. Implement `setUp()` and `tearDown()` methods if needed
4. Add test methods prefixed with `test_`
5. Use assertions to validate behavior

Example:
```python
def test_new_feature(self):
    """Test description."""
    logger = get_logger("test.module")
    logger.info("Test message")
    
    self.assertEqual(expected_value, actual_value)
```

## Common Issues

### Import Errors
If you see import errors, ensure the parent directory is in the Python path:
```python
sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Permission Errors
Tests that create log files require write permissions to the logs directory.

### Async/Threading Issues
Tests use synchronous logging. For async testing, consider using `unittest.mock` to patch I/O operations.

## Continuous Integration

To run tests in CI/CD pipeline:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests with coverage
pytest tests/ --cov=app.logger --cov-report=xml

# Generate HTML coverage report
pytest tests/ --cov=app.logger --cov-report=html
```

## Troubleshooting

**Tests are modifying global state**
- Tests use mock objects and temporary directories to isolate changes
- Check `setUp()` and `tearDown()` methods for cleanup

**Log files not being created**
- Verify `ENABLE_LOGGING=True` in environment
- Check directory permissions
- Ensure `LOG_DIR` path is writable

**Tests failing inconsistently**
- May indicate race conditions in file operations
- Check for proper cleanup in `tearDown()`
- Verify test isolation
