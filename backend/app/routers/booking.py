from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

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
    datetime_start = datetime.combine(booking_in.date, booking_in.start_time)
    datetime_end = datetime.combine(booking_in.date, booking_in.end_time)

    # 1. 종료 시간은 반드시 시작 시간보다 이후여야 함
    if datetime_end <= datetime_start:
        raise HTTPException(400, "종료 시간이 시작 시간보다 빨라요.")

    # 2. 예약 시간(분)을 정확하게 계산
    duration_minutes = (datetime_end - datetime_start).total_seconds() / 60

    # 디버깅: 실제 계산된 시간
    print("⏱️ 예약 시간:", duration_minutes, "분")

    # 3. 최대 120분까지만 허용
    if duration_minutes > 120:
        raise HTTPException(400, f"현재 예약 시간은 {duration_minutes}분입니다. 최대 2시간까지만 예약할 수 있습니다.")

    # 4. 중복 예약 검사: 사용자가 다른 방에 같은 시간 예약했는지 확인
    overlapping_booking = db.query(Booking).filter(
        Booking.user_id == current_user.user_id,
        Booking.date == booking_in.date,
        Booking.start_time < booking_in.end_time,
        Booking.end_time > booking_in.start_time
    ).first()
    if overlapping_booking:
        raise HTTPException(400, "이미 같은 시간대에 다른 연습실 예약이 존재합니다.")

    # 5. 연습실 중복 확인
    room_conflict = db.query(Booking).filter(
        Booking.room_id == booking_in.room_id,
        Booking.date == booking_in.date,
        Booking.start_time < booking_in.end_time,
        Booking.end_time > booking_in.start_time
    ).first()
    if room_conflict:
        raise HTTPException(400, "해당 시간에 연습실이 이미 예약되어 있습니다.")

    # 6. 예약 생성
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


@router.get(
    "/",
    response_model=List[BookingRead],
    summary="전체 예약 내역 조회 (관리자 전용)"
)
def read_all_bookings(
    room_id: Optional[int] = Query(None, description="호실 ID로 필터링"),

    db: Session = Depends(get_db),
    admin_user=Depends(get_current_admin_user)
):
    # # 모든 예약을 사용자, 방 정보와 함께 조회
    # rows = (
    #     db.query(Booking, User, Room)
    #       .join(User, Booking.user_id == User.user_id)
    #       .join(Room, Booking.room_id == Room.room_id)
    #       .order_by(Booking.date, Booking.start_time)
    #       .all()
    # )

    q = (
        db.query(Booking, User, Room)
          .join(User, Booking.user_id == User.user_id)
          .join(Room, Booking.room_id == Room.room_id)
    )
    if room_id is not None:
        q = q.filter(Booking.room_id == room_id)
    rows = q.order_by(Booking.date, Booking.start_time).all()

    return [
        BookingRead(
            booking_id=b.booking_id,
            date=b.date,
            start_time=b.start_time,
            end_time=b.end_time,
            user=UserRead(
                user_id=u.user_id,
                username=u.username,
                login_id=u.login_id,
                student_id=u.student_id,
                major=u.major,
                phone=u.phone,
                role=u.role
            ),
            room=RoomRead(
                room_id=r.room_id,
                room_name=str(r.room_name),
                state=r.state,
                equipment=r.equipment
            ),
            created_at=b.created_at
        )
        for b, u, r in rows
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
    # 현재 로그인한 사용자의 예약만 조회
    rows = (
        db.query(Booking, User, Room)
          .join(User, Booking.user_id == User.user_id)
          .join(Room, Booking.room_id == Room.room_id)
          .filter(Booking.user_id == current_user.user_id)
          .order_by(Booking.date, Booking.start_time)
          .all()
    )

    return [
        BookingRead(
            booking_id=b.booking_id,
            date=b.date,
            start_time=b.start_time,
            end_time=b.end_time,
            user=UserRead(
                user_id=u.user_id,
                username=u.username,
                login_id=u.login_id,
                student_id=u.student_id,
                major=u.major,
                phone=u.phone,
                role=u.role
            ),
            room=RoomRead(
                room_id=r.room_id,
                room_name=str(r.room_name),
                state=r.state,
                equipment=r.equipment
            ),
            created_at=b.created_at
        )
        for b, u, r in rows
    ]