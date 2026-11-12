
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import get_user_by_hash
from app.database import increment_request
from app.dependencies import get_llm
from app.main import app
from app.dependencies import get_user_by_hash, get_llm
from app import auth


TEST_KEY = "test-api-key-123"

TEST_USER = {
    "id": 1,
    "username": "testuser",
    "key_hash": __import__("hashlib").sha256(
        TEST_KEY.encode()
    ).hexdigest(),
    "request_count": 0
}


@pytest.fixture
def client():
    app.dependency_overrides[get_user_by_hash] = (
        lambda key_hash: (
            TEST_USER
            if key_hash == TEST_USER["key_hash"]
            else None
        )
    )

    app.dependency_overrides[increment_request] = (
        lambda user_id: None
    )

    app.dependency_overrides[get_llm] = (
        lambda: lambda message: f"Mocked AI: {message}"
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def valid_headers():
    return {"x-api-key": TEST_KEY}
TEST_KEY = "test-api-key-123"

TEST_USER = {
    "id": 1,
    "username": "testuser",
    "key_hash": hashlib.sha256(
        TEST_KEY.encode()
    ).hexdigest(),
    "request_count": 0
}


@pytest.fixture
def client(monkeypatch):

    app.dependency_overrides[get_user_by_hash] = (
        lambda key_hash: (
            TEST_USER
            if key_hash == TEST_USER["key_hash"]
            else None
        )
    )

    app.dependency_overrides[get_llm] = (
        lambda: lambda message: f"Mocked AI: {message}"
    )

    monkeypatch.setattr(
        auth,
        "increment_request",
        lambda user_id: None
    )

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def valid_headers():
    return {"x-api-key": TEST_KEY}