import io
import os
import sys
import types

import pytest

# Keep limits low in tests so 429 behavior is exercised quickly.
os.environ.setdefault("CV_UPLOAD_USER_RATE_LIMIT", "2 per minute")
os.environ.setdefault("CV_UPLOAD_IP_RATE_LIMIT", "5 per minute")

# Avoid importing heavyweight CV dependencies for route-level tests.
openpose_stub = types.ModuleType("app.exercises.openpose")
openpose_stub.user_output = lambda *_args, **_kwargs: (0.8, {"RWrist": 0.9}, {}, {}, {}, "OK")
sys.modules.setdefault("app.exercises.openpose", openpose_stub)

import app.main as main_module
import app.exercises.routes as routes_module
import app.rate_limit as rate_limit_module
from app.db_instance import db
from app.exercises.models import VideoAsset  # noqa: F401


@pytest.fixture
def app(monkeypatch, tmp_path):
    monkeypatch.setattr(main_module, "load_fitness_benchmarks", lambda: {"strength": {"example": 1}})
    monkeypatch.setattr(routes_module, "VIDEO_IN_DIR", str(tmp_path))
    monkeypatch.setattr(
        routes_module,
        "parse_user_video",
        lambda _filename, _exercise, _user_id: {
            "form_score": 90.0,
            "joint_scores": {"RWrist": 90.0},
            "feedback": "Good",
        },
    )

    app = main_module.create_app()
    app.testing = True
    with app.app_context():
        db.create_all()
    return app


def _post_upload(client, *, user_id, ip_address):
    return client.post(
        "/api/cv/analyze",
        data={
            "exercise": "bicep_curl",
            "user_id": user_id,
            "video": (io.BytesIO(b"tiny-bytes"), "clip.mp4", "video/mp4"),
        },
        content_type="multipart/form-data",
        headers={"X-User-Id": user_id},
        environ_base={"REMOTE_ADDR": ip_address},
    )


def test_upload_rate_limit_per_authenticated_user(app):
    client = app.test_client()

    r1 = _post_upload(client, user_id="user-a", ip_address="198.51.100.10")
    r2 = _post_upload(client, user_id="user-a", ip_address="198.51.100.10")
    r3 = _post_upload(client, user_id="user-a", ip_address="198.51.100.10")

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r3.status_code == 429
    payload = r3.get_json()
    assert payload["error"] == "Rate limit exceeded"


def test_upload_rate_limit_per_ip_address(app):
    client = app.test_client()

    responses = []
    for i in range(6):
        responses.append(_post_upload(client, user_id=f"user-{i}", ip_address="203.0.113.20"))

    assert responses[0].status_code == 200
    assert responses[4].status_code == 200
    assert responses[5].status_code == 429


def test_rate_limit_violation_is_logged(app, monkeypatch):
    warnings = []

    def _fake_warning(msg, *args):
        warnings.append(msg % args)

    monkeypatch.setattr(rate_limit_module.logger, "warning", _fake_warning)

    client = app.test_client()
    _post_upload(client, user_id="log-user", ip_address="192.0.2.99")
    _post_upload(client, user_id="log-user", ip_address="192.0.2.99")
    limited = _post_upload(client, user_id="log-user", ip_address="192.0.2.99")

    assert limited.status_code == 429
    assert any("Rate limit exceeded" in message for message in warnings)
