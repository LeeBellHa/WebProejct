from typing import Optional
from pydantic import BaseModel, ConfigDict

# 공통 필드
class RoomBase(BaseModel):
    room_name: str                     # 문자열로 변경
    floor: int                         # 층수
    pos_x: Optional[int] = None        # X좌표
    pos_y: Optional[int] = None        # Y좌표
    state: bool                        # 사용 가능 여부
    equipment: Optional[str] = None    # 장비 정보

# 생성용
class RoomCreate(RoomBase):
    """생성 시 room_name 중복만 체크하고 state/equipment/floor/pos_x/pos_y는 선택 가능."""
    pass

# 수정용
class RoomUpdate(BaseModel):
    room_name: Optional[str] = None
    floor: Optional[int] = None
    pos_x: Optional[int] = None
    pos_y: Optional[int] = None
    state: Optional[bool] = None
    equipment: Optional[str] = None

# 조회용
class RoomRead(RoomBase):
    room_id: int
    model_config = ConfigDict(from_attributes=True)
