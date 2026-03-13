"""Unit tests for auth/register and auth/login APIs."""
import pytest


# ---- Register API ----

def test_register_success(app):
    """POST /auth/register with valid username and password returns 201 and creates user."""
    client = app.test_client()
    response = client.post(
        "/auth/register",
        json={"username": "newuser", "password": "securepass123"},
        content_type="application/json",
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data == {"message": "User registered successfully"}

    # User can log in after registration
    login_resp = client.post(
        "/auth/login",
        json={"username": "newuser", "password": "securepass123"},
        content_type="application/json",
    )
    assert login_resp.status_code == 200
    assert login_resp.get_json() == {"message": "Login successful"}


def test_register_missing_username(app):
    """POST /auth/register without username returns 400."""
    client = app.test_client()
    response = client.post(
        "/auth/register",
        json={"password": "securepass123"},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing username or password"}


def test_register_missing_password(app):
    """POST /auth/register without password returns 400."""
    client = app.test_client()
    response = client.post(
        "/auth/register",
        json={"username": "newuser"},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing username or password"}


def test_register_empty_username(app):
    """POST /auth/register with empty username returns 400."""
    client = app.test_client()
    response = client.post(
        "/auth/register",
        json={"username": "", "password": "securepass123"},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing username or password"}


def test_register_empty_password(app):
    """POST /auth/register with empty password returns 400."""
    client = app.test_client()
    response = client.post(
        "/auth/register",
        json={"username": "newuser", "password": ""},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing username or password"}


def test_register_username_already_exists(app):
    """POST /auth/register with existing username returns 400."""
    client = app.test_client()
    client.post(
        "/auth/register",
        json={"username": "existinguser", "password": "firstpass"},
        content_type="application/json",
    )
    response = client.post(
        "/auth/register",
        json={"username": "existinguser", "password": "secondpass"},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "Username already exists"}


def test_register_empty_body(app):
    """POST /auth/register with empty JSON body returns 400 (missing username/password)."""
    client = app.test_client()
    response = client.post(
        "/auth/register",
        json={},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing username or password"}


# ---- Login API ----

def test_login_success(app):
    """POST /auth/login with correct credentials returns 200."""
    client = app.test_client()
    client.post(
        "/auth/register",
        json={"username": "logintest", "password": "mypassword"},
        content_type="application/json",
    )
    response = client.post(
        "/auth/login",
        json={"username": "logintest", "password": "mypassword"},
        content_type="application/json",
    )
    assert response.status_code == 200
    assert response.get_json() == {"message": "Login successful"}


def test_login_invalid_password(app):
    """POST /auth/login with wrong password returns 401."""
    client = app.test_client()
    client.post(
        "/auth/register",
        json={"username": "logintest", "password": "correct"},
        content_type="application/json",
    )
    response = client.post(
        "/auth/login",
        json={"username": "logintest", "password": "wrong"},
        content_type="application/json",
    )
    assert response.status_code == 401
    assert response.get_json() == {"error": "Invalid username or password"}


def test_login_nonexistent_user(app):
    """POST /auth/login with unknown username returns 401."""
    client = app.test_client()
    response = client.post(
        "/auth/login",
        json={"username": "nobody", "password": "any"},
        content_type="application/json",
    )
    assert response.status_code == 401
    assert response.get_json() == {"error": "Invalid username or password"}


def test_login_missing_username(app):
    """POST /auth/login without username returns 400 (missing credentials)."""
    client = app.test_client()
    response = client.post(
        "/auth/login",
        json={"password": "secret"},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing username or password"}


def test_login_missing_password(app):
    """POST /auth/login without password returns 400 (missing credentials)."""
    client = app.test_client()
    client.post(
        "/auth/register",
        json={"username": "nopass", "password": "real"},
        content_type="application/json",
    )
    response = client.post(
        "/auth/login",
        json={"username": "nopass"},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing username or password"}


def test_login_empty_username(app):
    """POST /auth/login with empty string username returns 400."""
    client = app.test_client()
    response = client.post(
        "/auth/login",
        json={"username": "", "password": "any"},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing username or password"}


def test_login_empty_password(app):
    """POST /auth/login with empty password returns 400."""
    client = app.test_client()
    client.post(
        "/auth/register",
        json={"username": "empty", "password": "real"},
        content_type="application/json",
    )
    response = client.post(
        "/auth/login",
        json={"username": "empty", "password": ""},
        content_type="application/json",
    )
    assert response.status_code == 400
    assert response.get_json() == {"error": "Missing username or password"}
