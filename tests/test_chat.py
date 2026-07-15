from fastapi.testclient import TestClient

from app.main import app
from app.memory.store import session_store

client = TestClient(app)


def test_health_check():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.2.0"
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


def test_create_session():
    response = client.post("/api/v1/sessions")
    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert data["message_count"] == 0


def test_list_sessions():
    response = client.get("/api/v1/sessions")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_session():
    create = client.post("/api/v1/sessions")
    sid = create.json()["session_id"]
    response = client.get(f"/api/v1/sessions/{sid}")
    assert response.status_code == 200
    assert response.json()["id"] == sid


def test_get_session_messages():
    create = client.post("/api/v1/sessions")
    sid = create.json()["session_id"]
    response = client.get(f"/api/v1/sessions/{sid}/messages")
    assert response.status_code == 200
    assert response.json() == []


def test_get_session_not_found():
    response = client.get("/api/v1/sessions/nonexistent")
    assert response.status_code == 404


def test_delete_session():
    create = client.post("/api/v1/sessions")
    sid = create.json()["session_id"]
    response = client.delete(f"/api/v1/sessions/{sid}")
    assert response.status_code == 200
    assert response.json()["status"] == "deleted"


def test_list_tools():
    response = client.get("/api/v1/tools")
    assert response.status_code == 200
    tools = response.json()
    assert len(tools) >= 3
    tool_names = [t["name"] for t in tools]
    assert "calculator" in tool_names
    assert "web_search" in tool_names
    assert "file_reader" in tool_names


def test_agent_execute_no_session():
    response = client.post(
        "/api/v1/agents/execute",
        json={
            "session_id": "nonexistent",
            "message": "Hello",
        },
    )
    assert response.status_code == 404


def test_mcp_message_no_session():
    response = client.post(
        "/api/v1/mcp/message?client_id=nonexistent",
        json={"method": "tools/list", "id": "1"},
    )
    assert response.status_code == 404
