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