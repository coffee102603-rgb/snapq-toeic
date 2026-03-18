from __future__ import annotations
import time
import streamlit as st

st.set_page_config(page_title="SnapQ P7 Lobby", layout="wide", initial_sidebar_state="collapsed")

# =========================
# P7 LOBBY (Timebomb Setup)
# =========================
st.markdown("""
<style>
header[data-testid="stHeader"], div[data-testid="stToolbar"], div[data-testid="stDecoration"], footer{display:none !important;}
html, body{margin:0 !important; padding:0 !important;}
.block-container{padding-top:0.6rem !important; padding-bottom:1.2rem !important; max-width:980px;}

.p7l-wrap{
  background: linear-gradient(180deg, rgba(15,23,42,0.92), rgba(2,6,23,0.92));
  border: 1px solid rgba(148,163,184,0.18);
  border-radius: 18px;
  padding: 18px 18px 16px 18px;
  box-shadow: 0 16px 60px rgba(0,0,0,0.35);
}
.p7l-title{
  font-weight: 900;
  letter-spacing: 0.5px;
  font-size: 22px;
  margin-bottom: 8px;
  color: #E2E8F0;
}
.p7l-sub{
  font-size: 14px;
  color: rgba(226,232,240,0.78);
  margin-bottom: 14px;
}
.p7l-chip{
  display:inline-block;
  font-size: 12px;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(99,102,241,0.35);
  background: rgba(99,102,241,0.10);
  color: rgba(226,232,240,0.92);
  margin-right: 6px;
}
.p7l-hr{height:1px; background: rgba(148,163,184,0.16); margin: 14px 0;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="p7l-wrap">', unsafe_allow_html=True)
st.markdown('<div class="p7l-title">🧨 P7 TIMEBOMB SETUP</div>', unsafe_allow_html=True)
st.markdown('<div class="p7l-sub">전장 입장 전, 제한시간을 선택하고 <b>START</b>를 눌러 미션을 시작하세요.</div>', unsafe_allow_html=True)
st.markdown('<span class="p7l-chip">2:00</span><span class="p7l-chip">2:30</span><span class="p7l-chip">3:00</span>', unsafe_allow_html=True)
st.markdown('<div class="p7l-hr"></div>', unsafe_allow_html=True)

# time options
opts = {
  "2:00 (120s)  —  HARD": 120,
  "2:30 (150s)  —  STANDARD": 150,
  "3:00 (180s)  —  SAFE": 180,
}

default_label = "2:30 (150s)  —  STANDARD"
choice = st.radio("⏱ 제한시간 선택", list(opts.keys()), index=list(opts.keys()).index(default_label))

c1, c2 = st.columns([1,1])
with c1:
    if st.button("🔥 START MISSION", use_container_width=True):
        st.session_state["p7_limit"] = int(opts[choice])
        st.session_state["p7_started"] = True
        st.session_state["p7_lobby_ts"] = time.time()
        st.switch_page("pages/01_P7_Reading_Arena.py")

with c2:
    if st.button("🏠 MAIN HUB", use_container_width=True):
        st.switch_page("main_hub.py")

st.markdown('</div>', unsafe_allow_html=True)
