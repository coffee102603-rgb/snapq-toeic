import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

# ------------------------------------------------------------
# 1) inject_css(): add P7 GAME THEME (ONCE) after the existing CRIT block
# ------------------------------------------------------------
def add_theme_css(s: str) -> str:
    if "P7_GAME_THEME_PACK_V1" in s:
        return s

    m = re.search(r"^def\s+inject_css\s*\(\s*\)\s*:\s*\n", s, flags=re.M)
    if not m:
        raise SystemExit("inject_css() not found")

    # Insert after the existing CRIT st.markdown(...) block close
    inj_start = m.start()
    inj_slice = s[inj_start:]
    pos = inj_slice.find("unsafe_allow_html=True")
    end_call = inj_slice.find("\n    )", pos) if pos >= 0 else -1
    insert_at = (inj_start + end_call + len("\n    )")) if end_call >= 0 else (inj_start + m.end())

    theme = r"""

    # ---- P7 GAME THEME (ONCE per session) ----
    if st.session_state.get("_p7_game_theme_once", False):
        return
    st.session_state["_p7_game_theme_once"] = True

    st.markdown(
        """
        <style>
        /* P7_GAME_THEME_PACK_V1 */

        /* ====== P7 전장 배경(ICE/STRATEGY) ====== */
        .stApp{
          background:
            radial-gradient(900px 650px at 18% 16%, rgba(34,211,238,0.18), transparent 60%),
            radial-gradient(900px 650px at 72% 14%, rgba(94,234,212,0.14), transparent 62%),
            radial-gradient(900px 900px at 50% 78%, rgba(56,189,248,0.10), transparent 70%),
            linear-gradient(180deg, #141C2B 0%, #0E1624 55%, #0B1020 100%) !important;
          color: #E5E7EB !important;
        }

        /* ====== HUD 칩/바 대비 강화 ====== */
        .p7-chip{
          background: rgba(0,0,0,0.32) !important;
          border: 1px solid rgba(34,211,238,0.22) !important;
          color:#fff !important;
          text-shadow: 0 2px 10px rgba(0,0,0,0.35) !important;
        }
        .p7-chip b{ color:#fff !important; }

        /* ====== 지문/문제 카드(네모박스) ====== */
        .p7-zone{
          position: relative;
          border-radius: 18px;
          padding: 16px 18px;
          border: 1px solid rgba(34,211,238,0.22);
          background: rgba(10,16,28,0.74);
          box-shadow: 0 14px 34px rgba(0,0,0,0.22);
          backdrop-filter: blur(8px);
          margin: 10px 0;
          overflow: hidden;
        }
        .p7-zone:before{
          content:"";
          position:absolute;
          left:0; top:0; bottom:0;
          width: 6px;
          border-radius: 18px 0 0 18px;
          background: rgba(34,211,238,0.90);
        }

        /* 지문(인텔) / 문제(미션) 색 분리 */
        .p7-zone.intel{
          border-color: rgba(34,211,238,0.26);
          background: linear-gradient(180deg, rgba(34,211,238,0.12), rgba(10,16,28,0.70));
        }
        .p7-zone.mission{
          border-color: rgba(167,139,250,0.24);
          background: linear-gradient(180deg, rgba(167,139,250,0.12), rgba(10,16,28,0.70));
        }
        .p7-zone.intel:before{ background: rgba(34,211,238,0.92); }
        .p7-zone.mission:before{ background: rgba(167,139,250,0.92); }

        /* 지문/문제 글자 크기(게임 가독성) */
        .p7-zone .p7-zone-body{
          color:#ffffff !important;
          font-weight: 800 !important;
          line-height: 1.65 !important;
          letter-spacing: 0.1px;
          text-shadow: 0 2px 10px rgba(0,0,0,0.55);
          font-size: 18px;
        }
        /* 문제는 더 크게 */
        .p7-zone.mission .p7-zone-body{ font-size: 19px; font-weight: 900 !important; }

        /* ====== 선택지(손가락 클릭 카드 버튼) ====== */
        .p7-opt-wrap{
          display:grid;
          gap: 14px;
          margin-top: 12px;
        }
        .p7-opt-wrap div[data-testid="stButton"] > button{
          width: 100% !important;
          min-height: 76px !important;
          padding: 18px 18px !important;
          border-radius: 18px !important;

          font-size: 18px !important;
          font-weight: 900 !important;
          line-height: 1.20 !important;

          background: rgba(255,255,255,0.96) !important;
          color: #0F172A !important;
          border: 1px solid rgba(255,255,255,0.22) !important;
          box-shadow: 0 14px 34px rgba(0,0,0,0.20) !important;

          white-space: normal !important;
          text-align: center !important;

          transition: transform .10s ease, box-shadow .10s ease, filter .10s ease;
        }
        /* hover = 락온 */
        .p7-opt-wrap div[data-testid="stButton"] > button:hover{
          transform: translateY(-2px);
          filter: brightness(1.04) saturate(1.05);
          box-shadow: 0 18px 40px rgba(0,0,0,0.26) !important;
          background: linear-gradient(135deg, rgba(34,211,238,0.95), rgba(77,163,255,0.95)) !important;
          color:#ffffff !important;
        }
        .p7-opt-wrap div[data-testid="stButton"] > button:hover *{ color:#ffffff !important; }
        /* press = 잠금 */
        .p7-opt-wrap div[data-testid="stButton"] > button:active{
          transform: translateY(1px) scale(0.995);
          box-shadow: 0 10px 22px rgba(0,0,0,0.18) !important;
        }

        /* ====== 타이머 심장쫄깃(항상 살아있음 + 구간별 강화) ====== */
        .p7-time-chip{ position:relative; font-weight:1000 !important; }
        .p7-time-chip b{ font-size: 20px !important; font-weight: 1100 !important; }

        @keyframes p7AlivePulse{
          0%{transform:scale(1); filter:brightness(1.00)}
          50%{transform:scale(1.03); filter:brightness(1.12)}
          100%{transform:scale(1); filter:brightness(1.00)}
        }
        @keyframes p7BlinkDanger{
          0%{filter:brightness(1)}
          50%{filter:brightness(1.35)}
          100%{filter:brightness(1)}
        }
        @keyframes p7JitterFinal{
          0%{transform:translateX(0)}
          20%{transform:translateX(-1px)}
          40%{transform:translateX(1px)}
          60%{transform:translateX(-1px)}
          80%{transform:translateX(1px)}
          100%{transform:translateX(0)}
        }

        /* 기본: 항상 심장박동 느낌 */
        .p7-time-alive{ animation: p7AlivePulse 1.1s ease-in-out infinite; }

        /* 60초↓ */
        .p7-time-warn{
          background: rgba(255,204,0,0.18) !important;
          border-color: rgba(255,204,0,0.45) !important;
          box-shadow: 0 0 0 1px rgba(255,204,0,0.18) inset, 0 0 22px rgba(255,204,0,0.10) !important;
          animation: p7AlivePulse .95s ease-in-out infinite;
        }

        /* 30초↓ */
        .p7-time-danger2{
          background: rgba(255,45,45,0.22) !important;
          border-color: rgba(255,45,45,0.55) !important;
          box-shadow: 0 0 0 1px rgba(255,45,45,0.20) inset, 0 0 30px rgba(255,45,45,0.18) !important;
          animation: p7BlinkDanger .75s infinite;
        }

        /* 10초↓: 흔들림 */
        .p7-time-final2{
          background: rgba(255,0,0,0.26) !important;
          border-color: rgba(255,0,0,0.70) !important;
          box-shadow: 0 0 0 1px rgba(255,0,0,0.22) inset, 0 0 42px rgba(255,0,0,0.28) !important;
          animation: p7JitterFinal .24s linear infinite, p7BlinkDanger .35s infinite;
        }

        /* ====== 모바일 최적 ====== */
        @media (max-width: 640px){
          .p7-zone .p7-zone-body{ font-size: 18px !important; }
          .p7-zone.mission .p7-zone-body{ font-size: 17px !important; }
          .p7-opt-wrap div[data-testid="stButton"] > button{
            min-height: 86px !important;
            font-size: 18px !important;
            padding: 18px 14px !important;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
"""
    return s[:insert_at] + theme + s[insert_at:]


# ------------------------------------------------------------
# 2) render_top_hud(): make TIME chip use stage classes
# ------------------------------------------------------------
def patch_render_top_hud(s: str) -> str:
    m = re.search(r"^def\s+render_top_hud\s*\(\s*\)\s*:\s*\n", s, flags=re.M)
    if not m:
        raise SystemExit("render_top_hud() not found")
    m2 = re.search(r"^\s*def\s+\w+\s*\(", s[m.end():], flags=re.M)
    end = (m.end() + m2.start()) if m2 else len(s)
    body = s[m.start():end]

    # ensure time stage exists after remaining assignment
    if "time_stage =" not in body:
        body = re.sub(
            r"(remaining\s*=\s*max\([^\n]+\)\s*\n)",
            r"""\1
    # --- TIME FX STAGE (UI ONLY) ---
    time_stage = "p7-time-alive"
    if remaining <= 10:
        time_stage = "p7-time-final2"
    elif remaining <= 30:
        time_stage = "p7-time-danger2"
    elif remaining <= 60:
        time_stage = "p7-time-warn"
""",
            body,
            count=1
        )

    # replace TIME span (exact current form)
    body = body.replace(
        '<span class="p7-chip">⏱ TIME <b>{get_time_display(remaining)}</b></span>',
        '<span class="p7-chip p7-time-chip {time_stage}">⏱ TIME <b>{get_time_display(remaining)}</b></span>'
    )

    return s[:m.start()] + body + s[end:]


src2 = add_theme_css(src)
src2 = patch_render_top_hud(src2)
open(path, "w", encoding="utf-8").write(src2)
print("[OK] P7 GAME SKIN PACK applied (theme + timer classes)")

