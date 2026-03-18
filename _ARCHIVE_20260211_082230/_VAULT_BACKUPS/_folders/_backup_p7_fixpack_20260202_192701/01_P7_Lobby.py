from __future__ import annotations
import time
import streamlit as st

st.set_page_config(page_title="P7 Timebomb Lobby", layout="wide", initial_sidebar_state="collapsed")

# ---------------------------
#  P7 TIMEBOMB LOBBY  <span style='color:#ff2d2d;font-weight:900;'>[BUILD:P7_BUILD_20260205_145812]</span> (PC-bang)
# ---------------------------

st.markdown("""
<style>
/* --- kill Streamlit chrome --- */
header[data-testid="stHeader"],
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
footer{display:none !important; height:0 !important; margin:0 !important; padding:0 !important;}
html, body{margin:0 !important; padding:0 !important;}
.block-container{padding-top:0.7rem !important; padding-bottom:1.0rem !important; max-width:980px;}

/* --- theme tokens (P7) --- */
:root{
  --p7-bg1:#0b1220;
  --p7-bg2:#050a14;
  --p7-panel:rgba(2,6,23,0.72);
  --p7-line:rgba(148,163,184,0.16);
  --p7-text:rgba(226,232,240,0.92);
  --p7-sub:rgba(226,232,240,0.72);
  --p7-cyan:rgba(0,229,255,0.95);
  --p7-blue:rgba(27,124,255,0.95);
  --p7-glow:rgba(56,189,248,0.22);
  --p7-danger:rgba(255,99,132,0.90);
  --p7-safe:rgba(34,197,94,0.82);
}

body{
  background: radial-gradient(1200px 700px at 25% 0%, rgba(0,229,255,0.12), rgba(0,0,0,0)) ,
              radial-gradient(1100px 620px at 85% 15%, rgba(27,124,255,0.10), rgba(0,0,0,0)) ,
              linear-gradient(180deg, var(--p7-bg1), var(--p7-bg2));
}

.p7l-wrap{
  background: linear-gradient(180deg, rgba(15,23,42,0.88), rgba(2,6,23,0.90));
  border: 1px solid var(--p7-line);
  border-radius: 18px;
  padding: 18px 18px 16px 18px;
  box-shadow: 0 18px 64px rgba(0,0,0,0.42);
}

.p7l-title{
  font-weight: 900;
  letter-spacing: 0.6px;
  font-size: 22px;
  margin-bottom: 6px;
  color: var(--p7-text);
}
.p7l-sub{
  font-size: 14px;
  color: var(--p7-sub);
  margin-bottom: 14px;
}

.p7l-chip{
  display:inline-block;
  font-size: 12px;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(0,229,255,0.25);
  background: rgba(0,229,255,0.08);
  color: rgba(226,232,240,0.92);
  margin-right: 6px;
}
.p7l-hr{height:1px; background: var(--p7-line); margin: 14px 0 12px 0;}

/* --- RADIO -> BIG ASYM CARDS --- */
div[role="radiogroup"]{
  display:grid !important;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto;
  gap: 12px;
}

/* base label style */
div[role="radiogroup"] > label{
  margin:0 !important;
  padding: 0 !important;
  border: 1px solid rgba(148,163,184,0.18) !important;
  background: linear-gradient(180deg, rgba(2,6,23,0.65), rgba(2,6,23,0.90)) !important;
  border-radius: 16px !important;
  box-shadow: 0 12px 42px rgba(0,0,0,0.30) !important;
  overflow:hidden !important;
  cursor:pointer !important;
  position:relative !important;
  transition: transform 0.14s ease, box-shadow 0.14s ease, border-color 0.14s ease;
}

/* bigger clickable area */
div[role="radiogroup"] > label > div{
  padding: 18px 16px 16px 16px !important;
}

/* remove default radio circle spacing */
div[role="radiogroup"] > label input{
  transform: scale(1.2);
  margin-right: 10px !important;
}

/* hover lift */
div[role="radiogroup"] > label:hover{
  transform: translateY(-2px);
  border-color: rgba(56,189,248,0.35) !important;
  box-shadow: 0 0 0 1px rgba(56,189,248,0.10), 0 18px 60px rgba(0,0,0,0.40);
}

/* selected highlight (Streamlit uses :has for modern browsers) */
div[role="radiogroup"] > label:has(input:checked){
  border-color: rgba(0,229,255,0.55) !important;
  box-shadow: 0 0 0 1px rgba(0,229,255,0.18), 0 20px 70px rgba(0,0,0,0.48);
}

/* top neon strip */
div[role="radiogroup"] > label::before{
  content:"";
  position:absolute; left:0; top:0; right:0; height:4px;
  background: linear-gradient(90deg, var(--p7-cyan), var(--p7-blue));
  opacity:0.95;
}

/* text formatting inside option */
div[role="radiogroup"] > label span{
  font-size: 15px !important;
  font-weight: 850 !important;
  color: rgba(226,232,240,0.94) !important;
  letter-spacing: 0.3px;
}

/* ASYM SHAPES (3 different feels) */
div[role="radiogroup"] > label:nth-child(1){
  /* HARD: slightly sharper + subtle danger hint */
  border-radius: 12px 22px 12px 22px !important;
}
div[role="radiogroup"] > label:nth-child(1)::before{
  background: linear-gradient(90deg, rgba(255,99,132,0.95), rgba(0,229,255,0.85)) !important;
}
div[role="radiogroup"] > label:nth-child(2){
  /* STANDARD: wide spanning bottom row */
  grid-column: 1 / span 2;
  border-radius: 22px 14px 22px 14px !important;
}
div[role="radiogroup"] > label:nth-child(2)::before{
  background: linear-gradient(90deg, var(--p7-cyan), var(--p7-blue)) !important;
}
div[role="radiogroup"] > label:nth-child(3){
  /* SAFE: softer round */
  border-radius: 26px !important;
}
div[role="radiogroup"] > label:nth-child(3)::before{
  background: linear-gradient(90deg, rgba(34,197,94,0.90), var(--p7-cyan)) !important;
}

/* Start buttons */
div[data-testid="stButton"] > button{
  height: 48px;
  border-radius: 14px;
  font-weight: 850;
  letter-spacing: 0.4px;
}
</style>
""", unsafe_allow_html=True)

# Wrapper
st.markdown('<div class="p7l-wrap">', unsafe_allow_html=True)
st.markdown('<div class="p7l-title">🧨 P7 TIMEBOMB LOBBY</div>', unsafe_allow_html=True)
st.markdown('<div class="p7l-sub">전장 입장 전, <b>시간폭탄 모드</b>를 선택하고 미션을 시작하세요.</div>', unsafe_allow_html=True)
st.markdown('<span class="p7l-chip">PC방 전장</span><span class="p7l-chip">시간 압박</span><span class="p7l-chip">랭크 미션</span>', unsafe_allow_html=True)
st.markdown('<div class="p7l-hr"></div>', unsafe_allow_html=True)

# Options (labels include naming + time)
options = [
  "💣 HARD — 초고압 전장 · 2:00",
  "💣 STANDARD — 실전 기준 · 2:30",
  "💣 SAFE — 안정형 전장 · 3:00",
]
default_idx = 1

choice = st.radio(" ", options, index=default_idx, label_visibility="collapsed")

# Map to seconds
sec_map = {
  options[0]: 120,
  options[1]: 150,
  options[2]: 180,
}

c1, c2 = st.columns([1,1])
with c1:
    if st.button("🔥 START MISSION", use_container_width=True):
        st.session_state["p7_limit"] = int(sec_map[choice])
        st.session_state["p7_started"] = True
        st.session_state["p7_lobby_choice"] = choice
        st.session_state["p7_lobby_ts"] = time.time()
        st.switch_page("pages/01_P7_Reading_Arena.py")

with c2:
    if st.button("🏠 MAIN HUB", use_container_width=True):
        st.switch_page("main_hub.py")

st.markdown('</div>', unsafe_allow_html=True)
