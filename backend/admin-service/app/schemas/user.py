from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: int
    email: str
    username: Optional[str]
    full_name: Optional[str]
    is_active: bool
    role_id: Optional[int]

    class Config:
        from_attriutes = True