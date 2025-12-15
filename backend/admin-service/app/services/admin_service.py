from fastapi import HTTPException, status
from app.services.http_client import HTTPClient
from app.schemas.update_user import UserUpdate
from app.schemas.user import User
from typing import List

class AdminService:
    def __init__(self):
        self.client = HTTPClient()

    #User mgmt

    async def list_users(self, token: str, limit: int = 50, offset: int = 0) -> List[User]:
        headers = self.forward_auth_header(token)
        response = await self.client.get("/users", params={"limit": limit, "offset": offset},
                                         headers = headers)

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="No users found")

        if response.status_code != 200:
            raise HTTPException(status_code=503, detail="Auth service unavailable")

        return [User(**u) for u in response.json()]
    
    async def get_user(self, token: str, user_id: int) -> User:
        headers = self.forward_auth_header(token)
        response = await self.client.get(f"/users/{user_id}", headers = headers)

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")

        if response.status_code != 200:
            raise HTTPException(status_code=503, detail="Auth service unavailable")

        return User(**response.json())

    async def ban_user(self, token: str, user_id: int) -> User:
        headers = self.forward_auth_header(token)
        update = UserUpdate(is_active=False)

        response = await self.client.patch(
            f"/users/{user_id}",
            json=update.model_dump(exclude_none=True),
            headers = headers
        )

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")

        if response.status_code != 200:
            raise HTTPException(status_code=503, detail="Auth service unavailable")

        return User(**response.json())

    async def unban_user(self, token: str, user_id: int) -> User:
        headers = self.forward_auth_header(token)
        update = UserUpdate(is_active=True)

        response = await self.client.patch(
            f"/users/{user_id}",
            json=update.model_dump(exclude_none=True),
            headers = headers
        )

        if response.status_code == 404:
            raise HTTPException(status_code=404, detail="User not found")

        if response.status_code != 200:
            raise HTTPException(status_code=503, detail="Auth service unavailable")

        return User(**response.json())
    
    def forward_auth_header(self, token: str):
        return {"Authorization": f"Bearer {token}"}