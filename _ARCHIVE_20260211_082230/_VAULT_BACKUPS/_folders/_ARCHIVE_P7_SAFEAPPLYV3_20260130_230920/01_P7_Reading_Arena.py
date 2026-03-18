import streamlit as st

# SNAPQ_GLOBAL_CSS_LOADER
import os as _os
def _snapq_load_global_css():
    _candidates = [
        _os.path.join("styles","global.css"),
        _os.path.join("assets","global.css"),
    ]
    _css = ""
    for _p in _candidates:
        if _os.path.exists(_p):
            try:
                with open(_p, "r", encoding="utf-8") as _f:
                    _css = _f.read()
                break
            except Exception:
                pass
    if _css:
        st.markdown("<style>" + _css + "</style>", unsafe_allow_html=True)

_snapq_load_global_css()
# /SNAPQ_GLOBAL_CSS_LOADER

from app.arenas import p7_reading_arena

def run():
    # ✅ SINGLE SOURCE OF TRUTH (SAFE FALLBACKS)
    if hasattr(p7_reading_arena, "run") and callable(getattr(p7_reading_arena, "run")):
        return p7_reading_arena.run()
    if hasattr(p7_reading_arena, "reading_arena_page") and callable(getattr(p7_reading_arena, "reading_arena_page")):
        return p7_reading_arena.reading_arena_page()
    st.error("P7 엔진 엔트리(run/reading_arena_page)를 찾지 못했습니다. app/arenas/p7_reading_arena.py를 확인해주세요.")
    st.stop()

if __name__ == "__main__":
    run()
