from pydantic import BaseModel
from typing import List

# ─────────────────────────────────────────────
# 읽기 전용
# ─────────────────────────────────────────────
class CellRead(BaseModel):
    id: int
    floor: int
    x: int
    y: int

    class Config:
        orm_mode = True

# ─────────────────────────────────────────────
# 생성용
# ─────────────────────────────────────────────
class CellCreate(BaseModel):
    floor: int
    x: int
    y: int

# ─────────────────────────────────────────────
# 여러개를 한 번에 생성하고 싶을 수도 있으니
# 리스트 형태로 받는 스키마도 추가
# ─────────────────────────────────────────────
class CellBulkCreate(BaseModel):
    cells: List[CellCreate]
