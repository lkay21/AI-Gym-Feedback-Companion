import json
import sys
import types

import pytest


supabase_stub = types.SimpleNamespace(create_client=lambda *args, **kwargs: None, Client=object)
botocore_exceptions_stub = types.SimpleNamespace(ClientError=Exception)
botocore_stub = types.SimpleNamespace(exceptions=botocore_exceptions_stub)
boto3_stub = types.SimpleNamespace(resource=lambda *args, **kwargs: None, client=lambda *args, **kwargs: None)

sys.modules.setdefault("supabase", supabase_stub)
sys.modules.setdefault("botocore", botocore_stub)
sys.modules.setdefault("botocore.exceptions", botocore_exceptions_stub)
sys.modules.setdefault("boto3", boto3_stub)

from app.main import create_app


@pytest.fixture()
def app():
    app = create_app()
    app.config.update({"TESTING": True})
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_generate_plan_success(client, monkeypatch):
    from app.chat_module import routes as chat_routes

    class DummyClient:
        def generate_response(self, *args, **kwargs):
            return json.dumps({
                "planName": "Test Plan",
                "weeks": [
                    {
                        "weekNumber": 1,
                        "days": [
                            {
                                "workoutType": "Upper Body",
                                "exercises": [
                                    {"name": "Bench Press", "sets": 3, "reps": 8, "weight": "70%"}
                                ],
                            }
                        ],
                    }
                ],
            })

    monkeypatch.setattr(chat_routes, "GeminiClient", DummyClient)

    response = client.post(
        "/api/chat/plan",
        json={
            "message": "Create plan",
            "startDate": "2026-02-15",
        },
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert payload["structuredPlan"]["planName"] == "Test Plan"
    assert payload["structuredPlan"]["weeks"][0]["days"][0]["date"] == "2026-02-15"


def test_generate_plan_missing_start_date(client):
    response = client.post(
        "/api/chat/plan",
        json={"message": "Create plan"},
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert "startDate" in payload["error"]


def test_generate_plan_parse_failure(client, monkeypatch):
    from app.chat_module import routes as chat_routes
    from app.fitness import plan_transformer

    class DummyClient:
        def generate_response(self, *args, **kwargs):
            return "not a plan"

    monkeypatch.setattr(chat_routes, "GeminiClient", DummyClient)
    monkeypatch.setattr(
        plan_transformer,
        "mapLLMPlanToStructuredPlan",
        lambda *args, **kwargs: (_ for _ in ()).throw(plan_transformer.PlanParseError("bad plan")),
    )

    response = client.post(
        "/api/chat/plan",
        json={
            "message": "Create plan",
            "startDate": "2026-02-15",
        },
    )

    assert response.status_code == 500
    payload = response.get_json()
    assert payload["error"] == "Failed to parse fitness plan"