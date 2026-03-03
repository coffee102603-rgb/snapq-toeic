"""
SnapQ TOEIC V2 - P5 TIMEBOMB Arena
최종 클린 버전
"""

import streamlit as st
from config.settings import PAGE_CONFIG

st.set_page_config(**PAGE_CONFIG)

# 클린 CSS
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg, #0a0e1a 0%, #1a1f35 50%, #0a0e1a 100%);
}

/* 상단 컨트롤 */
.top-bar {
    display: flex;
    align-items: center;
    gap: 20px;
    padding: 28px 30px;
    background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95));
    border: 3px solid rgba(0, 229, 255, 0.5);
    border-radius: 20px;
    margin-bottom: 25px;
    box-shadow: 0 0 50px rgba(0, 229, 255, 0.4);
}

.home-circle {
    width: 75px; height: 75px;
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
    width: 105px; height: 105px;
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

.timer-circle.t30:hover {
    box-shadow: 0 0 80px rgba(255, 45, 85, 0.9);
}

.timer-circle.t40:hover {
    box-shadow: 0 0 80px rgba(255, 107, 53, 0.9);
}

.timer-circle.t50:hover {
    box-shadow: 0 0 80px rgba(16, 185, 129, 0.9);
}

.timer-emoji { font-size: 38px;
    margin-bottom: 5px;
}

.timer-text { font-size: 24px;
    font-weight: 900;
    color: #FFFFFF;
}

/* 메인 그리드 */
.battle-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
}

/* 헤더 */
.arena-header {
    padding: 30px 25px;
    border-radius: 24px;
    text-align: center;
    margin-bottom: 15px;
    animation: header-pulse 3s infinite;
}

.arena-header.grammar {
    background: linear-gradient(135deg, #FF2D55, #DC2626);
    box-shadow: 0 20px 60px rgba(255, 45, 85, 0.6);
}

.arena-header.vocab {
    background: linear-gradient(135deg, #00E5FF, #0EA5E9);
    box-shadow: 0 20px 60px rgba(0, 229, 255, 0.6);
}

@keyframes header-pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.02); }
}

.arena-title {
    font-size: 32px;
    font-weight: 900;
    color: #FFFFFF;
    text-shadow: 0 0 30px rgba(0, 0, 0, 0.8);
    letter-spacing: 3px;
}

/* 테마 카드 - 전체 클릭 가능 */
.theme-card {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.98));
    border: 5px solid;
    border-radius: 28px;
    padding: 45px 30px;
    text-align: center;
    cursor: pointer;
    transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    min-height: 195px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7);
    margin-bottom: 15px;
    position: relative;
    overflow: hidden;
}

.theme-card::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.1) 50%, transparent 70%);
    animation: card-shine 4s infinite;
}

@keyframes card-shine {
    0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
    100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
}

.theme-card.verb {
    border-color: #FF2D55;
    animation: float-up 4s infinite;
    box-shadow: 0 0 60px rgba(255, 45, 85, 0.5);
}

.theme-card.connect {
    border-color: #00E5FF;
    animation: float-up 4.5s infinite;
    box-shadow: 0 0 60px rgba(0, 229, 255, 0.5);
}

.theme-card.advanced {
    border-color: #7C5CFF;
    animation: float-up 5s infinite;
    box-shadow: 0 0 60px rgba(124, 92, 255, 0.5);
}

.theme-card.hard {
    border-color: #FF2D55;
    animation: pulse-hard 2s infinite;
    box-shadow: 0 0 60px rgba(255, 45, 85, 0.5);
}

.theme-card.easy {
    border-color: #10B981;
    animation: float-up 4s infinite;
    box-shadow: 0 0 60px rgba(16, 185, 129, 0.5);
}

.theme-card.mix {
    border-color: #7C5CFF;
    animation: rainbow-border 5s infinite, float-up 4s infinite;
    box-shadow: 0 0 60px rgba(124, 92, 255, 0.5);
}

@keyframes float-up {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-10px); }
}

@keyframes pulse-hard {
    0%, 100% { box-shadow: 0 0 60px rgba(255, 45, 85, 0.5); }
    50% { box-shadow: 0 0 100px rgba(255, 45, 85, 0.9); }
}

@keyframes rainbow-border {
    0% { border-color: #FF2D55; }
    33% { border-color: #00E5FF; }
    66% { border-color: #10B981; }
    100% { border-color: #FF2D55; }
}

.theme-card:hover {
    transform: translateY(-20px) scale(1.08) !important;
    box-shadow: 0 30px 90px rgba(255, 255, 255, 0.4) !important;
}

.theme-emoji {
    font-size: 75px;
    margin-bottom: 15px;
    animation: emoji-bounce 3s infinite;
    filter: drop-shadow(0 0 25px rgba(255, 255, 255, 0.8));
}

@keyframes emoji-bounce {
    0%, 100% { transform: translateY(0px) rotate(-5deg); }
    50% { transform: translateY(-12px) rotate(5deg); }
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


/* 선택된 타이머 강조 */
.timer-circle.selected {
    transform: scale(1.15);
    animation: selected-pulse 1.5s infinite;
}

.timer-circle.t30.selected {
    box-shadow: 0 0 80px rgba(255, 45, 85, 1) !important;
    border-width: 6px;
}

.timer-circle.t40.selected {
    box-shadow: 0 0 80px rgba(255, 107, 53, 1) !important;
    border-width: 6px;
}

.timer-circle.t50.selected {
    box-shadow: 0 0 80px rgba(16, 185, 129, 1) !important;
    border-width: 6px;
}

@keyframes selected-pulse {
    0%, 100% { box-shadow: 0 0 80px rgba(255, 255, 255, 0.8); }
    50% { box-shadow: 0 0 120px rgba(255, 255, 255, 1); }
}

/* Form 버튼 숨김 */
.stForm button[kind="formSubmit"] {
    display: none !important;
}
/* Streamlit 버튼 완전 숨김 */
div[data-testid="stButton"] {
    display: none !important;
}

/* 모바일 */
@media (max-width: 768px) {
    .battle-grid {
        grid-template-columns: 1fr;
    }
    
    .timer-circles {
        flex-wrap: wrap;
    }
    
    .timer-circle {
        width: 80px;
        height: 80px;
    }
}
</style>
""", unsafe_allow_html=True)

# Session state
if "p5_selected_timer" not in st.session_state:
    st.session_state.p5_selected_timer = 40

# 상단 바
timer = st.session_state.p5_selected_timer
selected_class_30 = "selected" if timer == 30 else ""
selected_class_40 = "selected" if timer == 40 else ""
selected_class_50 = "selected" if timer == 50 else ""

st.markdown(f"""
<div class='top-bar'>
    <div class='home-circle' onpointerdown="document.getElementById('home_hidden').click()">🏠</div>
    <div class='timer-circles'>
        <div class='timer-circle t30 {selected_class_30}' onpointerdown="document.getElementById('t30_hidden').click()">
            <div class='timer-emoji'>🔥</div>
            <div class='timer-text'>30초</div>
        </div>
        <div class='timer-circle t40 {selected_class_40}' onpointerdown="document.getElementById('t40_hidden').click()">
            <div class='timer-emoji'>⚡</div>
            <div class='timer-text'>40초</div>
        </div>
        <div class='timer-circle t50 {selected_class_50}' onpointerdown="document.getElementById('t50_hidden').click()">
            <div class='timer-emoji'>✅</div>
            <div class='timer-text'>50초</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 숨겨진 버튼들 (기능용)
col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("h", key="home_hidden"):
        st.switch_page("main_hub.py")
with col2:
    if st.button("30", key="t30_hidden"):
        st.session_state.p5_selected_timer = 30
        st.rerun()
with col3:
    if st.button("40", key="t40_hidden"):
        st.session_state.p5_selected_timer = 40
        st.rerun()
with col4:
    if st.button("50", key="t50_hidden"):
        st.session_state.p5_selected_timer = 50
        st.rerun()



# 메인 그리드
st.markdown("<div class='battle-grid'>", unsafe_allow_html=True)

col_left, col_right = st.columns(2)

# 왼쪽 (어법)
with col_left:
    st.markdown("""
    <div class='arena-header grammar'>
        <div class='arena-title'>💣 어법 전장</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 동사
with st.form(key="form_verb", clear_on_submit=False):
    st.markdown("""
    <div class='theme-card verb'>
        <div class='theme-emoji'>⚙️</div>
        <div class='theme-title'>동사 전투</div>
        <div class='theme-desc'>시제·태</div>
    </div>
    """, unsafe_allow_html=True)
    
        st.markdown("</div>", unsafe_allow_html=True)
    if st.form_submit_button("출격", use_container_width=True):
        st.session_state.p5_selected_theme = "verb"
        st.switch_page("pages/03_P5_Game.py")
    
    # 연결
with st.form(key="form_connect", clear_on_submit=False):
    st.markdown("""
    <div class='theme-card connect'>
        <div class='theme-emoji'>🔗</div>
        <div class='theme-title'>연결 전투</div>
        <div class='theme-desc'>관계/구조</div>
    </div>
    """, unsafe_allow_html=True)
    
        st.markdown("</div>", unsafe_allow_html=True)
    if st.form_submit_button("출격", use_container_width=True):
        st.session_state.p5_selected_theme = "connect"
        st.switch_page("pages/03_P5_Game.py")
    
    # 변수
with st.form(key="form_advanced", clear_on_submit=False):
    st.markdown("""
    <div class='theme-card advanced'>
        <div class='theme-emoji'>💎</div>
        <div class='theme-title'>변수 전투</div>
        <div class='theme-desc'>가정/함정</div>
    </div>
    """, unsafe_allow_html=True)
    
        st.markdown("</div>", unsafe_allow_html=True)
    if st.form_submit_button("출격", use_container_width=True):
        st.session_state.p5_selected_theme = "advanced"
        st.switch_page("pages/03_P5_Game.py")

# 오른쪽 (어휘)
with col_right:
    st.markdown("""
    <div class='arena-header vocab'>
        <div class='arena-title'>📚 어휘 전장</div>
    </div>
    """, unsafe_allow_html=True)
    
    # HARD
with st.form(key="form_hard", clear_on_submit=False):
    st.markdown("""
    <div class='theme-card hard'>
        <div class='theme-emoji'>🔥</div>
        <div class='theme-title'>HARD</div>
        <div class='theme-desc'>77% 난이도</div>
    </div>
    """, unsafe_allow_html=True)
    
        st.markdown("</div>", unsafe_allow_html=True)
    if st.form_submit_button("출격", use_container_width=True):
        st.session_state.p5_selected_theme = "hard"
        st.switch_page("pages/03_P5_Game.py")
    
    # EASY
with st.form(key="form_easy", clear_on_submit=False):
    st.markdown("""
    <div class='theme-card easy'>
        <div class='theme-emoji'>✅</div>
        <div class='theme-title'>EASY</div>
        <div class='theme-desc'>22% 난이도</div>
    </div>
    """, unsafe_allow_html=True)
    
        st.markdown("</div>", unsafe_allow_html=True)
    if st.form_submit_button("출격", use_container_width=True):
        st.session_state.p5_selected_theme = "easy"
        st.switch_page("pages/03_P5_Game.py")
    
    # MIX
with st.form(key="form_mix", clear_on_submit=False):
    st.markdown("""
    <div class='theme-card mix'>
        <div class='theme-emoji'>🎲</div>
        <div class='theme-title'>MIX</div>
        <div class='theme-desc'>랜덤 믹스</div>
    </div>
    """, unsafe_allow_html=True)
    
        st.markdown("</div>", unsafe_allow_html=True)
    if st.form_submit_button("출격", use_container_width=True):
        st.session_state.p5_selected_theme = "mix"
        st.switch_page("pages/03_P5_Game.py")

st.markdown("</div>", unsafe_allow_html=True)

