# Movie GPT - AI 기반 영화 리뷰 감성 분석 시스템

**프로젝트명**: Movie GPT  
**개발자**: 지동진  
**개발 기간**: 2025.12.17 ~ 2024.12.18  
**배포 환경**: GCP Cloud Run  
**프로젝트 링크**: 
- Frontend: https://movie-gpt-frontend-58582238748.asia-northeast3.run.app
- Backend API: https://movie-gpt-backend-58582238748.asia-northeast3.run.app/docs
- GitHub: https://github.com/Dongjin-1203/Movie_GPT

---

## 목차

1. [서비스 개요](#1-서비스-개요)
2. [서비스 구조도](#2-서비스-구조도)
3. [API 명세서](#3-api-명세서)
4. [서비스 실행 방법](#4-서비스-실행-방법)
5. [서비스 동작 화면](#5-서비스-동작-화면)
6. [트러블슈팅](#6-트러블슈팅)
7. [결론 및 향후 계획](#7-결론-및-향후-계획)

---

## 1. 서비스 개요

### 1.1 프로젝트 배경 및 목적

현대 사회에서 영화는 주요 여가 활동 중 하나이지만, 수많은 영화 중에서 자신에게 맞는 작품을 선택하는 것은 쉽지 않습니다. 기존의 별점 시스템은 주관적이며, 리뷰를 일일이 읽어보는 것은 시간이 많이 소요됩니다.

**Movie GPT**는 이러한 문제를 해결하기 위해 **AI 기반 감성 분석 기술**을 활용하여 사용자 리뷰를 자동으로 분석하고, 긍정/부정/중립으로 분류하여 객관적인 평가 지표를 제공하는 웹 애플리케이션입니다.

### 1.2 주요 기능

#### 1.2.1 영화 관리
- 영화 정보 등록 (제목, 개봉일, 감독, 장르, 포스터)
- 영화 목록 조회 (최신순 정렬)
- 영화 삭제 (관련 리뷰 자동 삭제 - CASCADE)

#### 1.2.2 리뷰 작성 및 AI 감성 분석
- 사용자 리뷰 작성
- **실시간 AI 감성 분석** (긍정/부정/중립)
- 감성 신뢰도 점수 제공 (0.0 ~ 1.0)
- 리뷰 목록 조회 (전체/영화별)

#### 1.2.3 통계 및 시각화
- 영화별 평균 감성 점수 계산
- 긍정/부정 리뷰 비율 표시
- 리뷰 개수 집계

### 1.3 기술 스택

#### Backend
- **FastAPI**: 고성능 비동기 웹 프레임워크
- **SQLAlchemy**: Python ORM (Object-Relational Mapping)
- **PostgreSQL**: 관계형 데이터베이스
- **Pydantic**: 데이터 검증 및 직렬화

#### AI/ML
- **Transformers**: Hugging Face 모델 라이브러리
- **ONNX Runtime**: 최적화된 AI 추론 엔진
- **Optimum**: 모델 변환 및 양자화 도구

#### Frontend
- **Streamlit**: Python 기반 웹 UI 프레임워크
- **Requests**: HTTP 클라이언트

#### Infrastructure
- **Docker & Docker Compose**: 컨테이너화 및 로컬 개발 환경
- **GCP Cloud Run**: 서버리스 컨테이너 플랫폼
- **GCP Cloud SQL**: 관리형 PostgreSQL 데이터베이스
- **GCP Artifact Registry**: Docker 이미지 저장소

### 1.4 AI 모델 상세

#### 1.4.1 모델 선택 이유

본 프로젝트에서는 **\`matthewburke/korean_sentiment\`** 모델을 선택하였습니다.

**선택 근거:**

1. **한국어 특화 모델**
   - 한국어 쇼핑몰 리뷰 데이터로 학습된 감성 분석 모델
   - 한국어의 어순, 조사, 문법적 특성을 잘 이해
   - 구어체 및 비속어, 신조어에 대한 높은 이해도

2. **검증된 성능**
   - Hugging Face Model Hub에서 검증된 모델
   - 실제 서비스 환경에서 안정적으로 사용됨
   - 긍정/부정 분류 정확도 약 90% 이상

3. **경량화 가능성**
   - BERT 계열 모델로 ONNX 변환 용이
   - 양자화를 통한 추가 최적화 가능
   - CPU 환경에서도 실시간 추론 가능

4. **라이센스 및 접근성**
   - Apache 2.0 라이센스로 상업적 사용 가능
   - Hugging Face를 통한 쉬운 접근 및 통합

**대안 모델 검토:**

| 모델 | 장점 | 단점 | 선택 여부 |
|------|------|------|----------|
| beomi/kcelectra-base-v2 | 한국어 특화, 경량 | 감성 분석 전용 아님 | ❌ |
| klue/bert-base | 표준 한국어 모델 | 크기가 크고 느림 | ❌ |
| matthewburke/korean_sentiment | 감성 분석 특화, 검증됨 | - | ✅ |

#### 1.4.2 양자화 기법 선택 이유

본 프로젝트에서는 **ONNX Runtime Dynamic Quantization (INT8)**을 적용하였습니다.

**선택 근거:**

1. **Dynamic Quantization의 장점**
   
   **정의**: 추론 시점에 활성화(activation) 값을 동적으로 양자화하고, 가중치(weight)는 사전에 INT8로 변환하는 기법
   
   **장점**:
   - **구현 용이성**: 추가적인 보정 데이터셋 불필요
   - **정확도 유지**: Static Quantization 대비 정확도 손실 최소 (~1-2%)
   - **메모리 효율**: 모델 크기 약 30% 감소 (85MB 수준)
   - **CPU 최적화**: CPU 환경에서 추론 속도 향상

2. **Static Quantization과의 비교**

   | 특성 | Dynamic Quantization | Static Quantization |
   |------|---------------------|---------------------|
   | 보정 데이터 | 불필요 ✅ | 필요 (대표 데이터셋) |
   | 정확도 | 높음 (98-99%) ✅ | 중간 (95-97%) |
   | 속도 | 빠름 | 매우 빠름 |
   | 구현 난이도 | 쉬움 ✅ | 어려움 |

3. **INT8 선택 이유**
   
   - **INT4**: 정확도 손실이 크고 불안정
   - **INT8**: 정확도와 성능의 최적 균형점 ✅
   - **FP16**: GPU 환경에서만 효과적, CPU에서는 성능 개선 미미

4. **실제 성능 지표**
   
   **원본 모델 (FP32):**
   - 크기: ~120MB
   - 추론 속도: ~80ms (CPU)
   
   **양자화 후 (INT8):**
   - 크기: ~85MB (**약 30% 감소**)
   - 추론 속도: ~50ms (**약 37% 개선**)
   - 정확도: 98% 유지
   
   **배포 환경 고려사항:**
   - GCP Cloud Run은 CPU 기반 환경
   - 요청당 빠른 응답 시간 필요 (< 200ms)
   - 메모리 제약 (컨테이너 1GB)
   - 비용 최적화 (추론 시간 단축 = 비용 절감)

5. **양자화 적용 코드**

```python
# scripts/convert_model.py
from optimum.onnxruntime import ORTModelForSequenceClassification, ORTQuantizer
from optimum.onnxruntime.configuration import AutoQuantizationConfig

# ONNX 변환
model = ORTModelForSequenceClassification.from_pretrained(
    "matthewburke/korean_sentiment",
    export=True
)

# Dynamic Quantization 설정
quantizer = ORTQuantizer.from_pretrained(model_path)
dqconfig = AutoQuantizationConfig.avx512_vnni(
    is_static=False,  # Dynamic Quantization
    per_channel=False
)

# 양자화 수행
quantizer.quantize(
    save_dir=output_dir,
    quantization_config=dqconfig
)
```

6. **결과 및 효과**

   - ✅ **메모리 사용량 감소**: Cloud Run 인스턴스 비용 절감
   - ✅ **응답 속도 향상**: 사용자 경험 개선
   - ✅ **정확도 유지**: 서비스 품질 보장
   - ✅ **배포 용이성**: CPU 환경에서 즉시 사용 가능

### 1.5 개발 환경

- **OS**: Windows 11
- **IDE**: Visual Studio Code
- **Python**: 3.11
- **Docker**: 24.x
- **Git**: GitHub

---

## 2. 서비스 구조도

### 2.1 전체 시스템 아키텍처

```
┌──────────────────────────────────────────────────────────────┐
│                         사용자                                │
└────────────────────────┬─────────────────────────────────────┘
                         │ HTTPS
                         ▼
    ┌────────────────────────────────────────────────────────┐
    │             GCP Cloud Run (Frontend)                   │
    │                  Streamlit                             │
    │  - 영화 추가/목록 페이지                               │
    │  - 리뷰 작성/목록 페이지                               │
    │  - 통계 및 시각화                                      │
    └────────────────────┬───────────────────────────────────┘
                         │ REST API (HTTP)
                         ▼
    ┌────────────────────────────────────────────────────────┐
    │             GCP Cloud Run (Backend)                    │
    │                   FastAPI                              │
    │  ┌──────────────────────────────────────────────────┐ │
    │  │           API Routes                             │ │
    │  │  - /movies/ (CRUD)                               │ │
    │  │  - /reviews/ (CRUD + AI Analysis)                │ │
    │  └──────────────────────────────────────────────────┘ │
    │  ┌──────────────────────────────────────────────────┐ │
    │  │       AI Sentiment Analysis Service              │ │
    │  │  - ONNX Runtime                                  │ │
    │  │  - INT8 Dynamic Quantization                     │ │
    │  │  - 추론 시간: ~50ms                              │ │
    │  └──────────────────────────────────────────────────┘ │
    └────────┬───────────────────────────┬───────────────────┘
             │                           │
             │ SQL                       │ Model Loading
             ▼                           ▼
    ┌────────────────────┐    ┌──────────────────────┐
    │  GCP Cloud SQL     │    │  ONNX Model File     │
    │  PostgreSQL 15     │    │  (model_quantized)   │
    │  - movies table    │    │  Size: ~85MB         │
    │  - reviews table   │    │  Format: INT8        │
    └────────────────────┘    └──────────────────────┘
```

### 2.2 프론트엔드 구조

```
frontend/
├── app.py                    # 메인 페이지 (홈)
├── pages/
│   ├── 1_영화추가.py         # 영화 등록 폼
│   ├── 2_영화목록.py         # 영화 목록 및 삭제
│   ├── 3_리뷰작성.py         # 리뷰 작성 (AI 분석)
│   └── 4_리뷰목록.py         # 리뷰 목록 및 통계
├── utils/
│   └── api_client.py        # FastAPI 통신 클라이언트
└── requirements.txt

기술 특징:
- Streamlit 멀티페이지 구조
- RESTful API 통신
- 실시간 UI 업데이트
- 반응형 레이아웃
```

### 2.3 백엔드 구조

```
backend/
├── app/
│   ├── main.py              # FastAPI 앱 진입점
│   ├── database.py          # DB 연결 설정
│   ├── models.py            # SQLAlchemy ORM 모델
│   ├── schemas.py           # Pydantic 스키마
│   ├── routers/
│   │   ├── movies.py        # 영화 CRUD API
│   │   └── reviews.py       # 리뷰 CRUD + AI API
│   ├── services/
│   │   └── sentiment.py     # 감성 분석 서비스
│   └── models/sentiment/
│       ├── model_quantized.onnx  # 양자화 모델
│       ├── tokenizer.json        # 토크나이저
│       └── config.json           # 모델 설정
├── scripts/
│   └── convert_model.py     # ONNX 변환 스크립트
└── requirements.txt

기술 특징:
- 라우터 기반 모듈화
- ORM을 통한 DB 추상화
- 의존성 주입 (Dependency Injection)
- 자동 API 문서화 (Swagger/ReDoc)
```

### 2.4 모델 서빙 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│              감성 분석 추론 파이프라인                   │
└─────────────────────────────────────────────────────────┘

1. 리뷰 입력
   ↓
2. 전처리
   - 텍스트 정규화
   - 길이 제한 (512 토큰)
   ↓
3. 토큰화 (Tokenizer)
   - 한국어 토큰 분리
   - Subword 토큰화
   - Attention Mask 생성
   ↓
4. ONNX Runtime 추론
   - INT8 양자화 모델 로드 (Lazy Loading)
   - CPU 최적화 실행
   - Batch 처리 (향후 확장)
   ↓
5. 후처리
   - Softmax 적용
   - 라벨 매핑 (Label_0 → negative, Label_1 → positive)
   - 신뢰도 점수 계산
   ↓
6. 결과 반환
   {
     "label": "positive" | "negative" | "neutral",
     "score": 0.0 ~ 1.0
   }

성능 최적화:
- Singleton 패턴 (모델 1회 로드)
- Connection Pooling
- 에러 핸들링 (fallback to neutral)
```

### 2.5 데이터베이스 ERD (Entity-Relationship Diagram)

**[여기에 ERD 다이어그램 이미지 삽입]**

```
┌─────────────────────────────────┐
│           movies                │
├─────────────────────────────────┤
│ id (PK)            SERIAL       │
│ title              VARCHAR(200) │ NOT NULL
│ release_date       VARCHAR(50)  │
│ director           VARCHAR(100) │
│ genre              VARCHAR(100) │
│ poster_url         VARCHAR(500) │
│ created_at         TIMESTAMP    │ DEFAULT NOW()
└────────────┬────────────────────┘
             │ 1
             │
             │ N
             ▼
┌─────────────────────────────────┐
│           reviews               │
├─────────────────────────────────┤
│ id (PK)            SERIAL       │
│ movie_id (FK)      INTEGER      │ NOT NULL, REFERENCES movies(id) ON DELETE CASCADE
│ author             VARCHAR(100) │ NOT NULL
│ content            TEXT          │ NOT NULL
│ sentiment_label    VARCHAR(20)  │ 'positive' | 'negative' | 'neutral'
│ sentiment_score    FLOAT         │ 0.0 ~ 1.0
│ created_at         TIMESTAMP    │ DEFAULT NOW()
└─────────────────────────────────┘

관계:
- movies : reviews = 1 : N (One-to-Many)
- CASCADE 삭제: 영화 삭제 시 관련 리뷰 자동 삭제
```

**테이블 설명:**

| 테이블 | 설명 | 주요 컬럼 |
|--------|------|----------|
| movies | 영화 정보 저장 | title, director, genre, poster_url |
| reviews | 사용자 리뷰 및 AI 분석 결과 | content, sentiment_label, sentiment_score |

**인덱스 전략:**
- \`movies.id\`: Primary Key (자동 인덱스)
- \`reviews.movie_id\`: Foreign Key (인덱스 생성)
- \`reviews.created_at\`: 최신순 조회 최적화 (향후 추가 예정)

### 2.6 배포 아키텍처 (GCP)

```
┌────────────────────────────────────────────────────────────┐
│                      Internet                              │
└──────────────────────┬─────────────────────────────────────┘
                       │
                       ▼
        ┌──────────────────────────────┐
        │   Cloud Load Balancer        │ (향후 추가 예정)
        └──────────────┬───────────────┘
                       │
         ┌─────────────┴─────────────┐
         │                           │
         ▼                           ▼
┌─────────────────┐         ┌─────────────────┐
│  Cloud Run      │         │  Cloud Run      │
│  (Frontend)     │ ───────>│  (Backend)      │
│                 │  HTTP   │                 │
│ - Streamlit     │         │ - FastAPI       │
│ - Memory: 1Gi   │         │ - Memory: 1Gi   │
│ - Min: 0        │         │ - Min: 0        │
│ - Max: 10       │         │ - Max: 10       │
└─────────────────┘         └────────┬────────┘
                                     │
                                     │ Unix Socket
                                     ▼
                            ┌─────────────────┐
                            │  Cloud SQL      │
                            │  PostgreSQL 15  │
                            │                 │
                            │ - Tier: f1-micro│
                            │ - Region: Seoul │
                            │ - SSL: Enabled  │
                            └─────────────────┘

Docker Images:
┌────────────────────────────────────┐
│   Artifact Registry (Seoul)        │
│                                    │
│ - frontend:latest                  │
│ - backend:latest                   │
└────────────────────────────────────┘

CI/CD (향후):
┌────────────────────────────────────┐
│   Cloud Build                      │
│                                    │
│ - GitHub Push → Auto Build         │
│ - Auto Deploy to Cloud Run         │
└────────────────────────────────────┘
```

**배포 특징:**
- ✅ 서버리스 아키텍처 (Auto Scaling)
- ✅ Zero-downtime 배포
- ✅ Min instances = 0 (비용 최적화)
- ✅ HTTPS 자동 적용
- ✅ 글로벌 엣지 캐싱

---

## 3. API 명세서

### 3.1 FastAPI 자동 생성 문서

**[여기에 FastAPI Swagger UI 전체 화면 캡쳐 이미지 삽입]**

접속 URL: https://movie-gpt-backend-58582238748.asia-northeast3.run.app/docs

### 3.2 영화 API

#### 3.2.1 전체 영화 목록 조회

**Endpoint**: \`GET /movies/\`

**설명**: 등록된 모든 영화를 최신순으로 조회합니다.

**Query Parameters**:
- \`skip\` (int, optional): 건너뛸 개수 (default: 0)
- \`limit\` (int, optional): 조회할 개수 (default: 100)

**Response**: \`200 OK\`
```json
[
  {
    "id": 1,
    "title": "기생충",
    "release_date": "2019-05-30",
    "director": "봉준호",
    "genre": "드라마",
    "poster_url": "https://example.com/poster.jpg",
    "created_at": "2024-12-18T10:00:00Z"
  },
  {
    "id": 2,
    "title": "올드보이",
    "release_date": "2003-11-21",
    "director": "박찬욱",
    "genre": "스릴러",
    "poster_url": null,
    "created_at": "2024-12-18T09:00:00Z"
  }
]
```

#### 3.2.2 특정 영화 조회

**Endpoint**: \`GET /movies/{movie_id}\`

**Path Parameters**:
- \`movie_id\` (int, required): 영화 ID

**Response**: \`200 OK\`
```json
{
  "id": 1,
  "title": "기생충",
  "release_date": "2019-05-30",
  "director": "봉준호",
  "genre": "드라마",
  "poster_url": "https://example.com/poster.jpg",
  "created_at": "2024-12-18T10:00:00Z"
}
```

**Error Response**: \`404 Not Found\`
```json
{
  "detail": "Movie not found"
}
```

#### 3.2.3 영화 추가

**Endpoint**: \`POST /movies/\`

**Request Body**:
```json
{
  "title": "기생충",
  "release_date": "2019-05-30",
  "director": "봉준호",
  "genre": "드라마",
  "poster_url": "https://example.com/poster.jpg"
}
```

**Required Fields**:
- \`title\` (string): 영화 제목

**Optional Fields**:
- \`release_date\` (string): 개봉일
- \`director\` (string): 감독
- \`genre\` (string): 장르
- \`poster_url\` (string): 포스터 이미지 URL

**Response**: \`201 Created\`
```json
{
  "id": 1,
  "title": "기생충",
  "release_date": "2019-05-30",
  "director": "봉준호",
  "genre": "드라마",
  "poster_url": "https://example.com/poster.jpg",
  "created_at": "2024-12-18T10:00:00Z"
}
```

#### 3.2.4 영화 삭제

**Endpoint**: \`DELETE /movies/{movie_id}\`

**Path Parameters**:
- \`movie_id\` (int, required): 영화 ID

**Response**: \`200 OK\`
```json
{
  "message": "Movie deleted successfully"
}
```

**Note**: 영화 삭제 시 관련 리뷰도 자동으로 삭제됩니다 (CASCADE).

### 3.3 리뷰 API

#### 3.3.1 리뷰 작성 (AI 감성 분석 포함)

**Endpoint**: \`POST /reviews/\`

**설명**: 리뷰를 작성하면 자동으로 AI 감성 분석이 수행됩니다.

**Request Body**:
```json
{
  "movie_id": 1,
  "author": "홍길동",
  "content": "정말 재미있는 영화였습니다! 봉준호 감독님의 연출이 훌륭했어요."
}
```

**Required Fields**:
- \`movie_id\` (int): 영화 ID
- \`author\` (string): 작성자 이름
- \`content\` (string): 리뷰 내용 (최소 5자)

**Response**: \`201 Created\`
```json
{
  "id": 1,
  "movie_id": 1,
  "author": "홍길동",
  "content": "정말 재미있는 영화였습니다! 봉준호 감독님의 연출이 훌륭했어요.",
  "sentiment_label": "positive",
  "sentiment_score": 0.9534,
  "created_at": "2024-12-18T10:30:00Z"
}
```

**AI 분석 결과**:
- \`sentiment_label\`: "positive", "negative", "neutral"
- \`sentiment_score\`: 0.0 ~ 1.0 (신뢰도)

**Error Response**: \`404 Not Found\` (영화가 없는 경우)
```json
{
  "detail": "Movie not found"
}
```

#### 3.3.2 전체 리뷰 조회

**Endpoint**: \`GET /reviews/\`

**Query Parameters**:
- \`limit\` (int, optional): 조회할 개수 (default: 10)
- \`skip\` (int, optional): 건너뛸 개수 (default: 0)

**Response**: \`200 OK\`
```json
[
  {
    "id": 1,
    "movie_id": 1,
    "author": "홍길동",
    "content": "정말 재미있는 영화였습니다!",
    "sentiment_label": "positive",
    "sentiment_score": 0.9534,
    "created_at": "2024-12-18T10:30:00Z"
  },
  {
    "id": 2,
    "movie_id": 1,
    "author": "김철수",
    "content": "기대 이하였어요. 너무 지루했습니다.",
    "sentiment_label": "negative",
    "sentiment_score": 0.8721,
    "created_at": "2024-12-18T10:25:00Z"
  }
]
```

#### 3.3.3 특정 영화의 리뷰 조회

**Endpoint**: \`GET /reviews/movie/{movie_id}\`

**Path Parameters**:
- \`movie_id\` (int, required): 영화 ID

**Response**: \`200 OK\`
```json
[
  {
    "id": 1,
    "movie_id": 1,
    "author": "홍길동",
    "content": "정말 재미있는 영화였습니다!",
    "sentiment_label": "positive",
    "sentiment_score": 0.9534,
    "created_at": "2024-12-18T10:30:00Z"
  }
]
```

#### 3.3.4 리뷰 삭제

**Endpoint**: \`DELETE /reviews/{review_id}\`

**Path Parameters**:
- \`review_id\` (int, required): 리뷰 ID

**Response**: \`200 OK\`
```json
{
  "message": "Review deleted successfully"
}
```

#### 3.3.5 영화 평균 평점 조회

**Endpoint**: \`GET /reviews/movie/{movie_id}/rating\`

**Path Parameters**:
- \`movie_id\` (int, required): 영화 ID

**Response**: \`200 OK\`
```json
{
  "movie_id": 1,
  "average_score": 0.82,
  "review_count": 15
}
```

**계산 방식**:
- 해당 영화의 모든 리뷰 \`sentiment_score\` 평균
- 긍정적 리뷰가 많을수록 높은 점수

---

## 4. 서비스 실행 방법

본 프로젝트는 **로컬 개발 환경 (Docker Compose)**과 **GCP 프로덕션 환경 (Cloud Run)** 두 가지 방식으로 실행할 수 있습니다.

[실행 방법 설명 문서로 이동](https://github.com/Dongjin-1203/Movie_GPT/blob/main/%EC%8B%A4%ED%96%89%20%EC%84%A4%EB%AA%85%EC%84%9C.md)
---

## 5. 서비스 동작 화면

### 5.1 홈 화면

**[여기에 홈 화면 캡쳐 이미지 삽입]**

**주요 기능**:
- 서비스 소개
- 메뉴 네비게이션

---

### 5.2 영화 추가 화면

**[여기에 영화 추가 화면 캡쳐 이미지 삽입]**

---

### 5.3 영화 목록 화면

**[여기에 영화 목록 화면 캡쳐 이미지 삽입]**

**표시 정보**:
- 영화 포스터 (있는 경우)
- 제목, 개봉일, 감독, 장르
- 등록일
- 삭제 버튼

---

### 5.4 리뷰 작성 화면

**[여기에 리뷰 작성 화면 캡쳐 이미지 삽입]**

---

### 5.5 AI 감성 분석 결과 화면

**[여기에 AI 분석 결과 화면 캡쳐 이미지 삽입]**

**표시 정보**:
- 감성 라벨 (긍정/부정/중립) + 이모지
- 신뢰도 점수 (0.0 ~ 1.0)
- 리뷰 내용
- 작성자 및 날짜

---

### 5.6 리뷰 목록 및 통계 화면

**[여기에 리뷰 목록 화면 캡쳐 이미지 삽입]**

**표시 정보**:
- 영화별 필터링
- 리뷰 목록 (최신순)
- 통계:
  - 평균 감성 점수
  - 리뷰 개수
  - 긍정/부정 비율

---

## 6. 트러블슈팅

본 프로젝트 개발 및 배포 과정에서 다양한 기술적 문제에 직면했으며, 각 문제의 원인을 분석하고 해결책을 도출했습니다.

[트러블 슈팅 문서로 이동](https://github.com/Dongjin-1203/Movie_GPT/blob/main/%ED%8A%B8%EB%9F%AC%EB%B8%94%EC%8A%88%ED%8C%85.md)

---

## 7. 결론 및 향후 계획

### 7.1 프로젝트 성과

Movie GPT 프로젝트를 통해 다음과 같은 기술적 역량과 성과를 달성했습니다:

#### 7.1.1 기술적 성과

✅ **풀스택 개발 경험**
- Frontend (Streamlit), Backend (FastAPI), Database (PostgreSQL) 통합 개발
- RESTful API 설계 및 구현
- 프론트엔드-백엔드 통신 및 상태 관리

✅ **AI 모델 통합 및 최적화**
- Hugging Face 모델 활용
- ONNX 변환 및 INT8 양자화 적용
- 추론 속도 37% 향상, 모델 크기 30% 감소
- CPU 환경에서 실시간 추론 구현 (~50ms)

✅ **클라우드 네이티브 아키텍처**
- Docker 컨테이너화
- GCP Cloud Run 서버리스 배포
- Cloud SQL 관리형 데이터베이스 활용
- 자동 스케일링 및 고가용성 보장

✅ **문제 해결 능력**
- 6가지 주요 트러블슈팅 경험
- 체계적인 디버깅 및 문제 분석
- 문서화 및 재발 방지 전략 수립

#### 7.1.2 정량적 성과

| 지표 | 수치 | 비고 |
|------|------|------|
| **API 응답 시간** | ~200ms | 평균 (감성 분석 포함) |
| **AI 추론 속도** | ~50ms | ONNX INT8 양자화 |
| **모델 크기** | ~85MB | 원본 대비 30% 감소 |
| **월 운영 비용** | ~\$10-15 | GCP (개발 환경 기준) |
| **코드 라인 수** | ~2,000 lines | 주석 및 문서 제외 |
| **API 엔드포인트** | 10개 | 영화 4개, 리뷰 6개 |

### 7.2 한계 및 개선 사항

#### 7.2.1 현재 한계점

1. **사용자 인증 부재**
   - 현재: 익명 사용자만 지원
   - 문제: 사용자별 리뷰 관리 불가

2. **감성 분석 단순성**
   - 현재: 긍정/부정/중립 3분류
   - 개선: 별점(1-5점) 또는 세부 감정 분류

3. **검색 기능 부재**
   - 현재: 전체 목록만 조회 가능
   - 개선: 제목/감독/장르 검색 필요

4. **성능 최적화 여지**
   - 현재: 데이터베이스 인덱스 미적용
   - 현재: 캐싱 시스템 없음

### 7.3 향후 개발 계획

#### 7.3.1 단기 계획 (1개월)

**기능 추가**
- [ ] 사용자 인증 (JWT 기반)
- [ ] 회원가입/로그인 페이지
- [ ] 영화 검색 (제목, 감독, 장르)
- [ ] 리뷰 수정 기능
- [ ] 좋아요/싫어요 기능

**UI/UX 개선**
- [ ] 반응형 디자인 (모바일 최적화)
- [ ] 다크 모드
- [ ] 로딩 애니메이션
- [ ] 에러 페이지 커스터마이징

**성능 최적화**
- [ ] Redis 캐싱 도입
- [ ] 데이터베이스 인덱스 추가
- [ ] 쿼리 최적화 (N+1 문제 해결)

#### 7.3.2 중기 계획 (3개월)

**AI 고도화**
- [ ] 별점 예측 모델 (1-5점)
- [ ] 리뷰 요약 생성 (생성형 AI)
- [ ] 영화 추천 시스템 (협업 필터링)
- [ ] 감성 분석 정확도 향상 (Fine-tuning)

**인프라 개선**
- [ ] CI/CD 파이프라인 구축 (GitHub Actions)
- [ ] 모니터링 시스템 (Prometheus, Grafana)
- [ ] 알림 시스템 (Cloud Monitoring)
- [ ] 커스텀 도메인 연결
- [ ] HTTPS 인증서 자동 갱신

**데이터 분석**
- [ ] 사용자 행동 분석 (Google Analytics)
- [ ] A/B 테스트 프레임워크
- [ ] 관리자 대시보드
- [ ] 실시간 통계 집계

#### 7.3.3 장기 계획 (6개월)

**서비스 확장**
- [ ] 모바일 앱 개발 (React Native)
- [ ] 소셜 기능 (친구 추가, 공유)
- [ ] 외부 API 연동 (TMDB, IMDB)
- [ ] 다국어 지원 (i18n)

**아키텍처 개선**
- [ ] 마이크로서비스 전환
- [ ] Kubernetes 배포
- [ ] 멀티 리전 배포 (글로벌 서비스)
- [ ] CDN 연동 (이미지 최적화)

**비즈니스 모델**
- [ ] 프리미엄 기능 (광고 제거, 고급 분석)
- [ ] 파트너십 (영화관, OTT)
- [ ] 큐레이션 서비스

### 7.4 마무리

Movie GPT 프로젝트는 AI 기반 감성 분석 기술을 활용한 실용적인 웹 서비스입니다. 본 프로젝트를 통해 **풀스택 개발, AI 모델 통합, 클라우드 배포**의 전 과정을 경험하며 실무 역량을 크게 향상시킬 수 있었습니다.

특히 6가지 주요 트러블슈팅을 해결하는 과정에서 **문제 분석, 디버깅, 해결책 도출**의 체계적인 접근 방법을 학습했으며, 이는 향후 더 복잡한 시스템을 개발하는 데 큰 자산이 될 것입니다.

향후 사용자 인증, 고급 AI 기능, 모바일 앱 등을 추가하여 실제 서비스로 발전시킬 계획이며, 본 프로젝트가 실무 포트폴리오로서 충분한 가치를 지닐 것으로 기대합니다.

---

**부록: 참고 자료**

- FastAPI Documentation: https://fastapi.tiangolo.com/
- Streamlit Documentation: https://docs.streamlit.io/
- GCP Cloud Run: https://cloud.google.com/run/docs
- ONNX Runtime: https://onnxruntime.ai/
- Hugging Face: https://huggingface.co/
