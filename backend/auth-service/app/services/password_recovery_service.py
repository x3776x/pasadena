import random
import redis
import json
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import user_repository
from app import schemas, security
from app.helpers import mailSender

redis_client = redis.Redis(
     host='redis',
     port=6379,
     db=0,
     decode_responses=True
)

recovery_codes = {}

class PasswordRecoveryService:
    def __init__(self, db: Session):
        self.db = db
        self.redis_client = redis_client

    def generate_recovery_code(self) -> str:
            return str(random.randint(1000, 9999))
    
    def store_recovery_code(self, email: str, code_data: dict):
         self.redis_client.setex(
              f"recovery:{email}",
              300,
              json.dumps(code_data)
         )
        
    def initiate_password_recovery(self, request: schemas.PasswordRecoveryRequest
        ) -> schemas.PasswordRecoveryResponse:
        user = user_repository.get_user_by_email(self.db, request.email)
        if not user or user.username != request.username:
             raise ValueError("No user found with the provided email and username")
        
        recovery_code = self.generate_recovery_code()
        expiration = 120

        redis_key = f"recovery:{request.email}"
        redis_client.hmset(redis_key, {
             "code": recovery_code,
             "verified": "0"
        })
        redis_client.expire(redis_key, expiration)

        mailSender.send_recovery_email(request.email, recovery_code)

        return schemas.PasswordRecoveryResponse(
             message="Recovery code sent to your email",
             expires_in=2
        )
    
    def verify_recovery_code(self, request: schemas.PasswordRecoveryVerify) -> bool:
         redis_key = f"recovery:{request.email}"
         data = redis_client.hgetall(redis_key)

         if not data:
              raise ValueError("No recovery code found or expired")
         
         if data["code"] != request.code:
              raise ValueError("Invalid recovery code")
         
         redis_client.hset(redis_key, "verified", "1")
         return True
    
    def reset_password(self, request: schemas.PasswordReset) -> bool:
         redis_key = f"recovery:{request.email}"
         data = redis_client.hgetall(redis_key)

         if not data:
              raise ValueError("No recovery process initiated or expired")
         
         if data["verified"] != "1":
              raise ValueError("Recovery code not verified")
         
         if request.new_password != request.confirm_password:
              raise ValueError("Passwords do not match")
         
         if not security.validate_password_complexity(request.new_password):
              raise ValueError("Password must contain uppercase, lowercase and numbers")
         
         user = user_repository.get_user_by_email(self.db, request.email)
         if not user:
              raise ValueError("User not found")
         
         user_repository.update_user_password(self.db, user.id, request.new_password)

         redis_client.delete(redis_key)
         return True
    
def get_password_recovery_service(db: Session = Depends(get_db)):
         return PasswordRecoveryService(db)
        