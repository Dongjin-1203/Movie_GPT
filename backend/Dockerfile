FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN rm -f .env

RUN if [ ! -f "app/models/sentiment/model_quantized.onnx" ]; then \
        python scripts/convert_model.py; \
    fi

# 기본값 8080, 환경 변수로 오버라이드 가능
ENV PORT=8080

EXPOSE 8080

# 환경 변수 PORT 사용
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}