"""Additional tests for auth utility bearer/header resolution paths."""
from types import SimpleNamespace
from unittest.mock import MagicMock

from flask import jsonify

from app.auth_module.utils import login_required, resolve_authenticated_user_id


def test_resolve_authenticated_user_id_uses_x_user_id_header(app):
    with app.test_request_context(headers={"X-User-Id": "header-user"}):
        assert resolve_authenticated_user_id() == "header-user"


def test_resolve_authenticated_user_id_uses_bearer_token(app, monkeypatch):
    fake_supabase = MagicMock()
    fake_supabase.auth.get_user.return_value = SimpleNamespace(
        user=SimpleNamespace(id="bearer-user")
    )

    monkeypatch.setattr("app.auth_module.utils.get_supabase_client", lambda: fake_supabase)

    with app.test_request_context(headers={"Authorization": "Bearer secret-token"}):
        assert resolve_authenticated_user_id() == "bearer-user"

    fake_supabase.auth.get_user.assert_called_once_with("secret-token")


def test_resolve_authenticated_user_id_returns_none_for_invalid_bearer_token(app, monkeypatch):
    fake_supabase = MagicMock()
    fake_supabase.auth.get_user.side_effect = Exception("boom")

    monkeypatch.setattr("app.auth_module.utils.get_supabase_client", lambda: fake_supabase)

    with app.test_request_context(headers={"Authorization": "Bearer secret-token"}):
        assert resolve_authenticated_user_id() is None


def test_login_required_accepts_bearer_token(app, monkeypatch):
    fake_supabase = MagicMock()
    fake_supabase.auth.get_user.return_value = SimpleNamespace(
        user=SimpleNamespace(id="bearer-user")
    )

    monkeypatch.setattr("app.auth_module.utils.get_supabase_client", lambda: fake_supabase)

    @app.route("/auth/test-bearer-protected")
    @login_required
    def _bearer_protected():
        return jsonify({"ok": True}), 200

    client = app.test_client()
    response = client.get(
        "/auth/test-bearer-protected",
        headers={"Authorization": "Bearer secret-token"},
    )

    assert response.status_code == 200
    assert response.get_json() == {"ok": True}
