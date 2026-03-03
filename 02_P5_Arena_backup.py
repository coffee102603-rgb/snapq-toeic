"""
SnapQ TOEIC V2 - P5 TIMEBOMB Arena
PC방 게임 스타일 - 네온 효과
"""

import streamlit as st
import time

# Config
from config.settings import PAGE_CONFIG

st.set_page_config(**PAGE_CONFIG)

# CSS - PC방 게임 스타일
def load_game_css():
    st.markdown("""
    <style>
    /* 전역 배경 */
    .main {
        background: linear-gradient(135deg, #0a0e1a 0%, #1a1f35 50%, #0a0e1a 100%);
    }
    
    /* 파티클 배경 */
    @keyframes float-particle {
        0%, 100% { transform: translate(0, 0) scale(1); opacity: 0.3; }
        25% { transform: translate(10px, -10px) scale(1.1); opacity: 0.6; }
        50% { transform: translate(-5px, -20px) scale(0.9); opacity: 0.4; }
        75% { transform: translate(-10px, -10px) scale(1.05); opacity: 0.5; }
    }
    
    .particles {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        z-index: 0;
    }
    
    .particle {
        position: absolute;
        width: 3px;
        height: 3px;
        background: #fff;
        border-radius: 50%;
        animation: float-particle 8s infinite;
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.8);
    }
    
    /* 컨테이너 */
    .game-container {
        max-width: 900px;
        margin: 0 auto;
        padding: 20px;
        position: relative;
        z-index: 1;
    }
    
    /* 헤더 */
    .game-header {
        text-align: center;
        padding: 50px 30px;
        background: linear-gradient(135deg, #FF2D55 0%, #FF6B35 50%, #FFA500 100%);
        border-radius: 28px;
        margin-bottom: 30px;
        box-shadow: 0 0 60px rgba(255, 45, 85, 0.6),
                    0 0 100px rgba(255, 107, 53, 0.4),
                    inset 0 0 40px rgba(255, 255, 255, 0.1);
        border: 3px solid rgba(255, 255, 255, 0.3);
        animation: header-glow 3s ease-in-out infinite;
        position: relative;
        overflow: hidden;
    }
    
    .game-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent 30%, rgba(255, 255, 255, 0.1) 50%, transparent 70%);
        animation: shine 3s infinite;
    }
    
    @keyframes shine {
        0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
        100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
    }
    
    @keyframes header-glow {
        0%, 100% { 
            box-shadow: 0 0 60px rgba(255, 45, 85, 0.6),
                        0 0 100px rgba(255, 107, 53, 0.4);
        }
        50% { 
            box-shadow: 0 0 80px rgba(255, 45, 85, 0.8),
                        0 0 120px rgba(255, 107, 53, 0.6);
        }
    }
    
    .game-emoji {
        font-size: 72px;
        display: inline-block;
        animation: bomb-shake 2s ease-in-out infinite;
        filter: drop-shadow(0 0 20px rgba(255, 255, 255, 0.8));
    }
    
    @keyframes bomb-shake {
        0%, 100% { transform: rotate(-8deg) scale(1); }
        25% { transform: rotate(8deg) scale(1.05); }
        50% { transform: rotate(-8deg) scale(1); }
        75% { transform: rotate(8deg) scale(1.05); }
    }
    
    .game-title {
        font-size: 52px;
        font-weight: 900;
        color: #FFFFFF;
        margin: 15px 0 5px 0;
        text-shadow: 0 0 20px rgba(0, 0, 0, 0.5),
                     0 0 40px rgba(255, 255, 255, 0.3);
        letter-spacing: 4px;
        animation: title-glow 2s ease-in-out infinite;
    }
    
    @keyframes title-glow {
        0%, 100% { text-shadow: 0 0 20px rgba(0, 0, 0, 0.5), 0 0 40px rgba(255, 255, 255, 0.3); }
        50% { text-shadow: 0 0 30px rgba(0, 0, 0, 0.7), 0 0 60px rgba(255, 255, 255, 0.5); }
    }
    
    .game-subtitle {
        font-size: 26px;
        font-weight: 700;
        color: rgba(255, 255, 255, 0.95);
        letter-spacing: 3px;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.4);
    }
    
    /* 컨트롤 바 */
    .control-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: linear-gradient(135deg, rgba(15, 23, 42, 0.98), rgba(30, 41, 59, 0.98));
        backdrop-filter: blur(15px);
        border: 3px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 18px 25px;
        margin-bottom: 35px;
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.6),
                    0 0 30px rgba(124, 92, 255, 0.3);
        position: sticky;
        top: 20px;
        z-index: 100;
    }
    
    .tabs-section {
        display: flex;
        gap: 12px;
    }
    
    .tab-btn {
        padding: 12px 24px;
        background: rgba(255, 255, 255, 0.08);
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 14px;
        font-size: 24px;
        font-weight: 900;
        color: rgba(255, 255, 255, 0.6);
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .tab-btn.active {
        background: linear-gradient(135deg, #FF2D55, #FF6B35);
        border-color: #FF2D55;
        color: #FFFFFF;
        box-shadow: 0 0 30px rgba(255, 45, 85, 0.6);
        transform: scale(1.05);
    }
    
    .timer-section {
        display: flex;
        gap: 10px;
        align-items: center;
    }
    
    .timer-label {
        font-size: 16px;
        font-weight: 900;
        color: rgba(255, 255, 255, 0.8);
        margin-right: 8px;
    }
    
    .timer-option {
        padding: 30px 36px;
        border-radius: 16px;
        border: 4px solid;
        font-size: 32px;
        font-weight: 900;
        cursor: pointer;
        transition: all 0.2s ease;
        text-align: center;
        min-width: 135px;
        min-height: 95px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .timer-option.fast {
        background: linear-gradient(135deg, #FF2D55, #FF6B35);
        border-color: #FF2D55;
        color: #fff;
        box-shadow: 0 0 20px rgba(255, 45, 85, 0.4);
    }
    
    .timer-option.normal {
        background: linear-gradient(135deg, #FF6B35, #FFA500);
        border-color: #FF6B35;
        color: #fff;
        box-shadow: 0 0 20px rgba(255, 107, 53, 0.4);
    }
    
    .timer-option.slow {
        background: linear-gradient(135deg, #10B981, #34D399);
        border-color: #10B981;
        color: #fff;
        box-shadow: 0 0 20px rgba(16, 185, 129, 0.4);
    }
    
    .timer-option.selected {
        transform: scale(1.15);
        animation: timer-pulse 1s ease-in-out infinite;
    }
    
    @keyframes timer-pulse {
        0%, 100% { box-shadow: 0 0 20px rgba(255, 255, 255, 0.4); }
        50% { box-shadow: 0 0 35px rgba(255, 255, 255, 0.7); }
    }
    
    /* 배틀 카드 그리드 */
    .battle-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 25px;
        margin-bottom: 30px;
    }
    
    @media (max-width: 768px) {
        .battle-grid {
            gap: 18px;
        }
    }
    
    /* 배틀 카드 */
    .battle-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9));
        border: 4px solid;
        border-radius: 24px;
        padding: 35px 25px;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
        min-height: 280px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        animation: card-float 4s ease-in-out infinite;
    }
    
    @keyframes card-float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-8px); }
    }
    
    .battle-card::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, transparent 40%, rgba(255, 255, 255, 0.1) 50%, transparent 60%);
        border-radius: 24px;
        opacity: 0;
        transition: opacity 0.3s;
        animation: card-shine 3s infinite;
    }
    
    @keyframes card-shine {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .battle-card.type-verb {
        border-color: #FF2D55;
        box-shadow: 0 15px 40px rgba(255, 45, 85, 0.4),
                    0 0 30px rgba(255, 45, 85, 0.3);
    }
    
    .battle-card.type-connect {
        border-color: #00E5FF;
        box-shadow: 0 15px 40px rgba(0, 229, 255, 0.4),
                    0 0 30px rgba(0, 229, 255, 0.3);
    }
    
    .battle-card.type-particle {
        border-color: #7C5CFF;
        box-shadow: 0 15px 40px rgba(124, 92, 255, 0.4),
                    0 0 30px rgba(124, 92, 255, 0.3);
    }
    
    .battle-card.type-advanced {
        border-color: #FF6B35;
        box-shadow: 0 15px 40px rgba(255, 107, 53, 0.4),
                    0 0 30px rgba(255, 107, 53, 0.3);
    }
    
    .battle-card:hover {
        transform: translateY(-15px) scale(1.05);
        animation: none;
    }
    
    .battle-card:hover.type-verb {
        box-shadow: 0 25px 60px rgba(255, 45, 85, 0.7),
                    0 0 50px rgba(255, 45, 85, 0.5);
    }
    
    .battle-card:hover.type-connect {
        box-shadow: 0 25px 60px rgba(0, 229, 255, 0.7),
                    0 0 50px rgba(0, 229, 255, 0.5);
    }
    
    .battle-card:hover.type-particle {
        box-shadow: 0 25px 60px rgba(124, 92, 255, 0.7),
                    0 0 50px rgba(124, 92, 255, 0.5);
    }
    
    .battle-card:hover.type-advanced {
        box-shadow: 0 25px 60px rgba(255, 107, 53, 0.7),
                    0 0 50px rgba(255, 107, 53, 0.5);
    }
    
    .battle-card:hover::before {
        opacity: 1;
    }
    
    .card-emoji {
        font-size: 100px;
        margin-bottom: 20px;
        animation: emoji-bounce 2s ease-in-out infinite;
        filter: drop-shadow(0 0 15px rgba(255, 255, 255, 0.6));
    }
    
    @keyframes emoji-bounce {
        0%, 100% { transform: translateY(0px) rotate(-5deg); }
        50% { transform: translateY(-10px) rotate(5deg); }
    }
    
    .card-title {
        font-size: 36px;
        font-weight: 900;
        color: #FFFFFF;
        margin-bottom: 12px;
        text-shadow: 0 0 20px rgba(255, 255, 255, 0.5);
        letter-spacing: 1px;
    }
    
    .card-desc {
        font-size: 26px;
        font-weight: 700;
        color: rgba(255, 255, 255, 0.85);
        margin-bottom: 20px;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);
    }
    
    .card-button {
        padding: 14px 32px;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.85));
        border: 3px solid rgba(255, 255, 255, 0.9);
        border-radius: 16px;
        font-size: 26px;
        font-weight: 900;
        color: #1a1f35;
        cursor: pointer;
        transition: all 0.2s ease;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        text-shadow: none;
    }
    
    .card-button:hover {
        transform: scale(1.1);
        box-shadow: 0 12px 30px rgba(255, 255, 255, 0.4);
    }
    
    /* 홈 버튼 */
    .home-btn {
        position: fixed;
        top: 25px;
        left: 25px;
        z-index: 999;
    }
    
    .home-btn button {
        min-width: 60px !important;
        max-width: 60px !important;
        min-height: 60px !important;
        max-height: 60px !important;
        border-radius: 50% !important;
        font-size: 28px !important;
        padding: 0 !important;
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.85)) !important;
        border: 4px solid rgba(255, 255, 255, 0.9) !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4),
                    0 0 30px rgba(255, 255, 255, 0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .home-btn button:hover {
        transform: scale(1.15) rotate(15deg) !important;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.5),
                    0 0 40px rgba(255, 255, 255, 0.5) !important;
    }
    
    /* 버튼 숨김 */
    
    
    
/* 배틀 카드 버튼 스타일 */
div[data-testid="stButton"] > button {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.8), rgba(15, 23, 42, 0.9)) !important;
    border: 4px solid rgba(0, 229, 255, 0.4) !important;
    border-radius: 20px !important;
    padding: 40px 30px !important;
    min-height: 300px !important;
    font-size: 24px !important;
    font-weight: 900 !important;
    color: #FFFFFF !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4), 0 0 20px rgba(0, 229, 255, 0.2) !important;
    transition: all 0.3s ease !important;
    white-space: pre-line !important;
    line-height: 1.8 !important;
}

div[data-testid="stButton"] > button:hover {
    transform: scale(1.05) !important;
    border-color: rgba(0, 229, 255, 0.8) !important;
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.5), 0 0 40px rgba(0, 229, 255, 0.5) !important;
}

/* 모바일 최적화 */
    @media (max-width: 768px) {
        .game-title { font-size: 38px; }
        .game-emoji { font-size: 56px; }
        .control-bar { flex-direction: column; gap: 15px; padding: 15px; }
        .card-emoji { font-size: 75px; }
        .card-title { font-size: 28px; }
        .card-desc { font-size: 18px; }
        .battle-card { min-height: 250px; padding: 25px 18px; }
    }
    </style>
    """, unsafe_allow_html=True)

load_game_css()

# 파티클 배경
st.markdown("""
<div class='particles'>
    <div class='particle' style='top: 10%; left: 15%; animation-delay: 0s;'></div>
    <div class='particle' style='top: 20%; left: 85%; animation-delay: 1s;'></div>
    <div class='particle' style='top: 30%; left: 45%; animation-delay: 2s;'></div>
    <div class='particle' style='top: 40%; left: 70%; animation-delay: 0.5s;'></div>
    <div class='particle' style='top: 50%; left: 25%; animation-delay: 1.5s;'></div>
    <div class='particle' style='top: 60%; left: 60%; animation-delay: 2.5s;'></div>
    <div class='particle' style='top: 70%; left: 35%; animation-delay: 1.2s;'></div>
    <div class='particle' style='top: 80%; left: 80%; animation-delay: 0.8s;'></div>
    <div class='particle' style='top: 15%; left: 55%; animation-delay: 1.8s;'></div>
    <div class='particle' style='top: 85%; left: 40%; animation-delay: 2.2s;'></div>
    <div class='particle' style='top: 25%; left: 20%; animation-delay: 0.3s;'></div>
    <div class='particle' style='top: 55%; left: 75%; animation-delay: 1.3s;'></div>
    <div class='particle' style='top: 65%; left: 10%; animation-delay: 2.8s;'></div>
    <div class='particle' style='top: 35%; left: 90%; animation-delay: 0.7s;'></div>
    <div class='particle' style='top: 75%; left: 50%; animation-delay: 1.9s;'></div>
</div>
""", unsafe_allow_html=True)

# Session state
def init_state():
    defaults = {
        "p5_arena_type": "grammar",
        "p5_selected_timer": 35,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_state()

# 홈 버튼
st.markdown("<div class='home-btn'>", unsafe_allow_html=True)
if st.button("🏠", key="home"):
    st.switch_page("main_hub.py")
st.markdown("</div>", unsafe_allow_html=True)

# 헤더
st.markdown("""
<div class='game-header'>
    <div class='game-emoji'>💣</div>
    <div class='game-title'>P5 TIMEBOMB</div>
    <div class='game-subtitle'>BATTLE ARENA</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='game-container'>", unsafe_allow_html=True)

# 컨트롤 바
arena_type = st.session_state.p5_arena_type
selected_timer = st.session_state.p5_selected_timer

st.markdown(f"""
<div class='control-bar'>
    <div class='tabs-section'>
        <div class='tab-btn {"active" if arena_type == "grammar" else ""}'>💣 어법</div>
        <div class='tab-btn {"active" if arena_type == "vocab" else ""}'>📚 어휘</div>
    </div>
    <div class='timer-section'>
        <span class='timer-label'>⏱️</span>
        <div class='timer-option fast {"selected" if selected_timer == 25 else ""}'>🔥 25초</div>
        <div class='timer-option normal {"selected" if selected_timer == 35 else ""}'>⚡ 35초</div>
        <div class='timer-option slow {"selected" if selected_timer == 45 else ""}'>✅ 45초</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 컨트롤 버튼 (숨김)
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("grammar", key="tab_grammar"):
        st.session_state.p5_arena_type = "grammar"
        st.rerun()
with col2:
    if st.button("vocab", key="tab_vocab"):
        st.session_state.p5_arena_type = "vocab"
        st.rerun()
with col3:
    if st.button("25", key="time_25"):
        st.session_state.p5_selected_timer = 25
        st.rerun()
with col4:
    if st.button("35", key="time_35"):
        st.session_state.p5_selected_timer = 35
        st.rerun()
with col5:
    if st.button("45", key="time_45"):
        st.session_state.p5_selected_timer = 45
        st.rerun()

# 배틀 카드 그리드
if arena_type == "grammar":
    themes = [
        ("⚙️", "동사 전투", "시제 · 태", "verb"),
        ("🔗", "연결 전투", "관계/구조", "connect"),
        ("💎", "조사 전투", "품사/수식", "particle"),
        ("🔥", "변수 전투", "가정/함정", "advanced")
    ]
else:
    themes = [
        ("🔥", "HARD", "77% 난이도", "hard"),
        ("✅", "EASY", "22% 난이도", "easy"),
        ("🎲", "MIX", "랜덤", "mix"),
        ("⭐", "CUSTOM", "커스텀", "custom")
    ]

st.markdown("<div class='battle-grid'>", unsafe_allow_html=True)

cols = st.columns(2)
for idx, (emoji, title, desc, key) in enumerate(themes):
    with cols[idx % 2]:
        # 카드 전체를 버튼으로
        if st.button(
            f"{emoji}\n\n{title}\n{desc}\n\n🚀 출격!",
            key=f"battle_{arena_type}_{key}",
            use_container_width=True
        ):
            st.session_state.p5_selected_theme = key
            st.session_state.p5_selected_timer = selected_timer
            st.switch_page("pages/03_P5_Game.py")

st.markdown("</div>", unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)










