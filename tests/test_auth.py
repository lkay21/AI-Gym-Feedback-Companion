"""Unit tests for auth/register and auth/login APIs (Supabase-backed)."""
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
