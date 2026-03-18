# pages/07_P7_Reading_Arena_ZERO.py
# ============================================================
# SNAPQ P7 READING ARENA (ZERO TOP GAP) - SAFE WRAPPER PAGE v2
# - Does NOT modify app/arenas/p7_reading_arena.py
# - Strong "Last-Wins" CSS (inject BEFORE + AFTER)
# - Shows watermark to prove THIS page is loaded
# ============================================================

from __future__ import annotations
import time
import streamlit as st

import logging

# === SILENCE_STREAMLIT_LABEL_WARNINGS (SAFE) ===
# Streamlit warns repeatedly when st.radio(label="") is used.
# We keep the arena file untouched and simply silence that warning logger here.
logging.getLogger("streamlit.elements.lib.policies").setLevel(logging.ERROR)
logging.getLogger("streamlit.runtime.metrics_util").setLevel(logging.ERROR)


def _inject_zero_gap_lock():
    st.markdown(r"""


