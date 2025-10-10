import pytest
from tests.test_data import TEST_USER_REGISTER, TEST_USER_LOGIN

class TestAuthEndpoints:
    def test_register_user(self, client):
        response = client.post("/register", json=TEST_USER_REGISTER.model_dump())

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == TEST_USER_REGISTER.email
        assert data["username"] == TEST_USER_REGISTER.username
        assert "id" in data
        assert "hashed_password" not in data
    
    def test_register_user_existing_email(self, client):
        client.post("/register", json=TEST_USER_REGISTER.model_dump())

        duplicate_user = TEST_USER_REGISTER.model_dump()
        duplicate_user["username"] = "diffUsername"

        response = client.post("/register", json=duplicate_user)

        assert response.status_code == 400
        assert "already registered" in response.json()["detail"]
    
    def test_login_success(self, client):
        client.post("/register", json=TEST_USER_REGISTER.model_dump())

        response = client.post("/login", json={
            "identifier": TEST_USER_LOGIN["identifier"],
            "password": TEST_USER_LOGIN["password"]
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self,client):
        client.post("/register", json=TEST_USER_REGISTER.model_dump())

        response = client.post("/login", json={
            "identifier": TEST_USER_LOGIN["identifier"],
            "password": "NOTOKAY_"
        })

        assert response.status_code == 401
        assert "Incorrect credentials" in response.json()["detail"]
    
    def test_login_nonexistent_user(self, client):
        response = client.post("/login", json={
            "identifier": "notAllowed@test.com",
            "password": "bruhMoment"
        })

        assert response.status_code == 401
        assert "Incorrect credentials" in response.json()["detail"]
    
    def test_get_current_user_profile(self, client):
        client.post("/register", json=TEST_USER_REGISTER.model_dump())
        login_response = client.post("/login", json=TEST_USER_LOGIN)
        token = login_response.json()["access_token"]

        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == TEST_USER_REGISTER.email

    def test_get_current_user_profile_unauthenticated(self, client):
        response = client.get("/users/me")

        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    def test_get_current_user_invalid_token(self, client):
        response = client.get(
            "/users/me",
            headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]