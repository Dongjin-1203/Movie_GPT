# backend/Dockerfile

FROM python:3.11-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# ⭐ 로컬 .env 파일 삭제 (중요!)
RUN rm -f .env

# 모델이 없으면 생성
RUN if [ ! -f "app/models/sentiment/model_quantized.onnx" ]; then \
        python scripts/convert_model.py; \
    fi

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]