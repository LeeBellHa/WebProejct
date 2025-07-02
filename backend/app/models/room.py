from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.database import Base

class Room(Base):
    __tablename__ = "room"

    room_id     = Column(Integer, primary_key=True, index=True, autoincrement=True)
    room_number = Column(Integer, nullable=False, unique=True, index=True)
    is_empty    = Column(Boolean, nullable=False, default=True)
    remark      = Column(String(255), nullable=True)

    # 관계 설정 (예약 및 장비)
    reservations = relationship(
        "Reservation",
        back_populates="room",
        cascade="all, delete-orphan",
    )
    equipment = relationship(
        "Equipment",
        back_populates="room",
        cascade="all, delete-orphan",
    )
