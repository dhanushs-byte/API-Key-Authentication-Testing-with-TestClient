
import pytest
from app.main import app


def test_health(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_missing_api_key(client):
    response = client.post(
        "/chat",
        json={"message": "Hello"}
    )

    assert response.status_code == 401


def test_invalid_api_key(client):
    response = client.post(
        "/chat",
        headers={"x-api-key": "wrong-key"},
        json={"message": "Hello"}
    )

    assert response.status_code == 403


def test_valid_api_key(client, valid_headers):
    response = client.post(
        "/chat",
        headers=valid_headers,
        json={"message": "Hello"}
    )

    assert response.status_code == 200


def test_chat_validation(client, valid_headers):
    response = client.post(
        "/chat",
        headers=valid_headers,
        json={"message": ""}
    )

    assert response.status_code == 422


def test_chat_success_with_mock_llm(client, valid_headers):
    response = client.post(
        "/chat",
        headers=valid_headers,
        json={"message": "Explain Python"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["session_id"] == "session_1"
    assert data["reply"] == "Mocked AI: Explain Python"


def test_session_not_found(client, valid_headers):
    response = client.get(
        "/sessions/unknown",
        headers=valid_headers
    )

    assert response.status_code == 404


def test_error_handler(client):
    response = client.get("/test-error")

    assert response.status_code == 400
    assert response.json()["detail"] == "Demonstration error"


def test_second_user_authentication(client):
    import hashlib
    from app.dependencies import get_user_by_hash

    second_key = "second-test-key"

    second_user = {
        "id": 2,
        "username": "user2",
        "key_hash": hashlib.sha256(
            second_key.encode()
        ).hexdigest(),
        "request_count": 0
    }

    app.dependency_overrides[get_user_by_hash] = (
        lambda key_hash: (
            second_user
            if key_hash == second_user["key_hash"]
            else None
        )
    )

    response = client.post(
        "/chat",
        headers={"x-api-key": second_key},
        json={"message": "Hello user 2"}
    )

    assert response.status_code == 200
    assert response.json()["reply"] == "Mocked AI: Hello user 2"
