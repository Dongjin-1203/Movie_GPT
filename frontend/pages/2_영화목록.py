import streamlit as st
import requests
import os

st.set_page_config(page_title="영화 목록", page_icon="🎬", layout="wide")

BASE_URL = os.getenv("BASE_URL", "http://backend:8000")

import sys
sys.path.append('/app')  # Docker 경로

from components.chatbot import render_chatbot_button

def get_all_movies():
    """전체 영화 목록 가져오기"""
    try:
        response = requests.get(f"{BASE_URL}/movies/", timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"❌ 영화 목록 조회 실패: {str(e)}")
        return []


def delete_movie(movie_id: int):
    """영화 삭제"""
    try:
        response = requests.delete(f"{BASE_URL}/movies/{movie_id}", timeout=10)
        return response.status_code == 200
    except Exception as e:
        st.error(f"❌ 삭제 실패: {str(e)}")
        return False

# 메인 UI
st.title("🎬 영화 목록")
st.markdown("---")

# 영화 목록 가져오기
with st.spinner("📥 영화 목록을 불러오는 중..."):
    movies = get_all_movies()

if not movies:
    st.info("📭 등록된 영화가 없습니다. '영화 추가' 페이지에서 영화를 추가해보세요!")
    st.stop()

# 통계
st.success(f"✅ 총 {len(movies)}개의 영화가 등록되어 있습니다")

# 정렬 옵션
col1, col2 = st.columns([3, 1])
with col2:
    sort_option = st.selectbox(
        "정렬",
        ["최신순", "제목순", "평점순"],
        label_visibility="collapsed"
    )

# 정렬
if sort_option == "제목순":
    movies = sorted(movies, key=lambda x: x.get("title", ""))
elif sort_option == "평점순":
    movies = sorted(movies, key=lambda x: x.get("rating", 0), reverse=True)
else:  # 최신순 (기본)
    movies = sorted(movies, key=lambda x: x.get("id", 0), reverse=True)

st.markdown("---")

# 영화 카드 표시
for movie in movies:
    # 안전하게 데이터 가져오기
    movie_id = movie.get("id", 0)
    title = movie.get("title", "제목 없음")
    director = movie.get("director", "감독 미상")
    genre = movie.get("genre", "장르 미상")
    release_date = movie.get("release_date", "")
    actors = movie.get("actors", "")
    plot_summary = movie.get("plot_summary", "")
    poster_url = movie.get("poster_url")
    rating = movie.get("rating", 0.0)
    review_count = movie.get("review_count", 0)
    tmdb_id = movie.get("tmdb_id")
    
    # 카드 레이아웃
    col1, col2, col3 = st.columns([1, 4, 1])
    
    with col1:
        # 포스터
        if poster_url:
            st.image(poster_url, use_container_width=True)
        else:
            st.markdown("### 🎬")
    
    with col2:
        # 제목
        st.subheader(f"🎬 {title}")
        
        # 기본 정보
        info_parts = []
        if release_date:
            year = release_date[:4] if len(release_date) >= 4 else release_date
            info_parts.append(f"📅 {year}")
        if director:
            info_parts.append(f"🎥 {director}")
        if genre:
            info_parts.append(f"🎭 {genre}")
        
        if info_parts:
            st.caption(" | ".join(info_parts))
        
        # 배우
        if actors:
            st.caption(f"👥 출연: {actors}")
        
        # 평점 및 리뷰
        col_rating, col_reviews = st.columns(2)
        with col_rating:
            if rating > 0:
                stars = "⭐" * min(int(rating * 5), 5)
                st.caption(f"{stars} {rating:.2f}/1.0")
            else:
                st.caption("⭐ 평점 없음")
        
        with col_reviews:
            st.caption(f"💬 리뷰 {review_count}개")
        
        # 줄거리
        if plot_summary:
            with st.expander("📖 줄거리 보기"):
                st.write(plot_summary)
        
        # TMDB 정보
        if tmdb_id:
            st.caption(f"🎬 TMDB ID: {tmdb_id}")
    
    with col3:
        st.write("")
        st.write("")
        
        # 삭제 버튼
        if st.button("🗑️ 삭제", key=f"delete_{movie_id}", use_container_width=True):
            if delete_movie(movie_id):
                st.success("✅ 삭제 완료!")
                st.rerun()
    
    st.markdown("---")

# 사이드바
with st.sidebar:
    st.header("📊 통계")
    st.metric("등록된 영화", f"{len(movies)}개")
    
    if movies:
        # 평점 있는 영화
        rated_movies = [m for m in movies if m.get("rating", 0) > 0]
        if rated_movies:
            avg_rating = sum(m.get("rating", 0) for m in rated_movies) / len(rated_movies)
            st.metric("평균 평점", f"{avg_rating:.2f}/1.0")
        
        # 리뷰 있는 영화
        reviewed_movies = [m for m in movies if m.get("review_count", 0) > 0]
        st.metric("리뷰 있는 영화", f"{len(reviewed_movies)}개")
        
        # 총 리뷰 수
        total_reviews = sum(m.get("review_count", 0) for m in movies)
        st.metric("총 리뷰 수", f"{total_reviews}개")
    
    st.markdown("---")
    
    st.header("💡 사용 팁")
    st.markdown("""
    - 정렬 옵션으로 원하는 순서로 볼 수 있습니다
    - 줄거리 보기를 클릭하면 상세 내용을 볼 수 있습니다
    - 삭제 버튼으로 영화를 제거할 수 있습니다
    """)

render_chatbot_button()