# pages/07_P7_Reading_Arena_ZERO.py
# ============================================================
# P7 ZERO PAGE - MIN RESET + SCROLL LOCK (SAFE)
# - Keep app/arenas/p7_reading_arena.py untouched
# - Hide Streamlit chrome + kill top padding
# - Force scroll to TOP on each rerun (fixes "drifting downward")
# ============================================================

from __future__ import annotations
import logging
import streamlit as st
import streamlit.components.v1 as components

logging.getLogger("streamlit.elements.lib.policies").setLevel(logging.ERROR)
logging.getLogger("streamlit.runtime.metrics_util").setLevel(logging.ERROR)


def _inject_minimal_css():
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
/* prevent browser scroll anchoring */
*{ overflow-anchor: none !important; }
</style>
""", unsafe_allow_html=True)


def _force_scroll_top():
    # 핵심: 타이머 rerun 때마다 스크롤이 아래로 밀리는 걸 강제로 0으로 되돌림
    components.html(
        """
<script>
(function(){
  try{
    // main container
    const main = parent.document.querySelector('div[data-testid="stAppViewContainer"] > section > main');
    if(main){ main.scrollTop = 0; }
    // window
    parent.window.scrollTo(0,0);
    // 일부 브라우저에서 body/html도 같이
    parent.document.documentElement.scrollTop = 0;
    parent.document.body.scrollTop = 0;
  }catch(e){}
})();
</script>
        """,
        height=0,
        width=0,
    )


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
            page_title="SnapQ P7 Reading Arena (SCROLL LOCK)",
            page_icon="🔥",
            layout="wide",
            initial_sidebar_state="collapsed",
        )
    except Exception:
        pass

    # fixed badge (no layout impact)
    st.markdown(
        '<div style="position:fixed;top:6px;right:10px;z-index:1000000;'
        'padding:4px 10px;border-radius:999px;font-size:12px;font-weight:900;'
        'background:rgba(34,211,238,0.18);border:1px solid rgba(34,211,238,0.35);'
        'color:#ffffff;backdrop-filter: blur(10px);">SCROLL LOCK</div>',
        unsafe_allow_html=True,
    )

    _inject_minimal_css()
    _force_scroll_top()

    m = _import_arena_module()

    # ensure our minimal css stays last
    old_inject = getattr(m, "inject_css", None)

    def patched_inject_css():
        try:
            if callable(old_inject):
                old_inject()
        except Exception:
            pass
        _inject_minimal_css()
        _force_scroll_top()

    try:
        m.inject_css = patched_inject_css  # type: ignore
    except Exception:
        pass

    if hasattr(m, "run") and callable(getattr(m, "run")):
        m.run()
    else:
        m.reading_arena_page()

    # last wins
    _inject_minimal_css()
    _force_scroll_top()


main()
