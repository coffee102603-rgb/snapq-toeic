# pages/07_P7_Reading_Arena_ZERO.py
# ============================================================
# SNAPQ P7 READING ARENA (ZERO TOP GAP) - SAFE WRAPPER PAGE
# - Does NOT modify app/arenas/p7_reading_arena.py
# - Monkeypatch inject_css() so ZERO-GAP CSS is applied LAST
# ============================================================

from __future__ import annotations

import streamlit as st


def _inject_zero_gap_lock():
    st.markdown(
        r"""
<style>
/* =========================================================
   P7 ZERO TOP GAP LOCK (LAST WINS)
   핵심:
   1) 상단 헤더/툴바/장식 제거
   2) 상단 padding/margin 0
   3) body 스크롤 OFF (두번째 화면/빈 그라데이션 원천차단)
   4) 전장(.p7-battlefield)만 스크롤
   ========================================================= */

header[data-testid="stHeader"],
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
footer{
  display:none !important;
  height:0 !important;
  margin:0 !important;
  padding:0 !important;
}

/* 문서 스크롤 OFF */
html, body{
  height:100% !important;
  overflow:hidden !important;
  margin:0 !important;
  padding:0 !important;
  overscroll-behavior:none !important;
}

/* Streamlit 상위 컨테이너 고정 + 상단 여백 0 */
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

/* ✅ 전장만 스크롤 */
.p7-battlefield{
  height: 100vh !important;
  overflow-y: auto !important;
  overflow-x: hidden !important;
  margin-top: 0 !important;
  padding-top: 0 !important;
  padding-bottom: 22px !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )


def _import_arena_module():
    # 프로젝트 구조가 다를 수 있어 여러 후보를 안전하게 시도
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
                st.error("P7 arena 모듈 import 실패: app/arenas/p7_reading_arena.py 경로를 확인해주세요.")
                st.code(str(e))
                st.stop()


def main():
    # 페이지 설정(중복 set_page_config 방어)
    try:
        st.set_page_config(
            page_title="SnapQ P7 Reading Arena (ZERO GAP)",
            page_icon="🔥",
            layout="wide",
            initial_sidebar_state="collapsed",
        )
    except Exception:
        pass

    m = _import_arena_module()

    # ✅ 핵심: 기존 inject_css()를 '후킹'해서 마지막에 ZERO GAP LOCK을 반드시 넣는다.
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
    # run()이 있으면 그걸 사용 (프로젝트에서 pages/.. 와 main_hub.py가 쓰는 엔트리)
    if hasattr(m, "run") and callable(getattr(m, "run")):
        return m.run()
    # 없으면 reading_arena_page()로 폴백
    if hasattr(m, "reading_arena_page") and callable(getattr(m, "reading_arena_page")):
        return m.reading_arena_page()

    st.error("P7 arena 엔트리(run/reading_arena_page)를 찾지 못했습니다.")
    st.stop()


main()
