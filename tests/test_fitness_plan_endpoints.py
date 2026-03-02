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


def _login(client, user_id="test_user_123"):
    with client.session_transaction() as sess:
        sess["user_id"] = user_id


def test_list_fitness_plans_success(client, monkeypatch):
    from app.fitness_plan_module.models import FitnessPlan
    from app.fitness_plan_module import routes as fp_routes

    class MockFitnessPlanService:
        def get_by_user(self, user_id, limit=100, workout_id_after=None):
            assert user_id == "test_user_123"
            assert limit == 50
            assert workout_id_after == "w000"
            return [
                FitnessPlan(
                    user_id=user_id,
                    workout_id="w001",
                    exercise_name="Squat",
                    rep_count=10,
                )
            ]

    monkeypatch.setattr(fp_routes, "FitnessPlanService", MockFitnessPlanService)
    _login(client)

    response = client.get("/api/fitness-plan?limit=50&workout_id_after=w000")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["count"] == 1
    assert payload["fitness_plans"][0]["workout_id"] == "w001"


def test_create_fitness_plan_success(client, monkeypatch):
    from app.fitness_plan_module import routes as fp_routes

    class MockFitnessPlanService:
        def create(self, plan):
            return plan

    monkeypatch.setattr(fp_routes, "FitnessPlanService", MockFitnessPlanService)
    _login(client)

    response = client.post(
        "/api/fitness-plan",
        json={
            "workout_id": "w002",
            "date_of_workout": "2026-03-01",
            "exercise_name": "Bench Press",
            "rep_count": 8,
            "muscle_group": "Chest",
        },
    )

    assert response.status_code == 201
    payload = response.get_json()
    assert payload["message"] == "Created"
    assert payload["fitness_plan"]["user_id"] == "test_user_123"
    assert payload["fitness_plan"]["workout_id"] == "w002"


def test_get_fitness_plan_success(client, monkeypatch):
    from app.fitness_plan_module.models import FitnessPlan
    from app.fitness_plan_module import routes as fp_routes

    class MockFitnessPlanService:
        def get(self, user_id, workout_id):
            assert user_id == "test_user_123"
            assert workout_id == "w010"
            return FitnessPlan(
                user_id=user_id,
                workout_id=workout_id,
                exercise_name="Deadlift",
                rep_count=5,
            )

    monkeypatch.setattr(fp_routes, "FitnessPlanService", MockFitnessPlanService)
    _login(client)

    response = client.get("/api/fitness-plan/w010")

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["fitness_plan"]["exercise_name"] == "Deadlift"


def test_update_fitness_plan_success(client, monkeypatch):
    from app.fitness_plan_module.models import FitnessPlan
    from app.fitness_plan_module import routes as fp_routes

    class MockFitnessPlanService:
        def update(self, user_id, workout_id, updates):
            assert user_id == "test_user_123"
            assert workout_id == "w020"
            assert updates == {"rep_count": 12, "muscle_group": "Legs"}
            return FitnessPlan(
                user_id=user_id,
                workout_id=workout_id,
                exercise_name="Lunge",
                rep_count=12,
                muscle_group="Legs",
            )

    monkeypatch.setattr(fp_routes, "FitnessPlanService", MockFitnessPlanService)
    _login(client)

    response = client.put(
        "/api/fitness-plan/w020",
        json={"rep_count": 12, "muscle_group": "Legs", "ignored": "x"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["message"] == "Updated"
    assert payload["fitness_plan"]["rep_count"] == 12


def test_delete_fitness_plan_success(client, monkeypatch):
    from app.fitness_plan_module import routes as fp_routes

    class MockFitnessPlanService:
        def delete(self, user_id, workout_id):
            assert user_id == "test_user_123"
            assert workout_id == "w030"
            return True

    monkeypatch.setattr(fp_routes, "FitnessPlanService", MockFitnessPlanService)
    _login(client)

    response = client.delete("/api/fitness-plan/w030")

    assert response.status_code == 200
    assert response.get_json()["message"] == "Deleted"


def test_generate_endpoint_not_available(client):
    _login(client)
    response = client.post("/api/fitness-plan/generate", json={})
    assert response.status_code in (404, 405)


@pytest.mark.parametrize(
    "method,path,payload",
    [
        ("get", "/api/fitness-plan", None),
        ("post", "/api/fitness-plan", {"workout_id": "w100"}),
        ("get", "/api/fitness-plan/w100", None),
        ("put", "/api/fitness-plan/w100", {"rep_count": 10}),
        ("delete", "/api/fitness-plan/w100", None),
    ],
)
def test_fitness_plan_endpoints_require_auth(client, method, path, payload):
    request_func = getattr(client, method)
    kwargs = {"json": payload} if payload is not None else {}

    response = request_func(path, **kwargs)

    assert response.status_code == 401
    body = response.get_json()
    assert body["error"] == "Not authenticated"
