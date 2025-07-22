from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from zoneinfo import ZoneInfo

from app.database import get_db
from app.models.booking import Booking
from app.schemas.booking import BookingCreate, BookingRead, BookingOut
from app.routers.auth import get_current_user

router = APIRouter(prefix="/bookings", tags=["bookings"])

# ✅ 예약 생성
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
    seoul_tz = ZoneInfo("Asia/Seoul")
    now = datetime.now(seoul_tz)

    dt_start = datetime.combine(booking_in.start_date, booking_in.start_time, tzinfo=seoul_tz)
    dt_end   = datetime.combine(booking_in.end_date, booking_in.end_time, tzinfo=seoul_tz)

    if dt_end <= dt_start:
        raise HTTPException(400, "종료 시간이 시작 시간보다 빨라요.")
    if (dt_end - dt_start).total_seconds() > 120 * 60:
        raise HTTPException(400, "최대 2시간까지만 예약할 수 있습니다.")

    # 동일 방 재예약 제한
    last = db.query(Booking).filter(
        Booking.user_id    == current_user.user_id,
        Booking.room_id    == booking_in.room_id,
        Booking.start_date == booking_in.start_date
    ).order_by(Booking.end_time.desc()).first()
    if last:
        last_end = datetime.combine(last.end_date, last.end_time, tzinfo=seoul_tz)
        if now < last_end:
            raise HTTPException(
                400,
                "같은 연습실은 이전 예약의 종료 시각 이후에만 다시 예약할 수 있습니다."
            )

    # 시간 겹침 체크
    conflict = db.query(Booking).filter(
        Booking.room_id    == booking_in.room_id,
        Booking.start_date == booking_in.start_date,
        Booking.start_time < booking_in.end_time,
        Booking.end_time   > booking_in.start_time,
    ).first()
    if conflict:
        raise HTTPException(400, "해당 시간에 이미 다른 사용자의 예약이 있습니다.")

    # 예약 생성
    booking = Booking(
        user_id    = current_user.user_id,
        room_id    = booking_in.room_id,
        start_date = booking_in.start_date,
        end_date   = booking_in.end_date,
        start_time = booking_in.start_time,
        end_time   = booking_in.end_time
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)

    # BookingRead로 반환 (상세 정보 필요할 때)
    return BookingRead(
        booking_id = booking.booking_id,
        start_date = booking.start_date,
        end_date   = booking.end_date,
        start_time = booking.start_time,
        end_time   = booking.end_time,
        user       = booking.user,  # Pydantic에서 from_orm 가능
        room       = booking.room,
        created_at = booking.created_at
    )


# ✅ 예약 내역 조회 (BookingOut으로 단순 필드만 반환)
@router.get(
    "/",
    response_model=List[BookingOut],
    summary="예약 내역 조회"
)
def get_bookings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # 관리자는 전체 예약, 일반 사용자는 본인 예약만
    if current_user.role == "admin":
        bookings = db.query(Booking).all()
    else:
        bookings = db.query(Booking).filter(
            Booking.user_id == current_user.user_id
        ).all()

    result: List[BookingOut] = []
    for b in bookings:
        result.append(
            BookingOut(
                id=b.booking_id,
                room_id=b.room_id,
                user_id=b.user_id,
                date=b.start_date.isoformat(),
                start_time=b.start_time.strftime("%H:%M:%S"),
                end_time=b.end_time.strftime("%H:%M:%S")
            )
        )
    return result
