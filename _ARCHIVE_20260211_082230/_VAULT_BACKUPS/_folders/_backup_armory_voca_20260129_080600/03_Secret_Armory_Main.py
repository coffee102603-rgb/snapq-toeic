import streamlit as st

# ============================================================
# SECRET ARMORY (WRAPPER ONLY)
# - UI source of truth: app/arenas/secret_armory.py
# - This page must NOT draw TRAIN/BATTLE itself.
# ============================================================

st.set_page_config(page_title="Secret Armory", layout="wide")

# Tiny HUD chip (game-friendly)
st.markdown(
    f"""
    <style>
      .armory-chip {{
        display:inline-flex;
        align-items:center;
        gap:10px;
        padding: 8px 12px;
        border-radius: 999px;
        background: rgba(0,0,0,0.22);
        border: 1px solid rgba(255,120,80,0.35);
        color: #ffffff;
        font-weight: 900;
        margin-bottom: 10px;
      }}
      .armory-chip small{{opacity:.85;font-weight:800;}}
    </style>
    <div class="armory-chip">🔥 SECRET ARMORY <small>WRAPPER: {__file__}</small></div>
    """,
    unsafe_allow_html=True,
)

from app.arenas.secret_armory import render
render()
