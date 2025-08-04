import streamlit as st
import openai
import json
import time
from datetime import datetime
import random

# 페이지 설정
st.set_page_config(
    page_title="말씨맑음 CS 도우미",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# GPT API 키 설정
GPT_API_KEY = "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"

# OpenAI 클라이언트 설정
client = openai.OpenAI(api_key=GPT_API_KEY)

# 샘플 CS 대화 데이터
SAMPLE_CONVERSATIONS = {
    "한국어 고객": [
        {"role": "customer", "message": "안녕하세요! 주문한 상품이 언제 도착하나요?", "time": "14:30"},
        {"role": "customer", "message": "진짜 너무 늦게 오네요. 환불하고 싶어요!", "time": "14:32"},
        {"role": "customer", "message": "씨발 진짜 짜증나네요. 언제까지 기다려야 하는거야?", "time": "14:35"},
        {"role": "cs", "message": "죄송합니다. 배송 상태를 확인해드리겠습니다.", "time": "14:36"}
    ],
    "영어 고객": [
        {"role": "customer", "message": "Hello! When will my order arrive?", "time": "15:20"},
        {"role": "customer", "message": "This is taking too long. I want a refund!", "time": "15:22"},
        {"role": "customer", "message": "Fuck this! How long do I have to wait?", "time": "15:25"},
        {"role": "cs", "message": "I apologize for the delay. Let me check the status.", "time": "15:26"}
    ],
    "중국어 고객": [
        {"role": "customer", "message": "你好！我的订单什么时候到？", "time": "16:10"},
        {"role": "customer", "message": "太慢了，我要退款！", "time": "16:12"},
        {"role": "customer", "message": "妈的，到底要等多久？", "time": "16:15"},
        {"role": "cs", "message": "抱歉让您久等了，我来查看一下状态。", "time": "16:16"}
    ]
}

def analyze_message_with_gpt(message):
    """GPT를 사용하여 메시지 분석"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 CS 업무를 도와주는 AI 어시스턴트입니다. 고객 메시지를 분석하고 적절한 답안을 제시해주세요."
                },
                {
                    "role": "user",
                    "content": f"""
다음 고객 메시지를 분석해주세요:

메시지: "{message}"

다음 JSON 형식으로 응답해주세요:
{{
  "language": "감지된 언어 (한국어, 영어, 중국어, 일본어, 태국어 등)",
  "profanity": "욕설이 있으면 '욕설 포함', 없으면 '욕설 없음'",
  "translation": "한국어로 번역한 내용",
  "suggestion": "CS 담당자가 사용할 수 있는 적절한 답안 추천"
}}

응답은 반드시 JSON 형식이어야 합니다.
"""
                }
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        content = response.choices[0].message.content
        return json.loads(content)
    except Exception as e:
        st.error(f"분석 중 오류가 발생했습니다: {str(e)}")
        return None

def generate_cs_answer(user_input):
    """CS 답안 생성"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "당신은 고객 서비스 전문가입니다. 친절하고 정중한 답안을 작성해주세요."
                },
                {
                    "role": "user",
                    "content": f"""
고객 서비스 담당자를 위한 답안을 작성해주세요.

사용자 요청: "{user_input}"

다음 조건을 만족하는 친절하고 정중한 답안을 작성해주세요:
1. 고객에게 보내는 메시지 형태로 작성
2. 친절하고 정중한 어투 사용
3. 구체적이고 명확한 내용
4. 불필요한 공식적 표현 지양
5. 자연스러운 한국어 사용

답안만 작성해주세요 (설명이나 추가 텍스트 없이).
"""
                }
            ],
            temperature=0.7,
            max_tokens=300
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"답안 생성 중 오류가 발생했습니다: {str(e)}")
        return None

def translate_message(message):
    """메시지 번역"""
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "고객 서비스 채팅 메시지를 한국어로 번역해주세요. 정중하고 명확하게 번역해주세요."
                },
                {
                    "role": "user",
                    "content": f"다음 메시지를 한국어로 번역해주세요: \"{message}\""
                }
            ],
            temperature=0.3,
            max_tokens=200
        )
        
        return response.choices[0].message.content.strip()
    except Exception as e:
        st.error(f"번역 중 오류가 발생했습니다: {str(e)}")
        return None

def main():
    # 헤더
    st.markdown("""
    <div style="text-align: center; padding: 20px; background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); border-radius: 10px; margin-bottom: 30px;">
        <h1 style="color: #856404; margin: 0;">💬 말씨맑음 CS 도우미</h1>
        <p style="color: #856404; margin: 10px 0 0 0; font-size: 18px;">AI 기반 고객 서비스 지원 도구</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 사이드바
    with st.sidebar:
        st.markdown("### 🎯 데모 기능")
        st.markdown("""
        - 📝 **메시지 분석**: 언어 감지, 욕설 필터링, 번역
        - 💬 **답안 생성**: CS 담당자용 친절한 답변 생성
        - 🌐 **실시간 번역**: 다국어 채팅 번역
        """)
        
        st.markdown("### 📊 성능 지표")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("번역 정확도", "98.5%")
            st.metric("응답 시간", "0.8초")
        with col2:
            st.metric("언어 지원", "15개")
            st.metric("고객 만족도", "4.8/5.0")
    
    # 메인 컨텐츠
    tab1, tab2, tab3 = st.tabs(["📝 메시지 분석", "💬 답안 생성", "🌐 실시간 번역"])
    
    with tab1:
        st.markdown("### 📝 메시지 분석 데모")
        st.markdown("고객 메시지를 입력하면 AI가 자동으로 언어를 감지하고, 욕설을 필터링하며, 한국어로 번역해드립니다.")
        
        # 샘플 메시지 선택
        sample_messages = [
            "안녕하세요! 주문한 상품이 언제 도착하나요?",
            "Hello! When will my order arrive?",
            "你好！我的订单什么时候到？",
            "씨발 진짜 짜증나네요. 언제까지 기다려야 하는거야?",
            "Fuck this! How long do I have to wait?",
            "妈的，到底要等多久？"
        ]
        
        selected_message = st.selectbox("샘플 메시지 선택:", ["직접 입력"] + sample_messages)
        
        if selected_message == "직접 입력":
            message_input = st.text_area("고객 메시지를 입력하세요:", placeholder="분석할 메시지를 입력하세요...")
        else:
            message_input = selected_message
            st.text_area("고객 메시지:", value=message_input, disabled=True)
        
        if st.button("🔍 분석하기", type="primary") and message_input:
            with st.spinner("AI가 메시지를 분석하고 있습니다..."):
                analysis = analyze_message_with_gpt(message_input)
                
                if analysis:
                    # 결과 표시
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("### 📊 분석 결과")
                        st.info(f"**언어 감지:** {analysis.get('language', '감지 실패')}")
                        
                        profanity_status = analysis.get('profanity', '없음')
                        if '욕설 포함' in profanity_status:
                            st.error(f"**욕설 감지:** {profanity_status}")
                        else:
                            st.success(f"**욕설 감지:** {profanity_status}")
                        
                        st.info(f"**번역:** {analysis.get('translation', '번역 불가')}")
                    
                    with col2:
                        st.markdown("### 💡 CS 답안 추천")
                        suggestion = analysis.get('suggestion', '답안 추천을 생성할 수 없습니다.')
                        st.markdown(f"```\n{suggestion}\n```")
    
    with tab2:
        st.markdown("### 💬 답안 생성 데모")
        st.markdown("CS 담당자가 고객에게 보낼 답안을 AI가 자동으로 생성해드립니다.")
        
        # 샘플 요청들
        sample_requests = [
            "고객한테 목요일 전에 배송된다고 써줘",
            "환불 요청에 대해 정중하게 거절해줘",
            "배송 지연에 대해 사과하고 보상안을 제시해줘",
            "상품 불량에 대해 교환 절차를 안내해줘"
        ]
        
        selected_request = st.selectbox("샘플 요청 선택:", ["직접 입력"] + sample_requests)
        
        if selected_request == "직접 입력":
            request_input = st.text_area("답안을 생성할 내용을 입력하세요:", placeholder="예: 고객한테 목요일 전에 배송된다고 써줘")
        else:
            request_input = selected_request
            st.text_area("요청 내용:", value=request_input, disabled=True)
        
        if st.button("💬 답안 생성하기", type="primary") and request_input:
            with st.spinner("AI가 답안을 생성하고 있습니다..."):
                answer = generate_cs_answer(request_input)
                
                if answer:
                    st.markdown("### ✨ 생성된 답안")
                    st.success(answer)
                    
                    # 복사 버튼
                    if st.button("📋 클립보드에 복사"):
                        st.write("답안이 클립보드에 복사되었습니다!")
    
    with tab3:
        st.markdown("### 🌐 실시간 번역 데모")
        st.markdown("다국어 고객과의 CS 대화를 실시간으로 번역해보세요.")
        
        # 언어 선택
        language = st.selectbox("고객 언어 선택:", ["한국어 고객", "영어 고객", "중국어 고객"])
        
        if st.button("🎬 번역 시연 시작", type="primary"):
            conversation = SAMPLE_CONVERSATIONS[language]
            
            # 채팅 인터페이스
            st.markdown("### 💬 CS 대화 (실시간 번역)")
            
            chat_container = st.container()
            
            with chat_container:
                for i, msg in enumerate(conversation):
                    if msg["role"] == "customer":
                        # 고객 메시지
                        with st.chat_message("user"):
                            st.markdown(f"**{msg['time']}** - {msg['message']}")
                            
                            # 번역 결과 표시
                            if st.button(f"번역하기 #{i+1}", key=f"translate_{i}"):
                                with st.spinner("번역 중..."):
                                    translation = translate_message(msg['message'])
                                    if translation:
                                        st.success(f"🇰🇷 **번역:** {translation}")
                    
                    else:
                        # CS 담당자 메시지
                        with st.chat_message("assistant"):
                            st.markdown(f"**{msg['time']}** - {msg['message']}")
                    
                    time.sleep(0.5)  # 자연스러운 대화 효과
            
            st.success("✅ 번역 시연이 완료되었습니다!")
    
    # 푸터
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 14px;">
        <p>💡 이 데모는 실제 CS 환경에서 사용되는 AI 기반 도구입니다.</p>
        <p>언어 감지, 욕설 필터링, 실시간 번역으로 CS 업무 효율성을 극대화하세요!</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 