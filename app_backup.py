import streamlit as st
import pandas as pd
from openai import OpenAI
import os

# 1. 페이지 설정
st.set_page_config(page_title="243개 지역: 나만의 이야기 생성기", layout="wide")
st.title("🗺️ 243개 지역: 나만의 이야기 생성기")

# 2. [자동 로그인] Secrets에서 API 키 가져오기
# 이제 사용자에게 키를 입력받지 않고, 서버에 저장된 키를 사용합니다.
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except:
    # 혹시라도 Secrets 설정이 안 되어 있을 경우를 대비한 안내
    st.error("🚨 서버에 API 키가 설정되지 않았습니다. [Settings] > [Secrets]를 확인해주세요.")
    st.stop()

# 사이드바: 입력창 대신 환영 메시지 출력
with st.sidebar:
    st.success("✅ 인증된 사용자입니다.")
    st.info("팀원들과 함께 자유롭게 이야기를 만들어보세요! (키 입력 불필요)")

# 3. 데이터 로드 (인코딩 문제 해결사)
@st.cache_data
def load_data():
    file_path = 'data.csv'
    try:
        return pd.read_csv(file_path, encoding='utf-8')
    except:
        try:
            return pd.read_csv(file_path, encoding='cp949')
        except:
            return pd.read_csv(file_path, encoding='euc-kr')

data = load_data()

if data.empty:
    st.error("❌ 데이터 파일을 읽을 수 없습니다.")
    st.stop()

# --- [스마트 컬럼 찾기] ---
# 엑셀 파일의 이름이 조금 달라도(지역2, 입버릇 등) 알아서 찾아내는 똑똑한 기능
def find_column(candidates, df):
    for col in df.columns:
        for candidate in candidates:
            if candidate in str(col):
                return col
    return None

# 알아서 컬럼 찾기
region_col = find_column(['지역', '도시', 'region'], data)
char_col = find_column(['캐릭터', '이름', 'name'], data)
feat_col = find_column(['특징', '입버릇', '설명', 'desc'], data)

# 못 찾았을 경우 대비 (기본값 설정)
if region_col is None: region_col = data.columns[0]
if char_col is None: char_col = data.columns[1] if len(data.columns) > 1 else data.columns[0]
if feat_col is None: feat_col = data.columns[-1]

# 4. 화면 구성
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. 지역 선택")
    
    # 선택 상자
    selected_region = st.selectbox("어떤 지역으로 떠날까요?", data[region_col].unique())
    
    # 선택된 지역의 정보 가져오기
    row = data[data[region_col] == selected_region].iloc[0]
    
    c_name = row[char_col] if pd.notna(row[char_col]) else "알 수 없는 캐릭터"
    f_desc = row[feat_col] if pd.notna(row[feat_col]) else "특징 없음"
    
    st.info(f"📍 **{selected_region}**\n\n👤 **캐릭터:** {c_name}\n\n✨ **특징:** {f_desc}")

    with st.expander("데이터 원본 확인하기"):
        st.dataframe(data)

with col2:
    st.subheader("2. 이야기 아이디어")
    user_input = st.text_area("어떤 사건을 만들까요?", placeholder="예: 주인공이 우연히 보물을 발견했다.", height=150)
    
    generate_btn = st.button("이야기 생성하기 ✨", type="primary")

# 5. 이야기 생성 로직 (자동 로그인된 키 사용)
if generate_btn:
    if not user_input:
        st.warning("아이디어를 입력해주세요!")
    else:
        with st.spinner(f"AI가 '{selected_region}'의 이야기를 짓고 있습니다...✍️"):
            try:
                # Secrets에서 가져온 키로 연결
                client = OpenAI(api_key=api_key)
                
                prompt = f"""
                당신은 창의적인 소설가입니다.
                - 배경: {selected_region}
                - 캐릭터: {c_name}
                - 특징/입버릇: {f_desc}
                - 사건: {user_input}
                
                위 정보를 섞어서 재미있는 500자 내외의 소설을 써주세요.
                """
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini", 
                    messages=[{"role": "user", "content": prompt}]
                )
                
                st.markdown("---")
                st.success("🎉 이야기가 완성되었습니다!")
                st.write(response.choices[0].message.content)
                
            except Exception as e:
                st.error(f"에러가 발생했습니다: {e}")
