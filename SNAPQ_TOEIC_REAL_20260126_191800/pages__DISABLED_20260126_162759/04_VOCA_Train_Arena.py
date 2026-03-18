# pages/04_VOCA_Train_Arena.py
# SnapQ TOEIC – VOCA TRAIN (Study) Arena
# - 단어 무기고 학습 전용
# - 시간 제한 없음

import streamlit as st

st.set_page_config(
    page_title="🟩 VOCA TRAIN · SnapQ TOEIC",
    page_icon="🟩",
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

st.title("🟩 VOCA TRAIN")
st.caption("시간 제한 없음. 단어를 넘기며 감각을 만든다.")

items = arena._load_armory_items()  # type: ignore[attr-defined]
arena._render_voca_flip(items)      # type: ignore[attr-defined]

st.markdown("---")
if st.button("⬅ 무기고 로비", use_container_width=True):
    st.switch_page("pages/03_Secret_Armory_Main.py")

