# ─── 필요한 모듈 임포트 ─────────────────
import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from . import crud, database
from pydantic import BaseModel

# ─── FastAPI 앱 정의 (가장 먼저) ───────
app = FastAPI()

# ─── .env 로드 ─────────────────────────
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# ─── 환경변수 설정 ─────────────────────
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

# ─── SQLAlchemy 엔진 생성 ─────────────
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# ─── DB 세션 종속성 ────────────────────
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ─── Pydantic 모델 정의 ────────────────
class BookingRequest(BaseModel):
    student_id: str
    name: str
    major: str
    room: str
    floor: int
    date: str
    time_slot: str

# ─── 라우트 정의 ───────────────────────
@app.get("/ping")
def ping_db():
    with engine.connect() as conn:
        version = conn.execute(text("SELECT VERSION();")).scalar()
    return {"mysql_version": version}

@app.post("/book")
def create_booking(booking: BookingRequest, db: Session = Depends(get_db)):
    result = crud.create_booking(db, booking.dict())
    return {"status": "success", "id": result.id}

# ─── 정적 파일 서빙 ────────────────────
frontend_dir = Path(__file__).parent.parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/", response_class=HTMLResponse)
def read_index():
    html_path = frontend_dir / "index.html"
    return html_path.read_text(encoding="utf-8")
