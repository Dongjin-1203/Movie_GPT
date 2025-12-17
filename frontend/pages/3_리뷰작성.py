import streamlit as st
from utils.api_client import client 

# 페이지 제목
st.title("✍️ 리뷰 작성")
st.write("영화를 보고 느낀 점을 공유해주세요!")

st.divider()

# 영화 목록 가져오기
movies = client.get_all_movies()

if len(movies) == 0:
    st.warning("⚠️ 등록된 영화가 없습니다.")
    st.info("먼저 '영화 추가' 페이지에서 영화를 추가해주세요!")
    st.stop()  # 페이지 실행 중지

# 영화 선택
st.subheader("1️⃣ 영화 선택")

# 영화 목록을 {title: id} 딕셔너리로 변환
movie_dict = {movie["title"]: movie["id"] for movie in movies}

selected_movie_title = st.selectbox(
    "리뷰를 작성할 영화를 선택하세요",
    options=list(movie_dict.keys()),
    placeholder="영화를 선택하세요"
)

selected_movie_id = movie_dict[selected_movie_title]

st.divider()

# 리뷰 작성 폼
st.subheader("2️⃣ 리뷰 작성")

with st.form("review_form"):
    
    # 작성자
    author = st.text_input(
        "작성자 *",
        placeholder="이름 또는 닉네임",
        help="필수 입력 항목입니다"
    )
    
    # 리뷰 내용
    content = st.text_area(
        "리뷰 내용 *",
        placeholder="영화를 보고 느낀 점을 자유롭게 작성해주세요 (최소 5자)",
        height=200,
        help="필수 입력 항목입니다"
    )
    
    # 제출 버튼
    submitted = st.form_submit_button("리뷰 등록", type="primary")

# 폼 제출 처리
if submitted:
    # 입력 검증
    if not author.strip():
        st.error("❌ 작성자는 필수 입력 항목입니다!")
    elif not content.strip():
        st.error("❌ 리뷰 내용은 필수 입력 항목입니다!")
    elif len(content.strip()) < 5:
        st.error("❌ 리뷰 내용은 최소 5자 이상이어야 합니다!")
    else:
        # API 요청 데이터
        review_data = {
            "movie_id": selected_movie_id,
            "author": author.strip(),
            "content": content.strip()
        }
        
        # 로딩 표시
        with st.spinner("🤖 AI가 감성을 분석하고 있습니다..."):
            result = client.create_review(review_data)
        
        # 결과 처리
        if result:
            st.success(f"✅ 리뷰가 성공적으로 등록되었습니다!")
            st.balloons()
            
            # 감성 분석 결과 표시
            st.divider()
            st.subheader("🤖 AI 감성 분석 결과")
            
            sentiment_label = result.get("sentiment_label")
            sentiment_score = result.get("sentiment_score", 0)
            
            # 이모지 매핑
            emoji_map = {
                "positive": "😊",
                "negative": "😞",
                "neutral": "😐"
            }
            
            label_kr = {
                "positive": "긍정",
                "negative": "부정",
                "neutral": "중립"
            }
            
            emoji = emoji_map.get(sentiment_label, "😐")
            label_text = label_kr.get(sentiment_label, "중립")
            
            # 3열 레이아웃
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("감성", f"{emoji} {label_text}")
            
            with col2:
                st.metric("신뢰도", f"{sentiment_score:.1%}")
            
            with col3:
                st.metric("영화", selected_movie_title)
            
            # 등록된 리뷰 표시
            st.divider()
            st.subheader("등록된 리뷰")
            
            with st.expander("리뷰 내용 보기", expanded=True):
                st.write(f"**작성자**: {result['author']}")
                st.write(f"**내용**: {result['content']}")
                st.caption(f"등록일: {result['created_at'][:10]}")
        
        else:
            st.error("❌ 리뷰 등록에 실패했습니다. 다시 시도해주세요.")