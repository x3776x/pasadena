from fastapi import FastAPI, Depends, HTTPException, status
from app.services.user_service import UserService, get_user_service
from app.core.security import get_current_user
from app import schemas

app = FastAPI(
    title="User service",
    description="for profile pics and future features",
    version="1.0.0"
)

@app.get("/profiles/{user_id}", response_model=schemas.UserProfileResponse)
def get_user_profile(
    user_id: int,
    current_user = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    if current_user["user_id"] != user_id and current_user["role_id"] != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden",
        )
    try:
        profile = user_service.get_profile(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database error: {str(e)}"
        )


@app.post("/profiles", response_model=dict)
def create_user_profile(
    profile_data: schemas.UserProfileCreate,
    user_service: UserService = Depends(get_user_service)
):
    try: 
        profile_id = user_service.create_profile(profile_data)
        return {"message": "Profile created successfully", "profile_id": profile_id}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@app.put("/profiles/{user_id}", response_model=dict)
def update_user_profile(
    user_id: int,
    update_data: schemas.UserProfileUpdate,
    current_user = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    if current_user["user_id"] != user_id and current_user["role_id"] != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden",
        )
    
    try:
        success = user_service.update_profile(user_id, update_data)
        if success:
            return {"message": "Profile updated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e)
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
@app.put("/profiles/{user_id}/picture", response_model=dict)
def update_profile_picture(
    user_id: int,
    picture_data: schemas.UserProfileUpdate,
    current_user = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    if current_user["user_id"] != user_id and current_user["role_id"] != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden",
        )
    
    try: 
        success = user_service.update_profile_picture(user_id, picture_data.profile_picture)
        if success:
            return {"message": "Profile picture updated successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    

# === FOLLOW ENDPOINTS ===

@app.post("/users/{followed_id}/follow", response_model=dict)
def follow_user(
    followed_id: int,
    current_user = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        follow_id = user_service.follow_user(current_user["user_id"], followed_id)
        return {"message": "Followed successfully", "follow_id": follow_id}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database error: {str(e)}"
        )


@app.delete("/users/{followed_id}/unfollow", response_model=dict)
def unfollow_user(
    followed_id: int,
    current_user = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    try:
        success = user_service.unfollow_user(current_user["user_id"], followed_id)
        if success:
            return {"message": "Unfollowed successfully"}
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Follow relationship not found"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database error: {str(e)}"
        )


@app.get("/users/{user_id}/following", response_model=list[schemas.FollowResponse])
def get_following(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    try:
        return user_service.get_following(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database error: {str(e)}"
        )


@app.get("/users/{user_id}/followers", response_model=list[schemas.FollowResponse])
def get_followers(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    try:
        return user_service.get_followers(user_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database error: {str(e)}"
        )


    
@app.get("/health")
def health_check():
    return {"status": "OK"}