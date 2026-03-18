# pages/02_P5_Armory_Battle.py
# SnapQ TOEIC – P5 ARMORY BATTLE
# - "병기고에 저장된 P5 문제"로만 시험(전장) 진행
# - secret_armory.py의 _render_p5_timebomb(items) 호출

import streamlit as st

st.set_page_config(
    page_title="🟥 P5 ARMORY BATTLE · SnapQ TOEIC",
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

items = arena._load_armory_items()        # type: ignore[attr-defined]
arena._render_p5_timebomb(items)          # type: ignore[attr-defined]

st.markdown("---")
if st.button("⬅ 무기고 로비", use_container_width=True):
    st.switch_page("pages/03_Secret_Armory_Main.py")
