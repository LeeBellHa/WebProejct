from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.booking import Booking
from app.schemas.booking import Booking as BookingSchema, BookingCreate
from app.routers.auth import get_current_admin

router = APIRouter(
    prefix="/admin/bookings",
    tags=["admin_bookings"],
    dependencies=[Depends(get_current_admin)]
)

@router.get("/", response_model=list[BookingSchema])
def list_blocks(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    return (
        db.query(Booking)
          .filter(Booking.user_id == admin.user_id)
          .offset(skip)
          .limit(limit)
          .all()
    )

@router.post("/", response_model=BookingSchema, status_code=status.HTTP_201_CREATED)
def create_block(block_in: BookingCreate, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    if block_in.end_date < block_in.start_date or (block_in.end_date == block_in.start_date and block_in.end_time <= block_in.start_time):
        raise HTTPException(400, "끝날짜/끝시간이 시작보다 빨라요.")
    conflict = db.query(Booking).filter(
        Booking.room_id    == block_in.room_id,
        Booking.start_date <= block_in.end_date,
        Booking.end_date   >= block_in.start_date,
        Booking.start_time <  block_in.end_time,
        Booking.end_time   >  block_in.start_time
    ).first()
    if conflict:
        raise HTTPException(409, "겹치는 블록(예약)이 존재합니다.")
    new_block = Booking(
        user_id    = admin.user_id,
        room_id    = block_in.room_id,
        start_date = block_in.start_date,
        end_date   = block_in.end_date,
        start_time = block_in.start_time,
        end_time   = block_in.end_time
    )
    db.add(new_block)
    db.commit()
    db.refresh(new_block)
    return new_block

@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_block(booking_id: int, db: Session = Depends(get_db), admin=Depends(get_current_admin)):
    block = db.query(Booking).filter(Booking.booking_id == booking_id, Booking.user_id == admin.user_id).first()
    if not block:
        raise HTTPException(404, "블록(예약)을 찾을 수 없습니다.")
    db.delete(block)
    db.commit()
