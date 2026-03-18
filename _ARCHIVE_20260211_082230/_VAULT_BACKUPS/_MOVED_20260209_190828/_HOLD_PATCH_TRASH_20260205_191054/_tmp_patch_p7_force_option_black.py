import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

MARK="P7_FORCE_OPTION_BLACK_V1"
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
    # ---- P7 FORCE OPTION BLACK V1 ----
    st.markdown(
        r"""
        <style>
        /* ''' + MARK + r''' */

        /* ✅ 버튼 자체 */
        .p7-opt-wrap div[data-testid="stButton"] > button{
          color:#0B1020 !important;
          font-size:22px !important;
          font-weight:950 !important;
          text-shadow:none !important;
        }

        /* ✅ 버튼 안에 어떤 태그가 들어가도 전부 검정 */
        .p7-opt-wrap div[data-testid="stButton"] > button span,
        .p7-opt-wrap div[data-testid="stButton"] > button p,
        .p7-opt-wrap div[data-testid="stButton"] > button div,
        .p7-opt-wrap div[data-testid="stButton"] > button *{
          color:#0B1020 !important;
          text-shadow:none !important;
        }

        /* hover(락온)에서는 흰 글자 유지 */
        .p7-opt-wrap div[data-testid="stButton"] > button:hover{
          color:#ffffff !important;
        }
        .p7-opt-wrap div[data-testid="stButton"] > button:hover *{
          color:#ffffff !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
'''

body2 = body.rstrip() + "\n\n" + ADD + "\n"
src2 = src[:m.start()] + body2 + src[inj_end:]
open(path, "w", encoding="utf-8").write(src2)
print("[OK] injected FORCE OPTION BLACK CSS")

