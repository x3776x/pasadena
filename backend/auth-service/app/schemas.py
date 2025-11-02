from enum import Enum
from pydantic import BaseModel, EmailStr, Field


# Base schema for shared attributes
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    username: str
    is_active: bool = True
    role_id: int = 2

class UserLogin(BaseModel):
    identifier: str
    password: str = Field(min_length=8)

# Schema for creating a user (registration). Includes password.
class UserCreate(UserBase):
    password: str = Field(min_length=8)

# Schema for what we return to the client.
class User(UserBase):
    id: int

    class Config:
        from_attributes = True  # Allows ORM mode (translates ORM object -> Pydantic model)

# Schema for the login request
class Token(BaseModel):
    access_token: str
    token_type: str

# Schema for the data embedded inside the JWT token
class TokenData(BaseModel):
    user_id: int | None = None

# Schema for user to modify its password
class PasswordRecoveryRequest(BaseModel):
    email: EmailStr
    username: str

class PasswordRecoveryVerify(BaseModel):
    email: EmailStr
    code: str = Field(min_length=4, max_length=4, description="4-digit code")

class PasswordReset(BaseModel):
    email: EmailStr
    code: str = Field(min_length=4, max_length=4)
    new_password: str = Field(min_length=8)
    confirm_password: str

class PasswordRecoveryResponse(BaseModel):
    message: str
    expires_in: int