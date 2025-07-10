from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime
from app.database import Base

class Notice(Base):
    __tablename__ = "notices"

    notice_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    content   = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
