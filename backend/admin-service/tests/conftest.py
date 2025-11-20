import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies.dependencies import get_admin_service
from app.services.admin_service import AdminService

def fake_admin():
    return {"user_id": 999, "role_id": 1}

@pytest.fixture(autouse=True)
def override_admin_required():
    from app.core.security import admin_required
    app.dependency_overrides[admin_required] = lambda: fake_admin()
    yield
    app.dependency_overrides = {}

#mock httpclient

class MockHTTPClient:
    def __init__(self, responses):
        self.responses = responses

    async def get(self, path, params=None):
        return self.responses.get(("GET", path))

    async def patch(self, path, json=None):
        return self.responses.get(("PATCH", path))

class FakeResponse:
    def __init__(self, status, data):
        self.status_code = status
        self._data = data

    def json(self):
        return self._data
    
@pytest.fixture
def client(request):
    responses = getattr(request, "param", {})
    
    def get_mock_service():
        service = AdminService()
        service.client = MockHTTPClient(responses)
        return service

    app.dependency_overrides[get_admin_service] = get_mock_service

    return TestClient(app)