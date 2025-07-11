# app/routers/notice.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.notice import Notice
from app.schemas.notice import NoticeCreate, NoticeRead, NoticeUpdate
from app.routers.auth import get_current_admin

router = APIRouter(prefix="/api", tags=["notices"])

@router.get("/notices", response_model=List[NoticeRead], summary="공지사항 목록")
def list_notices(db: Session = Depends(get_db)):
    return db.query(Notice).order_by(Notice.created_at.desc()).all()

@router.get("/notices/{notice_id}", response_model=NoticeRead, summary="공지사항 상세")
def get_notice(notice_id: int, db: Session = Depends(get_db)):
    notice = db.get(Notice, notice_id)
    if not notice:
        raise HTTPException(status_code=404, detail="공지 없음")
    return notice

@router.post("/admin/notices", response_model=NoticeRead,
             status_code=status.HTTP_201_CREATED,
             dependencies=[Depends(get_current_admin)],
             summary="관리자용 공지 작성")
def create_notice(notice_in: NoticeCreate, db: Session = Depends(get_db)):
    new = Notice(title=notice_in.title, content=notice_in.content)
    db.add(new); db.commit(); db.refresh(new)
    return new

@router.patch("/admin/notices/{notice_id}", response_model=NoticeRead,
              dependencies=[Depends(get_current_admin)],
              summary="관리자용 공지 수정")
def update_notice(notice_id: int, notice_in: NoticeUpdate, db: Session = Depends(get_db)):
    notice = db.get(Notice, notice_id)
    if not notice:
        raise HTTPException(status_code=404, detail="공지 없음")
    if notice_in.title   is not None: notice.title   = notice_in.title
    if notice_in.content is not None: notice.content = notice_in.content
    db.commit(); db.refresh(notice)
    return notice

@router.delete("/admin/notices/{notice_id}",
               status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(get_current_admin)],
               summary="관리자용 공지 삭제")
def delete_notice(notice_id: int, db: Session = Depends(get_db)):
    notice = db.get(Notice, notice_id)
    if not notice:
        raise HTTPException(status_code=404, detail="공지 없음")
    db.delete(notice); db.commit()
    return
