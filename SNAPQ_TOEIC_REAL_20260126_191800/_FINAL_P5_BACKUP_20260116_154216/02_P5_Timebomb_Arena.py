# pages/02_P5_Timebomb_Arena.py
# ============================================================
# ✅ P5 "입구(Wrapper)" ONLY
# - pages는 전장 로직/스타일을 절대 소유하지 않는다.
# - 전장(HUD/타이머/콤보/문항/진행)은 app/arenas/p5_timebomb_arena.py가 담당한다.
# - 이 파일은 '안전한 호출'만 한다. (짧을수록 안전)
# ============================================================

import streamlit as st
from app.arenas import p5_timebomb_arena


def run() -> None:
    # ✅ 레이아웃만 지정 (HUD 컬럼이 잘리면 안 되므로 wide)
    st.set_page_config(
        page_title="💣 P5 Timebomb Arena · SnapQ TOEIC",
        page_icon="💣",
        layout="wide",
    )

    # ✅ 전장 본체 실행 (여기서만 호출)
    p5_timebomb_arena.run()


if __name__ == "__main__":
    run()
