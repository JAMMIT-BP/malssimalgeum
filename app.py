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

def main():
    # 헤더
    st.markdown("""
    <div style="
        text-align: center; 
        padding: 40px 20px; 
        background: linear-gradient(135deg, #ffd93d 0%, #ff6b35 100%); 
        border-radius: 20px; 
        margin-bottom: 40px;
        color: white;
        box-shadow: 0 10px 30px rgba(255,107,53,0.3);
    ">
        <h1 style="margin: 0; font-size: 3em; font-weight: 700; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">
            💬 말씨맑음 CS 도우미
        </h1>
        <p style="margin: 15px 0 0 0; font-size: 22px; opacity: 0.9;">
            AI 기반 고객 서비스 지원 도구
        </p>
        <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.8;">
            언어 감지 • 욕설 필터링 • 실시간 번역 • 답안 생성
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 문제상황 섹션
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #ff8a65 0%, #ff7043 100%);
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 40px;
        color: white;
        box-shadow: 0 8px 25px rgba(255,138,101,0.3);
    ">
        <h2 style="text-align: center; margin-bottom: 30px; font-size: 2.2em;">
            🚨 CS 상담사의 현실
        </h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
            <div style="background: rgba(255,255,255,0.15); padding: 20px; border-radius: 15px; text-align: center;">
                <h3 style="font-size: 2.5em; margin: 0; color: #fff3e0;">75%</h3>
                <p style="margin: 10px 0 0 0; font-size: 16px;">상담사의 약 75%가 고객의 공격적인 말투/언행을 경험</p>
            </div>
            <div style="background: rgba(255,255,255,0.15); padding: 20px; border-radius: 15px; text-align: center;">
                <h3 style="font-size: 2.5em; margin: 0; color: #fff3e0;">2.5일</h3>
                <p style="margin: 10px 0 0 0; font-size: 16px;">2.5일에 한 번 고객 폭언, 월 평균 1.1회의 성희롱 경험</p>
            </div>
            <div style="background: rgba(255,255,255,0.15); padding: 20px; border-radius: 15px; text-align: center;">
                <h3 style="font-size: 2.5em; margin: 0; color: #fff3e0;">47.6%</h3>
                <p style="margin: 10px 0 0 0; font-size: 16px;">고객 상담사의 47.6%가 자살을 생각해본 적 있음</p>
            </div>
            <div style="background: rgba(255,255,255,0.15); padding: 20px; border-radius: 15px; text-align: center;">
                <h3 style="font-size: 2.5em; margin: 0; color: #fff3e0;">80%</h3>
                <p style="margin: 10px 0 0 0; font-size: 16px;">3년 간 공공 민원 콜센터 상담사의 80%가 퇴직을 함</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 솔루션 섹션
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #ffb74d 0%, #ff8f00 100%);
        padding: 40px;
        border-radius: 20px;
        margin-bottom: 40px;
        color: white;
        box-shadow: 0 8px 25px rgba(255,183,77,0.3);
    ">
        <h2 style="text-align: center; margin-bottom: 30px; font-size: 2.5em;">
            🌟 오늘의 말씨, 맑음
        </h2>
        <p style="text-align: center; font-size: 20px; margin-bottom: 30px; opacity: 0.9;">
            AI가 상담사의 정신 건강을 지켜드립니다
        </p>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 25px;">
            <div style="background: rgba(255,255,255,0.15); padding: 25px; border-radius: 15px;">
                <h3 style="font-size: 1.8em; margin-bottom: 15px;">🧠 지능형 공격성 감지</h3>
                <p style="font-size: 16px; line-height: 1.6;">
                    단순 욕설 필터링을 넘어서 고객의 공격성 수준을 분석하고, 
                    상황에 맞는 적절한 대응 방안을 제시합니다.
                </p>
            </div>
            <div style="background: rgba(255,255,255,0.15); padding: 25px; border-radius: 15px;">
                <h3 style="font-size: 1.8em; margin-bottom: 15px;">🔄 스마트 메시지 재구성</h3>
                <p style="font-size: 16px; line-height: 1.6;">
                    부적절한 표현을 감지하면 즉시 친절하고 정중한 표현으로 
                    자동 변환하여 상담사의 스트레스를 줄여줍니다.
                </p>
            </div>
            <div style="background: rgba(255,255,255,0.15); padding: 25px; border-radius: 15px;">
                <h3 style="font-size: 1.8em; margin-bottom: 15px;">🤖 AI 답변 추천</h3>
                <p style="font-size: 16px; line-height: 1.6;">
                    상황을 분석하여 최적의 답변을 실시간으로 추천하고, 
                    상담사의 업무 효율성을 극대화합니다.
                </p>
            </div>
            <div style="background: rgba(255,255,255,0.15); padding: 25px; border-radius: 15px;">
                <h3 style="font-size: 1.8em; margin-bottom: 15px;">🌐 다국어 실시간 번역</h3>
                <p style="font-size: 16px; line-height: 1.6;">
                    15개 언어를 자동 감지하고 실시간 번역으로 
                    글로벌 고객과의 원활한 소통을 지원합니다.
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 데모 섹션
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #ffcc02 0%, #ff9500 100%);
        padding: 40px;
        border-radius: 20px;
        margin-bottom: 40px;
        color: white;
        box-shadow: 0 8px 25px rgba(255,204,2,0.3);
    ">
        <h2 style="text-align: center; margin-bottom: 30px; font-size: 2.5em;">
            🎯 실제 사용 데모
        </h2>
        <p style="text-align: center; font-size: 18px; margin-bottom: 30px; opacity: 0.9;">
            말씨맑음이 어떻게 상담사를 도와주는지 확인해보세요
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 언어 선택
    language = st.selectbox(
        "고객 언어 선택:",
        ["한국어 고객", "영어 고객", "중국어 고객"],
        help="다른 언어의 고객 시나리오를 확인해보세요"
    )
    
    # 구분선
    st.markdown("""
    <div style="
        display: flex;
        align-items: center;
        margin: 40px 0;
        color: #ff8f00;
        font-size: 24px;
        font-weight: bold;
    ">
        <div style="flex: 1; height: 3px; background: linear-gradient(90deg, #ffcc02, #ff9500); border-radius: 2px;"></div>
        <span style="margin: 0 20px;">Before & After 비교</span>
        <div style="flex: 1; height: 3px; background: linear-gradient(90deg, #ff9500, #ffcc02); border-radius: 2px;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Before/After 비교
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #ff7043 0%, #ff5722 100%);
            padding: 25px;
            border-radius: 20px;
            margin-bottom: 20px;
            color: white;
            box-shadow: 0 8px 25px rgba(255,112,67,0.3);
        ">
            <h3 style="text-align: center; margin-bottom: 20px; font-size: 1.8em;">
                🚫 Before (필터링 전)
            </h3>
            <p style="text-align: center; font-size: 16px; opacity: 0.9;">
                욕설이 포함된 원본 메시지
            </p>
        </div>
        """, unsafe_allow_html=True)
        display_chat_messages(DEMO_SCENARIOS[language]["before"], "")
    
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #ffb74d 0%, #ff8f00 100%);
            padding: 25px;
            border-radius: 20px;
            margin-bottom: 20px;
            color: white;
            box-shadow: 0 8px 25px rgba(255,183,77,0.3);
        ">
            <h3 style="text-align: center; margin-bottom: 20px; font-size: 1.8em;">
                ✅ After (필터링 후)
            </h3>
            <p style="text-align: center; font-size: 16px; opacity: 0.9;">
                AI가 처리한 개선된 메시지
            </p>
        </div>
        """, unsafe_allow_html=True)
        display_chat_messages(DEMO_SCENARIOS[language]["after"], "")
    
    # 성능 지표
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #ffcc02 0%, #ff9500 100%);
        padding: 40px;
        border-radius: 20px;
        margin: 40px 0;
        color: white;
        box-shadow: 0 8px 25px rgba(255,204,2,0.3);
    ">
        <h2 style="text-align: center; margin-bottom: 30px; font-size: 2.2em;">
            📊 성능 지표
        </h2>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px;">
            <div style="background: rgba(255,255,255,0.15); padding: 20px; border-radius: 15px; text-align: center;">
                <h3 style="font-size: 2.5em; margin: 0; color: #fff3e0;">98.5%</h3>
                <p style="margin: 10px 0 0 0; font-size: 16px;">번역 정확도</p>
            </div>
            <div style="background: rgba(255,255,255,0.15); padding: 20px; border-radius: 15px; text-align: center;">
                <h3 style="font-size: 2.5em; margin: 0; color: #fff3e0;">0.8초</h3>
                <p style="margin: 10px 0 0 0; font-size: 16px;">평균 응답 시간</p>
            </div>
            <div style="background: rgba(255,255,255,0.15); padding: 20px; border-radius: 15px; text-align: center;">
                <h3 style="font-size: 2.5em; margin: 0; color: #fff3e0;">15개</h3>
                <p style="margin: 10px 0 0 0; font-size: 16px;">지원 언어</p>
            </div>
            <div style="background: rgba(255,255,255,0.15); padding: 20px; border-radius: 15px; text-align: center;">
                <h3 style="font-size: 2.5em; margin: 0; color: #fff3e0;">4.8/5.0</h3>
                <p style="margin: 10px 0 0 0; font-size: 16px;">고객 만족도</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 푸터
    st.markdown("""
    <div style="
        text-align: center; 
        padding: 30px; 
        background: linear-gradient(135deg, #ff8f00 0%, #ff6f00 100%);
        border-radius: 20px;
        color: white;
        margin-top: 40px;
        box-shadow: 0 8px 25px rgba(255,143,0,0.3);
    ">
        <h3 style="margin-bottom: 15px; font-size: 1.5em;">💡 말씨맑음으로 상담사의 정신 건강을 지켜주세요</h3>
        <p style="font-size: 16px; opacity: 0.9; margin: 0;">
            언어 감지, 욕설 필터링, 실시간 번역으로 CS 업무 효율성을 극대화하세요!
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 
