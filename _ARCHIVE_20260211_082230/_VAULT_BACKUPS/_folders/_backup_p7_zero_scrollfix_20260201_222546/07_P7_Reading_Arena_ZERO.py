# pages/07_P7_Reading_Arena_ZERO.py
# ============================================================
# SNAPQ P7 READING ARENA (ZERO TOP GAP) - SAFE WRAPPER PAGE v2
# - Does NOT modify app/arenas/p7_reading_arena.py
# - Strong "Last-Wins" CSS (inject BEFORE + AFTER)
# - Shows watermark to prove THIS page is loaded
# ============================================================

from __future__ import annotations
import time
import streamlit as st

import logging

# === SILENCE_STREAMLIT_LABEL_WARNINGS (SAFE) ===
# Streamlit warns repeatedly when st.radio(label="") is used.
# We keep the arena file untouched and simply silence that warning logger here.
logging.getLogger("streamlit.elements.lib.policies").setLevel(logging.ERROR)
logging.getLogger("streamlit.runtime.metrics_util").setLevel(logging.ERROR)


def _inject_zero_gap_lock():
    st.markdown(r"""
<style>
/* ===================== ZERO GAP HARD LOCK ===================== */

/* Streamlit top UI kill */
header[data-testid="stHeader"],
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
footer{
  display:none !important;
  height:0 !important;
  margin:0 !important;
  padding:0 !important;
}

/* Kill document scroll (prevents "second screen" blank area) */
html, body{
  height:100% !important;
  overflow:hidden !important;
  margin:0 !important;
  padding:0 !important;
  overscroll-behavior:none !important;
}

/* Force top padding/margins to 0 everywhere */
.stApp,
div[data-testid="stAppViewContainer"],
div[data-testid="stAppViewContainer"] > section,
div[data-testid="stAppViewContainer"] > section > main,
section.main,
section.main > div,
.block-container{
  height:100vh !important;
  overflow:hidden !important;
  padding-top:0 !important;
  margin-top:0 !important;
  padding-bottom:0 !important;
  margin-bottom:0 !important;
}

.block-container{
  max-width: 100% !important;
  padding-left: 10px !important;
  padding-right: 10px !important;
}

/* ======= 핵심: HUD를 무조건 맨 위에 고정 ======= */
.p7-hudbar{
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  z-index: 999999 !important;
  margin: 0 !important;
}

/* HUD 아래 게이지/본문이 HUD에 가리지 않게 */
:root{
  --p7-hud-h: 64px;
  --p7-gauge-h: 10px;
}

/* 기존 전장 레이아웃을 "전장만 스크롤"로 강제 */
.p7-battlefield{
  height: calc(100vh - (var(--p7-hud-h) + var(--p7-gauge-h))) !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  margin-top: calc(var(--p7-hud-h) + var(--p7-gauge-h)) !important;
  padding-top: 8px !important;
  padding-bottom: 22px !important;
}

/* 혹시 상단에 빈 div가 있는 경우를 강제로 눌러버림 */
div[data-testid="stVerticalBlock"] > div:empty{
  margin:0 !important;
  padding:0 !important;
  height:0 !important;
}

/* 워터마크(눈으로 확인용) */
.p7-zero-watermark{
  position: fixed !important;
  top: 6px !important;
  right: 10px !important;
  z-index: 1000000 !important;
  padding: 4px 10px !important;
  border-radius: 999px !important;
  font-size: 12px !important;
  font-weight: 950 !important;
  background: rgba(34,211,238,0.30) !important;
  border: 1px solid rgba(34,211,238,0.55) !important;
  color: #ffffff !important;
  backdrop-filter: blur(10px) !important;
}
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
        except Exception:
            try:
                import p7_reading_arena as m  # type: ignore
                return m
            except Exception as e:
                st.error("P7 arena 모듈 import 실패: app/arenas/p7_reading_arena.py 경로 확인 필요")
                st.code(str(e))
                st.stop()


def main():
    # set_page_config 중복 방어
    try:
        st.set_page_config(
            page_title="SnapQ P7 Reading Arena (ZERO GAP v2)",
            page_icon="🔥",
            layout="wide",
            initial_sidebar_state="collapsed",
        )
    except Exception:
        pass

    # ✅ 워터마크 + 로드 표시 (이게 안 보이면 다른 페이지임)
    st.markdown('<div class="p7-zero-watermark">✅ ZERO GAP v2 LOADED</div>', unsafe_allow_html=True)
    st.caption("✅ P7 ZERO GAP v2 PAGE LOADED (이 문구가 안 보이면 다른 파일입니다)")

    m = _import_arena_module()
    st.caption(f"LOADED ARENA FILE = {getattr(m, '__file__', 'UNKNOWN')}")

    # (1) 먼저 한 번 강제 주입
    _inject_zero_gap_lock()

    # ✅ 기존 inject_css 후킹: old -> zero
    old_inject = getattr(m, "inject_css", None)

    def patched_inject_css():
        try:
            if callable(old_inject):
                old_inject()
        except Exception:
            pass
        _inject_zero_gap_lock()

    try:
        m.inject_css = patched_inject_css  # type: ignore
    except Exception:
        pass

    # 전장 실행
    if hasattr(m, "run") and callable(getattr(m, "run")):
        m.run()
    elif hasattr(m, "reading_arena_page") and callable(getattr(m, "reading_arena_page")):
        m.reading_arena_page()
    else:
        st.error("P7 arena 엔트리(run/reading_arena_page) 없음")
        st.stop()

    # (2) 마지막에 또 한 번 강제 주입 (진짜 LAST-WINS)
    _inject_zero_gap_lock()


main()

