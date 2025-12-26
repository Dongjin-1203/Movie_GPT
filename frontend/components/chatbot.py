# frontend/components/chatbot.py
import streamlit as st
import requests
import os

BASE_URL = os.getenv("BASE_URL", "http://backend:8000")


def render_chatbot_button():
    """우하단 고정 챗봇 버튼 렌더링"""
    
    # ✅ 버튼 크기와 위치 모두 고정
    st.markdown("""
    <style>
    /* 챗봇 버튼 스타일 */
    div[data-testid="stVerticalBlock"]:last-of-type button[kind="secondary"]:last-of-type {
        position: fixed !important;
        bottom: 30px !important;
        right: 30px !important;
        z-index: 9999 !important;
        
        /* ✅ 크기 고정 (길게 늘어나지 않도록) */
        width: 60px !important;
        height: 60px !important;
        min-width: 60px !important;
        max-width: 60px !important;
        
        /* ✅ 원형 */
        border-radius: 50% !important;
        
        /* ✅ 이모지 크기 */
        font-size: 28px !important;
        padding: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # ✅ Dialog 정의
    @st.dialog("🤖 영화 추천 챗봇", width="large")
    def show_chatbot():
        st.markdown("### 💬 어떤 영화를 찾으시나요?")
        
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = [
                {
                    "role": "assistant",
                    "content": "안녕하세요! 😊\n\n**AI 추천 시스템**이 TMDB 데이터베이스에서 최적의 영화를 찾아드립니다!\n\n**예시:**\n- '긴장감 넘치는 스릴러 추천해줘'\n- '2020년대 코미디 영화'\n- '평점 높은 SF 영화'\n- '감동적인 드라마'"
                }
            ]
        
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_messages:
                if msg["role"] == "user":
                    with st.chat_message("user"):
                        st.write(msg["content"])
                else:
                    with st.chat_message("assistant"):
                        st.write(msg["content"])
        
        user_input = st.chat_input("메시지를 입력하세요...")
        
        if user_input:
            st.session_state.chat_messages.append({
                "role": "user",
                "content": user_input
            })
            
            with chat_container:
                with st.chat_message("user"):
                    st.write(user_input)
            
            with st.spinner("🤖 AI가 TMDB에서 영화를 검색하는 중..."):
                ai_response = get_ai_recommendations(user_input)
            
            response = None
            
            if ai_response and ai_response.get("response"):
                response = ai_response["response"]
                if ai_response.get("conversation"):
                    response += "\n\n---\n_🤖 AI 추천 시스템 사용됨_"
            else:
                st.warning("AI 추천을 사용할 수 없습니다. 기본 검색을 사용합니다.")
                params = extract_keywords(user_input)
                recommendations = get_recommendations(params)
                
                if recommendations:
                    response = "추천 영화를 찾았습니다! 🎉\n\n"
                    for i, movie in enumerate(recommendations, 1):
                        response += f"**{i}. {movie.get('title', '제목 없음')}**\n"
                        info = []
                        if movie.get('director'):
                            info.append(f"🎥 {movie['director']}")
                        if movie.get('genre'):
                            info.append(f"🎭 {movie['genre']}")
                        if movie.get('release_date'):
                            info.append(f"📅 {movie['release_date'][:4]}")
                        if info:
                            response += f"   {' | '.join(info)}\n"
                        if movie.get('rating', 0) > 0:
                            stars = "⭐" * min(int(movie['rating'] * 5), 5)
                            response += f"   {stars} {movie['rating']:.2f}\n"
                        if movie.get('plot_summary'):
                            summary = movie['plot_summary']
                            if len(summary) > 100:
                                summary = summary[:100] + "..."
                            response += f"   💭 {summary}\n"
                        response += "\n"
                    response += f"\n_🔍 검색 조건: {params}_"
                else:
                    response = f"조건에 맞는 영화를 찾지 못했습니다. 😢\n\n_검색 조건: {params}_"
            
            if response:
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": response
                })
                with chat_container:
                    with st.chat_message("assistant"):
                        st.write(response)
    
    # ✅ Streamlit 버튼 (JavaScript가 스타일 적용)
    if st.button("🤖", key="chatbot_trigger", help="영화 추천 챗봇", type="secondary"):
        show_chatbot()


def get_recommendations(params: dict):
    """Backend API 호출 (기존 방식)"""
    try:
        response = requests.get(
            f"{BASE_URL}/movies/recommend",
            params=params,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"추천 API 오류: {str(e)}")
        return []


def get_ai_recommendations(user_query: str):
    """Claude + MCP AI 추천"""
    try:
        response = requests.post(
            f"{BASE_URL}/movies/recommend/ai",
            json={"query": user_query},
            timeout=60
        )
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"AI 추천 API 오류: {response.status_code}")
            return None
    except requests.exceptions.Timeout:
        st.error("AI 추천 시간 초과 (60초)")
        return None
    except Exception as e:
        st.error(f"AI 추천 오류: {str(e)}")
        return None


def extract_keywords(query: str):
    """사용자 입력에서 키워드 추출 (Fallback용)"""
    query_lower = query.lower()
    params = {"limit": 5}
    
    genre_map = {
        "스릴러": ["스릴러", "thriller", "긴장", "추리", "서스펜스", "미스터리"],
        "드라마": ["드라마", "drama", "감동", "인간", "휴먼", "가족"],
        "코미디": ["코미디", "comedy", "웃긴", "재미있는", "유머", "개그", "웃음"],
        "액션": ["액션", "action", "전투", "격투", "싸움"],
        "공포": ["공포", "horror", "무서운", "호러", "귀신", "좀비"],
        "로맨스": ["로맨스", "romance", "사랑", "멜로", "연애"],
        "SF": ["sf", "공상과학", "미래", "우주"],
        "애니메이션": ["애니", "animation", "만화"],
        "범죄": ["범죄", "crime", "형사", "수사"],
    }
    
    for genre, keywords in genre_map.items():
        if any(kw in query_lower for kw in keywords):
            params["genre"] = genre
            break
    
    if any(word in query_lower for word in ["평점 높은", "명작", "최고", "인기"]):
        params["min_rating"] = 0.7
    elif any(word in query_lower for word in ["재미있는", "좋은"]):
        params["min_rating"] = 0.5
    else:
        params["min_rating"] = 0.3
    
    return params