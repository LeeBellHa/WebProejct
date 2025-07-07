# backend/app/routers/booking.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import join

from app.database import get_db
from app.models.booking import Booking
from app.models.user import User
from app.schemas.booking import BookingCreate, BookingRead
from app.schemas.user import UserRead
from app.routers.auth import get_current_user
from app.routers.user import get_current_admin_user

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
    current_user=Depends(get_current_user)
):
    # (검증 로직 생략)
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

    return BookingRead(
        booking_id=booking.booking_id,
        date=booking.date,
        start_time=booking.start_time,
        end_time=booking.end_time,
        room_id=booking.room_id,
        created_at=booking.created_at,
        user=UserRead(
            user_id=current_user.user_id,
            login_id=current_user.login_id,
            student_id=current_user.student_id,
            major=current_user.major,
            phone=current_user.phone,
            role=current_user.role,
            username=current_user.username
        )
    )

@router.get(
    "/",
    response_model=List[BookingRead],
    summary="전체 예약 내역 조회 (관리자 전용)"
)
def read_all_bookings(
    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin_user)
):
    rows = (
        db.query(Booking, User)
          .join(User, Booking.user_id == User.user_id)
          .all()
    )
    return [
        BookingRead(
            booking_id=b.booking_id,
            date=b.date,
            start_time=b.start_time,
            end_time=b.end_time,
            room_id=b.room_id,
            created_at=b.created_at,
            user=UserRead(
                user_id=u.user_id,
                login_id=u.login_id,
                student_id=u.student_id,
                major=u.major,
                phone=u.phone,
                role=u.role,
                username=u.username
            )
        )
        for b, u in rows
    ]

@router.get(
    "/me",
    response_model=List[BookingRead],
    summary="내 예약 내역 조회"
)
def read_my_bookings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    rows = (
        db.query(Booking, User)
          .join(User, Booking.user_id == User.user_id)
          .filter(Booking.user_id == current_user.user_id)
          .all()
    )
    return [
        BookingRead(
            booking_id=b.booking_id,
            date=b.date,
            start_time=b.start_time,
            end_time=b.end_time,
            room_id=b.room_id,
            created_at=b.created_at,
            user=UserRead(
                user_id=u.user_id,
                login_id=u.login_id,
                student_id=u.student_id,
                major=u.major,
                phone=u.phone,
                role=u.role,
                username=u.username
            )
        )
        for b, u in rows
    ]
