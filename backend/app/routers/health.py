# backend/app/routers/health.py
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from app.database import SessionLocal

router = APIRouter()

@router.get("/db")
def db_health_check():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1")).scalar()
        return {"db": "OK"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB 연결 실패: {e}")
    finally:
        db.close()
