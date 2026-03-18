from __future__ import annotations

import streamlit as st

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

st.set_page_config(
    page_title="💣 P5 BATTLE+MINE · SnapQ TOEIC",
    page_icon="💣",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from app.arenas import p5_battle_mine_arena

p5_battle_mine_arena.render()