import streamlit as st

st.set_page_config(
    page_title="SNAPQ P7 Reading Arena",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"] {
    margin: 0 !important;
    padding: 0 !important;
}
.block-container {
    padding-top: 0 !important;
    padding-bottom: 0 !important;
    max-width: 100% !important;
}
.p7-hud {
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 46px;
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 6px 12px;
    background: rgba(20,25,40,0.95);
    color: white;
    font-weight: 700;
    z-index: 1000000;
}
.p7-timer {
    position: fixed;
    top: 46px; left: 0; right: 0;
    height: 8px;
    background: linear-gradient(90deg,#30cfd0,#8b5cf6);
    z-index: 999999;
}
.p7-body {
    margin-top: 54px;
    padding: 6px 12px 20px 12px;
}
.p7-card {
    background: rgba(15,20,35,0.95);
    border-radius: 18px;
    padding: 16px;
    margin: 6px 0;
    color: white;
}
.p7-option {
    background: white;
    color: black;
    border-radius: 14px;
    padding: 12px;
    margin: 6px 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="p7-hud">
🔥 STEP 1/3 &nbsp; ⏱ TIME 02:16 &nbsp; ❌ MISS 0/3 &nbsp; 🟣 COMBO 0
</div>
<div class="p7-timer"></div>
""", unsafe_allow_html=True)

st.markdown('<div class="p7-body">', unsafe_allow_html=True)

st.markdown("""
<div class="p7-card">
Dear staff, This is to inform you that our customer support team will be relocated next month.
</div>
<div class="p7-card">
<b>What is the main purpose of this message?</b>
</div>
""", unsafe_allow_html=True)

options = [
    "To ask employees to work overtime this weekend",
    "To notify staff about a team relocation",
    "To announce a new product for customers",
    "To invite staff to a training workshop",
]

for o in options:
    st.markdown(f'<div class="p7-option">◯ {o}</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

<style>
/* =========================================================
   SNAPQ P7 TIMER MONSTER MODE
   - No layout shift
   - No font change
   - Visual pressure only
   ========================================================= */

.p7-timer-bar {
    height: 18px !important;
    margin-bottom: 6px !important;
    transform: translateY(4px);
    box-shadow: 0 8px 18px rgba(0,0,0,0.35);
    transition: all 0.25s ease;
}

/* 30s warning */
.p7-timer-30 .p7-timer-bar {
    animation: pulse_soft 1.4s infinite;
}

/* 20s danger */
.p7-timer-20 .p7-timer-bar {
    background: linear-gradient(90deg, #ff9800, #ff5722);
    animation: shake_soft 0.9s infinite;
}

/* 10s critical */
.p7-timer-10 .p7-timer-bar {
    background: linear-gradient(90deg, #ff1744, #ff5252);
    animation: shake_hard 0.45s infinite, pulse_hard 0.9s infinite;
}

/* 5s death zone */
.p7-timer-5 .p7-timer-bar {
    background: linear-gradient(90deg, #ff0000, #ff5252, #ff0000);
    animation: heartbeat 0.55s infinite;
}

/* ===== Animations ===== */

@keyframes pulse_soft {
    0%   { box-shadow: 0 0 6px rgba(255,152,0,0.4); }
    50%  { box-shadow: 0 0 16px rgba(255,152,0,0.9); }
    100% { box-shadow: 0 0 6px rgba(255,152,0,0.4); }
}

@keyframes pulse_hard {
    0%   { box-shadow: 0 0 10px rgba(255,0,0,0.6); }
    50%  { box-shadow: 0 0 28px rgba(255,0,0,1); }
    100% { box-shadow: 0 0 10px rgba(255,0,0,0.6); }
}

@keyframes shake_soft {
    0% { transform: translateY(4px) translateX(0); }
    25% { transform: translateY(4px) translateX(-1px); }
    50% { transform: translateY(4px) translateX(1px); }
    75% { transform: translateY(4px) translateX(-1px); }
    100% { transform: translateY(4px) translateX(0); }
}

@keyframes shake_hard {
    0% { transform: translateY(4px) translateX(0); }
    20% { transform: translateY(4px) translateX(-2px); }
    40% { transform: translateY(4px) translateX(2px); }
    60% { transform: translateY(4px) translateX(-2px); }
    80% { transform: translateY(4px) translateX(2px); }
    100% { transform: translateY(4px) translateX(0); }
}

@keyframes heartbeat {
    0%   { transform: translateY(4px) scaleY(1); }
    25%  { transform: translateY(4px) scaleY(1.25); }
    40%  { transform: translateY(4px) scaleY(0.9); }
    60%  { transform: translateY(4px) scaleY(1.35); }
    100% { transform: translateY(4px) scaleY(1); }
}
</style>
