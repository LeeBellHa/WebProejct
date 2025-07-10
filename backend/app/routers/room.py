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
    if db.query(Room).filter(Room.room_name == room_in.room_name).first():
        raise HTTPException(status_code=400, detail="이미 존재하는 방 이름입니다.")
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
        raise HTTPException(status_code=404, detail="Room not found")
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
        raise HTTPException(status_code=404, detail="Room not found")
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
        raise HTTPException(status_code=404, detail="Room not found")
    db.delete(room)
    db.commit()

# 6) 슬롯 조회 (주간 윈도우 적용)
@router.get(
    "/{room_id}/slots",
    response_model=List[TimeSlot],
    summary="방 시간표 조회 (주간 윈도우 자동 적용)",
)
def get_room_slots(
    room_id: int,
    booking_date: date = Query(..., description="예약 날짜 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),
):
    # 1) 서버 시간 (Asia/Seoul) 기준 now
    seoul = ZoneInfo("Asia/Seoul")
    now = datetime.now(seoul)

    # 2) 이번 주 금요일 09:00 계산
    today_wd = now.weekday()           # Mon=0 ... Fri=4 ... Sun=6
    days_to_friday = (4 - today_wd) % 7
    friday_date = (now + timedelta(days=days_to_friday)).date()
    friday9 = datetime.combine(friday_date, time(9, 0), tzinfo=seoul)

    # 3) 예약 오픈 주(월~일) 결정
    if now >= friday9:
        # 금요일 09:00 이후 → 다음 주
        window_start = friday_date + timedelta(days=3)   # 다음 주 월요일
    else:
        # 금요일 09:00 이전 → 이번 주
        window_start = friday_date - timedelta(days=4)   # 이번 주 월요일
    window_end = window_start + timedelta(days=6)       # 주 일요일

    # 4) 요청된 날짜가 오픈 윈도우 내인지 확인
    if not (window_start <= booking_date <= window_end):
        # 범위 밖일 땐 빈 리스트 반환 (모두 비활성)
        return []

    # 5) 룸 존재 확인
    room = db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # 6) 영업 시간 슬롯 생성 (09:00~23:00, 30분 단위)
    start_dt = datetime.combine(booking_date, time(9, 0), tzinfo=seoul)
    end_dt   = datetime.combine(booking_date, time(23, 0), tzinfo=seoul)

    slots: List[TimeSlot] = []
    current = start_dt
    while current < end_dt:
        next_dt = current + timedelta(minutes=30)

        # 7) 블록/예약 충돌 체크 (start_date~end_date 범위 & 시간)
        conflict = db.query(Booking).filter(
            Booking.room_id    == room_id,
            Booking.start_date <= booking_date,
            Booking.end_date   >= booking_date,
            Booking.start_time <  next_dt.time(),
            Booking.end_time   >  current.time()
        ).first() is not None

        # 8) 오늘 과거 슬롯 비활성
        past = (booking_date == now.date() and current < now)

        slots.append(TimeSlot(
            start=current,
            end=next_dt,
            available=not conflict and not past
        ))
        current = next_dt

    return slots
