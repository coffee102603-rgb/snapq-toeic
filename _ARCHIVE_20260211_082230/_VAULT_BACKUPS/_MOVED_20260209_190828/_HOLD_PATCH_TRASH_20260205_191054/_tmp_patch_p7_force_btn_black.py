import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

MARK = "P7_FORCE_BTN_BLACK_V1"
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
    # ---- P7 FORCE BTN BLACK V1 ----
    st.markdown(
        r"""
        <style>
        /* ''' + MARK + r''' */

        /*
          ✅ 핵심: Streamlit 테마가 p/span에 !important로 흰색을 줘도
          우리가 더 넓은 범위 + 더 강한 셀렉터로 '검정'을 다시 박는다.
          (P7 전장 전체 버튼 텍스트를 강제 가독성 모드로)
        */
        .stApp div[data-testid="stButton"] > button,
        .stApp div[data-testid="stButton"] > button *{
          color:#0B1020 !important;
          opacity:1 !important;
          text-shadow:none !important;
        }

        /* 선택지는 1.2배 크게(버튼 전체) */
        .stApp div[data-testid="stButton"] > button{
          font-size:22px !important;
          font-weight:950 !important;
        }

        /* 단, hover(락온) 효과는 흰 글자 유지 (게임 느낌) */
        .stApp div[data-testid="stButton"] > button:hover,
        .stApp div[data-testid="stButton"] > button:hover *{
          color:#ffffff !important;
        }

        /* 모바일 */
        @media (max-width: 640px){
          .stApp div[data-testid="stButton"] > button{
            font-size:20px !important;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
'''

body2 = body.rstrip() + "\n\n" + ADD + "\n"
src2 = src[:m.start()] + body2 + src[inj_end:]
open(path, "w", encoding="utf-8").write(src2)
print("[OK] injected FORCE BTN BLACK CSS")

