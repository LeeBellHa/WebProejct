from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.notice import Notice
from app.schemas.notice import NoticeCreate, NoticeRead
from app.routers.auth import get_current_admin, get_current_user

router = APIRouter(prefix="/api", tags=["notices"])

@router.get("/notices", response_model=List[NoticeRead], summary="공지사항 목록")
def list_notices(db: Session = Depends(get_db)):
    return db.query(Notice).order_by(Notice.created_at.desc()).all()

@router.post(
    "/admin/notices",
    response_model=NoticeRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(get_current_admin)],
    summary="관리자용 공지 작성"
)
def create_notice(
    notice_in: NoticeCreate,
    db: Session = Depends(get_db)
):
    new = Notice(content=notice_in.content)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new
