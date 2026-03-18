# pages/04_VOCA_Battle_Arena.py
# SnapQ TOEIC – VOCA BATTLE (Exam) Arena
# - 단어 무기고 실전 전용
# - 현재 arena._render_voca_timebomb()가 placeholder여도 진입은 정상
# - 다음 단계에서 15초/5문제 규칙으로 전장화하면 됨

import streamlit as st

st.set_page_config(
    page_title="🟥 VOCA BATTLE · SnapQ TOEIC",
    page_icon="🟥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

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

from app.arenas import secret_armory as arena

st.title("🟥 VOCA BATTLE")
st.caption("실전 모드. 다음 단계에서 타이머/연속 라운드 적용.")

items = arena._load_armory_items()   # type: ignore[attr-defined]
arena._render_voca_timebomb(items)   # type: ignore[attr-defined]

st.markdown("---")
if st.button("⬅ 무기고 로비", use_container_width=True):
    st.switch_page("pages/03_Secret_Armory_Main.py")

