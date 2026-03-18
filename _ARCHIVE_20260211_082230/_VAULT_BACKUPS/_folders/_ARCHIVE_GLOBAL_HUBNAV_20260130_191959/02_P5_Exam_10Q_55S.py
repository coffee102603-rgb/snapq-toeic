# pages/02_P5_Exam_10Q_55S.py
# ============================================================
# SNAPQ TOEIC - P5 EXAM 10Q · 44s (Page wrapper)
# - Calls arena.render()
# ============================================================

import streamlit as st
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
