import csv
from datetime import datetime
from typing import Optional
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.models import ParkingLot, ParkingRate, ParkingRecord, User, Role

async def change_user_status(user: User, is_active: bool, db: AsyncSession):
    user.is_active = is_active
    await db.commit()
    await db.refresh(user)

async def update_user_role(user: User, role: Role, db: AsyncSession):
    user.role = role
    await db.commit()
    await db.refresh(user)

async def set_parking_rate(rate_per_hour: int, max_daily_rate: Optional[int], currency: str, db: AsyncSession):
    new_rate = ParkingRate(
        rate_per_hour=rate_per_hour,
        max_daily_rate=max_daily_rate,
        currency=currency
    )
    db.add(new_rate)
    await db.commit()
    await db.refresh(new_rate)
    return new_rate


async def get_latest_parking_info(db: AsyncSession):
    result = await db.execute(select(ParkingRate).order_by(ParkingRate.created_at.desc()))
    parking_rate = result.scalar_one_or_none()
    
    if parking_rate:
        parking_rate.occupied_spaces = parking_rate.total_spaces - parking_rate.available_spaces
    return parking_rate


async def generate_parking_report(vehicle_id: uuid.UUID, db: AsyncSession):
    result = await db.execute(
        select(ParkingRecord)
        .where(ParkingRecord.vehicle_id == vehicle_id)
        .order_by(ParkingRecord.entry_time)
    )
    
    parking_records = result.scalars().all()
    
    if not parking_records:
        return None
    filename = f"parking_report_{vehicle_id}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    fields = ['Час в’їзду', 'Час виїзду', 'Тривалість (хв)', 'Вартість (грн)']
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        for record in parking_records:
            csvwriter.writerow([record.entry_time, record.exit_time, record.duration, record.cost])
    
    return filename