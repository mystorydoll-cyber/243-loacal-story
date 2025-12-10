import streamlit as st
import pandas as pd
import os

# 1. 페이지 설정 (가장 윗부분에 있어야 함)
st.set_page_config(page_title="243개 지역: 나만의 이야기 생성기", layout="wide")
st.title("🗺️ 243개 지역: 나만의 이야기 생성기")

# 2. 사이드바: API 키 입력 받기
with st.sidebar:
    api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")
    st.markdown("---")
    st.write("키를 입력해야 이야기가 생성됩니다.")

# 3. API 키가 없으면 경고하고 멈춤
if not api_key:
    st.warning("👈 왼쪽 사이드바에 API Key를 먼저 입력해주세요.")
    st.info("키를 입력하면 화면이 자동으로 새로고침됩니다.")
    st.stop()  # 여기서 코드 실행 중단

# 4. API 키 설정
os.environ["OPENAI_API_KEY"] = api_key

# 5. 데이터 로드 (인코딩 문제 해결사)
@st.cache_data
def load_data():
    file_path = 'data.csv'
    # 1순위: utf-8 (맥/리눅스 표준)
    try:
        return pd.read_csv(file_path, encoding='utf-8')
    except:
        pass
    # 2순위: cp949 (윈도우 엑셀 표준)
    try:
        return pd.read_csv(file_path, encoding='cp949')
    except:
        pass
    # 3순위: euc-kr (구형 한글)
    try:
        return pd.read_csv(file_path, encoding='euc-kr')
    except:
        return pd.DataFrame() # 실패하면 빈 데이터 반환

data = load_data()

# 6. 데이터 로드 결과 확인 및 화면 표시
if data.empty:
    st.error("❌ 데이터 파일(data.csv)을 읽을 수 없습니다. 파일 내용이나 형식을 확인해주세요.")
else:
    st.success("✅ 데이터를 성공적으로 불러왔습니다! 이야기 생성을 시작할 수 있습니다.")
    
    # 여기서부터 실제 앱 화면 구성
    st.markdown(f"**총 {len(data)}개의 지역 데이터가 준비되었습니다.**")
    st.write("당신이 선택한 지역의 캐릭터와 함께 새로운 전설을 만들어보세요!")

    # 사용자 입력 받기
    user_input = st.text_area("당신의 아이디어를 더해주세요!", placeholder="예: 주인공이 갑자기 초능력을 얻게 된다면?")
    
    if st.button("새로운 이야기 만들기 ✨"):
        st.write("이야기를 만드는 중입니다... (여기에 LLM 연결 코드가 들어갑니다)")
