from app.database import user_profiles, follows
from app.models import UserProfile, Follow
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
    
    @staticmethod
    def follow_user(follower_id: int, followed_id: int):
        follow_doc = {
            "follower_id": follower_id,
            "followed_id": followed_id,
            "created_at": datetime.now()
        }
        result = follows.insert_one(follow_doc)
        return str(result.inserted_id)

    @staticmethod
    def unfollow_user(follower_id: int, followed_id: int):
        result = follows.delete_one({
            "follower_id": follower_id,
            "followed_id": followed_id
        })
        return result.deleted_count > 0
    
    @staticmethod
    def get_following(user_id: int):
        """Usuarios que sigue este user_id"""
        cursor = follows.find({"follower_id": user_id})
        return [Follow(**{**doc, "created_at": doc["created_at"]}) for doc in cursor]

    @staticmethod
    def get_followers(user_id: int):
        """Usuarios que siguen a este user_id"""
        cursor = follows.find({"followed_id": user_id})
        return [Follow(**{**doc, "created_at": doc["created_at"]}) for doc in cursor]

    @staticmethod
    def is_following(follower_id: int, followed_id: int) -> bool:
        """Verifica si follower_id ya sigue a followed_id"""
        return follows.find_one({
            "follower_id": follower_id,
            "followed_id": followed_id
        }) is not None