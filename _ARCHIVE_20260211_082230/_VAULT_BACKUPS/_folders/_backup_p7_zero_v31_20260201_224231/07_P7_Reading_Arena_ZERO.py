# pages/07_P7_Reading_Arena_ZERO.py
# ============================================================
# SNAPQ P7 READING ARENA - ZERO TOP GAP (STABLE WRAPPER v3)
# - Keep app/arenas/p7_reading_arena.py untouched
# - Apply only minimal, stable CSS (no scroll/height forcing)
# - Avoid layout-shift elements (no st.caption)
# - Monkeypatch inject_css() so our CSS applies LAST
# ============================================================

from __future__ import annotations

import logging
import streamlit as st

# Quiet repeated accessibility warnings (safe)
logging.getLogger("streamlit.elements.lib.policies").setLevel(logging.ERROR)
logging.getLogger("streamlit.runtime.metrics_util").setLevel(logging.ERROR)


def _inject_zero_gap_minimal():
    st.markdown(
        """
<style>
/* Hide Streamlit chrome */
header[data-testid="stHeader"],
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
footer{
  display:none !important;
  height:0 !important;
  margin:0 !important;
  padding:0 !important;
}

/* Top gap kill (stable) */
div[data-testid="stAppViewContainer"] > section > main{
  padding-top:0 !important;
  margin-top:0 !important;
}
.block-container{
  padding-top:0 !important;
  margin-top:0 !important;
  padding-left:10px !important;
  padding-right:10px !important;
  max-width:100% !important;
}

/* Safety: remove any accidental top spacer blocks */
section.main > div:first-child{
  margin-top:0 !important;
  padding-top:0 !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )


def _import_arena_module():
    try:
        from app.arenas import p7_reading_arena as m  # type: ignore
        return m
    except Exception:
        try:
            import app.arenas.p7_reading_arena as m  # type: ignore
            return m
        except Exception as e:
            st.error("P7 arena import failed: app/arenas/p7_reading_arena.py")
            st.code(str(e))
            st.stop()


def main():
    # Guard against duplicate set_page_config
    try:
        st.set_page_config(
            page_title="SnapQ P7 Reading Arena (ZERO GAP v3)",
            page_icon="🔥",
            layout="wide",
            initial_sidebar_state="collapsed",
        )
    except Exception:
        pass

    # Fixed badge only (does not affect layout flow)
    st.markdown(
        '<div style="position:fixed;top:6px;right:10px;z-index:1000000;'
        'padding:4px 10px;border-radius:999px;font-size:12px;font-weight:900;'
        'background:rgba(34,211,238,0.22);border:1px solid rgba(34,211,238,0.45);'
        'color:#ffffff;backdrop-filter: blur(10px);">'
        'ZERO GAP v3</div>',
        unsafe_allow_html=True,
    )

    m = _import_arena_module()

    # Apply minimal CSS early
    _inject_zero_gap_minimal()

    # Monkeypatch inject_css so ours applies last (stable)
    old_inject = getattr(m, "inject_css", None)

    def patched_inject_css():
        try:
            if callable(old_inject):
                old_inject()
        except Exception:
            pass
        _inject_zero_gap_minimal()

    try:
        m.inject_css = patched_inject_css  # type: ignore
    except Exception:
        pass

    # Run original arena
    if hasattr(m, "run") and callable(getattr(m, "run")):
        m.run()
    elif hasattr(m, "reading_arena_page") and callable(getattr(m, "reading_arena_page")):
        m.reading_arena_page()
    else:
        st.error("P7 arena entry not found (run/reading_arena_page)")
        st.stop()

    # Last-wins
    _inject_zero_gap_minimal()


main()
