from app.repositories.user_repository import UserRepository
from app import schemas

class UserService:
    def __init__(self):
        self.repository = UserRepository()

    def create_profile(self, profile_data: schemas.UserProfileCreate):
        existing_profile = self.repository.get_user_profile(profile_data.user_id)
        if existing_profile:
            raise ValueError("User profile already exists")

        profile_dict = profile_data.model_dump()
        return self.repository.create_user_profile(profile_dict)

    def get_profile(self, user_id: int):
        profile = self.repository.get_user_profile(user_id)
        if not profile:
            raise ValueError("User profile not found")
        return profile
    
    def update_profile(self, user_id: int, update_data: schemas.UserProfileUpdate):
        existing_profile = self.repository.get_user_profile(user_id)
        if not existing_profile:
            raise ValueError("User profile not found")
        
        update_dict = {k: v for k, v in update_data.model_dump(). items() if v is not None}
        return self.repository.update_user_profile(user_id, update_dict)
    
    def update_profile_picture(self, user_id: int , profile_picture: str):
        return self.repository.update_user_profile(user_id, {"profile_picture": profile_picture})
    
def get_user_service():
    return UserService()