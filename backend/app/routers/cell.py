from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.cell import Cell
from app.schemas.cell import CellCreate, CellRead, CellBulkCreate
from app.routers.user import get_current_admin_user   # ✅ 여기로 수정!

router = APIRouter(prefix="/cells", tags=["cells"])

# ────────────────────────────────
# 관리자 전용 접근 의존성
# ────────────────────────────────
def admin_only(current_user=Depends(get_current_admin_user)):
    return current_user

# ────────────────────────────────
# 1) 전체 cell 목록 조회 (층별 optional)
# GET /api/cells?floor=1
# ────────────────────────────────
@router.get("/", response_model=List[CellRead], summary="전체 Cell 조회")
def list_cells(
    floor: Optional[int] = Query(None, description="층 필터"),
    db: Session = Depends(get_db),
    _: object = Depends(admin_only),
):
    query = db.query(Cell)
    if floor is not None:
        query = query.filter(Cell.floor == floor)
    return query.all()

# ────────────────────────────────
# 2) 단일 cell 생성
# POST /api/cells
# ────────────────────────────────
@router.post("/", response_model=CellRead, status_code=status.HTTP_201_CREATED, summary="단일 Cell 생성")
def create_cell(
    cell_in: CellCreate,
    db: Session = Depends(get_db),
    _: object = Depends(admin_only),
):
    cell = Cell(floor=cell_in.floor, x=cell_in.x, y=cell_in.y)
    db.add(cell)
    db.commit()
    db.refresh(cell)
    return cell

# ────────────────────────────────
# 3) 여러 cell 한꺼번에 생성
# POST /api/cells/bulk
# ────────────────────────────────
@router.post("/bulk", status_code=status.HTTP_201_CREATED, summary="여러 Cell 생성")
def bulk_create_cells(
    bulk: CellBulkCreate,
    db: Session = Depends(get_db),
    _: object = Depends(admin_only),
):
    objs = [Cell(floor=c.floor, x=c.x, y=c.y) for c in bulk.cells]
    db.add_all(objs)
    db.commit()
    return {"message": f"{len(objs)} cells created"}

# ────────────────────────────────
# 4) 전체 cell 삭제 (층별 optional)
# DELETE /api/cells?floor=1
# ────────────────────────────────
@router.delete("/", status_code=status.HTTP_204_NO_CONTENT, summary="Cell 전체 삭제(층별 가능)")
def delete_all_cells(
    floor: Optional[int] = Query(None, description="층 필터"),
    db: Session = Depends(get_db),
    _: object = Depends(admin_only),
):
    query = db.query(Cell)
    if floor is not None:
        query = query.filter(Cell.floor == floor)
    query.delete()
    db.commit()
    return
