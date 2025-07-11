# app/models/notice.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base

class Notice(Base):
    __tablename__ = "notices"

    notice_id  = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title      = Column(String(255), nullable=False)          # ← 추가
    content    = Column(Text,   nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
