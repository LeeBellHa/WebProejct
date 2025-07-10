# backend/app/schemas/room.py

from typing import Optional, Union
from pydantic import BaseModel, ConfigDict

class RoomBase(BaseModel):
    room_name: int               # ex) 12402, 22214, 41901 …
    state:     bool              # True=empty, False=full
    equipment: Optional[str] = None  # 비고(장비 리스트)

class RoomCreate(RoomBase):
    """생성 시 room_name 중복만 체크하고 state/equipment는 선택 가능."""
    pass

class RoomUpdate(BaseModel):
    room_name: Optional[int]    = None
    state:     Optional[bool]   = None
    equipment: Optional[str]    = None

class RoomRead(RoomBase):
    room_id:   int
    room_name: Union[int, str]

    model_config = ConfigDict(from_attributes=True)
