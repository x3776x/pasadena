# admin-service/tests/test_admin.py
import pytest
from tests.conftest import FakeResponse

@pytest.mark.parametrize(
    "client",
    [{
        ("GET", "/users"): FakeResponse(200, [
            {"id": 1, "email": "test1@example.com", "username": "test1",
             "full_name": "Test User 1", "is_active": True, "role_id": 2},
            {"id": 2, "email": "test2@example.com", "username": "test2",
             "full_name": "Test User 2", "is_active": True, "role_id": 2},
        ])
    }],
    indirect=True
)
def test_list_user_success(client):
    response = client.get("/admin/users",
        headers={"Authorization": "Bearer testtoken"}
    )
    assert response.status_code == 200
    users = response.json()
    assert len(users) == 2
    assert users[0]["email"] == "test1@example.com"


@pytest.mark.parametrize(
    "client",
    [{
        ("GET", "/users/1"): FakeResponse(200, {
            "id": 1, "email": "admin@example.com", "username": "admin",
            "full_name": "Test Admin", "is_active": True, "role_id": 1
        })
    }],
    indirect=True
)
def test_get_user_success(client):
    resp = client.get("/admin/users/1",
        headers={"Authorization": "Bearer testtoken"}
    )
    assert resp.status_code == 200
    assert resp.json()["id"] == 1


@pytest.mark.parametrize(
    "client",
    [{
        ("PATCH", "/users/3"): FakeResponse(200, {
            "id": 3, "email": "x@example.com", "username": "usr",
            "full_name": "Test User X", "is_active": False, "role_id": 2
        })
    }],
    indirect=True
)
def test_ban_user_success(client):
    resp = client.patch("/admin/users/3/ban",
        headers={"Authorization": "Bearer testtoken"}
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


@pytest.mark.parametrize(
    "client",
    [{
        ("PATCH", "/users/3"): FakeResponse(200, {
            "id": 3, "email": "x@example.com", "username": "usr",
            "full_name": "Test User X", "is_active": True, "role_id": 2
        })
    }],
    indirect=True
)
def test_unban_user_success(client):
    resp = client.patch("/admin/users/3/unban",
        headers={"Authorization": "Bearer testtoken"}
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is True
