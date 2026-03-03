"""SnapQ TOEIC V2 - P5 TIMEBOMB Arena - Reliable Click"""
import streamlit as st
from config.settings import PAGE_CONFIG

st.set_page_config(**PAGE_CONFIG)

# 쿼리 파라미터 먼저 체크
query_params = st.query_params.to_dict()

if "theme" in query_params:
    theme = query_params["theme"]
    st.session_state.p5_selected_theme = theme
    st.query_params.clear()
    st.switch_page("pages/03_P5_Game.py")
    st.stop()

if "timer" in query_params:
    timer_val = int(query_params["timer"])
    st.session_state.p5_selected_timer = timer_val
    st.query_params.clear()
    st.rerun()

if "home" in query_params:
    st.query_params.clear()
    st.switch_page("main_hub.py")
    st.stop()

st.markdown("""
<style>
.main { background: linear-gradient(135deg, #0a0e1a 0%, #1a1f35 50%, #0a0e1a 100%); }
.top-bar { display: flex; align-items: center; gap: 20px; padding: 28px 30px; background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95)); border: 3px solid rgba(0, 229, 255, 0.5); border-radius: 20px; margin-bottom: 15px; box-shadow: 0 0 50px rgba(0, 229, 255, 0.4); }
.home-circle { width: 75px; height: 75px; border-radius: 50%; background: linear-gradient(135deg, #FF2D55, #DC2626); display: flex; align-items: center; justify-content: center; font-size: 35px; cursor: pointer; border: 3px solid rgba(255, 45, 85, 0.6); box-shadow: 0 0 30px rgba(255, 45, 85, 0.5); transition: all 0.3s ease; user-select: none; }
.home-circle:active { transform: scale(0.95); }
.timer-circles { display: flex; gap: 15px; flex: 1; justify-content: center; }
.timer-circle { width: 105px; height: 105px; border-radius: 50%; background: linear-gradient(135deg, rgba(30, 41, 59, 0.9), rgba(15, 23, 42, 0.95)); border: 4px solid; display: flex; flex-direction: column; align-items: center; justify-content: center; cursor: pointer; transition: all 0.3s ease; user-select: none; }
.timer-circle.t30 { border-color: #FF2D55; box-shadow: 0 0 40px rgba(255, 45, 85, 0.4); }
.timer-circle.t40 { border-color: #FF6B35; box-shadow: 0 0 40px rgba(255, 107, 53, 0.4); }
.timer-circle.t50 { border-color: #10B981; box-shadow: 0 0 40px rgba(16, 185, 129, 0.4); }
.timer-circle.selected { transform: scale(1.15); border-width: 6px; }
.timer-circle:active { transform: scale(1.05); }
.timer-emoji { font-size: 38px; margin-bottom: 5px; pointer-events: none; }
.timer-text { font-size: 24px; font-weight: 900; color: #FFFFFF; pointer-events: none; }
.arena-header { padding: 30px 25px; border-radius: 24px; text-align: center; margin-bottom: 8px; }
.arena-header.grammar { background: linear-gradient(135deg, #FF2D55, #DC2626); box-shadow: 0 20px 60px rgba(255, 45, 85, 0.6); }
.arena-header.vocab { background: linear-gradient(135deg, #00E5FF, #0EA5E9); box-shadow: 0 20px 60px rgba(0, 229, 255, 0.6); }
.arena-title { font-size: 32px; font-weight: 900; color: #FFFFFF; text-shadow: 0 0 30px rgba(0, 0, 0, 0.8); letter-spacing: 3px; }
.theme-card { background: linear-gradient(135deg, rgba(30, 41, 59, 0.95), rgba(15, 23, 42, 0.98)); border: 5px solid; border-radius: 28px; padding: 45px 30px; text-align: center; min-height: 195px; display: flex; flex-direction: column; justify-content: center; align-items: center; box-shadow: 0 20px 60px rgba(0, 0, 0, 0.7); margin-bottom: 8px; transition: all 0.4s ease; cursor: pointer; user-select: none; }
.theme-card.verb { border-color: #FF2D55; box-shadow: 0 0 60px rgba(255, 45, 85, 0.5); animation: wave1 4s infinite; }
.theme-card.connect { border-color: #00E5FF; box-shadow: 0 0 60px rgba(0, 229, 255, 0.5); animation: wave2 4s infinite; }
.theme-card.advanced { border-color: #7C5CFF; box-shadow: 0 0 60px rgba(124, 92, 255, 0.5); animation: wave3 4s infinite; }
.theme-card.hard { border-color: #FF2D55; box-shadow: 0 0 60px rgba(255, 45, 85, 0.5); animation: wave4 4s infinite; }
.theme-card.easy { border-color: #10B981; box-shadow: 0 0 60px rgba(16, 185, 129, 0.5); animation: wave5 4s infinite; }
.theme-card.mix { border-color: #7C5CFF; box-shadow: 0 0 60px rgba(124, 92, 255, 0.5); animation: wave6 4s infinite; }
@keyframes wave1 { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-15px); } }
@keyframes wave2 { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-12px); } }
@keyframes wave3 { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-18px); } }
@keyframes wave4 { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
@keyframes wave5 { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-14px); } }
@keyframes wave6 { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-16px); } }
.theme-card:hover { transform: translateY(-25px) scale(1.12) !important; box-shadow: 0 40px 100px rgba(255, 255, 255, 0.5) !important; animation: none !important; }
.theme-card:active { transform: translateY(-20px) scale(1.05) !important; }
.theme-emoji { font-size: 75px; margin-bottom: 15px; filter: drop-shadow(0 0 25px rgba(255, 255, 255, 0.8)); pointer-events: none; }
.theme-title { font-size: 33px; font-weight: 900; color: #FFFFFF; margin-bottom: 10px; text-shadow: 0 0 30px rgba(255, 255, 255, 0.6); letter-spacing: 2px; pointer-events: none; }
.theme-desc { font-size: 17px; font-weight: 700; color: rgba(255, 255, 255, 0.9); pointer-events: none; }
</style>

<script>
function navigateTo(param, value) {
    const url = new URL(window.location.href);
    url.searchParams.set(param, value);
    window.location.href = url.toString();
}
</script>
""", unsafe_allow_html=True)

if "p5_selected_timer" not in st.session_state:
    st.session_state.p5_selected_timer = 40

timer = st.session_state.p5_selected_timer
sel30, sel40, sel50 = ["selected" if timer == t else "" for t in [30, 40, 50]]

st.markdown(f"""
<div class='top-bar'>
    <div class='home-circle' onclick="navigateTo('home', '1')">🏠</div>
    <div class='timer-circles'>
        <div class='timer-circle t30 {sel30}' onclick="navigateTo('timer', '30')">
            <div class='timer-emoji'>🔥</div>
            <div class='timer-text'>30초</div>
        </div>
        <div class='timer-circle t40 {sel40}' onclick="navigateTo('timer', '40')">
            <div class='timer-emoji'>⚡</div>
            <div class='timer-text'>40초</div>
        </div>
        <div class='timer-circle t50 {sel50}' onclick="navigateTo('timer', '50')">
            <div class='timer-emoji'>✅</div>
            <div class='timer-text'>50초</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

col_left, col_right = st.columns(2)

with col_left:
    st.markdown("<div class='arena-header grammar'><div class='arena-title'>💣 어법 전장</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='theme-card verb' onclick=\"navigateTo('theme', 'verb')\"><div class='theme-emoji'>⚙️</div><div class='theme-title'>동사 전투</div><div class='theme-desc'>시제·태</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='theme-card connect' onclick=\"navigateTo('theme', 'connect')\"><div class='theme-emoji'>🔗</div><div class='theme-title'>연결 전투</div><div class='theme-desc'>관계/구조</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='theme-card advanced' onclick=\"navigateTo('theme', 'advanced')\"><div class='theme-emoji'>💎</div><div class='theme-title'>변수 전투</div><div class='theme-desc'>가정/함정</div></div>", unsafe_allow_html=True)

with col_right:
    st.markdown("<div class='arena-header vocab'><div class='arena-title'>📚 어휘 전장</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='theme-card hard' onclick=\"navigateTo('theme', 'hard')\"><div class='theme-emoji'>🔥</div><div class='theme-title'>HARD</div><div class='theme-desc'>77% 난이도</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='theme-card easy' onclick=\"navigateTo('theme', 'easy')\"><div class='theme-emoji'>✅</div><div class='theme-title'>EASY</div><div class='theme-desc'>22% 난이도</div></div>", unsafe_allow_html=True)
    st.markdown("<div class='theme-card mix' onclick=\"navigateTo('theme', 'mix')\"><div class='theme-emoji'>🎲</div><div class='theme-title'>MIX</div><div class='theme-desc'>랜덤 믹스</div></div>", unsafe_allow_html=True)
