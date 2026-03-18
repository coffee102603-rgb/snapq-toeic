# pages/02_P5_Armory_Battle.py
# SnapQ TOEIC - P5 ARMORY BATTLE (Selector Hub)
# B-PLAN: UI Restore (Card Lobby) / Engine & Data 0 change

import streamlit as st

st.set_page_config(
    page_title="🔥 P5 ARMORY BATTLE · SnapQ TOEIC",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ------------------------------------------------------------
# Debug banner switch (default OFF)
# ------------------------------------------------------------
if "DEBUG_BANNER" not in st.session_state:
    st.session_state["DEBUG_BANNER"] = False

with st.sidebar:
    st.markdown("### 🛠 DEBUG")
    st.session_state["DEBUG_BANNER"] = st.checkbox(
        "Show debug banner (FILE path)",
        value=bool(st.session_state.get("DEBUG_BANNER", False)),
        key="dbg_banner_toggle",
    )

if st.session_state.get("DEBUG_BANNER", False):
    try:
        st.warning("🧩 FILE LOADED: " + __file__)
    except Exception:
        pass

# Theme (keep if available)
try:
    from app.core.ui_shell import apply_ui_shell
    apply_ui_shell(theme="armory")
except Exception:
    pass

try:
    from app.core.battle_theme import apply_battle_theme
    apply_battle_theme()
except Exception:
    pass


def _switch(target: str):
    """Navigation: keep switch_page only (stable)."""
    try:
        st.switch_page(target)  # type: ignore[attr-defined]
        return
    except Exception:
        st.error("페이지 이동 실패 🧨 (파일 경로/페이지 등록을 확인하세요)")
        st.stop()


def _count_p5_items() -> int:
    """Count saved P5 items in armory without changing any engine logic."""
    try:
        from app.arenas import secret_armory as arena  # type: ignore[attr-defined]
        items = arena._load_armory_items()  # type: ignore[attr-defined]
        return sum(1 for x in (items or []) if isinstance(x, dict) and x.get("source") == "P5")
    except Exception:
        return 0


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

  --p5a:#FF2D55;
  --p5b:#FF7A18;
  --vio:#A78BFA;
  --cyan:#00E5FF;

  --glass: rgba(255,255,255,.06);
  --glass2: rgba(255,255,255,.10);
}

html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"]{
  background:
    radial-gradient(900px 650px at 18% 8%, rgba(255,45,85,.20), transparent 55%),
    radial-gradient(820px 620px at 78% 10%, rgba(255,122,24,.18), transparent 58%),
    radial-gradient(1000px 900px at 50% 80%, rgba(0,229,255,.10), transparent 70%),
    linear-gradient(180deg, #111827 0%, #0B0E14 60%, #070A10 100%) !important;
  color: var(--txt) !important;
}

header, footer {display:none;}
[data-testid="stHeader"]{display:none !important;}
[data-testid="stToolbar"]{display:none !important;}
#MainMenu{display:none !important;}

.block-container{
  max-width: 1040px;
  padding-top: 0.9rem;
  padding-bottom: 1.4rem;
}

@media (max-width: 520px){
  .block-container{ padding-left: .85rem; padding-right: .85rem; }
}

.h-title{
  font-weight: 1000;
  font-size: 44px;
  letter-spacing: -0.5px;
  margin: 0.2rem 0 0.25rem 0;
  text-shadow: 0 10px 24px rgba(0,0,0,.40);
}
.h-sub{
  color: var(--muted);
  font-weight: 800;
  font-size: 13px;
  letter-spacing: .2px;
  margin-bottom: 0.75rem;
}

/* HUD pill */
.hud{
  border-radius: 18px;
  padding: 14px 16px;
  border: 1px solid rgba(255,255,255,.12);
  background: rgba(255,255,255,.06);
  box-shadow: 0 14px 34px rgba(0,0,0,.30);
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 10px;
}
.hud .left{
  display:flex;
  flex-direction:column;
  gap: 4px;
}
.hud .k{
  font-size: 12px;
  letter-spacing: .3px;
  color: rgba(255,255,255,.72);
  font-weight: 900;
}
.hud .v{
  font-size: 18px;
  font-weight: 1000;
}
.hud .tag{
  padding: 8px 10px;
  border-radius: 999px;
  font-weight: 1000;
  font-size: 12px;
  border: 1px solid rgba(255,255,255,.14);
  background: linear-gradient(90deg, rgba(255,45,85,.16), rgba(255,122,24,.12));
}

/* Cards */
.card{
  border-radius: 20px;
  border: 1px solid rgba(255,255,255,.12);
  background: rgba(255,255,255,.05);
  box-shadow: 0 18px 42px rgba(0,0,0,.35);
  overflow:hidden;
  position: relative;
  padding: 18px 16px 16px 16px;
}
.card::before{
  content:"";
  position:absolute; left:0; top:0; right:0;
  height: 12px;
  border-bottom: 1px solid rgba(255,255,255,.10);
  background: linear-gradient(90deg, var(--p5a), var(--p5b));
}

.card .t{
  font-size: 18px;
  font-weight: 1000;
  margin: 4px 0 6px 0;
}
.card .d{
  font-size: 13px;
  color: rgba(255,255,255,.76);
  font-weight: 850;
  line-height: 1.35;
  margin-bottom: 12px;
}

.card .minirow{
  display:flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}
.mini{
  font-size: 12px;
  font-weight: 950;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,.12);
  background: rgba(255,255,255,.06);
  color: rgba(255,255,255,.90);
}
.mini.hot{ border-color: rgba(255,45,85,.35); background: rgba(255,45,85,.12); }
.mini.cool{ border-color: rgba(0,229,255,.25); background: rgba(0,229,255,.08); }
.mini.vio{ border-color: rgba(167,139,250,.25); background: rgba(167,139,250,.10); }

/* Big buttons */
div[data-testid="stButton"] > button{
  width: 100% !important;
  border-radius: 16px !important;
  border: 1px solid rgba(0,0,0,.10) !important;
  background: rgba(255,255,255,.92) !important;
  color: #0B0E14 !important;
  font-weight: 1000 !important;
  letter-spacing: .4px !important;
  height: 86px !important;
  font-size: 20px !important;
  box-shadow: 0 12px 26px rgba(0,0,0,.26) !important;
  white-space: pre-line !important;
}
div[data-testid="stButton"] > button:hover{
  transform: translateY(-1px);
  border-color: rgba(255,45,85,.40) !important;
}

@media (max-width: 520px){
  div[data-testid="stButton"] > button{
    height: 78px !important;
    font-size: 18px !important;
  }
}

.sep{
  height: 10px;
}
.footerbtn div[data-testid="stButton"] > button{
  height: 72px !important;
  font-size: 18px !important;
}
</style>
""",
    unsafe_allow_html=True,
)

st.markdown("## 🔥 P5 ARMORY BATTLE")
st.markdown("<div class='h-sub'>저장된 P5 문제로 전장 진입 (전장 선택 로비)</div>", unsafe_allow_html=True)

cnt = _count_p5_items()
st.markdown(
    f"""
    <div class="hud">
      <div class="left">
        <div class="k">ARMORY STOCK</div>
        <div class="v">저장된 P5 문제 수: <b>{cnt}</b></div>
      </div>
      <div class="tag">⚠️ BATTLE SELECTOR</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div class='sep'></div>", unsafe_allow_html=True)

c1, c2 = st.columns(2, gap="large")

with c1:
    st.markdown(
        """
        <div class="card">
          <div class="t">🧨 P5 TIMEBOMB 전장</div>
          <div class="d">
            5문제 미션 · 시간폭탄 HUD · 오답 누적 폭발<br/>
            (문법/어휘 선택 → 즉시 출격)
          </div>
          <div class="minirow">
            <div class="mini hot">⏱ 40/60/80s</div>
            <div class="mini vio">🎯 Grammar / Voca</div>
            <div class="mini cool">🏠 Hub 복귀</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("🧨 P5 TIMEBOMB\n전장 입장", use_container_width=True, key="go_p5_timebomb_from_armory"):
        _switch("pages/02_P5_Timebomb_Arena.py")

with c2:
    st.markdown(
        """
        <div class="card">
          <div class="t">🔥 P5 EXAM 10Q · 55s</div>
          <div class="d">
            10문항 시험 모드 · 카드 클릭 4지선다<br/>
            (빠른 실전 감각 체크)
          </div>
          <div class="minirow">
            <div class="mini hot">⏱ 55s</div>
            <div class="mini vio">🎯 10 Questions</div>
            <div class="mini cool">⚡ Sudden Death</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    # NOTE: existing routing target kept as-is (engine/structure 0 change)
    if st.button("🔥 P5 EXAM 10Q\n55s 미션", use_container_width=True, key="go_p5_exam10q_from_armory"):
        _switch("pages/02_P5_Exam_10Q_55S.py")

st.markdown("<div class='sep'></div>", unsafe_allow_html=True)

st.markdown("<div class='footerbtn'>", unsafe_allow_html=True)
if st.button("⬅ 무기고 로비로", use_container_width=True, key="back_to_armory_lobby"):
    _switch("pages/03_Secret_Armory_Main.py")
st.markdown("</div>", unsafe_allow_html=True)
