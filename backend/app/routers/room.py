# backend/app/routers/room.py

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo

from app.database import get_db
from app.models.room import Room
from app.models.booking import Booking
from app.schemas.room import RoomCreate, RoomRead, RoomUpdate
from app.schemas.booking import TimeSlot
from app.routers.auth import get_current_user
from app.routers.user import get_current_admin_user

router = APIRouter(prefix="/rooms", tags=["rooms"])

# 관리자 전용 의존성
def admin_only(current_user=Depends(get_current_admin_user)):
    return current_user

# 1) 방 생성 (관리자)
@router.post(
    "/",
    response_model=RoomRead,
    status_code=status.HTTP_201_CREATED,
    summary="방 생성",
)
def create_room(
    room_in: RoomCreate,
    db: Session = Depends(get_db),
    _: object = Depends(admin_only),
):
    # 중복 확인: 방 이름으로 체크
    if db.query(Room).filter(Room.room_name == room_in.room_name).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 방 이름입니다."
        )
    room = Room(
        room_name=room_in.room_name,
        state=room_in.state,
        equipment=room_in.equipment
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room

# 2) 방 목록 조회 (모두)
@router.get(
    "/",
    response_model=List[RoomRead],
    summary="전체 방 조회",
)
def list_rooms(
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
):
    return db.query(Room).all()

# 3) 특정 방 조회
@router.get(
    "/{room_id}",
    response_model=RoomRead,
    summary="방 상세 조회",
)
def get_room(
    room_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
):
    room = db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    return room

# 4) 방 정보 수정 (관리자)
@router.patch(
    "/{room_id}",
    response_model=RoomRead,
    summary="방 정보 수정",
)
def update_room(
    room_id: int,
    room_in: RoomUpdate,
    db: Session = Depends(get_db),
    _: object = Depends(admin_only),
):
    room = db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    for field, val in room_in.dict(exclude_unset=True).items():
        setattr(room, field, val)
    db.commit()
    db.refresh(room)
    return room

# 5) 방 삭제 (관리자)
@router.delete(
    "/{room_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="방 삭제",
)
def delete_room(
    room_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(admin_only),
):
    room = db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    db.delete(room)
    db.commit()

# 6) 슬롯 조회 (예약 날짜 기준)
@router.get(
    "/{room_id}/slots",
    response_model=List[TimeSlot],
    summary="방 시간표 조회",
)
def get_room_slots(
    room_id: int,
    booking_date: date = Query(..., description="예약 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
):
    room = db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")

    # — 서버 시간 (Asia/Seoul) 기준 now
    seoul_tz = ZoneInfo("Asia/Seoul")
    now = datetime.now(seoul_tz)

    # — 운영 시간 09:00 ~ 23:00 (tz-aware)
    start_dt = datetime.combine(booking_date, time(9, 0)).replace(tzinfo=seoul_tz)
    end_dt   = datetime.combine(booking_date, time(23, 0)).replace(tzinfo=seoul_tz)

    slots: List[TimeSlot] = []
    current = start_dt
    while current < end_dt:
        next_dt = current + timedelta(minutes=30)

        # 이미 예약된 슬롯인지
        conflict = db.query(Booking).filter(
            Booking.room_id == room_id,
            Booking.date == booking_date,
            Booking.start_time < next_dt.time(),
            Booking.end_time > current.time()
        ).first() is not None

        # “오늘”이고 과거(slot 시작 시각 < now)이면 비활성화
        past_slot = (booking_date == now.date() and current < now)

        slots.append(TimeSlot(
            start=current,
            end=next_dt,
            available=not conflict and not past_slot
        ))
        current = next_dt

    return slots
