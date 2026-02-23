"""
Global configuration module for AI Fitness Planner.

This module stores all project-level constants and configuration values including:
- Paths to exercise data and models
- OpenPose parameters
- AI model settings
- Database configuration

Use load_config() to retrieve all current settings as a dictionary.
Use update_config(key, value) to modify settings at runtime.
"""

import os
from pathlib import Path
from typing import Any, Dict

# ============================================================================
# PROJECT PATHS
# ============================================================================

# Base directory for the application
BASE_DIR = Path(__file__).parent.parent

# Data directories
DATA_DIR = BASE_DIR / "data"
EXERCISE_DATA_DIR = DATA_DIR / "exercises"
MODELS_DIR = DATA_DIR / "models"

# Exercise data files
EXERCISE_JSON_PATH = EXERCISE_DATA_DIR / "exercises.json"
EXERCISE_CSV_PATH = EXERCISE_DATA_DIR / "exercises.csv"
WORKOUT_HISTORY_DIR = DATA_DIR / "workout_history"

# ============================================================================
# OPENPOSE CONFIGURATION
# ============================================================================

# OpenPose model paths
OPENPOSE_MODEL_DIR = MODELS_DIR / "openpose"
OPENPOSE_PROTO_FILE = OPENPOSE_MODEL_DIR / "pose_deploy_librealsense.prototxt"
OPENPOSE_WEIGHTS_FILE = OPENPOSE_MODEL_DIR / "pose_iter_440000.caffemodel"

# OpenPose detection parameters
OPENPOSE_CONFIDENCE_THRESHOLD = 0.1  # Minimum confidence for pose detection
OPENPOSE_NMS_THRESHOLD = 0.2  # Non-maximum suppression threshold
OPENPOSE_SCALE_NUMBER = 1  # Number of scales to process
OPENPOSE_SCALE_GAP = 0.3  # Scale increase between multi-scale processing

# OpenPose processing parameters
OPENPOSE_TARGET_HEIGHT = 368  # Target height for pose estimation
OPENPOSE_TARGET_WIDTH = 656  # Target width for pose estimation

# ============================================================================
# AI MODEL CONFIGURATION
# ============================================================================

# Default AI model settings
AI_MODEL_NAME = "gpt-3.5-turbo"  # Default LLM model
AI_MAX_TOKENS = 500  # Maximum tokens for AI responses
AI_TEMPERATURE = 0.7  # Temperature for response generation (0.0 to 1.0)
AI_TOP_P = 0.9  # Top-p sampling parameter
AI_BATCH_SIZE = 32  # Batch size for processing

# Model endpoints
AI_API_BASE = os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
AI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# Database settings
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///instance/app.db"
)
DATABASE_ECHO = os.getenv("DATABASE_ECHO", "False").lower() == "true"

# ============================================================================
# CHATBOT CONFIGURATION
# ============================================================================

# Chatbot settings
CHATBOT_SYSTEM_PROMPT = (
    "You are an expert fitness coach and personal trainer assistant. "
    "Provide personalized workout recommendations based on user fitness levels and goals. "
    "Always prioritize safety and form correctness."
)
CHATBOT_MAX_CONVERSATION_LENGTH = 20  # Maximum number of turns to keep in memory

# ============================================================================
# WORKOUT TRACKING CONFIGURATION
# ============================================================================

# Pose detection settings for workout tracking
MIN_POSE_CONFIDENCE = 0.5  # Minimum confidence to consider a pose valid
MIN_KEYPOINT_CONFIDENCE = 0.3  # Minimum confidence for individual keypoints
POSE_SMOOTHING_WINDOW = 5  # Number of frames for pose smoothing

# Rep counting and exercise detection
REP_DETECTION_THRESHOLD = 0.4  # Threshold for detecting rep completion
EXERCISE_DETECTION_MINIMUM_FRAMES = 30  # Minimum frames to identify an exercise

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================

# Debug and logging
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / "logs" / "app.log"

# Session and user settings
SESSION_TIMEOUT_MINUTES = 30
MAX_FILE_UPLOAD_MB = 50

# ============================================================================
# CONFIGURATION MANAGEMENT
# ============================================================================

# Global configuration dictionary (stores runtime-modifiable values)
_config: Dict[str, Any] = {
    # Paths
    "BASE_DIR": str(BASE_DIR),
    "DATA_DIR": str(DATA_DIR),
    "EXERCISE_DATA_DIR": str(EXERCISE_DATA_DIR),
    "EXERCISE_JSON_PATH": str(EXERCISE_JSON_PATH),
    "EXERCISE_CSV_PATH": str(EXERCISE_CSV_PATH),
    "MODELS_DIR": str(MODELS_DIR),
    
    # OpenPose
    "OPENPOSE_MODEL_DIR": str(OPENPOSE_MODEL_DIR),
    "OPENPOSE_CONFIDENCE_THRESHOLD": OPENPOSE_CONFIDENCE_THRESHOLD,
    "OPENPOSE_NMS_THRESHOLD": OPENPOSE_NMS_THRESHOLD,
    "OPENPOSE_SCALE_NUMBER": OPENPOSE_SCALE_NUMBER,
    "OPENPOSE_SCALE_GAP": OPENPOSE_SCALE_GAP,
    "OPENPOSE_TARGET_HEIGHT": OPENPOSE_TARGET_HEIGHT,
    "OPENPOSE_TARGET_WIDTH": OPENPOSE_TARGET_WIDTH,
    
    # AI Model
    "AI_MODEL_NAME": AI_MODEL_NAME,
    "AI_MAX_TOKENS": AI_MAX_TOKENS,
    "AI_TEMPERATURE": AI_TEMPERATURE,
    "AI_TOP_P": AI_TOP_P,
    "AI_BATCH_SIZE": AI_BATCH_SIZE,
    "AI_API_BASE": AI_API_BASE,
    
    # Database
    "DATABASE_URL": DATABASE_URL,
    "DATABASE_ECHO": DATABASE_ECHO,
    
    # Chatbot
    "CHATBOT_SYSTEM_PROMPT": CHATBOT_SYSTEM_PROMPT,
    "CHATBOT_MAX_CONVERSATION_LENGTH": CHATBOT_MAX_CONVERSATION_LENGTH,
    
    # Workout tracking
    "MIN_POSE_CONFIDENCE": MIN_POSE_CONFIDENCE,
    "MIN_KEYPOINT_CONFIDENCE": MIN_KEYPOINT_CONFIDENCE,
    "POSE_SMOOTHING_WINDOW": POSE_SMOOTHING_WINDOW,
    "REP_DETECTION_THRESHOLD": REP_DETECTION_THRESHOLD,
    "EXERCISE_DETECTION_MINIMUM_FRAMES": EXERCISE_DETECTION_MINIMUM_FRAMES,
    
    # Application
    "DEBUG": DEBUG,
    "LOG_LEVEL": LOG_LEVEL,
    "SESSION_TIMEOUT_MINUTES": SESSION_TIMEOUT_MINUTES,
    "MAX_FILE_UPLOAD_MB": MAX_FILE_UPLOAD_MB,
}


def load_config() -> Dict[str, Any]:
    """
    Load and return all current configuration values as a dictionary.
    
    Returns:
        Dict[str, Any]: Dictionary containing all configuration key-value pairs.
        
    Example:
        >>> config = load_config()
        >>> print(config["AI_MODEL_NAME"])
        'gpt-3.5-turbo'
    """
    return _config.copy()


def update_config(key: str, value: Any) -> bool:
    """
    Update a configuration value at runtime.
    
    Args:
        key (str): The configuration key to update.
        value (Any): The new value for the configuration key.
        
    Returns:
        bool: True if update was successful, False if key doesn't exist.
        
    Example:
        >>> update_config("AI_TEMPERATURE", 0.8)
        True
        >>> update_config("INVALID_KEY", 123)
        False
        
    Raises:
        TypeError: If attempting to set an unsupported key.
    """
    if key not in _config:
        raise KeyError(f"Configuration key '{key}' does not exist.")
    
    _config[key] = value
    return True


def get_config(key: str, default: Any = None) -> Any:
    """
    Get a specific configuration value.
    
    Args:
        key (str): The configuration key to retrieve.
        default (Any): Default value if key is not found.
        
    Returns:
        Any: The configuration value, or default if not found.
        
    Example:
        >>> temperature = get_config("AI_TEMPERATURE")
        >>> invalid = get_config("INVALID_KEY", default=0.5)
    """
    return _config.get(key, default)


def reset_config() -> None:
    """
    Reset all configuration values to their defaults.
    
    This function reinitializes the global configuration dictionary to original values.
    Useful for testing or resetting the application state.
    """
    global _config
    _config = {
        # Paths
        "BASE_DIR": str(BASE_DIR),
        "DATA_DIR": str(DATA_DIR),
        "EXERCISE_DATA_DIR": str(EXERCISE_DATA_DIR),
        "EXERCISE_JSON_PATH": str(EXERCISE_JSON_PATH),
        "EXERCISE_CSV_PATH": str(EXERCISE_CSV_PATH),
        "MODELS_DIR": str(MODELS_DIR),
        
        # OpenPose
        "OPENPOSE_MODEL_DIR": str(OPENPOSE_MODEL_DIR),
        "OPENPOSE_CONFIDENCE_THRESHOLD": OPENPOSE_CONFIDENCE_THRESHOLD,
        "OPENPOSE_NMS_THRESHOLD": OPENPOSE_NMS_THRESHOLD,
        "OPENPOSE_SCALE_NUMBER": OPENPOSE_SCALE_NUMBER,
        "OPENPOSE_SCALE_GAP": OPENPOSE_SCALE_GAP,
        "OPENPOSE_TARGET_HEIGHT": OPENPOSE_TARGET_HEIGHT,
        "OPENPOSE_TARGET_WIDTH": OPENPOSE_TARGET_WIDTH,
        
        # AI Model
        "AI_MODEL_NAME": AI_MODEL_NAME,
        "AI_MAX_TOKENS": AI_MAX_TOKENS,
        "AI_TEMPERATURE": AI_TEMPERATURE,
        "AI_TOP_P": AI_TOP_P,
        "AI_BATCH_SIZE": AI_BATCH_SIZE,
        "AI_API_BASE": AI_API_BASE,
        
        # Database
        "DATABASE_URL": DATABASE_URL,
        "DATABASE_ECHO": DATABASE_ECHO,
        
        # Chatbot
        "CHATBOT_SYSTEM_PROMPT": CHATBOT_SYSTEM_PROMPT,
        "CHATBOT_MAX_CONVERSATION_LENGTH": CHATBOT_MAX_CONVERSATION_LENGTH,
        
        # Workout tracking
        "MIN_POSE_CONFIDENCE": MIN_POSE_CONFIDENCE,
        "MIN_KEYPOINT_CONFIDENCE": MIN_KEYPOINT_CONFIDENCE,
        "POSE_SMOOTHING_WINDOW": POSE_SMOOTHING_WINDOW,
        "REP_DETECTION_THRESHOLD": REP_DETECTION_THRESHOLD,
        "EXERCISE_DETECTION_MINIMUM_FRAMES": EXERCISE_DETECTION_MINIMUM_FRAMES,
        
        # Application
        "DEBUG": DEBUG,
        "LOG_LEVEL": LOG_LEVEL,
        "SESSION_TIMEOUT_MINUTES": SESSION_TIMEOUT_MINUTES,
        "MAX_FILE_UPLOAD_MB": MAX_FILE_UPLOAD_MB,
    }


# ============================================================================
# USAGE EXAMPLES
# ============================================================================
"""
Usage examples:

    # Import configuration
    from app.config import load_config, update_config, get_config
    
    # Load all configuration
    config = load_config()
    print(f"AI Model: {config['AI_MODEL_NAME']}")
    
    # Get a specific config value
    confidence = get_config("MIN_POSE_CONFIDENCE")
    
    # Update a configuration value
    update_config("AI_TEMPERATURE", 0.9)
    
    # Update multiple values
    updates = {
        "AI_MAX_TOKENS": 1000,
        "AI_TEMPERATURE": 0.8,
    }
    for key, value in updates.items():
        update_config(key, value)
"""