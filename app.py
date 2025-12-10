import streamlit as st
import pandas as pd
from openai import OpenAI
import os

# 1. 페이지 설정
st.set_page_config(page_title="243개 지역: 나만의 이야기 생성기", layout="wide")
st.title("🗺️ 243개 지역: 나만의 이야기 생성기")

# 2. 사이드바: API 키 입력
with st.sidebar:
    api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")
    if not api_key:
        st.warning("⚠️ 키를 입력해야 이야기가 만들어집니다.")
        st.stop()
    st.success("✅ 연결되었습니다!")

# 3. 데이터 로드 (파일 읽기)
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
# 엑셀 파일의 이름이 조금 달라도 알아서 찾아내는 기능입니다.
def find_column(candidates, df):
    for col in df.columns:
        # 컬럼 이름에 후보 단어가 포함되어 있으면 선택 (예: '지역2' 안에 '지역'이 있음)
        for candidate in candidates:
            if candidate in str(col):
                return col
    return None

# 1. 지역 컬럼 찾기 ('지역', 'region', '도시' 중 하나)
region_col = find_column(['지역', '도시', 'region'], data)
# 2. 캐릭터 컬럼 찾기 ('캐릭터', '이름', 'name' 중 하나)
char_col = find_column(['캐릭터', '이름', 'name'], data)
# 3. 특징 컬럼 찾기 ('특징', '입버릇', '설명', 'desc' 중 하나)
feat_col = find_column(['특징', '입버릇', '설명', 'desc'], data)

# 컬럼을 못 찾았을 경우 대비 (첫번째, 두번째, 마지막 컬럼 강제 지정)
if region_col is None: region_col = data.columns[0]
if char_col is None: char_col = data.columns[1] if len(data.columns) > 1 else data.columns[0]
if feat_col is None: feat_col = data.columns[-1]

# 4. 화면 구성
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. 지역 선택")
    
    # 선택 상자
    selected_region = st.selectbox("어떤 지역으로 떠날까요?", data[region_col].unique())
    
    # 선택된 행 찾기
    row = data[data[region_col] == selected_region].iloc[0]
    
    # 데이터 가져오기 (비어있을 경우 대비)
    c_name = row[char_col] if pd.notna(row[char_col]) else "알 수 없는 캐릭터"
    f_desc = row[feat_col] if pd.notna(row[feat_col]) else "특징 없음"
    
    st.info(f"📍 **{selected_region}**\n\n👤 **캐릭터:** {c_name}\n\n✨ **특징(입버릇):** {f_desc}")

    # 전체 데이터 보기 버튼 (디버깅용)
    with st.expander("데이터 원본 확인하기"):
        st.dataframe(data)

with col2:
    st.subheader("2. 이야기 아이디어")
    user_input = st.text_area("어떤 사건을 만들까요?", placeholder="예: 주인공이 우연히 보물을 발견했다.", height=150)
    
    # --- 버튼은 여기에 있습니다! ---
    generate_btn = st.button("이야기 생성하기 ✨", type="primary")

# 5. 이야기 생성 로직
if generate_btn:
    if not user_input:
        st.warning("아이디어를 입력해주세요!")
    else:
        with st.spinner(f"AI가 '{selected_region}'의 이야기를 짓고 있습니다...✍️"):
            try:
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
