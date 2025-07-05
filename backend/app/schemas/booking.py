from datetime import date, time, datetime
from typing import Optional
from pydantic import BaseModel

class BookingBase(BaseModel):
    date:       date
    start_time: time
    end_time:   time

class BookingCreate(BookingBase):
    user_id: int  # 예약자 PK
    room_id: int  # 예약할 방의 PK

class BookingUpdate(BaseModel):
    user_id:     Optional[int]  = None
    room_id:     Optional[int]  = None
    date:        Optional[date] = None
    start_time:  Optional[time] = None
    end_time:    Optional[time] = None

class BookingRead(BookingBase):
    booking_id:  int
    user_id:     int
    room_id:     int
    created_at:  datetime

    class Config:
        orm_mode = True
