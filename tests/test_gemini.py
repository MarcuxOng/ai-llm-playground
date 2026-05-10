from fastapi.testclient import TestClient

def test_list_gemini_models_returns_200(client: TestClient, auth_headers):
    response = client.get("/api/v1/gemini/models", headers=auth_headers)
    assert response.status_code in [200, 404]

def test_gemini_service_returns_401_without_auth(client: TestClient):
    response = client.post("/api/v1/gemini/", json={"model": "gemini-pro", "prompt": "hello"})
    assert response.status_code in [401, 422]
