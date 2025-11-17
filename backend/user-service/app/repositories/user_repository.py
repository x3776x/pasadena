from app.database import user_profiles
from app.models import UserProfile
from bson import ObjectId
from datetime import datetime

class UserRepository:
    @staticmethod
    def get_user_profile(user_id: int):
        profile = user_profiles.find_one({"user_id": user_id})
        if profile: 
            profile["_id"] = str(profile["_id"])
            return UserProfile(**profile)
        return None
    
    @staticmethod
    def create_user_profile(profile_data: dict):
        profile_data["created_at"] = datetime.now()
        profile_data["updated_at"] = datetime.now()

        result = user_profiles.insert_one(profile_data)
        return str(result.inserted_id)
    
    @staticmethod
    def update_user_profile(user_id: int, update_data: dict):
        update_data["updated_at"] = datetime.now()

        result = user_profiles.update_one(
            {"user_id": user_id},
            {"$set": update_data}
        )
        return result.modified_count > 0