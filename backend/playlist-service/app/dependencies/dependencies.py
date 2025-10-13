from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import requests
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "http://auth_service:8001")

def get_current_user(token: str = Depends(oauth2_scheme)):
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(f"{AUTH_SERVICE_URL}/verify-token", headers=headers)
    if resp.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    return resp.json()  # Retorna info del usuario
