# backend/app/crud.py
from sqlalchemy.orm import Session
from .models import Booking
from datetime import datetime

def create_booking(db: Session, booking_data: dict):
    booking = Booking(
        student_id=booking_data["student_id"],
        name=booking_data["name"],
        major=booking_data["major"],
        room=booking_data["room"],
        floor=booking_data["floor"],
        date=booking_data["date"],
        time_slot=booking_data["time_slot"],
        created_at=datetime.utcnow()
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking
