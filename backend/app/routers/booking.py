from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from zoneinfo import ZoneInfo

from app.database import get_db
from app.models.booking import Booking
from app.schemas.booking import BookingCreate, BookingRead
from app.schemas.user import UserRead
from app.schemas.room import RoomRead
from app.routers.auth import get_current_user

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
    # 0) 서울 시간 기준 now (tz-aware)
    seoul_tz = ZoneInfo("Asia/Seoul")
    now = datetime.now(seoul_tz)

    # 1) 시작/종료 tz-aware datetime 결합
    dt_start = datetime.combine(booking_in.start_date, booking_in.start_time, tzinfo=seoul_tz)
    dt_end   = datetime.combine(booking_in.end_date,   booking_in.end_time,   tzinfo=seoul_tz)

    # 2) 기본 유효성 검사
    if dt_end <= dt_start:
        raise HTTPException(status_code=400, detail="종료 시간이 시작 시간보다 빨라요.")
    if (dt_end - dt_start).total_seconds() > 120*60:
        raise HTTPException(status_code=400, detail="최대 2시간까지만 예약할 수 있습니다.")

    # 3) 동일 사용자, 동일 날짜 이전 예약 종료 시각 검사
    last = db.query(Booking).filter(
        Booking.user_id == current_user.user_id,
        Booking.start_date == booking_in.start_date
    ).order_by(Booking.end_time.desc()).first()

    if last:
        last_end = datetime.combine(last.end_date, last.end_time, tzinfo=seoul_tz)
        # 현재 시간이 아직 이전 예약 종료 전이라면 새 예약 불가
        if now < last_end:
            raise HTTPException(
                status_code=400,
                detail="같은 날짜에 이미 예약이 있어 이전 예약의 종료 시각 이후에만 재예약할 수 있습니다."
            )

    # 4) 다른 사람 예약 겹침 체크 (같은 방에서)
    conflict = db.query(Booking).filter(
        Booking.room_id == booking_in.room_id,
        Booking.start_date == booking_in.start_date,
        Booking.start_time < booking_in.end_time,
        Booking.end_time > booking_in.start_time
    ).first()
    if conflict:
        raise HTTPException(status_code=400, detail="해당 시간에 이미 다른 사용자의 예약이 있습니다.")

    # 5) 동일 사용자 다른 방 예약 겹침 체크 (추가)
    user_conflict = db.query(Booking).filter(
        Booking.user_id == current_user.user_id,
        Booking.start_date == booking_in.start_date,
        Booking.start_time < booking_in.end_time,
        Booking.end_time > booking_in.start_time,
        Booking.room_id != booking_in.room_id
    ).first()
    if user_conflict:
        raise HTTPException(status_code=400, detail="동일한 시간대에 다른 연습실을 예약할 수 없습니다.")

    # 6) 예약 생성
    booking = Booking(
        user_id=current_user.user_id,
        room_id=booking_in.room_id,
        start_date=booking_in.start_date,
        end_date=booking_in.end_date,
        start_time=booking_in.start_time,
        end_time=booking_in.end_time
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    db.refresh(booking, ["user", "room"])

    return BookingRead(
        booking_id=booking.booking_id,
        start_date=booking.start_date,
        end_date=booking.end_date,
        start_time=booking.start_time,
        end_time=booking.end_time,
        user=UserRead.from_orm(booking.user),
        room=RoomRead.from_orm(booking.room),
        created_at=booking.created_at
    )
