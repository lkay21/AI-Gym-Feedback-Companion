"""
Example: How to add logging to different modules in the AI Fitness Planner

This file demonstrates best practices for integrating the logging utility
across different parts of the application.
"""

# ============================================================================
# EXAMPLE 1: Logging in Authentication Routes
# ============================================================================
# Location: app/auth_module/routes.py

from flask import Blueprint, request, jsonify
from app.logger import get_logger

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
logger = get_logger(__name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user with logging."""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        
        logger.info(f"Registration attempt for user: {username}")
        
        # Validate input
        if not username or not email:
            logger.warning(f"Registration failed - missing fields for user: {username}")
            return jsonify({'error': 'Username and email required'}), 400
        
        # Your registration logic here
        logger.info(f"User registered successfully: {username}")
        return jsonify({'message': 'Registration successful'}), 201
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}", exc_info=True)
        return jsonify({'error': 'Registration failed'}), 500


# ============================================================================
# EXAMPLE 2: Logging in Database Operations
# ============================================================================
# Location: app/database/models.py (hypothetical)

from app.logger import get_logger
from app.db_instance import db

logger = get_logger(__name__)

class User(db.Model):
    """User model with logging."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    def save(self):
        """Save user to database with logging."""
        try:
            logger.debug(f"Saving user: {self.username}")
            db.session.add(self)
            db.session.commit()
            logger.info(f"User saved successfully: {self.username}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to save user {self.username}: {str(e)}", exc_info=True)
            raise
    
    @classmethod
    def find_by_username(cls, username):
        """Find user by username with logging."""
        logger.debug(f"Searching for user: {username}")
        user = cls.query.filter_by(username=username).first()
        
        if user:
            logger.debug(f"User found: {username}")
        else:
            logger.warning(f"User not found: {username}")
        
        return user


# ============================================================================
# EXAMPLE 3: Logging in Service Layer
# ============================================================================
# Location: app/fitness/workout_service.py (hypothetical)

from app.logger import get_logger

logger = get_logger(__name__)

class WorkoutService:
    """Service for handling workout operations."""
    
    @staticmethod
    def create_workout(user_id, workout_data):
        """Create a new workout with detailed logging."""
        try:
            logger.info(f"Creating workout for user: {user_id}")
            logger.debug(f"Workout data: {workout_data}")
            
            # Validate workout data
            if not workout_data.get('name'):
                logger.warning(f"Workout creation failed - missing name for user: {user_id}")
                raise ValueError("Workout name is required")
            
            # Create workout logic
            logger.info(f"Workout created successfully for user: {user_id}")
            return {"status": "success", "user_id": user_id}
            
        except ValueError as e:
            logger.warning(f"Invalid workout data for user {user_id}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to create workout for user {user_id}: {str(e)}", exc_info=True)
            raise
    
    @staticmethod
    def get_user_workouts(user_id):
        """Get all workouts for a user with logging."""
        logger.debug(f"Fetching workouts for user: {user_id}")
        
        try:
            workouts = []  # Your fetch logic here
            logger.info(f"Retrieved {len(workouts)} workouts for user: {user_id}")
            return workouts
        except Exception as e:
            logger.error(f"Failed to fetch workouts for user {user_id}: {str(e)}", exc_info=True)
            raise


# ============================================================================
# EXAMPLE 4: Logging in Middleware/Utilities
# ============================================================================
# Location: app/utils/decorators.py (hypothetical)

from functools import wraps
from app.logger import get_logger

logger = get_logger(__name__)

def log_request(f):
    """Decorator to log all requests."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.debug(f"Request to {f.__name__} with args: {args}, kwargs: {kwargs}")
        try:
            result = f(*args, **kwargs)
            logger.debug(f"Request to {f.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Request to {f.__name__} failed: {str(e)}", exc_info=True)
            raise
    return decorated_function

@log_request
def process_data(user_data):
    """Process user data with logging."""
    logger.info(f"Processing data for user")
    # Your processing logic here
    return {"processed": True}


# ============================================================================
# EXAMPLE 5: Logging in Initialization
# ============================================================================
# Location: app/auth_module/__init__.py

from app.logger import get_logger

logger = get_logger(__name__)

def init_auth_module():
    """Initialize auth module with logging."""
    logger.info("Initializing auth module")
    
    try:
        # Your initialization logic here
        logger.info("Auth module initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize auth module: {str(e)}", exc_info=True)
        raise


# ============================================================================
# EXAMPLE 6: Conditional Logging Based on Environment
# ============================================================================
# Location: Any module

import os
from app.logger import get_logger

logger = get_logger(__name__)

def debug_sensitive_operation(data):
    """Only log detailed debug info in development."""
    if os.getenv('FLASK_ENV') == 'development':
        logger.debug(f"Sensitive operation data: {data}")
    else:
        logger.info("Sensitive operation executed")

def handle_api_response(response):
    """Log API responses with appropriate detail."""
    status_code = response.get('status_code')
    
    if status_code >= 500:
        logger.error(f"API error - Status: {status_code}, Response: {response}")
    elif status_code >= 400:
        logger.warning(f"API client error - Status: {status_code}")
    else:
        logger.debug(f"API response - Status: {status_code}")


# ============================================================================
# QUICK REFERENCE
# ============================================================================
# 
# 1. Import at the top of your module:
#    from app.logger import get_logger
#
# 2. Create logger instance (typically at module level):
#    logger = get_logger(__name__)
#
# 3. Use throughout your module:
#    logger.debug("Detailed info")
#    logger.info("Important event")
#    logger.warning("Warning condition")
#    logger.error("Error occurred", exc_info=True)  # Use exc_info=True for exceptions
#    logger.critical("Critical issue")
#
# 4. For async/background operations, pass logger to functions if needed:
#    def worker_function(item, logger=logger):
#        logger.info(f"Processing {item}")
#
# Configuration is handled via .env:
# - ENABLE_LOGGING=True/False (enable/disable all logging)
# - LOG_LEVEL=DEBUG/INFO/WARNING/ERROR/CRITICAL (set minimum log level)
#
# Logs are stored in: logs/app.log
# Console output shows INFO level and above
# File output shows DEBUG level and above
