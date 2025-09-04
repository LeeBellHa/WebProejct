from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import Query


from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.routers.auth import get_current_user  # 로그인된 사용자

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

templates = Jinja2Templates(directory="frontend")


# ─── 1-1) 중복 체크 API ───────────────────────────────────────────────
@router.get(
    "/check-duplicate",
    summary="ID/학번 중복 체크"
)
def check_duplicate(
    field: str = Query(..., pattern="^(login_id|student_id)$"),
    value: str = Query(...),
    db: Session = Depends(get_db),
):
    if field == "login_id":
        exists = db.query(User).filter(User.login_id == value).first()
        if exists:
            return {"exists": True, "message": "이미 사용 중인 로그인 ID입니다."}
    elif field == "student_id":
        exists = db.query(User).filter(User.student_id == value).first()
        if exists:
            return {"exists": True, "message": "이미 사용 중인 학번입니다."}
    return {"exists": False}



# ─── helper: 관리자 검증 의존성 ─────────────────────────────────────────────
def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="관리자만 접근 가능합니다."
        )
    return current_user

# ─── 1) 일반 회원가입 ─────────────────────────────────────────────────────
@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
)
def register_user(
    user_in: UserCreate,
    db: Session = Depends(get_db),
):
    # ✅ 사전 중복 체크
    if db.query(User).filter(User.login_id == user_in.login_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 로그인 ID입니다."
        )
    if db.query(User).filter(User.student_id == user_in.student_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이미 사용 중인 학번입니다."
        )

    db_user = User(
        login_id=user_in.login_id,
        password=user_in.password,
        username=user_in.username,
        student_id=user_in.student_id,
        major=user_in.major,
        phone=user_in.phone,
        role="pending"
    )
    db.add(db_user)

    try:
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError as e:
        db.rollback()
        # ✅ 동시 요청 대비 예외 처리
        if "student_id" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용 중인 학번입니다."
            )
        elif "login_id" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 사용 중인 로그인 ID입니다."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="중복된 값이 존재합니다."
            )

# ─── 2) 전체 사용자 조회 (관리자) ─────────────────────────────────────────
@router.get(
    "",
    response_model=List[UserRead],
    summary="전체 사용자 조회",
)
@router.get(
    "/",
    response_model=List[UserRead],
    summary="전체 사용자 조회",
)
def list_all_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    return db.query(User).all()

# ─── 3) 승인 대기중 사용자 조회 (관리자) ───────────────────────────────────
@router.get(
    "/pending",
    response_model=List[UserRead],
    summary="승인 대기 사용자 조회",
)
def list_pending_users(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    return db.query(User).filter(User.role == "pending").all()

# ─── 4) 특정 사용자 승인 (관리자) ─────────────────────────────────────────
@router.patch(
    "/{user_id}/approve",
    response_model=UserRead,
    summary="사용자 승인",
)
def approve_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    if user.role != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="승인 대상이 아닙니다."
        )
    user.role = "user"
    db.commit()
    db.refresh(user)
    return user

# ─── 5) 사용자 삭제 (관리자 전용) ─────────────────────────────────────────
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="사용자 삭제 (관리자)",
)
def delete_user_by_admin(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin_user),
):
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    db.delete(user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# ─── 6) 내 계정 삭제 (본인용) ─────────────────────────────────────────────
@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="내 계정 삭제",
)
def delete_own_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db.delete(current_user)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# ─── 7) 관리자 HTML: 사용자 목록 렌더링 ───────────────────────────────────
@router.get(
    "/admin/html/users",
    response_class=HTMLResponse,
    summary="관리자 사용자 목록 페이지",
)
async def admin_users_html(
    request: Request,
    _: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    users = db.query(User).all()
    return templates.TemplateResponse("admin_users.html", {"request": request, "users": users})
