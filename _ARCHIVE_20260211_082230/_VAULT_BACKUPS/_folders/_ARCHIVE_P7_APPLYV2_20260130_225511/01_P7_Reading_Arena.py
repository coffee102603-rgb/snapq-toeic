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
# SNAPQ_GLOBAL_CSS_LOADER
from app.arenas import p7_reading_arena

def run():
    # ✅ SINGLE SOURCE OF TRUTH
    return p7_reading_arena.run()

if __name__ == "__main__":
    run()
