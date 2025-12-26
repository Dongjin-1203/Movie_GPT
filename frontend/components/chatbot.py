# frontend/components/chatbot.py
import streamlit as st
import requests
import os

BASE_URL = os.getenv("BASE_URL", "http://backend:8000")


def render_chatbot_button():
    """우하단 고정 챗봇 버튼 렌더링"""
    
    # Dialog 정의
    @st.dialog("🤖 영화 추천 챗봇", width="large")
    def show_chatbot():
        st.markdown("### 💬 어떤 영화를 찾으시나요?")
        
        # 세션 초기화
        if 'chat_messages' not in st.session_state:
            st.session_state.chat_messages = [
                {
                    "role": "assistant",
                    "content": "안녕하세요! 😊\n\n원하는 **장르**, **감독**, **분위기**를 알려주시면 추천해드립니다!\n\n**예시:**\n- '스릴러 추천해줘'\n- '봉준호 감독 영화'\n- '평점 높은 드라마'\n- '재미있는 코미디'"
                }
            ]
        
        # 대화 히스토리 표시
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_messages:
                if msg["role"] == "user":
                    with st.chat_message("user"):
                        st.write(msg["content"])
                else:
                    with st.chat_message("assistant"):
                        st.write(msg["content"])
        
        # 하단 버튼들
        col1, col2 = st.columns([5, 1])
        with col2:
            if st.button("🗑️ 초기화", use_container_width=True, key="reset_chat"):
                st.session_state.chat_messages = []
                st.rerun()
        
        # 사용자 입력 (✅ st.rerun() 제거)
        user_input = st.chat_input("메시지를 입력하세요...")
        
        if user_input:
            # 사용자 메시지 추가
            st.session_state.chat_messages.append({
                "role": "user",
                "content": user_input
            })
            
            # 즉시 표시
            with chat_container:
                with st.chat_message("user"):
                    st.write(user_input)
            
            # 추천 받기
            with st.spinner("🎬 영화를 찾는 중..."):
                params = extract_keywords(user_input)
                
                # 디버그 정보
                debug_info = f"🔍 검색 조건: {params}"
                
                recommendations = get_recommendations(params)
            
            # 봇 응답 생성
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
                        summary = movie['plot_summary'][:100] + "..." if len(movie.get('plot_summary', '')) > 100 else movie.get('plot_summary', '')
                        response += f"   💭 {summary}\n"
                    
                    response += "\n"
                
                response += f"\n_{debug_info}_"
            else:
                response = f"조건에 맞는 영화를 찾지 못했습니다. 😢\n\n"
                response += f"_{debug_info}_\n\n"
                response += "**다른 키워드를 시도해보세요:**\n"
                response += "- 장르: 스릴러, 드라마, 코미디, 액션, 공포\n"
                response += "- 감독: 봉준호, 박찬욱, 나홍진\n"
                response += "- 평점: '평점 높은', '재미있는'"
            
            # 봇 응답 추가
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": response
            })
            
            # 즉시 표시
            with chat_container:
                with st.chat_message("assistant"):
                    st.write(response)
            
            # ✅ st.rerun() 제거 - 자동으로 업데이트됨
    
    # 우하단 고정 버튼
    if st.button("🤖", key="chatbot_trigger", help="영화 추천 챗봇", type="secondary"):
        show_chatbot()
    
    # CSS - 우하단 고정
    st.markdown("""
    <style>
    /* 챗봇 버튼 우하단 고정 */
    button[data-testid="baseButton-secondary"] {
        position: fixed !important;
        bottom: 30px !important;
        right: 30px !important;
        z-index: 9999 !important;
        width: 60px !important;
        height: 60px !important;
        border-radius: 50% !important;
        font-size: 28px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3) !important;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
    }
    
    button[data-testid="baseButton-secondary"]:hover {
        transform: scale(1.1) !important;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.4) !important;
    }
    </style>
    """, unsafe_allow_html=True)


def get_recommendations(params: dict):
    """Backend API 호출"""
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


def extract_keywords(query: str):
    """사용자 입력에서 키워드 추출 (개선된 버전)"""
    query_lower = query.lower()
    params = {"limit": 5}
    
    found_any = False
    
    # ========================================
    # 장르 키워드 (확장)
    # ========================================
    genre_map = {
        "스릴러": ["스릴러", "thriller", "긴장", "추리", "서스펜스", "미스터리"],
        "드라마": ["드라마", "drama", "감동", "인간", "휴먼", "가족"],
        "코미디": ["코미디", "comedy", "웃긴", "재미있는", "유머", "개그", "웃음"],
        "액션": ["액션", "action", "전투", "격투", "싸움", "액션"],
        "공포": ["공포", "horror", "무서운", "호러", "귀신", "좀비"],
        "로맨스": ["로맨스", "romance", "사랑", "멜로", "연애"],
        "SF": ["sf", "공상과학", "미래", "우주"],
        "애니메이션": ["애니", "animation", "만화", "애니메이션"],
        "범죄": ["범죄", "crime", "형사", "수사"],
        "전쟁": ["전쟁", "war", "전투"],
        "다큐": ["다큐", "documentary", "실화"]
    }
    
    for genre, keywords in genre_map.items():
        if any(kw in query_lower for kw in keywords):
            params["genre"] = genre
            found_any = True
            break
    
    # ========================================
    # 감독 키워드 (확장)
    # ========================================
    director_map = {
        "봉준호": ["봉준호", "bong joon", "bong"],
        "박찬욱": ["박찬욱", "park chan"],
        "나홍진": ["나홍진", "na hong"],
        "김지운": ["김지운", "kim jee"],
        "최동훈": ["최동훈", "choi dong"],
        "이창동": ["이창동", "lee chang"],
        "홍상수": ["홍상수", "hong sang"]
    }
    
    for director, keywords in director_map.items():
        if any(kw in query_lower for kw in keywords):
            params["director"] = director
            found_any = True
            break
    
    # ========================================
    # 평점 키워드 (확장)
    # ========================================
    if any(word in query_lower for word in ["평점 높은", "명작", "최고", "인기", "유명한", "대박"]):
        params["min_rating"] = 0.7
        found_any = True
    elif any(word in query_lower for word in ["재미있는", "잘 만든", "괜찮은", "좋은"]):
        params["min_rating"] = 0.6
        found_any = True
    
    # ========================================
    # 키워드를 하나도 못 찾은 경우
    # ========================================
    if not found_any:
        # 기본값: 평점 높은 영화 추천
        params["min_rating"] = 0.5
    
    return params