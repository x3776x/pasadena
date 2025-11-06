from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum

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
    profile_pciture: AllowedProfilePictures = AllowedProfilePictures.AVATAR1

class UserProfileCreate(UserProfileBase):
    user_id: int

class UserProfileUpdate(BaseModel):
    profile_pciture: Optional[AllowedProfilePictures] = None

class UserProfileResponse(UserProfileBase):
    user_id: int 
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True