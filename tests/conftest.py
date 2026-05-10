import pytest
from fastapi.testclient import TestClient
from app.app import app
from app.config import settings

@pytest.fixture
def client():
    # Use a dummy master key if not set to ensure auth passes for tests that use it
    if not settings.master_api_key:
        settings.master_api_key = "test-master-key"
    return TestClient(app)

@pytest.fixture
def auth_headers():
    return {"X-API-Key": settings.master_api_key or "test-master-key"}

@pytest.fixture
def mock_gemini_client(monkeypatch):
    class MockClient:
        def __init__(self, *args, **kwargs):
            pass
        class Models:
            def list_models(self):
                return []
        models = Models()

    monkeypatch.setattr("google.genai.Client", MockClient)
    return MockClient
