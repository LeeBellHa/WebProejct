# backend/app/database.py

import os
from dotenv import load_dotenv, find_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ─── 1) .env 파일 로드 (없어도 그냥 넘어가기) ─────────────────
dotenv_path = find_dotenv()
if dotenv_path:
    load_dotenv(dotenv_path, override=True)
    print(f"✅ .env 로드됨: {dotenv_path}")
else:
    print("⚠️ .env 파일이 없어도 Cloudtype 환경변수를 사용합니다.")

# ─── 2) 환경변수 확인용 디버깅 출력 ────────────────────────────
print(">>> DB_HOST:", os.getenv("DB_HOST"))
print(">>> DB_PORT:", os.getenv("DB_PORT"))
print(">>> DB_USER:", os.getenv("DB_USER"))
print(">>> DB_PASS:", os.getenv("DB_PASS"))
print(">>> DB_NAME:", os.getenv("DB_NAME"))

# ─── 3) SQLAlchemy 연결 문자열 구성 ───────────────────────────
DATABASE_URL = (
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASS')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
print(">>> DATABASE_URL:", DATABASE_URL)

# ─── 4) 엔진·세션·베이스 선언 ─────────────────────────────────
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ─── 5) FastAPI 의존성 주입용 함수 ────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
