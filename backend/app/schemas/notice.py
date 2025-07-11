# app/schemas/notice.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class NoticeBase(BaseModel):
    title:   str = Field(..., description="공지 제목")
    content: str = Field(..., description="공지 내용")

class NoticeCreate(NoticeBase):
    pass

class NoticeUpdate(BaseModel):
    title:   Optional[str] = Field(None, description="공지 제목")
    content: Optional[str] = Field(None, description="공지 내용")

class NoticeRead(NoticeBase):
    notice_id:  int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
