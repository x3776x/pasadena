from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum
from datetime import datetime

class AllowedProfilePictures(str, Enum):
    AVATAR1 = "avatar1.png"
    AVATAR2 = "avatar2.png"
    AVATAR3 = "avatar3.png"
    AVATAR4 = "avatar4.png"
    AVATAR5 = "avatar5.png"
    AVATAR6 = "avatar6.png"
    AVATAR7 = "avatar7.png"
    AVATAR8 = "avatar8.png"
    AVATAR9 = "avatar9.png"
    AVATAR10 = "avatar10.png"

class UserProfileBase(BaseModel):
    profile_picture: AllowedProfilePictures = AllowedProfilePictures.AVATAR1

class UserProfileCreate(UserProfileBase):
    user_id: int

class UserProfileUpdate(BaseModel):
    profile_picture: Optional[AllowedProfilePictures] = None

class UserProfileResponse(UserProfileBase):
    user_id: int 
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# === FOLLOW SCHEMAS ===

class FollowBase(BaseModel):
    follower_id: int = Field(..., description="User who follows")
    followed_id: int = Field(..., description="User being followed")

class FollowCreate(FollowBase):
    """Schema para crear un follow (seguir a un usuario)."""
    pass

class FollowResponse(FollowBase):
    created_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "follower_id": 10,
                "followed_id": 20,
                "created_at": "2023-01-01T12:00:00"
            }
        }
