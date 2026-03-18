from __future__ import annotations
import os
import streamlit as st

BUILD = "P7_PAGE_WRAPPER_IMPORTONLY__20260205"
st.caption(f"🧩 BUILD: {BUILD} | PAGE={os.path.abspath(__file__)}")

# ✅ IMPORTANT:
# p7_reading_arena.py is a "script-style" arena (renders on import).
# So we DO NOT call arena.run().
from app.arenas import p7_reading_arena as arena
st.caption(f"🔎 P7 ARENA REAL FILE: {os.path.abspath(arena.__file__)}")
