# user 테이블
# backend/app/models/user.py
from sqlalchemy import Column, Integer, String, Boolean, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.database import Base

# 사용자 역할 정의
USER_ROLES = ("pending", "user", "admin") #가입대기, 사용자, 관리자

# --- 전공(Major) 선택지 정의 ---
MAJORS = (
    "뮤직테크놀러지&컴퓨터음악작곡",
    "싱어송라이터전공",
    "재즈퍼포먼스전공",
)

class User(Base): #사용자 테이블을 나타내는 ORM모델 클래스, 실제 DB는 users라는 이름의 테이블로 생성
    __tablename__ = "users"

    # 내부 고유번호 (PK)
    user_id = Column(Integer, primary_key=True, index=True) #id, 기본키 설정, 레코드 식별용
    login_id = Column(String(50), unique=True, index=True, nullable=False) #로그인할때 쓰는 id
    password = Column(String(128), nullable=False)
    username = Column(String(100), nullable=False) #사용자의 이름
    student_id = Column(String(20), unique=True, nullable=False) #학번, 중복 불가
    major = Column(SAEnum(*MAJORS, name = "major_types"), nullable = False)
    phone = Column(String(20), nullable=True) #핸드폰번호
    role = Column(SAEnum(*USER_ROLES, name="user_roles"), default="pending", nullable=False)

    # 예약 관계
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")
