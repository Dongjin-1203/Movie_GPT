FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN rm -f .env

# 모델 변환은 선택적으로
RUN if [ -f "scripts/convert_model.py" ] && [ ! -f "app/models/sentiment/model_quantized.onnx" ]; then \
        python scripts/convert_model.py || echo "Model conversion skipped"; \
    fi

# ✅ Cloud Run의 PORT 환경 변수 사용 (기본값 8080)
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}