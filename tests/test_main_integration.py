"""
Integration tests for app/main.py data flow.

Validates:
- App creation and core route registration
- UserProfile creation from request data
- AI call wiring with correct arguments
"""

import pytest

import app.main as main_module
from app.database.models import UserProfile


@pytest.fixture
def app():
    """Create a Flask app for integration testing."""
    app = main_module.create_app()
    app.testing = True
    return app


def test_create_app_registers_core_routes(app):
    """Ensure app initializes and core routes are available."""
    routes = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/" in routes
    assert "/chat" in routes
    assert "/api/scaffolding/chat" in routes


def test_chat_api_data_flow(monkeypatch, app):
    """Validate UserProfile creation and AI call data flow."""
    captured = {}

    def fake_ai_call(profile, message, api_key):
        captured["profile"] = profile
        captured["message"] = message
        captured["api_key"] = api_key
        return "mocked response"

    monkeypatch.setattr(main_module, "get_ai_recommendation", fake_ai_call)
    monkeypatch.setattr(main_module, "GEMINI_API_KEY", "test-key")

    client = app.test_client()
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

    response = client.post("/api/scaffolding/chat", json=payload)

    assert response.status_code == 200
    assert response.get_json() == {"response": "mocked response"}

    assert isinstance(captured.get("profile"), UserProfile)
    assert captured["profile"].name == "Avery"
    assert captured["profile"].age == 29
    assert captured["profile"].gender == "female"
    assert captured["profile"].fitness_goals == ["strength", "mobility"]
    assert captured["message"] == payload["message"]
    assert captured["api_key"] == "test-key"
