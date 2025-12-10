import streamlit as st
import openai

# 1. 페이지 기본 설정
st.set_page_config(page_title="나만의 지역 이야기 만들기", page_icon="🗺️")

st.title("🗺️ 243개 지역: 나만의 이야기 생성기")
st.write("원하는 지역을 선택하고, 당신만의 상상력을 더해 새로운 이야기를 만들어보세요!")

# 2. 가상의 데이터 (나중에는 243개 데이터베이스나 엑셀 파일로 대체합니다)
# 예시로 3개만 넣어두었습니다.
region_data = {
    "서울 종로": {
        "story": "과거와 현재가 공존하는 거리, 오래된 골목마다 시간 여행자가 숨어 있다.",
        "character": "김시간 (회중시계를 든 골동품 가게 주인)"
    },
    "부산 해운대": {
        "story": "푸른 바다 아래 용궁으로 가는 비밀 통로가 존재한다.",
        "character": "박파도 (말하는 갈매기와 대화하는 서퍼)"
    },
    "전주 한옥마을": {
        "story": "한복을 입으면 조선시대의 기억을 엿볼 수 있는 능력이 생긴다.",
        "character": "이단아 (비밀을 간직한 한복 디자이너)"
    }
}

# 사이드바에 API 키 입력 (보안을 위해)
api_key = st.sidebar.text_input("sk-proj—3XaLlqjVIwKOhrX8tCeLFZh-U8HJeTHrO7o9VUe2AlvnS-MjGwdtO4-wxckPBzE4EwXcsZSmcT3BlbkFJAUpMjG9P4w2cGsMeYXzfN8r27UZE5QzTzqMkn-lTPE8kS1HbTtB042HAQP0xXMHFlox8Lg4tcA", type="password")

# 3. 사용자 인터페이스 (UI) 구성
# 지역 선택
selected_region = st.selectbox("어떤 지역의 이야기를 원하시나요?", list(region_data.keys()))

if selected_region:
    # 선택된 지역 정보 보여주기
    info = region_data[selected_region]
    st.info(f"**기본 설정**\n\n* **스토리:** {info['story']}\n* **캐릭터:** {info['character']}")

    # 사용자 입력 받기
    user_idea = st.text_area("당신의 아이디어를 더해주세요! (예: 주인공이 갑자기 초능력을 얻게 된다면?)")

    # 이야기 생성 버튼
    if st.button("새로운 이야기 만들기 ✨"):
        if not api_key:
            st.warning("먼저 왼쪽 사이드바에 OpenAI API Key를 입력해주세요.")
            # API 키가 없을 때 테스트용 가짜 응답
            st.markdown("---")
            st.subheader("🤖 AI가 만든 이야기 (테스트 모드)")
            st.write(f"테스트 모드입니다.\n\n'{selected_region}'의 '{info['character']}'가 '{user_idea}'라는 상황을 겪는 멋진 이야기가 생성될 예정입니다!")
        else:
            # 실제 AI 호출 로직
            try:
                client = openai.OpenAI(api_key=api_key)
                
                prompt = f"""
                당신은 창의적인 소설가입니다. 아래 설정을 바탕으로 새로운 짧은 소설을 써주세요.
                
                [기본 설정]
                - 지역: {selected_region}
                - 배경 스토리: {info['story']}
                - 주인공: {info['character']}
                
                [사용자 아이디어]
                {user_idea}
                
                위 내용을 결합하여 흥미진진한 이야기를 500자 내외로 작성해 주세요.
                """
                
                with st.spinner("AI가 열심히 이야기를 쓰고 있습니다..."):
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo", # 또는 gpt-4
                        messages=[{"role": "user", "content": prompt}]
                    )
                    story_result = response.choices[0].message.content
                
                st.markdown("---")
                st.subheader(f"📖 {selected_region}의 새로운 전설")
                st.write(story_result)
                
            except Exception as e:
                st.error(f"오류가 발생했습니다: {e}")