"""
리뷰 목록 페이지
"""

import streamlit as st
from utils.api_client import client

# 페이지 제목
st.title("📝 리뷰 목록")

# 새로고침 버튼
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("🔄 새로고침", type="secondary"):
        st.rerun()

st.divider()

# 필터 섹션
st.subheader("🔍 필터")

# 영화 목록 가져오기
movies = client.get_all_movies()

# 필터 옵션
filter_option = st.radio(
    "보기 옵션",
    options=["전체 리뷰", "영화별 리뷰"],
    horizontal=True
)

selected_movie_id = None

if filter_option == "영화별 리뷰":
    if len(movies) == 0:
        st.warning("⚠️ 등록된 영화가 없습니다.")
        st.stop()
    
    # 영화 선택
    movie_dict = {movie["title"]: movie["id"] for movie in movies}
    selected_movie_title = st.selectbox(
        "영화 선택",
        options=list(movie_dict.keys())
    )
    selected_movie_id = movie_dict[selected_movie_title]

st.divider()

# 리뷰 조회
st.subheader("💬 리뷰")

if filter_option == "전체 리뷰":
    reviews = client.get_all_reviews(limit=50)
else:
    reviews = client.get_movie_reviews(selected_movie_id)

# 리뷰가 없는 경우
if len(reviews) == 0:
    st.info("📭 등록된 리뷰가 없습니다.")
    st.markdown("**리뷰 작성** 페이지에서 첫 리뷰를 작성해보세요!")
else:
    st.write(f"총 **{len(reviews)}개**의 리뷰가 있습니다.")
    
    st.divider()
    
    # 각 리뷰 카드
    for review in reviews:
        with st.container():
            
            # 2열 레이아웃 (정보 | 삭제 버튼)
            col_info, col_action = st.columns([5, 1])
            
            with col_info:
                # 감성 이모지
                sentiment_emoji = {
                    "positive": "😊",
                    "negative": "😞",
                    "neutral": "😐"
                }
                
                sentiment_label_kr = {
                    "positive": "긍정",
                    "negative": "부정",
                    "neutral": "중립"
                }
                
                emoji = sentiment_emoji.get(review.get("sentiment_label"), "😐")
                label = sentiment_label_kr.get(review.get("sentiment_label"), "중립")
                score = review.get("sentiment_score", 0)
                
                # 영화 정보 (영화별 필터가 아닐 때만)
                if filter_option == "전체 리뷰":
                    # 영화 제목 찾기
                    movie_title = "알 수 없음"
                    for movie in movies:
                        if movie["id"] == review["movie_id"]:
                            movie_title = movie["title"]
                            break
                    
                    st.markdown(f"### 🎬 {movie_title}")
                
                # 감성 분석 결과
                st.markdown(f"**{emoji} {label}** (신뢰도: {score:.1%})")
                
                # 작성자
                st.markdown(f"**작성자**: {review['author']}")
                
                # 리뷰 내용
                st.markdown(f"**리뷰**: {review['content']}")
                
                # 등록일
                created_at = review.get("created_at", "")[:10]
                st.caption(f"등록일: {created_at}")
            
            with col_action:
                # 삭제 버튼
                if st.button("🗑️", key=f"delete_{review['id']}", help="리뷰 삭제"):
                    # 삭제 확인
                    success = client.delete_review(review["id"])
                    
                    if success:
                        st.success("✅ 삭제되었습니다!")
                        st.rerun()
                    else:
                        st.error("❌ 삭제 실패")
            
            st.divider()

# 통계 정보 (영화별 필터일 때)
if filter_option == "영화별 리뷰" and selected_movie_id and len(reviews) > 0:
    st.subheader("📊 통계")
    
    # 평균 평점 가져오기
    rating_data = client.get_movie_rating(selected_movie_id)
    
    if rating_data:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("평균 점수", f"{rating_data['average_score']:.2f}")
        
        with col2:
            st.metric("리뷰 수", f"{rating_data['review_count']}개")
        
        with col3:
            # 긍정/부정 비율
            positive_count = sum(1 for r in reviews if r.get("sentiment_label") == "positive")
            negative_count = sum(1 for r in reviews if r.get("sentiment_label") == "negative")
            
            if positive_count + negative_count > 0:
                positive_ratio = positive_count / (positive_count + negative_count) * 100
                st.metric("긍정 비율", f"{positive_ratio:.1f}%")
            else:
                st.metric("긍정 비율", "N/A")