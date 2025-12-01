from fastapi import FastAPI, Depends, HTTPException, status

from app import schemas
from app.database import get_db
from app.dependencies.dependencies import get_current_user, oauth2_scheme
from app.services.auth_service import AuthService, get_auth_service
from app.services.password_recovery_service import PasswordRecoveryService, get_password_recovery_service

app = FastAPI(title="Pasadena")
# --- Authentication helpers ---

# --- API Endpoints ---
@app.post("/register", response_model=schemas.User)
def register(
    user: schemas.UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        return auth_service.register_user(user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service Unavailable, please try again later"
        )
    
@app.post("/login", response_model=schemas.Token)
def login(
    form_data: schemas.UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    try: 
        return auth_service.login_user(form_data.identifier, form_data.password)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service Unavailable, please try again later"
        )

@app.post("/password-recovery/initiate", response_model=schemas.PasswordRecoveryResponse)
def initiate_password_recovery(
    request: schemas.PasswordRecoveryRequest,
    recovery_service: PasswordRecoveryService = Depends(get_password_recovery_service)
): 
    try: 
        return recovery_service.initiate_password_recovery(request)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.post("/password-recovery/verify")
def verify_recovery_code(
    request: schemas.PasswordRecoveryVerify,
    recovery_service: PasswordRecoveryService = Depends(get_password_recovery_service)
):
    try:
        recovery_service.verify_recovery_code(request)
        return {"message:" "Code verified successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
@app.post("/password-recovery/reset")
def reset_password(
    request: schemas.PasswordReset,
    recovery_service: PasswordRecoveryService = Depends(get_password_recovery_service)
):
    try:
        recovery_service.reset_password(request)
        return {"message:" "Password reset successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.get("/verify-token")
def verify_token(current_user: schemas.User = Depends(get_current_user)):
    return current_user

@app.get("/health")
def health_check():
    return {"status": "ok"}


#user mgmt
@app.get("/users", response_model=list[schemas.User])
def list_users(
    limit: int = 50,
    offset: int = 0,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        return auth_service.get_all_users(limit=limit, offset=offset)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )
    
@app.get("/users/{user_id}", response_model=schemas.User)
def get_user(
    user_id: int,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        return auth_service.get_user_by_id(user_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@app.patch("/users/{user_id}", response_model=schemas.User)
def update_user(
    user_id: int,
    user_data: schemas.UserUpdate,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        return auth_service.update_user(user_id, user_data)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(e)
        )