import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

MARK="P7_TOP_SPACE_KILL_V2"
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
    # ---- P7_TOP_SPACE_KILL_V2 (CSS ONLY) ----
    st.markdown(
        r"""
        <style>
        /* ''' + MARK + r''' */

        /* ✅ Streamlit 상단 여백/헤더/메인 패딩을 “강제 0” */
        header[data-testid="stHeader"]{ display:none !important; }
        footer{ display:none !important; }

        /* 최상위 컨테이너들에 강제 패딩 0 */
        div[data-testid="stAppViewContainer"] > section > div,
        div[data-testid="stAppViewContainer"] > section > main,
        div[data-testid="stAppViewContainer"] > section > main > div{
          padding-top: 0rem !important;
          margin-top: 0rem !important;
        }

        /* block-container (메인) */
        .block-container{
          padding-top: 0rem !important;
          padding-bottom: 0.7rem !important;
          margin-top: 0rem !important;
        }

        /* 첫 VerticalBlock/HorizontalBlock 위 마진 제거 */
        div[data-testid="stVerticalBlock"]{ margin-top:0 !important; padding-top:0 !important; }
        div[data-testid="stHorizontalBlock"]{ margin-top:0 !important; }

        /* HUD/게이지를 살짝 위로 당김 (최대 안전치) */
        .p7-hud-left{ margin-top:-12px !important; }
        .p7-hud-gauge{ margin-top:-10px !important; margin-bottom:8px !important; }

        </style>
        """,
        unsafe_allow_html=True,
    )
'''
body2 = body.rstrip() + "\n\n" + ADD + "\n"
src2 = src[:m.start()] + body2 + src[inj_end:]
open(path, "w", encoding="utf-8").write(src2)
print("[OK] TOP SPACE KILL V2 injected")

