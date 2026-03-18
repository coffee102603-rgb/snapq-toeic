# pages/07_P7_Reading_Arena_ZERO.py
# ============================================================
# P7 ZERO PAGE - MINIMAL SAFE RESET
# - Hide Streamlit chrome only
# - Do NOT touch overflow/height/scroll containers
# - Keep app/arenas/p7_reading_arena.py untouched
# ============================================================

from __future__ import annotations
import streamlit as st
import logging

logging.getLogger("streamlit.elements.lib.policies").setLevel(logging.ERROR)
logging.getLogger("streamlit.runtime.metrics_util").setLevel(logging.ERROR)


def _inject_minimal():
    st.markdown("""
<style>
header[data-testid="stHeader"],
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
footer{
  display:none !important;
  height:0 !important;
  margin:0 !important;
  padding:0 !important;
}
div[data-testid="stAppViewContainer"] > section > main{
  padding-top:0 !important;
  margin-top:0 !important;
}
.block-container{
  padding-top:0 !important;
  margin-top:0 !important;
  max-width:100% !important;
  padding-left:10px !important;
  padding-right:10px !important;
}
</style>
""", unsafe_allow_html=True)


def _import_arena_module():
    try:
        from app.arenas import p7_reading_arena as m  # type: ignore
        return m
    except Exception:
        import app.arenas.p7_reading_arena as m  # type: ignore
        return m


def main():
    try:
        st.set_page_config(
            page_title="SnapQ P7 Reading Arena (ZERO SAFE RESET)",
            page_icon="🔥",
            layout="wide",
            initial_sidebar_state="collapsed",
        )
    except Exception:
        pass

    st.markdown(
        '<div style="position:fixed;top:6px;right:10px;z-index:1000000;'
        'padding:4px 10px;border-radius:999px;font-size:12px;font-weight:900;'
        'background:rgba(34,211,238,0.18);border:1px solid rgba(34,211,238,0.35);'
        'color:#ffffff;backdrop-filter: blur(10px);">MIN RESET</div>',
        unsafe_allow_html=True,
    )

    m = _import_arena_module()
    _inject_minimal()

    old_inject = getattr(m, "inject_css", None)

    def patched_inject_css():
        try:
            if callable(old_inject):
                old_inject()
        except Exception:
            pass
        _inject_minimal()

    try:
        m.inject_css = patched_inject_css  # type: ignore
    except Exception:
        pass

    if hasattr(m, "run") and callable(getattr(m, "run")):
        m.run()
    else:
        m.reading_arena_page()

    _inject_minimal()


main()
