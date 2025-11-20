from sqlalchemy.orm import Session
from app import models, schemas
from app.security import get_password_hash
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError

def get_user_by_email(db: Session, email: str):
    """Find a user by their email address."""
    return db.query(models.User).filter(models.User.email == email).first()

def get_user_by_username(db: Session, username: str):
    """Find a user by their username"""
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_id(db: Session, user_id: int):
    """Find a user by their ID."""
    try:
        return db.query(models.User).filter(models.User.id == user_id).first()
    except OperationalError as e:
        raise ConnectionError("Database connection error - please try again later")
    except Exception as e:
        raise e

def create_user(db: Session, user: schemas.UserCreate):
    try:
        new_user = models.User(
            email=user.email,
            hashed_password=get_password_hash(user.password),
            full_name=user.full_name,
            username=user.username,
            role_id=user.role_id
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except IntegrityError:
        db.rollback()
        raise ValueError("User with this email or username already registered")
    except OperationalError as e:
        db.rollback()
        raise ConnectionError("Database connection error - please try again later")
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception("Database error - please try again later")
    except Exception as e:
        db.rollback()
        raise e

def update_user_password(db: Session, user_id: int, new_password: str):
    try: 
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user: 
            user.hashed_password = get_password_hash(new_password)
            db.commit()
            db.refresh(user)
        return user
    except OperationalError as e:
        db.rollback()
        raise ConnectionError("Database connection error, please try again later")
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception("Database error, please try again later")
    except Exception as e:
        db.rollback()
        raise e

def delete_user(db: Session, user_id: int):
    try:
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
        else:
            raise ValueError("User not found")
    except OperationalError as e:
        db.rollback()
        raise ConnectionError("Database connection error, please try again later")
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception("Database error, please try again later")
    except Exception as e:
        db.rollback()
        raise e

def get_all_users(db: Session, limit : int = 100, offset: int = 0):
    try:
        safe_limit = min(limit, 1000)
        return (
            db.query(models.User)
            .offset(offset)
            .limit(safe_limit)
            .all()
        )
    except OperationalError as e:
        raise ConnectionError("Database connection error, please try again later")
    except Exception as e:
        raise e
    
def update_user(db: Session, user_id: int, updates: dict):
    try: 
        user = get_user_by_id(db, user_id)
        if not user: 
            return None
        for key, value in updates.items():
            setattr(user, key, value)

        db.commit()
        db.refresh(user)
        return user
    except OperationalError as e:
        db.rollback()
        raise ConnectionError("Database connection error, please try again later")
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise e

