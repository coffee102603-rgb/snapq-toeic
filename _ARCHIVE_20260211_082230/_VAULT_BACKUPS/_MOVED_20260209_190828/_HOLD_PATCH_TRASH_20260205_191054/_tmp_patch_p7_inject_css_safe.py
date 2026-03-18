import re, sys

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

m = re.search(r"^def\s+inject_css\s*\(\s*\)\s*:\s*\n", src, flags=re.M)
if not m:
    raise SystemExit("inject_css() not found")

start = m.start()
# find next top-level def after inject_css
m2 = re.search(r"^\s*def\s+\w+\s*\(", src[m.end():], flags=re.M)
end = (m.end() + m2.start()) if m2 else len(src)

SAFE_FUNC = r'''def inject_css():
    """
    ✅ P7 CSS STABILIZER (SAFE)
    - CRITICAL CSS: 매 rerun마다 주입 (1초 후 붕괴/흰 화면 방지)
    - Streamlit 상단 여백 최소화 (P7 전장 공간 확보)
    """
    # ---- CRITICAL CSS (ALWAYS) ----
    st.markdown(
        """
        <style>
        /* ===== P7 CRIT (ALWAYS) ===== */
        /* Streamlit 기본 상단/하단 여백 최소화 */
        .block-container { padding-top: 0.6rem !important; padding-bottom: 1.0rem !important; }
        header[data-testid="stHeader"] { display: none !important; }
        footer { display: none !important; }

        /* HUD 관련 최소 스타일(깨짐 방지) */
        .p7-hudbar { margin: 0 0 6px 0 !important; padding: 6px 10px !important; border-radius: 14px !important; }
        .p7-hud-left { display: flex !important; gap: 10px !important; align-items: center !important; flex-wrap: wrap !important; }
        .p7-hud-right { display: flex !important; justify-content: flex-end !important; align-items: center !important; }
        .p7-hud-gauge { height: 10px !important; border-radius: 999px !important; overflow: hidden !important; margin: 6px 0 10px 0 !important; }
        .p7-hud-gauge .fill { height: 100% !important; }

        /* 보기(버튼) 터치감 개선(기본 유지) */
        div[data-testid="stButton"] > button { border-radius: 12px !important; }

        </style>
        """,
        unsafe_allow_html=True,
    )

    # ---- NOTE ----
    # 여기서는 '항상 주입되는 최소 CSS'만 둡니다.
    # 기존의 거대한 테마 CSS는 다른 함수/블록에서 이미 처리되어도 되고,
    # 없더라도 최소한 UI가 "1초 후 붕괴"하지 않게 하는 것이 목적입니다.
'''

patched = src[:start] + SAFE_FUNC + src[end:]
open(path, "w", encoding="utf-8").write(patched)
print("[OK] inject_css() replaced with SAFE stabilizer")

