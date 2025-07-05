# backend/app/main.py

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.routers.user import router as user_router
from app.routers.health import router as health_router
from app.routers.auth import router as auth_router
from app.routers.room import router as room_router
from app.routers.booking import router as booking_router
from app.routers import auth, user, booking 

# 1) 테이블 자동생성 (개발/테스트 용)
Base.metadata.create_all(bind=engine)

# 2) FastAPI 앱 생성
app = FastAPI(title="NM Study Room Booking")

# 3) CORS 설정 (개발 중에만 "*"로 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4) API 라우터 등록
app.include_router(user_router)                     # /users
app.include_router(health_router)                   # /health
app.include_router(auth_router)                     # /auth
# 연습실/예약 라우터를 /api 아래에 한 번만 붙입니다.
app.include_router(room_router,    prefix="/api", tags=["rooms"])     # → /api/rooms, /api/rooms/{id}/slots
app.include_router(booking_router, prefix="/api", tags=["bookings"])  # → /api/bookings
app.include_router(booking.router)   


# 5) 정적 파일 서빙 설정
#    프로젝트 루트의 frontend 폴더 전체를 루트("/") 경로로 마운트합니다.
frontend_dir = Path(__file__).parent.parent.parent / "frontend"
app.mount(
    "/",
    StaticFiles(directory=frontend_dir, html=True),
    name="frontend"
)

# 6) 스크립트 직접 실행 시 Uvicorn으로 구동
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
