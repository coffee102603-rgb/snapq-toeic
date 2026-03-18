import streamlit as st
from app.arenas import p7_reading_arena

def run():
    if hasattr(p7_reading_arena, "run") and callable(getattr(p7_reading_arena, "run")):
        return p7_reading_arena.run()
    if hasattr(p7_reading_arena, "reading_arena_page") and callable(getattr(p7_reading_arena, "reading_arena_page")):
        return p7_reading_arena.reading_arena_page()
    st.error("P7 엔진 엔트리(run/reading_arena_page)를 찾지 못했습니다. app/arenas/p7_reading_arena.py를 확인해주세요.")
    st.stop()

if __name__ == "__main__":
    run()