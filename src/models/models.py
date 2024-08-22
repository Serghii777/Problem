import enum
import uuid
from datetime import datetime

from sqlalchemy import String, Integer, ForeignKey, DateTime, func, Column, Boolean, Enum, CheckConstraint, UUID, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import DeclarativeBase, relationship, Mapped, mapped_column, declarative_base

Base = declarative_base()

# class Base(DeclarativeBase):
#     pass


class Role(enum.Enum):
    admin: str = "admin"
    moderator: str = "moderator"
    user: str = "user"


class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    first_name = Column(String(50))
    last_name = Column(String(50))
    email = Column(String(length=320), unique=True, index=True, nullable=False)
    password = Column(String(length=1024), nullable=False)
    role = Column(Enum(Role), default=Role.user, nullable=False)
    avatar = Column(String(100))
    refresh_token = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    confirmed = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=False)

    vehicles = relationship("Vehicle", back_populates="user")  

    @hybrid_property
    def fullname(self):
        return self.first_name + " " + self.last_name


class BlackList(Base):
    __tablename__ = 'black_list'

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, index=True)
    email = Column(String(320), unique=True, index=True, nullable=False)


class Vehicle(Base):
    __tablename__ = "vehicles"
    
    id = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    license_plate = mapped_column(String(20), unique=True, index=True, nullable=False)
    brand_model = mapped_column(String(50), index=True, unique=False, nullable=True)
    user_id = mapped_column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    is_blacklisted = mapped_column(Boolean, default=False)
    
    user = relationship("User", back_populates="vehicles")
    parking_records = relationship("ParkingRecord", back_populates="vehicle")


class ParkingRecord(Base):
    __tablename__ = "parking_records"
    
    id = mapped_column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    vehicle_id = mapped_column(UUID(as_uuid=True), ForeignKey('vehicles.id'), nullable=False)
    entry_time = mapped_column(DateTime, default=func.now(), nullable=False)
    exit_time = mapped_column(DateTime, nullable=True)
    duration = mapped_column(Integer, nullable=True)
    cost = mapped_column(Integer, nullable=True)
    
    vehicle = relationship("Vehicle", back_populates="parking_records")


class ParkingRate(Base):
    __tablename__ = "parking_rates"
    
    id = mapped_column(Integer, primary_key=True, index=True)
    total_spaces = mapped_column(Integer, nullable=False, default=100)  # Загальна кількість місць
    available_spaces = mapped_column(Integer, nullable=False, default=100)  # Доступні місця
    rate_per_hour = mapped_column(Integer, nullable=False)  # Тариф за годину
    max_daily_rate = mapped_column(Integer, nullable=True)  # Максимальний денний тариф
    currency = mapped_column(String(10), default="USD", nullable=False)  # Валюта
    created_at = mapped_column(DateTime, default=func.now())  # Дата створення
    updated_at = mapped_column(DateTime, default=func.now(), onupdate=func.now())  # Дата оновлення


class ParkingLot(Base):
    __tablename__ = "parking_lot"
    
    id = mapped_column(Integer, primary_key=True, index=True)
    total_spaces = mapped_column(Integer, nullable=False, default=100)
    available_spaces = mapped_column(Integer, nullable=False, default=100)
    created_at = mapped_column(DateTime, default=func.now())
    updated_at = mapped_column(DateTime, default=func.now(), onupdate=func.now())