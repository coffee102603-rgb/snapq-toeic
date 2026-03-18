# pages/03_Secret_Armory_Main.py
# ============================================================
# SnapQ TOEIC :: Secret Armory Lobby (A안: 2카드/4버튼)
# - ✅ 하단 "본부 복귀" 제거 (요청 반영)
# - ✅ MAIN HUB 길은 상단 auto 버튼(있으면)로 유지
# - 구조/로직: 전장 이동 경로 그대로
# ============================================================

from __future__ import annotations
import streamlit as st

from app.core.ui_shell import apply_ui_shell
from app.core.battle_theme import apply_battle_theme

st.set_page_config(page_title="🗡 Secret Armory Lobby", page_icon="🗡", layout="wide", initial_sidebar_state="collapsed")

apply_ui_shell(theme="armory", max_width_px=1040, pad_px=14)
apply_battle_theme()

st.markdown(
    """
<style>
.arm-wrap{ margin-top:0.35rem; }

.arm-debug{
  display:flex; align-items:center; gap:10px;
  padding:10px 14px; border-radius:16px;
  border:1px solid rgba(255,255,255,0.14);
  background: rgba(255,120,80,0.10);
  box-shadow:0 14px 34px rgba(0,0,0,.28);
  font-weight:950;
}
.arm-debug small{opacity:.85;font-weight:850;}

.arm-hero{
  display:flex; align-items:flex-end; justify-content:space-between;
  gap:12px; margin:0.55rem 0 0.75rem 0; flex-wrap:wrap;
}
.arm-title{ font-size:clamp(1.55rem,2.2vw,2.25rem); font-weight:950; }
.arm-sub{ opacity:.82; font-weight:800; margin-top:4px; }

.arm-card{
  border-radius:22px;
  border:1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.06);
  box-shadow:0 18px 44px rgba(0,0,0,.40);
  padding:16px 16px 14px 16px;
  overflow:hidden; position:relative;
  backdrop-filter: blur(10px);
}
.arm-card::before{
  content:""; position:absolute; left:0; top:0; right:0;
  height:14px; border-bottom:1px solid rgba(255,255,255,.10);
}
.arm-card.p5::before{ background: linear-gradient(90deg, rgba(255,45,85,.95), rgba(255,122,24,.92)); }
.arm-card.voca::before{ background: linear-gradient(90deg, rgba(0,229,255,.92), rgba(27,124,255,.92)); }

.arm-cap{ opacity:.82; font-weight:800; margin-bottom:10px; }

.arm-card div[data-testid="stButton"] > button{
  width:100% !important;
  border-radius:18px !important;
  padding:0.92rem 1.0rem !important;
  font-weight:1000 !important;
  letter-spacing:.45px !important;
  font-size:1.18rem !important;
  border:1px solid rgba(255,255,255,0.18) !important;
  background: rgba(255,255,255,0.10) !important;
  color: rgba(255,255,255,0.96) !important;
  box-shadow:0 14px 30px rgba(0,0,0,0.42) !important;
  text-align:left !important;
}
.arm-card.p5 div[data-testid="stButton"] > button{
  border-color: rgba(255,45,85,.26) !important;
  background: rgba(255,45,85,.12) !important;
}
.arm-card.voca div[data-testid="stButton"] > button{
  border-color: rgba(0,229,255,.22) !important;
  background: rgba(0,229,255,.10) !important;
}

.arm-bottom{
  margin-top:0.85rem;
  padding-top:0.65rem;
  border-top:1px solid rgba(255,255,255,0.10);
}
.arm-note{ opacity:.80; font-weight:800; font-size:0.95rem; }

@media (max-width: 860px){
  .arm-card{ padding:14px 14px 12px 14px; }
  .arm-card div[data-testid="stButton"] > button{
    font-size:1.06rem !important;
    padding:0.88rem 0.92rem !important;
  }
}
</style>
    """,
    unsafe_allow_html=True,
)

def safe_switch(page: str) -> None:
    try:
        st.switch_page(page)
    except Exception:
        st.error("페이지 이동 실패")
        st.stop()

st.markdown('<div class="arm-wrap">', unsafe_allow_html=True)

st.markdown(
    f"""
<div class="arm-debug">
  <span>🗡 ARMORY LOBBY LOADED</span>
  <small>{__file__}</small>
</div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="arm-hero">
  <div>
    <div class="arm-title">🗡 Secret Armory</div>
    <div class="arm-sub">P5 저장 문제 / P7 저장 단어 — TRAIN(정리) / BATTLE(시험) 4갈래 입구</div>
  </div>
</div>
    """,
    unsafe_allow_html=True,
)

left, right = st.columns(2, gap="large")

with left:
    st.markdown('<div class="arm-card p5">', unsafe_allow_html=True)
    st.markdown("### 🧨 P5 무기고")
    st.markdown('<div class="arm-cap">저장된 P5 문제로 연습/시험</div>', unsafe_allow_html=True)
    if st.button("🟩 P5 TRAIN", use_container_width=True, key="go_p5_train"):
        safe_switch("pages/02_P5_Train_Arena.py")
    if st.button("🔥 P5 BATTLE", use_container_width=True, key="go_p5_battle"):
        safe_switch("pages/02_P5_Armory_Battle.py")
    st.markdown("</div>", unsafe_allow_html=True)

with right:
    st.markdown('<div class="arm-card voca">', unsafe_allow_html=True)
    st.markdown("### 🧩 VOCA 무기고 (P7 저장 단어)")
    st.markdown('<div class="arm-cap">저장된 단어로 정리/시험</div>', unsafe_allow_html=True)
    if st.button("🟩 VOCA TRAIN", use_container_width=True, key="go_voca_train"):
        safe_switch("pages/04_VOCA_Train_Arena.py")
    if st.button("🔥 VOCA BATTLE", use_container_width=True, key="go_voca_battle"):
        safe_switch("pages/04_VOCA_Battle_Arena.py")
    st.markdown("</div>", unsafe_allow_html=True)

# ✅ 하단은 안내문만 (본부복귀 버튼 제거)
st.markdown('<div class="arm-bottom">', unsafe_allow_html=True)
st.markdown('<div class="arm-note">✅ 로비만 UI 업그레이드. 내부 엔진/데이터는 그대로 유지됩니다.</div>', unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)