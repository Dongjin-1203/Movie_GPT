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

import requests
import os
import streamlit as st
from typing import List, Dict, Any

from utils.api_client import client

st.set_page_config(page_title="영화 추가", page_icon="🎬", layout="wide")

BASE_URL = os.getenv("BASE_URL", "http://backend:8000")

def search_movies(query: str) -> List[Dict[str, Any]]:
    """TMDB에서 영화 검색"""
    try:
        response = requests.get(
            f"{BASE_URL}/movies/search",
            params={"query": query},
            timeout=5
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"❌ 검색 실패: {str(e)}")
        return []


def add_movie_from_tmdb(tmdb_id: int) -> bool:
    """TMDB에서 영화 추가"""
    try:
        response = requests.post(
            f"{BASE_URL}/movies/from-tmdb/{tmdb_id}",
            timeout=10
        )
        if response.status_code == 201:
            return True
        elif response.status_code == 400:
            st.warning("⚠️ 이미 등록된 영화입니다")
            return False
        else:
            st.error(f"❌ 추가 실패 (코드: {response.status_code})")
            return False
    except Exception as e:
        st.error(f"❌ 추가 실패: {str(e)}")
        return False

# 페이지 제목
st.title("🎬 영화 추가")
st.write("새로운 영화 정보를 입력하세요")

# 탭으로 구분
tab1, tab2 = st.tabs(["🔍 영화 검색 (추천)", "✍️ 수동 입력"])


# ========================================
# Tab 1: TMDB 검색
# ========================================
with tab1:
    st.header("영화 검색")
    st.caption("제목을 입력하면 자동으로 검색됩니다 (2글자 이상)")
    
    # 검색 입력
    search_query = st.text_input(
        "🔎 영화 제목",
        placeholder="예: 기생충, 올드보이, 극한직업...",
        key="search_input",
        label_visibility="collapsed"
    )
    
    # 실시간 검색
    if search_query and len(search_query) >= 2:
        with st.spinner("🔍 검색 중..."):
            results = search_movies(search_query)
        
        if results:
            st.success(f"✅ {len(results)}개의 영화를 찾았습니다")
            st.markdown("---")
            
            # 검색 결과 표시
            for idx, movie in enumerate(results):
                col1, col2, col3 = st.columns([1, 4, 1])
                
                with col1:
                    # 포스터 이미지
                    if movie.get("poster_path"):
                        st.image(movie["poster_path"], use_container_width=True)
                    else:
                        st.markdown("### 🎬")
                
                with col2:
                    # 영화 제목
                    st.subheader(movie["title"])
                    
                    # 정보 표시
                    info_parts = []
                    if movie.get("original_title") and movie["original_title"] != movie["title"]:
                        info_parts.append(f"*{movie['original_title']}*")
                    if movie.get("release_date"):
                        info_parts.append(f"📅 {movie['release_date'][:4]}")
                    if movie.get("vote_average"):
                        rating = movie['vote_average']
                        stars = "⭐" * int(rating / 2)
                        info_parts.append(f"{stars} {rating:.1f}/10")
                    
                    if info_parts:
                        st.caption(" | ".join(info_parts))
                    
                    # 줄거리
                    if movie.get("overview"):
                        with st.expander("📖 줄거리 보기"):
                            st.write(movie["overview"])
                    else:
                        st.caption("*줄거리 정보 없음*")
                
                with col3:
                    # 간격
                    st.write("")
                    st.write("")
                    
                    # 추가 버튼
                    if st.button(
                        "➕ 추가",
                        key=f"add_{movie['tmdb_id']}_{idx}",
                        type="primary",
                        use_container_width=True
                    ):
                        with st.spinner("추가 중..."):
                            if add_movie_from_tmdb(movie["tmdb_id"]):
                                st.success(f"✅ '{movie['title']}' 추가 완료!")
                                st.balloons()
                                st.rerun()
                
                st.markdown("---")
        
        else:
            st.info("📭 검색 결과가 없습니다. 다른 제목으로 시도해보세요.")
    
    elif search_query and len(search_query) < 2:
        st.info("💡 2글자 이상 입력해주세요")

# ========================================
# Tab 2: 수동 입력
# ========================================
with tab2:
    st.header("수동 입력")
    st.caption("TMDB에 없는 영화는 직접 입력할 수 있습니다")
    
    with st.form("manual_movie_form"):
        title = st.text_input("영화 제목*", placeholder="예: 기생충")
        
        col1, col2 = st.columns(2)
        with col1:
            release_date = st.text_input("개봉일", placeholder="YYYY-MM-DD")
            director = st.text_input("감독", placeholder="예: 봉준호")
        with col2:
            genre = st.text_input("장르", placeholder="예: 드라마")
            actors = st.text_input("주연 배우", placeholder="예: 송강호, 이선균")
        
        poster_url = st.text_input("포스터 URL", placeholder="https://...")
        plot_summary = st.text_area("줄거리", placeholder="영화 줄거리를 입력하세요...")
        
        submitted = st.form_submit_button("➕ 영화 추가", type="primary", use_container_width=True)
        
        if submitted:
            if not title:
                st.error("❌ 제목은 필수입니다")
            else:
                movie_data = {
                    "title": title,
                    "release_date": release_date if release_date else None,
                    "director": director if director else None,
                    "genre": genre if genre else None,
                    "actors": actors if actors else None,
                    "poster_url": poster_url if poster_url else None,
                    "plot_summary": plot_summary if plot_summary else None
                }
                
                try:
                    response = requests.post(
                        f"{BASE_URL}/movies/",
                        json=movie_data,
                        timeout=10
                    )
                    
                    if response.status_code == 201:
                        st.success(f"✅ '{title}' 추가 완료!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ 추가 실패 (코드: {response.status_code})")
                except Exception as e:
                    st.error(f"❌ 추가 실패: {str(e)}")

# ========================================
# 사이드바 (사용 가이드)
# ========================================
with st.sidebar:
    st.header("💡 사용 가이드")
    
    st.markdown("""
    ### 🔍 검색 방법
    1. 영화 제목 입력 (2글자 이상)
    2. 검색 결과 확인
    3. "추가" 버튼 클릭
    
    ### ✨ 장점
    - ⚡ **10초 만에 추가**
    - 📸 포스터 자동
    - 📝 정보 자동 완성
    - 🎭 배우/감독 자동
    - 📖 줄거리 자동
    
    ### 💾 수동 입력
    TMDB에 없는 영화는  
    "수동 입력" 탭에서  
    직접 추가할 수 있습니다.
    """)
    
    st.markdown("---")
    
    # 통계 표시
    try:
        movies_response = requests.get(f"{BASE_URL}/movies/", timeout=5)
        if movies_response.status_code == 200:
            movies = movies_response.json()
            st.metric("📊 등록된 영화", f"{len(movies)}개")
    except:
        pass

import sys
sys.path.append('/app')  # Docker 경로

from components.chatbot import render_chatbot_button

render_chatbot_button()