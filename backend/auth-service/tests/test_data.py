from app.schemas import UserCreate

# User data for testing

TEST_USER_REGISTER = UserCreate(
    email="testOne@example.com",
    password="testPassword1",
    full_name="Test User One",
    username="testUserOne",
    profile_picture="avatar1.png"
)

TEST_USER_LOGIN = {
    "identifier": "testOne@example.com",
    "password": "testPassword1"
}