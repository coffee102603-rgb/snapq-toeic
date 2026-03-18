import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

MARK="P7_UI_TUNE_V1"
if MARK in src:
    print("[SKIP] UI TUNE already present")
    raise SystemExit(0)

m = re.search(r"^def\s+inject_css\s*\(\s*\)\s*:\s*\n", src, flags=re.M)
if not m:
    raise SystemExit("inject_css() not found")

m2 = re.search(r"^\s*def\s+\w+\s*\(", src[m.end():], flags=re.M)
inj_end = (m.end() + m2.start()) if m2 else len(src)
body = src[m.start():inj_end]

ADD = r'''
    # ---- P7_UI_TUNE_V1 (CSS ONLY) ----
    st.markdown(
        r"""
        <style>
        /* P7_UI_TUNE_V1 */

        /* (3) 상단 공간 더 위로: 전장 HUD/게이지를 위로 당김 */
        .block-container{ padding-top: 0.10rem !important; padding-bottom: 0.85rem !important; }
        /* HUD/게이지 마진을 조금 줄여 본문이 위로 올라오게 */
        .p7-hud-left{ margin-top: -6px !important; }
        .p7-hud-gauge{ margin-top: -4px !important; margin-bottom: 8px !important; }

        /* (1) 선택지: 더 크고(1.1배) 더 진하게, 검정으로, 흐림 제거 */
        /* 버튼 자체 + 내부 모든 텍스트를 강제 */
        .p7-opt-wrap div[data-testid="stButton"] > button{
          font-size: 22px !important;         /* 기존 20~21에서 +1.1배 느낌 */
          font-weight: 1000 !important;
          color:#0B1020 !important;
          opacity: 1 !important;
          text-shadow:none !important;
        }
        .p7-opt-wrap div[data-testid="stButton"] > button *{
          font-size: 22px !important;
          font-weight: 1000 !important;
          color:#0B1020 !important;
          opacity: 1 !important;
          text-shadow:none !important;
        }

        /* hover(락온) 시에는 흰 글자 유지(게임 느낌) */
        .p7-opt-wrap div[data-testid="stButton"] > button:hover,
        .p7-opt-wrap div[data-testid="stButton"] > button:hover *{
          color:#ffffff !important;
        }

        /* 모바일은 약간만 다운 */
        @media (max-width: 640px){
          .p7-opt-wrap div[data-testid="stButton"] > button,
          .p7-opt-wrap div[data-testid="stButton"] > button *{
            font-size: 20px !important;
          }
        }

        /* (2) 게이지 30초마다 색 변화가 “눈에 띄게”:
           fill 뿐 아니라 border/글로우도 stage별로 강하게 */
        .p7-hud-gauge{ border-width: 1px !important; }

        .p7-hud-gauge.stage5{ border-color: rgba(34,211,238,0.35) !important; box-shadow: 0 0 18px rgba(34,211,238,0.12) !important; }
        .p7-hud-gauge.stage4{ border-color: rgba(56,189,248,0.35) !important; box-shadow: 0 0 18px rgba(56,189,248,0.12) !important; }
        .p7-hud-gauge.stage3{ border-color: rgba(45,212,191,0.35) !important; box-shadow: 0 0 18px rgba(45,212,191,0.12) !important; }
        .p7-hud-gauge.stage2{ border-color: rgba(250,204,21,0.40) !important; box-shadow: 0 0 18px rgba(250,204,21,0.14) !important; }
        .p7-hud-gauge.stage1{ border-color: rgba(251,146,60,0.45) !important; box-shadow: 0 0 22px rgba(251,146,60,0.16) !important; }
        .p7-hud-gauge.stage0{ border-color: rgba(239,68,68,0.55) !important; box-shadow: 0 0 26px rgba(239,68,68,0.20) !important; }

        /* last60/last30/final은 이미 흔들림이 동작하니 그대로 두고,
           “색 변화가 더 티나게”만 강화함 */

        </style>
        """,
        unsafe_allow_html=True,
    )
'''

body2 = body.rstrip() + "\n\n" + ADD + "\n"
src2 = src[:m.start()] + body2 + src[inj_end:]
open(path, "w", encoding="utf-8").write(src2)
print("[OK] UI TUNE V1 injected (CSS ONLY)")

