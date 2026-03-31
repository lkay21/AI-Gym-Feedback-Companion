"""
Integration tests for Chat API (POST /api/chat) with authentication and request validation.

Covers: valid session, invalid/missing auth semantics, optional profile and conversation_history,
and validation (empty message, message too long) to catch regressions in the real request/response flow.
"""
import sys
import types

import pytest

# Stub external deps so create_app() can load (same as test_chat_plan_endpoint)
supabase_stub = types.SimpleNamespace(create_client=lambda *args, **kwargs: None, Client=object)
botocore_exceptions_stub = types.SimpleNamespace(ClientError=Exception)
botocore_stub = types.SimpleNamespace(exceptions=botocore_exceptions_stub)
boto3_stub = types.SimpleNamespace(resource=lambda *args, **kwargs: None, client=lambda *args, **kwargs: None)
sys.modules.setdefault("supabase", supabase_stub)
sys.modules.setdefault("botocore", botocore_stub)
sys.modules.setdefault("botocore.exceptions", botocore_exceptions_stub)
sys.modules.setdefault("boto3", boto3_stub)

from app.main import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config.update({"TESTING": True})
    return app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def mock_gemini(monkeypatch):
    """Mock GeminiClient so POST /api/chat returns a fixed response without calling the API."""
    from app.chat_module import routes as chat_routes

    class MockGeminiClient:
        def __init__(self):
            self.model_name = "integration-test-mock"

        def generate_response(self, user_message, conversation_history=None, user_profile=None):
            return "Integration test reply"

    monkeypatch.setattr(chat_routes, "GeminiClient", MockGeminiClient)


@pytest.fixture
def authenticated_session(client):
    """Set a valid session so requests are treated as authenticated."""
    with client.session_transaction() as sess:
        sess["user_id"] = "integration_test_user"
        sess["username"] = "testuser"
    return "integration_test_user"


# ---- Valid request: with and without auth ----

def test_chat_with_valid_message_returns_200(client, mock_gemini):
    """POST /api/chat with valid message returns 200 and AI response."""
    response = client.post("/api/chat", json={"message": "What exercises are good for beginners?"})
    assert response.status_code == 200
    data = response.get_json()
    assert data.get("success") is True
    assert "response" in data
    assert data["response"] == "Integration test reply"


def test_chat_with_valid_session_returns_200(client, mock_gemini, authenticated_session):
    """POST /api/chat with valid session and message returns 200."""
    response = client.post("/api/chat", json={"message": "Hello"})
    assert response.status_code == 200
    data = response.get_json()
    assert data.get("success") is True
    assert "response" in data


def test_chat_with_profile_returns_200(client, mock_gemini):
    """POST /api/chat with optional profile passes through and returns 200."""
    payload = {
        "message": "Suggest a workout",
        "profile": {
            "name": "Test User",
            "age": 25,
            "fitness_goals": ["build muscle"],
            "activity_level": "moderate",
        },
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data.get("success") is True
    assert "response" in data


def test_chat_with_conversation_history_returns_200(client, mock_gemini):
    """POST /api/chat with optional conversation_history returns 200."""
    payload = {
        "message": "What about cardio?",
        "conversation_history": [
            {"role": "user", "content": "I want to lose weight"},
            {"role": "assistant", "content": "Here are some tips..."},
        ],
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data.get("success") is True
    assert "response" in data


# ---- Validation: invalid request body ----

def test_chat_empty_message_returns_400(client, mock_gemini):
    """POST /api/chat with empty or whitespace message returns 400."""
    response = client.post("/api/chat", json={"message": ""})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "message" in data["error"].lower() or "empty" in data["error"].lower()

    response2 = client.post("/api/chat", json={"message": "   \n  "})
    assert response2.status_code == 400
    assert "error" in response2.get_json()


def test_chat_message_too_long_returns_400(client, mock_gemini):
    """POST /api/chat with message over 2000 chars returns 400."""
    response = client.post("/api/chat", json={"message": "x" * 2001})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "2000" in data["error"] or "long" in data["error"].lower()


def test_chat_missing_body_returns_400(client, mock_gemini):
    """POST /api/chat with no JSON body or missing message returns 400."""
    response = client.post("/api/chat", json={})
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

    # Invalid/empty JSON body: request.get_json() raises BadRequest; route may return 400 or 500
    response2 = client.post(
        "/api/chat",
        data="",
        content_type="application/json",
    )
    assert response2.status_code in (400, 500)
    if response2.get_json():
        assert "error" in response2.get_json()


# ---- Error handling: Gemini not configured ----

def test_chat_gemini_not_configured_returns_500(client, monkeypatch):
    """POST /api/chat when GeminiClient raises ValueError returns 500."""
    from app.chat_module import routes as chat_routes

    class FailingGemini:
        def __init__(self):
            raise ValueError("API key missing")

    monkeypatch.setattr(chat_routes, "GeminiClient", FailingGemini)
    response = client.post("/api/chat", json={"message": "Hello"})
    assert response.status_code == 500
    data = response.get_json()
    assert "error" in data
    assert "configured" in data.get("error", "").lower() or "details" in data
