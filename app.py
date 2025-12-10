import streamlit as st
import pandas as pd
from openai import OpenAI  # OpenAI를 불러오는 주문

# 1. 페이지 설정
st.set_page_config(page_title="나만의 이야기 생성기", layout="wide")
st.title("🧙‍♂️ 나만의 이야기 생성기 (AI 작동중)")

# 2. 사이드바: API 키 입력
with st.sidebar:
    api_key = st.text_input("OpenAI API Key를 입력하세요", type="password")
    
    if not api_key:
        st.warning("⚠️ 키를 입력해야 이야기가 만들어집니다.")
        st.stop()
    
    st.success("✅ 연결되었습니다!")

# 3. 샘플 데이터 (파일 없이 테스트)
data = pd.DataFrame({
    '지역': ['서울 종로', '부산 해운대', '제주도', '경주'],
    '캐릭터': ['김시간 (골동품 가게 주인)', '박파도 (서퍼)', '한라봉 (요정)', '이천년 (신라의 유령)'],
    '특징': ['과거와 현재가 공존함', '열정적이고 활기참', '신비롭고 자연친화적', '역사가 살아숨쉼']
})

# 4. 화면 구성
col1, col2 = st.columns(2)

with col1:
    st.subheader("1. 지역 선택")
    selected_region = st.selectbox("어떤 지역으로 떠날까요?", data['지역'])
    
    # 선택된 지역의 정보 가져오기
    selected_row = data[data['지역'] == selected_region].iloc[0]
    character = selected_row['캐릭터']
    feature = selected_row['특징']
    
    st.info(f"🗺️ **{selected_region}**\n\n👤 캐릭터: {character}\n\n✨ 특징: {feature}")

with col2:
    st.subheader("2. 이야기 아이디어")
    user_input = st.text_area("어떤 사건을 만들까요?", placeholder="예: 주인공이 우연히 보물을 발견했다.", height=150)
    
    generate_btn = st.button("이야기 생성하기 ✨", type="primary")

# 5. 진짜 이야기 생성 로직 (AI 호출)
if generate_btn:
    if not user_input:
        st.warning("아이디어를 입력해주세요!")
    else:
        # 여기에 진짜 AI를 부르는 코드가 들어갑니다
        with st.spinner("AI가 열심히 이야기를 짓고 있습니다...✍️"):
            try:
                # 1) AI에게 줄 명령서 만들기
                client = OpenAI(api_key=api_key)
                
                prompt = f"""
                당신은 창의적인 소설가입니다. 아래 정보를 바탕으로 재미있는 짧은 소설을 써주세요.
                
                - 배경 지역: {selected_region} ({feature})
                - 등장 인물: {character}
                - 주요 사건: {user_input}
                
                이야기는 500자 내외로 흥미진진하게 써주세요.
                제목도 멋지게 지어주세요.
                """
                
                # 2) AI에게 명령 보내기 (GPT-4o-mini 모델 사용)
                response = client.chat.completions.create(
                    model="gpt-4o-mini", 
                    messages=[{"role": "user", "content": prompt}]
                )
                
                # 3) 결과 받아서 화면에 보여주기
                story = response.choices[0].message.content
                
                st.markdown("---")
                st.success("🎉 이야기가 완성되었습니다!")
                st.markdown(story)
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
