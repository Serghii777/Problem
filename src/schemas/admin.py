from typing import Optional
import uuid
from pydantic import BaseModel, EmailStr

from src.models.models import Role


class UserStatusUpdate(BaseModel):
    email: EmailStr
    is_active: bool


class ImageRequest(BaseModel):
    image_id: int


class UserRoleUpdate(BaseModel):
    user_id: uuid.UUID
    role: Role


class ParkingRateCreate(BaseModel):
    rate_per_hour: int
    max_daily_rate: int
    currency: str

    class Config:
        orm_mode = True

class ParkingRateUpdate(BaseModel):
    total_spaces: int
    available_spaces: int
    occupied_spaces: Optional[int] = None  

    class Config:
        orm_mode = True


class ParkingReportRequest(BaseModel):
    vehicle_id: uuid.UUID