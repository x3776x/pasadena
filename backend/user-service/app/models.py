from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class UserProfile(BaseModel):
    user_id: int = Field(..., description="Reference to authService user ID")
    profile_picture: str = Field(default="avata1.png")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Config:
    json_schema_extra = {
        "example": {
            "user_id": 1,
            "profile_picture": "avata1.png",
            "created_at": "2023-01-01T12:00:00",
            "updated_at": "2023-01-01T12:00:00"
        }
    }