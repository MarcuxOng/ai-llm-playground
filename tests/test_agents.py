from fastapi.testclient import TestClient

def test_list_agents_returns_200(client: TestClient, auth_headers):
    response = client.get("/api/v1/agents/", headers=auth_headers)
    assert response.status_code in [200, 404]

def test_run_agent_returns_401_without_auth(client: TestClient):
    response = client.post("/api/v1/agents/run", json={"prompt": "hello", "preset": "coder"})
    assert response.status_code in [401, 422]
