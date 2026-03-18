# pages/01_P7_Reading_Arena.py
# ============================================================
# SNAPQ P7 READING ARENA (FINAL STABLE + GAME LOBBY) v1.2
# - SAFE: Full replacement file
# - Lobby (Fuse Setting): NO HUD/NO gauge, compact game-style speed selector
# - Battle: HUD fixed + Gauge fixed, HUB/RESET floating overlay (no space waste)
# - Goal: passage/question/options take ~90% of viewport
# ============================================================

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List

import streamlit as st
import streamlit.components.v1 as components

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    st_autorefresh = None


# -----------------------------
# DEMO DATA (나중에 여기만 실데이터로 교체)
# -----------------------------
@dataclass
class Step:
    passage: str
    question: str
    options: List[str]
    answer_idx: int


STEPS: List[Step] = [
    Step(
        passage="Dear staff, This is to inform you that our customer support team will be relocated next month.",
        question="What is the main purpose of this message?",
        options=[
            "To ask employees to work overtime this weekend",
            "To notify staff about a team relocation",
            "To announce a new product for customers",
            "To invite staff to a training workshop",
        ],
        answer_idx=1,
    ),
    Step(
        passage=(
            "Dear staff, This is to inform you that our customer support team will be relocated next month. "
            "Starting from May 3, the team will move from the 5th floor to the 9th floor of the same building."
        ),
        question="According to the notice, what will NOT change after the relocation?",
        options=[
            "The building where the team works",
            "The floor where the team works",
            "The team’s working hours",
            "The team’s manager",
        ],
        answer_idx=0,
    ),
    Step(
        passage=(
            "Dear staff, please pack your personal belongings by April 28. "
            "IT staff will assist you with moving your desktop computers. "
            "We appreciate your cooperation during this transition period."
        ),
        question="What can be inferred about the relocation?",
        options=[
            "It will happen without preparation",
            "Employees must do all technical tasks alone",
            "Preparation and support are planned for the move",
            "The team will move to another city",
        ],
        answer_idx=2,
    ),
]


# -----------------------------
# CSS
# -----------------------------
def inject_css(mode: str) -> None:
    """
    mode:
      - "lobby": HUD/게이지 숨김 (상단 회색바 제거)
      - "battle": HUD/게이지 표시 + 버튼 오버레이 + 본문 90% 확보
    """
    hud_display = "none" if mode == "lobby" else "block"
    gauge_display = "none" if mode == "lobby" else "block"

    st.markdown(
        f"""
<style>
/* Hide Streamlit chrome */
header[data-testid="stHeader"],
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
footer{{display:none !important; height:0 !important; margin:0 !important; padding:0 !important;}}

/* Prevent scroll anchoring drift */
*{{ overflow-anchor: none !important; }}

/* Full-width layout */
div[data-testid="stAppViewContainer"] > section > main{{ padding-top:0 !important; margin-top:0 !important; }}
.block-container{{
  max-width: 100% !important;
  padding-left: 10px !important;
  padding-right: 10px !important;
  margin-top: 0 !important;
}}

/* Game background */
.stApp{{
  background:
    radial-gradient(900px 650px at 18% 16%, rgba(34,211,238,0.22), transparent 60%),
    radial-gradient(900px 650px at 72% 14%, rgba(167,139,250,0.18), transparent 62%),
    radial-gradient(900px 900px at 50% 78%, rgba(56,189,248,0.10), transparent 70%),
    linear-gradient(180deg, #141C2B 0%, #0E1624 55%, #0B1020 100%) !important;
  color: #E5E7EB !important;
}}

/* HUD sizes */
:root{{
  --hudH: 56px;
  --gaugeH: 10px;
}}

/* HUD fixed */
.p7hud{{
  display: {hud_display};
  position: fixed;
  top: 0; left: 0; right: 0;
  height: var(--hudH);
  z-index: 999999;

  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 10px;

  padding: 10px 12px;
  background: rgba(0,0,0,0.22);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255,255,255,0.10);
}}

.p7chips{{display:flex; gap:10px; flex-wrap:wrap; align-items:center;}}
.p7chip{{
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.10);
  border: 1px solid rgba(255,255,255,0.14);
  color: #fff;
  font-weight: 900;
  font-size: 13px;
  line-height: 1;
  white-space: nowrap;
}}

/* Gauge fixed */
.p7gauge{{
  display: {gauge_display};
  position: fixed;
  top: var(--hudH);
  left: 0; right: 0;
  height: var(--gaugeH);
  z-index: 999998;
  background: rgba(255,255,255,0.10);
}}
.p7gauge .fill{{
  height:100%;
  background: linear-gradient(90deg, rgba(34,211,238,0.95), rgba(167,139,250,0.90));
  width: 50%;
}}

/* Spacer ONLY in battle */
.p7spacer{{
  height: calc(var(--hudH) + var(--gaugeH) + 10px);
  display: {("block" if mode == "battle" else "none")};
}}

/* Floating controls (HUB/RESET) - DOES NOT take layout space */
.p7-float-controls{{
  position: fixed;
  right: 12px;
  top: calc(var(--hudH) + 12px);
  z-index: 1000000;
  display:flex;
  gap: 10px;
}}
.p7-float-controls div[data-testid="stButton"] > button{{
  border-radius: 16px !important;
  padding: 10px 14px !important;
  font-weight: 950 !important;
  background: rgba(255,255,255,0.94) !important;
  border: 1px solid rgba(0,0,0,0.10) !important;
}}

/* Lobby card */
.p7-lobby-card{{
  border-radius: 20px;
  padding: 18px 18px;
  margin: 14px 0;
  background: rgba(10,16,28,0.72);
  border: 1px solid rgba(34,211,238,0.22);
  box-shadow: 0 14px 34px rgba(0,0,0,0.25);
}}
.p7-lobby-title{{
  font-size: 22px;
  font-weight: 1000;
  color: #fff;
  margin-bottom: 6px;
}}
.p7-lobby-sub{{
  font-size: 13px;
  font-weight: 850;
  color: rgba(255,255,255,0.78);
  margin-bottom: 14px;
}}

/* Radio cards for fuse setting */
.stRadio > label{{display:none !important;}}
div[role="radiogroup"] > label{{
  width:100% !important;
  border-radius: 18px !important;
  border: 1px solid rgba(255,255,255,0.18) !important;
  background: rgba(255,255,255,0.96) !important;
  padding: 14px 14px !important;
  margin: 8px 0 !important;
  box-shadow: 0 14px 34px rgba(0,0,0,0.18) !important;
}}
div[role="radiogroup"] > label *{{
  color:#000 !important;
  -webkit-text-fill-color:#000 !important;
  font-weight: 950 !important;
}}
div[role="radiogroup"] > label:has(input:checked){{
  background: linear-gradient(135deg, rgba(34,211,238,0.92), rgba(167,139,250,0.88)) !important;
}}
div[role="radiogroup"] > label:has(input:checked) *{{
  color:#fff !important;
  -webkit-text-fill-color:#fff !important;
}}

/* Passage / Question cards */
.box{{
  border-radius: 18px;
  padding: 14px 16px;
  margin: 10px 0;
  background: rgba(10,16,28,0.78);
  border: 1px solid rgba(34,211,238,0.22);
  box-shadow: 0 14px 34px rgba(0,0,0,0.25);
  color:#fff;
  font-weight: 900;
  font-size: 19px;
  line-height: 1.6;
}}
.box.q{{ border-color: rgba(167,139,250,0.22); }}

/* Options spacing tighter (maximize content) */
div[role="radiogroup"] > label{{ margin: 6px 0 !important; }}
</style>
        """,
        unsafe_allow_html=True,
    )


def gentle_top_lock():
    """
    드리프트가 '살짝씩 아래로 밀림' 형태일 때만 막기:
    - main.scrollTop이 60px 이하이면 0으로 보정
    - 사용자가 아래로 일부러 스크롤한 경우는 방해하지 않음
    """
    components.html(
        """
<script>
(function(){
  try{
    const main = parent.document.querySelector('div[data-testid="stAppViewContainer"] > section > main');
    if(!main) return;
    if(main.scrollTop <= 60){ main.scrollTop = 0; }
  }catch(e){}
})();
</script>
        """,
        height=0,
        width=0,
    )


# -----------------------------
# Navigation
# -----------------------------
def hub_switch():
    for p in ["main_hub.py", "pages/00_Main_Hub.py"]:
        try:
            st.switch_page(p)
            return
        except Exception:
            continue
    st.warning("Main Hub 페이지 경로를 찾지 못했습니다.")


# -----------------------------
# State
# -----------------------------
def init_state():
    st.session_state.setdefault("p7_started", False)
    st.session_state.setdefault("p7_done", False)
    st.session_state.setdefault("p7_step", 1)
    st.session_state.setdefault("p7_miss", 0)
    st.session_state.setdefault("p7_combo", 0)
    st.session_state.setdefault("p7_limit", 150)
    st.session_state.setdefault("p7_t0", 0.0)
    st.session_state.setdefault("p7_lobby_fuse", "STANDARD (150s)")


def reset_state():
    # keep last fuse
    keep = st.session_state.get("p7_lobby_fuse", "STANDARD (150s)")
    for k in list(st.session_state.keys()):
        if str(k).startswith("p7_"):
            del st.session_state[k]
    init_state()
    st.session_state["p7_lobby_fuse"] = keep


def mmss(sec: int) -> str:
    sec = max(0, int(sec))
    m, s = divmod(sec, 60)
    return f"{m:02d}:{s:02d}"


def remaining() -> int:
    if not st.session_state.get("p7_started", False):
        return int(st.session_state.get("p7_limit", 150))
    t0 = float(st.session_state.get("p7_t0", 0.0))
    lim = int(st.session_state.get("p7_limit", 150))
    if t0 <= 0:
        return lim
    return max(0, lim - int(time.time() - t0))


def fuse_to_seconds(label: str) -> int:
    if "FAST" in label:
        return 120
    if "ENDURANCE" in label:
        return 180
    return 150


# -----------------------------
# HUD / Controls
# -----------------------------
def render_hud(rem: int):
    step = int(st.session_state.get("p7_step", 1))
    miss = int(st.session_state.get("p7_miss", 0))
    combo = int(st.session_state.get("p7_combo", 0))
    lim = max(1, int(st.session_state.get("p7_limit", 150)))
    pct = max(0.0, min(1.0, rem / lim))

    st.markdown(
        f"""
<div class="p7hud">
  <div class="p7chips">
    <span class="p7chip">🔥 STEP <b>{step}</b>/3</span>
    <span class="p7chip">⏱ TIME <b>{mmss(rem)}</b></span>
    <span class="p7chip">❌ MISS <b>{miss}</b>/3</span>
    <span class="p7chip">💣 COMBO <b>{combo}</b></span>
  </div>
</div>
<div class="p7gauge"><div class="fill" style="width:{int(pct*100)}%"></div></div>
        """,
        unsafe_allow_html=True,
    )


def render_float_controls():
    # fixed overlay (no layout space)
    st.markdown('<div class="p7-float-controls">', unsafe_allow_html=True)
    b1, b2 = st.columns(2, gap="small")
    with b1:
        if st.button("🏠 HUB", key="p7_hub_float"):
            hub_switch()
    with b2:
        if st.button("🔄 RESET", key="p7_reset_float"):
            reset_state()
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# Main
# -----------------------------
def main():
    st.set_page_config(page_title="SnapQ P7 Reading (Final v1.2)", page_icon="🔥", layout="wide")
    init_state()

    # =======================
    # LOBBY (Fuse Setting)
    # =======================
    if not st.session_state.get("p7_started", False):
        inject_css(mode="lobby")
        gentle_top_lock()

        st.markdown(
            """
<div class="p7-lobby-card">
  <div class="p7-lobby-title">🧨 FUSE SETTING</div>
  <div class="p7-lobby-sub">전장 속도(=세트 제한시간)를 고르고 바로 돌입하세요. HUD는 전투 시작 후에만 뜹니다.</div>
</div>
            """,
            unsafe_allow_html=True,
        )

        fuse = st.radio(
            "fuse",
            options=[
                "FAST (120s)  ·  RUSH RAID",
                "STANDARD (150s)  ·  MAIN RUN",
                "ENDURANCE (180s)  ·  LONG SURVIVE",
            ],
            index=1,
            key="p7_lobby_fuse",
            label_visibility="collapsed",
        )

        # Start button
        if st.button("🚀 DROP IN (START)", use_container_width=True, key="p7_start"):
            st.session_state["p7_limit"] = fuse_to_seconds(fuse)
            st.session_state["p7_started"] = True
            st.session_state["p7_t0"] = time.time()
            st.rerun()

        return

    # =======================
    # BATTLE
    # =======================
    inject_css(mode="battle")
    gentle_top_lock()

    # timer tick
    if st_autorefresh and not st.session_state.get("p7_done", False):
        st_autorefresh(interval=1000, key="p7_tick")

    rem = remaining()
    if rem <= 0:
        st.session_state["p7_done"] = True

    render_hud(rem)
    render_float_controls()

    # spacer below fixed HUD/gauge
    st.markdown('<div class="p7spacer"></div>', unsafe_allow_html=True)

    # end state
    if st.session_state.get("p7_done", False):
        miss = int(st.session_state.get("p7_miss", 0))
        if rem <= 0:
            st.error("💥 TIME BOMB! (시간 종료)")
        elif miss >= 3:
            st.error("❌ FAILED (MISS 3)")
        else:
            st.success("✅ CLEAR!")

        b1, b2 = st.columns(2)
        with b1:
            if st.button("🔥 REMATCH", use_container_width=True):
                reset_state()
                st.session_state["p7_started"] = True
                st.session_state["p7_t0"] = time.time()
                st.rerun()
        with b2:
            if st.button("🏠 HUB로 복귀", use_container_width=True):
                hub_switch()
        return

    # step content (stable flow)
    step_idx = int(st.session_state.get("p7_step", 1)) - 1
    step_idx = max(0, min(2, step_idx))
    step = STEPS[step_idx]

    st.markdown(f'<div class="box">{step.passage}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="box q">{step.question}</div>', unsafe_allow_html=True)

    key = f"p7_choice_{st.session_state['p7_step']}"
    choice = st.radio("choose", step.options, index=None, key=key, label_visibility="collapsed")

    if choice is not None:
        picked = step.options.index(choice)
        if picked == step.answer_idx:
            st.session_state["p7_combo"] = int(st.session_state.get("p7_combo", 0)) + 1
            if int(st.session_state.get("p7_step", 1)) < 3:
                st.session_state["p7_step"] = int(st.session_state["p7_step"]) + 1
            else:
                st.session_state["p7_done"] = True
        else:
            st.session_state["p7_miss"] = int(st.session_state.get("p7_miss", 0)) + 1
            st.session_state["p7_combo"] = 0
            if int(st.session_state["p7_miss"]) >= 3:
                st.session_state["p7_done"] = True

        st.session_state[key] = None
        st.rerun()


main()
