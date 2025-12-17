from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()

db_url = os.getenv("DATABASE_URL")

# 데이터 베이스 연결(echo=True: SQL 쿼리 로깅 활성화, pool_pre_ping=True: 연결 유효성 검사)
engine = create_engine(db_url, echo=True, pool_pre_ping=True)

# 베이스 클래스 생성
Base = declarative_base()

# 세션 팩토리 생성
Session = sessionmaker(bind=engine)

# 세션 객체 생성
session = Session()

# 세션을 통해 데이터베이스 작업 수행
# 예: session.query(모델).filter(조건).all()

# 세션 종료
session.close()

def get_db():
    """FASTAPI의 의존성 주입용 함수"""
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()