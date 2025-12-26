"""
FastAPI 라우터 - 영화 관련 모든 API 엔드포인트 정의

구현할 API:
1. POST /movies/          - 영화 추가
2. GET /movies/           - 전체 영화 목록 조회
3. GET /movies/{movie_id} - 특정 영화 조회
4. DELETE /movies/{movie_id} - 영화 삭제
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import requests
import os

from app.database import get_db
from .. import models, schemas
from ..database import get_db

# 라우터 생성
router = APIRouter(
    prefix="/movies",
    tags=["movies"]
)

# TMDB API 설정
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

# ========================================
# 🆕 TMDB 검색 API
# ========================================

@router.get("/search", response_model=List[schemas.MovieSearchResult])
def search_movies(
    query: str = Query(..., min_length=1, description="검색할 영화 제목"),
    db: Session = Depends(get_db)
):
    """
    TMDB에서 영화 검색
    
    - **query**: 검색할 영화 제목 (2글자 이상 권장)
    - 실시간 자동완성용
    """
    if not TMDB_API_KEY:
        raise HTTPException(status_code=500, detail="TMDB API key not configured")
    
    try:
        # TMDB API 호출
        response = requests.get(
            f"{TMDB_BASE_URL}/search/movie",
            params={
                "api_key": TMDB_API_KEY,
                "language": "ko-KR",
                "query": query,
                "page": 1
            },
            timeout=5
        )
        response.raise_for_status()
        data = response.json()
        
        # 결과 변환 (상위 10개만)
        results = []
        for movie in data.get("results", [])[:10]:
            results.append(schemas.MovieSearchResult(
                tmdb_id=movie["id"],
                title=movie.get("title", ""),
                original_title=movie.get("original_title", ""),
                release_date=movie.get("release_date", ""),
                poster_path=f"{TMDB_IMAGE_BASE}{movie['poster_path']}" if movie.get("poster_path") else None,
                overview=movie.get("overview", ""),
                vote_average=movie.get("vote_average", 0.0)
            ))
        
        return results
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"TMDB API error: {str(e)}")


@router.get("/tmdb/{tmdb_id}", response_model=schemas.MovieDetail)
def get_tmdb_movie_detail(tmdb_id: int):
    """
    TMDB에서 영화 상세 정보 가져오기
    
    - **tmdb_id**: TMDB 영화 ID
    - 배우, 감독 정보 포함
    """
    if not TMDB_API_KEY:
        raise HTTPException(status_code=500, detail="TMDB API key not configured")
    
    try:
        # 영화 상세 정보 + 크레딧 정보
        response = requests.get(
            f"{TMDB_BASE_URL}/movie/{tmdb_id}",
            params={
                "api_key": TMDB_API_KEY,
                "language": "ko-KR",
                "append_to_response": "credits"  # 배우/감독 정보 포함
            },
            timeout=5
        )
        response.raise_for_status()
        movie = response.json()
        
        # 배우 추출 (상위 5명)
        cast = movie.get("credits", {}).get("cast", [])
        actors = ", ".join([actor["name"] for actor in cast[:5]])
        
        # 감독 추출
        crew = movie.get("credits", {}).get("crew", [])
        directors = [person["name"] for person in crew if person["job"] == "Director"]
        director = directors[0] if directors else None
        
        # 장르 추출 (첫 번째)
        genres = movie.get("genres", [])
        genre = genres[0]["name"] if genres else None
        
        return schemas.MovieDetail(
            tmdb_id=movie["id"],
            title=movie.get("title", ""),
            original_title=movie.get("original_title", ""),
            release_date=movie.get("release_date", ""),
            director=director,
            genre=genre,
            actors=actors,
            poster_url=f"{TMDB_IMAGE_BASE}{movie['poster_path']}" if movie.get("poster_path") else None,
            plot_summary=movie.get("overview", ""),
            vote_average=movie.get("vote_average", 0.0)
        )
    
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"TMDB API error: {str(e)}")


@router.post("/from-tmdb/{tmdb_id}", response_model=schemas.MovieResponse, status_code=201)
def create_movie_from_tmdb(tmdb_id: int, db: Session = Depends(get_db)):
    """
    TMDB에서 영화 정보를 가져와서 DB에 추가 (원클릭)
    
    - **tmdb_id**: TMDB 영화 ID
    - 중복 체크 자동
    """
    # 중복 체크
    existing = db.query(models.Movie).filter(models.Movie.tmdb_id == tmdb_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="이미 등록된 영화입니다")
    
    # TMDB에서 상세 정보 가져오기
    movie_detail = get_tmdb_movie_detail(tmdb_id)
    
    # DB에 저장
    db_movie = models.Movie(
        tmdb_id=movie_detail.tmdb_id,
        title=movie_detail.title,
        release_date=movie_detail.release_date,
        director=movie_detail.director,
        genre=movie_detail.genre,
        actors=movie_detail.actors,
        poster_url=movie_detail.poster_url,
        plot_summary=movie_detail.plot_summary,
        rating=movie_detail.vote_average / 10.0  # TMDB는 0-10, 우리는 0-1
    )
    
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    
    return db_movie


# ========================================
# 기존 영화 CRUD API
# ========================================

@router.get("/", response_model=List[schemas.MovieResponse])
def read_movies(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """전체 영화 목록 조회"""
    movies = db.query(models.Movie).order_by(models.Movie.created_at.desc()).offset(skip).limit(limit).all()
    return movies


@router.get("/{movie_id}", response_model=schemas.MovieResponse)
def read_movie(movie_id: int, db: Session = Depends(get_db)):
    """특정 영화 조회"""
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.post("/", response_model=schemas.MovieResponse, status_code=201)
def create_movie(movie: schemas.MovieCreate, db: Session = Depends(get_db)):
    """영화 수동 추가"""
    db_movie = models.Movie(**movie.dict())
    db.add(db_movie)
    db.commit()
    db.refresh(db_movie)
    return db_movie


@router.delete("/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    """영화 삭제"""
    movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    db.delete(movie)
    db.commit()
    return {"message": "Movie deleted successfully"}