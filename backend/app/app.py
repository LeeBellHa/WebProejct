# backend/app/app.py

import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from sqlalchemy import create_engine, text

# ─── 1) .env 로드 ────────────────────────────────────
env_path = Path(__file__).parent.parent / ".env"
print("→ Loading .env from:", env_path, "exists?", env_path.exists())
load_dotenv(env_path, override=True)

# ─── 2) 환경변수 읽기 ──────────────────────────────────
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
print("→ Loaded env:", {
    "DB_HOST": DB_HOST,
    "DB_PORT": DB_PORT,
    "DB_USER": DB_USER,
    "DB_PASS": DB_PASS,
    "DB_NAME": DB_NAME,
})

# ─── 3) SQLAlchemy 엔진 생성 ────────────────────────────
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print("→ DATABASE_URL:", DATABASE_URL)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# ─── 4) FastAPI 앱 정의 ────────────────────────────────
app = FastAPI()

# ─── 4.1) API 라우터 등록 ───────────────────────────────
from app.routers.user import router as user_router
app.include_router(user_router)

from app.routers.booking import router as booking_router
app.include_router(booking_router)


# ─── 5) 프론트엔드 전체 정적 서빙 ─────────────────────────
frontend_dir = Path(__file__).parent.parent.parent / "frontend"
app.mount(
    "/", 
    StaticFiles(directory=frontend_dir, html=True),
    name="frontend"
)
# 이제
# GET  /           → frontend/index.html
# GET  /register_test.html → frontend/register_test.html

# ─── 6) RDS 연결 확인용 핑 엔드포인트 ────────────────────
@app.get("/ping")
def ping_db():
    with engine.connect() as conn:
        version = conn.execute(text("SELECT VERSION();")).scalar()
    return {"mysql_version": version}
