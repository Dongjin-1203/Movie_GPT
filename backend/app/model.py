"""
SQLAlchemy ORM 모델 정의
→ Python 클래스가 DB 테이블로 매핑됨

Movie 클래스 → movies 테이블
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.database import Base

class Movie(Base):
    __tablename__ = "movies"

    # 컬럼 정의
    id = Column(Integer, primary_key = True, autoincrement = True)
    title = Column(String(200), nullable = True)
    release_date = Column(String(50), nullable = True)
    director = Column(String(100), nullable = True)
    genre = Column(String(100), nullable = True)
    poster_url = Column(String(500), nullable = True)
    created_at = Column(DateTime, default=func.now(), nullable = False )