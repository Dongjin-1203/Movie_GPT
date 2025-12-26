# frontend/app.py
import streamlit as st
import requests
import os

st.set_page_config(
    page_title="Movie GPT - AI 영화 리뷰 플랫폼",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE_URL = os.getenv("BASE_URL", "http://backend:8000")


def get_movies(limit=None):
    """영화 목록 가져오기"""
    try:
        response = requests.get(f"{BASE_URL}/movies/", timeout=10)
        if response.status_code == 200:
            movies = response.json()
            return movies[:limit] if limit else movies
        return []
    except:
        return []


def get_reviews(limit=None):
    """리뷰 목록 가져오기"""
    try:
        response = requests.get(f"{BASE_URL}/reviews/", timeout=10)
        if response.status_code == 200:
            reviews = response.json()
            return reviews[:limit] if limit else reviews
        return []
    except:
        return []


# ========================================
# Hero Section
# ========================================
st.markdown("""
<div style='text-align: center; padding: 2rem 0;'>
    <h1 style='font-size: 3.5rem; margin-bottom: 0.5rem;'>🎬 Movie GPT</h1>
    <p style='font-size: 1.3rem; color: #666;'>AI 기반 영화 리뷰 플랫폼</p>
    <p style='font-size: 1rem; color: #999;'>영화를 검색하고, 리뷰를 작성하고, AI가 감성을 분석합니다</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# ========================================
# 통계 대시보드
# ========================================
st.subheader("📊 현황")

movies = get_movies()
reviews = get_reviews()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="등록된 영화",
        value=f"{len(movies)}개",
        delta="TMDB 연동" if movies else None
    )

with col2:
    st.metric(
        label="전체 리뷰",
        value=f"{len(reviews)}개",
        delta="AI 분석" if reviews else None
    )

with col3:
    if movies:
        avg_rating = sum(m.get('rating', 0) for m in movies) / len(movies)
        st.metric(
            label="평균 평점",
            value=f"{avg_rating:.2f}",
            delta="⭐" * int(avg_rating * 5)
        )
    else:
        st.metric(label="평균 평점", value="0.00")

with col4:
    reviewed_movies = len([m for m in movies if m.get('review_count', 0) > 0])
    st.metric(
        label="리뷰 있는 영화",
        value=f"{reviewed_movies}개",
        delta=f"{reviewed_movies}/{len(movies)}" if movies else None
    )

st.markdown("---")

# ========================================
# 최근 등록 영화 미리보기
# ========================================
st.subheader("🎥 최근 등록 영화")

recent_movies = get_movies(limit=3)

if recent_movies:
    cols = st.columns(3)
    
    for idx, movie in enumerate(recent_movies):
        with cols[idx]:
            if movie.get('poster_url'):
                st.image(movie['poster_url'], use_container_width=True)
            else:
                st.markdown("### 🎬")
            
            st.markdown(f"**{movie.get('title', '제목 없음')}**")
            
            if movie.get('rating', 0) > 0:
                rating = movie['rating']
                stars = "⭐" * int(rating * 5)
                st.caption(f"{stars} {rating:.2f}")
            
            if movie.get('director'):
                st.caption(f"🎥 {movie['director']}")
    
    # 더보기 버튼
    if st.button("➡️ 전체 영화 보기", key="view_all_movies", use_container_width=True):
        st.switch_page("pages/2_영화목록.py")
else:
    st.info("아직 등록된 영화가 없습니다. 영화를 추가해보세요!")

st.markdown("---")

# ========================================
# 최근 리뷰 미리보기
# ========================================
st.subheader("💬 최근 리뷰")

recent_reviews = get_reviews(limit=5)

if recent_reviews:
    for review in recent_reviews:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"**{review.get('author', '익명')}**")
                content = review.get('content', '')
                preview = content[:100] + "..." if len(content) > 100 else content
                st.caption(preview)
            
            with col2:
                sentiment = review.get('sentiment_label', '')
                score = review.get('sentiment_score', 0)
                
                if sentiment == 'positive':
                    st.success(f"😊 {score:.2f}")
                elif sentiment == 'negative':
                    st.error(f"😞 {score:.2f}")
                else:
                    st.info(f"😐 {score:.2f}")
            
            st.markdown("---")
    
    # 더보기 버튼
    if st.button("➡️ 전체 리뷰 보기", key="view_all_reviews", use_container_width=True):
        st.switch_page("pages/4_리뷰목록.py")
else:
    st.info("아직 작성된 리뷰가 없습니다. 첫 리뷰를 작성해보세요!")

st.markdown("---")

# ========================================
# 빠른 액션 버튼
# ========================================
st.subheader("⚡ 빠른 시작")

col1, col2 = st.columns(2)

with col1:
    if st.button("➕ 영화 추가하기", type="primary", use_container_width=True, key="add_movie"):
        st.switch_page("pages/1_영화추가.py")

with col2:
    if st.button("✍️ 리뷰 작성하기", type="primary", use_container_width=True, key="write_review"):
        st.switch_page("pages/3_리뷰작성.py")

st.markdown("---")

# ========================================
# 전체 영화 갤러리
# ========================================
st.subheader("🎞️ 영화 갤러리")

all_movies = get_movies()

if all_movies:
    # 정렬 옵션
    sort_option = st.selectbox(
        "정렬",
        ["최신순", "평점순", "제목순"],
        label_visibility="collapsed",
        key="gallery_sort"
    )
    
    if sort_option == "평점순":
        all_movies = sorted(all_movies, key=lambda x: x.get('rating', 0), reverse=True)
    elif sort_option == "제목순":
        all_movies = sorted(all_movies, key=lambda x: x.get('title', ''))
    else:
        all_movies = sorted(all_movies, key=lambda x: x.get('id', 0), reverse=True)
    
    # 그리드 레이아웃 (4열)
    num_cols = 4
    rows = [all_movies[i:i + num_cols] for i in range(0, len(all_movies), num_cols)]
    
    for row in rows:
        cols = st.columns(num_cols)
        
        for idx, movie in enumerate(row):
            with cols[idx]:
                # 포스터
                if movie.get('poster_url'):
                    st.image(movie['poster_url'], use_container_width=True)
                else:
                    st.markdown("""
                    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                height: 300px; 
                                display: flex; 
                                align-items: center; 
                                justify-content: center; 
                                border-radius: 8px;'>
                        <span style='font-size: 4rem;'>🎬</span>
                    </div>
                    """, unsafe_allow_html=True)
                
                # 제목
                title = movie.get('title', '제목 없음')
                st.markdown(f"**{title[:20]}{'...' if len(title) > 20 else ''}**")
                
                # 평점
                rating = movie.get('rating', 0)
                if rating > 0:
                    stars = "⭐" * min(int(rating * 5), 5)
                    st.caption(f"{stars} {rating:.2f}")
                else:
                    st.caption("⭐ 평점 없음")
                
                # 리뷰 개수
                review_count = movie.get('review_count', 0)
                st.caption(f"💬 리뷰 {review_count}개")
else:
    st.info("등록된 영화가 없습니다. 첫 영화를 추가해보세요!")
    
    if st.button("🎬 영화 추가하러 가기", type="primary", use_container_width=True):
        st.switch_page("pages/1_영화추가.py")

# ========================================
# 사이드바
# ========================================
with st.sidebar:
    st.header("🎬 Movie GPT")
    
    st.markdown("""
    ### 주요 기능
    
    - 🔍 **영화 검색**: TMDB API로 빠른 검색
    - 📝 **리뷰 작성**: AI 감성 분석
    - 📊 **통계 확인**: 평점 및 리뷰 현황
    - 🎯 **영화 추천**: 취향 기반 추천 (예정)
    """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 📖 사용 가이드
    
    1. **영화 추가**: TMDB에서 검색하여 추가
    2. **리뷰 작성**: 영화 선택 후 의견 작성
    3. **AI 분석**: 자동으로 감성 분석
    4. **통계 확인**: 평점 및 리뷰 확인
    """)
    
    st.markdown("---")
    
    # 통계
    if movies or reviews:
        st.metric("총 영화", f"{len(movies)}개")
        st.metric("총 리뷰", f"{len(reviews)}개")
        
        if movies:
            avg = sum(m.get('rating', 0) for m in movies) / len(movies)
            st.metric("평균 평점", f"{avg:.2f}")

# ========================================
# 챗봇 버튼 추가
# ========================================
from components.chatbot import render_chatbot_button

render_chatbot_button()