"""
Integration tests for app/main.py data flow.

Validates:
- Benchmarks loader integration on app creation
- UserProfile creation from request data
- AI call wiring with correct arguments
"""

import json

import pytest

import app.main as main_module
import app.scaffolding_chat as scaffolding_chat
from app.database.models import UserProfile
from app.scaffolding_chat import scaffold_chat_post


@pytest.fixture
def app(monkeypatch):
    """Create a Flask app with benchmark loader mocked."""
    benchmarks = {"strength": {"example": 1}}

    monkeypatch.setattr(main_module, "load_fitness_benchmarks", lambda: benchmarks)
    app = main_module.create_app()
    app.testing = True
    return app


def test_create_app_loads_benchmarks(app):
    """Ensure benchmarks are loaded and stored on the app."""
    assert isinstance(app.benchmarks, dict)
    assert app.benchmarks.get("strength") == {"example": 1}


def test_chat_api_data_flow(monkeypatch, app):
    """Validate UserProfile creation and AI call data flow."""
    captured = {}

    def fake_ai_call(profile, message, api_key):
        captured["profile"] = profile
        captured["message"] = message
        captured["api_key"] = api_key
        return "mocked response"

    monkeypatch.setattr(scaffolding_chat, "get_ai_recommendation", fake_ai_call)
    monkeypatch.setattr(scaffolding_chat, "GEMINI_API_KEY", "test-key")

    payload = {
        "message": "How can I improve my squat?",
        "profile": {
            "name": "Avery",
            "age": 29,
            "gender": "female",
            "height": "5'6\"",
            "weight": "140 lbs",
            "fitness_goals": ["strength", "mobility"],
        },
    }

    with app.app_context():
        with app.test_request_context(
            "/",
            method="POST",
            data=json.dumps(payload),
            content_type="application/json",
        ):
            response = scaffold_chat_post()

    assert response.status_code == 200
    assert response.get_json() == {"response": "mocked response"}

    assert isinstance(captured.get("profile"), UserProfile)
    assert captured["profile"].name == "Avery"
    assert captured["profile"].age == 29
    assert captured["profile"].gender == "female"
    assert captured["profile"].fitness_goals == ["strength", "mobility"]
    assert captured["message"] == payload["message"]
    assert captured["api_key"] == "test-key"
