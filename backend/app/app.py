import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy import create_engine, text

# ─── 1) .env 로드 ────────────────────────────────────
# backend/app/app.py 기준으로 backend/까지 올라가서 .env 읽기
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# ─── 2) 환경변수 읽기 ──────────────────────────────────
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

# ─── 3) SQLAlchemy 엔진 생성 ────────────────────────────
DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# ─── 4) FastAPI 앱 정의 ────────────────────────────────
app = FastAPI()

# ─── 5) 정적 파일 서빙 (해결방법 1 적용) ──────────────────
# /static 경로에 frontend/ 폴더 전체를 서빙합니다.
frontend_dir = Path(__file__).parent.parent.parent / "frontend"
app.mount(
    "/static",
    StaticFiles(directory=frontend_dir),
    name="static"
)

# 루트(/) 요청 시 index.html 직접 반환
@app.get("/", response_class=HTMLResponse)
def read_index():
    html_path = frontend_dir / "index.html"
    return html_path.read_text(encoding="utf-8")

# ─── 6) RDS 연결 확인용 핑 엔드포인트 ────────────────────
@app.get("/ping")
def ping_db():
    with engine.connect() as conn:
        version = conn.execute(text("SELECT VERSION();")).scalar()
    return {"mysql_version": version}
