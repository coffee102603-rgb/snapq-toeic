import streamlit as st

# --- SNAPQ_MAIN_HUB_NAV (auto) ---
try:
    _hub_col, _hub_spacer = st.columns([1.4, 8.6])
    with _hub_col:
        if st.button("🏠 MAIN HUB", key=f"hub_{__file__}", use_container_width=True):
            try:
                st.switch_page("main_hub.py")
            except Exception:
                st.info("좌측 메뉴(사이드바)에서 Main Hub로 이동해주세요.")
except Exception:
    pass
# --- /SNAPQ_MAIN_HUB_NAV ---


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
