# pages/07_P7_Reading_Arena_ZERO.py
# ============================================================
# SNAPQ P7 READING ARENA - ZERO TOP GAP (STABLE WRAPPER v3.1)
# - Keep app/arenas/p7_reading_arena.py untouched
# - REAL FIX: HUD is .p7-hud-compact (not p7-hudbar)
# - Pin HUD + Gauge to TOP with minimal reserved space
# - Reduce jitter: disable scroll anchoring
# ============================================================

from __future__ import annotations

import logging
import streamlit as st

logging.getLogger("streamlit.elements.lib.policies").setLevel(logging.ERROR)
logging.getLogger("streamlit.runtime.metrics_util").setLevel(logging.ERROR)


def _inject_zero_gap_v31():
    st.markdown(
        r"""
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

/* Kill top padding */
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

/* Reduce "jump" on rerun */
* { overflow-anchor: none !important; }

/* ------------------------------------------------------------
   ✅ REAL HUD FIX: p7_reading_arena uses .p7-hud-compact
   ------------------------------------------------------------ */
:root{
  --p7HudH: 52px;   /* HUD 실측보다 약간 여유 */
  --p7GaugeH: 12px; /* 게이지 */
}

/* HUD pinned */
.p7-hud-compact{
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  z-index: 999999 !important;

  margin: 0 !important;
  border-radius: 0 !important;

  /* 좌우가 너무 넓으면 답답하니 살짝만 */
  width: 100% !important;
}

/* 게이지도 HUD 아래에 고정 */
.p7-hud-gauge{
  position: fixed !important;
  top: var(--p7HudH) !important;
  left: 0 !important;
  right: 0 !important;
  z-index: 999998 !important;

  margin: 0 !important;
  border-radius: 0 !important;
}

/* 본문은 HUD+게이지만큼만 아래로(최소) */
.p7-battlefield,
.p7-zone,
.p7-opt-wrap{
  scroll-margin-top: calc(var(--p7HudH) + var(--p7GaugeH)) !important;
}

div.block-container{
  padding-top: calc(var(--p7HudH) + var(--p7GaugeH) + 6px) !important;
}

/* 카드 간격도 약간 타이트 */
.p7-zone{ margin: 6px 0 !important; }
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
    try:
        st.set_page_config(
            page_title="SnapQ P7 Reading Arena (ZERO GAP v3.1)",
            page_icon="🔥",
            layout="wide",
            initial_sidebar_state="collapsed",
        )
    except Exception:
        pass

    # fixed badge (layout 영향 없음)
    st.markdown(
        '<div style="position:fixed;top:6px;right:10px;z-index:1000000;'
        'padding:4px 10px;border-radius:999px;font-size:12px;font-weight:900;'
        'background:rgba(34,211,238,0.22);border:1px solid rgba(34,211,238,0.45);'
        'color:#ffffff;backdrop-filter: blur(10px);">'
        'ZERO GAP v3.1</div>',
        unsafe_allow_html=True,
    )

    m = _import_arena_module()

    # Apply early
    _inject_zero_gap_v31()

    # Apply last (after arena inject_css)
    old_inject = getattr(m, "inject_css", None)

    def patched_inject_css():
        try:
            if callable(old_inject):
                old_inject()
        except Exception:
            pass
        _inject_zero_gap_v31()

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
    _inject_zero_gap_v31()


main()
