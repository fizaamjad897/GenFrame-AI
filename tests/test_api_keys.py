import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from main import app, get_current_user
import auth as auth_module

client = TestClient(app)


def _clear_overrides():
    app.dependency_overrides = {}


def test_create_api_key_success(monkeypatch):
    # use a 24-char hex string so ObjectId(...) won't raise
    user = {"_id": "60c5f8b8f1a4c2b1a2b3c4d5", "email": "test@example.com"}

    # Override the auth dependency to return our user
    app.dependency_overrides[get_current_user] = lambda: user

    # Mock generator
    called = {}

    def fake_generate(user_id):
        called['user_id'] = user_id
        return "raw_api_key_ABC"

    # Patch auth module generator (main calls auth_module.generate_api_key_for_user)
    monkeypatch.setattr(auth_module, "generate_api_key_for_user", fake_generate)

    resp = client.post("/api/users/api-key")
    assert resp.status_code == 200
    data = resp.json()
    assert data["api_key"] == "raw_api_key_ABC"
    assert "message" in data
    assert called['user_id'] == str(user["_id"])

    _clear_overrides()


def test_create_api_key_already_exists():
    user = {"_id": "user123", "apiKeyHash": "exists"}
    app.dependency_overrides[get_current_user] = lambda: user

    resp = client.post("/api/users/api-key")
    assert resp.status_code == 400
    assert "API key already exists" in resp.json()["detail"]

    _clear_overrides()


def test_delete_api_key_success(monkeypatch):
    user = {"_id": "60c5f8b8f1a4c2b1a2b3c4d5", "email": "test@example.com"}
    app.dependency_overrides[get_current_user] = lambda: user

    monkeypatch.setattr(auth_module, "delete_api_key", lambda uid: True)

    resp = client.delete("/api/users/api-key")
    assert resp.status_code == 200
    assert resp.json()["message"] == "API key deleted"

    _clear_overrides()


def test_delete_api_key_no_key(monkeypatch):
    user = {"_id": "60c5f8b8f1a4c2b1a2b3c4d5", "email": "test@example.com"}
    app.dependency_overrides[get_current_user] = lambda: user

    monkeypatch.setattr(auth_module, "delete_api_key", lambda uid: False)

    resp = client.delete("/api/users/api-key")
    assert resp.status_code == 400
    assert "No API key to delete" in resp.json()["detail"]

    _clear_overrides()


def test_api_key_auth_flow(monkeypatch):
    # When X-API-KEY header present, verify_api_key should be called
    user = {
        "_id": "user123",
        "email": "test@example.com",
        "fullName": "API User",
        "plan": "Free Tier",
        "units": 0,
        "maxUnits": 50,
        "createdAt": datetime.utcnow(),
    }

    def fake_verify(raw):
        return user if raw == "valid-key" else None

    monkeypatch.setattr(auth_module, "verify_api_key", fake_verify)

    # Valid key
    resp = client.get("/api/users/me", headers={"X-API-KEY": "valid-key"})
    assert resp.status_code == 200
    json_data = resp.json()
    assert json_data["email"] == "test@example.com"

    # Invalid key
    resp = client.get("/api/users/me", headers={"X-API-KEY": "invalid-key"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid API key"
