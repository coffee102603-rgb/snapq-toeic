import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

MARK="P7_PLAN_A_OPTION_TEXT_V1"
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
    # ---- P7 PLAN A OPTION TEXT V1 ----
    st.markdown(
        r"""
        <style>
        /* ''' + MARK + r''' */

        /* 우리가 커스텀 텍스트를 그릴 버튼 */
        .p7-opt-wrap div[data-testid="stButton"] > button{
          position: relative !important;
          min-height: 78px !important;
          padding: 18px 18px !important;
          border-radius: 18px !important;
          background: rgba(255,255,255,0.96) !important;
          border: 1px solid rgba(255,255,255,0.22) !important;
          box-shadow: 0 14px 34px rgba(0,0,0,0.22) !important;
          overflow: hidden !important;
        }

        /* ✅ 기본 Streamlit 텍스트는 "완전 숨김" */
        .p7-opt-wrap div[data-testid="stButton"] > button p,
        .p7-opt-wrap div[data-testid="stButton"] > button span,
        .p7-opt-wrap div[data-testid="stButton"] > button div{
          opacity: 0 !important;
        }

        /* ✅ 우리가 원하는 텍스트를 aria-label에서 꺼내서 그린다 */
        .p7-opt-wrap div[data-testid="stButton"] > button::after{
          content: attr(aria-label);
          position: absolute;
          left: 18px;
          right: 18px;
          top: 50%;
          transform: translateY(-50%);
          color: #0B1020 !important;
          font-size: 22px !important;    /* 1.2배 */
          font-weight: 950 !important;
          line-height: 1.15 !important;
          text-align: center;
          white-space: normal;
          word-break: break-word;
          pointer-events: none; /* 클릭은 버튼이 받음 */
          opacity: 1 !important;
        }

        /* hover: 락온(게임 느낌) */
        .p7-opt-wrap div[data-testid="stButton"] > button:hover{
          transform: translateY(-2px);
          filter: brightness(1.04) saturate(1.06);
          background: linear-gradient(135deg, rgba(34,211,238,0.95), rgba(167,139,250,0.90)) !important;
        }
        .p7-opt-wrap div[data-testid="stButton"] > button:hover::after{
          color:#ffffff !important;
        }

        /* press */
        .p7-opt-wrap div[data-testid="stButton"] > button:active{
          transform: translateY(1px) scale(0.995);
          box-shadow: 0 10px 22px rgba(0,0,0,0.18) !important;
        }

        /* 모바일 */
        @media (max-width: 640px){
          .p7-opt-wrap div[data-testid="stButton"] > button{
            min-height: 92px !important;
            padding: 18px 14px !important;
          }
          .p7-opt-wrap div[data-testid="stButton"] > button::after{
            font-size: 20px !important;
            left: 14px;
            right: 14px;
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
print("[OK] PLAN A option text overlay injected")

