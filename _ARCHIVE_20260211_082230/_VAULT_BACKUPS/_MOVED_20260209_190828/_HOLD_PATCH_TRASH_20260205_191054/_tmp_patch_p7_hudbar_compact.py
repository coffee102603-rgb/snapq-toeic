import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

# --- A) Remove big spacer div markdowns (top space killers) ---
# matches: st.markdown("<div style='height: 200px'></div>", unsafe_allow_html=True)
src2 = re.sub(
    r"""st\.markdown\(\s*([rRuU]?[\'\"])\s*<div[^>]*style\s*=\s*[\'\"][^\'\"]*height\s*:\s*\d+px[^\'\"]*[\'\"][^>]*>\s*</div>\s*\1\s*,\s*unsafe_allow_html\s*=\s*True\s*\)""",
    "# [AUTO-REMOVED SPACER DIV]",
    src,
    flags=re.I | re.S,
)

# --- B) Replace render_top_hud() fully ---
m = re.search(r"^def\s+render_top_hud\s*\(\s*\)\s*:\s*\n", src2, flags=re.M)
if not m:
    raise SystemExit("render_top_hud() not found")

start = m.start()
m2 = re.search(r"^\s*def\s+\w+\s*\(", src2[m.end():], flags=re.M)
end = (m.end() + m2.start()) if m2 else len(src2)

NEW_FUNC = r'''def render_top_hud():
    """
    ✅ P7 HUD BAR COMPACT
    - STEP/TIME/MISS/COMBO/HUB를 '한 줄 바'에 정리
    - 아래에 게이지(긴 막대) 바로 출력
    - 로직 변화 0 (표시/배치만)
    """
    update_timebomb()
    tb: TimebombState = st.session_state.p7_timebomb
    combo: ComboState = st.session_state.p7_combo

    # 1초 갱신(전투 중만) - 기존 유지
    if st.session_state.get("p7_has_started", False) and not st.session_state.get("p7_has_finished", False) and not tb.is_over:
        try:
            from streamlit_autorefresh import st_autorefresh
            st_autorefresh(interval=1000, key="p7_top_hud_tick")
        except ModuleNotFoundError:
            pass

    wrong = int(st.session_state.get("p7_miss_count", 0))
    step = int(st.session_state.get("p7_current_step", 1))

    total = max(1, int(getattr(tb, "total_limit", 150) or 150))
    remaining = max(0, int(getattr(tb, "remaining", 0)))

    # ---- HUD BAR (ONE ROW) ----
    # 왼쪽(4요소) + 오른쪽(HUB 버튼)을 같은 바 안에
    st.markdown(
        """
        <style>
        /* HUD 바를 '진짜 한 줄 바'로 고정 */
        .p7-hudbar{
          display:flex; align-items:center; justify-content:space-between;
          gap:10px; padding:8px 10px; border-radius:16px;
          background: rgba(15,23,42,0.55);
          border: 1px solid rgba(255,255,255,0.14);
          backdrop-filter: blur(10px);
          margin: 0 0 6px 0;
        }
        .p7-hud-left{ display:flex; gap:10px; align-items:center; flex-wrap:wrap; }
        .p7-chip{
          display:inline-flex; align-items:center; gap:6px;
          padding:6px 10px; border-radius:999px;
          background: rgba(255,255,255,0.10);
          border: 1px solid rgba(255,255,255,0.12);
          font-weight:900;
        }
        .p7-hud-gauge{
          height:10px; border-radius:999px; overflow:hidden;
          background: rgba(255,255,255,0.10);
          border: 1px solid rgba(255,255,255,0.12);
          margin: 6px 0 10px 0;
        }
        .p7-hud-gauge .fill{
          height:100%;
          background: linear-gradient(90deg, rgba(34,211,238,0.95), rgba(124,58,237,0.95));
        }
        /* 버튼을 칩처럼 */
        .p7-hubbtn div[data-testid="stButton"]>button{
          height:34px !important; min-height:34px !important;
          padding:0 12px !important; border-radius:14px !important;
          font-weight:900 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    colL, colR = st.columns([10,2], gap="small")
    with colL:
        st.markdown(
            f"""
            <div class="p7-hudbar">
              <div class="p7-hud-left">
                <span class="p7-chip">🔥 STEP <b>{step}</b>/3</span>
                <span class="p7-chip">⏱ TIME <b>{get_time_display(remaining)}</b></span>
                <span class="p7-chip">❌ MISS <b>{wrong}</b>/3</span>
                <span class="p7-chip">💣 COMBO <b>{combo.current_combo}</b></span>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with colR:
        st.markdown('<div class="p7-hubbtn">', unsafe_allow_html=True)
        if st.button("🏠 HUB", key="p7_hud_mainhub_btn", use_container_width=True):
            _safe_switch_page(
                ["main_hub.py", "./main_hub.py", "pages/00_Main_Hub.py", "pages\\00_Main_Hub.py"],
                fallback_hint="메인 허브",
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # ---- GAUGE (UNDER BAR) ----
    pct = max(0.0, min(1.0, remaining / total))
    w = int(pct * 100)
    st.markdown(
        f"""
        <div class="p7-hud-gauge">
          <div class="fill" style="width:{w}%"></div>
        </div>
        """,
        unsafe_allow_html=True
    )
'''

patched = src2[:start] + NEW_FUNC + src2[end:]
open(path, "w", encoding="utf-8").write(patched)
print("[OK] render_top_hud replaced + spacer div removed (if any)")

