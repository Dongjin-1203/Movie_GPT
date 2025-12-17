# Movie_GPT
---
## 개발 배경
우리는 영화를 선택할때 많은 어려움이 있다. 특히 이 영화가 재미있는지가 굉장히 중요하다. 비싼 돈 주고 보는데 좀 더 나은 선택을 할 수 있도록 도움을 주는 서비스가 있으면 좋을 것 같아 개발하게 되었다.

## 프로젝트 디렉토리 구조
```
Movie_GPT/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # FastAPI 앱
│   │   ├── database.py      # DB 연결
│   │   ├── models.py        # SQLAlchemy 모델
│   │   ├── schemas.py       # Pydantic 스키마
│   │   └── routers/
│   │       └── movies.py    # 영화 CRUD API
│   └── requirements.txt
│
└── frontend/
    ├── app.py               # Streamlit 메인
    ├── pages/
    │   ├── 1_영화목록.py
    │   └── 2_영화추가.py
    ├── utils/
    │   └── api_client.py    # API 호출 래퍼
    └── requirements.txt
```