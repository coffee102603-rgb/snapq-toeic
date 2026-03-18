# pages/02_P5_Exam_10Q_55S.py
# ============================================================
# SNAPQ TOEIC - P5 EXAM 10Q · 44s (Page wrapper)
# - Calls arena.render()
# ============================================================

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

from app.arenas import p5_exam_10q_55s


def main():
    st.set_page_config(
        page_title="SnapQ TOEIC | P5 EXAM 10Q · 44s",
        page_icon="🔥",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    p5_exam_10q_55s.render()


if __name__ == "__main__":
    main()