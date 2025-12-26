# frontend/pages/4_리뷰목록.py
import streamlit as st
import requests
import os
import plotly.graph_objects as go
from collections import defaultdict

st.set_page_config(page_title="리뷰 목록", page_icon="💬", layout="wide")

BASE_URL = os.getenv("BASE_URL", "http://backend:8000")


def get_all_reviews():
    """전체 리뷰 목록 가져오기"""
    try:
        response = requests.get(f"{BASE_URL}/reviews/", timeout=10)
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        st.error(f"❌ 리뷰 목록 조회 실패: {str(e)}")
        return []


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


def delete_review(review_id: int):
    """리뷰 삭제"""
    try:
        response = requests.delete(f"{BASE_URL}/reviews/{review_id}", timeout=10)
        return response.status_code == 200
    except Exception as e:
        st.error(f"❌ 삭제 실패: {str(e)}")
        return False


def create_sentiment_pie_chart(reviews, title="감성 분석 분포", height=400):
    """감성 분석 파이 차트 생성"""
    # 감성별 개수 집계
    sentiment_counts = {
        'positive': 0,
        'negative': 0,
        'neutral': 0
    }
    
    for review in reviews:
        label = review.get('sentiment_label', 'neutral')
        if label in sentiment_counts:
            sentiment_counts[label] += 1
        else:
            sentiment_counts['neutral'] += 1
    
    # 데이터 준비
    labels_korean = {
        'positive': '😊 긍정',
        'negative': '😞 부정',
        'neutral': '😐 중립'
    }
    
    colors = {
        'positive': '#10b981',  # 초록
        'negative': '#ef4444',  # 빨강
        'neutral': '#6b7280'    # 회색
    }
    
    labels = [labels_korean[key] for key in sentiment_counts.keys()]
    values = list(sentiment_counts.values())
    colors_list = [colors[key] for key in sentiment_counts.keys()]
    
    # Plotly 파이 차트 생성
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.3,  # 도넛 차트
        marker=dict(colors=colors_list),
        textinfo='label+percent',
        textfont=dict(size=13),
        hovertemplate='<b>%{label}</b><br>개수: %{value}<br>비율: %{percent}<extra></extra>'
    )])
    
    # ✅ 수정: 레전드를 하단으로 배치
    fig.update_layout(
        title={
            'text': title,
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 16}
        },
        showlegend=True,
        # 🔥 추가: 레전드 클릭 비활성화
        legend=dict(
            itemclick=False,        # 싱글 클릭 비활성화
            itemdoubleclick=False   # 더블 클릭 비활성화
        ),
        height=height,
        margin=dict(t=50, b=20, l=40, r=40)
    )
    
    return fig, sentiment_counts


def get_reviews_by_movie(reviews):
    """영화별로 리뷰 그룹핑"""
    movie_reviews = defaultdict(list)
    for review in reviews:
        movie_id = review.get('movie_id')
        if movie_id:
            movie_reviews[movie_id].append(review)
    return movie_reviews


# 메인 UI
st.title("💬 리뷰 목록")
st.markdown("---")

# 리뷰 목록 가져오기
with st.spinner("📥 리뷰 목록을 불러오는 중..."):
    reviews = get_all_reviews()
    movies = get_all_movies()

if not reviews:
    st.info("📭 작성된 리뷰가 없습니다. '리뷰 작성' 페이지에서 첫 리뷰를 작성해보세요!")
    
    if st.button("✍️ 리뷰 작성하러 가기", type="primary"):
        st.switch_page("pages/3_리뷰작성.py")
    
    st.stop()

# ========================================
# 리뷰 통계 (탭 구조)
# ========================================
st.subheader("🎬 영화별 통계")

movie_reviews = get_reviews_by_movie(reviews)

# 리뷰가 있는 영화만 필터링
movies_with_reviews = [m for m in movies if m.get('id') in movie_reviews]

if not movies_with_reviews:
    st.info("아직 리뷰가 작성된 영화가 없습니다.")
else:
    # 정렬 옵션
    sort_by = st.selectbox(
        "정렬 기준",
        ["리뷰 많은 순", "리뷰 적은 순", "평점 높은 순", "평점 낮은 순"],
        key="movie_stats_sort"
    )
    
    # 정렬 적용
    if sort_by == "리뷰 많은 순":
        movies_with_reviews = sorted(movies_with_reviews, key=lambda m: len(movie_reviews.get(m.get('id'), [])), reverse=True)
    elif sort_by == "리뷰 적은 순":
        movies_with_reviews = sorted(movies_with_reviews, key=lambda m: len(movie_reviews.get(m.get('id'), [])))
    elif sort_by == "평점 높은 순":
        movies_with_reviews = sorted(movies_with_reviews, key=lambda m: m.get('rating', 0), reverse=True)
    else:  # 평점 낮은 순
        movies_with_reviews = sorted(movies_with_reviews, key=lambda m: m.get('rating', 0))
    
    st.markdown("---")
    
    # ✅ 수정: Expander로 각 영화를 깔끔하게 표시
    for movie in movies_with_reviews:
        movie_id = movie.get('id')
        movie_title = movie.get('title', '제목 없음')
        movie_poster = movie.get('poster_url')
        movie_rating = movie.get('rating', 0)
        
        reviews_for_movie = movie_reviews.get(movie_id, [])
        
        if not reviews_for_movie:
            continue
        
        # ✅ Expander로 감싸서 공간 절약
        with st.expander(f"🎬 {movie_title} (리뷰 {len(reviews_for_movie)}개)", expanded=True):
            # 상단: 영화 기본 정보
            col_info1, col_info2 = st.columns([1, 3])
            
            with col_info1:
                # 포스터
                if movie_poster:
                    st.image(movie_poster, use_container_width=True)
                else:
                    st.markdown("### 🎬")
            
            with col_info2:
                st.markdown(f"### {movie_title}")
                
                info_parts = []
                if movie.get('director'):
                    info_parts.append(f"🎥 {movie['director']}")
                if movie.get('genre'):
                    info_parts.append(f"🎭 {movie['genre']}")
                if movie.get('release_date'):
                    info_parts.append(f"📅 {movie['release_date'][:4]}")
                
                if info_parts:
                    st.caption(" | ".join(info_parts))
                
                if movie_rating > 0:
                    stars = "⭐" * min(int(movie_rating * 5), 5)
                    st.caption(f"{stars} {movie_rating:.2f}")
            
            st.markdown("---")
            
            # 하단: 통계 + 차트
            col_chart, col_stats = st.columns([2.5, 1.5])
            
            with col_chart:
                # 파이 차트
                reviews_for_movie_list = movie_reviews.get(movie_id, [])
                
                # 감성별 개수 집계
                sentiment_counts_movie = {
                    'positive': 0,
                    'negative': 0,
                    'neutral': 0
                }
                
                for review in reviews_for_movie_list:
                    label = review.get('sentiment_label', 'neutral')
                    if label in sentiment_counts_movie:
                        sentiment_counts_movie[label] += 1
                    else:
                        sentiment_counts_movie['neutral'] += 1
                
                # 파이 차트 생성
                labels_korean = {
                    'positive': '😊 긍정',
                    'negative': '😞 부정',
                    'neutral': '😐 중립'
                }
                
                colors = {
                    'positive': '#10b981',
                    'negative': '#ef4444',
                    'neutral': '#6b7280'
                }
                
                labels = [labels_korean[key] for key in sentiment_counts_movie.keys()]
                values = list(sentiment_counts_movie.values())
                colors_list = [colors[key] for key in sentiment_counts_movie.keys()]
                
                fig_movie = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    hole=0.3,
                    marker=dict(colors=colors_list),
                    textinfo='label+percent',
                    textfont=dict(size=12),
                    hovertemplate='<b>%{label}</b><br>개수: %{value}<br>비율: %{percent}<extra></extra>'
                )])
                
                fig_movie.update_layout(
                    showlegend=True,
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=-0.25,
                        xanchor="center",
                        x=0.5,
                        itemclick=False,
                        itemdoubleclick=False 
                    ),
                    height=320,
                    margin=dict(t=20, b=90, l=20, r=20)
                )
                
                st.plotly_chart(fig_movie, use_container_width=True)
            
            with col_stats:
                st.markdown("### 📊 통계")
                
                st.metric("총 리뷰", f"{len(reviews_for_movie)}개")
                
                st.markdown("---")
                
                # 감성별 개수
                st.markdown("**감성 분포**")
                st.write(f"😊 긍정: {sentiment_counts_movie['positive']}개")
                st.write(f"😞 부정: {sentiment_counts_movie['negative']}개")
                st.write(f"😐 중립: {sentiment_counts_movie['neutral']}개")
                
                # 평균 감성 점수
                movie_scores = [r.get('sentiment_score', 0) for r in reviews_for_movie if r.get('sentiment_score') is not None]
                if movie_scores:
                    avg_movie_score = sum(movie_scores) / len(movie_scores)
                    
                    st.markdown("---")
                    st.metric("평균 감성", f"{avg_movie_score:.3f}")
                    
                    # 감성 평가
                    if avg_movie_score >= 0.6:
                        st.success("😊 긍정적")
                    elif avg_movie_score <= 0.4:
                        st.error("😞 부정적")
                    else:
                        st.info("😐 중립적")

st.markdown("---")

# ========================================
# 필터링 옵션
# ========================================
st.subheader("🔍 필터 및 정렬")

col1, col2 = st.columns(2)

with col1:
    # 영화 필터
    movie_dict = {f"{m.get('title', '제목 없음')} ({m.get('id')})": m.get('id') for m in movies}
    movie_filter = st.selectbox(
        "영화 필터",
        ["전체"] + list(movie_dict.keys()),
        key="movie_filter"
    )

with col2:
    # 정렬
    sort_option = st.selectbox(
        "정렬",
        ["최신순", "오래된순", "감성 점수 높은순", "감성 점수 낮은순"],
        key="sort_option"
    )

# 필터링 적용
filtered_reviews = reviews.copy()

# 영화 필터
if movie_filter != "전체":
    selected_movie_id = movie_dict[movie_filter]
    filtered_reviews = [r for r in filtered_reviews if r.get('movie_id') == selected_movie_id]

# 정렬
if sort_option == "오래된순":
    filtered_reviews = sorted(filtered_reviews, key=lambda x: x.get('id', 0))
elif sort_option == "감성 점수 높은순":
    filtered_reviews = sorted(filtered_reviews, key=lambda x: x.get('sentiment_score', 0), reverse=True)
elif sort_option == "감성 점수 낮은순":
    filtered_reviews = sorted(filtered_reviews, key=lambda x: x.get('sentiment_score', 0))
else:  # 최신순
    filtered_reviews = sorted(filtered_reviews, key=lambda x: x.get('id', 0), reverse=True)

st.markdown("---")

# ========================================
# 리뷰 목록 표시
# ========================================
st.subheader(f"📝 리뷰 목록 ({len(filtered_reviews)}개)")

if not filtered_reviews:
    st.info("필터 조건에 맞는 리뷰가 없습니다.")
else:
    for review in filtered_reviews:
        # 영화 정보 찾기
        movie = next((m for m in movies if m.get('id') == review.get('movie_id')), None)
        movie_title = movie.get('title', '알 수 없음') if movie else '알 수 없음'
        
        # 리뷰 카드
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                # 영화 제목
                st.markdown(f"### 🎬 {movie_title}")
                
                # 작성자
                st.caption(f"✍️ {review.get('author', '익명')} | 📅 {review.get('created_at', '')[:10]}")
                
                # 리뷰 내용
                st.write(review.get('content', ''))
            
            with col2:
                # 감성 분석 결과
                sentiment_label = review.get('sentiment_label', 'neutral')
                sentiment_score = review.get('sentiment_score', 0)
                
                if sentiment_label == 'positive':
                    st.success("😊 긍정")
                    st.metric("감성 점수", f"{sentiment_score:.3f}")
                elif sentiment_label == 'negative':
                    st.error("😞 부정")
                    st.metric("감성 점수", f"{sentiment_score:.3f}")
                else:
                    st.info("😐 중립")
                    st.metric("감성 점수", f"{sentiment_score:.3f}")
            
            with col3:
                st.write("")
                st.write("")
                
                # 삭제 버튼
                if st.button("🗑️ 삭제", key=f"delete_{review.get('id')}", use_container_width=True):
                    if delete_review(review.get('id')):
                        st.success("✅ 삭제 완료!")
                        st.rerun()
            
            st.markdown("---")

# ========================================
# 사이드바
# ========================================
with st.sidebar:
    st.header("📊 통계 요약")
    
    st.metric("총 리뷰", f"{len(reviews)}개")
    st.metric("필터된 리뷰", f"{len(filtered_reviews)}개")
    
    # 리뷰가 있는 영화 계산
    movie_reviews_dict = get_reviews_by_movie(reviews)
    movies_with_reviews_count = len([m for m in movies if m.get('id') in movie_reviews_dict])
    st.metric("리뷰 있는 영화", f"{movies_with_reviews_count}개")
    
    if reviews:
        st.markdown("---")
        st.markdown("### 감성 분포")
        
        # 전체 통계에서 가져오기
        _, overall_sentiment = create_sentiment_pie_chart(reviews)
        
        # 프로그레스 바
        total = len(reviews)
        positive_pct = overall_sentiment['positive'] / total * 100 if total > 0 else 0
        negative_pct = overall_sentiment['negative'] / total * 100 if total > 0 else 0
        neutral_pct = overall_sentiment['neutral'] / total * 100 if total > 0 else 0
        
        st.markdown(f"**😊 긍정** ({overall_sentiment['positive']}개)")
        st.progress(positive_pct / 100)
        
        st.markdown(f"**😞 부정** ({overall_sentiment['negative']}개)")
        st.progress(negative_pct / 100)
        
        st.markdown(f"**😐 중립** ({overall_sentiment['neutral']}개)")
        st.progress(neutral_pct / 100)
    
    st.markdown("---")
    
    st.header("💡 사용 팁")
    st.markdown("""
    - **전체 통계**: 모든 리뷰의 감성 분포
    - **영화별 통계**: 각 영화의 감성 분포
    - 감성 필터로 특정 감성만 확인
    - 영화 필터로 영화별 리뷰 확인
    - Expander를 접으면 공간 절약
    """)

import sys
sys.path.append('/app')  # Docker 경로

from components.chatbot import render_chatbot_button

render_chatbot_button()