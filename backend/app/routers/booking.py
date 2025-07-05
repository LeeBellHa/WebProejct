# backend/app/routers/booking.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.booking import Booking
from app.schemas.booking import BookingCreate, BookingRead
from app.routers.auth import get_current_user
from app.routers.user import get_current_admin_user  # 관리자 체크용 의존성

router = APIRouter(prefix="/bookings", tags=["bookings"])

@router.post(
    "/",
    response_model=BookingRead,
    status_code=status.HTTP_201_CREATED,
    summary="예약 생성"
)
def create_booking(
    booking_in: BookingCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    # 30분 단위 검사
    if booking_in.start_time.minute % 30 != 0 or booking_in.end_time.minute % 30 != 0:
        raise HTTPException(status_code=400, detail="Times must be in 30-minute increments")
    # 허용 시간 검사
    if booking_in.start_time.hour < 9 or booking_in.end_time.hour > 23 or \
       (booking_in.end_time.hour == 23 and booking_in.end_time.minute > 0):
        raise HTTPException(status_code=400, detail="Booking must be between 09:00 and 23:00")
    # 중복 예약 방지
    overlap = db.query(Booking).filter(
        Booking.room_id == booking_in.room_id,
        Booking.date == booking_in.date,
        Booking.start_time < booking_in.end_time,
        Booking.end_time > booking_in.start_time
    ).first()
    if overlap:
        raise HTTPException(status_code=400, detail="Time slot already booked")

    booking = Booking(
        user_id=current_user.user_id,
        room_id=booking_in.room_id,
        date=booking_in.date,
        start_time=booking_in.start_time,
        end_time=booking_in.end_time
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking

@router.get(
    "/me",
    response_model=List[BookingRead],
    summary="내 예약 내역 조회"
)
def read_own_bookings(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    일반 사용자는 자신의 예약만, 관리자는 전체 예약을 조회할 수 있도록 분기
    """
    if current_user.role == "admin":
        # admin 계정일 경우 전체 예약 내역 반환
        return db.query(Booking).all()
    # user 계정은 본인 예약만
    return (
        db.query(Booking)
          .filter(Booking.user_id == current_user.user_id)
          .all()
    )
