"""
사용자가 새로운 영화를 추가할 수 있는 폼

필수 입력:
- 제목 (title)

선택 입력:
- 개봉일 (release_date)
- 감독 (director)
- 장르 (genre)
- 포스터 URL (poster_url)
"""

import streamlit as st
from utils.api_client import client

# 페이지 제목
st.title("🎬 영화 추가")
st.write("새로운 영화 정보를 입력하세요")

# 폼 생성 (입력 필드들을 그룹화)
with st.form("movie_form"):
    
    # 1. 제목 입력 (필수)
    title = st.text_input(
        "제목 *",
        placeholder="예: 기생충",
        help="필수 입력 항목입니다"
    )
    
    # 2. 개봉일 입력 (선택)
    release_date = st.date_input(
        "개봉일",
        value=None,
        help="선택 사항입니다"
    )
    
    # 3. 감독 입력 (선택)
    director = st.text_input(
        "감독",
        placeholder="예: 봉준호"
    )
    
    # 4. 장르 선택 (선택)
    genre = st.selectbox(
        "장르",
        options=[
            "",  # 빈 값
            "액션",
            "코미디",
            "드라마",
            "스릴러",
            "SF",
            "로맨스",
            "애니메이션",
            "공포",
            "판타지",
            "다큐멘터리"
        ]
    )
    
    # 5. 포스터 URL 입력 (선택)
    poster_url = st.text_input(
        "포스터 URL",
        placeholder="https://example.com/poster.jpg"
    )
    
    # 제출 버튼
    submitted = st.form_submit_button("등록하기", type="primary")

# 폼 제출 처리
if submitted:
    # 필수 항목 검증
    if title.strip() == "":
        st.error("❌ 제목은 필수 입력 항목입니다!")
    else:
        # API 요청 데이터 구성
        movie_data = {
            "title": title.strip(),
            "release_date": str(release_date) if release_date else None,
            "director": director.strip() if director else None,
            "genre": genre if genre else None,
            "poster_url": poster_url.strip() if poster_url else None
        }
        
        # API 호출
        result = client.create_movie(movie_data)
        
        # 결과 처리
        if result:
            st.success(f"✅ '{title}' 영화가 성공적으로 등록되었습니다!")
            st.balloons()  # 축하 애니메이션
            
            # 등록된 영화 정보 표시
            st.subheader("등록된 영화 정보")
            st.json(result)
        else:
            st.error("❌ 영화 등록에 실패했습니다. 다시 시도해주세요.")