from pydantic import BaseModel, EmailStr

# Base schema for shared attributes
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    username: str
    is_active: bool = True
    role_id: int = 2
    profile_picture: str = "avatar1.png" # Default profile picture ID, Smiley face

# Schema for creating a user (registration). Includes password.
class UserCreate(UserBase):
    password: str

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