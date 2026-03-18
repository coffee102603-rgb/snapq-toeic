import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

# -------------------------
# A) inject_css(): add readability CSS (idempotent)
# -------------------------
UI_MARK = "P7_UI_READABLE_V1"
if UI_MARK not in src:
    m = re.search(r"^def\s+inject_css\s*\(\s*\)\s*:\s*\n", src, flags=re.M)
    if not m:
        raise SystemExit("inject_css() not found")
    m2 = re.search(r"^\s*def\s+\w+\s*\(", src[m.end():], flags=re.M)
    inj_end = (m.end() + m2.start()) if m2 else len(src)
    body = src[m.start():inj_end]

    add = r'''
    # ---- P7_UI_READABLE_V1 ----
    st.markdown(
        r"""
        <style>
        /* P7_UI_READABLE_V1 */

        /* 선택지: 흰 버튼이면 글자 검정 + 1.2배 */
        .p7-opt-wrap div[data-testid="stButton"] > button,
        .p7-opt-wrap div[data-testid="stButton"] > button *{
          color:#0B1020 !important;
          text-shadow:none !important;
        }
        .p7-opt-wrap div[data-testid="stButton"] > button{
          font-size:22px !important;
          font-weight:950 !important;
        }
        .p7-opt-wrap div[data-testid="stButton"] > button:hover,
        .p7-opt-wrap div[data-testid="stButton"] > button:hover *{
          color:#ffffff !important;
        }

        /* 지문/문제 글자도 1.2배 */
        .p7-zone .p7-zone-body{ font-size:22px !important; }
        .p7-zone.mission .p7-zone-body{ font-size:23px !important; }

        /* 게이지 애니메이션 CSS */
        @keyframes p7_gauge_wiggle{
          0%{transform:translateX(0)}25%{transform:translateX(-2px)}50%{transform:translateX(0)}75%{transform:translateX(2px)}100%{transform:translateX(0)}
        }
        @keyframes p7_gauge_shake{
          0%{transform:translateX(0)}20%{transform:translateX(-4px)}40%{transform:translateX(4px)}60%{transform:translateX(-3px)}80%{transform:translateX(3px)}100%{transform:translateX(0)}
        }
        @keyframes p7_gauge_flash{
          0%{filter:brightness(1.0)}50%{filter:brightness(1.55)}100%{filter:brightness(1.0)}
        }

        /* stage 색상 */
        .p7-hud-gauge.stage5 .fill{ background: linear-gradient(90deg, rgba(34,211,238,.95), rgba(124,58,237,.95)) !important; }
        .p7-hud-gauge.stage4 .fill{ background: linear-gradient(90deg, rgba(56,189,248,.95), rgba(167,139,250,.95)) !important; }
        .p7-hud-gauge.stage3 .fill{ background: linear-gradient(90deg, rgba(45,212,191,.95), rgba(34,211,238,.95)) !important; }
        .p7-hud-gauge.stage2 .fill{ background: linear-gradient(90deg, rgba(250,204,21,.95), rgba(34,211,238,.95)) !important; }
        .p7-hud-gauge.stage1 .fill{ background: linear-gradient(90deg, rgba(251,146,60,.95), rgba(250,204,21,.95)) !important; }
        .p7-hud-gauge.stage0 .fill{ background: linear-gradient(90deg, rgba(239,68,68,.98), rgba(220,38,38,.98)) !important; }

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
    print("[OK] readability CSS injected")

# -------------------------
# B) render_top_hud(): replace ONLY the gauge rendering block safely
# -------------------------
m = re.search(r"^def\s+render_top_hud\s*\(\s*\)\s*:\s*\n", src, flags=re.M)
if not m:
    open(path, "w", encoding="utf-8").write(src)
    raise SystemExit("render_top_hud() not found")

m2 = re.search(r"^\s*def\s+\w+\s*\(", src[m.end():], flags=re.M)
end = (m.end() + m2.start()) if m2 else len(src)
body = src[m.start():end]

GAUGE_MARK = "P7_GAUGE_BLOCK_V1"
if GAUGE_MARK not in body:
    # find the st.markdown block that renders <div class="p7-hud-gauge"> ... </div>
    # Replace that whole call with our safe computed gauge_cls block.
    pat = re.compile(r"(?P<indent>^\s*)st\.markdown\(\s*f?\"\"\"[\s\S]*?<div class=\"p7-hud-gauge\">[\s\S]*?\"\"\"\s*,\s*unsafe_allow_html\s*=\s*True\s*,?\s*\)\s*", re.M)
    mm = pat.search(body)
    if not mm:
        # If current gauge is already in another form, do nothing (safe)
        print("[WARN] gauge block not found to replace - skipping gauge patch")
    else:
        indent = mm.group("indent")
        replace = (
            indent + f"# ---- {GAUGE_MARK} ----\n" +
            indent + "pct = 0.0 if total <= 0 else max(0.0, min(1.0, remaining / total))\n" +
            indent + "w = int(pct * 100)\n" +
            indent + "stage = int(remaining // 30)\n" +
            indent + "gauge_cls = f\"p7-hud-gauge stage{stage}\"\n" +
            indent + "if remaining <= 60:\n" +
            indent + "    gauge_cls += \" last60\"\n" +
            indent + "if remaining <= 30:\n" +
            indent + "    gauge_cls += \" last30\"\n" +
            indent + "if remaining <= 10:\n" +
            indent + "    gauge_cls += \" final\"\n" +
            indent + "st.markdown(\n" +
            indent + "    f\"\"\"\n" +
            indent + "    <div class=\\\"{gauge_cls}\\\">\n" +
            indent + "      <div class=\\\"fill\\\" style=\\\"width:{w}%\\\"></div>\n" +
            indent + "    </div>\n" +
            indent + "    \"\"\",\n" +
            indent + "    unsafe_allow_html=True,\n" +
            indent + ")\n"
        )
        body = body[:mm.start()] + replace + body[mm.end():]
        print("[OK] gauge block replaced safely")

src = src[:m.start()] + body + src[end:]
open(path, "w", encoding="utf-8").write(src)
print("[DONE] SAFE UI+GAUGE patch applied")

