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
from typing import List, Optional
import requests
import os
from sqlalchemy import or_
from anthropic import Anthropic
import json

from app.database import get_db
from .. import models, schemas
from ..database import get_db
from app.services.mcp_client import get_mcp_client

# 라우터 생성
router = APIRouter(
    prefix="/movies",
    tags=["movies"]
)

# TMDB API 설정
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/w500"

# claude 설정
anthropic_client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

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

# ========================================
# 추천 API
# ========================================

@router.get("/recommend", response_model=List[schemas.MovieResponse])
def recommend_movies(
    genre: Optional[str] = None,
    director: Optional[str] = None,
    min_rating: float = 0.0,
    sentiment: Optional[str] = None,  # positive, negative, neutral
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """
    간단한 영화 추천 API
    
    Parameters:
    - genre: 장르 (예: "스릴러", "드라마")
    - director: 감독 이름
    - min_rating: 최소 평점 (0.0 ~ 1.0)
    - sentiment: 긍정/부정 리뷰가 많은 영화
    - limit: 추천 개수
    """
    query = db.query(models.Movie)
    
    # 장르 필터
    if genre:
        query = query.filter(models.Movie.genre.ilike(f"%{genre}%"))
    
    # 감독 필터
    if director:
        query = query.filter(models.Movie.director.ilike(f"%{director}%"))
    
    # 최소 평점 필터
    query = query.filter(models.Movie.rating >= min_rating)
    
    # 리뷰가 있는 영화만
    query = query.filter(models.Movie.review_count > 0)
    
    # 평점 높은 순 정렬
    query = query.order_by(models.Movie.rating.desc())
    
    # 제한
    movies = query.limit(limit).all()
    
    return movies


@router.get("/recommend/similar/{movie_id}", response_model=List[schemas.MovieResponse])
def recommend_similar(
    movie_id: int,
    limit: int = 5,
    db: Session = Depends(get_db)
):
    """
    특정 영화와 비슷한 영화 추천
    (같은 장르 + 같은 감독 우선)
    """
    # 기준 영화
    base_movie = db.query(models.Movie).filter(models.Movie.id == movie_id).first()
    if not base_movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    # 비슷한 영화 찾기
    query = db.query(models.Movie).filter(models.Movie.id != movie_id)
    
    # 같은 장르 또는 같은 감독
    if base_movie.genre or base_movie.director:
        conditions = []
        
        if base_movie.genre:
            conditions.append(models.Movie.genre.ilike(f"%{base_movie.genre}%"))
        
        if base_movie.director:
            conditions.append(models.Movie.director.ilike(f"%{base_movie.director}%"))
        
        query = query.filter(or_(*conditions))
    
    # 평점 높은 순
    movies = query.order_by(models.Movie.rating.desc()).limit(limit).all()
    
    return movies

@router.post("/recommend/ai")
async def ai_recommend(request: dict):
    """
    Claude API + MCP를 사용한 완전한 AI 추천
    """
    user_query = request.get("query", "")
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY not configured")
    
    if not os.getenv("TMDB_API_KEY"):
        raise HTTPException(status_code=500, detail="TMDB_API_KEY not configured")
    
    try:
        # MCP Client 가져오기
        mcp_client = get_mcp_client()
        
        # MCP Tools 목록 가져오기
        tools = await mcp_client.list_tools()
        
        # 1단계: Claude API 호출 (Tool 포함)
        messages = [{
            "role": "user",
            "content": f"""사용자가 다음과 같은 영화를 찾고 있습니다:

"{user_query}"

TMDB API tools를 사용하여 적절한 영화를 5개 찾아서 추천해주세요.
각 영화에 대해 제목, 개봉일, 평점, 줄거리를 포함하여 추천 이유를 설명해주세요.

사용 가능한 도구:
- discover_movies: 장르로 영화 찾기 (genre: "스릴러", "드라마", "코미디" 등)
- search_movies: 영화 제목으로 검색
- get_movie_details: 영화 상세 정보"""
        }]
        
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            tools=tools,
            messages=messages
        )
        
        # 2단계: Tool 호출 처리
        while response.stop_reason == "tool_use":
            # Tool 호출 결과 수집
            tool_results = []
            
            for content_block in response.content:
                if content_block.type == "tool_use":
                    tool_name = content_block.name
                    tool_input = content_block.input
                    
                    # MCP Server에 Tool 호출
                    result = await mcp_client.call_tool(tool_name, tool_input)
                    
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": content_block.id,
                        "content": result
                    })
            
            # Claude에게 Tool 결과 전달
            messages.append({"role": "assistant", "content": response.content})
            messages.append({"role": "user", "content": tool_results})
            
            # 다시 Claude 호출
            response = anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                tools=tools,
                messages=messages
            )
        
        # 3단계: 최종 응답 추출
        final_text = ""
        for content_block in response.content:
            if hasattr(content_block, "text"):
                final_text += content_block.text
        
        return {
            "response": final_text,
            "conversation": messages
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI 추천 오류: {str(e)}")