from pydantic import BaseModel, EmailStr

# Base schema for shared attributes
class UserBase(BaseModel):
    email: EmailStr
    full_name: str | None = None

# Schema for creating a user (registration). Includes password.
class UserCreate(UserBase):
    password: str

# Schema for what we return to the client.
class User(UserBase):
    id: int
    is_active: bool
    role: str

    class Config:
        from_attributes = True  # Allows ORM mode (translates ORM object -> Pydantic model)

# Schema for the login request
class Token(BaseModel):
    access_token: str
    token_type: str

# Schema for the data embedded inside the JWT token
class TokenData(BaseModel):
    user_id: int | None = None