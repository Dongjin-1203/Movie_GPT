FROM python:3.11-slim

WORKDIR /app

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 로컬 .env 파일 삭제
RUN rm -f .env

# PORT 환경 변수 (기본값 8501, Cloud Run은 8080 주입)
ENV PORT=8501

EXPOSE ${PORT}

# Streamlit 실행
# 로컬: PORT=8501 (기본값)
# Cloud Run: PORT=8080 (자동 주입)
CMD streamlit run app.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false \
    --server.enableXsrfProtection=false