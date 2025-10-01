import random
import secrets
from datetime import datetime, timedelta
from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import user_repository
from app import schemas

recovery_codes = {} #just to test

class PasswordRecoveryService:
    def __init__(self, db: Session):
        self.db = db

    def generate_recovery_code(self) -> str:
            return str(random.randint(1000, 9999))
        
    def initiate_password_recovery(self, request: schemas.PasswordRecoveryRequest
        ) -> schemas.PasswordRecoveryResponse:
        user = user_repository.get_user_by_email(self.db, request.email)
        if not user or user.username != request.username:
             raise ValueError("No user found with the provided email and username")
        
        recovery_code = self.generate_recovery_code()
        expiration = datetime.now() + timedelta(minutes=2)

        recovery_codes[request.email] = {
             'code': recovery_code,
             'expires_at': expiration,
             'verified': False
        }

        print(f"RECOVERY CODE for {request.email}: {recovery_code}")

        return schemas.PasswordRecoveryResponse(
             message="Recovery code sent to your email",
             expires_in=2
        )
    def verify_recovery_code(self, request: schemas.PasswordRecoveryVerify) -> bool:
         if request.email not in recovery_codes:
              raise ValueError("No code was generated")
         
         recovery_data = recovery_codes[request.email]

         if datetime.now() > recovery_data['expires_at']:
              del recovery_codes[request.email]
              raise ValueError("Recovery code has expired")
         
         if recovery_data['code'] != request.code:
              raise ValueError("Invalid recovery code")
         
         recovery_codes[request.email]['verified'] = True
         return True
    
    def reset_password(self, request: schemas.PasswordReset) -> bool:
         if request.new_password != request.confirm_password:
              raise ValueError("Passwords do not match")
         
         if len(request.new_password) < 8:
              raise ValueError("Password must be at least 8 characters long")
         
         if request.email not in recovery_codes:
              raise ValueError("No recovery process initiated for this email")
         
         recovery_data = recovery_codes[request.email]

         if not recovery_data['verified']:
            raise ValueError("Recovery code not verified")
         
         if datetime.now() > recovery_data['expires_at']:
              del recovery_codes[request.email]
              raise ValueError("Recovery process has expired")
         
         user = user_repository.get_user_by_email(self.db, request.email)
         if not user:
              raise ValueError("User not found")
         
         user_repository.update_user_password(self.db, user.id, request.new_password)

         del recovery_codes[request.email]

         return True
    
def get_password_recovery_service(db: Session = Depends(get_db)):
         return PasswordRecoveryService(db)
        