from functools import wraps
from flask import session
from app.db_instance import db
from app.core.errors import UnauthorizedError
from .models import User

def login_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user_id')
        if not user_id:
            raise UnauthorizedError("Authentication required")
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get the current logged-in user"""
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

def is_authenticated():
    """Check if user is authenticated"""
    return session.get('user_id') is not None

