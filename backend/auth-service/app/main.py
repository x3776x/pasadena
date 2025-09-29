from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles

from app import schemas
from app.database import get_db
from app.dependencies.dependencies import get_current_user, oauth2_scheme
from app.services.auth_service import AuthService, get_auth_service

app = FastAPI(title="Auth Service")
# --- Authentication helpers ---

app.mount("/static/avatars", StaticFiles(directory="app/static/avatars"), name="static")

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
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
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
    
@app.get("/users/me", response_model=schemas.User)
def get_current_user_profile(
    current_user: schemas.User = Depends(get_current_user)
):
    return current_user

@app.get("/profile-pictures")
def get_available_profile_pictures():
    return {"available_pictures": [pic.value for pic in schemas.AllowedProfilePics]}