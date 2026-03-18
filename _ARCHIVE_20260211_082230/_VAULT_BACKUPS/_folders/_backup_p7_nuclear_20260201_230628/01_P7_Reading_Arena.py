# pages/01_P7_Reading_Arena.py
# ============================================================
# SAFE REDIRECTOR
# - Any old route to P7 goes to ZERO GAP page
# ============================================================
import streamlit as st
try:
    st.switch_page("pages/07_P7_Reading_Arena_ZERO.py")
except Exception:
    st.error("Redirect failed: pages/07_P7_Reading_Arena_ZERO.py not found")
