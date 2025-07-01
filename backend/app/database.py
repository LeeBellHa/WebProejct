# # backend/app/database.py
# import os
# from pathlib import Path
# from dotenv import load_dotenv
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base

# # 1) .env 파일 로드
# env_path = Path(__file__).resolve().parent.parent / ".env"
# load_dotenv(env_path)

# # 2) 환경변수 읽기
# RDS_HOST     = os.getenv("RDS_HOST")
# RDS_PORT     = os.getenv("RDS_PORT", "3306")
# RDS_USER     = os.getenv("RDS_USER")
# RDS_PASSWORD = os.getenv("RDS_PASSWORD")
# RDS_DB_NAME  = os.getenv("RDS_DB_NAME")

# # 3) MySQL 연결 문자열 구성
# DATABASE_URL = (
#     f"mysql+pymysql://{RDS_USER}:{RDS_PASSWORD}"
#     f"@{RDS_HOST}:{RDS_PORT}/{RDS_DB_NAME}"
# )

# # 4) SQLAlchemy 엔진·세션 설정
# engine = create_engine(DATABASE_URL, pool_pre_ping=True)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()

# # 5) FastAPI 의존성 함수
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# backend/app/database.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv, find_dotenv

# 프로젝트 어디에서 실행하든 .env를 찾아 로드합니다
dotenv_path = find_dotenv()
if not dotenv_path:
    raise FileNotFoundError(".env 파일을 찾을 수 없습니다! 프로젝트 루트에 .env가 있나요?")
load_dotenv(dotenv_path)

# 이제 env가 제대로 로드됐는지 디버그 출력해 봅니다
print(">>> RDS_HOST:", os.getenv("RDS_HOST"))
print(">>> RDS_PORT:", os.getenv("RDS_PORT"))
print(">>> RDS_USER:", os.getenv("RDS_USER"))
print(">>> RDS_DB_NAME:", os.getenv("RDS_DB_NAME"))

# DB URL 구성
DATABASE_URL = (
    f"mysql+pymysql://{os.getenv('RDS_USER')}:{os.getenv('RDS_PASSWORD')}"
    f"@{os.getenv('RDS_HOST')}:{os.getenv('RDS_PORT')}/{os.getenv('RDS_DB_NAME')}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
