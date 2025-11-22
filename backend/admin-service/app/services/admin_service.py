from fastapi import HTTPException, status
from app.services.http_client import HTTPClient
from app.schemas.update_user import UserUpdate
from app.schemas.user import User
from typing import List

class AdminService:
    def __init__(self):
        self.client = HTTPClient()

    #User mgmt

    async def list_users(self, limit: int = 50, offset: int = 0) -> List[User]:
        response = await self.client.get("/users", params={"limit": limit, "offset": offset})

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="No users found")

        if response.status_code != 200:
            raise HTTPException(status_code=503, detail="Auth service unavailable")

        return [User(**u) for u in response.json()]
    
    async def get_user(self, user_id: int) -> User:
        response = await self.client.get(f"/users/{user_id}")

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")

        if response.status_code != 200:
            raise HTTPException(status_code=503, detail="Auth service unavailable")

        return User(**response.json())

    async def ban_user(self, user_id: int) -> User:
        update = UserUpdate(is_active=False)

        response = await self.client.patch(
            f"/users/{user_id}",
            json=update.model_dump(exclude_none=True)
        )

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")

        if response.status_code != 200:
            raise HTTPException(status_code=503, detail="Auth service unavailable")

        return User(**response.json())

    async def unban_user(self, user_id: int) -> User:
        update = UserUpdate(is_active=True)

        response = await self.client.patch(
            f"/users/{user_id}",
            json=update.model_dump(exclude_none=True)
        )

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")

        if response.status_code != 200:
            raise HTTPException(status_code=503, detail="Auth service unavailable")

        return User(**response.json())