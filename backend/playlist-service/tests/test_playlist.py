# tests/test_playlist.py
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# -----------------------------
# Configuración de BD SQLite temporal
# -----------------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

# -----------------------------
# Fixtures
# -----------------------------
@pytest.fixture
def client():
    """Crea un cliente de prueba de FastAPI."""
    return TestClient(app)

@pytest.fixture
def override_get_db():
    """Usa una base de datos SQLite temporal en lugar de Postgres."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# Override de dependencia global de la app
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(autouse=True)
def mock_auth(monkeypatch):
    """Mockea la verificación de token del servicio de auth."""
    def fake_get(url, headers=None):
        class FakeResponse:
            status_code = 200
            def json(self):
                return {"id": 1, "email": "mockuser@example.com"}
        return FakeResponse()
    monkeypatch.setattr("app.dependencies.dependencies.requests.get", fake_get)

# -----------------------------
# Tests
# -----------------------------
def test_create_playlist(client):
    response = client.post(
        "/playlist",
        json={"name": "Rock Classics", "description": "Old but gold"},
        headers={"Authorization": "Bearer test-token"},
    )
    print(response.json())
    assert response.status_code == 200


def test_get_all_playlists(client):
    response = client.get("/playlist/all")
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)
