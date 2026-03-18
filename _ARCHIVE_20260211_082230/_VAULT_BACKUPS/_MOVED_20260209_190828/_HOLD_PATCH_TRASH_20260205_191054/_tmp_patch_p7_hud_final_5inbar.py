import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

m = re.search(r"^def\s+render_top_hud\s*\(\s*\)\s*:\s*\n", src, flags=re.M)
if not m:
    raise SystemExit("render_top_hud() not found")

start = m.start()
m2 = re.search(r"^\s*def\s+\w+\s*\(", src[m.end():], flags=re.M)
end = (m.end() + m2.start()) if m2 else len(src)

NEW_FUNC = r'''def render_top_hud():
    """
    ✅ P7 FINAL HUD (5 INSIDE ONE BAR)
    - STEP/TIME/MISS/COMBO + HUB 를 "같은 한 줄(st.columns)" 안에서 바 형태로 스타일링
    - 바 아래에 게이지
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

    # ✅ 이 컨테이너 안에서만 "첫 stHorizontalBlock"을 HUD BAR로 만든다
    with st.container():
        st.markdown(
            """
            <style>
            /* 이 컨테이너의 첫 줄(columns = stHorizontalBlock)을 HUD BAR로 */
            div[data-testid="stVerticalBlock"]:has(#p7hud_scope_anchor) > div[data-testid="stHorizontalBlock"]{
                background: rgba(15,23,42,0.55);
                border: 1px solid rgba(255,255,255,0.14);
                border-radius: 16px;
                padding: 6px 10px;
                margin: 0 0 6px 0;
                backdrop-filter: blur(10px);
            }

            /* 칩 */
            .p7-hud-left{ display:flex; gap:8px; align-items:center; flex-wrap:wrap; }
            .p7-chip{
                display:inline-flex; align-items:center; gap:6px;
                padding:5px 9px;
                border-radius:999px;
                background: rgba(255,255,255,0.10);
                border: 1px solid rgba(255,255,255,0.12);
                font-weight:900;
                line-height:1;
            }

            /* HUB 버튼도 같은 바 안(우측 컬럼)에서 칩처럼 */
            div[data-testid="stVerticalBlock"]:has(#p7hud_scope_anchor) div[data-testid="stButton"]>button{
                height:28px !important;
                min-height:28px !important;
                padding:0 10px !important;
                border-radius:999px !important;
                font-weight:900 !important;
                width:100% !important;
            }

            /* 게이지 */
            .p7-hud-gauge{
                height:10px;
                border-radius:999px;
                overflow:hidden;
                background: rgba(255,255,255,0.10);
                border: 1px solid rgba(255,255,255,0.12);
                margin: 6px 0 10px 0;
            }
            .p7-hud-gauge .fill{
                height:100%;
                background: linear-gradient(90deg, rgba(34,211,238,0.95), rgba(124,58,237,0.95));
            }
            </style>

            <div id="p7hud_scope_anchor"></div>
            """,
            unsafe_allow_html=True
        )

        # ✅ 이 st.columns 한 줄 자체가 "HUD BAR"가 된다 (HUB도 같은 줄)
        colL, colR = st.columns([12, 2], gap="small")
        with colL:
            st.markdown(
                f"""
                <div class="p7-hud-left">
                  <span class="p7-chip">🔥 STEP <b>{step}</b>/3</span>
                  <span class="p7-chip">⏱ TIME <b>{get_time_display(remaining)}</b></span>
                  <span class="p7-chip">❌ MISS <b>{wrong}</b>/3</span>
                  <span class="p7-chip">💣 COMBO <b>{combo.current_combo}</b></span>
                </div>
                """,
                unsafe_allow_html=True
            )
        with colR:
            if st.button("🏠 HUB", key="p7_hud_mainhub_btn", use_container_width=True):
                _safe_switch_page(
                    ["main_hub.py", "./main_hub.py", "pages/00_Main_Hub.py", "pages\\00_Main_Hub.py"],
                    fallback_hint="메인 허브",
                )

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

patched = src[:start] + NEW_FUNC + src[end:]
open(path, "w", encoding="utf-8").write(patched)
print("[OK] render_top_hud -> 5 items inside ONE BAR")

