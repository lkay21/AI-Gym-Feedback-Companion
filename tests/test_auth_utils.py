"""Unit tests for app.auth_module.utils (login_required, get_current_user, is_authenticated)."""
import pytest
from flask import jsonify


def test_is_authenticated_false(app):
    """is_authenticated() returns False when session has no user_id."""
    with app.test_request_context():
        from app.auth_module import utils
        assert utils.is_authenticated() is False


def test_is_authenticated_true(app):
    """is_authenticated() returns True when session has user_id."""
    with app.test_request_context():
        from flask import session
        session["user_id"] = "test-user-123"
        from app.auth_module import utils
        assert utils.is_authenticated() is True


def test_get_current_user_none(app):
    """get_current_user() returns None when not logged in."""
    with app.test_request_context():
        from app.auth_module import utils
        assert utils.get_current_user() is None


def test_get_current_user_returns_user(app):
    """get_current_user() returns User when session has user_id and user exists."""
    from app.auth_module.models import User
    from app.auth_module import utils
    from app.db_instance import db

    with app.app_context():
        db.create_all()
        user = User(username="utilsuser", email="utilsuser@example.com")
        user.set_password("pass123")
        db.session.add(user)
        db.session.commit()
        uid = user.id

    with app.test_request_context():
        from flask import session
        session["user_id"] = uid
        u = utils.get_current_user()
        assert u is not None
        assert u.username == "utilsuser"


def test_login_required_unauthorized(app):
    """Route protected by login_required returns 401 when no session."""
    from app.auth_module.utils import login_required

    @app.route("/auth/test-protected")
    @login_required
    def _protected():
        return jsonify({"ok": True}), 200

    client = app.test_client()
    response = client.get("/auth/test-protected")
    assert response.status_code == 401
    assert response.get_json() == {"error": "Authentication required"}


def test_login_required_authorized(app):
    """Route protected by login_required returns 200 when session has user_id."""
    from app.auth_module.utils import login_required

    @app.route("/auth/test-protected-2")
    @login_required
    def _protected2():
        return jsonify({"ok": True}), 200

    client = app.test_client()
    with client.session_transaction() as sess:
        sess["user_id"] = "any-user-id"
    response = client.get("/auth/test-protected-2")
    assert response.status_code == 200
    assert response.get_json() == {"ok": True}
