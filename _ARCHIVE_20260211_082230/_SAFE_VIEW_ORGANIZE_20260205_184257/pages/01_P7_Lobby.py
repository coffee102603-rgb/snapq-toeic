from __future__ import annotations
import time
import streamlit as st

st.set_page_config(page_title="P7 Timebomb Lobby", layout="wide", initial_sidebar_state="collapsed")

# ---------------------------
#  P7 TIMEBOMB LOBBY  <span style='color:#ff2d2d;font-weight:900;'>[BUILD:P7_BUILD_20260205_145812]</span> (PC-bang)
# ---------------------------

st.markdown("""
<style>

/* ===== P7 LOBBY VISIBILITY FIX v1 ===== */

/* Lock the whole page background to P7 dark theme (Streamlit containers) */
div[data-testid="stAppViewContainer"],
div[data-testid="stAppViewContainer"] > section,
div[data-testid="stAppViewContainer"] > section > main,
div[data-testid="stAppViewBlockContainer"],
section.main, section.main > div,
div.block-container{
  background:
    radial-gradient(1200px 700px at 25% 0%, rgba(0,229,255,0.10), rgba(0,0,0,0)) ,
    radial-gradient(1100px 620px at 85% 15%, rgba(27,124,255,0.09), rgba(0,0,0,0)) ,
    linear-gradient(180deg, #0b1220, #050a14) !important;
}

/* Make title/sub text readable */
.p7l-title{
  color: rgba(255,255,255,0.96) !important;
  text-shadow: 0 2px 10px rgba(0,0,0,0.35);
}
.p7l-sub{
  color: rgba(226,232,240,0.86) !important;
}
.p7l-chip{
  color: rgba(226,232,240,0.92) !important;
  border-color: rgba(0,229,255,0.28) !important;
  background: rgba(0,229,255,0.10) !important;
}

/* Radio option text stronger */
div[role="radiogroup"] > label span{
  color: rgba(255,255,255,0.92) !important;
  text-shadow: 0 2px 10px rgba(0,0,0,0.35);
}

/* Bigger buttons (START / MAIN HUB) */
div[data-testid="stButton"] > button{
  height: 64px !important;
  font-size: 18px !important;
  border-radius: 16px !important;
  font-weight: 900 !important;
  letter-spacing: 0.6px !important;
}
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

/* ===== P7 LOBBY FINAL VISUAL v1 ===== */

/* Make top area text readable (strong white) */
.p7l-title{
  color: rgba(255,255,255,0.98) !important;
  font-weight: 950 !important;
  text-shadow: 0 2px 14px rgba(0,0,0,0.45) !important;
}
.p7l-sub{
  color: rgba(226,232,240,0.92) !important;
  font-weight: 800 !important;
  text-shadow: 0 2px 12px rgba(0,0,0,0.35) !important;
}
.p7l-chip{
  color: rgba(255,255,255,0.92) !important;
  font-weight: 850 !important;
}

/* Radio cards text: force white + bold */
div[role="radiogroup"] > label span{
  color: rgba(255,255,255,0.92) !important;
  font-weight: 900 !important;
  text-shadow: 0 2px 14px rgba(0,0,0,0.45) !important;
  letter-spacing: 0.3px !important;
}

/* Buttons: bigger + bolder */
div[data-testid="stButton"] > button{
  height: 70px !important;
  font-size: 19px !important;
  border-radius: 18px !important;
  font-weight: 950 !important;
  letter-spacing: 0.7px !important;
}

/* START MISSION ONLY: give color + different shape (more "arcade") 
   We target the first column button with a safe selector.
*/
div[data-testid="stHorizontalBlock"] > div:nth-child(1) div[data-testid="stButton"] > button{
  background: linear-gradient(90deg, rgba(0,229,255,0.85), rgba(27,124,255,0.88)) !important;
  color: rgba(255,255,255,0.98) !important;
  border: 1px solid rgba(0,229,255,0.30) !important;
  box-shadow: 0 14px 60px rgba(0,0,0,0.35), 0 0 0 1px rgba(0,229,255,0.15) !important;
  border-radius: 12px 26px 12px 26px !important;  /* main hub랑 다른 느낌 */
}
div[data-testid="stHorizontalBlock"] > div:nth-child(1) div[data-testid="stButton"] > button:hover{
  transform: translateY(-1px);
  filter: brightness(1.06);
}

/* MAIN HUB: keep clean but still strong */
div[data-testid="stHorizontalBlock"] > div:nth-child(2) div[data-testid="stButton"] > button{
  background: rgba(255,255,255,0.96) !important;
  color: rgba(2,6,23,0.92) !important;
  border: 1px solid rgba(148,163,184,0.30) !important;
}

/* ===== P7 LOBBY TEXT BOOST v1 ===== */

/* 카드(시간 선택 3개) 내부 텍스트: 무조건 흰색/굵게/크게 */
div[role="radiogroup"] > label span,
div[role="radiogroup"] > label p,
div[role="radiogroup"] > label div{
  color: rgba(255,255,255,0.98) !important;
  font-weight: 950 !important;
  font-size: 18px !important;       /* <- 여기서 확 커짐 */
  letter-spacing: 0.4px !important;
  text-shadow: 0 2px 14px rgba(0,0,0,0.55) !important;
}

/* (추가) 라디오 동그라미도 더 눈에 띄게 */
div[role="radiogroup"] > label input[type="radio"]{
  filter: drop-shadow(0 0 6px rgba(0,229,255,0.35));
  transform: scale(1.35) !important;
}

/* 선택된 카드: 테두리/글로우 더 강하게 */
div[role="radiogroup"] > label:has(input:checked){
  border-color: rgba(0,229,255,0.78) !important;
  box-shadow: 0 0 0 2px rgba(0,229,255,0.18), 0 22px 80px rgba(0,0,0,0.55) !important;
}

/* 카드 안에 아이콘(💣)이나 텍스트가 더 또렷하게 */
div[role="radiogroup"] > label{
  background: linear-gradient(180deg, rgba(2,6,23,0.55), rgba(2,6,23,0.92)) !important;
}

/* ===== P7 LOBBY MODE VISIBILITY v1 (NEON BORDERS + FILLED DOTS) ===== */

/* Base: cards pop from dark background */
div[role="radiogroup"] > label{
  border-width: 2.5px !important;
  border-style: solid !important;
  background: linear-gradient(180deg, rgba(2,6,23,0.55), rgba(2,6,23,0.92)) !important;
}

/* Ensure the left "dot" area looks filled (not hollow) */
div[role="radiogroup"] > label input[type="radio"]{
  transform: scale(1.35) !important;
  filter: drop-shadow(0 0 10px rgba(0,229,255,0.25));
}

/* HARD (1st) - RED */
div[role="radiogroup"] > label:nth-child(1){
  border-color: rgba(255, 70, 70, 0.95) !important;
  box-shadow:
    0 0 0 1px rgba(255,70,70,0.30),
    0 0 30px rgba(255,70,70,0.28) !important;
}
div[role="radiogroup"] > label:nth-child(1)::before{
  background: linear-gradient(90deg, rgba(255,70,70,0.95), rgba(0,229,255,0.85)) !important;
}

/* STANDARD (2nd) - CYAN/BLUE */
div[role="radiogroup"] > label:nth-child(2){
  border-color: rgba(0, 200, 255, 0.95) !important;
  box-shadow:
    0 0 0 1px rgba(0,200,255,0.30),
    0 0 30px rgba(0,200,255,0.26) !important;
}
div[role="radiogroup"] > label:nth-child(2)::before{
  background: linear-gradient(90deg, rgba(0,229,255,0.95), rgba(27,124,255,0.95)) !important;
}

/* SAFE (3rd) - GREEN */
div[role="radiogroup"] > label:nth-child(3){
  border-color: rgba(80, 255, 170, 0.95) !important;
  box-shadow:
    0 0 0 1px rgba(80,255,170,0.28),
    0 0 30px rgba(80,255,170,0.22) !important;
}
div[role="radiogroup"] > label:nth-child(3)::before{
  background: linear-gradient(90deg, rgba(80,255,170,0.95), rgba(0,229,255,0.85)) !important;
}

/* Selected card: extra crisp outline (still clean) */
div[role="radiogroup"] > label:has(input:checked){
  box-shadow:
    0 0 0 2px rgba(255,255,255,0.10),
    0 0 0 4px rgba(0,229,255,0.10),
    0 22px 80px rgba(0,0,0,0.55) !important;
}

/* ===== P7 LOBBY FILLED DOTS v1 (NEON CIRCLES) ===== */

/* We paint our own filled dot on each label */
div[role="radiogroup"] > label{
  position: relative !important;
}

/* Common dot shape */
div[role="radiogroup"] > label::after{
  content:"";
  position:absolute;
  left: 18px;               /* 위치: 카드 안 왼쪽 */
  top: 50%;
  transform: translateY(-50%);
  width: 18px;
  height: 18px;
  border-radius: 999px;
  opacity: 0.95;
  box-shadow: 0 0 12px rgba(255,255,255,0.18);
  pointer-events:none;
}

/* HARD = red filled */
div[role="radiogroup"] > label:nth-child(1)::after{
  background: rgba(255, 70, 70, 0.98);
  box-shadow: 0 0 14px rgba(255,70,70,0.85), 0 0 28px rgba(255,70,70,0.35);
}

/* STANDARD = cyan/blue filled */
div[role="radiogroup"] > label:nth-child(2)::after{
  background: rgba(0, 200, 255, 0.98);
  box-shadow: 0 0 14px rgba(0,200,255,0.90), 0 0 28px rgba(0,200,255,0.35);
}

/* SAFE = green filled */
div[role="radiogroup"] > label:nth-child(3)::after{
  background: rgba(80, 255, 170, 0.98);
  box-shadow: 0 0 14px rgba(80,255,170,0.85), 0 0 28px rgba(80,255,170,0.30);
}

/* Optional: keep native radio visible but less distracting */
div[role="radiogroup"] > label input[type="radio"]{
  opacity: 0.35;           /* 기본 동그라미는 살짝 흐리게 */
}

/* ===== P7 LOBBY BIG DOT FORCE FILL v1 ===== */

/* Base: label must be relative */
div[role="radiogroup"] > label{
  position: relative !important;
}

/* BIG LEFT DOT – force paint layer */
div[role="radiogroup"] > label::before{
  content:"";
  position:absolute;
  left: 16px;
  top: 50%;
  transform: translateY(-50%);
  width: 26px;
  height: 26px;
  border-radius: 999px;
  z-index: 2;
  opacity: 0.95;
  pointer-events: none;
}

/* HARD – RED */
div[role="radiogroup"] > label:nth-child(1)::before{
  background: rgba(255,70,70,0.98);
  box-shadow:
    0 0 16px rgba(255,70,70,0.9),
    0 0 32px rgba(255,70,70,0.45);
}

/* STANDARD – CYAN */
div[role="radiogroup"] > label:nth-child(2)::before{
  background: rgba(0,200,255,0.98);
  box-shadow:
    0 0 16px rgba(0,200,255,0.9),
    0 0 32px rgba(0,200,255,0.45);
}

/* SAFE – GREEN */
div[role="radiogroup"] > label:nth-child(3)::before{
  background: rgba(80,255,170,0.98);
  box-shadow:
    0 0 16px rgba(80,255,170,0.9),
    0 0 32px rgba(80,255,170,0.45);
}

/* Keep native radio but push it behind */
div[role="radiogroup"] > label input[type="radio"]{
  position: relative;
  z-index: 1;
  opacity: 0.25;
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
  "💣 HARD\n- 초고압 전장 · 2:00",
  "💣 STANDARD — 실전 기준 · 2:30",
  "💣 SAFE\n- 안정형 전장 · 3:00",
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







