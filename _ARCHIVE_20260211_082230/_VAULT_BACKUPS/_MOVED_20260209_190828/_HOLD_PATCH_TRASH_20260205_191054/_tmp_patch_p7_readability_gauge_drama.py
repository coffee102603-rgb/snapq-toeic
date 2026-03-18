import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

# ---------------------------
# A) inject_css(): insert STRONG overrides right after CRIT block close
# ---------------------------
MARK = "P7_READABILITY_GAUGE_V1"
if MARK not in src:
    m = re.search(r"^def\s+inject_css\s*\(\s*\)\s*:\s*\n", src, flags=re.M)
    if not m:
        raise SystemExit("inject_css() not found")

    # locate first st.markdown(... unsafe_allow_html=True ...) close inside inject_css
    # (we insert right after it, still inside function)
    inj_start = m.start()
    m2 = re.search(r"^\s*def\s+\w+\s*\(", src[m.end():], flags=re.M)
    inj_end = (m.end() + m2.start()) if m2 else len(src)
    body = src[inj_start:inj_end]

    pos = body.find("unsafe_allow_html=True")
    close = body.find("\n    )", pos) if pos >= 0 else -1
    insert_at = (inj_start + close + len("\n    )")) if close >= 0 else (inj_start + m.end())

    ADD = r'''

    # ---- P7 READABILITY + GAUGE DRAMA (SAFE OVERRIDES) ----
    st.markdown(
        r"""
        <style>
        /* ''' + MARK + r''' */

        /* (1) 선택지: 흰 버튼이면 글자는 '진짜 검정' */
        .p7-opt-wrap div[data-testid="stButton"] > button,
        .p7-opt-wrap div[data-testid="stButton"] > button *{
          color:#0B1020 !important;
          text-shadow:none !important;
        }

        /* 선택지 글자 1.2배 */
        .p7-opt-wrap div[data-testid="stButton"] > button{
          font-size: 22px !important;
          font-weight: 950 !important;
        }

        /* hover(락온)에서는 흰 글자 유지 */
        .p7-opt-wrap div[data-testid="stButton"] > button:hover,
        .p7-opt-wrap div[data-testid="stButton"] > button:hover *{
          color:#ffffff !important;
        }

        /* (2) 지문/문제도 1.2배 */
        .p7-zone .p7-zone-body{ font-size: 22px !important; }
        .p7-zone.mission .p7-zone-body{ font-size: 23px !important; }

        @media (max-width: 640px){
          .p7-zone .p7-zone-body{ font-size: 20px !important; }
          .p7-zone.mission .p7-zone-body{ font-size: 20px !important; }
          .p7-opt-wrap div[data-testid="stButton"] > button{ font-size: 20px !important; min-height: 92px !important; }
        }

        /* (3) 게이지 연출 */
        @keyframes p7_gauge_wiggle {
          0%{ transform:translateX(0); } 25%{ transform:translateX(-2px); }
          50%{ transform:translateX(0); } 75%{ transform:translateX(2px); }
          100%{ transform:translateX(0); }
        }
        @keyframes p7_gauge_shake {
          0%{ transform:translateX(0); } 20%{ transform:translateX(-4px); }
          40%{ transform:translateX(4px); } 60%{ transform:translateX(-3px); }
          80%{ transform:translateX(3px); } 100%{ transform:translateX(0); }
        }
        @keyframes p7_gauge_flash {
          0%{ filter:brightness(1.0); } 50%{ filter:brightness(1.55); } 100%{ filter:brightness(1.0); }
        }

        /* 30초마다 색 변경 (stage 0~5) */
        .p7-hud-gauge.stage5 .fill{ background: linear-gradient(90deg, rgba(34,211,238,0.95), rgba(124,58,237,0.95)) !important; }
        .p7-hud-gauge.stage4 .fill{ background: linear-gradient(90deg, rgba(56,189,248,0.95), rgba(167,139,250,0.95)) !important; }
        .p7-hud-gauge.stage3 .fill{ background: linear-gradient(90deg, rgba(45,212,191,0.95), rgba(34,211,238,0.95)) !important; }
        .p7-hud-gauge.stage2 .fill{ background: linear-gradient(90deg, rgba(250,204,21,0.95), rgba(34,211,238,0.95)) !important; }
        .p7-hud-gauge.stage1 .fill{ background: linear-gradient(90deg, rgba(251,146,60,0.95), rgba(250,204,21,0.95)) !important; }
        .p7-hud-gauge.stage0 .fill{ background: linear-gradient(90deg, rgba(239,68,68,0.98), rgba(220,38,38,0.98)) !important; }

        /* 마지막 60초부터: 요동 */
        .p7-hud-gauge.last60{ animation: p7_gauge_wiggle 0.9s linear infinite; }

        /* 마지막 30초: 빨강 흔들 + 번쩍 */
        .p7-hud-gauge.last30{
          animation: p7_gauge_shake 0.35s linear infinite, p7_gauge_flash 0.55s ease-in-out infinite;
          border-color: rgba(239,68,68,0.55) !important;
          box-shadow: 0 0 26px rgba(239,68,68,0.18) !important;
        }

        /* 마지막 10초: 더 강하게 */
        .p7-hud-gauge.final{
          animation: p7_gauge_shake 0.24s linear infinite, p7_gauge_flash 0.35s ease-in-out infinite;
          box-shadow: 0 0 40px rgba(239,68,68,0.25) !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )
'''
    src = src[:insert_at] + ADD + src[insert_at:]
    print("[OK] injected readability/gauge CSS overrides")

# ---------------------------
# B) render_top_hud(): add gauge class calculation (stage/last60/last30/final)
# ---------------------------
m = re.search(r"^def\s+render_top_hud\s*\(\s*\)\s*:\s*\n", src, flags=re.M)
if not m:
    open(path, "w", encoding="utf-8").write(src)
    raise SystemExit("[WARN] render_top_hud not found (css only)")

m2 = re.search(r"^\s*def\s+\w+\s*\(", src[m.end():], flags=re.M)
end = (m.end() + m2.start()) if m2 else len(src)
body = src[m.start():end]

# If already patched, skip
if "stage = int(remaining // 30)" not in body:
    # Find gauge markup and make it use gauge_cls
    # 1) Ensure there is a gauge st.markdown block with <div class="p7-hud-gauge">
    idx = body.find('<div class="p7-hud-gauge"')
    if idx < 0:
        # some versions use {gauge_cls} already; then we only need class computation
        pass

    # Insert gauge_cls computation just before the gauge st.markdown that prints the gauge
    # We look for the FIRST occurrence of 'st.markdown(' that contains 'p7-hud-gauge'
    pat = re.compile(r"st\.markdown\(\s*(f?)(\"\"\"|\'\'\')[\s\S]*?p7-hud-gauge[\s\S]*?\2\s*,\s*unsafe_allow_html\s*=\s*True\s*\)", re.M)
    mm = pat.search(body)
    if mm:
        # Ensure the markdown is an f-string
        is_f = mm.group(1)
        block = mm.group(0)
        if is_f != "f":
            block2 = block.replace("st.markdown(", "st.markdown(f", 1)
        else:
            block2 = block

        # Replace class="p7-hud-gauge" with class="{gauge_cls}"
        block2 = block2.replace('class="p7-hud-gauge"', 'class="{gauge_cls}"')

        pre = body[:mm.start()]
        post = body[mm.end():]

        gauge_code = r'''
    # ---- Gauge Drama Classes (30s stage + last60/last30/final) ----
    stage = int(remaining // 30)  # 0~5 (150초 기준)
    gauge_cls = f"p7-hud-gauge stage{stage}"
    if remaining <= 60:
        gauge_cls += " last60"
    if remaining <= 30:
        gauge_cls += " last30"
    if remaining <= 10:
        gauge_cls += " final"
'''
        body = pre + gauge_code + block2 + post
        print("[OK] render_top_hud gauge class computation injected")

patched = src[:m.start()] + body + src[end:]
open(path, "w", encoding="utf-8").write(patched)
print("[DONE] patch applied")

