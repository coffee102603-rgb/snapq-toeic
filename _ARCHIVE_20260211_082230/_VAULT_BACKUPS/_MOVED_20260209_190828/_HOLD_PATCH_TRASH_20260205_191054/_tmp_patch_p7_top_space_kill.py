import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

MARK = "P7_TOP_SPACE_KILL_V1"
if MARK in src:
    print("[SKIP] already applied")
    raise SystemExit(0)

m = re.search(r"^def\s+inject_css\s*\(\s*\)\s*:\s*\n", src, flags=re.M)
if not m:
    raise SystemExit("inject_css() not found")

m2 = re.search(r"^\s*def\s+\w+\s*\(", src[m.end():], flags=re.M)
inj_end = (m.end() + m2.start()) if m2 else len(src)
body = src[m.start():inj_end]

ADD = r'''
    # ---- P7 TOP SPACE KILL V1 (CSS ONLY) ----
    st.markdown(
        r"""
        <style>
        /* ''' + MARK + r''' */

        /* Streamlit 상단 빈공간 제거 (헤더/툴바 영향 최소화) */
        header[data-testid="stHeader"] { display: none !important; }
        footer { display: none !important; }

        /* 메인 컨테이너 패딩 최소 */
        .block-container{
          padding-top: 0rem !important;
          padding-bottom: 0.7rem !important;
        }

        /* 첫 블록(세로 블록) 위쪽 마진 제거 */
        .block-container > div:first-child{
          margin-top: 0rem !important;
          padding-top: 0rem !important;
        }

        /* HUD 줄을 위로 당김 (과하지 않게 -8px) */
        .p7-hud-left{
          margin-top: -8px !important;
        }

        /* 게이지도 위로 살짝 당김 */
        .p7-hud-gauge{
          margin-top: -8px !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
'''

body2 = body.rstrip() + "\n\n" + ADD + "\n"
src2 = src[:m.start()] + body2 + src[inj_end:]
open(path, "w", encoding="utf-8").write(src2)
print("[OK] TOP SPACE KILL CSS injected")

