import re

path = r"""C:\Users\최정은\Desktop\snapq_toeic\app\arenas\p7_reading_arena.py"""
src = open(path, "r", encoding="utf-8").read()

# -----------------------------
# A) inject_css: add CSS once (marker)
# -----------------------------
CSS_MARK = "P7_HUD_GAUGE_OPTIONS_CSS_V1"
if CSS_MARK not in src:
    m = re.search(r"^def\s+inject_css\s*\(\s*\)\s*:\s*\n", src, flags=re.M)
    if not m:
        raise SystemExit("inject_css() not found")

    m2 = re.search(r"^\s*def\s+\w+\s*\(", src[m.end():], flags=re.M)
    inj_end = (m.end() + m2.start()) if m2 else len(src)
    body = src[m.start():inj_end]

    add = r'''
    # ---- P7_HUD_GAUGE_OPTIONS_CSS_V1 ----
    st.markdown(
        r"""
        <style>
        /* ''' + CSS_MARK + r''' */

        /* (1) 선택지 1.1배 + 더 굵게 */
        .p7-opt-wrap div[data-testid="stButton"] > button{
          font-size: 20px !important;   /* 기존보다 1.1배 */
          font-weight: 950 !important;
        }

        /* (선택지 글자색은 이미 검정 패치가 있을 수 있어 유지) */
        .p7-opt-wrap div[data-testid="stButton"] > button,
        .p7-opt-wrap div[data-testid="stButton"] > button *{
          color:#0B1020 !important;
          opacity:1 !important;
          text-shadow:none !important;
        }
        .p7-opt-wrap div[data-testid="stButton"] > button:hover,
        .p7-opt-wrap div[data-testid="stButton"] > button:hover *{
          color:#ffffff !important;
        }

        /* (2) 게이지: 30초 단계색 + last60 wiggle + last30 red shake + final stronger */
        @keyframes p7_gauge_wiggle{
          0%{transform:translateX(0)}25%{transform:translateX(-2px)}50%{transform:translateX(0)}75%{transform:translateX(2px)}100%{transform:translateX(0)}
        }
        @keyframes p7_gauge_shake{
          0%{transform:translateX(0)}20%{transform:translateX(-4px)}40%{transform:translateX(4px)}60%{transform:translateX(-3px)}80%{transform:translateX(3px)}100%{transform:translateX(0)}
        }
        @keyframes p7_gauge_flash{
          0%{filter:brightness(1.0)}50%{filter:brightness(1.55)}100%{filter:brightness(1.0)}
        }

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
    print("[OK] CSS injected inside inject_css()")


# -----------------------------
# B) Replace render_top_hud() ENTIRELY (safe)
# -----------------------------
m = re.search(r"^def\s+render_top_hud\s*\(\s*\)\s*:\s*\n", src, flags=re.M)
if not m:
    # if missing, we won't crash; just write and exit
    open(path, "w", encoding="utf-8").write(src)
    raise SystemExit("[WARN] render_top_hud() not found")

m2 = re.search(r"^\s*def\s+\w+\s*\(", src[m.end():], flags=re.M)
end = (m.end() + m2.start()) if m2 else len(src)

NEW_FUNC = r'''def render_top_hud():
    """
    ✅ HUD 복구 + 게이지 드라마
    - STEP/TIME/MISS/COMBO 표시 복구
    - 게이지: stage(30초) + last60/last30/final 클래스 부여
    - 로직 변화 0 (표시/클래스만)
    """
    update_timebomb()
    tb: TimebombState = st.session_state.p7_timebomb
    combo: ComboState = st.session_state.p7_combo

    # HUD 전용 tick (전투 중만)
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

    # HUD bar
    colL, colR = st.columns([12, 2], gap="small")
    with colL:
        st.markdown(
            f"""
            <div class="p7-hud-left">
              <span class="p7-chip">🔥 STEP <b>{step}</b>/3</span>
              <span class="p7-chip p7-time-chip">⏱ TIME <b>{get_time_display(remaining)}</b></span>
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

    # Gauge drama
    pct = max(0.0, min(1.0, remaining / total))
    w = int(pct * 100)

    stage = int(remaining // 30)  # 0~5
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
'''

src = src[:m.start()] + NEW_FUNC + src[end:]
open(path, "w", encoding="utf-8").write(src)
print("[OK] render_top_hud replaced safely")

# -----------------------------
# C) Ensure reading_arena_page() calls render_top_hud()
# -----------------------------
src = open(path, "r", encoding="utf-8").read()
if "def reading_arena_page" in src and "render_top_hud()" not in src:
    # fallback: insert render_top_hud call before render_p7_step call
    src = src.replace("render_p7_step(", "render_top_hud()\n    render_p7_step(", 1)
    open(path, "w", encoding="utf-8").write(src)
    print("[OK] ensured render_top_hud() call")

print("[DONE] patch complete")

