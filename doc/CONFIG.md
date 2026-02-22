# Configuration Module Documentation

## Overview

The `config.py` module is the centralized configuration hub for the AI Fitness Planner application. It defines all project-level constants and configuration values including paths to data files, model parameters, AI settings, database configuration, and runtime adjustable values.

**Location:** `app/config.py`

## Purpose

The configuration module serves several key purposes:

1. **Centralized Settings**: Single source of truth for all configuration values
2. **Environment Variables**: Reads sensitive data from environment variables (API keys, database URLs)
3. **Runtime Modifications**: Supports updating configuration values without restarting the application
4. **Directory Management**: Manages all path references using `pathlib.Path` for cross-platform compatibility
5. **Documentation**: Clear organization of settings by functional category

## Configuration Categories

### 1. Project Paths

These variables define the directory structure for the application:

```python
BASE_DIR              # Base directory for the application
DATA_DIR              # Root directory for all data
EXERCISE_DATA_DIR     # Exercise definitions and metadata
MODELS_DIR            # Pre-trained model files
EXERCISE_JSON_PATH    # Exercise data in JSON format
EXERCISE_CSV_PATH     # Exercise data in CSV format
WORKOUT_HISTORY_DIR   # User workout history files
```

**Usage:**
```python
from app.config import BASE_DIR, EXERCISE_DATA_DIR

# Access data files
exercise_data = EXERCISE_DATA_DIR / "exercises.json"
```

### 2. OpenPose Configuration

Settings for the OpenPose pose estimation model:

#### Model Paths
```python
OPENPOSE_MODEL_DIR       # Directory containing OpenPose model files
OPENPOSE_PROTO_FILE      # Neural network architecture definition
OPENPOSE_WEIGHTS_FILE    # Pre-trained model weights
```

#### Detection Parameters
```python
OPENPOSE_CONFIDENCE_THRESHOLD   # 0.1 - Minimum confidence for pose detection
OPENPOSE_NMS_THRESHOLD          # 0.2 - Non-maximum suppression threshold
OPENPOSE_SCALE_NUMBER           # 1   - Number of scales to process
OPENPOSE_SCALE_GAP              # 0.3 - Scale increase between multi-scale processing
```

#### Processing Parameters
```python
OPENPOSE_TARGET_HEIGHT   # 368 - Target height for pose estimation
OPENPOSE_TARGET_WIDTH    # 656 - Target width for pose estimation
```

**Adjustment Guidelines:**
- **Lower `OPENPOSE_CONFIDENCE_THRESHOLD`**: Detects more poses but increases false positives
- **Higher `OPENPOSE_CONFIDENCE_THRESHOLD`**: More accurate but may miss valid poses
- Adjust `TARGET_HEIGHT` and `TARGET_WIDTH` for different input resolutions (maintain 368:656 aspect ratio)

### 3. AI Model Configuration

Settings for LLM and AI recommendation generation:

```python
AI_MODEL_NAME      # "gpt-3.5-turbo" - Default language model
AI_MAX_TOKENS      # 500 - Maximum tokens per response
AI_TEMPERATURE     # 0.7 - Response creativity (0.0=deterministic, 1.0=creative)
AI_TOP_P           # 0.9 - Top-p sampling parameter
AI_BATCH_SIZE      # 32 - Batch size for processing
AI_API_BASE        # API endpoint (from env var OPENAI_API_BASE)
AI_API_KEY         # API authentication key (from env var OPENAI_API_KEY)
```

**Temperature Guidelines:**
- `0.0 - 0.3`: Deterministic, good for factual information
- `0.4 - 0.7`: Balanced, suitable for fitness recommendations
- `0.8 - 1.0`: Creative, for diverse response generation

**Required Environment Variables:**
```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_API_BASE=https://api.openai.com/v1  # Optional, has default
```

### 4. Database Configuration

Settings for the database connection:

```python
DATABASE_URL    # Connection string (default: sqlite:///instance/app.db)
DATABASE_ECHO   # Boolean - Log all SQL queries when True
```

**Environment Variables:**
```bash
DATABASE_URL=sqlite:///instance/app.db    # SQLite (default)
DATABASE_URL=postgresql://user:pass@host  # PostgreSQL
DATABASE_ECHO=true                         # Enable SQL logging
```

### 5. Chatbot Configuration

Settings for the fitness chatbot:

```python
CHATBOT_SYSTEM_PROMPT                # System prompt for the AI assistant
CHATBOT_MAX_CONVERSATION_LENGTH      # 20 - Maximum conversation turns to retain
```

The system prompt defines the chatbot's role and behavior:
> "You are an expert fitness coach and personal trainer assistant. Provide personalized workout recommendations based on user fitness levels and goals. Always prioritize safety and form correctness."

### 6. Workout Tracking Configuration

Parameters for pose detection and exercise tracking:

```python
MIN_POSE_CONFIDENCE              # 0.5 - Minimum confidence for valid poses
MIN_KEYPOINT_CONFIDENCE          # 0.3 - Minimum confidence for individual keypoints
POSE_SMOOTHING_WINDOW            # 5 - Number of frames for smoothing
REP_DETECTION_THRESHOLD          # 0.4 - Threshold for rep detection
EXERCISE_DETECTION_MINIMUM_FRAMES # 30 - Minimum frames to identify exercise
```

**Tuning Tips:**
- Increase `MIN_POSE_CONFIDENCE` to reduce false positives in crowded environments
- Increase `POSE_SMOOTHING_WINDOW` for smoother tracking but higher latency
- Adjust `REP_DETECTION_THRESHOLD` based on exercise speed (fast vs slow movements)

### 7. Application Settings

General application configuration:

```python
DEBUG                   # Enable debug mode (from env var DEBUG)
LOG_LEVEL              # Logging level: DEBUG, INFO, WARNING, ERROR (from env var LOG_LEVEL)
LOG_FILE               # Path to application log file
SESSION_TIMEOUT_MINUTES # 30 - Session timeout duration
MAX_FILE_UPLOAD_MB     # 50 - Maximum upload file size
```

**Environment Variables:**
```bash
DEBUG=true          # Enable debug mode
LOG_LEVEL=INFO      # Set logging level
```

## Configuration Management Functions

### `load_config() -> Dict[str, Any]`

Returns a copy of all current configuration values as a dictionary.

**Example:**
```python
from app.config import load_config

config = load_config()
print(f"AI Model: {config['AI_MODEL_NAME']}")
print(f"Database: {config['DATABASE_URL']}")
```

### `get_config(key: str, default: Any = None) -> Any`

Retrieves a specific configuration value with an optional default fallback.

**Example:**
```python
from app.config import get_config

# Get a value with default
temperature = get_config("AI_TEMPERATURE")
unknown = get_config("UNKNOWN_KEY", default=0.5)
```

### `update_config(key: str, value: Any) -> bool`

Updates a configuration value at runtime without restarting the application.

**Parameters:**
- `key`: The configuration key to update
- `value`: The new value

**Returns:** `True` if successful

**Raises:** `KeyError` if the key doesn't exist

**Example:**
```python
from app.config import update_config

# Update a single value
update_config("AI_TEMPERATURE", 0.9)

# Update multiple values
updates = {
    "AI_MAX_TOKENS": 1000,
    "AI_TEMPERATURE": 0.8,
}
for key, value in updates.items():
    update_config(key, value)
```

### `reset_config() -> None`

Resets all configuration values to their defaults. Useful for testing or resetting application state.

**Example:**
```python
from app.config import reset_config

# Reset to defaults
reset_config()
```

## Environment Variable Configuration

The following values are read from environment variables:

| Variable | Default | Usage |
|----------|---------|-------|
| `OPENAI_API_KEY` | `""` | API key for OpenAI |
| `OPENAI_API_BASE` | `https://api.openai.com/v1` | OpenAI API endpoint |
| `DATABASE_URL` | `sqlite:///instance/app.db` | Database connection string |
| `DATABASE_ECHO` | `false` | Enable SQL query logging |
| `DEBUG` | `false` | Enable debug mode |
| `LOG_LEVEL` | `INFO` | Logging level |

**Setting Environment Variables:**

On Linux/macOS:
```bash
export OPENAI_API_KEY=your_key_here
export DEBUG=true
export LOG_LEVEL=DEBUG
```

In `.env` file (if using python-dotenv):
```
OPENAI_API_KEY=your_key_here
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_URL=sqlite:///instance/app.db
```

## Usage Examples

### Basic Configuration Access

```python
from app.config import load_config, get_config

# Load entire configuration
config = load_config()

# Access specific values
model = config["AI_MODEL_NAME"]
db_url = config["DATABASE_URL"]

# Or use get_config for cleaner syntax
confidence = get_config("MIN_POSE_CONFIDENCE")
max_tokens = get_config("AI_MAX_TOKENS")
```

### Runtime Configuration Updates

```python
from app.config import update_config

# Update single values
update_config("AI_TEMPERATURE", 0.9)
update_config("MIN_POSE_CONFIDENCE", 0.6)

# Update for specific session
original_temp = get_config("AI_TEMPERATURE")
update_config("AI_TEMPERATURE", 0.5)
# ... do work with lower temperature ...
update_config("AI_TEMPERATURE", original_temp)  # Restore
```

### Configuration in Flask App

```python
from flask import Flask
from app.config import load_config, update_config

app = Flask(__name__)
config = load_config()

# Use configuration in app setup
app.config['DEBUG'] = config['DEBUG']
app.config['SQLALCHEMY_DATABASE_URI'] = config['DATABASE_URL']

# Modify at runtime based on conditions
if app.config['DEBUG']:
    update_config("LOG_LEVEL", "DEBUG")
    update_config("AI_TEMPERATURE", 0.5)
```

### Testing with Configuration Reset

```python
import pytest
from app.config import reset_config, update_config, get_config

@pytest.fixture(autouse=True)
def reset_config_fixture():
    """Reset configuration before and after each test"""
    reset_config()
    yield
    reset_config()

def test_temperature_update():
    original = get_config("AI_TEMPERATURE")
    update_config("AI_TEMPERATURE", 0.9)
    assert get_config("AI_TEMPERATURE") == 0.9
```

## Best Practices

1. **Use `get_config()` over direct imports** for flexibility in testing and configuration changes
   ```python
   # Good
   temp = get_config("AI_TEMPERATURE")
   
   # Avoid
   from app.config import AI_TEMPERATURE
   ```

2. **Handle missing keys with defaults**
   ```python
   custom_value = get_config("CUSTOM_KEY", default=None)
   ```

3. **Update configuration at application startup** rather than mid-operation
   ```python
   def initialize_app():
       update_config("LOG_LEVEL", os.getenv("LOG_LEVEL", "INFO"))
   ```

4. **Document custom configuration keys** added at runtime
   ```python
   # Add custom config with explanation
   update_config("CUSTOM_AI_SYSTEM_PROMPT", "Your custom prompt here")
   ```

5. **Reset configuration between test runs**
   ```python
   @pytest.fixture
   def clean_config():
       reset_config()
       yield
       reset_config()
   ```

## Adding New Configuration Values

To add a new configuration value:

1. **Define the constant** at module level:
   ```python
   NEW_SETTING = os.getenv("NEW_SETTING", "default_value")
   ```

2. **Add to `_config` dictionary** in the configuration management section:
   ```python
   _config: Dict[str, Any] = {
       # ... existing values ...
       "NEW_SETTING": NEW_SETTING,
   }
   ```

3. **Update `reset_config()`** to include the new value:
   ```python
   def reset_config() -> None:
       global _config
       _config = {
           # ... existing values ...
           "NEW_SETTING": NEW_SETTING,
       }
   ```

4. **Document** in this file under the appropriate section

## Troubleshooting

### Issue: Configuration Key Not Found
```
KeyError: Configuration key 'UNKNOWN_KEY' does not exist.
```
**Solution:** Ensure the key is defined in `_config` dictionary and spelled correctly.

### Issue: Environment Variable Not Read
```python
api_key = get_config("AI_API_KEY")  # Returns empty string
```
**Solution:** Set the environment variable before running the application:
```bash
export OPENAI_API_KEY=your_key_here
```

### Issue: Changes Not Persisting
**Solution:** Configuration updates are in-memory only. Changes are lost when the application restarts. For persistent changes, update environment variables or `.env` files.

## See Also

- [Logging Documentation](LOGGING.md) - Related to `LOG_LEVEL` and `LOG_FILE` settings
- [Backend Scaffolding Tests](BACKEND_SCAFFOLDING_TESTS.md) - Examples of testing configuration
- Flask Documentation: [Configuration Handling](https://flask.palletsprojects.com/config/)
