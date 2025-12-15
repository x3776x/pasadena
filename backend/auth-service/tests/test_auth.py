import pytest
from unittest.mock import patch, MagicMock
from tests.test_data import create_test_user_register, create_test_user_login, TEST_USER_REGISTER, TEST_USER_LOGIN

class TestAuthEndpoints:
    @patch('app.services.auth_service.httpx.Client')
    def test_register_user(self, mock_httpx, client):
        test_user = create_test_user_register()
        
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_httpx.return_value.__enter__.return_value.post.return_value = mock_response

        print("\nTest payload:", test_user.model_dump())
        response = client.post("/register", json=test_user.model_dump())

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user.email
        assert data["username"] == test_user.username
        assert "id" in data
        assert "hashed_password" not in data
    
    @patch('app.services.auth_service.httpx.Client')
    def test_register_user_existing_email(self, mock_httpx, client):
        test_user = create_test_user_register()
        
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_httpx.return_value.__enter__.return_value.post.return_value = mock_response

        client.post("/register", json=test_user.model_dump())

        duplicate_user = test_user.model_dump()
        duplicate_user["username"] = "diffUsername"

        response = client.post("/register", json=duplicate_user)

        assert response.status_code == 422
        assert "already registered" in response.json()["detail"]

    @patch('app.services.auth_service.httpx.Client')
    def test_register_user_invalid_email(self, mock_httpx, client):
        test_user = create_test_user_register()
        test_user.email = 'simpleexample.com'

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_httpx.return_value.__enter__.return_value.post.return_value = mock_response

        response = client.post("/register", json=test_user.model_dump())

        assert response.status_code == 422
        error_detail = response.json()["detail"][0]
        assert "email" in error_detail["loc"]
        assert "valid email" in error_detail["msg"].lower()

    @patch('app.services.auth_service.httpx.Client')
    def test_register_user_invalid_password(self, mock_httpx, client):
        test_user = create_test_user_register()
        test_user.password = 'smpass'

        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_httpx.return_value.__enter__.return_value.post.return_value = mock_response

        response = client.post("/register", json=test_user.model_dump())

        assert response.status_code == 422
        error_detail = response.json()["detail"][0]
        assert "password" in error_detail["loc"]
        assert "at least 8" in error_detail["msg"].lower()

    @patch('app.services.auth_service.httpx.Client')
    def test_server_crash(self, mock_httpx, client):
        mock_httpx.return_value.__enter__.return_value.post.side_effect = Exception("Try again later")

        test_user = create_test_user_register()
        response = client.post("/register", json=test_user.model_dump())

        assert response.status_code == 503
        assert "Service Unavailable, please try again later" in response.json()["detail"]


    @patch('app.services.auth_service.httpx.Client')
    def test_login_success(self, mock_httpx, client):
        test_user = create_test_user_register()
        
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_httpx.return_value.__enter__.return_value.post.return_value = mock_response

        client.post("/register", json=test_user.model_dump())

        response = client.post("/login", json={
            "identifier": test_user.email,
            "password": "testPassword123"
        })

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    @patch('app.services.auth_service.httpx.Client')
    def test_login_wrong_password(self, mock_httpx, client):
        test_user = create_test_user_register()
        
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_httpx.return_value.__enter__.return_value.post.return_value = mock_response

        client.post("/register", json=test_user.model_dump())

        response = client.post("/login", json={
            "identifier": test_user.email,
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