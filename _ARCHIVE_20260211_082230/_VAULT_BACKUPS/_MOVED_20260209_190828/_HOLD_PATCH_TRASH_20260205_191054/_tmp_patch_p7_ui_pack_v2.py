import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

# ------------------------------------------------------------
# 1) Inject CSS INSIDE inject_css() (safe)
# ------------------------------------------------------------
MARK = "P7_SAFE_UI_PACK_V2"
if MARK not in src:
    m = re.search(r"^def\s+inject_css\s*\(\s*\)\s*:\s*\n", src, flags=re.M)
    if not m:
        raise SystemExit("inject_css() not found")
    m2 = re.search(r"^\s*def\s+\w+\s*\(", src[m.end():], flags=re.M)
    end = (m.end() + m2.start()) if m2 else len(src)
    body = src[m.start():end]

    ADD = r'''
    # ---- P7 SAFE UI PACK V2 ----
    st.markdown(
        r"""
        <style>
        /* ''' + MARK + r''' */

        /* (A) 선택지: 흰 버튼이면 글자는 검정 (가독성) */
        .p7-opt-wrap div[data-testid="stButton"] > button{
          color:#111827 !important;
          font-size: 22px !important;   /* 1.2배 업 */
          font-weight: 950 !important;
        }
        .p7-opt-wrap div[data-testid="stButton"] > button *{
          color:#111827 !important;
        }

        /* hover(락온)에서는 흰 글자 유지 */
        .p7-opt-wrap div[data-testid="stButton"] > button:hover,
        .p7-opt-wrap div[data-testid="stButton"] > button:hover *{
          color:#ffffff !important;
        }

        /* (A-2) 모바일에서도 크게 */
        @media (max-width: 640px){
          .p7-opt-wrap div[data-testid="stButton"] > button{
            font-size: 21px !important;
            min-height: 92px !important;
          }
        }

        /* (B) 게이지(막대) 연출: 30초 단계 + 마지막 60/30/10 */
        @keyframes p7_gauge_wiggle {
          0%{ transform:translateX(0); }
          25%{ transform:translateX(-2px); }
          50%{ transform:translateX(0); }
          75%{ transform:translateX(2px); }
          100%{ transform:translateX(0); }
        }
        @keyframes p7_gauge_shake {
          0%{ transform:translateX(0); }
          20%{ transform:translateX(-4px); }
          40%{ transform:translateX(4px); }
          60%{ transform:translateX(-3px); }
          80%{ transform:translateX(3px); }
          100%{ transform:translateX(0); }
        }
        @keyframes p7_gauge_flash {
          0%{ filter:brightness(1.0); }
          50%{ filter:brightness(1.55); }
          100%{ filter:brightness(1.0); }
        }

        /* 30초마다 색 변화 (stage 0~5) */
        .p7-hud-gauge.stage5 .fill{ background: linear-gradient(90deg, rgba(34,211,238,0.95), rgba(124,58,237,0.95)) !important; }
        .p7-hud-gauge.stage4 .fill{ background: linear-gradient(90deg, rgba(56,189,248,0.95), rgba(167,139,250,0.95)) !important; }
        .p7-hud-gauge.stage3 .fill{ background: linear-gradient(90deg, rgba(45,212,191,0.95), rgba(34,211,238,0.95)) !important; }
        .p7-hud-gauge.stage2 .fill{ background: linear-gradient(90deg, rgba(250,204,21,0.95), rgba(34,211,238,0.95)) !important; }
        .p7-hud-gauge.stage1 .fill{ background: linear-gradient(90deg, rgba(251,146,60,0.95), rgba(250,204,21,0.95)) !important; }
        .p7-hud-gauge.stage0 .fill{ background: linear-gradient(90deg, rgba(239,68,68,0.98), rgba(220,38,38,0.98)) !important; }

        /* 마지막 60초: 요동 시작 */
        .p7-hud-gauge.last60{
          animation: p7_gauge_wiggle 0.9s linear infinite;
        }

        /* 마지막 30초: 빨간색 + 흔들 + 번쩍 */
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
    body2 = body.rstrip() + "\n\n" + ADD + "\n"
    src = src[:m.start()] + body2 + src[end:]
    print("[OK] SAFE UI PACK V2 injected")

# ------------------------------------------------------------
# 2) Patch gauge class generation INSIDE render_top_hud()
#    - Add stage + last60 + last30 + final classes
# ------------------------------------------------------------
m = re.search(r"^def\s+render_top_hud\s*\(\s*\)\s*:\s*\n", src, flags=re.M)
if not m:
    open(path, "w", encoding="utf-8").write(src)
    raise SystemExit("[WARN] render_top_hud not found (css only)")

m2 = re.search(r"^\s*def\s+\w+\s*\(", src[m.end():], flags=re.M)
end = (m.end() + m2.start()) if m2 else len(src)
body = src[m.start():end]

# Find the gauge HTML emission and replace only the class computation part
# We'll inject stage/lastXX right before the gauge st.markdown f-string.
if "stage" not in body or "last60" not in body:
    # Find the line that starts the gauge render: st.markdown(f""" <div class="{gauge_cls}">
    # We'll locate 'st.markdown(' and preceding gauge_cls = ... and replace with our safe block.
    # Safe heuristic: replace the FIRST occurrence of gauge_cls assignment to p7-hud-gauge in this function.
    body = re.sub(
        r'gauge_cls\s*=\s*["\']p7-hud-gauge["\'][\s\S]*?st\.markdown\(\s*f?"""[\s\S]*?<div class="\{gauge_cls\}">[\s\S]*?unsafe_allow_html\s*=\s*True[\s\S]*?\)\s*',
        r'''    # Thick gauge (30s stage colors + last-minute movement)
    pct = 0.0 if total <= 0 else max(0.0, min(1.0, remaining / total))
    w = int(pct * 100)

    stage = int(remaining // 30)  # 0~5 (150초 기준)
    gauge_cls = f"p7-hud-gauge stage{stage}"

    if remaining <= 60:
        gauge_cls += " last60"
    if remaining <= 30:
        gauge_cls += " last30"
    if remaining <= 10:
        gauge_cls += " final"

    st.markdown(
        f"""
        <div class="{gauge_cls}">
          <div class="fill" style="width:{w}%"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
''',
        body,
        count=1,
        flags=re.M
    )
    print("[OK] render_top_hud gauge classes patched (stage/last60/last30/final)")

patched = src[:m.start()] + body + src[end:]
open(path, "w", encoding="utf-8").write(patched)
print("[DONE] UI PACK V2 applied")

