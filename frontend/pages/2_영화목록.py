import streamlit as st
from utils.api_client import client

# 페이지 제목
st.title("🎬 영화 목록")

# 새로고침 버튼
if st.button("🔄 새로고침", type="secondary"):
    st.rerun()

# 구분선
st.divider()

# API 호출 - 전체 영화 목록 조회
movies = client.get_all_movies()

# 영화가 없는 경우
if len(movies) == 0:
    st.info("📭 등록된 영화가 없습니다.")
    st.markdown("**영화 추가** 페이지에서 영화를 추가해주세요!")
else:
    # 영화 개수 표시
    st.success(f"총 **{len(movies)}개**의 영화가 등록되어 있습니다.")
    
    st.divider()
    
    # 각 영화를 카드 형식으로 표시
    for movie in movies:
        with st.container():
            
            # 2열 레이아웃 (포스터 | 정보)
            col1, col2 = st.columns([1, 3])
            
            with col1:
                # 포스터 이미지
                if movie.get("poster_url"):
                    try:
                        st.image(
                            movie["poster_url"],
                            width=150,
                            use_container_width=False
                        )
                    except Exception:
                        st.write("🎬")
                        st.caption("포스터 없음")
                else:
                    st.write("🎬")
                    st.caption("포스터 없음")
            
            with col2:
                # 영화 제목
                st.subheader(f"🎬 {movie['title']}")
                
                # 영화 정보 (있는 것만 표시)
                info_parts = []
                
                if movie.get("release_date"):
                    info_parts.append(f"📅 {movie['release_date']}")
                
                if movie.get("director"):
                    info_parts.append(f"🎬 {movie['director']}")
                
                if movie.get("genre"):
                    info_parts.append(f"🎭 {movie['genre']}")
                
                # 정보를 한 줄로 표시
                if len(info_parts) > 0:
                    st.write(" | ".join(info_parts))
                
                # 등록일 (작게 표시)
                if movie.get("created_at"):
                    created_at = movie["created_at"][:10]  # YYYY-MM-DD만 추출
                    st.caption(f"등록일: {created_at}")
                
                # 삭제 버튼
                if st.button(
                    "🗑️ 삭제",
                    key=f"delete_{movie['id']}",
                    type="secondary"
                ):
                    # 삭제 API 호출
                    success = client.delete_movie(movie["id"])
                    
                    if success:
                        st.success(f"✅ '{movie['title']}' 영화가 삭제되었습니다!")
                        st.rerun()  # 페이지 새로고침
                    else:
                        st.error("❌ 삭제에 실패했습니다.")
            
            # 영화 카드 사이 구분선
            st.divider()