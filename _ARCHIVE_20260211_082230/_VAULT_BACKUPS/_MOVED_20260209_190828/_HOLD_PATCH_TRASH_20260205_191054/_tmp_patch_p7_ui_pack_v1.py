import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

# ------------------------------------------------------------
# A) inject_css(): append UI PACK CSS (marker-based, idempotent)
# ------------------------------------------------------------
MARK = "P7_UI_PACK_V1"
if MARK not in src:
    m = re.search(r"^def\s+inject_css\s*\(\s*\)\s*:\s*\n", src, flags=re.M)
    if not m:
        raise SystemExit("inject_css() not found")

    # insert near the top of inject_css (after first line break)
    line_end = src.find("\n", m.end())
    insert_at = (line_end + 1) if line_end > 0 else m.end()

    css = r'''
    # ---- P7 UI PACK V1 (ALWAYS SAFE OVERRIDES) ----
    st.markdown(
        r"""
        <style>
        /* ''' + MARK + r''' */

        /* 1) 선택지 글자색: 흰 바탕이면 검정 글자 */
        .p7-opt-wrap div[data-testid="stButton"] > button,
        .p7-opt-wrap div[data-testid="stButton"] > button *{
          color: #111827 !important;  /* 거의 검정 */
        }

        /* hover 시에는 우리가 원하는 ‘락온’ 컬러(흰 글자) 유지 */
        .p7-opt-wrap div[data-testid="stButton"] > button:hover,
        .p7-opt-wrap div[data-testid="stButton"] > button:hover *{
          color:#ffffff !important;
        }

        /* 2) 글자 크기 1.2배 (지문/문제/선택지) */
        .p7-zone .p7-zone-body{ font-size: 22px !important; }   /* (기존 18~19 → 22) */
        .p7-zone.mission .p7-zone-body{ font-size: 23px !important; }
        .p7-opt-wrap div[data-testid="stButton"] > button{
          font-size: 21px !important;   /* (기존 18 → 21) */
          font-weight: 950 !important;
        }

        @media (max-width: 640px){
          .p7-zone .p7-zone-body{ font-size: 20px !important; }
          .p7-zone.mission .p7-zone-body{ font-size: 20px !important; }
          .p7-opt-wrap div[data-testid="stButton"] > button{ font-size: 20px !important; }
        }

        /* 3) 타이머 게이지: 30초마다 색 변화 + 마지막 1분부터 움직임 + 마지막 30초 빨강 흔들 */
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

        /* stage0~5: 30초 단위 컬러 테마 */
        .p7-hud-gauge.stage5 .fill{ background: linear-gradient(90deg, rgba(34,211,238,0.95), rgba(124,58,237,0.95)) !important; } /* 150~120 */
        .p7-hud-gauge.stage4 .fill{ background: linear-gradient(90deg, rgba(56,189,248,0.95), rgba(167,139,250,0.95)) !important; } /* 119~90 */
        .p7-hud-gauge.stage3 .fill{ background: linear-gradient(90deg, rgba(45,212,191,0.95), rgba(34,211,238,0.95)) !important; } /* 89~60 */
        .p7-hud-gauge.stage2 .fill{ background: linear-gradient(90deg, rgba(250,204,21,0.95), rgba(34,211,238,0.95)) !important; }  /* 59~30 */
        .p7-hud-gauge.stage1 .fill{ background: linear-gradient(90deg, rgba(251,146,60,0.95), rgba(250,204,21,0.95)) !important; } /* 29~? (우리는 아래에서 빨강으로 덮음) */
        .p7-hud-gauge.stage0 .fill{ background: linear-gradient(90deg, rgba(239,68,68,0.95), rgba(251,146,60,0.95)) !important; }  /* 29~0 */

        /* 마지막 60초부터: 요동 */
        .p7-hud-gauge.last60{
          animation: p7_gauge_wiggle 0.9s linear infinite;
        }

        /* 마지막 30초부터: 빨간색 + 흔들 + 번쩍 */
        .p7-hud-gauge.last30 .fill{
          background: linear-gradient(90deg, rgba(239,68,68,0.98), rgba(220,38,38,0.98)) !important;
        }
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
        unsafe_allow_html=True
    )
'''
    src = src[:insert_at] + css + src[insert_at:]
    print("[OK] injected UI PACK CSS")

# ------------------------------------------------------------
# B) render_top_hud(): gauge class -> stageN + last60/last30/final (no logic change)
# ------------------------------------------------------------
m = re.search(r"^def\s+render_top_hud\s*\(\s*\)\s*:\s*\n", src, flags=re.M)
if not m:
    open(path, "w", encoding="utf-8").write(src)
    raise SystemExit("[WARN] render_top_hud() not found - CSS only applied")

m2 = re.search(r"^\s*def\s+\w+\s*\(", src[m.end():], flags=re.M)
end = (m.end() + m2.start()) if m2 else len(src)
body = src[m.start():end]

if "stage" not in body or "last60" not in body:
    # Replace the existing gauge_cls computation block (safe pattern)
    # Find block starting at: gauge_cls = "p7-hud-gauge"
    body2 = re.sub(
        r'''
gauge_cls\s*=\s*"p7-hud-gauge"\s*
(?:.|\n)*?
st\.markdown\(
\s*f?"""[\s\S]*?<div class="\{gauge_cls\}">[\s\S]*?"""\s*,
\s*unsafe_allow_html\s*=\s*True\s*,?\s*\)
''',
        r'''
    # Thick gauge (30s stage colors + last-minute movement)
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
        flags=re.X
    )
    body = body2
    print("[OK] patched gauge classes (stage/last60/last30/final)")

patched = src[:m.start()] + body + src[end:]
open(path, "w", encoding="utf-8").write(patched)
print("[DONE] UI PACK v1 applied")

