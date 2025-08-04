import streamlit as st
import time
from datetime import datetime, timedelta

# 페이지 설정
st.set_page_config(
    page_title="말씨맑음 CS 도우미",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 가상 채팅 시나리오 데이터
DEMO_SCENARIOS = {
    "한국어 고객": {
        "before": [
            {"role": "customer", "message": "안녕하세요! 주문한 상품이 언제 도착하나요?", "time": "14:30", "status": "normal"},
            {"role": "customer", "message": "진짜 너무 늦게 오네요. 환불하고 싶어요!", "time": "14:32", "status": "normal"},
            {"role": "customer", "message": "씨발 진짜 짜증나네요. 언제까지 기다려야 하는거야?", "time": "14:35", "status": "profanity"},
            {"role": "cs", "message": "죄송합니다. 배송 상태를 확인해드리겠습니다.", "time": "14:36", "status": "normal"},
            {"role": "cs", "message": "고객님, 주문하신 상품은 목요일 전에 배송될 예정입니다. 불편을 끼쳐 정말 죄송합니다.", "time": "14:37", "status": "generated"}
        ],
        "after": [
            {"role": "customer", "message": "안녕하세요! 주문한 상품이 언제 도착하나요?", "time": "14:30", "status": "normal"},
            {"role": "customer", "message": "진짜 너무 늦게 오네요. 환불하고 싶어요!", "time": "14:32", "status": "normal"},
            {"role": "customer", "message": "정말 답답하네요. 언제까지 기다려야 하는거야?", "time": "14:35", "status": "filtered"},
            {"role": "cs", "message": "죄송합니다. 배송 상태를 확인해드리겠습니다.", "time": "14:36", "status": "normal"},
            {"role": "cs", "message": "고객님, 주문하신 상품은 목요일 전에 배송될 예정입니다. 불편을 끼쳐 정말 죄송합니다.", "time": "14:37", "status": "generated"}
        ]
    },
    "영어 고객": {
        "before": [
            {"role": "customer", "message": "Hello! When will my order arrive?", "time": "15:20", "status": "normal"},
            {"role": "customer", "message": "This is taking too long. I want a refund!", "time": "15:22", "status": "normal"},
            {"role": "customer", "message": "Fuck this! How long do I have to wait?", "time": "15:25", "status": "profanity"},
            {"role": "cs", "message": "I apologize for the delay. Let me check the status.", "time": "15:26", "status": "normal"},
            {"role": "cs", "message": "Dear customer, your order will be delivered by Thursday. We sincerely apologize for the inconvenience.", "time": "15:27", "status": "generated"}
        ],
        "after": [
            {"role": "customer", "message": "Hello! When will my order arrive?", "time": "15:20", "status": "normal"},
            {"role": "customer", "message": "This is taking too long. I want a refund!", "time": "15:22", "status": "normal"},
            {"role": "customer", "message": "This is really frustrating! How long do I have to wait?", "time": "15:25", "status": "filtered"},
            {"role": "cs", "message": "I apologize for the delay. Let me check the status.", "time": "15:26", "status": "normal"},
            {"role": "cs", "message": "Dear customer, your order will be delivered by Thursday. We sincerely apologize for the inconvenience.", "time": "15:27", "status": "generated"}
        ]
    },
    "중국어 고객": {
        "before": [
            {"role": "customer", "message": "你好！我的订单什么时候到？", "time": "16:10", "status": "normal"},
            {"role": "customer", "message": "太慢了，我要退款！", "time": "16:12", "status": "normal"},
            {"role": "customer", "message": "妈的，到底要等多久？", "time": "16:15", "status": "profanity"},
            {"role": "cs", "message": "抱歉让您久等了，我来查看一下状态。", "time": "16:16", "status": "normal"},
            {"role": "cs", "message": "尊敬的顾客，您的订单将在周四前送达。给您带来不便，我们深表歉意。", "time": "16:17", "status": "generated"}
        ],
        "after": [
            {"role": "customer", "message": "你好！我的订单什么时候到？", "time": "16:10", "status": "normal"},
            {"role": "customer", "message": "太慢了，我要退款！", "time": "16:12", "status": "normal"},
            {"role": "customer", "message": "真是让人着急，到底要等多久？", "time": "16:15", "status": "filtered"},
            {"role": "cs", "message": "抱歉让您久等了，我来查看一下状态。", "time": "16:16", "status": "normal"},
            {"role": "cs", "message": "尊敬的顾客，您的订单将在周四前送达。给您带来不便，我们深表歉意。", "time": "16:17", "status": "generated"}
        ]
    }
}

def get_message_style(status, role):
    """메시지 상태와 역할에 따른 스타일 반환"""
    base_style = "padding: 12px 16px; margin: 8px 0; border-radius: 18px; word-wrap: break-word; position: relative; box-sizing: border-box;"
    
    if role == "customer":
        # 고객 메시지 (왼쪽 정렬)
        alignment = "margin-right: auto; margin-left: 0;"
        if status == "profanity":
            return f"{base_style} {alignment} background-color: #ffebee; border: 2px solid #f44336; color: #333;"
        elif status == "filtered":
            return f"{base_style} {alignment} background-color: #e8f5e8; border: 2px solid #4caf50; color: #333;"
        else:
            return f"{base_style} {alignment} background-color: #f0f0f0; color: #333;"
    else:
        # CS 담당자 메시지 (오른쪽 정렬)
        alignment = "margin-left: auto; margin-right: 0;"
        if status == "generated":
            return f"{base_style} {alignment} background-color: #fff3e0; border: 2px solid #ff9800; color: #333;"
        else:
            return f"{base_style} {alignment} background-color: #007bff; color: white;"

def get_status_icon(status):
    """상태에 따른 아이콘 반환"""
    if status == "profanity":
        return "🚫"
    elif status == "filtered":
        return "✅"
    elif status == "generated":
        return "🤖"
    else:
        return ""

def display_chat_messages(messages, title):
    """카카오톡 스타일 채팅 메시지 표시"""
    st.markdown(f"### {title}")
    
    # 채팅 컨테이너
    st.markdown("""
    <div style="
        background-color: #f8f9fa; 
        border-radius: 15px; 
        padding: 20px; 
        margin: 10px 0; 
        min-height: 400px;
        max-height: 500px;
        overflow-y: auto;
        border: 2px solid #e9ecef;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        position: relative;
        width: 100%;
        box-sizing: border-box;
    ">
    """, unsafe_allow_html=True)
    
    for msg in messages:
        role_icon = "👤" if msg["role"] == "customer" else "💼"
        role_text = "고객" if msg["role"] == "customer" else "CS 담당자"
        status_icon = get_status_icon(msg["status"])
        
        # 메시지 스타일 적용
        style = get_message_style(msg["status"], msg["role"])
        
        # 상태 아이콘을 메시지 옆에 표시
        status_display = f'<span style="margin-left: 8px; font-size: 14px;">{status_icon}</span>' if status_icon else ""
        
        st.markdown(f"""
        <div style="
            display: flex; 
            align-items: flex-start; 
            margin-bottom: 12px;
            width: 100%;
            position: relative;
            box-sizing: border-box;
        ">
            <div style="
                {style}
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                max-width: 75%;
                min-width: 120px;
                position: relative;
                box-sizing: border-box;
                word-wrap: break-word;
                overflow-wrap: break-word;
            ">
                <div style="
                    display: flex; 
                    justify-content: space-between; 
                    align-items: center; 
                    margin-bottom: 4px;
                    font-size: 12px;
                    color: #666;
                ">
                    <span style="font-weight: bold;">
                        {role_icon} {role_text} {status_display}
                    </span>
                    <span>{msg['time']}</span>
                </div>
                <div style="
                    line-height: 1.4; 
                    font-size: 14px;
                    word-wrap: break-word;
                    overflow-wrap: break-word;
                ">{msg['message']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

def main():
    # 헤더
    st.markdown("""
    <div style="text-align: center; padding: 30px; background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%); border-radius: 15px; margin-bottom: 30px;">
        <h1 style="color: #856404; margin: 0; font-size: 2.5em;">💬 말씨맑음 CS 도우미</h1>
        <p style="color: #856404; margin: 10px 0 0 0; font-size: 20px;">AI 기반 고객 서비스 지원 도구 데모</p>
        <p style="color: #856404; margin: 5px 0 0 0; font-size: 16px;">언어 감지 • 욕설 필터링 • 실시간 번역 • 답안 생성</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 언어 선택
    language = st.selectbox(
        "고객 언어 선택:",
        ["한국어 고객", "영어 고객", "중국어 고객"],
        help="다른 언어의 고객 시나리오를 확인해보세요"
    )
    
    # Before/After 비교
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🚫 Before (필터링 전)")
        st.markdown("*욕설이 포함된 원본 메시지*")
        display_chat_messages(DEMO_SCENARIOS[language]["before"], "")
    
    with col2:
        st.markdown("### ✅ After (필터링 후)")
        st.markdown("*AI가 처리한 개선된 메시지*")
        display_chat_messages(DEMO_SCENARIOS[language]["after"], "")
    
    # 기능 설명
    st.markdown("---")
    st.markdown("### 🎯 주요 기능")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: #e3f2fd; border-radius: 10px;">
            <h3>🌐 언어 감지</h3>
            <p>자동으로 15개 언어 감지</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: #f3e5f5; border-radius: 10px;">
            <h3>🚫 욕설 필터링</h3>
            <p>부적절한 표현 자동 감지 및 변환</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: #e8f5e8; border-radius: 10px;">
            <h3>🔄 실시간 번역</h3>
            <p>다국어 고객과의 원활한 소통</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style="text-align: center; padding: 20px; background: #fff3e0; border-radius: 10px;">
            <h3>🤖 답안 생성</h3>
            <p>AI가 친절하고 정중한 답변 생성</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 성능 지표
    st.markdown("---")
    st.markdown("### 📊 성능 지표")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("번역 정확도", "98.5%", "↑ 2.3%")
    
    with col2:
        st.metric("응답 시간", "0.8초", "↓ 0.3초")
    
    with col3:
        st.metric("언어 지원", "15개", "↑ 3개")
    
    with col4:
        st.metric("고객 만족도", "4.8/5.0", "↑ 0.4점")
    
    # 푸터
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 14px; padding: 20px;">
        <p>💡 이 데모는 실제 CS 환경에서 사용되는 AI 기반 도구입니다.</p>
        <p>언어 감지, 욕설 필터링, 실시간 번역으로 CS 업무 효율성을 극대화하세요!</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 
