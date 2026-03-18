# pages/02_P5_Timebomb_Arena.py
# UI/CSS SAFE PATCH (A-PALETTE FINAL):
# - Keep structure/keys/flow exactly the same
# - Apply SnapQ A palette: common navy/charcoal base + P5 warm accents
# - Mobile readability maintained (A-mode brightness uplift)
# - No arena logic change

import streamlit as st
from app.arenas import p5_timebomb_arena


def _switch(target: str):
    if hasattr(st, "switch_page"):
        try:
            st.switch_page(target)  # type: ignore[attr-defined]
            return
        except Exception:
            pass
    if hasattr(st, "page_link"):
        try:
            st.page_link(target, label=f"Go: {target}")  # type: ignore[attr-defined]
            return
        except Exception:
            pass
    st.info("이 환경에선 페이지 이동이 제한될 수 있어요. (브라우저 뒤로가기/좌측 메뉴)")


def _nav_card(label: str, target: str, key: str):
    if st.button(label, key=key, use_container_width=True):
        _switch(target)


def _set_timer(sec: int):
    st.session_state["p5_set_seconds"] = int(sec)


GRAM4 = [
    "⚙️ 동력 · 동사/시제",
    "🎯 조준 · 품사/수식",
    "🔗 연결 · 관계/구조",
    "🧨 변수 · 가정법/함정",
]
VOCA3 = ["EASY 77 ✅", "MIX 🎲", "HARD 33 ☠️"]


def _inject_gate_css():
    st.markdown(
        """
        <style>
        /* =========================================================
           SNAPQ A PALETTE (COMMON BASE)
           - Mobile-first
           - Same game, different arena
           ========================================================= */
        :root{
          /* Common base (navy/charcoal) */
          --bg-base: #0E1624;
          --bg-grad-1: #141C2B;
          --bg-grad-2: #1B2333;

          /* Text */
          --txt: rgba(229,231,235,0.96);
          --muted: rgba(156,163,175,0.90);
          --line: rgba(255,255,255,0.20);

          /* P5 (heat) accents */
          --p5-main: #FF4D4F;      /* bomb / danger */
          --p5-accent: #FF8A3D;    /* gauge / highlight */
          --p5-accentA: #FF2D55;   /* hot pink-red */
          --p5-accentB: #FF7A18;   /* orange */

          /* Panels (glass) */
          --glass: rgba(255,255,255,0.12);
          --glass2: rgba(255,255,255,0.14);

          /* Lane tints (keep subtle) */
          --lane-timer-a: rgba(255,138,61,0.18);
          --lane-timer-b: rgba(255,77,79,0.08);

          --lane-gram-a: rgba(255,77,79,0.16);
          --lane-gram-b: rgba(255,138,61,0.08);

          --lane-voca-a: rgba(167,139,250,0.16);
          --lane-voca-b: rgba(56,189,248,0.08);

          /* Chips */
          --chip-rule-a: rgba(255,77,79,0.22);
          --chip-rule-b: rgba(255,45,85,0.14);
          --chip-timer-a: rgba(255,138,61,0.20);
          --chip-timer-b: rgba(255,122,24,0.13);
        }

        /* =========================================================
           Background (A-mode: not too dark, still arena)
           ========================================================= */
        [data-testid="stAppViewContainer"]{
          background:
            radial-gradient(900px 650px at 22% 16%, rgba(255,138,61,0.18), transparent 58%),
            radial-gradient(820px 620px at 72% 14%, rgba(255,77,79,0.14), transparent 62%),
            radial-gradient(1000px 900px at 50% 78%, rgba(56,189,248,0.10), transparent 72%),
            linear-gradient(180deg, var(--bg-grad-1) 0%, var(--bg-base) 55%, #0B1020 100%) !important;
        }

        /* Mobile-friendly margins (0.3cm-ish) */
        .block-container{
          max-width: 1200px !important;
          padding-top: 2.0rem !important;
          padding-bottom: 1.8rem !important;
        }
        @media (max-width: 520px){
          .block-container{
            padding-left: 0.85rem !important;
            padding-right: 0.85rem !important;
            padding-top: 1.4rem !important;
          }
        }

        /* Center-align EVERYTHING */
        .p5-titlewrap, .p5-title, .p5-titleline{ text-align:center; margin-left:auto; margin-right:auto; }
        .p5-panel, .p5-briefbar, .p5-sidechip, .p5-currentbar, .p5-modecard, .p5-chip{ text-align:center; }
        .p5-modecard h4, .p5-modecard .tag{ text-align:center; }
        details summary{ text-align:center !important; }
        .p5-topnav, .p5-topnav *{ text-align:center; }
        .p5-timercol, .p5-timercol *{ text-align:center; }

        /* Streamlit button text center */
        div[data-testid="stButton"] > button{ justify-content:center !important; }
        div[data-testid="stButton"] > button p{ text-align:center !important; width:100% !important; }

        .p5-titlewrap{ margin-top: 18px; }
        .p5-title{
          font-size: 48px; font-weight: 950; color: var(--txt);
          text-shadow: 0 8px 22px rgba(0,0,0,0.52);
          margin: 0.0rem 0 0.35rem 0; letter-spacing: -0.5px;
        }
        .p5-titleline{
          height: 2px; width: 320px; border-radius: 999px;
          background: linear-gradient(90deg, var(--p5-accentA), var(--p5-accentB));
          box-shadow: 0 10px 26px rgba(0,0,0,0.32);
          margin-bottom: 0.75rem;
        }

        /* Top mini-nav */
        .p5-topnav div[data-testid="stButton"] > button{
          height: 52px !important;
          font-size: 15px !important;
          font-weight: 950 !important;
          border-radius: 14px !important;
          background: rgba(255,255,255,0.13) !important;
          border: 1px solid rgba(255,255,255,0.18) !important;
          color: var(--txt) !important;
          box-shadow: 0 10px 22px rgba(0,0,0,0.20) !important;
        }

        /* Side panel (RULE/TIMER) — navy glass + warm tint */
        .p5-panel{
          border-radius: 18px;
          padding: 10px 10px;
          background:
            radial-gradient(700px 280px at 50% 12%, var(--lane-timer-a), transparent 62%),
            linear-gradient(180deg, rgba(255,255,255,0.10), rgba(255,255,255,0.06));
          border: 1px solid rgba(255,255,255,0.16);
          box-shadow: 0 16px 36px rgba(0,0,0,0.26);
          backdrop-filter: blur(10px);
        }

        .p5-sidechip{
          display:inline-flex;
          justify-content:center;
          align-items:center;
          gap:8px;
          padding: 7px 10px;
          border-radius: 999px;
          border: 1px solid rgba(255,255,255,0.16);
          color: var(--txt);
          font-weight: 950;
          margin: 6px auto 8px auto;
          box-shadow: 0 10px 20px rgba(0,0,0,0.18);
          font-size: 13px;
        }
        .p5-chip-rule{ background: linear-gradient(90deg, var(--chip-rule-a), var(--chip-rule-b)); }
        .p5-chip-timer{ background: linear-gradient(90deg, var(--chip-timer-a), var(--chip-timer-b)); }

        .p5-briefbar{
          border-radius: 14px;
          padding: 10px 10px;
          background: rgba(255,255,255,0.13);
          border: 1px solid rgba(255,255,255,0.16);
          color: var(--txt);
          font-weight: 950;
          line-height: 1.18;
          font-size: 14px;
        }
        .p5-briefbar .mini{
          display:block;
          color: var(--muted);
          font-weight: 900;
          margin-top: 4px;
          font-size: 12px;
        }

        /* Timer buttons */
        .p5-timercol div[data-testid="stButton"] > button{
          min-height: 54px !important;
          font-size: 15px !important;
          font-weight: 1000 !important;
          border-radius: 16px !important;
          background: rgba(255,255,255,0.92) !important;
          color: #0b0e14 !important;
          border: 1px solid rgba(0,0,0,0.10) !important;
          box-shadow: 0 12px 22px rgba(0,0,0,0.18) !important;
        }
        .p5-selected{
          outline: 3px solid rgba(255,77,79,0.55);
          border-radius: 18px;
          box-shadow: 0 0 0 6px rgba(255,77,79,0.12);
          margin-bottom: 10px;
        }
        .p5-unselected{ margin-bottom: 10px; }

        /* Lanes (Grammar / Voca) */
        .p5-lane{
          border-radius: 18px;
          padding: 0px;
        }
        .p5-lane-gram{
          background:
            radial-gradient(900px 360px at 50% 10%, var(--lane-gram-a), transparent 62%),
            radial-gradient(900px 600px at 50% 100%, var(--lane-gram-b), transparent 72%);
          border-radius: 18px;
          padding: 10px 10px;
        }
        .p5-lane-voca{
          background:
            radial-gradient(900px 360px at 50% 10%, var(--lane-voca-a), transparent 62%),
            radial-gradient(900px 600px at 50% 100%, var(--lane-voca-b), transparent 72%);
          border-radius: 18px;
          padding: 10px 10px;
        }

        .p5-modecard{
          border-radius: 18px;
          padding: 18px 16px;
          background: rgba(255,255,255,0.13);
          border: 1px solid rgba(255,255,255,0.18);
          box-shadow: 0 16px 36px rgba(0,0,0,0.22);
          backdrop-filter: blur(10px);
        }
        .p5-modecard h4{ margin:0 0 6px 0; color: var(--txt); font-weight: 950; }
        .p5-modecard .tag{ color: var(--muted); font-weight: 850; }

        .p5-chip{
          display:inline-flex;
          justify-content:center;
          align-items:center;
          gap:8px;
          padding: 8px 12px;
          border-radius: 999px;
          background: linear-gradient(90deg, rgba(255,77,79,0.22), rgba(255,138,61,0.16));
          border: 1px solid rgba(255,255,255,0.20);
          color: var(--txt);
          font-weight: 950;
          margin: 12px auto 10px auto;
          box-shadow: 0 10px 22px rgba(0,0,0,0.18);
        }

        /* Choice buttons */
        .p5-gramgrid div[data-testid="stButton"] > button,
        .p5-vocagrid div[data-testid="stButton"] > button{
          min-height: 72px !important;
          font-size: 16px !important;
          font-weight: 1000 !important;
          border-radius: 16px !important;
          background: rgba(255,255,255,0.92) !important;
          color: #0b0e14 !important;
          border: 2px solid rgba(0,0,0,0.10) !important;
          box-shadow: 0 12px 22px rgba(0,0,0,0.16) !important;
          white-space: normal !important;
          line-height: 1.15 !important;
          padding-top: 10px !important;
          padding-bottom: 10px !important;
        }

        /* Current selection bar */
        .p5-currentbar{
          margin-top: 8px;
          padding: 8px 10px;
          border-radius: 12px;
          background: rgba(255,255,255,0.10);
          border: 1px solid rgba(255,255,255,0.14);
          color: rgba(255,255,255,0.92);
          font-weight: 900;
          font-size: 13px;
          line-height: 1.15;
          backdrop-filter: blur(10px);
        }
        .p5-currentbar .lbl{
          color: rgba(255,255,255,0.78);
          font-weight: 900;
          margin-right: 6px;
        }

        /* Expander (manual launch) */
        details{
          border: 1px solid rgba(255,255,255,0.14) !important;
          border-radius: 14px !important;
          background: rgba(255,255,255,0.07) !important;
          backdrop-filter: blur(10px);
        }
        details summary{
          color: rgba(255,255,255,0.82) !important;
          font-weight: 900 !important;
          padding: 8px 10px !important;
          font-size: 13px !important;
        }

        .p5-launch div[data-testid="stButton"] > button{
          min-height: 62px !important;
          font-size: 16px !important;
          font-weight: 1000 !important;
          border-radius: 16px !important;
          background: rgba(255,255,255,0.92) !important;
          color: #0b0e14 !important;
          border: 1px solid rgba(0,0,0,0.10) !important;
          box-shadow: 0 12px 22px rgba(0,0,0,0.16) !important;
        }

        @media (max-width: 768px){
          .p5-title{ font-size: 40px; }
          .p5-titleline{ width: 240px; }
          .p5-topnav div[data-testid="stButton"] > button{
            height: 48px !important; font-size: 14px !important;
          }
          .p5-gramgrid div[data-testid="stButton"] > button,
          .p5-vocagrid div[data-testid="stButton"] > button{
            min-height: 74px !important;
            font-size: 16px !important;
          }
          .p5-currentbar{
            font-size: 12.5px;
            padding: 7px 9px;
          }
          details summary{
            font-size: 12.5px !important;
            padding: 7px 9px !important;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_gate():
    ss = st.session_state
    _inject_gate_css()

    st.markdown('<div class="p5-titlewrap">', unsafe_allow_html=True)
    st.markdown('<div class="p5-title">💣 P5 Timebomb Arena</div>', unsafe_allow_html=True)
    st.markdown('<div class="p5-titleline"></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="p5-topnav">', unsafe_allow_html=True)
    n1, n2, n3 = st.columns(3, gap="medium")
    with n1:
        _nav_card("🏠 Main Hub", "main_hub.py", "p5_nav_hub")
    with n2:
        _nav_card("📊 Scoreboard", "pages/04_Scoreboard.py", "p5_nav_score")
    with n3:
        _nav_card("🗡 Secret Armory", "pages/03_Secret_Armory_Main.py", "p5_nav_armory")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

    ctrl, main = st.columns([0.60, 2.00], gap="large")

    with ctrl:
        st.markdown('<div class="p5-panel">', unsafe_allow_html=True)
        st.markdown('<div class="p5-sidechip p5-chip-rule">📌 RULE</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="p5-briefbar">
              🎯 5Q · ⏱ TIME<br/>
              <span class="mini">💣 3 FAIL = 💥</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

        st.markdown('<div class="p5-sidechip p5-chip-timer">⏱ TIMER</div>', unsafe_allow_html=True)
        st.markdown('<div class="p5-timercol">', unsafe_allow_html=True)

        def timer_button(sec: int, label: str, key: str):
            wrap = "p5-selected" if ss["p5_set_seconds"] == sec else "p5-unselected"
            st.markdown(f"<div class='{wrap}'>", unsafe_allow_html=True)
            if st.button(label, use_container_width=True, key=key):
                _set_timer(sec)
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        timer_button(40, "⚡ 40s", "p5_t40")
        timer_button(60, "✅ 60s", "p5_t60")
        timer_button(80, "🛡 80s", "p5_t80")

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with main:
        left, right = st.columns(2, gap="large")

        with left:
            st.markdown('<div class="p5-lane p5-lane-gram">', unsafe_allow_html=True)

            st.markdown(
                """
                <div class="p5-modecard">
                  <h4>🧠 어법 전장 (Grammar)</h4>
                  <div class="tag">“구조로 명중.”</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            ss.setdefault("p5_grammar_category", GRAM4[0])

            st.markdown('<div class="p5-chip">🎯 문법 분류 (4)</div>', unsafe_allow_html=True)

            st.markdown('<div class="p5-gramgrid">', unsafe_allow_html=True)
            g1, g2 = st.columns(2, gap="medium")
            with g1:
                if st.button(GRAM4[0], key="p5_g4_0", use_container_width=True):
                    ss["p5_grammar_category"] = GRAM4[0]
                    ss["p5_mode"] = "grammar"
                    ss["p5_stage"] = "battle"
                    st.rerun()
            with g2:
                if st.button(GRAM4[1], key="p5_g4_1", use_container_width=True):
                    ss["p5_grammar_category"] = GRAM4[1]
                    ss["p5_mode"] = "grammar"
                    ss["p5_stage"] = "battle"
                    st.rerun()
            g3, g4 = st.columns(2, gap="medium")
            with g3:
                if st.button(GRAM4[2], key="p5_g4_2", use_container_width=True):
                    ss["p5_grammar_category"] = GRAM4[2]
                    ss["p5_mode"] = "grammar"
                    ss["p5_stage"] = "battle"
                    st.rerun()
            with g4:
                if st.button(GRAM4[3], key="p5_g4_3", use_container_width=True):
                    ss["p5_grammar_category"] = GRAM4[3]
                    ss["p5_mode"] = "grammar"
                    ss["p5_stage"] = "battle"
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(
                f"""
                <div class="p5-currentbar">
                  <span class="lbl">현재 선택</span>
                  <span style="font-weight:1000;">{ss["p5_grammar_category"]}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander("🛡 수동 출격(옵션)", expanded=False):
                st.markdown('<div class="p5-launch">', unsafe_allow_html=True)
                if st.button("🔥 어법 전장 출격", use_container_width=True, key="p5_start_grammar"):
                    ss["p5_mode"] = "grammar"
                    ss["p5_stage"] = "battle"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        with right:
            st.markdown('<div class="p5-lane p5-lane-voca">', unsafe_allow_html=True)

            st.markdown(
                """
                <div class="p5-modecard">
                  <h4>🧩 어휘 전장 (VOCA)</h4>
                  <div class="tag">“바로 나와야 실력.”</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            ss.setdefault("p5_vocab_level", VOCA3[0])

            st.markdown('<div class="p5-chip">🎲 난이도 (3)</div>', unsafe_allow_html=True)

            st.markdown('<div class="p5-vocagrid">', unsafe_allow_html=True)
            v1, v2 = st.columns(2, gap="medium")
            with v1:
                if st.button(VOCA3[0], key="p5_v3_0", use_container_width=True):
                    ss["p5_vocab_level"] = VOCA3[0]
                    ss["p5_mode"] = "vocab"
                    ss["p5_stage"] = "battle"
                    st.rerun()
            with v2:
                if st.button(VOCA3[1], key="p5_v3_1", use_container_width=True):
                    ss["p5_vocab_level"] = VOCA3[1]
                    ss["p5_mode"] = "vocab"
                    ss["p5_stage"] = "battle"
                    st.rerun()
            if st.button(VOCA3[2], key="p5_v3_2", use_container_width=True):
                ss["p5_vocab_level"] = VOCA3[2]
                ss["p5_mode"] = "vocab"
                ss["p5_stage"] = "battle"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown(
                f"""
                <div class="p5-currentbar">
                  <span class="lbl">현재 선택</span>
                  <span style="font-weight:1000;">{ss["p5_vocab_level"]}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            with st.expander("🛡 수동 출격(옵션)", expanded=False):
                st.markdown('<div class="p5-launch">', unsafe_allow_html=True)
                if st.button("⚡ 어휘 전장 출격", use_container_width=True, key="p5_start_vocab"):
                    ss["p5_mode"] = "vocab"
                    ss["p5_stage"] = "battle"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)


def run():
    st.set_page_config(page_title="P5 Timebomb Arena", page_icon="💣", layout="wide")

    ss = st.session_state
    ss.setdefault("p5_stage", "lobby")
    ss.setdefault("p5_set_seconds", 40)
    ss.setdefault("p5_mode", "grammar")
    ss.setdefault("p5_grammar_category", GRAM4[0])
    ss.setdefault("p5_vocab_level", VOCA3[0])

    if ss.get("p5_stage") == "battle":
        p5_timebomb_arena.run()
        return

    _render_gate()


if __name__ == "__main__":
    run()
