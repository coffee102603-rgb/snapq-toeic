import streamlit as st

# IMPORTANT:
# This page must NOT call private functions inside secret_armory.py (they may change).
# We only set the desired mode and delegate to arena.render() safely.

try:
    from app.arenas import secret_armory as arena
except Exception as e:
    st.error("Secret Armory 모듈 로드 실패: " + str(e))
    st.stop()

st.set_page_config(page_title="VOCA TRAIN", layout="wide")

# Force the mode that Armory should open with
st.session_state["armory_mode"] = "VOCA_TRAIN"
st.session_state["armory_submode"] = "TRAIN"

# Delegate rendering to the arena module
# (arena.render() should handle UI/CSS + TRAIN screen internally)
try:
    arena.render()
except Exception as e:
    st.error("VOCA TRAIN 렌더링 중 오류: " + str(e))
    st.stop()
