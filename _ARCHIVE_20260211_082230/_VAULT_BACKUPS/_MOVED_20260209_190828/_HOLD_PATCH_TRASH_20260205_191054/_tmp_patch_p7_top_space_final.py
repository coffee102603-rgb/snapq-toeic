import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

MARK = "P7_TOP_SPACE_FINAL_V1"
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
    # ---- P7 TOP SPACE FINAL V1 (MAX SAVE) ----
    st.markdown(
        r"""
        <style>
        /* ''' + MARK + r''' */

        /* ✅ 최대한 위로 당김 (HUD+게이지) */
        .p7-hud-left{ margin-top:-22px !important; }
        .p7-hud-gauge{ margin-top:-22px !important; margin-bottom:8px !important; }

        /* 혹시 다른 래퍼가 있으면 같이 당김 */
        div[data-testid="stHorizontalBlock"]{ margin-top:0 !important; }
        div[data-testid="stVerticalBlock"]{ margin-top:0 !important; padding-top:0 !important; }

        </style>
        """,
        unsafe_allow_html=True,
    )
'''

body2 = body.rstrip() + "\n\n" + ADD + "\n"
src2 = src[:m.start()] + body2 + src[inj_end:]
open(path, "w", encoding="utf-8").write(src2)
print("[OK] TOP SPACE FINAL (-22px) CSS injected")

