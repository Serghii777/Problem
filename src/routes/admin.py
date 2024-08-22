from typing import Optional
from fastapi import APIRouter, Form, HTTPException, Depends, FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.repository import admin as repository_admin
from src.schemas.admin import  ParkingRateCreate, ParkingRateUpdate, ParkingReportRequest, UserRoleUpdate, UserStatusUpdate
from src.schemas.user import UserReadSchema
from src.models.models import User, Role
from src.services.role import RoleAccess
from src.services.auth import auth_service
from src.database.db import get_db
from src.repository import users as repository_users

router = APIRouter(prefix="/admin", tags=["admin"])
role_admin = RoleAccess([Role.admin])
role_admin_moderator = RoleAccess([Role.admin, Role.moderator])


@router.put("/users/block", dependencies=[Depends(role_admin)])
async def change_user_status_by_email(
    body: UserStatusUpdate = Depends(),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    user = await repository_users.get_user_by_email(body.email, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    await repository_admin.change_user_status(user, body.is_active, db)
    return {"message": f"User status changed to {'active' if body.is_active else 'inactive'}."}


@router.put("/unblock", dependencies=[Depends(role_admin)])
async def unblock_user_by_email(
    body: UserStatusUpdate = Depends(),
    current_user: User = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await repository_users.get_user_by_email(body.email, db)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    await repository_admin.change_user_status(user, body.is_active, db)
    return {"message": f"User status changed to {'active' if body.is_active else 'inactive'}."}


@router.put("/{user_id}/change_role", dependencies=[Depends(role_admin)])
async def update_user_role(
    body: UserRoleUpdate = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await repository_users.get_user_by_id(body.user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    await repository_admin.update_user_role(user, body.role, db)
    return {"message": f"User role updated to {body.role}"}


@router.post("/parking-rates", response_model=ParkingRateCreate, dependencies=[Depends(role_admin)])
async def set_parking_rate(
    rate_data: ParkingRateCreate,
    db: AsyncSession = Depends(get_db)
):
    rate = await repository_admin.set_parking_rate(
        rate_per_hour=rate_data.rate_per_hour,
        max_daily_rate=rate_data.max_daily_rate,
        currency=rate_data.currency,
        db=db
    )
    return rate


@router.get("/parking-info/available-spaces", response_model=ParkingRateUpdate)
async def get_available_spaces(
    db: AsyncSession = Depends(get_db)
):
    parking_info = await repository_admin.get_latest_parking_info(db)
    if not parking_info:
        raise HTTPException(status_code=404, detail="Інформація про паркінг не знайдена.")
    
    return parking_info


@router.post("/generate-report", dependencies=[Depends(role_admin)])
async def generate_parking_report(
    body: ParkingReportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user)
):
    filename = await repository_admin.generate_parking_report(body.vehicle_id, db)
    
    if not filename:
        raise HTTPException(status_code=404, detail="Паркувальних записів не знайдено для цього авто.")
    return FileResponse(filename, media_type='text/csv', filename=filename)


@router.put("/parking-info", response_model=ParkingRateUpdate, dependencies=[Depends(role_admin)])
async def update_parking_info(
    lot_data: ParkingRateUpdate,  
    db: AsyncSession = Depends(get_db)
):
    parking_info = await repository_admin.update_parking_info(
        total_spaces=lot_data.total_spaces,
        available_spaces=lot_data.available_spaces,
        rate_per_hour=lot_data.rate_per_hour,  
        max_daily_rate=lot_data.max_daily_rate,
        currency=lot_data.currency,
        db=db
    )
    return parking_info