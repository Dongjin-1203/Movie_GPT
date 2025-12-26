# frontend/pages/3_리뷰작성.py
import streamlit as st
import requests
import os

st.set_page_config(page_title="리뷰 작성", page_icon="✍️", layout="wide")

BASE_URL = os.getenv("BASE_URL", "http://backend:8000")


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


def create_review(movie_id: int, author: str, content: str):
    """리뷰 작성"""
    try:
        response = requests.post(
            f"{BASE_URL}/reviews/",
            json={
                "movie_id": movie_id,
                "author": author,
                "content": content
            },
            timeout=10
        )
        if response.status_code == 201:
            return True, response.json()
        else:
            return False, None
    except Exception as e:
        st.error(f"❌ 리뷰 작성 실패: {str(e)}")
        return False, None


# 세션 상태 초기화
if 'review_submitted' not in st.session_state:
    st.session_state.review_submitted = False
if 'review_data' not in st.session_state:
    st.session_state.review_data = None


# 메인 UI
st.title("✍️ 리뷰 작성")
st.markdown("---")

# 영화 목록 가져오기
with st.spinner("📥 영화 목록을 불러오는 중..."):
    movies = get_all_movies()

if not movies:
    st.warning("⚠️ 등록된 영화가 없습니다.")
    st.info("💡 '영화 추가' 페이지에서 먼저 영화를 추가해주세요.")
    st.stop()

# 영화 선택
st.subheader("🎬 영화 선택")

movie_options = {}
for movie in movies:
    title = movie.get('title', '제목 없음')
    year = movie.get('release_date', '')[:4] if movie.get('release_date') else '?'
    label = f"{title} ({year})"
    movie_options[label] = movie.get('id')

selected_movie_label = st.selectbox(
    "영화를 선택하세요",
    options=list(movie_options.keys()),
    label_visibility="collapsed"
)

selected_movie_id = movie_options[selected_movie_label]
selected_movie = next((m for m in movies if m.get("id") == selected_movie_id), None)

# 선택된 영화 정보 표시
if selected_movie:
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if selected_movie.get("poster_url"):
            st.image(selected_movie["poster_url"], use_container_width=True)
        else:
            st.markdown("### 🎬")
    
    with col2:
        st.markdown(f"### {selected_movie.get('title', '제목 없음')}")
        
        info_parts = []
        if selected_movie.get("director"):
            info_parts.append(f"🎥 {selected_movie['director']}")
        if selected_movie.get("genre"):
            info_parts.append(f"🎭 {selected_movie['genre']}")
        if selected_movie.get("release_date"):
            info_parts.append(f"📅 {selected_movie['release_date'][:4]}")
        
        if info_parts:
            st.caption(" | ".join(info_parts))
        
        if selected_movie.get("actors"):
            st.caption(f"👥 출연: {selected_movie['actors']}")

st.markdown("---")

# 리뷰 작성 폼
st.subheader("✍️ 리뷰 작성")

# 🔥 Form 시작
with st.form("review_form", clear_on_submit=True):
    author = st.text_input(
        "작성자 이름*",
        placeholder="예: 홍길동",
        help="리뷰 작성자의 이름을 입력하세요"
    )
    
    content = st.text_area(
        "리뷰 내용*",
        placeholder="영화에 대한 솔직한 의견을 작성해주세요...\n\n예:\n- 연기가 정말 인상적이었어요\n- 스토리가 흥미진진했습니다\n- 영상미가 뛰어났어요",
        height=200,
        help="최소 5자 이상 작성해주세요"
    )
    
    st.caption("💡 **작성 팁**: AI가 자동으로 감성을 분석합니다. 솔직하고 구체적으로 작성할수록 정확도가 높아집니다.")
    
    # Form 안에서는 form_submit_button만 사용!
    submitted = st.form_submit_button(
        "📝 리뷰 등록",
        type="primary",
        use_container_width=True
    )
    
    if submitted:
        if not author or not author.strip():
            st.error("❌ 작성자 이름을 입력해주세요")
        elif not content or not content.strip():
            st.error("❌ 리뷰 내용을 입력해주세요")
        elif len(content.strip()) < 5:
            st.error("❌ 리뷰 내용은 최소 5자 이상 작성해주세요")
        else:
            with st.spinner("🤖 AI가 감성을 분석 중입니다..."):
                success, review_data = create_review(
                    selected_movie_id,
                    author.strip(),
                    content.strip()
                )
            
            if success:
                st.session_state.review_submitted = True
                st.session_state.review_data = review_data
                st.rerun()
# 🔥 Form 끝 - 이 줄 이후부터 일반 버튼 사용 가능!

# 🔥 Form 밖에서 결과 표시
if st.session_state.review_submitted and st.session_state.review_data:
    st.success("✅ 리뷰가 성공적으로 등록되었습니다!")
    st.balloons()
    
    review_data = st.session_state.review_data
    st.markdown("---")
    st.subheader("📊 감성 분석 결과")
    
    sentiment_label = review_data.get("sentiment_label", "알 수 없음")
    sentiment_score = review_data.get("sentiment_score", 0)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if sentiment_label == "positive":
            st.success("😊 긍정적인 리뷰입니다")
        elif sentiment_label == "negative":
            st.error("😞 부정적인 리뷰입니다")
        else:
            st.info("😐 중립적인 리뷰입니다")
    
    with col2:
        st.metric("감성 점수", f"{sentiment_score:.2f}")
    
    st.caption("💡 감성 점수는 0(부정)부터 1(긍정)까지의 값입니다")
    
    # 🔥 이제 Form 밖이므로 일반 버튼 사용 가능!
    st.markdown("---")
    if st.button("🔄 다른 영화 리뷰 작성하기", type="secondary"):
        st.session_state.review_submitted = False
        st.session_state.review_data = None
        st.rerun()

# 사이드바
with st.sidebar:
    st.header("💡 리뷰 작성 가이드")
    
    st.markdown("""
    ### ✍️ 좋은 리뷰 작성법
    
    **구체적으로 작성하세요:**
    - ✅ "연기가 훌륭했다"
    - ✅ "스토리가 흥미진진했다"
    - ❌ "좋았다", "별로"
    
    **솔직하게 작성하세요:**
    - 장점과 단점을 균형있게
    - 개인적인 감상 포함
    
    **스포일러 주의:**
    - 핵심 반전은 피해주세요
    - 결말 언급 시 주의 표시
    """)
    
    st.markdown("---")
    
    st.header("🤖 AI 감성 분석")
    st.markdown("""
    작성된 리뷰는 AI가 자동으로 분석하여:
    - 😊 긍정 / 😞 부정 / 😐 중립 분류
    - 0-1 사이의 감성 점수 부여
    
    이 정보는 다른 사용자들에게 영화 선택의 참고 자료가 됩니다!
    """)

import sys
sys.path.append('/app')  # Docker 경로

from components.chatbot import render_chatbot_button

render_chatbot_button()