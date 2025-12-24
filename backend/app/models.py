"""
SQLAlchemy ORM 모델 정의
→ Python 클래스가 DB 테이블로 매핑됨

Movie 클래스 → movies 테이블
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey
# ForeignKey: 테이블 간의 관계를 정의하는데 사용
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.database import Base

class Movie(Base):
    __tablename__ = "movies"

    # 컬럼 정의
    id = Column(Integer, primary_key=True, index=True)
    tmdb_id = Column(Integer, unique=True, nullable=True, index=True)
    title = Column(String(200), nullable=False)
    release_date = Column(String(50))
    director = Column(String(100))
    genre = Column(String(100))
    poster_url = Column(String(500))
    actors = Column(Text)
    plot_summary = Column(Text)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # relationship
    reviews = relationship("Review", back_populates="movie", cascade="all, delete-orphan")

class Review(Base):
    __tablename__ = "reviews"

    # 컬럼 정의
    id = Column(Integer, primary_key=True, index=True)
    movie_id = Column(
        Integer,
        ForeignKey("movies.id", ondelete="CASCADE"),
        # ForeignKey("movies.id"): movies 테이블의 id 참조
        # ondelete="CASCADE": 영화 삭제 시 리뷰도 자동 삭제
        nullable=False
    )
    author = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    sentiment_label = Column(String(20))  # 'positive', 'negative', 'neutral'
    sentiment_score = Column(Float)       # 0.0 ~ 1.0
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship (영화와의 관계 - 선택사항)
    movie = relationship("Movie", back_populates="reviews")