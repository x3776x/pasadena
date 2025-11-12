from app.schemas import UserProfileCreate, UserProfileUpdate, AllowedProfilePictures

def create_test_profile():
    return UserProfileCreate(user_id=1, profile_picture=AllowedProfilePictures.AVATAR2)

def create_update_profile():
    return UserProfileUpdate(profile_picture=AllowedProfilePictures.AVATAR5)