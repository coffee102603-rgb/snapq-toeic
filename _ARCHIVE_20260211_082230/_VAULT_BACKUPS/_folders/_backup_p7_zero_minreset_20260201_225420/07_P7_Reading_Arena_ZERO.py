# pages/07_P7_Reading_Arena_ZERO.py
# ============================================================
# SNAPQ P7 READING ARENA - ZERO TOP GAP (WRAPPER v3.4)
# - Fix: "blank screen" by NOT hiding block-container content
# - Fix: "drift" by disabling scroll anchoring + fixed HUD/Gauge
# - Battlefield scroll if present; else MAIN scroll fallback
# ============================================================

from __future__ import annotations
import logging
import streamlit as st

logging.getLogger("streamlit.elements.lib.policies").setLevel(logging.ERROR)
logging.getLogger("streamlit.runtime.metrics_util").setLevel(logging.ERROR)


def _inject_zero_gap_v34():
    st.markdown(r"""
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

/* Remove top gap */
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

/* Stop rerun "jump" */
* { overflow-anchor: none !important; }

:root{
  --p7HudH: 46px;
  --p7GaugeH: 10px;
}

/* Document scroll OFF (prevents drift feel) */
html, body{
  height:100% !important;
  overflow:hidden !important;
  margin:0 !important;
  padding:0 !important;
}

/* MAIN: fallback scroll container */
div[data-testid="stAppViewContainer"] > section > main{
  height:100vh !important;
  overflow:auto !important;           /* ✅ fallback */
  overscroll-behavior:none !important;
  scroll-behavior:auto !important;
}

/* IMPORTANT: do NOT hide content here (prevents blank screen) */
.block-container{
  height:auto !important;
  overflow:visible !important;        /* ✅ 콘텐츠가 어디에 렌더돼도 보이게 */
  padding-bottom:18px !important;
}

/* HUD fixed */
.p7-hud-compact{
  position: fixed !important;
  top: 0 !important; left: 0 !important; right: 0 !important;
  z-index: 999999 !important;

  height: var(--p7HudH) !important;
  box-sizing: border-box !important;
  margin: 0 !important;
  padding: 6px 10px !important;

  border-radius: 0 !important;
  background: rgba(0,0,0,0.22) !important;
  backdrop-filter: blur(8px) !important;
  -webkit-backdrop-filter: blur(8px) !important;
}

/* Gauge fixed under HUD */
.p7-hud-gauge{
  position: fixed !important;
  top: var(--p7HudH) !important;
  left: 0 !important; right: 0 !important;
  z-index: 999998 !important;

  height: var(--p7GaugeH) !important;
  margin: 0 !important;
  border-radius: 0 !important;
}

/* If battlefield exists: make it the scroll area (preferred) */
.p7-battlefield{
  position: relative !important;
  margin-top: calc(var(--p7HudH) + var(--p7GaugeH) + 6px) !important;

  height: calc(100vh - (var(--p7HudH) + var(--p7GaugeH) + 6px)) !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  padding-bottom: 18px !important;
}

/* If battlefield does NOT exist and content is in main flow:
   reserve space below fixed HUD+Gauge */
body:has(.p7-hud-compact) .block-container{
  padding-top: calc(var(--p7HudH) + var(--p7GaugeH) + 6px) !important;
}

/* Tighten cards */
.p7-zone{ margin: 6px 0 !important; }
</style>
    """, unsafe_allow_html=True)


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
    try:
        st.set_page_config(
            page_title="SnapQ P7 Reading Arena (ZERO GAP v3.4)",
            page_icon="🔥",
            layout="wide",
            initial_sidebar_state="collapsed",
        )
    except Exception:
        pass

    st.markdown(
        '<div style="position:fixed;top:6px;right:10px;z-index:1000000;'
        'padding:4px 10px;border-radius:999px;font-size:12px;font-weight:900;'
        'background:rgba(34,211,238,0.22);border:1px solid rgba(34,211,238,0.45);'
        'color:#ffffff;backdrop-filter: blur(10px);">'
        'ZERO GAP v3.4</div>',
        unsafe_allow_html=True,
    )

    m = _import_arena_module()
    _inject_zero_gap_v34()

    old_inject = getattr(m, "inject_css", None)

    def patched_inject_css():
        try:
            if callable(old_inject):
                old_inject()
        except Exception:
            pass
        _inject_zero_gap_v34()

    try:
        m.inject_css = patched_inject_css  # type: ignore
    except Exception:
        pass

    if hasattr(m, "run") and callable(getattr(m, "run")):
        m.run()
    elif hasattr(m, "reading_arena_page") and callable(getattr(m, "reading_arena_page")):
        m.reading_arena_page()
    else:
        st.error("P7 arena entry not found (run/reading_arena_page)")
        st.stop()

    _inject_zero_gap_v34()


main()
