import re
path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

MARK="P7_FINAL_UI_FORCE_V1"
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
    # ---- P7_FINAL_UI_FORCE_V1 ----
    st.markdown(
        r"""
        <style>
        /* === ''' + MARK + r''' === */

        /* 1️⃣ 상단 빈 공간 제거 */
        header[data-testid="stHeader"]{ display:none !important; }
        .block-container{
          padding-top:0.2rem !important;
          margin-top:0 !important;
        }
        div[data-testid="stVerticalBlock"]{
          margin-top:0 !important;
          padding-top:0 !important;
        }

        /* HUD / 게이지 위로 당김 */
        .p7-hud-left{ margin-top:-16px !important; }
        .p7-hud-gauge{ margin-top:-14px !important; margin-bottom:10px !important; }

        /* 2️⃣ 선택지 글자: 1.1배 + 검정 + 진하게 */
        .p7-opt-wrap div[data-testid="stButton"] > button{
          font-size:1.1em !important;
          font-weight:900 !important;
          color:#000000 !important;
        }
        .p7-opt-wrap div[data-testid="stButton"] > button *{
          color:#000000 !important;
        }

        /* 3️⃣ 타이머 게이지 30초 단계 색 */
        .p7-hud-gauge.stage3 .fill{ background:#22d3ee !important; } /* 90~60 */
        .p7-hud-gauge.stage2 .fill{ background:#38bdf8 !important; } /* 60~30 */
        .p7-hud-gauge.stage1 .fill{ background:#facc15 !important; } /* 30~10 */
        .p7-hud-gauge.stage0 .fill{ background:#ef4444 !important; } /* last */

        </style>
        """,
        unsafe_allow_html=True,
    )
'''
body2 = body.rstrip() + "\n\n" + ADD + "\n"
src2 = src[:m.start()] + body2 + src[inj_end:]
open(path, "w", encoding="utf-8").write(src2)
print("[OK] FINAL UI CSS applied")

