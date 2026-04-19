from functools import wraps
from typing import Optional

from flask import jsonify, request, session

from app.db_instance import db
from .supabase_client import get_supabase_client
from .models import User


def _resolve_user_id_from_bearer_token() -> Optional[str]:
    authorization = request.headers.get("Authorization", "")
    if not authorization.lower().startswith("bearer "):
        return None

    token = authorization.split(" ", 1)[1].strip() if " " in authorization else ""
    if not token:
        return None

    try:
        supabase = get_supabase_client()
        response = supabase.auth.get_user(token)
        user = getattr(response, "user", None)
        user_id = getattr(user, "id", None)
        return str(user_id) if user_id else None
    except Exception:
        return None


def resolve_authenticated_user_id() -> Optional[str]:
    """
    User id from Flask session (browser / cookie clients) or X-User-Id header.

    React Native fetch often does not persist or send session cookies to the API host;
    the app stores Supabase user id in AsyncStorage and should send it on each request.
    """
    uid = session.get("user_id")
    if uid:
        return str(uid)
    header = request.headers.get("X-User-Id") or request.headers.get("X-User-ID")
    if header:
        h = header.strip()
        if h:
            return h
    bearer_user_id = _resolve_user_id_from_bearer_token()
    if bearer_user_id:
        return bearer_user_id
    return None


def login_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = resolve_authenticated_user_id()
        if not user_id:
            return jsonify({'error': 'Authentication required'}), 401
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
    return resolve_authenticated_user_id() is not None

