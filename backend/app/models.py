from sqlalchemy import Column, Integer, String, Date, TIMESTAMP
from .database import Base

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(20))
    name = Column(String(50))
    major = Column(String(50))
    room = Column(String(10))
    floor = Column(Integer)
    date = Column(Date)
    time_slot = Column(String(10))
    created_at = Column(TIMESTAMP)
