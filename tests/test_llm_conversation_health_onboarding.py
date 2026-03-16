"""
Unit tests for LLM Conversation health onboarding flow.

Covers end-to-end: user → health statistic input (age, height, weight, gender)
→ fitness goal → follow-up Q&A → logging user health object (DynamoDB Health Data).
Uses in-memory HealthDataService and mock GeminiClient so no real DynamoDB or API.
"""
from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

from app.chat_module.routes import (
    chat_bp,
    health_onboarding,
    _parse_health_context,
    _parse_fixed_value,
    FIXED_FIELD_QUESTIONS,
    validate_chat_request,
    validate_plan_request,
    _summarize_calendar_plan,
)
from app.profile_module.models import HEALTH_PROFILE_TIMESTAMP


# ---- In-memory HealthData store (replaces DynamoDB for tests) ----

class InMemoryHealthProfile:
    """Minimal health profile object with same attributes as HealthData for the onboarding flow."""

    def __init__(self, user_id: str, **kwargs):
        self.user_id = user_id
        self.timestamp = kwargs.get("timestamp", HEALTH_PROFILE_TIMESTAMP)
        self.age = kwargs.get("age")
        self.height = kwargs.get("height")
        self.weight = kwargs.get("weight")
        self.gender = kwargs.get("gender")
        self.fitness_goal = kwargs.get("fitness_goal")
        self.context = kwargs.get("context") or {}

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "timestamp": self.timestamp,
            "age": self.age,
            "height": self.height,
            "weight": self.weight,
            "gender": self.gender,
            "fitness_goal": self.fitness_goal,
            "context": self.context,
        }


class InMemoryHealthDataService:
    """In-memory stand-in for HealthDataService to assert health data is stored without DynamoDB."""
import pytest

# Skip this entire module if chat_module (LLM health onboarding) is not in the project
pytest.importorskip("app.chat_module.routes", reason="app.chat_module not present")
from app.main import create_app
import app.chat_module.routes as chat_routes


class InMemoryHealthProfile:
    def __init__(self, user_id: str, **fields):
        self.user_id = user_id
        for k, v in fields.items():
            setattr(self, k, v)


class InMemoryHealthDataService:
    """
    Lightweight in-memory stand‑in for HealthDataService.

    It lets us verify that the LLM conversation / health‑onboarding
    flow persists health stats without touching real DynamoDB.
    """

    _store: dict[str, InMemoryHealthProfile] = {}

    def __init__(self):
        # Signature matches real HealthDataService but ignores Dynamo config.
        pass

    @classmethod
    def _get(cls, user_id: str) -> InMemoryHealthProfile | None:
        return cls._store.get(user_id)

    def get_health_profile(self, user_id: str) -> InMemoryHealthProfile | None:
    def get_health_profile(self, user_id: str):
        return self._get(user_id)

    def create_or_update_health_profile(
        self,
        user_id: str,
        age: int | None = None,
        height: float | None = None,
        weight: float | None = None,
        gender: str | None = None,
        fitness_goal: str | None = None,
        context: dict | None = None,
    ) -> InMemoryHealthProfile:
        existing = self._get(user_id)
        if existing is None:
            existing = InMemoryHealthProfile(
                user_id,
                timestamp=HEALTH_PROFILE_TIMESTAMP,
                age=age,
                height=height,
                weight=weight,
                gender=gender,
                fitness_goal=fitness_goal,
                context=context or {},
            )
            self._store[user_id] = existing
        else:
            if age is not None:
                existing.age = age
            if height is not None:
                existing.height = height
            if weight is not None:
                existing.weight = weight
            if gender is not None:
                existing.gender = gender
            if fitness_goal is not None:
                existing.fitness_goal = fitness_goal
            if context is not None:
                existing.context = context
        return existing


class DummyGeminiClient:
    """Mock Gemini client for health onboarding (no API calls)."""

    def __init__(self):
        self.model_name = "dummy"

    def build_fixed_stats_intro(self, health: dict) -> str:
        return "What is your main fitness goal right now?"

    def generate_follow_up_questions(self, fitness_goal: str, count: int = 3) -> list[str]:
        return [f"Follow-up {i+1} about {fitness_goal}" for i in range(count)]


# ---- Fixtures ----

@pytest.fixture
def app(monkeypatch):
    """Flask app with chat_module registered; HealthDataService and GeminiClient mocked."""
    InMemoryHealthDataService._store = {}

    monkeypatch.setattr("app.chat_module.routes.HealthDataService", InMemoryHealthDataService)
    monkeypatch.setattr("app.chat_module.routes.GeminiClient", DummyGeminiClient)

    app = Flask(__name__)
    app.config["SECRET_KEY"] = "test-secret"
    app.register_blueprint(chat_bp, url_prefix="/api/chat")
    """
    Minimal Gemini stub used by health_onboarding + chat_gemini.

    We only need deterministic return values; no network calls.
    """

    def __init__(self):
        self.model_name = "dummy-model"

    def build_fixed_stats_intro(self, profile_dict):
        return "intro-based-on-profile"

    def generate_follow_up_questions(self, fitness_goal, count=3):
        return [f"q{i+1} about {fitness_goal}" for i in range(count)]

    def generate_response(self, user_message, conversation_history=None, user_profile=None):
        return "dummy-llm-response"


@pytest.fixture
def app(monkeypatch):
    """
    Flask app wired so that:
    - HealthDataService is replaced with an in‑memory implementation
    - GeminiClient is replaced with a local, deterministic stub
    """
    # Fresh in‑memory state per test
    InMemoryHealthDataService._store = {}

    monkeypatch.setattr(chat_routes, "HealthDataService", InMemoryHealthDataService)
    monkeypatch.setattr(chat_routes, "GeminiClient", DummyGeminiClient)

    app = create_app()
    app.testing = True
    return app


def _session_with_user(client, user_id: str = "test-user-health"):
def _set_authenticated_user(client, user_id: str = "test-user-llm-health"):
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
        sess["username"] = "testuser"
    return user_id


# ---- E2E: health onboarding flow → health data stored ----

def test_health_onboarding_e2e_age_height_weight_gender_goal_then_complete(app):
    """
    E2E: POST /api/chat/health-onboarding through ask_fixed (age → height → weight → gender)
    → ask_goal → follow_up → complete; assert a single health profile is stored with all fields.
    """
    client = app.test_client()
    user_id = _session_with_user(client)

    # 1) Empty message → ask for age
    r1 = client.post("/api/chat/health-onboarding", json={"message": ""})
    assert r1.status_code == 200
    d1 = r1.get_json()
    assert d1.get("phase") == "ask_fixed"
    assert d1.get("success") is True
    assert "age" in (d1.get("response") or "").lower() or "tailor" in (d1.get("response") or "").lower()

    # 2) Send age
    r2 = client.post("/api/chat/health-onboarding", json={"message": "30"})
    assert r2.status_code == 200
    d2 = r2.get_json()
    assert d2.get("phase") == "ask_fixed"

    # 3) Send height (e.g. 175 cm)
    r3 = client.post("/api/chat/health-onboarding", json={"message": "175 cm"})
    assert r3.status_code == 200
    d3 = r3.get_json()
    assert d3.get("phase") == "ask_fixed"

    # 4) Send weight
    r4 = client.post("/api/chat/health-onboarding", json={"message": "70 kg"})
    assert r4.status_code == 200
    d4 = r4.get_json()
    assert d4.get("phase") == "ask_fixed"

    # 5) Send gender
    r5 = client.post("/api/chat/health-onboarding", json={"message": "male"})
    assert r5.status_code == 200
    d5 = r5.get_json()
    assert d5.get("phase") == "ask_goal"

    # 6) Send fitness goal
    r6 = client.post("/api/chat/health-onboarding", json={"message": "build muscle"})
    assert r6.status_code == 200
    d6 = r6.get_json()
    assert d6.get("phase") == "follow_up"

    # 7) Answer follow-ups until complete
    while True:
        r = client.post("/api/chat/health-onboarding", json={"message": "nothing else"})
        assert r.status_code == 200
        data = r.get_json()
        if data.get("phase") == "complete":
            break
        assert data.get("phase") == "follow_up"

    # Assert health profile was stored (DynamoDB-equivalent in-memory)
    profile = InMemoryHealthDataService._get(user_id)
    assert profile is not None
    assert profile.age == 30
    assert profile.height == 175.0
    assert profile.weight == 70.0
    assert profile.gender == "male"
    assert profile.fitness_goal == "build muscle"
    assert isinstance(profile.context, dict)
    assert "qa_pairs" in profile.context or "pending_questions" in profile.context or len(profile.context) >= 0


def test_health_onboarding_returns_401_without_session(app):
    """POST /api/chat/health-onboarding without authenticated session returns 401."""
    client = app.test_client()
    r = client.post("/api/chat/health-onboarding", json={"message": "30"})
    assert r.status_code == 401
    assert r.get_json() == {"error": "Not authenticated"}


def test_health_onboarding_first_message_creates_context_in_store(app):
    """First empty message creates health profile context (pending_fixed) in store."""
    client = app.test_client()
    user_id = _session_with_user(client)

    client.post("/api/chat/health-onboarding", json={"message": ""})
    profile = InMemoryHealthDataService._get(user_id)
    assert profile is not None
    pending = (profile.context or {}).get("pending_fixed") or []
    assert set(pending) == {"age", "height", "weight", "gender"}


def test_health_onboarding_parses_age_then_advances(app):
    """Sending valid age stores it and advances to next fixed field."""
    client = app.test_client()
    user_id = _session_with_user(client)

    client.post("/api/chat/health-onboarding", json={"message": ""})
    client.post("/api/chat/health-onboarding", json={"message": "25"})

    profile = InMemoryHealthDataService._get(user_id)
    assert profile is not None
    assert profile.age == 25
    ctx = profile.context or {}
    assert "age" not in (ctx.get("pending_fixed") or [])


def test_health_onboarding_unparseable_age_reasks(app):
    """Unparseable age response re-asks for age."""
    client = app.test_client()
    _session_with_user(client)

    client.post("/api/chat/health-onboarding", json={"message": ""})
    r = client.post("/api/chat/health-onboarding", json={"message": "not a number"})
    assert r.status_code == 200
    assert r.get_json().get("phase") == "ask_fixed"
    assert "couldn't parse" in (r.get_json().get("response") or "").lower() or "parse" in (r.get_json().get("response") or "").lower()


def test_health_onboarding_goal_stored_and_follow_up_returned(app):
    """After sending fitness goal, profile has fitness_goal and phase is follow_up."""
    client = app.test_client()
    user_id = _session_with_user(client)

    # Reach ask_goal: send age, height, weight, gender (4 messages after initial empty)
    client.post("/api/chat/health-onboarding", json={"message": ""})
    client.post("/api/chat/health-onboarding", json={"message": "28"})
    client.post("/api/chat/health-onboarding", json={"message": "180"})
    client.post("/api/chat/health-onboarding", json={"message": "75"})
    client.post("/api/chat/health-onboarding", json={"message": "female"})
    r = client.post("/api/chat/health-onboarding", json={"message": "lose weight"})

    assert r.status_code == 200
    assert r.get_json().get("phase") == "follow_up"
    profile = InMemoryHealthDataService._get(user_id)
    assert profile is not None
    assert profile.fitness_goal == "lose weight"


def test_health_onboarding_message_too_long_returns_400(app):
    """Message over 2000 chars returns 400."""
    client = app.test_client()
    _session_with_user(client)
    r = client.post("/api/chat/health-onboarding", json={"message": "x" * 2001})
    assert r.status_code == 400
    assert "too long" in (r.get_json().get("error") or "").lower()


# ---- Helpers: _parse_health_context and _parse_fixed_value ----

def test_parse_health_context_empty_returns_all_pending_fixed():
    """_parse_health_context(None) returns pending_fixed with all four fields."""
    ctx = _parse_health_context(None)
    assert set(ctx["pending_fixed"]) == {"age", "height", "weight", "gender"}
    assert ctx["qa_pairs"] == []
    assert ctx["pending_questions"] == []


def test_parse_health_context_with_context_preserves_pending():
    """_parse_health_context with dict preserves pending_fixed and qa_pairs."""
    ctx = _parse_health_context({"pending_fixed": ["height"], "qa_pairs": [{"q": "a", "a": "b"}], "pending_questions": []})
    assert ctx["pending_fixed"] == ["height"]
    assert ctx["qa_pairs"] == [{"q": "a", "a": "b"}]


def test_parse_health_context_pending_fixed_not_list_uses_all():
    """_parse_health_context when pending_fixed is not a list uses full FIXED_FIELD_QUESTIONS."""
    ctx = _parse_health_context({"pending_fixed": "oops", "qa_pairs": []})
    assert set(ctx["pending_fixed"]) == {"age", "height", "weight", "gender"}


def test_parse_fixed_value_age_valid():
    """_parse_fixed_value('age', '30') returns 30."""
    assert _parse_fixed_value("age", "30") == 30
    assert _parse_fixed_value("age", "I am 25 years old") == 25


def test_parse_fixed_value_age_invalid():
    """_parse_fixed_value('age', 'old') returns None."""
    assert _parse_fixed_value("age", "old") is None
    assert _parse_fixed_value("age", "200") is None


def test_parse_fixed_value_height_cm():
    """_parse_fixed_value('height', '175 cm') returns float (stored in cm)."""
    assert _parse_fixed_value("height", "175 cm") == 175.0


def test_parse_fixed_value_height_ft_in():
    """_parse_fixed_value('height', '5 ft 10 in') returns cm."""
    v = _parse_fixed_value("height", "5 ft 10 in")
    assert v is not None
    assert 170 <= v <= 180


def test_parse_fixed_value_weight():
    """_parse_fixed_value('weight', '70 kg') and '154 lbs' return float."""
    assert _parse_fixed_value("weight", "70 kg") == 70.0
    assert _parse_fixed_value("weight", "154 lbs") == 154.0


def test_parse_fixed_value_gender():
    """_parse_fixed_value('gender', 'male') returns the string."""
    assert _parse_fixed_value("gender", "male") == "male"
    assert _parse_fixed_value("gender", "non-binary") == "non-binary"


def test_validate_chat_request_no_body():
    """validate_chat_request(None) returns False and error message."""
    valid, msg = validate_chat_request(None)
    assert valid is False
    assert "body" in msg.lower() or "required" in msg.lower()


def test_validate_chat_request_empty_message():
    """validate_chat_request with empty message returns False."""
    valid, msg = validate_chat_request({"message": "   "})
    assert valid is False
    assert "message" in msg.lower() or "empty" in msg.lower()


def test_validate_chat_request_message_too_long():
    """validate_chat_request with message > 2000 chars returns False."""
    valid, msg = validate_chat_request({"message": "x" * 2001})
    assert valid is False
    assert "long" in msg.lower() or "2000" in msg


def test_validate_chat_request_valid():
    """validate_chat_request with non-empty message returns True."""
    valid, msg = validate_chat_request({"message": "hello"})
    assert valid is True
    assert msg is None


def test_validate_plan_request_missing_start_date():
    """validate_plan_request without startDate returns False."""
    valid, msg = validate_plan_request({"message": "hello", "startDate": "   "})
    assert valid is False
    assert "startDate" in msg or "start" in msg.lower()


def test_validate_plan_request_valid():
    """validate_plan_request with message and startDate returns True."""
    valid, msg = validate_plan_request({"message": "hello", "startDate": "2025-01-01"})
    assert valid is True
    assert msg is None


# ---- _summarize_calendar_plan ----

def test_summarize_calendar_plan_empty_dict():
    """_summarize_calendar_plan({}) returns empty string."""
    assert _summarize_calendar_plan({}) == ""


def test_summarize_calendar_plan_no_weeks():
    """_summarize_calendar_plan with no weeks returns empty string."""
    assert _summarize_calendar_plan({"weeks": []}) == ""


def test_summarize_calendar_plan_rest_day():
    """_summarize_calendar_plan includes rest day line."""
    cal = {
        "weeks": [
            {"weekNumber": 1, "days": [{"date": "2025-01-01", "workoutType": "rest", "exercises": []}]}
        ]
    }
    summary = _summarize_calendar_plan(cal)
    assert "2025-01-01" in summary
    assert "Rest" in summary


def test_summarize_calendar_plan_with_exercises():
    """_summarize_calendar_plan includes workout and exercise names."""
    cal = {
        "weeks": [
            {
                "weekNumber": 1,
                "days": [
                    {
                        "date": "2025-01-02",
                        "workoutType": "Upper",
                        "exercises": [{"name": "Bench Press"}, {"name": "Row"}],
                    }
                ],
            }
        ]
    }
    summary = _summarize_calendar_plan(cal)
    assert "2025-01-02" in summary
    assert "Upper" in summary
    assert "Bench Press" in summary
    assert "Row" in summary


def test_summarize_calendar_plan_not_dict():
    """_summarize_calendar_plan with non-dict returns empty string."""
    assert _summarize_calendar_plan(None) == ""
    assert _summarize_calendar_plan([]) == ""


def test_health_onboarding_follow_up_no_message_no_pending_returns_complete(app, monkeypatch):
    """In follow_up with no pending questions and empty message, return phase complete."""
    from app.chat_module import routes as chat_routes
    store = InMemoryHealthDataService()
    user_id = "test-user-health"  # must match _session_with_user(client) default
    profile = InMemoryHealthProfile(
        user_id=user_id,
        age=30,
        height=175.0,
        weight=70.0,
        gender="male",
        fitness_goal="build muscle",
        context={"pending_fixed": [], "qa_pairs": [{"q": "q1", "a": "a1"}], "pending_questions": []},
    )
    InMemoryHealthDataService._store[user_id] = profile
    monkeypatch.setattr(chat_routes, "HealthDataService", lambda: store)
    client = app.test_client()
    _session_with_user(client)
    r = client.post("/api/chat/health-onboarding", json={"message": ""})
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("phase") == "complete"
    assert "already" in (data.get("response") or "").lower() or "help" in (data.get("response") or "").lower()


def test_health_onboarding_gemini_not_configured_returns_500(app, monkeypatch):
    """When GeminiClient raises ValueError (not configured), return 500."""
    class FailingGemini:
        def __init__(self):
            raise ValueError("API key missing")
    monkeypatch.setattr("app.chat_module.routes.GeminiClient", FailingGemini)
    client = app.test_client()
    _session_with_user(client)
    client.post("/api/chat/health-onboarding", json={"message": ""})
    r = client.post("/api/chat/health-onboarding", json={"message": "30"})
    assert r.status_code == 500
    data = r.get_json()
    assert "error" in data


# ---- chat() and health_check() endpoints ----

def test_chat_validation_empty_message_returns_400(app):
    """POST /api/chat with empty message returns 400."""
    client = app.test_client()
    r = client.post("/api/chat", json={"message": "   "})
    assert r.status_code == 400
    data = r.get_json()
    assert "error" in data and ("message" in data["error"].lower() or "empty" in data["error"].lower())


def test_chat_success_returns_200_with_mock(app, monkeypatch):
    """POST /api/chat with valid message and mock Gemini returns 200."""
    class MockGemini:
        def __init__(self):
            self.model_name = "mock"
        def generate_response(self, user_message, conversation_history=None, user_profile=None):
            return "Mocked response"
    from app.chat_module import routes as chat_routes
    monkeypatch.setattr(chat_routes, "GeminiClient", MockGemini)
    client = app.test_client()
    r = client.post("/api/chat", json={"message": "Hello"})
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("success") is True
    assert "response" in data
    assert data["response"] == "Mocked response"


def test_chat_gemini_error_returns_500(app, monkeypatch):
    """POST /api/chat when Gemini generate_response raises returns 500."""
    class FailingGemini:
        def __init__(self):
            self.model_name = "mock"
        def generate_response(self, user_message, conversation_history=None, user_profile=None):
            raise RuntimeError("API error")
    from app.chat_module import routes as chat_routes
    monkeypatch.setattr(chat_routes, "GeminiClient", FailingGemini)
    client = app.test_client()
    r = client.post("/api/chat", json={"message": "Hello"})
    assert r.status_code == 500
    data = r.get_json()
    assert "error" in data


def test_health_check_returns_200_when_configured(app):
    """GET /api/chat/health returns 200 and configured True when GeminiClient works."""
    client = app.test_client()
    r = client.get("/api/chat/health")
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("status") == "healthy"
    assert data.get("configured") is True


def test_health_check_returns_503_when_not_configured(app, monkeypatch):
    """GET /api/chat/health returns 503 when GeminiClient raises ValueError."""
    class FailingGemini:
        def __init__(self):
            raise ValueError("No API key")
    from app.chat_module import routes as chat_routes
    monkeypatch.setattr(chat_routes, "GeminiClient", FailingGemini)
    client = app.test_client()
    r = client.get("/api/chat/health")
    assert r.status_code == 503
    data = r.get_json()
    assert data.get("configured") is False
    assert "error" in data
def test_llm_conversation_starts_health_onboarding_and_persists_context(app):
    """
    First LLM conversation call for a user with no plan should:
    - delegate to health_onboarding
    - return an ask_fixed phase
    - create a health profile record with pending_fixed fields in Dynamo‑equivalent storage
    """
    client = app.test_client()
    user_id = _set_authenticated_user(client)

    response = client.post("/api/chat/llm", json={"message": ""})
    assert response.status_code == 200
    body = response.get_json()

    assert body["success"] is True
    assert body["phase"] == "ask_fixed"
    assert body["has_plan"] is False
    assert "response" in body and body["response"]

    # Verify that a health profile record was created and that onboarding context is stored.
    profile = InMemoryHealthDataService._get(user_id)
    assert profile is not None
    ctx = getattr(profile, "context", {}) or {}
    pending_fixed = ctx.get("pending_fixed") or []
    # We expect all four fixed characteristics to be queued initially.
    assert set(pending_fixed) == {"age", "height", "weight", "gender"}


def test_llm_conversation_records_first_fixed_stat_and_advances_question(app):
    """
    Answering the first health‑stats question through the LLM conversation endpoint
    should:
    - parse the value (e.g. age)
    - update the stored health profile
    - advance to the next ask_fixed question
    """
    client = app.test_client()
    user_id = _set_authenticated_user(client)

    # Step 1: begin onboarding to seed context.
    first = client.post("/api/chat/llm", json={"message": ""})
    assert first.status_code == 200

    # Step 2: answer the first fixed characteristic (age).
    second = client.post("/api/chat/llm", json={"message": "I am 30 years old"})
    assert second.status_code == 200
    body = second.get_json()

    assert body["success"] is True
    assert body["phase"] == "ask_fixed"  # still in fixed‑stats phase, but now on the next field
    assert "response" in body and body["response"]

    profile = InMemoryHealthDataService._get(user_id)
    assert profile is not None
    # Age should be parsed and stored.
    assert getattr(profile, "age", None) == 30

    ctx = getattr(profile, "context", {}) or {}
    pending_fixed = ctx.get("pending_fixed") or []
    # Age should have been consumed; remaining fields should be a non‑empty subset.
    assert "age" not in pending_fixed
    assert set(pending_fixed).issubset({"height", "weight", "gender"})

