from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer
from jose import jwt, JWTError
import os

security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

def verify_jwt(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id = payload.get("sub")
        role_id = payload.get("role_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing 'sub'"
            )

        if role_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing 'role_id'"
            )
        return {"user_id": int(user_id), "role_id": int(role_id)}

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )


def admin_required(current_user = Depends(security)):
    user = verify_jwt(current_user.credentials)

    if user["role_id"] != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access only"
        )
    return user