from __future__ import annotations
import os
import streamlit as st

BUILD = "P7_PAGE_WRAPPER_ENTRYFIX__20260205"
st.caption(f"🧩 BUILD: {BUILD} | PAGE={os.path.abspath(__file__)}")

from app.arenas import p7_reading_arena as arena
st.caption(f"🔎 P7 ARENA REAL FILE: {os.path.abspath(arena.__file__)}")

# Auto-entry call
ENTRY = ""
if hasattr(arena, ENTRY):
    getattr(arena, ENTRY)()
else:
    st.error(f"❌ Entry function not found in arena: {ENTRY}")
