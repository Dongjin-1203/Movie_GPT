"""
리뷰 관련 API 엔드포인트
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Review, Movie
from app.schemas import ReviewCreate, ReviewResponse
from app.services.sentiment import analyze_sentiment

# 라우터 생성
router = APIRouter(
    prefix="/reviews",
    tags=["reviews"]
)


# API 1: 리뷰 작성
@router.post("/", response_model=ReviewResponse, status_code=201)
def create_review(review: ReviewCreate, db: Session = Depends(get_db)):
    """새 리뷰 작성 (자동 감성 분석)"""
    
    # 1. 영화 존재 여부 확인
    movie = db.query(Movie).filter(Movie.id == review.movie_id).first()
    if movie is None:
        raise HTTPException(404, "Movie not found")
    
    # 2. 감성 분석 수행
    sentiment_result = analyze_sentiment(review.content)
    
    # 3. 리뷰 생성
    db_review = Review(
        movie_id=review.movie_id,
        author=review.author,
        content=review.content,
        sentiment_label=sentiment_result["label"],
        sentiment_score=sentiment_result["score"]
    )
    
    # 4. DB 저장
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    return db_review


# API 2: 전체 리뷰 조회 (최근 10개)
@router.get("/", response_model=List[ReviewResponse])
def get_reviews(
    limit: int = 10,
    skip: int = 0,
    db: Session = Depends(get_db)
):
    """최근 리뷰 목록 조회"""
    
    reviews = db.query(Review)\
                .order_by(Review.created_at.desc())\
                .offset(skip)\
                .limit(limit)\
                .all()
    
    return reviews


# API 3: 특정 영화 리뷰 조회
@router.get("/movie/{movie_id}", response_model=List[ReviewResponse])
def get_movie_reviews(movie_id: int, db: Session = Depends(get_db)):
    """특정 영화의 모든 리뷰 조회"""
    
    # 영화 존재 확인
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie is None:
        raise HTTPException(404, "Movie not found")
    
    # 리뷰 조회
    reviews = db.query(Review)\
                .filter(Review.movie_id == movie_id)\
                .order_by(Review.created_at.desc())\
                .all()
    
    return reviews


# API 4: 리뷰 삭제
@router.delete("/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db)):
    """리뷰 삭제"""
    
    # 리뷰 조회
    review = db.query(Review).filter(Review.id == review_id).first()
    
    if review is None:
        raise HTTPException(404, "Review not found")
    
    # 삭제
    db.delete(review)
    db.commit()
    
    return {"message": "Review deleted successfully"}


# API 5: 영화 평균 평점
@router.get("/movie/{movie_id}/rating")
def get_movie_rating(movie_id: int, db: Session = Depends(get_db)):
    """영화의 평균 감성 점수 계산"""
    
    # 영화 존재 확인
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if movie is None:
        raise HTTPException(404, "Movie not found")
    
    # 리뷰 조회
    reviews = db.query(Review)\
                .filter(Review.movie_id == movie_id)\
                .all()
    
    # 평균 계산
    if len(reviews) == 0:
        return {
            "movie_id": movie_id,
            "average_score": 0.0,
            "review_count": 0
        }
    
    total_score = sum(r.sentiment_score for r in reviews if r.sentiment_score)
    count = len([r for r in reviews if r.sentiment_score])
    
    average = total_score / count if count > 0 else 0.0
    
    return {
        "movie_id": movie_id,
        "average_score": round(average, 2),
        "review_count": len(reviews)
    }