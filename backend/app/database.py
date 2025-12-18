from sqlalchemy import create_engine
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

db_url = os.getenv("DATABASE_URL")

# 디버깅 출력
print("=" * 80)
print("🔍 DATABASE CONFIGURATION DEBUG")
print("=" * 80)
if not db_url:
    raise ValueError("❌ DATABASE_URL environment variable is not set!")

# 데이터베이스 엔진 생성
engine = create_engine(
    db_url,
    echo=True,           # SQL 쿼리 로깅
    pool_pre_ping=True   # 연결 유효성 검사
)

# 세션 팩토리 생성
Session = sessionmaker(
    autocommit=False,  # 트랜잭션 수동 관리
    autoflush=False,   # 명시적 flush
    bind=engine
)

# 베이스 클래스 생성
Base = declarative_base()

def get_db():
    """FASTAPI의 의존성 주입용 함수"""
    db = Session()

    try:
        yield db
    finally:
        db.close()