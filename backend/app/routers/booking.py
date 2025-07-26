from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

from app.database import get_db
from app.models.booking import Booking
from app.schemas.booking import BookingCreate, BookingRead
from app.schemas.user import UserRead
from app.schemas.room import RoomRead
from app.routers.auth import get_current_user

# ===========================
# 📌 Jinja2 템플릿 경로: frontend 폴더
# ===========================
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/
TEMPLATE_DIR = BASE_DIR / "frontend"                      # webproject/frontend/
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))

# ===========================
# 📌 Router 설정
# ===========================
router = APIRouter(prefix="/bookings", tags=["bookings"])

# =========================================================
# ✅ HTML 페이지로 현재 로그인한 사용자의 예약 리스트 보기
# =========================================================
@router.get("/my-booking-list", response_class=HTMLResponse, summary="현재 사용자 예약 내역 HTML 페이지")
async def my_booking_list(
    request: Request,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    my_bookings = db.query(Booking).filter(
        Booking.user_id == current_user.user_id
    ).order_by(Booking.start_date, Booking.start_time).all()

    return templates.TemplateResponse(
        "user_booking_list.html",
        {"request": request, "bookings": my_bookings}
    )

# =========================================================
# ✅ JSON API: 현재 로그인한 사용자의 예약 리스트 조회
# =========================================================
@router.get(
    "/me",
    response_model=List[BookingRead],
    summary="현재 로그인한 사용자의 예약 리스트 조회"
)
def get_my_bookings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    bookings = db.query(Booking).filter(
        Booking.user_id == current_user.user_id
    ).order_by(Booking.start_date, Booking.start_time).all()

    return [
        BookingRead(
            booking_id=b.booking_id,
            start_date=b.start_date,
            end_date=b.end_date,
            start_time=b.start_time,
            end_time=b.end_time,
            user=UserRead.from_orm(b.user),
            room=RoomRead.from_orm(b.room),
            created_at=b.created_at
        ) for b in bookings
    ]

# =========================================================
# ✅ JSON API: 전체 예약 리스트 (관리자 전용)
# =========================================================
@router.get(
    "/",
    response_model=List[BookingRead],
    summary="전체 예약 리스트 (관리자 전용)"
)
def get_all_bookings(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # 관리자 권한 체크
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="관리자만 접근 가능합니다.")
    bookings = db.query(Booking).order_by(Booking.start_date, Booking.start_time).all()
    return [
        BookingRead(
            booking_id=b.booking_id,
            start_date=b.start_date,
            end_date=b.end_date,
            start_time=b.start_time,
            end_time=b.end_time,
            user=UserRead.from_orm(b.user),
            room=RoomRead.from_orm(b.room),
            created_at=b.created_at
        ) for b in bookings
    ]

# =========================================================
# ✅ 예약 생성
# =========================================================
@router.post(
    "/",
    response_model=BookingRead,
    status_code=status.HTTP_201_CREATED,
    summary="예약 생성"
)
def create_booking(
    booking_in: BookingCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    seoul_tz = ZoneInfo("Asia/Seoul")
    now = datetime.now(seoul_tz)

    dt_start = datetime.combine(booking_in.start_date, booking_in.start_time, tzinfo=seoul_tz)
    dt_end   = datetime.combine(booking_in.end_date, booking_in.end_time, tzinfo=seoul_tz)

    if dt_end <= dt_start:
        raise HTTPException(status_code=400, detail="종료 시간이 시작 시간보다 빨라요.")
    if (dt_end - dt_start).total_seconds() > 120*60:
        raise HTTPException(status_code=400, detail="최대 2시간까지만 예약할 수 있습니다.")

    last = db.query(Booking).filter(
        Booking.user_id == current_user.user_id,
        Booking.start_date == booking_in.start_date
    ).order_by(Booking.end_time.desc()).first()

    if last:
        last_end = datetime.combine(last.end_date, last.end_time, tzinfo=seoul_tz)
        if now < last_end:
            raise HTTPException(
                status_code=400,
                detail="같은 날짜에 이미 예약이 있어 이전 예약의 종료 시각 이후에만 재예약할 수 있습니다."
            )

    conflict = db.query(Booking).filter(
        Booking.room_id == booking_in.room_id,
        Booking.start_date == booking_in.start_date,
        Booking.start_time < booking_in.end_time,
        Booking.end_time > booking_in.start_time
    ).first()
    if conflict:
        raise HTTPException(status_code=400, detail="해당 시간에 이미 다른 사용자의 예약이 있습니다.")

    user_conflict = db.query(Booking).filter(
        Booking.user_id == current_user.user_id,
        Booking.start_date == booking_in.start_date,
        Booking.start_time < booking_in.end_time,
        Booking.end_time > booking_in.start_time,
        Booking.room_id != booking_in.room_id
    ).first()
    if user_conflict:
        raise HTTPException(status_code=400, detail="동일한 시간대에 다른 연습실을 예약할 수 없습니다.")

    booking = Booking(
        user_id=current_user.user_id,
        room_id=booking_in.room_id,
        start_date=booking_in.start_date,
        end_date=booking_in.end_date,
        start_time=booking_in.start_time,
        end_time=booking_in.end_time
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    db.refresh(booking, ["user", "room"])

    return BookingRead(
        booking_id=booking.booking_id,
        start_date=booking.start_date,
        end_date=booking.end_date,
        start_time=booking.start_time,
        end_time=booking.end_time,
        user=UserRead.from_orm(booking.user),
        room=RoomRead.from_orm(booking.room),
        created_at=booking.created_at
    )
