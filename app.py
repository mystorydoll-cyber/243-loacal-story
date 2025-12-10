import streamlit as st
import pandas as pd
from openai import OpenAI
import os

# 1. 페이지 설정
st.set_page_config(page_title="243개 지역: 캐릭터 스튜디오", layout="wide")
st.title("🎨 243개 지역: 캐릭터 스튜디오")

# 2. API 키 설정 (자동 로그인)
try:
    api_key = st.secrets["OPENAI_API_KEY"]
except:
    st.error("🚨 API 키가 설정되지 않았습니다.")
    st.stop()

# 3. 데이터 로드
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

# 스마트 컬럼 찾기
def find_column(candidates, df):
    for col in df.columns:
        for candidate in candidates:
            if candidate in str(col):
                return col
    return None

region_col = find_column(['지역', '도시', 'region'], data)
char_col = find_column(['캐릭터', '이름', 'name'], data)
feat_col = find_column(['특징', '입버릇', '설명', 'desc'], data)

# 4. 화면 구성
col1, col2 = st.columns([1, 1.5]) # 왼쪽(이미지), 오른쪽(생성도구)

with col1:
    st.subheader("1. 오리지널 캐릭터")
    
    # 지역 선택
    selected_region = st.selectbox("지역을 선택하세요", data[region_col].unique())
    
    # 선택된 캐릭터 정보 찾기
    row = data[data[region_col] == selected_region].iloc[0]
    c_name = row[char_col] if pd.notna(row[char_col]) else "알 수 없는 캐릭터"
    f_desc = row[feat_col] if pd.notna(row[feat_col]) else "특징 없음"
    
    st.info(f"선택: **{c_name}** ({selected_region})")
    
    # --- [이미지 찾기 기능] ---
    # 깃허브 images 폴더에 있는 파일을 찾습니다.
    img_path_png = f"images/{c_name}.png"
    img_path_jpg = f"images/{c_name}.jpg"
    
    # 파일이 있으면 화면에 보여주고, 없으면 안내 문구를 띄웁니다.
    if os.path.exists(img_path_png):
        st.image(img_path_png, caption=f"✅ {c_name} 원본 디자인", use_container_width=True)
    elif os.path.exists(img_path_jpg):
        st.image(img_path_jpg, caption=f"✅ {c_name} 원본 디자인", use_container_width=True)
    else:
        st.warning(f"📷 아직 '{c_name}'의 이미지가 등록되지 않았습니다.")
        st.caption(f"('images/{c_name}.png' 파일을 올려주세요)")

with col2:
    st.subheader("2. 새로운 모습 상상하기")
    
    st.write(f"**{c_name}**의 원래 특징을 유지하면서 새로운 모습을 그려볼까요?")
    st.info(f"💡 원래 특징: {f_desc}")
    
    user_request = st.text_input("어떤 모습을 보고 싶나요?", placeholder="예: 한복을 입고 춤추는 모습")
    style = st.radio("그림 스타일", ["3D 애니메이션", "웹툰/일러스트", "실사 사진"], horizontal=True)
    
    if st.button("새로운 이미지 생성하기 ✨", type="primary"):
        if not user_request:
            st.warning("내용을 입력해주세요!")
        else:
            client = OpenAI(api_key=api_key)
            with st.spinner("AI 화가가 그림을 그리는 중입니다..."):
                try:
                    # 프롬프트: 원본 특징 + 사용자 요청
                    prompt = f"""
                    Draw a character named '{c_name}'.
                    [Original Features]: {f_desc}
                    [User Request]: {user_request}
                    [Style]: {style}
                    Keep the character's core identity but change the action/outfit as requested.
                    """
                    
                    response = client.images.generate(
                        model="dall-e-3",
                        prompt=prompt,
                        size="1024x1024",
                        quality="standard",
                        n=1
                    )
                    
                    st.image(response.data[0].url, caption="AI가 생성한 새로운 모습")
                    st.success("완성되었습니다!")
                    
                except Exception as e:
                    st.error(f"오류 발생: {e}")
