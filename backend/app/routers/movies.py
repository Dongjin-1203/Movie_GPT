"""
FastAPI 라우터 - 영화 관련 모든 API 엔드포인트 정의

구현할 API:
1. POST /movies/          - 영화 추가
2. GET /movies/           - 전체 영화 목록 조회
3. GET /movies/{movie_id} - 특정 영화 조회
4. DELETE /movies/{movie_id} - 영화 삭제
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Movie
from app.schemas import MovieCreate, MovieResponse

# 라우터 생성
router = APIRouter(
    prefix="/movies",
    tags=["movies"]
)

# API 엔드포인트 구현

# 영화 추가
@router.post("/", response_model=MovieResponse, status_code=201)
def create_movie(movie: MovieCreate, db: Session = Depends(get_db)):
    """새로운 영화 추가"""

    # Pydantic 모델 → SQLAlchemy 모델 변환
    db_movie = Movie(
        **movie.model_dump()
    )
    
    # DB에 추가
    db.add(db_movie)

    # 변경사항 저장
    db.commit()

    # 새로 추가된 영화 객체 새로고침
    db.refresh(db_movie)

    return db_movie

# 영화 목록 조회
@router.get("/", response_model=List[MovieResponse])
def get_movies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """전체 영화 목록 조회 (페이지네이션 지원)"""
    
    # DB 쿼리 (최신순 정렬)
    movies = db.query(Movie)\
               .order_by(Movie.created_at.desc())\
               .offset(skip)\
               .limit(limit)\
               .all()
    return movies

# 특정 영화 조회
@router.get("/{movie_id}", response_model=MovieResponse)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    """특정 영화 조회"""
    
    # DB에서 조회
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    
    # 존재하지 않으면 404 에러
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

# 영화 삭제
@router.delete("/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    """영화 삭제"""
    
    # 1. 영화 조회
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    
    # 2. 존재하지 않으면 404
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    # 3. 삭제
    db.delete(movie)
    db.commit()
    
    # 4. 성공 메시지 반환
    return {"message": "Movie deleted successfully"}