"""Pytest configuration and shared fixtures for auth and app tests."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from flask import Flask

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.db_instance import db
from app.auth_module.routes import auth_bp
from app.auth_module.models import User  # noqa: F401 - needed so db.create_all() creates table


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
