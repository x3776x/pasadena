from fastapi import FastAPI, Depends, HTTPException, status
from app.dependencies.dependencies import get_admin_service
from app.services.admin_service import AdminService
from app.schemas.user import User
from app.core.security import admin_required

app = FastAPI(title="Admin service")

@app.get("/admin/users", response_model=list[User])
async def list_users(
    limit: int = 50,
    offset: int = 0,
    current_user = Depends(admin_required),
    admin_service: AdminService = Depends(get_admin_service)
):
    try:
        return await admin_service.list_users(limit, offset)
    except HTTPException as e:
        raise e


@app.get("/admin/users/{user_id}", response_model=User)
async def get_user(
    user_id: int,
    current_user = Depends(admin_required),
    admin_service: AdminService = Depends(get_admin_service)
):
    try:
        return await admin_service.get_user(user_id)
    except HTTPException as e:
        raise e


@app.patch("/admin/users/{user_id}/ban", response_model=User)
async def ban_user(
    user_id: int,
    current_user = Depends(admin_required),
    admin_service: AdminService = Depends(get_admin_service)
):
    try:
        return await admin_service.ban_user(user_id)
    except HTTPException as e:
        raise e


@app.patch("/admin/users/{user_id}/unban", response_model=User)
async def unban_user(
    user_id: int,
    current_user = Depends(admin_required),
    admin_service: AdminService = Depends(get_admin_service)
):
    try:
        return await admin_service.unban_user(user_id)
    except HTTPException as e:
        raise e


@app.get("/health")
def health_check():
    return {"status": "ok"}