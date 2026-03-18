import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

MARK = "P7_SAFE_UI_PACK_V1"
if MARK in src:
    print("[SKIP] UI PACK already present")
    raise SystemExit(0)

m = re.search(r"^def\s+inject_css\s*\(\s*\)\s*:\s*\n", src, flags=re.M)
if not m:
    raise SystemExit("inject_css() not found")

# find inject_css end (next top-level def)
m2 = re.search(r"^\s*def\s+\w+\s*\(", src[m.end():], flags=re.M)
end = (m.end() + m2.start()) if m2 else len(src)
body = src[m.start():end]

# Append near the end of inject_css body (still inside function)
ADD = r'''
    # ---- P7 SAFE UI PACK V1 ----
    st.markdown(
        r"""
        <style>
        /* ''' + MARK + r''' */

        /* (1) 선택지 글자: 흰 버튼이면 검정 글자 */
        .p7-opt-wrap div[data-testid="stButton"] > button,
        .p7-opt-wrap div[data-testid="stButton"] > button *{
          color: #111827 !important;
        }
        /* hover 시에는 흰 글자(락온) */
        .p7-opt-wrap div[data-testid="stButton"] > button:hover,
        .p7-opt-wrap div[data-testid="stButton"] > button:hover *{
          color:#ffffff !important;
        }

        /* (2) 글자 크기 1.2배 */
        .p7-zone .p7-zone-body{ font-size: 22px !important; }
        .p7-zone.mission .p7-zone-body{ font-size: 23px !important; }
        .p7-opt-wrap div[data-testid="stButton"] > button{
          font-size: 21px !important;
          font-weight: 950 !important;
        }
        @media (max-width: 640px){
          .p7-zone .p7-zone-body{ font-size: 20px !important; }
          .p7-zone.mission .p7-zone-body{ font-size: 20px !important; }
          .p7-opt-wrap div[data-testid="stButton"] > button{ font-size: 20px !important; }
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
'''

# Only add once, right before function end
body2 = body.rstrip() + "\n\n" + ADD + "\n"
patched = src[:m.start()] + body2 + src[end:]
open(path, "w", encoding="utf-8").write(patched)
print("[OK] SAFE UI PACK injected inside inject_css()")

