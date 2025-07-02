from pydantic import BaseModel
from typing import Optional

class RoomBase(BaseModel):
    room_number: int
    is_empty: bool
    remark: Optional[str] = None

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    room_number: Optional[int] = None
    is_empty: Optional[bool] = None
    remark: Optional[str] = None

class RoomRead(RoomBase):
    room_id: int

    model_config = {
        "from_attributes": True  # Pydantic V2: ORM 객체 읽기
    }
