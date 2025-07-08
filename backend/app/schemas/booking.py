# schemas/booking.py
from datetime import date, time, datetime
from typing import Optional, List
from pydantic import BaseModel
from app.schemas.user import UserRead
from app.schemas.room import RoomRead



class TimeSlot(BaseModel):
    start: datetime
    end: datetime
    available: bool

class BookingBase(BaseModel):
    date:       date
    start_time: time
    end_time:   time

class BookingCreate(BookingBase):
    room_id: int  # 예약할 방의 PK

class BookingUpdate(BaseModel):
    user_id:     Optional[int]  = None
    room_id:     Optional[int]  = None
    date:        Optional[date] = None
    start_time:  Optional[time] = None
    end_time:    Optional[time] = None

class BookingRead(BookingBase):
    booking_id:  int
    user:        UserRead        # ← user 객체를 중첩
    room:        RoomRead
    created_at:  datetime

    # class Config:
    #     orm_mode = True
    # Pydantic V2: orm_mode → from_attributes
    model_config = {
        "from_attributes": True
    }