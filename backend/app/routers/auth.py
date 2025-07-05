# backend/app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import os
from jose import jwt
from app.database import get_db
from app.models.user import User

SECRET_KEY = os.getenv("JWT_SECRET", "devsecret")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # 1) 사용자 조회 및 비밀번호 검증
    user: User = db.query(User).filter(User.login_id == form.username).first()
    if not user or user.password != form.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인 정보가 올바르지 않습니다."
        )

    # 2) 승인 대기 상태면 접근 차단
    if user.role == "pending":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="아직 승인 대기 중인 계정입니다. 관리자 승인을 기다려 주세요."
        )

    # 3) JWT 발급 (payload에 user 전체 정보 담기)
    payload = {
        "sub":         user.login_id,
        "user_id":     user.user_id,
        "username":    user.username,
        "student_id":  user.student_id,
        "major":       user.major,
        "phone":       user.phone,
        "role":        user.role,
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return {
        "access_token": token,
        "token_type":   "bearer",
        "role":         user.role,  # ← 로그인 응답에 role 필드 추가
    }


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    try:
        data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        login_id = data.get("sub")
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    user = db.query(User).filter(User.login_id == login_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user
