from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, Date, Time, DateTime
from sqlalchemy.orm import relationship
from app.database import Base

class Booking(Base):
    __tablename__ = "bookings"

    booking_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id    = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    room_id    = Column(Integer, ForeignKey("rooms.room_id"), nullable=False)

    # 단일 date → 기간: start_date, end_date
    start_date = Column(Date, nullable=False)
    end_date   = Column(Date, nullable=False)

    start_time = Column(Time, nullable=False)
    end_time   = Column(Time, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="bookings")
    room = relationship("Room", back_populates="bookings")
