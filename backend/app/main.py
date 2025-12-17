"""
FastAPI 애플리케이션 진입점

담당:
1. FastAPI 앱 생성 및 설정
2. 라우터 등록 (movies.py)
3. 데이터베이스 테이블 생성
4. CORS 설정 (Streamlit 연동용)
5. 루트 엔드포인트
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app import models
from app.routers import movies, reviews

# ===== 데이터베이스 테이블 생성 =====
Base.metadata.create_all(bind=engine)

# ===== FastAPI 앱 생성 =====
app = FastAPI(
    title="Movie Review API",
    description="영화 정보 및 리뷰 관리 API",
    version="1.0.0"
)

# ===== CORS(Cross-Origin Resource Sharing) 설정 =====
# 다른 도메인에서 API 호출 허용
# Streamlit과 통신하기 위해 필요
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 origin 허용 (개발용)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용
    allow_headers=["*"]   # 모든 헤더 허용
)

# ===== 라우터 등록 =====
app.include_router(movies.router)
app.include_router(reviews.router)

# ===== 루트 엔드포인트 =====
@app.get("/")
def read_root():
    """API 루트 엔드포인트 서버 상태 확인용"""
    return {
        "message": "Movie Review API",
        "version": "1.0.0",
        "docs": "/docs"
    }