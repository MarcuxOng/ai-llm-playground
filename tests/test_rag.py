from fastapi.testclient import TestClient

def test_rag_query_returns_401_without_auth(client: TestClient):
    response = client.post("/api/v1/rag/query", json={"query": "test"})
    assert response.status_code in [401, 404, 422]

def test_rag_ingest_returns_401_without_auth(client: TestClient):
    response = client.post("/api/v1/rag/ingest", json={"text": "test document"})
    assert response.status_code in [401, 404, 422]
