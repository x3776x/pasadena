from pydantic import BaseModel
from typing import Optional

class UserUpdate(BaseModel):
    is_active: Optional[bool] = None
    role_id: Optional[int] = None