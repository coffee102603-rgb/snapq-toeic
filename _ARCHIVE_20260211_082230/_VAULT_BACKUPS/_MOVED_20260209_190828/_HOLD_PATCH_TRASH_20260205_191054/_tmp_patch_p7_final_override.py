import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src  = open(path, "r", encoding="utf-8").read()

# ------------------------------------------------------------
# A) inject_css(): insert FINAL CSS right before the LAST </style>
# (so it always wins no matter how many CSS blocks exist)
# ------------------------------------------------------------
CSS_MARK = "P7_FINAL_OVERRIDE_V9"
if CSS_MARK not in src:
    # Find the inject_css st.markdown style block ending
    # We insert JUST BEFORE the last '</style>"""' inside inject_css.
    # Safer: insert before the first occurrence of '</style>""",' AFTER def inject_css()
    inj_pos = src.find("def inject_css()")
    if inj_pos < 0:
        raise SystemExit("inject_css() not found")

    # limit search region to inject_css block (until next 'def ')
    m2 = re.search(r"^\s*def\s+\w+\s*\(", src[inj_pos+1:], flags=re.M)
    inj_end = inj_pos + (m2.start() if m2 else len(src))

    inj_block = src[inj_pos:inj_end]
    end_tag = inj_block.rfind("</style>")
    if end_tag < 0:
        raise SystemExit("inject_css() style </style> not found")

    FINAL_CSS = f"""

/* =========================
   {CSS_MARK}  (LAST WINS)
   ========================= */

/* (3) TOP SPACE: 더 위로 당김 (두번째 캡쳐 해결) */
section.main > div.block-container,
main .block-container {{
  padding-top: 0.05rem !important;
  margin-top: 0 !important;
}}
.p7-hudbar {{ margin-bottom: 2px !important; }}
.p7-hud-gauge {{ margin: 0 auto 6px auto !important; }}

/* (1) OPTIONS: 1.1배 + 검정 + 더 굵게 (첫번째 캡쳐 기준) */
.p7-opt-wrap div[data-testid="stButton"] > button,
.p7-opt-wrap div[data-testid="stButton"] > button * {{
  color: #0B1020 !important;
  opacity: 1 !important;
  text-shadow: none !important;
  font-weight: 950 !important;
}}
.p7-opt-wrap div[data-testid="stButton"] > button {{
  font-size: 1.10rem !important;   /* 1.1배 */
  background: rgba(255,255,255,0.98) !important;
  border: 1px solid rgba(0,0,0,0.10) !important;
}}

/* (2) GAUGE: 30초 stage 색상 (stage0~5) */
.p7-hud-gauge.stage5 .fill {{ background: linear-gradient(90deg, rgba(34,211,238,.95), rgba(124,58,237,.95)) !important; }}
.p7-hud-gauge.stage4 .fill {{ background: linear-gradient(90deg, rgba(56,189,248,.95), rgba(167,139,250,.95)) !important; }}
.p7-hud-gauge.stage3 .fill {{ background: linear-gradient(90deg, rgba(45,212,191,.95), rgba(34,211,238,.95)) !important; }}
.p7-hud-gauge.stage2 .fill {{ background: linear-gradient(90deg, rgba(250,204,21,.95), rgba(34,211,238,.95)) !important; }}
.p7-hud-gauge.stage1 .fill {{ background: linear-gradient(90deg, rgba(251,146,60,.95), rgba(250,204,21,.95)) !important; }}
.p7-hud-gauge.stage0 .fill {{ background: linear-gradient(90deg, rgba(239,68,68,.98), rgba(220,38,38,.98)) !important; }}

"""

    inj_block2 = inj_block[:end_tag] + FINAL_CSS + inj_block[end_tag:]
    src = src[:inj_pos] + inj_block2 + src[inj_end:]
    print("[OK] FINAL CSS injected (last-wins)")

# ------------------------------------------------------------
# B) render_top_hud(): add stage class to gauge_cls (minimal code)
#    We DO NOT rewrite blocks; we just add 2 lines after gauge_cls definition.
# ------------------------------------------------------------
HUD_MARK = "P7_GAUGE_STAGE_CODE_V1"
if HUD_MARK not in src:
    m = re.search(r"^def\s+render_top_hud\s*\(\s*\)\s*:\s*\n", src, flags=re.M)
    if m:
        # find render_top_hud block end
        m2 = re.search(r"^\s*def\s+\w+\s*\(", src[m.end():], flags=re.M)
        end = (m.end() + m2.start()) if m2 else len(src)
        body = src[m.start():end]

        # locate gauge_cls assignment inside function
        # common pattern: gauge_cls = "p7-hud-gauge" (and maybe warn/danger)
        lines = body.splitlines(True)
        for i,ln in enumerate(lines):
            if 'gauge_cls' in ln and 'p7-hud-gauge' in ln and '=' in ln:
                indent = re.match(r"^\s*", ln).group(0)
                insert = (
                    f"{indent}# ---- {HUD_MARK} ----\n"
                    f"{indent}stage = int(remaining // 30)\n"
                    f"{indent}gauge_cls += f\" stage{stage}\"\n"
                )
                # only insert once
                lines.insert(i+1, insert)
                body2 = "\n".join([l.rstrip("\n") for l in lines]) + "\n"
                src = src[:m.start()] + body2 + src[end:]
                print("[OK] stage class code injected into render_top_hud()")
                break

# write
open(path, "w", encoding="utf-8").write(src)
print("[DONE] final override patch applied")

