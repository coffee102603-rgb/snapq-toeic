# pages/03_Secret_Armory_Main.py
# SnapQ TOEIC - SECRET ARMORY LOBBY (FINAL LOBBY SHELL)
# - 목적: 예전 "무기고 로비" 느낌으로 복구 + Main Hub 길 100% 보장
# - 엔진/데이터 0 변경 (이 페이지는 라우팅/UI만)

import streamlit as st

st.set_page_config(
    page_title="🗡 Secret Armory Lobby · SnapQ TOEIC",
    page_icon="🗡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------
# THEME (safe try)
# ------------------------------------------------------------
try:
    from app.core.ui_shell import apply_ui_shell
    apply_ui_shell(max_width_px=1040, pad_px=14)
except Exception:
    pass

try:
    from app.core.battle_theme import apply_battle_theme
    apply_battle_theme()
except Exception:
    pass


def safe_switch(page: str):
    try:
        st.switch_page(page)  # type: ignore[attr-defined]
    except Exception:
        st.error("페이지 이동 실패 (페이지 경로/파일명 확인 필요)")
        st.stop()


# ------------------------------------------------------------
# Debug banner (default OFF)
# ------------------------------------------------------------
st.session_state.setdefault("DEBUG_BANNER", False)
with st.sidebar:
    st.markdown("### 🛠 DEBUG")
    st.session_state["DEBUG_BANNER"] = st.checkbox(
        "Show debug banner (FILE path)",
        value=bool(st.session_state.get("DEBUG_BANNER", False)),
        key="dbg_banner_armory",
    )

if st.session_state.get("DEBUG_BANNER", False):
    st.info(f"🗡 ARMORY LOBBY LOADED: {__file__}")


# ------------------------------------------------------------
# UI (Card Lobby)
# ------------------------------------------------------------
st.markdown(
    """
<style>
:root{
  --bg:#0B0E14;
  --txt:rgba(255,255,255,.92);
  --muted:rgba(255,255,255,.72);
  --line:rgba(255,255,255,.12);

  --stripe-p5: linear-gradient(90deg, #FF2D55, #FF7A18);
  --stripe-voca: linear-gradient(90deg, #22C55E, #A3E635);
  --stripe-hub: linear-gradient(90deg, #00E5FF, #1B7CFF);
  --stripe-arm: linear-gradient(90deg, #7C5CFF, #A78BFA);
}

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"]{
  background:
    radial-gradient(900px 650px at 18% 8%, rgba(124,92,255,.18), transparent 55%),
    radial-gradient(820px 620px at 78% 10%, rgba(0,229,255,.14), transparent 58%),
    radial-gradient(1000px 900px at 50% 80%, rgba(255,45,85,.10), transparent 70%),
    linear-gradient(180deg, #111827 0%, #0B0E14 60%, #070A10 100%) !important;
  color: var(--txt) !important;
}

header, footer {display:none;}
[data-testid="stHeader"]{display:none !important;}
[data-testid="stToolbar"]{display:none !important;}
#MainMenu{display:none !important;}

.block-container{ max-width:1040px; padding-top:0.9rem; padding-bottom:1.4rem; }
@media (max-width: 520px){
  .block-container{ padding-left:.85rem; padding-right:.85rem; }
}

.h1{
  font-weight:1000;
  font-size: 44px;
  letter-spacing:-0.5px;
  margin: 0.2rem 0 0.1rem 0;
  text-shadow: 0 10px 24px rgba(0,0,0,.40);
}
.sub{
  color: var(--muted);
  font-weight: 850;
  font-size: 13px;
  margin-bottom: 0.9rem;
}

/* cards */
.card{
  position:relative;
  overflow:hidden;
  border-radius: 20px;
  border: 1px solid rgba(255,255,255,.10);
  background: rgba(255,255,255,.05);
  box-shadow: 0 18px 42px rgba(0,0,0,.35);
  padding: 18px 16px 14px 16px;
}
.card::before{
  content:"";
  position:absolute; left:0; top:0; right:0;
  height: 12px;
  border-bottom: 1px solid rgba(255,255,255,.10);
}
.card.p5::before{ background: var(--stripe-p5); }
.card.voca::before{ background: var(--stripe-voca); }
.card.hub::before{ background: var(--stripe-hub); }
.card.arm::before{ background: var(--stripe-arm); }

.t{
  font-size: 18px;
  font-weight: 1000;
  margin: 4px 0 6px 0;
}
.d{
  font-size: 13px;
  color: rgba(255,255,255,.78);
  font-weight: 850;
  line-height: 1.35;
  margin-bottom: 12px;
}

.minirow{ display:flex; gap:8px; flex-wrap:wrap; margin-bottom: 10px; }
.mini{
  font-size: 12px;
  font-weight: 950;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,.12);
  background: rgba(255,255,255,.06);
  color: rgba(255,255,255,.90);
}

/* buttons */
div[data-testid="stButton"] > button{
  width:100% !important;
  border-radius: 16px !important;
  border: 1px solid rgba(0,0,0,.10) !important;
  background: rgba(255,255,255,.92) !important;
  color: #0B0E14 !important;
  font-weight: 1000 !important;
  letter-spacing: .35px !important;
  height: 78px !important;
  font-size: 18px !important;
  box-shadow: 0 12px 26px rgba(0,0,0,.26) !important;
  white-space: pre-line !important;
}
div[data-testid="stButton"] > button:hover{
  transform: translateY(-1px);
}

.sep{ height: 10px; }
.footerbtn div[data-testid="stButton"] > button{
  height: 72px !important;
  font-size: 18px !important;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown('<div class="h1">🗡 Secret Armory</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">P5 저장 문제 / P7 저장 단어 — TRAIN(정리) / BATTLE(시험) 4갈래 입구</div>', unsafe_allow_html=True)

left, right = st.columns(2, gap="large")

with left:
    st.markdown(
        """
        <div class="card p5">
          <div class="t">🧨 P5 무기고</div>
          <div class="d">저장된 P5 문제로 연습/시험</div>
          <div class="minirow">
            <div class="mini">🟩 TRAIN</div>
            <div class="mini">🔥 BATTLE</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("🟩 P5 TRAIN", use_container_width=True, key="go_p5_train"):
        safe_switch("pages/02_P5_Train_Arena.py")
    if st.button("🔥 P5 BATTLE", use_container_width=True, key="go_p5_battle"):
        safe_switch("pages/02_P5_Armory_Battle.py")

with right:
    st.markdown(
        """
        <div class="card voca">
          <div class="t">🧩 VOCA 무기고 (P7 저장 단어)</div>
          <div class="d">저장된 단어로 정리/시험</div>
          <div class="minirow">
            <div class="mini">🟩 TRAIN</div>
            <div class="mini">🔥 BATTLE</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("🟩 VOCA TRAIN", use_container_width=True, key="go_voca_train"):
        safe_switch("pages/04_VOCA_Train_Arena.py")
    if st.button("🔥 VOCA BATTLE", use_container_width=True, key="go_voca_battle"):
        safe_switch("pages/04_VOCA_Battle_Arena.py")

st.markdown("<div class='sep'></div>", unsafe_allow_html=True)
st.markdown("<div class='footerbtn'>", unsafe_allow_html=True)
if st.button("🏠 Main Hub(본부) 복귀", use_container_width=True, key="go_home"):
    safe_switch("main_hub.py")
st.markdown("</div>", unsafe_allow_html=True)
