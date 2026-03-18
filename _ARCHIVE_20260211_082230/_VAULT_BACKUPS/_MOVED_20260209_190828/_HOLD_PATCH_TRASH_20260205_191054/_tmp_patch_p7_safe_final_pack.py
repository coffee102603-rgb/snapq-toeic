import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

# ------------------------------------------------------------
# A) inject_css(): add CSS (idempotent)
# ------------------------------------------------------------
CSS_MARK = "P7_SAFE_FINAL_PACK_V1"
if CSS_MARK not in src:
    m = re.search(r"^def\s+inject_css\s*\(\s*\)\s*:\s*\n", src, flags=re.M)
    if not m:
        raise SystemExit("inject_css() not found")

    m2 = re.search(r"^\s*def\s+\w+\s*\(", src[m.end():], flags=re.M)
    inj_end = (m.end() + m2.start()) if m2 else len(src)
    body = src[m.start():inj_end]

    add = r'''
    # ---- P7_SAFE_FINAL_PACK_V1 ----
    st.markdown(
        r"""
        <style>
        /* P7_SAFE_FINAL_PACK_V1 */

        /* (1) TOP SPACE: 두번째 캡쳐 상단 공간 압축 */
        header[data-testid="stHeader"]{ display:none !important; }
        footer{ display:none !important; }

        div[data-testid="stAppViewContainer"] > section > main,
        div[data-testid="stAppViewContainer"] > section > main > div,
        div[data-testid="stAppViewContainer"] > section > div{
          padding-top: 0rem !important;
          margin-top: 0rem !important;
        }
        .block-container{
          padding-top: 0.05rem !important;
          margin-top: 0 !important;
          padding-bottom: 0.8rem !important;
        }
        /* HUD+게이지를 더 위로 (과하지 않게) */
        .p7-hud-left{ margin-top:-18px !important; }
        .p7-hud-gauge{ margin-top:-16px !important; margin-bottom:10px !important; }

        /* (2) OPTIONS: 첫번째 캡쳐 기준 선택지 글자 1.1배 + 검정 + 더 진하게 + 흐림 제거 */
        .p7-opt-wrap div[data-testid="stButton"] > button{
          font-size: 22px !important;
          font-weight: 1000 !important;
          color:#000 !important;
          opacity:1 !important;
          text-shadow:none !important;
        }
        .p7-opt-wrap div[data-testid="stButton"] > button *{
          font-size: 22px !important;
          font-weight: 1000 !important;
          color:#000 !important;
          opacity:1 !important;
          text-shadow:none !important;
        }
        /* hover(락온)은 흰 글자 유지 */
        .p7-opt-wrap div[data-testid="stButton"] > button:hover,
        .p7-opt-wrap div[data-testid="stButton"] > button:hover *{
          color:#ffffff !important;
        }

        @media (max-width: 640px){
          .p7-opt-wrap div[data-testid="stButton"] > button,
          .p7-opt-wrap div[data-testid="stButton"] > button *{
            font-size: 20px !important;
          }
        }

        /* (3) GAUGE: 30초마다 색 변화 + last60/last30/final 흔들/빨강은 유지 */
        @keyframes p7_gauge_wiggle{
          0%{transform:translateX(0)}25%{transform:translateX(-2px)}50%{transform:translateX(0)}75%{transform:translateX(2px)}100%{transform:translateX(0)}
        }
        @keyframes p7_gauge_shake{
          0%{transform:translateX(0)}20%{transform:translateX(-4px)}40%{transform:translateX(4px)}60%{transform:translateX(-3px)}80%{transform:translateX(3px)}100%{transform:translateX(0)}
        }
        @keyframes p7_gauge_flash{
          0%{filter:brightness(1.0)}50%{filter:brightness(1.55)}100%{filter:brightness(1.0)}
        }

        /* stage5~0: 30초 단위 */
        .p7-hud-gauge.stage5 .fill{ background:linear-gradient(90deg, rgba(34,211,238,.95), rgba(124,58,237,.95)) !important; }
        .p7-hud-gauge.stage4 .fill{ background:linear-gradient(90deg, rgba(56,189,248,.95), rgba(167,139,250,.95)) !important; }
        .p7-hud-gauge.stage3 .fill{ background:linear-gradient(90deg, rgba(45,212,191,.95), rgba(34,211,238,.95)) !important; }
        .p7-hud-gauge.stage2 .fill{ background:linear-gradient(90deg, rgba(250,204,21,.95), rgba(34,211,238,.95)) !important; }
        .p7-hud-gauge.stage1 .fill{ background:linear-gradient(90deg, rgba(251,146,60,.95), rgba(250,204,21,.95)) !important; }
        .p7-hud-gauge.stage0 .fill{ background:linear-gradient(90deg, rgba(239,68,68,.98), rgba(220,38,38,.98)) !important; }

        .p7-hud-gauge.last60{ animation:p7_gauge_wiggle .9s linear infinite; }
        .p7-hud-gauge.last30{
          animation:p7_gauge_shake .35s linear infinite, p7_gauge_flash .55s ease-in-out infinite;
          border-color: rgba(239,68,68,.55) !important;
          box-shadow: 0 0 26px rgba(239,68,68,.18) !important;
        }
        .p7-hud-gauge.final{
          animation:p7_gauge_shake .24s linear infinite, p7_gauge_flash .35s ease-in-out infinite;
          box-shadow: 0 0 40px rgba(239,68,68,.25) !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
'''
    body2 = body.rstrip() + "\n\n" + add + "\n"
    src = src[:m.start()] + body2 + src[inj_end:]
    print("[OK] CSS added")

# ------------------------------------------------------------
# B) render_top_hud(): replace ONLY gauge_cls block safely
#   current code: gauge_cls="p7-hud-gauge" + warn/danger
#   -> stage based + last60/last30/final
# ------------------------------------------------------------
m = re.search(r"^def\s+render_top_hud\s*\(\s*\)\s*:\s*\n", src, flags=re.M)
if not m:
    open(path, "w", encoding="utf-8").write(src)
    raise SystemExit("render_top_hud() not found")

m2 = re.search(r"^\s*def\s+\w+\s*\(", src[m.end():], flags=re.M)
end = (m.end() + m2.start()) if m2 else len(src)
body = src[m.start():end]

if "stage = int(remaining // 30)" not in body:
    # find the gauge section starting with: gauge_cls = "p7-hud-gauge"
    # and ending at the st.markdown that prints the gauge div.
    pat = re.compile(
        r'(?P<indent>^\s*)gauge_cls\s*=\s*"p7-hud-gauge"[\s\S]*?^\s*st\.markdown\(\s*f"""[\s\S]*?<div class="\{gauge_cls\}">[\s\S]*?unsafe_allow_html\s*=\s*True[\s\S]*?\)\s*',
        re.M
    )
    mm = pat.search(body)
    if mm:
        indent = mm.group("indent")
        repl = (
            indent + "# ---- GAUGE_STAGE_V1 (30s) ----\n" +
            indent + "pct = 0.0 if total <= 0 else max(0.0, min(1.0, remaining / total))\n" +
            indent + "w = int(pct * 100)\n\n" +
            indent + "stage = int(remaining // 30)  # 0~5\n" +
            indent + "gauge_cls = f\"p7-hud-gauge stage{stage}\"\n" +
            indent + "if remaining <= 60:\n" +
            indent + "    gauge_cls += \" last60\"\n" +
            indent + "if remaining <= 30:\n" +
            indent + "    gauge_cls += \" last30\"\n" +
            indent + "if remaining <= 10:\n" +
            indent + "    gauge_cls += \" final\"\n\n" +
            indent + "st.markdown(\n" +
            indent + "    f\"\"\"\n" +
            indent + "    <div class=\\\"{gauge_cls}\\\">\n" +
            indent + "      <div class=\\\"fill\\\" style=\\\"width:{w}%\\\"></div>\n" +
            indent + "    </div>\n" +
            indent + "    \"\"\",\n" +
            indent + "    unsafe_allow_html=True,\n" +
            indent + ")\n"
        )
        body = body[:mm.start()] + repl + body[mm.end():]
        print("[OK] gauge stage block replaced")
    else:
        print("[WARN] gauge block pattern not found; skipped gauge replacement")

src = src[:m.start()] + body + src[end:]
open(path, "w", encoding="utf-8").write(src)
print("[DONE] Final pack applied")

