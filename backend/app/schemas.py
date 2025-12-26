from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class MovieBase(BaseModel):
    """영화 기본 정보 (공통 필드)"""
    title: str = Field(..., min_length=1, max_length=200, description="영화 제목")
    release_date: Optional[str] = Field(None, max_length=50, description="개봉일 (YYYY-MM-DD)")
    director: Optional[str] = Field(None, max_length=100, description="감독")
    genre: Optional[str] = Field(None, max_length=100, description="장르")
    poster_url: Optional[str] = Field(None, max_length=500, description="포스터 URL")
    actors: Optional[str] = Field(None, description="출연 배우 (쉼표로 구분)")
    plot_summary: Optional[str] = Field(None, description="줄거리")
    tmdb_id: Optional[int] = Field(None, description="TMDB ID")


class MovieCreate(MovieBase):  # 🔥 MovieBase 상속 추가!
    """POST /movies/ 요청 시 사용. 사용자가 입력하는 데이터"""
    pass


class MovieResponse(MovieBase):  # 🔥 MovieBase 상속 추가!
    """GET /movies/ 응답 시 사용. DB에서 조회한 데이터"""
    id: int
    rating: float = Field(default=0.0, ge=0.0, le=1.0, description="평균 평점")
    review_count: int = Field(default=0, ge=0, description="리뷰 개수")
    created_at: datetime
    
    class Config:
        from_attributes = True  # Pydantic v2


class ReviewCreate(BaseModel):
    """리뷰 작성 요청 스키마"""
    movie_id: int = Field(..., gt=0, description="영화 ID")
    author: str = Field(..., min_length=1, max_length=100, description="작성자")
    content: str = Field(..., min_length=5, description="리뷰 내용")


class ReviewResponse(BaseModel):
    """리뷰 응답 스키마"""
    id: int
    movie_id: int
    author: str
    content: str
    sentiment_label: Optional[str] = Field(None, description="감성 라벨 (positive/negative/neutral)")
    sentiment_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="감성 점수")
    created_at: datetime
    
    class Config:
        from_attributes = True


# ========================================
# TMDB 전용 스키마
# ========================================

class MovieSearchResult(BaseModel):
    """TMDB 검색 결과"""
    tmdb_id: int
    title: str
    original_title: str
    release_date: Optional[str] = None
    poster_path: Optional[str] = None
    overview: Optional[str] = None
    vote_average: float = 0.0


class MovieDetail(BaseModel):
    """TMDB 영화 상세 정보"""
    tmdb_id: int
    title: str
    original_title: str
    release_date: Optional[str] = None
    director: Optional[str] = None
    genre: Optional[str] = None
    actors: Optional[str] = None
    poster_url: Optional[str] = None
    plot_summary: Optional[str] = None
    vote_average: float = 0.0