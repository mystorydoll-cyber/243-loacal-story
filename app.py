import streamlit as st
import pandas as pd
from openai import OpenAI
import os
import unicodedata # 한글 자모 분리 해결사

# 1. 페이지 설정
st.set_page_config(page_title="243개 지역: 나만의 이야기 & 캐릭터", layout="wide")
st.title("🗺️ 243개 지역: 나만의 이야기 & 캐릭터 세상")

# 2. API 키 설정
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

# --- [맥북 한글 문제 해결 함수] ---
def find_image_path(char_name):
    # 1. images 폴더가 없으면 포기
    if not os.path.exists('images'):
        return None
        
    # 2. 엑셀에서 가져온 이름을 'NFC(완성형)'로 통일
    target_name = unicodedata.normalize('NFC', str(char_name))
    
    # 3. 폴더에 있는 모든 파일을 하나씩 검사
    for filename in os.listdir('images'):
        # 파일 이름도 'NFC(완성형)'로 변환해서 비교
        normalized_file = unicodedata.normalize('NFC', filename)
        
        # 확장자(.png) 떼고 이름만 비교
        name_only = os.path.splitext(normalized_file)[0]
        
        if target_name == name_only:
            return os.path.join('images', filename) # 찾았다!
            
    return None # 못 찾음

# 4. 화면 구성
tab1, tab2 = st.tabs(["📖 나만의 이야기 작가", "🎨 캐릭터 변형 스튜디오"])

# [탭 1] 이야기 생성기
with tab1:
    st.header("1. 지역 전설을 바탕으로 소설 쓰기")
    col1_story, col2_story = st.columns([1, 2])
    
    with col1_story:
        region_story = st.selectbox("어떤 지역의 이야기를 쓸까요?", data[region_col].unique(), key="story_select")
        row_s = data[data[region_col] == region_story].iloc[0]
        c_name_s = row_s[char_col] if pd.notna(row_s[char_col]) else "알 수 없음"
        f_desc_s = row_s[feat_col] if pd.notna(row_s[feat_col]) else "특징 없음"
        st.info(f"📍 **{region_story}**\n\n👤 **{c_name_s}**\n\n✨ {f_desc_s}")

    with col2_story:
        user_input_story = st.text_area("어떤 사건이 일어나나요?", placeholder="예: 주인공이 우연히 보물을 발견했다.", height=150)
        if st.button("이야기 생성하기 ✨", key="story_btn", type="primary"):
            if not user_input_story:
                st.warning("내용을 입력해주세요!")
            else:
                client = OpenAI(api_key=api_key)
                with st.spinner("AI 작가가 집필 중입니다...✍️"):
                    try:
                        prompt = f"배경: {region_story}, 캐릭터: {c_name_s}, 특징: {f_desc_s}, 사건: {user_input_story}. 재미있는 500자 소설을 써주세요."
                        response = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "user", "content": prompt}])
                        st.success("🎉 이야기가 완성되었습니다!")
                        st.markdown(response.choices[0].message.content)
                    except Exception as e:
                        st.error(f"오류: {e}")

# [탭 2] 캐릭터 스튜디오
with tab2:
    st.header("2. 캐릭터의 새로운 모습 그리기")
    col1_img, col2_img = st.columns([1, 1.5])
    
    with col1_img:
        region_img = st.selectbox("어떤 캐릭터를 변신시킬까요?", data[region_col].unique(), key="img_select")
        row_i = data[data[region_col] == region_img].iloc[0]
        c_name_i = row_i[char_col] if pd.notna(row_i[char_col]) else "알 수 없음"
        f_desc_i = row_i[feat_col] if pd.notna(row_i[feat_col]) else "특징 없음"
        st.info(f"선택: **{c_name_i}**")
        
        # --- [스마트 이미지 찾기 적용] ---
        found_image_path = find_image_path(c_name_i)
        
        if found_image_path:
            st.image(found_image_path, caption=f"✅ {c_name_i} 원본", use_container_width=True)
        else:
            st.warning("📷 등록된 이미지가 없습니다.")
            st.caption(f"('images/{c_name_i}.png' 파일을 올려주세요)")
            
            # 디버깅용: 실제 폴더에 무슨 파일이 있는지 보여줌 (범인 색출)
            with st.expander("📂 서버에 있는 파일 목록 보기 (디버깅)"):
                if os.path.exists('images'):
                    st.write(os.listdir('images'))
                else:
                    st.write("images 폴더가 없습니다.")

    with col2_img:
        st.markdown(f"**{c_name_i}**의 특징: {f_desc_i}")
        user_request_img = st.text_input("원하는 모습 입력", placeholder="예: 한복을 입고 춤추는 모습", key="img_input")
        style = st.radio("그림 스타일", ["3D 애니메이션", "웹툰", "실사"], horizontal=True, key="img_style")
        
        if st.button("새로운 이미지 생성하기 🎨", key="img_btn", type="primary"):
            if not user_request_img:
                st.warning("요청 사항을 입력해주세요!")
            else:
                client = OpenAI(api_key=api_key)
                with st.spinner("그림 그리는 중..."):
                    try:
                        prompt = f"Draw '{c_name_i}'. Features: {f_desc_i}. Request: {user_request_img}. Style: {style}."
                        response = client.images.generate(model="dall-e-3", prompt=prompt, size="1024x1024", quality="standard", n=1)
                        st.image(response.data[0].url, caption="AI 생성 이미지")
                        st.success("완성!")
                    except Exception as e:
                        st.error(f"오류: {e}")
