# Movie_GPT
---
## 개발 배경
우리는 영화를 선택할때 많은 어려움이 있다. 특히 이 영화가 재미있는지가 굉장히 중요하다. 비싼 돈 주고 보는데 좀 더 나은 선택을 할 수 있도록 도움을 주는 서비스가 있으면 좋을 것 같아 개발하게 되었다.

---

## ✨ 주요 기능

- **영화 관리**: 영화 추가, 조회, 삭제
- **리뷰 작성**: 영화 리뷰 작성 및 관리
- **AI 감성 분석**: ONNX 기반 한국어 감성 분석 (긍정/부정/중립)
- **통계**: 영화별 평균 평점 및 리뷰 통계

---

## 🏗️ 기술 스택

### Backend
- **FastAPI**: RESTful API 서버
- **SQLAlchemy**: ORM (PostgreSQL)
- **ONNX Runtime**: 경량 AI 추론
- **Optimum**: Hugging Face 모델 최적화

### Frontend
- **Streamlit**: 웹 UI
- **Requests**: API 통신

### Infrastructure
- **Docker & Docker Compose**: 컨테이너화
- **PostgreSQL**: 데이터베이스

## 프로젝트 디렉토리 구조
```
Movie_GPT/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 앱
│   │   ├── database.py          # DB 연결
│   │   ├── models.py            # SQLAlchemy 모델
│   │   ├── schemas.py           # Pydantic 스키마
│   │   ├── routers/
│   │   │   ├── movies.py        # 영화 CRUD API
│   │   │   └── reviews.py       # 리뷰 CRUD API
│   │   ├── services/
│   │   │   └── sentiment.py    # 감성 분석 서비스
│   │   └── models/sentiment/    # ONNX 모델 저장 위치
│   ├── scripts/
│   │   └── convert_model.py    # 모델 변환 스크립트
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── pages/
│   │   ├── 1_영화추가.py
│   │   ├── 2_영화목록.py
│   │   ├── 3_리뷰작성.py
│   │   └── 4_리뷰목록.py
│   ├── utils/
│   │   └── api_client.py        # API 클라이언트
│   ├── app.py                   # Streamlit 메인
│   ├── Dockerfile
│   └── requirements.txt
│
├── docker-compose.yml
├── .dockerignore
├── .gitignore
└── README.md
```

---

## 🚀 로컬 실행 (Docker)

### 1. 사전 요구사항
- Docker Desktop 설치
- Git 설치

### 2. 프로젝트 클론
```bash
git clone 
cd Movie_GPT
```

### 3. 모델 파일 준비
```bash
# backend 디렉토리로 이동
cd backend

# 모델 변환 스크립트 실행 (최초 1회)
python scripts/convert_model.py

# 또는 Docker 빌드 시 자동 생성됨
```

### 4. Docker Compose로 실행
```bash
# 프로젝트 루트에서
docker-compose up --build
```

### 5. 접속
- **Frontend**: http://localhost:8501
- **Backend API Docs**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432

### 6. 종료
```bash
# Ctrl+C 후
docker-compose down

# 볼륨까지 삭제 (데이터베이스 초기화)
docker-compose down -v
```

## 🔧 개발 모드

### Backend만 실행
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend만 실행
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

## 📊 API 엔드포인트

### 영화
- `GET /movies/` - 전체 영화 목록
- `GET /movies/{id}` - 특정 영화 조회
- `POST /movies/` - 영화 추가
- `DELETE /movies/{id}` - 영화 삭제

### 리뷰
- `GET /reviews/` - 최근 리뷰 목록
- `GET /reviews/movie/{id}` - 특정 영화 리뷰
- `POST /reviews/` - 리뷰 작성 (자동 감성 분석)
- `DELETE /reviews/{id}` - 리뷰 삭제
- `GET /reviews/movie/{id}/rating` - 영화 평균 평점

## 🤖 감성 분석

- **모델**: `matthewburke/korean_sentiment`
- **최적화**: ONNX Runtime (INT8 양자화)
- **결과**: 긍정/부정/중립 + 신뢰도 점수

---

## 🐛 트러블슈팅

### DB 연결 실패
```
# 볼륨 완전 삭제 후 재시작
docker-compose down -v
docker volume prune -f
docker-compose up --build
```

---

## 📝 라이선스

MIT License

## 👥 기여

1. Fork
2. Feature Branch 생성
3. Commit
4. Push
5. Pull Request

## 📧 문의

이슈 등록 또는 이메일(hambur1203@gmail.com) 연락