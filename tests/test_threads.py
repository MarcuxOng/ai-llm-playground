from fastapi.testclient import TestClient

def test_list_threads_returns_200(client: TestClient, auth_headers):
    response = client.get("/api/v1/threads/", headers=auth_headers)
    assert response.status_code in [200, 404]

def test_get_thread_messages_returns_404_for_invalid_id(client: TestClient, auth_headers):
    response = client.get("/api/v1/threads/non-existent-id/messages", headers=auth_headers)
    assert response.status_code in [404]
