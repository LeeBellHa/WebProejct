# backend/app/routers/user.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserRead)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    # login_id 중복 체크
    if db.query(User).filter(User.login_id == user_in.login_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 로그인 ID입니다."
        )
    # 비밀번호 해싱
    hashed_pw = pwd_ctx.hash(user_in.password)
    db_user = User(
        login_id=user_in.login_id,
        hashed_password=hashed_pw,
        username=user_in.username,
        student_id=user_in.student_id,
        major=user_in.major,
        phone=user_in.phone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user