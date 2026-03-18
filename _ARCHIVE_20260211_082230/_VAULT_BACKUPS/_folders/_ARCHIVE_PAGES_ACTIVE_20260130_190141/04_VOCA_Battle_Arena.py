import streamlit as st

st.set_page_config(
    page_title="🔥 VOCA BATTLE · SnapQ",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

from app.arenas import secret_armory as arena
st.session_state["armory_mode"] = "VOCA_BATTLE"
arena.render()
