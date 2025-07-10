from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class NoticeBase(BaseModel):
    content: str = Field(..., description="공지 내용")

class NoticeCreate(NoticeBase):
    pass

class NoticeRead(NoticeBase):
    notice_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
