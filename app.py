import streamlit as st
import openai
import pandas as pd
import os
st.error(f"📂 파일 목록: {os.listdir('.')}")
import os
st.error(f"현재 파일 목록: {os.listdir('.')}")
# 1. 페이지 기본 설정
st.set_page_config(page_title="243개 지역: 나만의 이야기 생성기", page_icon="🗺️")

st.title("🗺️ 243개 지역: 나만의 이야기 생성기")
st.write("당신이 선택한 지역의 캐릭터와 함께 새로운 전설을 만들어보세요!")

# Secrets에서 키 가져오기 (없으면 사이드바 입력)
if "OPENAI_API_KEY" in st.secrets:
    api_key = st.secrets["OPENAI_API_KEY"]
else:
    api_key = st.sidebar.text_input("OpenAI API Key를 입력하세요", type="password")

# 2. 데이터 불러오기
@st.cache_data
def load_data():
    try:
        # 엑셀(CSV) 파일 읽기
        return pd.read_csv("data.csv")
    except:
        # 윈도우에서 저장한 파일인 경우 인코딩 처리
        return pd.read_csv("data.csv", encoding='cp949')

try:
    df = load_data()
    # 데이터가 잘 읽혔다면 사이드바에 표시 (확인용)
    st.sidebar.success(f"📂 {len(df)}개 지역 데이터 준비 완료!")
except Exception as e:
    st.error(f"데이터 파일(data.csv)을 읽을 수 없습니다. 깃허브에 파일이 있는지 확인해주세요!\n에러 내용: {e}")
    st.stop()

# 3. 사용자 인터페이스 (UI) 구성
# '지역' 컬럼을 기준으로 선택 상자 만들기
selected_region = st.selectbox("어떤 지역의 이야기를 원하시나요?", df['지역'].unique())

if selected_region:
    # 선택된 지역의 모든 정보 가져오기
    info = df[df['지역'] == selected_region].iloc[0]

    # 화면에 정보 예쁘게 보여주기
    st.markdown(f"### {info['제목']}") # 제목을 크게 표시
    st.info(f"""
    * **👤 이름:** {info['이름']}
    * **🗣️ 입버릇:** "{info['입버릇']}"
    * **💖 좋아하는 것:** {info['좋아하는 것']}
    * **✨ 성격:** {info['성격']}
    * **🎒 아이템:** {info['외형 아이템']}
    * **📜 스토리:** {info['지역테마 스토리']}
    """)
    
    # 이미지 설명은 화면엔 안 보여줘도 되지만, 필요하면 아래 주석(#)을 풀어서 보세요
    # st.caption(f"이미지 컨셉: {info['이미지용 한줄 설명']}")

    # 사용자 아이디어 입력
    user_idea = st.text_area("당신의 상상력을 더해주세요! (예: 주인공이 갑자기 아이템을 잃어버린다면?)")

    # 이야기 생성 버튼
    if st.button("새로운 이야기 만들기 ✨"):
        if not api_key:
            st.warning("API Key가 설정되지 않았습니다.")
        else:
            try:
                client = openai.OpenAI(api_key=api_key)
                
                # AI에게 보낼 상세한 명령서 (프롬프트)
                prompt = f"""
                당신은 창의적인 판타지 소설가입니다. 아래 캐릭터 설정을 완벽하게 반영하여 새로운 단편 소설을 써주세요.
                
                [캐릭터 및 배경 설정]
                - 지역: {info['지역']}
                - 소설 제목: {info['제목']}
                - 주인공 이름: {info['이름']}
                - 성격: {info['성격']} (이 성격이 드러나는 행동을 묘사할 것)
                - 입버릇: "{info['입버릇']}" (대화 중에 이 입버릇을 반드시 1회 이상 사용할 것)
                - 좋아하는 것: {info['좋아하는 것']}
                - 소지 아이템: {info['외형 아이템']}
                - 원작 배경 스토리: {info['지역테마 스토리']}
                
                [사용자 추가 아이디어]
                상황: {user_idea}
                
                [요청사항]
                1. 위 '원작 배경 스토리'와 '사용자 아이디어'를 자연스럽게 연결해주세요.
                2. 주인공의 성격과 말투(입버릇)를 살려서 생동감 있게 묘사해주세요.
                3. 글자 수는 600자 내외로 작성해주세요.
                """
                
                with st.spinner(f"AI가 '{info['이름']}'의 이야기를 쓰고 있습니다..."):
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo", # 더 똑똑한 모델을 원하면 "gpt-4"로 변경 가능
                        messages=[{"role": "user", "content": prompt}]
                    )
                    story_result = response.choices[0].message.content
                
                # 결과 출력
                st.markdown("---")
                st.subheader(f"📖 {info['이름']}의 새로운 모험")
                st.write(story_result)
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")
