# backend/app/models/room.py
from sqlalchemy import Column, Integer, Boolean, String
from sqlalchemy.orm import relationship
from app.database import Base

class Room(Base):
    __tablename__ = "rooms"

    room_id   = Column(Integer, primary_key=True, index=True, autoincrement=True)
    room_name = Column(Integer, nullable=False, unique=True)
    state     = Column(Boolean, default=True, nullable=False)
    equipment = Column(String(255), nullable=True)

    bookings = relationship("Booking", back_populates="room", cascade="all, delete-orphan")
