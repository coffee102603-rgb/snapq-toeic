"""SnapQ TOEIC V2 - P5 TIMEBOMB Game"""
import streamlit as st
import time
from config.settings import PAGE_CONFIG

st.set_page_config(**PAGE_CONFIG)

# 게임 CSS
st.markdown("""
<style>
.main { background: linear-gradient(135deg, #0a0e1a 0%, #1a1f35 100%); }

.game-header {
    background: linear-gradient(135deg, #FF2D55, #FF6B35, #FFA500);
    border-radius: 24px;
    padding: 30px 25px;
    margin-bottom: 25px;
    box-shadow: 0 0 80px rgba(255, 45, 85, 0.7);
    text-align: center;
}

.game-title {
    font-size: 48px;
    font-weight: 900;
    color: #FFFFFF;
    text-shadow: 0 0 40px rgba(0, 0, 0, 0.6);
    letter-spacing: 4px;
    margin-bottom: 15px;
}

.game-info {
    display: flex;
    justify-content: space-around;
    font-size: 24px;
    font-weight: 900;
    color: #FFFFFF;
}

.timer-display {
    color: #FF2D55;
    font-size: 36px;
    animation: timer-pulse 1s infinite;
}

@keyframes timer-pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.1); }
}

.question-box {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.98));
    border: 4px solid rgba(0, 229, 255, 0.5);
    border-radius: 24px;
    padding: 40px 35px;
    margin-bottom: 30px;
    box-shadow: 0 0 60px rgba(0, 229, 255, 0.4);
}

.question-text {
    font-size: 28px;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1.6;
    text-align: center;
}

.choice-btn {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.98));
    border: 5px solid;
    border-radius: 24px;
    padding: 35px 30px;
    margin-bottom: 15px;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6);
    min-height: 110px;
    display: flex;
    align-items: center;
    justify-content: center;
}

.choice-btn.choice1 {
    border-color: #FF2D55;
    box-shadow: 0 0 40px rgba(255, 45, 85, 0.4);
}

.choice-btn.choice2 {
    border-color: #FF6B35;
    box-shadow: 0 0 40px rgba(255, 107, 53, 0.4);
}

.choice-btn.choice3 {
    border-color: #00E5FF;
    box-shadow: 0 0 40px rgba(0, 229, 255, 0.4);
}

.choice-btn.choice4 {
    border-color: #10B981;
    box-shadow: 0 0 40px rgba(16, 185, 129, 0.4);
}

.choice-btn:hover {
    transform: scale(1.08);
    box-shadow: 0 20px 80px rgba(255, 255, 255, 0.5) !important;
}

.choice-text {
    font-size: 26px;
    font-weight: 900;
    color: #FFFFFF;
    text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
}

.stButton { width: 100% !important; }
.stButton > button {
    width: 100% !important;
    min-height: 110px !important;
    font-size: 26px !important;
    font-weight: 900 !important;
    border-radius: 24px !important;
    border: 5px solid !important;
    transition: all 0.3s ease !important;
}

@media (max-width: 768px) {
    .game-title { font-size: 36px; }
    .question-text { font-size: 24px; }
    .choice-text { font-size: 22px; }
}
</style>
""", unsafe_allow_html=True)

# Session state
if "p5_current_question" not in st.session_state:
    st.session_state.p5_current_question = 1
if "p5_score" not in st.session_state:
    st.session_state.p5_score = 0
if "p5_start_time" not in st.session_state:
    st.session_state.p5_start_time = time.time()

# 타이머 계산
timer_limit = st.session_state.get("p5_selected_timer", 40)
elapsed = int(time.time() - st.session_state.p5_start_time)
remaining = max(0, timer_limit - elapsed)

# 헤더
st.markdown(f"""
<div class='game-header'>
    <div class='game-title'>💣 P5 TIMEBOMB</div>
    <div class='game-info'>
        <div>⏱️ <span class='timer-display'>{remaining}초</span></div>
        <div>📊 {st.session_state.p5_current_question}/5</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 타임아웃 체크
if remaining == 0:
    st.error("💥 시간 초과! 폭탄이 터졌습니다!")
    if st.button("🔄 다시 도전", use_container_width=True):
        for key in list(st.session_state.keys()):
            if key.startswith("p5_"):
                del st.session_state[key]
        st.switch_page("pages/02_P5_Arena.py")
    st.stop()

# 예시 문제
question = "The company _____ a new policy next month."
choices = [
    "① will implement",
    "② implements",
    "③ implemented",
    "④ is implementing"
]
correct_answer = 0

# 문제 표시
st.markdown(f"""
<div class='question-box'>
    <div class='question-text'>{question}</div>
</div>
""", unsafe_allow_html=True)

# 선택지
for idx, choice in enumerate(choices):
    class_name = f"choice{idx+1}"
    st.markdown(f"""
    <div class='choice-btn {class_name}'>
        <div class='choice-text'>{choice}</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(choice, key=f"choice_{idx}", use_container_width=True):
        if idx == correct_answer:
            st.session_state.p5_score += 1
            st.success("✅ 정답!")
        else:
            st.error(f"❌ 오답! 정답: {choices[correct_answer]}")
        
        time.sleep(1)
        
        if st.session_state.p5_current_question >= 5:
            st.balloons()
            st.success(f"🎉 완료! 점수: {st.session_state.p5_score}/5")
            if st.button("🏠 메인으로", use_container_width=True):
                st.switch_page("main_hub.py")
        else:
            st.session_state.p5_current_question += 1
            st.rerun()

# 자동 새로고침 (타이머용)
st.markdown("""
<script>
setTimeout(function() {
    window.location.reload();
}, 1000);
</script>
""", unsafe_allow_html=True)
