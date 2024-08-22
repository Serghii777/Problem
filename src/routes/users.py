import uuid
from fastapi import APIRouter, Depends, status, HTTPException, Request, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
from src.database.db import get_db
from src.models.models import User
from src.repository.users import UserRepository, VehicleRepository, ParkingRecordRepository
from src.services.auth import auth_service
from src.schemas.user import UserDbSchema, RequestEmail
from src.services.email import send_email_reset_password

router = APIRouter(prefix="/users", tags=["users"])
templates = Jinja2Templates(directory="src/services/templates")


@router.get("/me/", response_model=UserDbSchema)
async def read_users_me(current_user: User = Depends(auth_service.get_current_user)):
    return current_user


@router.post("/forgot_password")
async def forgot_password(background_tasks: BackgroundTasks,
                          request: Request,
                          body: RequestEmail = Depends(),
                          db: AsyncSession = Depends(get_db)) -> dict:
    user = await UserRepository(db).get_user_by_email(body.email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user:
        background_tasks.add_task(send_email_reset_password, user.email, user.fullname, str(request.base_url))
    return {"message": "Check your email for confirmation."}


@router.post("/reset_password/{token}")
async def reset_password(token: str,
                         request_: Request,
                         db: AsyncSession = Depends(get_db)) -> dict:
    form_data = await request_.form()
    new_password = form_data["new_password"]
    email = await auth_service.get_email_from_token(token)
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    user = await UserRepository(db).get_user_by_email(email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    new_password = await auth_service.get_password_hash(new_password)
    await UserRepository(db).update_password(user, new_password, db)
    return {"message": "Password reset successfully"}


@router.get("/reset_password/{token}", response_class=HTMLResponse)
async def get_reset_password_page(token: str, request_: Request):
    return templates.TemplateResponse("reset_password.html", {"request": request_, "token": token})


@router.get("/vehicle/{license_plate}/check", response_model=dict)
async def check_vehicle_registration(license_plate: str, db: AsyncSession = Depends(get_db)):
    vehicle_repo = VehicleRepository(db)
    is_registered = await vehicle_repo.is_vehicle_registered(license_plate)
    return {"is_registered": is_registered}


@router.get("/vehicle/{vehicle_id}/parking_duration", response_model=dict)
async def get_parking_duration(vehicle_id: str, db: AsyncSession = Depends(get_db)):
    parking_repo = ParkingRecordRepository(db)
    duration = await parking_repo.get_parking_duration(uuid.UUID(vehicle_id))
    if duration is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Parking record not found or still in progress")
    return {"duration_minutes": duration}
