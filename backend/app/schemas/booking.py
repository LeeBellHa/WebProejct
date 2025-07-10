from datetime import date, time, datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.user import UserRead
from app.schemas.room import RoomRead

class TimeSlot(BaseModel):
    start: datetime
    end: datetime
    available: bool

class BookingBase(BaseModel):
    start_date: date
    end_date:   date
    start_time: time
    end_time:   time

class BookingCreate(BookingBase):
    room_id: int

class BookingRead(BookingBase):
    booking_id: int
    user:       UserRead
    room:       RoomRead
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

Booking = BookingRead  # alias for admin router
