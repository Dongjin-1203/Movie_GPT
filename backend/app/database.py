# backend/app/database.py
from sqlalchemy import create_engine
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 환경 변수에서 DATABASE_URL 가져오기
db_url = os.getenv("DATABASE_URL")

if not db_url:
    raise ValueError("❌ DATABASE_URL environment variable is not set!")

# 데이터베이스 엔진 생성
engine = create_engine(
    db_url,
    echo=False,  # ← 프로덕션에서는 False로 (SQL 쿼리 로깅 끄기)
    pool_pre_ping=True
)

Session = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    """FastAPI의 의존성 주입용 함수"""
    db = Session()
    try:
        yield db
    finally:
        db.close()