from __future__ import annotations
import os
import streamlit as st

BUILD = "P7_PAGE_WRAPPER_LOCK__20260205"
st.caption(f"🧩 BUILD: {BUILD} | PAGE={os.path.abspath(__file__)}")

# arena import (real runtime)
from app.arenas import p7_reading_arena as arena
st.caption(f"🔎 P7 ARENA REAL FILE: {os.path.abspath(arena.__file__)}")

arena.run()
