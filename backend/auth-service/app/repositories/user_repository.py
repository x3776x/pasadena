from sqlalchemy.orm import Session
from app import models, schemas
from app.security import get_password_hash

def get_user_by_email(db: Session, email: str):
    """Find a user by their email address."""
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    """Create a new user in the database. Hashes their password."""
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user) # Refresh to get the ID from the database
    return db_user

def get_user_by_id(db: Session, user_id: int):
    """Find a user by their ID."""
    return db.query(models.User).filter(models.User.id == user_id).first()