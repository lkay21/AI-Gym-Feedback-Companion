import io
import sys
import types

import pytest

# Avoid importing heavyweight CV dependencies for route-level validation tests.
openpose_stub = types.ModuleType("app.exercises.openpose")
openpose_stub.user_output = lambda *_args, **_kwargs: None
sys.modules.setdefault("app.exercises.openpose", openpose_stub)

import app.main as main_module
import app.exercises.routes as routes_module


@pytest.fixture
def app(monkeypatch, tmp_path):
    monkeypatch.setattr(main_module, "load_fitness_benchmarks", lambda: {"strength": {"example": 1}})
    monkeypatch.setattr(routes_module, "VIDEO_IN_DIR", str(tmp_path))

    app = main_module.create_app()
    app.testing = True
    return app


def test_analyze_video_rejects_unsupported_mime(monkeypatch, app, tmp_path):
    parse_mock_called = {"called": False}

    def fake_parse(*_args, **_kwargs):
        parse_mock_called["called"] = True
        return {}

    monkeypatch.setattr(routes_module, "parse_user_video", fake_parse)

    client = app.test_client()
    response = client.post(
        "/api/cv/analyze",
        data={
            "exercise": "bicep_curl",
            "user_id": "user123",
            "video": (io.BytesIO(b"not-a-video"), "clip.mp4", "text/plain"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 415
    payload = response.get_json()
    assert payload["error"] == "unsupported video MIME type"
    assert parse_mock_called["called"] is False
    assert list(tmp_path.iterdir()) == []


def test_analyze_video_rejects_oversized_upload(monkeypatch, app, tmp_path):
    monkeypatch.setattr(routes_module, "MAX_VIDEO_UPLOAD_SIZE_BYTES", 8)

    parse_mock_called = {"called": False}

    def fake_parse(*_args, **_kwargs):
        parse_mock_called["called"] = True
        return {}

    monkeypatch.setattr(routes_module, "parse_user_video", fake_parse)

    client = app.test_client()
    response = client.post(
        "/api/cv/analyze",
        data={
            "exercise": "bicep_curl",
            "user_id": "user123",
            "video": (io.BytesIO(b"0123456789"), "clip.mp4", "video/mp4"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 413
    payload = response.get_json()
    assert payload["error"] == "uploaded video file exceeds maximum allowed size"
    assert payload["max_size_bytes"] == 8
    assert payload["received_size_bytes"] == 10
    assert parse_mock_called["called"] is False
    assert list(tmp_path.iterdir()) == []


def test_analyze_video_accepts_valid_upload(monkeypatch, app):
    expected_output = {
        "form_score": 92.5,
        "joint_scores": {"RWrist": 93.0},
        "feedback": "Great form!",
    }

    def fake_parse(_filename, _exercise, _user_id):
        return dict(expected_output)

    monkeypatch.setattr(routes_module, "parse_user_video", fake_parse)

    client = app.test_client()
    response = client.post(
        "/api/cv/analyze",
        data={
            "exercise": "bicep_curl",
            "user_id": "user123",
            "video": (io.BytesIO(b"01234567"), "clip.mp4", "video/mp4"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["form_score"] == expected_output["form_score"]
    assert payload["joint_scores"] == expected_output["joint_scores"]
    assert payload["feedback"] == expected_output["feedback"]
    assert payload["exercise"] == "bicep_curl"
    assert payload["user_id"] == "user123"
