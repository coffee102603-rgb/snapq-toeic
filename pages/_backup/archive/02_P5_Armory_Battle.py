# pages/02_P5_Armory_Battle.py
# SnapQ TOEIC - P5 ARMORY BATTLE (Selector Hub)
# - Engine/data stay the same
# - This page only routes user to:
#   1) P5 Timebomb Arena
#   2) P5 Exam 10Q Arena
#   3) Back to Secret Armory Lobby

import streamlit as st



st.set_page_config(
    page_title="🔥 P5 ARMORY BATTLE · SnapQ TOEIC",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ===== TRACE BANNER =====
try:
    st.error("🔥 SECRET ARMORY FILE LOADED: FILE = " + __file__)
except Exception:
    pass
# ========================

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
    if hasattr(st, "switch_page"):
        try:
            st.switch_page(target)  # type: ignore[attr-defined]
            return
        except Exception:
            pass
    st.info("이 환경에선 페이지 이동이 제한될 수 있어요. (좌측 사이드바/브라우저 뒤로가기)")


def _count_p5_items() -> int:
    """Count saved P5 items in armory without changing any engine logic."""
    try:
        from app.arenas import secret_armory as arena  # type: ignore[attr-defined]
        items = arena._load_armory_items()  # type: ignore[attr-defined]
        return sum(1 for x in (items or []) if isinstance(x, dict) and x.get("source") == "P5")
    except Exception:
        return 0


st.markdown("# 🔥 P5 ARMORY BATTLE")
st.caption("호환 모드: 저장된 P5 문제로 전장 진입 (전장 선택 화면)")

cnt = _count_p5_items()
st.markdown(
    f"""
    <div style="
      padding:14px 16px;
      border-radius:16px;
      background: rgba(255,255,255,0.10);
      border: 1px solid rgba(255,255,255,0.14);
      font-weight: 950;
    ">
      저장된 P5 문제 수: <b>{cnt}</b>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

c1, c2 = st.columns(2, gap="large")
with c1:
    if st.button("🧨 P5 TIMEBOMB 전장으로", use_container_width=True, key="go_p5_timebomb_from_armory"):
        _switch("pages/02_P5_Timebomb_Arena.py")

with c2:
    if st.button("🔥 P5 EXAM 10Q-55s로", use_container_width=True, key="go_p5_exam10q_from_armory"):
        _switch("pages/02_P5_Exam_10Q_55S.py")

st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

if st.button("⬅ 무기고 로비", use_container_width=True, key="back_to_armory_lobby"):
    _switch("pages/03_Secret_Armory_Main.py")