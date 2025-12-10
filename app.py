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

# 3. 데이터 로드 (인코딩 문제 해결사)
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

# 데이터가 잘 읽혔는지 확인
if data.empty:
    st.error("❌ 데이터 파일(data.csv)을 읽을 수 없습니다. 엑셀 파일의 내용이 비어있거나 형식이 잘못되었는지 확인해주세요.")
    st.stop()

# 4. 화면 구성
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. 지역 선택")
    # CSV 파일의 첫 번째 열(보통 지역명)을 선택 상자로 만듦
    # 주의: 엑셀 파일의 첫 줄(헤더)이 '지역', '캐릭터', '특징' 등으로 되어있다고 가정합니다.
    # 만약 에러가 난다면 엑셀 파일의 첫 줄 제목을 확인해야 합니다.
    
    try:
        selected_region = st.selectbox("어떤 지역으로 떠날까요?", data['지역'])
        
        # 선택된 지역의 행(Row) 찾기
        selected_row = data[data['지역'] == selected_region].iloc[0]
        
        # 엑셀 컬럼 이름에 맞춰서 변수 저장 (컬럼명이 다르면 여기서 에러가 날 수 있음)
        character = selected_row['캐릭터']
        feature = selected_row['특징']
        
        st.info(f"📍 **{selected_region}**\n\n👤 캐릭터: {character}\n\n✨ 특징: {feature}")
        
    except KeyError:
        st.error("⚠️ 엑셀 파일의 맨 윗줄(제목)이 '지역', '캐릭터', '특징'으로 되어 있는지 확인해주세요!")
        st.dataframe(data.head()) # 데이터 미리보기 제공
        st.stop()

with col2:
    st.subheader("2. 이야기 아이디어")
    user_input = st.text_area("어떤 사건을 만들까요?", placeholder="예: 주인공이 우연히 보물을 발견했다.", height=150)
    
    generate_btn = st.button("이야기 생성하기 ✨", type="primary")

# 5. 진짜 이야기 생성 로직 (AI 호출)
if generate_btn:
    if not user_input:
        st.warning("아이디어를 입력해주세요!")
    else:
        with st.spinner(f"AI가 '{selected_region}'의 이야기를 짓고 있습니다...✍️"):
            try:
                client = OpenAI(api_key=api_key)
                
                prompt = f"""
                당신은 창의적인 소설가입니다. 아래 정보를 바탕으로 재미있는 짧은 소설을 써주세요.
                
                - 배경 지역: {selected_region} ({feature})
                - 등장 인물: {character}
                - 주요 사건: {user_input}
                
                이야기는 500자 내외로 흥미진진하게 써주세요.
                제목도 멋지게 지어주세요.
                """
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini", 
                    messages=[{"role": "user", "content": prompt}]
                )
                
                story = response.choices[0].message.content
                
                st.markdown("---")
                st.success("🎉 이야기가 완성되었습니다!")
                st.markdown(story)
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
