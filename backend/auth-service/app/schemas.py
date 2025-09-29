from enum import Enum
from pydantic import BaseModel, EmailStr, Field

# Validation for valid profile pictures
class AllowedProfilePics(str, Enum):
    avatar1 = "avatar1.png"
    avatar2 = "avatar2.png"
    avatar3 = "avatar3.png"
    avatar4 = "avatar4.png"
    avatar5 = "avatar5.png"
    avatar6 = "avatar6.png"
    avatar7 = "avatar7.png"
    avatar8 = "avatar8.png"
    avatar9 = "avatar9.png"
    avatar10 = "avatar10.png"

# Base schema for shared attributes
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    username: str
    is_active: bool = True
    role_id: int = 2
    profile_picture: AllowedProfilePics = AllowedProfilePics.avatar1 #Default profile pic

class UserLogin(BaseModel):
    identifier: str
    password: str = Field(format="password")

# Schema for creating a user (registration). Includes password.
class UserCreate(UserBase):
    password: str = Field(format="password")

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