import sys
import types
import uuid

import pytest

# Avoid importing heavyweight CV dependencies for route-level ownership tests.
openpose_stub = types.ModuleType("app.exercises.openpose")
openpose_stub.user_output = lambda *_args, **_kwargs: (0.8, {"RWrist": 0.9}, {}, {}, {}, "OK")
sys.modules.setdefault("app.exercises.openpose", openpose_stub)

import app.main as main_module
import app.exercises.routes as routes_module
from app.db_instance import db
from app.exercises.models import VideoAsset


@pytest.fixture
def app(monkeypatch, tmp_path):
    monkeypatch.setattr(main_module, "load_fitness_benchmarks", lambda: {"strength": {"example": 1}})
    monkeypatch.setattr(routes_module, "VIDEO_IN_DIR", str(tmp_path))

    app = main_module.create_app()
    app.testing = True
    with app.app_context():
        db.create_all()
    return app


@pytest.fixture
def seeded_asset(app):
    asset_id = f"asset_{uuid.uuid4().hex}"
    with app.app_context():
        asset = VideoAsset(
            asset_id=asset_id,
            owner_user_id="owner-123",
            exercise="bicep_curl",
            original_filename="clip.mp4",
            raw_s3_key="owner-123_bicep_curl?clip.mp4_raw",
            pose_s3_key="owner-123_bicep_curl?clip.mp4",
        )
        db.session.add(asset)
        db.session.commit()
    return asset_id


def test_get_raw_video_url_requires_authentication(app, seeded_asset):
    client = app.test_client()
    response = client.get(f"/api/cv/assets/{seeded_asset}/raw")

    assert response.status_code == 401
    assert response.get_json()["error"] == "Authentication required"


def test_get_raw_video_url_rejects_non_owner(app, seeded_asset):
    client = app.test_client()
    response = client.get(
        f"/api/cv/assets/{seeded_asset}/raw",
        headers={"X-User-Id": "other-user"},
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "Not authorized to access this video resource"


def test_get_raw_video_url_allows_owner(app, seeded_asset, monkeypatch):
    monkeypatch.setattr(routes_module, "_build_presigned_get_url", lambda key, expires_seconds=900: f"https://example.test/{key}")

    client = app.test_client()
    response = client.get(
        f"/api/cv/assets/{seeded_asset}/raw",
        headers={"X-User-Id": "owner-123"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["asset_id"] == seeded_asset
    assert payload["resource"] == "raw_video"
    assert payload["s3_key"] == "owner-123_bicep_curl?clip.mp4_raw"
    assert payload["url"].startswith("https://example.test/")


def test_get_pose_video_url_allows_owner(app, seeded_asset, monkeypatch):
    monkeypatch.setattr(routes_module, "_build_presigned_get_url", lambda key, expires_seconds=900: f"https://example.test/{key}")

    client = app.test_client()
    response = client.get(
        f"/api/cv/assets/{seeded_asset}/pose",
        headers={"X-User-Id": "owner-123"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["asset_id"] == seeded_asset
    assert payload["resource"] == "pose_video"
    assert payload["s3_key"] == "owner-123_bicep_curl?clip.mp4"
    assert payload["url"].startswith("https://example.test/")


def test_get_asset_metadata_rejects_non_owner(app, seeded_asset):
    client = app.test_client()
    response = client.get(
        f"/api/cv/assets/{seeded_asset}",
        headers={"X-User-Id": "other-user"},
    )

    assert response.status_code == 403
    assert response.get_json()["error"] == "Not authorized to access this video resource"
