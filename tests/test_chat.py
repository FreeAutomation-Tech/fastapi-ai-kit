from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"
    assert isinstance(data["uptime"], float)


def test_chat_validation_no_messages():
    response = client.post(
        "/api/v1/chat",
        json={"model": "gpt-4o", "messages": []},
    )
    assert response.status_code == 422


def test_chat_validation_invalid_model():
    response = client.post(
        "/api/v1/chat",
        json={
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": "Hello"}],
            "temperature": -1,
        },
    )
    assert response.status_code == 422


def test_chat_validation_missing_field():
    response = client.post(
        "/api/v1/chat",
        json={"model": "gpt-4o"},
    )
    assert response.status_code == 422


def test_chat_stream_validation():
    response = client.post(
        "/api/v1/chat/stream",
        json={"model": "gpt-4o", "messages": []},
    )
    assert response.status_code == 422


def test_embeddings_validation():
    response = client.post(
        "/api/v1/embeddings",
        json={"model": "text-embedding-3-small"},
    )
    assert response.status_code == 422


def test_similarity_validation_single_input():
    response = client.post(
        "/api/v1/embeddings/similarity",
        json={
            "model": "text-embedding-3-small",
            "input": ["only one"],
        },
    )
    assert response.status_code == 422


def test_rate_limiter_disabled():
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_root_docs():
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema():
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "FastAPI AI Kit"
