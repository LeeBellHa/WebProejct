# backend/app/routers/booking.py

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo  # ← 추가

from app.database import get_db
from app.models.booking import Booking
from app.models.user import User
from app.models.room import Room
from app.schemas.booking import BookingCreate, BookingRead
from app.schemas.user import UserRead
from app.schemas.room import RoomRead
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
    # 0) 서울 시간 기준 now
    seoul_tz = ZoneInfo("Asia/Seoul")
    now = datetime.now(seoul_tz)

    # 1) 시작/종료 datetime 결합
    datetime_start = datetime.combine(booking_in.date, booking_in.start_time)
    datetime_end   = datetime.combine(booking_in.date, booking_in.end_time)

    # 2) 종료 시간은 반드시 시작 시간보다 이후여야 함
    if datetime_end <= datetime_start:
        raise HTTPException(400, "종료 시간이 시작 시간보다 빨라요.")

    # 3) 최대 120분까지만 허용
    duration_minutes = (datetime_end - datetime_start).total_seconds() / 60
    if duration_minutes > 120:
        raise HTTPException(
            400,
            f"현재 예약 시간은 {duration_minutes:.0f}분입니다. 최대 2시간까지만 예약할 수 있습니다."
        )

    # 4) 동일 사용자가 다른 방에 같은 시간 예약했는지 확인
    overlapping_booking = db.query(Booking).filter(
        Booking.user_id == current_user.user_id,
        Booking.date == booking_in.date,
        Booking.start_time < booking_in.end_time,
        Booking.end_time > booking_in.start_time
    ).first()
    if overlapping_booking:
        raise HTTPException(400, "이미 같은 시간대에 다른 연습실 예약이 존재합니다.")

    # 5) 같은 방에 당일 예약이 있고, 아직 종료 시간이 지나지 않았다면 거부
    if booking_in.date == now.date():
        last_same_room = (
            db.query(Booking)
              .filter(
                  Booking.user_id == current_user.user_id,
                  Booking.room_id == booking_in.room_id,
                  Booking.date == booking_in.date
              )
              .order_by(Booking.end_time.desc())
              .first()
        )
        if last_same_room:
            # last_end를 datetime으로 만들기
            last_end_dt = datetime.combine(
                last_same_room.date,
                last_same_room.end_time,
                tzinfo=seoul_tz
            )
            if now < last_end_dt:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="현재 예약 중인 같은 연습실은 종료 시각 이후에만 다시 예약할 수 있습니다."
                )

    # 6) 연습실 중복 확인 (다른 사람이 이미 예약했는지)
    room_conflict = db.query(Booking).filter(
        Booking.room_id == booking_in.room_id,
        Booking.date == booking_in.date,
        Booking.start_time < booking_in.end_time,
        Booking.end_time > booking_in.start_time
    ).first()
    if room_conflict:
        raise HTTPException(400, "해당 시간에 연습실이 이미 예약되어 있습니다.")

    # 7) 예약 생성
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
    db.refresh(booking, ["user", "room"])

    return BookingRead(
        booking_id=booking.booking_id,
        date=booking.date,
        start_time=booking.start_time,
        end_time=booking.end_time,
        user=UserRead(
            user_id=booking.user.user_id,
            username=booking.user.username,
            login_id=booking.user.login_id,
            student_id=booking.user.student_id,
            major=booking.user.major,
            phone=booking.user.phone,
            role=booking.user.role
        ),
        room=RoomRead(
            room_id=booking.room.room_id,
            room_name=str(booking.room.room_name),
            state=booking.room.state,
            equipment=booking.room.equipment
        ),
        created_at=booking.created_at
    )
