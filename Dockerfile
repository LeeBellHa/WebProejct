FROM python:3.11-slim

WORKDIR /app

RUN pip install --upgrade pip

# requirements.txt는 backend에 있으니 경로 지정
COPY backend/requirements.txt .

RUN pip install -r requirements.txt

# backend와 frontend 모두 복사
COPY backend /app/backend
COPY frontend /app/frontend

WORKDIR /app/backend

EXPOSE 5000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]
