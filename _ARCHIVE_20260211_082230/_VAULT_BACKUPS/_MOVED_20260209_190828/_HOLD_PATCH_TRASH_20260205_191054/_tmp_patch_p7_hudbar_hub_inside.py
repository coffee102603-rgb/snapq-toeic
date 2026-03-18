import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

# -------------------------
# A) inject_css(): tighten top padding (safe small edit)
# -------------------------
m_inj = re.search(r"^def\s+inject_css\s*\(\s*\)\s*:\s*\n", src, flags=re.M)
if not m_inj:
    raise SystemExit("inject_css() not found")

# we only tweak the existing CRIT CSS line for .block-container if present
# if not present, we won't force-insert big stuff; we just adjust if found.
src2 = src
src2 = re.sub(
    r"\.block-container\s*\{\s*padding-top:\s*0\.6rem\s*!important;\s*padding-bottom:\s*1\.0rem\s*!important;\s*\}",
    ".block-container { padding-top: 0.15rem !important; padding-bottom: 0.85rem !important; }",
    src2
)

# also reduce any remaining generic top padding if it exists
src2 = re.sub(
    r"\.block-container\s*\{\s*padding-top:\s*0\.2rem\s*!important;\s*padding-bottom:\s*1\.0rem\s*!important;\s*\}",
    ".block-container { padding-top: 0.15rem !important; padding-bottom: 0.85rem !important; }",
    src2
)

# -------------------------
# B) render_top_hud(): replace fully with "anchor + columns styled as ONE BAR"
# -------------------------
m = re.search(r"^def\s+render_top_hud\s*\(\s*\)\s*:\s*\n", src2, flags=re.M)
if not m:
    raise SystemExit("render_top_hud() not found")

start = m.start()
m2 = re.search(r"^\s*def\s+\w+\s*\(", src2[m.end():], flags=re.M)
end = (m.end() + m2.start()) if m2 else len(src2)

NEW_FUNC = r'''def render_top_hud():
    """
    ✅ P7 HUD (HUB INSIDE BAR)
    - 긴 막대(바) 안에 STEP/TIME/MISS/COMBO + HUB까지 전부 포함(시각적으로 1바)
    - 게이지는 바로 아래
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

    # ✅ 앵커 + 다음 horizontal block을 "바"로 스타일링 (HUB 버튼도 같은 블록 안이라 바 안처럼 보임)
    st.markdown(
        """
        <style>
        /* anchor 다음에 오는 columns 블록을 통째로 HUD BAR로 만들기 */
        div#p7hud_anchor + div[data-testid="stHorizontalBlock"]{
            background: rgba(15,23,42,0.55);
            border: 1px solid rgba(255,255,255,0.14);
            border-radius: 16px;
            padding: 6px 10px;
            margin: 0 0 6px 0;
            backdrop-filter: blur(10px);
        }

        /* columns 내부 정렬 */
        div#p7hud_anchor + div[data-testid="stHorizontalBlock"] > div{
            align-items: center;
        }

        /* 왼쪽 칩 라인 */
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

        /* HUB 버튼을 바 안 칩처럼 */
        div#p7hud_anchor + div[data-testid="stHorizontalBlock"] div[data-testid="stButton"]>button{
            height:28px !important;
            min-height:28px !important;
            padding:0 10px !important;
            border-radius:999px !important;
            font-weight:900 !important;
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
        <div id="p7hud_anchor"></div>
        """,
        unsafe_allow_html=True
    )

    # ✅ 이 columns 블록 자체가 위 CSS에 의해 "긴 바"가 됨 -> HUB도 바 안으로 흡수됨(시각적으로)
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

patched = src2[:start] + NEW_FUNC + src2[end:]
open(path, "w", encoding="utf-8").write(patched)
print("[OK] render_top_hud -> HUB INSIDE BAR + inject_css compact tweak")

