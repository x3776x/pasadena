from datetime import timedelta
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app import schemas, security
from app.database import get_db
from app.repositories import user_repository
import httpx
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
USER_SERVICE_URL = os.getenv("USER_SERVICE_URL", "http://user_service:8003/profiles")

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(self, user_data: schemas.UserCreate) -> schemas.User:
        try:
            user_data.email = user_data.email.lower().strip()
            user_data.username = user_data.username.strip()

            if user_repository.get_user_by_email(self.db, user_data.email):
                raise ValueError("Email already registered")
            
            if user_repository.get_user_by_username(self.db, user_data.username):
                raise ValueError("Username already taken")
            
            if not security.validate_password_complexity(user_data.password):
                raise ValueError('Password must contain uppercase, lowercase and numbers')
            
            db_user = user_repository.create_user(self.db, user_data)

            payload = {
                "user_id": db_user.id,
                "profile_picture": "avatar1.png"
            }

            try: 
                with httpx.Client() as client:
                    response = client.post(USER_SERVICE_URL, json=payload, timeout=5)
                    response.raise_for_status()
            except httpx.RequestError as e:
                user_repository.delete_user(self.db, db_user.id)
                raise ConnectionError("Failed to communicate with user service") from e
            
            return db_user
        except (ValueError, ConnectionError) as e:
            raise e
        except Exception as e:
            raise Exception("Registration service unavailable - please try again later")
    
    def login_user(self, identifier: str, password: str) -> schemas.Token:
        try:
            user = user_repository.get_user_by_email(self.db, identifier)
            if not user:
                user = user_repository.get_user_by_username(self.db, identifier)

            if not user or not security.verify_password(password, user.hashed_password):
                raise ValueError("Incorrect credentials")

            access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = security.create_access_token(
                data={"sub": str(user.id), "role_id": user.role_id},
                expires_delta=access_token_expires
            )

            return schemas.Token(access_token=access_token, token_type="bearer")

        except ValueError as e:
            raise e
        except Exception as e:
            print(f"[LOGIN ERROR] {e}")   # <== Add this temporarily
            raise Exception("Login service unavailable - please try again later")

    
    def get_user_by_id(self, user_id: int) -> schemas.User:
        user = user_repository.get_user_by_id(self.db, user_id)
        if not user:
            raise ValueError("User not found")
        return user
    
    def get_all_users(self, limit: int = 100, offset: int = 0):
        users = user_repository.get_all_users(self.db, limit=limit, offset=offset)
        if not users:
            raise ValueError("No users registered/active")
        return users
    
    def update_user(self, user_id: int, user_data: schemas.UserUpdate):
        updates = user_data.model_dump(exclude_none=True)

        updated = user_repository.update_user(self.db, user_id, updates)
        if not updated:
            raise ValueError("User not found")
        return updated

def get_auth_service(db: Session = Depends(get_db)):
    return AuthService(db)