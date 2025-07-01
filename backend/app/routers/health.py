# backend/app/routers/health.py

from fastapi import APIRouter, HTTPException
# - APIRouter: 엔드포인트(라우터) 그룹을 모듈 단위로 관리할 때 사용
# - HTTPException: API 처리 중 에러가 발생하면 적절한 HTTP 에러 응답을 던질 때 사용

from sqlalchemy import text # SQLAlchemy raw SQL 실행을 위한 text 함수
from app.database import SessionLocal # DB 세션 생성기(SessionLocal)를 가져옴

router = APIRouter()
# - 이 모듈에서 정의하는 모든 엔드포인트는 이 router 객체에 등록됨
# - main.py 등에서 `app.include_router(router, prefix="/health")` 식으로 붙여주면
#   해당 prefix 아래에 이 라우터의 경로들이 합쳐집니다.

@router.get("/db")
def db_health_check():
    try:
        db = SessionLocal() #세션 생성
        db.execute(text("SELECT 1")).scalar() #SQL 실행 SELECT 1으로
        return {"db": "OK"} #예외가 없으면 OK 응답
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB 연결 실패: {e}")
    finally:
        db.close()
