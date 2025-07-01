# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import Base, engine
from app.routers.user import router as user_router
from app.routers.health import router as health_router 

# 테이블 자동생성
Base.metadata.create_all(bind=engine)

app = FastAPI(title="NM Study Room Booking")

# CORS 허용 (개발 중에만 "*"로 풀어주세요)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# /users, /health 라우터 등록
app.include_router(user_router)
app.include_router(health_router)

# static 디렉터리(/static) 마운트: 여기 안에 HTML·JS·CSS 파일을 두면 됩니다
app.mount( "/static", StaticFiles(directory="app/static"), name="static")
# 이 아래만 추가
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)