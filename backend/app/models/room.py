# backend/app/models/room.py
from sqlalchemy import Column, Integer, Boolean, String
from sqlalchemy.orm import relationship
from app.database import Base

class Room(Base):
    __tablename__ = "rooms"

    room_id   = Column(Integer, primary_key=True, index=True, autoincrement=True)
    room_name = Column(String(100), nullable=False, unique=True)   # int → string
    floor     = Column(Integer, nullable=False, default=1)         # 층수 추가
    pos_x     = Column(Integer, nullable=True)                     # 이름표 X 좌표
    pos_y     = Column(Integer, nullable=True)                     # 이름표 Y 좌표
    state     = Column(Boolean, default=True, nullable=False)
    equipment = Column(String(255), nullable=True)

    bookings = relationship("Booking", back_populates="room", cascade="all, delete-orphan")
