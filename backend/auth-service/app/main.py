from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app import schemas, security
from app.repositories import user_repository
from app.database import get_db
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="Auth Service")
# --- Authentication helpers ---
def authenticate_user(db: Session, identifier: str, password: str):
    user = user_repository.get_user_by_email(db, identifier)
    if not user:
        user = user_repository.get_user_by_username(db, identifier)

    if not user or not security.verify_password(password, user.hashed_password):
        return None
    return user

app.mount("/avatars", StaticFiles(directory="app/static/avatars"), name="avatars")

# --- API Endpoints ---
@app.post("/register", response_model=schemas.User)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    if user_repository.get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    if user_repository.get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    if len(user.password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 8 characters long"
        )
    return user_repository.create_user(db=db, user=user)

@app.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )

    return schemas.Token(access_token=access_token, token_type="bearer")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None: 
            raise credentials_exception
        user = user_repository.get_user_by_id(db, int(user_id))
        if not user or not user.is_active:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user

@app.get("/profile-pictures")
def get_available_profile_pictures():
    """Return list of available profile pictures"""
    picture_dir = "app/static/profile_pictures"
    pictures = []
    
    if os.path.exists(picture_dir):
        pictures = [f for f in os.listdir(picture_dir) if f.endswith(('.png', '.jpg', '.jpeg'))]
    
    return {"available_pictures": pictures}