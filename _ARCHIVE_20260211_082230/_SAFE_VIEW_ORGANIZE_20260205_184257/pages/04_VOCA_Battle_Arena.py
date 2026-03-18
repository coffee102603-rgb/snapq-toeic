import streamlit as st

# --- SNAPQ_MAIN_HUB_NAV (auto) ---
try:
    _hub_col, _hub_spacer = st.columns([1.4, 8.6])
    with _hub_col:
        if st.button("🏠 MAIN HUB", key=f"hub_{__file__}", use_container_width=True):
            try:
                st.switch_page("main_hub.py")
            except Exception:
                st.info("좌측 메뉴(사이드바)에서 Main Hub로 이동해주세요.")
except Exception:
    pass
# --- /SNAPQ_MAIN_HUB_NAV ---


st.set_page_config(
    page_title="🔥 VOCA BATTLE · SnapQ",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from app.arenas import secret_armory as arena
st.session_state["armory_mode"] = "VOCA_BATTLE"
arena.render()