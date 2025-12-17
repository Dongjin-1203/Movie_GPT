import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="Movie Review System",
    page_icon="🎬",
    layout="wide"
)

# 메인 페이지 제목
st.title("🎬 Movie GPT")

# 환영 메시지
st.markdown("""
## 환영합니다! 👋

이 시스템에서는 다음과 같은 기능을 사용할 수 있습니다:

### 📋 주요 기능
- **🎬 영화 목록**: 등록된 모든 영화를 확인하고 삭제할 수 있습니다
- **➕ 영화 추가**: 새로운 영화를 등록할 수 있습니다

### 🚀 시작하기
왼쪽 사이드바에서 원하는 메뉴를 선택하세요!
""")

# 시스템 정보
st.info("""
**💡 Tip**: 
- 영화를 추가하려면 '영화 추가' 페이지로 이동하세요
- 등록된 영화를 보려면 '영화 목록' 페이지로 이동하세요
""")

# 사이드바 안내
with st.sidebar:
    st.success("👈 메뉴를 선택하세요!")
    
    st.divider()
    
    st.caption("Made with ❤️ using Streamlit & FastAPI")