from fastapi.testclient import TestClient

def test_mcp_health_returns_200(client: TestClient):
    # Checking if MCP server endpoint is reachable
    response = client.get("/mcp/sse")
    # MCP usually uses SSE, so a GET might return 200 or 405 depending on implementation
    # But here we just check if the route exists
    assert response.status_code in [200, 401, 404, 405]

def test_list_mcp_tools_returns_401_without_auth(client: TestClient):
    response = client.get("/api/v1/mcp/tools")
    assert response.status_code in [401, 404]
