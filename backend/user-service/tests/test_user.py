import pytest
from fastapi.testclient import TestClient
from app.database import database
from app.main import app, get_current_user, get_user_service
from app.schemas import UserProfileResponse, UserProfileCreate, UserProfileUpdate

@pytest.fixture(scope="session", autouse=True)
def setup_indexes():
    from app.database import database
    database.user_profiles.create_index("user_id", unique=True)

@pytest.fixture(scope="session", autouse=True)
def seed_user_profile():
    """create user already exists fails withouth this, lol."""
    profiles = database.user_profiles
    profiles.delete_many({})
    profiles.create_index("user_id", unique=True, background=False)
    profiles.insert_one({
        "user_id": 1,
        "profile_picture": "avatar1.png",
        "created_at": "2025-11-11T00:00:00Z",
        "updated_at": "2025-11-11T00:00:00Z"
    })

# --- Fixtures ---
@pytest.fixture
def client():
    return TestClient(app)

def create_mock_user(user_id=1, role_id=2):
    return {"user_id": user_id, "role_id": role_id}

def create_test_profile(user_id=1):
    return UserProfileCreate(user_id=user_id, profile_picture="avatar1.png")

def create_update_profile():
    return UserProfileUpdate(profile_picture="avatar1.png")

class MockUserService:
    def get_profile(self, user_id):
        return UserProfileResponse(
            user_id=user_id,
            profile_picture="avatar1.png",
            created_at="2025-01-01T00:00:00",
            updated_at="2025-01-01T00:00:00"
        )

    def create_profile(self, profile_data):
        if profile_data.user_id == 1:
            raise ValueError("Profile already exists")
        return 2 

    def update_profile(self, user_id, update_data):
        return True

    def update_profile_picture(self, user_id, picture):
        return True

app.dependency_overrides[get_user_service] = lambda: MockUserService()

class TestUserEndpoints:

    def test_get_user_profile_success(self, client):
        app.dependency_overrides[get_current_user] = lambda: create_mock_user(user_id=1)
        response = client.get("/profiles/1")
        assert response.status_code == 200
        assert response.json()["user_id"] == 1

    def test_create_user_profile_already_exists(self, client):
        profile = create_test_profile(user_id=1)
        response = client.post("/profiles", json=profile.model_dump())
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    def test_get_user_profile_forbidden(self, client):
        app.dependency_overrides[get_current_user] = lambda: create_mock_user(user_id=2, role_id=2)
        response = client.get("/profiles/1")
        assert response.status_code == 403
        assert "Access forbidden" in response.json()["detail"]

    def test_update_profile_success(self, client):
        app.dependency_overrides[get_current_user] = lambda: create_mock_user(user_id=1)
        update_data = create_update_profile()
        response = client.put("/profiles/1", json=update_data.model_dump())
        assert response.status_code == 200
        assert response.json()["message"] == "Profile updated successfully"

    def test_update_profile_forbidden(self, client):
        app.dependency_overrides[get_current_user] = lambda: create_mock_user(user_id=2, role_id=2)
        update_data = create_update_profile()
        response = client.put("/profiles/1", json=update_data.model_dump())
        assert response.status_code == 403
        assert "Access forbidden" in response.json()["detail"]

    def test_update_profile_picture_success(self, client):
        app.dependency_overrides[get_current_user] = lambda: create_mock_user(user_id=1)
        update_data = create_update_profile()
        response = client.put("/profiles/1/picture", json=update_data.model_dump())
        assert response.status_code == 200
        assert response.json()["message"] == "Profile picture updated successfully"

# Cleanup overrides after tests
@pytest.fixture(autouse=True)
def cleanup_dependency_overrides():
    yield
    app.dependency_overrides = {}
