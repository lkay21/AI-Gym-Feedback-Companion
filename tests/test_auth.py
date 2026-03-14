"""Unit tests for auth/register and auth/login APIs (Supabase-backed)."""
from unittest.mock import patch

import pytest

# Valid payloads for develop API: register requires username + email + password
REGISTER_PAYLOAD = {
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "securepass123",
}
LOGIN_PAYLOAD = {"username": "newuser@example.com", "password": "securepass123"}

# ---- Register API (validation only: no Supabase mock needed) ----

def test_register_missing_username(app):
    """POST /auth/register without username returns 400."""
    client = app.test_client()
    response = client.post(
        "/auth/register",
        json={"email": "a@b.com", "password": "securepass123"},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "Username, email, and password are required"}


def test_register_missing_email(app):
    """POST /auth/register without email returns 400."""
    client = app.test_client()
    response = client.post(
        "/auth/register",
        json={"username": "newuser", "password": "securepass123"},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "Username, email, and password are required"}


def test_register_missing_password(app):
    """POST /auth/register without password returns 400."""
    client = app.test_client()
    response = client.post(
        "/auth/register",
        json={"username": "newuser", "email": "newuser@example.com"},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "Username, email, and password are required"}


def test_register_empty_username(app):
    """POST /auth/register with empty username returns 400."""
    client = app.test_client()
    response = client.post(
        "/auth/register",
        json={"username": "", "email": "a@b.com", "password": "securepass123"},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "Username, email, and password are required"}


def test_register_empty_password(app):
    """POST /auth/register with empty password returns 400."""
    client = app.test_client()
    response = client.post(
        "/auth/register",
        json={"username": "newuser", "email": "newuser@example.com", "password": ""},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "Username, email, and password are required"}


def test_register_invalid_email(app):
    """POST /auth/register with invalid email format returns 400."""
    client = app.test_client()
    response = client.post(
        "/auth/register",
        json={"username": "newuser", "email": "not-an-email", "password": "securepass123"},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "Invalid email format"}


def test_register_short_password(app):
    """POST /auth/register with password < 6 chars returns 400."""
    client = app.test_client()
    response = client.post(
        "/auth/register",
        json={"username": "newuser", "email": "newuser@example.com", "password": "short"},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "Password must be at least 6 characters long"}


def test_register_short_username(app):
    """POST /auth/register with username < 3 chars returns 400."""
    client = app.test_client()
    response = client.post(
        "/auth/register",
        json={"username": "ab", "email": "ab@example.com", "password": "securepass123"},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "Username must be at least 3 characters long"}


def test_register_username_invalid_characters(app):
    """POST /auth/register with username containing invalid chars returns 400."""
    client = app.test_client()
    response = client.post(
        "/auth/register",
        json={"username": "user name", "email": "user@example.com", "password": "securepass123"},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {
        "error": "Username can only contain letters, numbers, underscores, and hyphens"
    }


def test_register_empty_body(app):
    """POST /auth/register with empty JSON body returns 400."""
    client = app.test_client()
    response = client.post(
        "/auth/register",
        json={},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "No data provided"}


# ---- Register API (with Supabase mock) ----

def test_register_success(app_with_supabase_mock):
    """POST /auth/register with valid username, email, password returns 201."""
    app, _ = app_with_supabase_mock
    client = app.test_client()
    response = client.post(
        "/auth/register",
        json=REGISTER_PAYLOAD,
        content_type="application/json",
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["message"] == "User registered successfully"
    assert "user" in data
    assert data["user"]["username"] == "newuser"
    assert "email" in data["user"] and "id" in data["user"]


def test_register_email_already_registered(app_with_supabase_mock):
    """POST /auth/register when email already exists returns 400."""
    app, supabase_mock = app_with_supabase_mock
    supabase_mock.auth.sign_up.side_effect = Exception("User already registered")
    client = app.test_client()
    response = client.post(
        "/auth/register",
        json=REGISTER_PAYLOAD,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "Email already registered"}


def test_register_password_requirement_error(app_with_supabase_mock):
    """POST /auth/register when Supabase returns password error returns 400."""
    app, supabase_mock = app_with_supabase_mock
    supabase_mock.auth.sign_up.side_effect = Exception("Password should be at least 6 characters")
    client = app.test_client()
    response = client.post(
        "/auth/register",
        json=REGISTER_PAYLOAD,
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "Password does not meet requirements"}


def test_register_server_config_error(app):
    """POST /auth/register when Supabase not configured returns 500."""
    client = app.test_client()
    with patch("app.auth_module.routes.get_supabase_client") as m:
        m.side_effect = ValueError("SUPABASE_URL not set")
        response = client.post(
            "/auth/register",
            json=REGISTER_PAYLOAD,
            content_type="application/json",
        )
    assert response.status_code == 500
    assert response.get_json() == {"error": "Server configuration error. Please contact administrator."}


def test_register_email_confirmation_required(app_with_supabase_mock):
    """POST /auth/register when email confirmation required returns 201 with message."""
    from types import SimpleNamespace

    app, supabase_mock = app_with_supabase_mock
    user = SimpleNamespace(
        id="uid", email="new@example.com", created_at="2024-01-01",
        user_metadata={"username": "newuser"},
    )
    supabase_mock.auth.sign_up.return_value = SimpleNamespace(user=user, session=None)
    client = app.test_client()
    response = client.post(
        "/auth/register",
        json=REGISTER_PAYLOAD,
        content_type="application/json",
    )
    assert response.status_code == 201
    data = response.get_json()
    assert "Please check your email to confirm" in data["message"]
    assert data["user"]["email_confirmed"] is False


def test_register_profile_service_failure_still_returns_201(app_with_supabase_mock):
    """POST /auth/register when ProfileService.update_profile fails still returns 201."""
    app, supabase_mock = app_with_supabase_mock
    with patch("app.auth_module.routes.ProfileService") as ProfileServiceMock:
        ProfileServiceMock.return_value.update_profile.side_effect = Exception("DynamoDB error")
        client = app.test_client()
        response = client.post(
            "/auth/register",
            json=REGISTER_PAYLOAD,
            content_type="application/json",
        )
    assert response.status_code == 201
    assert response.get_json()["message"] == "User registered successfully"


# ---- Login API (validation only) ----

def test_login_missing_username(app):
    """POST /auth/login without username returns 400."""
    client = app.test_client()
    response = client.post(
        "/auth/login",
        json={"password": "secret"},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "Username/email and password are required"}


def test_login_missing_password(app):
    """POST /auth/login without password returns 400."""
    client = app.test_client()
    response = client.post(
        "/auth/login",
        json={"username": "user@example.com"},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "Username/email and password are required"}


def test_login_empty_username(app):
    """POST /auth/login with empty string username returns 400."""
    client = app.test_client()
    response = client.post(
        "/auth/login",
        json={"username": "", "password": "any"},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "Username/email and password are required"}


def test_login_empty_password(app):
    """POST /auth/login with empty password returns 400."""
    client = app.test_client()
    response = client.post(
        "/auth/login",
        json={"username": "user@example.com", "password": ""},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "Username/email and password are required"}


# ---- Login API (with Supabase mock) ----

def test_login_success(app_with_supabase_mock):
    """POST /auth/login with correct credentials returns 200."""
    app, _ = app_with_supabase_mock
    client = app.test_client()
    response = client.post(
        "/auth/login",
        json=LOGIN_PAYLOAD,
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Login successful"
    assert data["user"]["email"] == "test@example.com"


def test_login_invalid_password(app_with_supabase_mock):
    """POST /auth/login with wrong password returns 401."""
    app, supabase_mock = app_with_supabase_mock
    supabase_mock.auth.sign_in_with_password.side_effect = Exception("Invalid login credentials")
    client = app.test_client()
    response = client.post(
        "/auth/login",
        json=LOGIN_PAYLOAD,
        content_type="application/json",
    )
    assert response.status_code == 401
    assert response.get_json() == {"error": "Invalid email or password"}


def test_login_nonexistent_user(app_with_supabase_mock):
    """POST /auth/login with unknown email returns 401."""
    app, supabase_mock = app_with_supabase_mock
    supabase_mock.auth.sign_in_with_password.side_effect = Exception("Invalid login credentials")
    client = app.test_client()
    response = client.post(
        "/auth/login",
        json={"username": "nobody@example.com", "password": "any"},
        content_type="application/json",
    )
    assert response.status_code == 401
    assert response.get_json() == {"error": "Invalid email or password"}


def test_login_email_not_confirmed(app_with_supabase_mock):
    """POST /auth/login when email not confirmed returns 401."""
    app, supabase_mock = app_with_supabase_mock
    supabase_mock.auth.sign_in_with_password.side_effect = Exception("Email not confirmed")
    client = app.test_client()
    response = client.post(
        "/auth/login",
        json=LOGIN_PAYLOAD,
        content_type="application/json",
    )
    assert response.status_code == 401
    assert response.get_json() == {"error": "Please confirm your email before logging in"}


def test_login_server_config_error(app):
    """POST /auth/login when Supabase not configured returns 500."""
    client = app.test_client()
    with patch("app.auth_module.routes.get_supabase_client") as m:
        m.side_effect = ValueError("SUPABASE_URL not set")
        response = client.post(
            "/auth/login",
            json=LOGIN_PAYLOAD,
            content_type="application/json",
        )
    assert response.status_code == 500
    assert response.get_json() == {"error": "Server configuration error. Please contact administrator."}


# ---- Logout, check session, get user (with Supabase mock) ----

def test_logout_success(app_with_supabase_mock):
    """POST /auth/logout with session returns 200 and clears session."""
    app, _ = app_with_supabase_mock
    client = app.test_client()
    # Log in first to set session
    client.post("/auth/login", json=LOGIN_PAYLOAD, content_type="application/json")
    response = client.post("/auth/logout")
    assert response.status_code == 200
    assert response.get_json() == {"message": "Logged out successfully"}


def test_check_session_not_logged_in(app):
    """GET /auth/check when not logged in returns 200 with logged_in false."""
    client = app.test_client()
    response = client.get("/auth/check")
    assert response.status_code == 200
    assert response.get_json() == {"logged_in": False}


def test_check_session_logged_in(app_with_supabase_mock):
    """GET /auth/check when logged in returns 200 with logged_in true and user."""
    app, _ = app_with_supabase_mock
    client = app.test_client()
    client.post("/auth/login", json=LOGIN_PAYLOAD, content_type="application/json")
    response = client.get("/auth/check")
    assert response.status_code == 200
    data = response.get_json()
    assert data["logged_in"] is True
    assert "user" in data
    assert data["user"]["email"] == "test@example.com"


def test_get_user_not_authenticated(app):
    """GET /auth/user without session returns 401."""
    client = app.test_client()
    response = client.get("/auth/user")
    assert response.status_code == 401
    assert response.get_json() == {"error": "Not authenticated"}


def test_get_user_success(app_with_supabase_mock):
    """GET /auth/user when logged in returns 200 with user info."""
    app, _ = app_with_supabase_mock
    client = app.test_client()
    client.post("/auth/login", json=LOGIN_PAYLOAD, content_type="application/json")
    response = client.get("/auth/user")
    assert response.status_code == 200
    data = response.get_json()
    assert "user" in data
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["username"] == "testuser"


def test_supabase_client_raises_when_credentials_missing():
    """get_supabase_client() raises ValueError when SUPABASE_URL or key not set."""
    from app.auth_module import supabase_client

    with patch.object(supabase_client, "SUPABASE_URL", None):
        with pytest.raises(ValueError) as exc_info:
            supabase_client.get_supabase_client()
        assert "SUPABASE" in str(exc_info.value) and "credentials" in str(exc_info.value).lower()
