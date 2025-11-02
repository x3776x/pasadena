import random, string
from app.schemas import UserCreate, UserLogin

# User data for testing
def generate_random_email():
    random_str = ''.join(random.choices(string.ascii_lowercase + string.digits, k =8))

    return f"test_{random_str}@example.com"

def generate_random_username():
    return f"testUser_{''.join(random.choices(string.ascii_lowercase + string.digits, k=8))}"

def create_test_user_register():
    email = generate_random_email()
    username = generate_random_username()
    
    return UserCreate(
        email=email,
        full_name="Test User",
        username=username,
        password="testPassword123",
    )

def create_test_user_login(email=None, password="testPassword123"):
    return UserLogin(
        identifier=email or generate_random_email(),
        password=password
    )

TEST_USER_REGISTER_ONE = create_test_user_register()
TEST_USER_LOGIN_ONE = create_test_user_login(TEST_USER_REGISTER_ONE.email)

TEST_USER_REGISTER = {
    "email": TEST_USER_REGISTER_ONE.email,
    "password": "testPassword123",
    "full_name": "Test User",
    "username": TEST_USER_REGISTER_ONE.username
}

TEST_USER_LOGIN = {
    "identifier": TEST_USER_REGISTER_ONE.email,
    "password": "testPassword123"
}