"""
Pydantic 모델 정의 (데이터 검증 및 직렬화)

용도:
1. API 요청 데이터 검증 (Request Body)
2. API 응답 데이터 형식 (Response)
3. 자동 문서화 (FastAPI Docs)
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MovieCreate(BaseModel):
    """POST /movies/ 요청 시 사용. 사용자가 입력하는 데이터"""

    # id, created_at는 자동 생성
    # 필수 항목
    title: str
    # 선택 사항들
    release_date: Optional[str] = None
    director: Optional[str] = None
    genre: Optional[str] = None
    poster_url: Optional[str] = None

class MovieResponse(BaseModel):
    """GET /movies/ 응답 시 사용. DB에서 조회한 데이터"""

    id: int
    title: str
    release_date: Optional[str] = None
    director: Optional[str] = None
    genre: Optional[str] = None
    poster_url: Optional[str] = None
    created_at: datetime
    class Config:
        from_attributes = True  # Pydantic v2
        # from_orm = True  # ORM 모델을 Pydantic 모델로 변환 허용(구버전이면 이걸 사용)