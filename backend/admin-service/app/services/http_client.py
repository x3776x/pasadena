import httpx, os

class HTTPClient:
    def __init__(self):
        self.base_url = os.getenv("AUTH_SERVICE_URL")

    async def get(self, path: str, params=None, headers=None):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{self.base_url}{path}", params=params, headers=headers)
            return response
        
    async def patch(self, path: str, json=None, headers=None):
        async with httpx.AsyncClient() as client:
            response = await client.patch(f"{self.base_url}{path}", json=json, headers=headers)
            return response