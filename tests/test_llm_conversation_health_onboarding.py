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

    def get_health_profile(self, user_id: str):
        return self._get(user_id)

    def create_or_update_health_profile(
        self,
        user_id: str,
        age=None,
        height=None,
        weight=None,
        gender=None,
        fitness_goal=None,
        context=None,
    ):
        existing = self._get(user_id)
        if existing is None:
            existing = InMemoryHealthProfile(
                user_id,
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


def _set_authenticated_user(client, user_id: str = "test-user-llm-health"):
    with client.session_transaction() as sess:
        sess["user_id"] = user_id
        sess["username"] = "testuser"
    return user_id


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

