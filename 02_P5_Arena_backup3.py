"""
SnapQ TOEIC V2 - P5 TIMEBOMB Arena
최종 완성 버전
"""

import streamlit as st
from config.settings import PAGE_CONFIG

st.set_page_config(**PAGE_CONFIG)

# CSS
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #0a0e1a 0%, #1a1f35 50%, #0a0e1a 100%);
}

.top-bar {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 28px 30px;
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95));
    border: 3px solid rgba(0, 229, 255, 0.5);
    border-radius: 20px;
    margin-bottom: 15px;
    box-shadow: 0 0 50px rgba(0, 229, 255, 0.4);
}

.home-circle {
    width: 75px;
    height: 75px;
    border-radius: 50%;
    background: linear-gradient(135deg, #FF2D55, #DC2626);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 35px;
    cursor: pointer;
    border: 3px solid rgba(255, 45, 85, 0.6);
    box-shadow: 0 0 30px rgba(255, 45, 85, 0.5);
    transition: all 0.3s ease;
}

.home-circle:hover {
    transform: scale(1.15);
    box-shadow: 0 0 50px rgba(255, 45, 85, 0.9);
}

.timer-circles {
    display: flex;
    gap: 15px;
    flex: 1;
    justify-content: center;
}

.timer-circle {
    width: 105px;
    height: 105px;
    border-radius: 50%;
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95));
    border: 4px solid;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
}

.timer-circle.t30 {
    border-color: #FF2D55;
    box-shadow: 0 0 40px rgba(255, 45, 85, 0.4);
}

.timer-circle.t40 {
    border-color: #FF6B35;
    box-shadow: 0 0 40px rgba(255, 107, 53, 0.4);
}

.timer-circle.t50 {
    border-color: #10B981;
    box-shadow: 0 0 40px rgba(16, 185, 129, 0.4);
}

.timer-circle:hover {
    transform: scale(1.15);
}

.timer-circle.selected {
    transform: scale(1.15);
    border-width: 6px;
}

.timer-circle.t30.selected {
    box-shadow: 0 0 80px rgba(255, 45, 85, 1);
}

.timer-circle.t40.selected {
    box-shadow: 0 0 80px rgba(255, 107, 53, 1);
}

.timer-circle.t50.selected {
    box-shadow: 0 0 80px rgba(16, 185, 129, 1);
}

.timer-emoji {
    font-size: 38px;
    margin-bottom: 5px;
}

.timer-text {
    font-size: 24px;
    font-weight: 900;
    color: #FFFFFF;
}

.battle-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

.arena-header {
    padding: 30px 25px;
    border-radius: 24px;
    text-align: center;
    margin-bottom: 8px;
}

.arena-header.grammar {
    background: linear-gradient(135deg, #FF2D55, #DC2626);
    box-shadow: 0 20px 60px rgba(255, 45, 85, 0.6);
}

.arena-header.vocab {
    background: linear-gradient(135deg, #00E5FF, #0EA5E9);
    box-shadow: 0 20px 60px rgba(0, 229, 255, 0.6);
}

.arena-title {
    font-size: 32px;
    font-weight: 900;
    color: #FFFFFF;
    text-shadow: 0 0 30px rgba(0, 0, 0, 0.8);
    letter-spacing: 3px;
}

.theme-card {
    position: relative;
    animation: card-float 4s infinite, card-glow 3s infinite;
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.98));
    border: 5px solid;
    border-radius: 28px;
    padding: 45px 30px;
    text-align: center;
    cursor: pointer;
    transition: all 0.4s ease;
    min-height: 195px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7);
    margin-bottom: 8px;
}

.theme-card.verb {
    animation: wave-1 4s infinite;
    border-color: #FF2D55;
    box-shadow: 0 0 60px rgba(255, 45, 85, 0.5);
}

.theme-card.connect {
    animation: wave-2 4s infinite;
    border-color: #00E5FF;
    box-shadow: 0 0 60px rgba(0, 229, 255, 0.5);
}

.theme-card.advanced {
    animation: wave-3 4s infinite;
    border-color: #7C5CFF;
    box-shadow: 0 0 60px rgba(124, 92, 255, 0.5);
}

.theme-card.hard {
    animation: wave-4 4s infinite;
    border-color: #FF2D55;
    box-shadow: 0 0 60px rgba(255, 45, 85, 0.5);
}

.theme-card.easy {
    animation: wave-5 4s infinite;
    border-color: #10B981;
    box-shadow: 0 0 60px rgba(16, 185, 129, 0.5);
}

.theme-card.mix {
    animation: wave-6 4s infinite;
    border-color: #7C5CFF;
    box-shadow: 0 0 60px rgba(124, 92, 255, 0.5);
}

.theme-card:hover {
    transform: translateY(-25px) scale(1.1) !important;
    box-shadow: 0 40px 100px rgba(255, 255, 255, 0.5) !important;
    z-index: 10;
}

.theme-emoji {
    animation: emoji-bounce 3s infinite, emoji-rotate 6s infinite;
    font-size: 75px;
    margin-bottom: 8px;
    @keyframes emoji-bounce {
    0%, 100% { transform: translateY(0px) rotate(0deg); }
    25% { transform: translateY(-10px) rotate(-5deg); }
    75% { transform: translateY(-10px) rotate(5deg); }
}

@keyframes emoji-rotate {
    0%, 100% { transform: rotate(0deg); }
    50% { transform: rotate(360deg); }
}

filter: drop-shadow(0 0 25px rgba(255, 255, 255, 0.8));
}

.theme-title {
    font-size: 33px;
    font-weight: 900;
    color: #FFFFFF;
    margin-bottom: 10px;
    text-shadow: 0 0 30px rgba(255, 255, 255, 0.6);
    letter-spacing: 2px;
}

.theme-desc {
    font-size: 17px;
    font-weight: 700;
    color: rgba(255, 255, 255, 0.9);
}


/* 물결 애니메이션 */
@keyframes wave-1 {
    0%, 100% { transform: translateY(0px) scale(1); }
    50% { transform: translateY(-15px) scale(1.02); }
}

@keyframes wave-2 {
    0%, 100% { transform: translateY(0px) scale(1); }
    50% { transform: translateY(-12px) scale(1.02); }
}

@keyframes wave-3 {
    0%, 100% { transform: translateY(0px) scale(1); }
    50% { transform: translateY(-18px) scale(1.02); }
}

@keyframes wave-4 {
    0%, 100% { transform: translateY(0px) scale(1); }
    50% { transform: translateY(-10px) scale(1.02); }
}

@keyframes wave-5 {
    0%, 100% { transform: translateY(0px) scale(1); }
    50% { transform: translateY(-14px) scale(1.02); }
}

@keyframes wave-6 {
    0%, 100% { transform: translateY(0px) scale(1); }
    50% { transform: translateY(-16px) scale(1.02); }
}

div[data-testid="stButton"] {
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 100% !important;
    z-index: 1000 !important;
}

div[data-testid="stButton"] > button {
    opacity: 0 !important;
    width: 100% !important;
    height: 100% !important;
    cursor: pointer !important;
    border: none !important;
    background: transparent !important;
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
}

@media (max-width: 768px) {
    .battle-grid {
        grid-template-columns: 1fr;
    }
}
</style>
""", unsafe_allow_html=True)

# 파티클 배경
import random
particles_html = '<div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 0;">'
for i in range(30):
    top = random.randint(0, 100)
    left = random.randint(0, 100)
    delay = random.uniform(0, 4)
    duration = random.uniform(6, 10)
    particles_html += f'<div style="position: absolute; top: {top}%; left: {left}%; width: 3px; height: 3px; background: rgba(255,255,255,0.8); border-radius: 50%; animation: particle-float {duration}s infinite; animation-delay: {delay}s; box-shadow: 0 0 10px rgba(255,255,255,0.6);"></div>'
particles_html += '</div>'

st.markdown("""
<style>
@keyframes card-float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-12px); }
}

@keyframes card-glow {
    0%, 100% { box-shadow: 0 0 60px currentColor; }
    50% { box-shadow: 0 0 100px currentColor; }
}

@keyframes particle-float {
    0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.3; }
    25% { transform: translate(20px, -30px) scale(1.2); opacity: 0.8; }
    50% { transform: translate(-10px, -60px) scale(0.8); opacity: 0.5; }
    75% { transform: translate(-20px, -30px) scale(1.1); opacity: 0.6; }
}
</style>
""", unsafe_allow_html=True)

st.markdown(particles_html, unsafe_allow_html=True)
# Session state
if "p5_selected_timer" not in st.session_state:
    st.session_state.p5_selected_timer = 40

# 상단 바
timer = st.session_state.p5_selected_timer
sel30 = "selected" if timer == 30 else ""
sel40 = "selected" if timer == 40 else ""
sel50 = "selected" if timer == 50 else ""

st.markdown(f"""
<div class='top-bar'>
    <div class='home-circle' onclick='alert("home")'>🏠</div>
    <div class='timer-circles'>
        <div class='timer-circle t30 {sel30}' onclick='alert("t30")'>
            <div class='timer-emoji'>🔥</div>
            <div class='timer-text'>30초</div>
        </div>
        <div class='timer-circle t40 {sel40}' onclick='alert("t40")'>
            <div class='timer-emoji'>⚡</div>
            <div class='timer-text'>40초</div>
        </div>
        <div class='timer-circle t50 {sel50}' onclick='alert("t50")'>
            <div class='timer-emoji'>✅</div>
            <div class='timer-text'>50초</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 숨겨진 버튼들
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("h", key="h"):
        st.switch_page("main_hub.py")
with col2:
    if st.button("30", key="30"):
        st.session_state.p5_selected_timer = 30
        st.rerun()
with col3:
    if st.button("40", key="40"):
        st.session_state.p5_selected_timer = 40
        st.rerun()
with col4:
    if st.button("50", key="50"):
        st.session_state.p5_selected_timer = 50
        st.rerun()

# 그리드
st.markdown("<div class='battle-grid'>", unsafe_allow_html=True)

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("""
    <div class='arena-header grammar'>
        <div class='arena-title'>💣 어법 전장</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='theme-card verb' style="cursor: pointer;">
        <div class='theme-emoji'>⚙️</div>
        <div class='theme-title'>동사 전투</div>
        <div class='theme-desc'>시제·태</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("동사전투", key="v", use_container_width=True):
        st.session_state.p5_selected_theme = "verb"
        st.switch_page("pages/03_P5_Game.py")
st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("""
    <div class='theme-card connect' style="cursor: pointer;">
        <div class='theme-emoji'>🔗</div>
        <div class='theme-title'>연결 전투</div>
        <div class='theme-desc'>관계/구조</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("연결전투", key="c", use_container_width=True):
        st.session_state.p5_selected_theme = "connect"
        st.switch_page("pages/03_P5_Game.py")
    
    st.markdown("""
    <div class='theme-card advanced' style="cursor: pointer;">
        <div class='theme-emoji'>💎</div>
        <div class='theme-title'>변수 전투</div>
        <div class='theme-desc'>가정/함정</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("변수전투", key="a", use_container_width=True):
        st.session_state.p5_selected_theme = "advanced"
        st.switch_page("pages/03_P5_Game.py")

with col_right:
    st.markdown("""
    <div class='arena-header vocab'>
        <div class='arena-title'>📚 어휘 전장</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class='theme-card hard' style="cursor: pointer;">
        <div class='theme-emoji'>🔥</div>
        <div class='theme-title'>HARD</div>
        <div class='theme-desc'>77% 난이도</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("HARD출격", key="h2", use_container_width=True):
        st.session_state.p5_selected_theme = "hard"
        st.switch_page("pages/03_P5_Game.py")
    
    st.markdown("""
    <div class='theme-card easy' style="cursor: pointer;">
        <div class='theme-emoji'>✅</div>
        <div class='theme-title'>EASY</div>
        <div class='theme-desc'>22% 난이도</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("EASY출격", key="e", use_container_width=True):
        st.session_state.p5_selected_theme = "easy"
        st.switch_page("pages/03_P5_Game.py")
    
    st.markdown("""
    <div class='theme-card mix' style="cursor: pointer;">
        <div class='theme-emoji'>🎲</div>
        <div class='theme-title'>MIX</div>
        <div class='theme-desc'>랜덤 믹스</div>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("MIX출격", key="m", use_container_width=True):
        st.session_state.p5_selected_theme = "mix"
        st.switch_page("pages/03_P5_Game.py")

st.markdown("</div>", unsafe_allow_html=True)



