# pages/07_P7_Reading_Arena_ZERO.py
# ============================================================
# SNAPQ P7 READING ARENA (ZERO GAP) - SAFE WRAPPER PAGE v2.2
# - Keep app/arenas/p7_reading_arena.py untouched
# - Watermark + loaded file path
# - Patch inject_css() so ZERO CSS applies LAST
# - MAIN scroll ON (prevents "content invisible" issue)
# - Silence Streamlit empty-label warnings (console clean)
# ============================================================

from __future__ import annotations

import logging
import streamlit as st


# --- Silence Streamlit warnings about empty labels (safe) ---
logging.getLogger("streamlit.elements.lib.policies").setLevel(logging.ERROR)
logging.getLogger("streamlit.runtime.metrics_util").setLevel(logging.ERROR)


def _inject_zero_gap_lock():
    """Hide Streamlit top chrome + kill top gap."""
    st.markdown(
        """
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

/* Top padding truly 0 */
div[data-testid="stAppViewContainer"] > section > main,
section.main,
section.main > div,
.block-container{
  padding-top:0 !important;
  margin-top:0 !important;
}

/* Keep body from creating extra space */
html, body{
  height:100% !important;
  margin:0 !important;
  padding:0 !important;
  overflow:hidden !important;
  overscroll-behavior:none !important;
}

/* Make MAIN scrollable so content is always reachable */
div[data-testid="stAppViewContainer"] > section > main{
  height:100vh !important;
  overflow:auto !important;
}
.block-container{
  min-height:100vh !important;
  overflow:visible !important;
  max-width:100% !important;
  padding-left:10px !important;
  padding-right:10px !important;
  padding-bottom:24px !important;
}

/* HUD pinned to top */
.p7-hudbar{
  position: fixed !important;
  top:0 !important; left:0 !important; right:0 !important;
  z-index:999999 !important;
  margin:0 !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )


def _inject_scrollfix_lastwins():
    """Last-wins patch to avoid 'blank screen' + allow arena scrolling."""
    st.markdown(
        """
<style>
/* LAST-WINS: allow battlefield scroll too */
.p7-battlefield{
  overflow-y:auto !important;
  overflow-x:hidden !important;
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
            st.error("P7 arena 모듈 import 실패: app/arenas/p7_reading_arena.py 경로 확인 필요")
            st.code(str(e))
            st.stop()


def main():
    # set_page_config 중복 방어
    try:
        st.set_page_config(
            page_title="SnapQ P7 Reading Arena (ZERO GAP v2.2)",
            page_icon="🔥",
            layout="wide",
            initial_sidebar_state="collapsed",
        )
    except Exception:
        pass

    # Watermark + proof
    st.markdown(
        '<div style="position:fixed;top:6px;right:10px;z-index:1000000;'
        'padding:4px 10px;border-radius:999px;font-size:12px;font-weight:950;'
        'background:rgba(34,211,238,0.30);border:1px solid rgba(34,211,238,0.55);'
        'color:#ffffff;backdrop-filter: blur(10px);">'
        '✅ ZERO GAP v2 LOADED</div>',
        unsafe_allow_html=True,
    )
    st.caption("✅ P7 ZERO GAP v2 PAGE LOADED (이 문구가 안 보이면 다른 파일입니다)")

    m = _import_arena_module()
    st.caption(f"LOADED ARENA FILE = {getattr(m, '__file__', 'UNKNOWN')}")

    # Inject base lock early
    _inject_zero_gap_lock()

    # Monkeypatch: ensure our CSS applies after arena inject_css
    old_inject = getattr(m, "inject_css", None)

    def patched_inject_css():
        try:
            if callable(old_inject):
                old_inject()
        except Exception:
            pass
        _inject_zero_gap_lock()
        _inject_scrollfix_lastwins()

    try:
        m.inject_css = patched_inject_css  # type: ignore
    except Exception:
        pass

    # Run arena (keep original logic untouched)
    if hasattr(m, "run") and callable(getattr(m, "run")):
        m.run()
    elif hasattr(m, "reading_arena_page") and callable(getattr(m, "reading_arena_page")):
        m.reading_arena_page()
    else:
        st.error("P7 arena 엔트리(run/reading_arena_page) 없음")
        st.stop()

    # Last-wins injection (after arena renders)
    _inject_zero_gap_lock()
    _inject_scrollfix_lastwins()


main()
