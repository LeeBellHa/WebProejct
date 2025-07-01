# user 테이블
# backend/app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.database import Base

# 사용자 역할 정의
USER_ROLES = ("pending", "user", "admin")

class User(Base):
    __tablename__ = "users"

    # 내부 고유번호 (PK)
    id = Column(Integer, primary_key=True, index=True)
    login_id = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)
    username = Column(String(100), nullable=False)
    student_id = Column(String(20), unique=True, nullable=False)
    major = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    role = Column(SAEnum(*USER_ROLES, name="user_roles"), default="pending", nullable=False)

    # 예약 관계 (추후 정의)
    # reservations = relationship("Reservation", back_populates="user")