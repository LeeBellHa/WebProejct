from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.room import Room
from app.schemas.room import RoomCreate, RoomRead, RoomUpdate
from app.routers.auth import get_current_user
from app.routers.user import get_current_admin_user

router = APIRouter(prefix="/room", tags=["room"])

# 관리자 전용 의존성
def admin_only(current_user = Depends(get_current_admin_user)):
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
    _: Room = Depends(admin_only),
):
    # 중복 확인: 방 번호로 체크
    if db.query(Room).filter(Room.room_number == room_in.room_number).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 존재하는 방 번호입니다."
        )
    room = Room(
        room_number=room_in.room_number,
        is_empty=room_in.is_empty,
        remark=room_in.remark
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
def list_room(
    db: Session = Depends(get_db),
    _: object = Depends(get_current_user),  # 로그인만 하면 OK
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
    _: Room = Depends(admin_only),
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
    _: Room = Depends(admin_only),
):
    room = db.get(Room, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room not found")
    db.delete(room)
    db.commit()
    return