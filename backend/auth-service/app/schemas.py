import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


# Base schema for shared attributes
class UserBase(BaseModel):
    email: EmailStr = Field(max_length=50)
    full_name: str = Field(min_length=4, max_length=50)
    username: str = Field(min_length=3, max_length=50)
    is_active: bool = True
    role_id: int = 2

class UserLogin(BaseModel):
    identifier: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8, max_length=30)

# Schema for creating a user (registration). Includes password.
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=30)

    @field_validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username can only contain letters, numbers and underscores')
        return v
    
    @field_validator('password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v
    
    @field_validator('email')
    def validate_email_domain(cls, v):
        disposable_domains = ['tempmail.com', 'throwaway.com']
        domain = v.split('@')[1]
        if domain in disposable_domains:
            raise ValueError('Disposable email addresses are not allowed')
        return v
    
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
    email: EmailStr = Field(min_length=8, max_length=50)
    username: str = Field(min_length=4, max_length=50)

class PasswordRecoveryVerify(BaseModel):
    email: EmailStr = Field(min_length=8, max_length=50)
    code: str = Field(min_length=4, max_length=4, description="4-digit code")

class PasswordReset(BaseModel):
    email: EmailStr = Field(max_length=50)
    code: str = Field(min_length=4, max_length=4)
    new_password: str = Field(min_length=8, max_length=30)
    confirm_password: str = Field(min_length=8, max_length=30)

class PasswordRecoveryResponse(BaseModel):
    message: str
    expires_in: int

#update user fields
class UserUpdate(BaseModel):
    is_active: Optional[bool] = None
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=50)
    username: Optional[str] = Field(default=None, min_length=4, max_length=50)
    role_id: Optional[int] = Field(min_length=1)

class FullUserResponse(User):
    profile_picture: str | None