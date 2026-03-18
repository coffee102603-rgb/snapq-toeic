import streamlit as st

# ============================================================
# SnapQ Secret Armory - Wrapper (ARENA 100% Delegation)
# - This page must NOT draw UI (no mode selectors, no layout)
# - Single source of truth: app/arenas/secret_armory.py
# ============================================================

st.set_page_config(page_title="SnapQ • Secret Armory", layout="wide")

try:
    from app.arenas.secret_armory import render
    render()
except Exception as e:
    st.error("❌ Secret Armory wrapper failed to load arena.")
    st.code(f"WRAPPER: {__file__}")
    st.exception(e)
