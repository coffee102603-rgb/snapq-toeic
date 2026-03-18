# ===== SNAPQ ARMORY TRACE BANNER (AUTO) =====
try:
    import streamlit as st
    st.error("🔥 SECRET ARMORY FILE LOADED: __FILE__ = " + __file__)
except Exception:
    pass
# ===========================================
# pages/02_P5_Armory_Battle.py
# SnapQ TOEIC ??P5 ARMORY BATTLE
# - "蹂묎린怨좎뿉 ??λ맂 P5 臾몄젣"濡쒕쭔 ?쒗뿕(?꾩옣) 吏꾪뻾
# - secret_armory.py??_render_p5_timebomb(items) ?몄텧

import streamlit as st

st.set_page_config(
    page_title="?윥 P5 ARMORY BATTLE 쨌 SnapQ TOEIC",
    page_icon="?윥",
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
if st.button("燧?臾닿린怨?濡쒕퉬", use_container_width=True):
    st.switch_page("pages/03_Secret_Armory_Main.py")

