from datetime import timedelta
from sqlalchemy.orm import Session
from app import schemas, security
from app.repositories import user_repository

def register_user(db: Session, user: schemas.UserCreate):
    if user_repository.get_user_by_email(db, user.email):
        raise ValueError("Email already registered")
    
    if user_repository.get_user_by_username(db, user.username):
        raise ValueError("Username already taken")
    
    if len(user.password) < 8:
        raise ValueError("Password must be at least 8 characters long")
    
    return user_repository.create_user(db, user)

def login_user(db: Session, form_data: schemas.UserCreate):
    user = user_repository.get_user_by_email(db, form_data.email)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise ValueError("Incorrect email or password")
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}