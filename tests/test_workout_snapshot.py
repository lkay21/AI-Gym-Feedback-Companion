from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.main import create_app
from app.db_instance import db
from app.auth_module.models import User


@pytest.fixture()
def app():
    app = create_app()
    app.testing = True
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def user_id(app):
    with app.app_context():
        user = User(username="snapshot_user", email="snapshot@example.com")
        user.set_password("password")
        db.session.add(user)
        db.session.commit()
        return user.id


def _valid_payload(user_id: int) -> dict:
    return {
        "user_id": user_id,
        "workout_id": "workout-001",
        "workout_type": "Strength",
        "duration_minutes": 45,
        "total_volume": 1250.5,
        "calories_burned": 320,
        "average_heart_rate": 140,
        "exercises_completed": [
            {"name": "Squat", "sets": 3, "reps": 8},
            {"name": "Bench Press", "sets": 3, "reps": 10},
        ],
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }


def test_create_snapshot_missing_fields(client, user_id):
    response = client.post("/api/workout-snapshots", json={"user_id": user_id})
    assert response.status_code == 400
    payload = response.get_json()
    assert "Missing required fields" in payload.get("error", "")


def test_create_snapshot_user_not_found(client):
    response = client.post("/api/workout-snapshots", json=_valid_payload(9999))
    assert response.status_code == 404
    payload = response.get_json()
    assert payload.get("error") == "User not found"


def test_create_snapshot_negative_numeric(client, user_id):
    payload = _valid_payload(user_id)
    payload["duration_minutes"] = -5
    response = client.post("/api/workout-snapshots", json=payload)
    assert response.status_code == 400
    payload = response.get_json()
    assert payload.get("error") == "duration_minutes must be a positive integer"


def test_create_snapshot_invalid_exercises_completed(client, user_id):
    payload = _valid_payload(user_id)
    payload["exercises_completed"] = "not-a-list"
    response = client.post("/api/workout-snapshots", json=payload)
    assert response.status_code == 400
    payload = response.get_json()
    assert payload.get("error") == "exercises_completed must be an array of objects"


def test_create_snapshot_invalid_completed_at(client, user_id):
    payload = _valid_payload(user_id)
    payload["completed_at"] = "not-a-date"
    response = client.post("/api/workout-snapshots", json=payload)
    assert response.status_code == 400
    payload = response.get_json()
    assert payload.get("error") == "completed_at must be an ISO timestamp"


def test_create_and_get_snapshot(client, user_id):
    payload = _valid_payload(user_id)
    create_response = client.post("/api/workout-snapshots", json=payload)
    assert create_response.status_code == 201
    snapshot = create_response.get_json()["snapshot"]

    get_response = client.get(f"/api/workout-snapshots/{snapshot['snapshot_id']}")
    assert get_response.status_code == 200
    fetched = get_response.get_json()["snapshot"]
    assert fetched["snapshot_id"] == snapshot["snapshot_id"]
    assert fetched["user_id"] == user_id


def test_get_snapshot_not_found(client):
    response = client.get("/api/workout-snapshots/not-a-real-id")
    assert response.status_code == 404
    payload = response.get_json()
    assert payload.get("error") == "Workout snapshot not found"


def test_list_snapshots_with_pagination(client, user_id):
    payload = _valid_payload(user_id)
    client.post("/api/workout-snapshots", json=payload)
    payload["workout_id"] = "workout-002"
    client.post("/api/workout-snapshots", json=payload)

    response = client.get(f"/api/users/{user_id}/workout-snapshots?limit=1&offset=0")
    assert response.status_code == 200
    body = response.get_json()
    assert body["count"] == 1
    assert body["total"] == 2
    assert body["limit"] == 1
    assert body["offset"] == 0


def test_list_snapshots_user_not_found(client):
    response = client.get("/api/users/9999/workout-snapshots")
    assert response.status_code == 404
    payload = response.get_json()
    assert payload.get("error") == "User not found"
