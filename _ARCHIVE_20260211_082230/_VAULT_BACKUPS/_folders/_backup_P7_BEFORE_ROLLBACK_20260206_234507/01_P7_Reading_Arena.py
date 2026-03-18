from __future__ import annotations

import streamlit as st
import app.arenas.p7_reading_arena as arena

# ✅ BUILD/FILE TRACE (디버그용 - 이미 쓰고 계신 방식 유지)
st.markdown(
    f"🧩 **PAGE:** `{__file__}`",
)

arena.run()