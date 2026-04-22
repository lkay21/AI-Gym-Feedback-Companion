"""Pytest configuration and shared fixtures for auth and app tests."""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db_instance import db
from app.auth_module.routes import auth_bp

# Import User if present (SQLAlchemy auth); develop may use Supabase-only auth
try:
    from app.auth_module.models import User  # noqa: F401
except ImportError:
    User = None


def _make_supabase_auth_response(user_id="test-uuid", email="test@example.com", username="testuser"):
    """Build a fake Supabase sign_up/sign_in response with .user and .session."""
    user = SimpleNamespace(
        id=user_id,
        email=email,
        created_at="2024-01-01T00:00:00Z",
        user_metadata={"username": username},
    )
    session = SimpleNamespace(
        access_token="fake-token",
        refresh_token="fake-refresh",
    )
    return SimpleNamespace(user=user, session=session)


@pytest.fixture
def app():
    """Flask app with in-memory SQLite for testing (no external DB)."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test-secret"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    app.register_blueprint(auth_bp)
    with app.app_context():
        db.create_all()
    app.testing = True
    return app


@pytest.fixture
def app_with_supabase_mock(app):
    """
    App with get_supabase_client and ProfileService mocked so auth routes
    run without real Supabase/DynamoDB. Use for register/login success/failure tests.
    """
    supabase_mock = MagicMock()
    supabase_mock.auth.sign_up.return_value = _make_supabase_auth_response(
        email="test@example.com", username="testuser"
    )
    supabase_mock.auth.sign_in_with_password.return_value = _make_supabase_auth_response(
        email="test@example.com", username="testuser"
    )

    profile_service_mock = MagicMock()
    profile_service_mock.update_profile.return_value = None

    # For check_session and get_user
    session_user = SimpleNamespace(
        id="test-uuid",
        email="test@example.com",
        created_at="2024-01-01T00:00:00Z",
        user_metadata={"username": "testuser"},
    )
    supabase_mock.auth.get_user.return_value = SimpleNamespace(user=session_user)
    supabase_mock.auth.set_session.return_value = None
    supabase_mock.auth.sign_out.return_value = None

    with patch("app.auth_module.routes.get_supabase_client", return_value=supabase_mock), patch(
        "app.auth_module.routes.ProfileService", return_value=profile_service_mock
    ):
        yield app, supabase_mock
