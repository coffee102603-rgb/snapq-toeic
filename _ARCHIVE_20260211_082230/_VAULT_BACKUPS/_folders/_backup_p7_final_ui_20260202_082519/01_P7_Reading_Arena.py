# pages/01_P7_Reading_Arena.py
# ============================================================
# SNAPQ P7 READING ARENA (FINAL STABLE) v1.1
# - HUD fixed + Gauge fixed
# - Content ALWAYS visible (no overflow/height clamp on main)
# - Drift reduction:
#    * overflow-anchor disabled
#    * soft main scrollTop reset each rerun (prevents gradual drift)
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
# CSS (safe: no overflow/height clamps on main)
# -----------------------------
def inject_css():
    st.markdown(
        r"""
<style>
header[data-testid="stHeader"],
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
footer{display:none !important; height:0 !important; margin:0 !important; padding:0 !important;}

div[data-testid="stAppViewContainer"] > section > main{
  padding-top:0 !important;
  margin-top:0 !important;
}
.block-container{
  max-width: 100% !important;
  padding-left: 10px !important;
  padding-right: 10px !important;
  margin-top: 0 !important;
}

/* Prevent "scroll anchoring" drift */
*{ overflow-anchor: none !important; }

:root{
  --hudH: 56px;
  --gaugeH: 10px;
}

/* Fixed HUD */
.p7hud{
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
}

.p7chips{display:flex; gap:10px; flex-wrap:wrap; align-items:center;}
.p7chip{
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.10);
  border: 1px solid rgba(255,255,255,0.14);
  color: #fff;
  font-weight: 900;
  font-size: 13px;
  line-height: 1;
  white-space: nowrap;
}

/* Fixed gauge */
.p7gauge{
  position: fixed;
  top: var(--hudH);
  left: 0; right: 0;
  height: var(--gaugeH);
  z-index: 999998;
  background: rgba(255,255,255,0.10);
}
.p7gauge .fill{
  height:100%;
  background: linear-gradient(90deg, rgba(34,211,238,0.95), rgba(167,139,250,0.90));
  width: 50%;
}

/* Content spacer (stable) */
.p7spacer{
  height: calc(var(--hudH) + var(--gaugeH) + 12px);
}

/* Cards */
.box{
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
}
.box.q{ border-color: rgba(167,139,250,0.22); }

/* Radio option cards */
.stRadio > label{display:none !important;}
div[role="radiogroup"] > label{
  width:100% !important;
  border-radius: 18px !important;
  border: 1px solid rgba(255,255,255,0.20) !important;
  background: rgba(255,255,255,0.96) !important;
  padding: 16px 16px !important;
  margin: 8px 0 !important;
  box-shadow: 0 14px 34px rgba(0,0,0,0.18) !important;
}
div[role="radiogroup"] > label *{
  color:#000 !important;
  -webkit-text-fill-color:#000 !important;
  font-weight: 950 !important;
}
div[role="radiogroup"] > label:has(input:checked){
  background: linear-gradient(135deg, rgba(34,211,238,0.92), rgba(167,139,250,0.88)) !important;
}
div[role="radiogroup"] > label:has(input:checked) *{
  color:#fff !important;
  -webkit-text-fill-color:#fff !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )


def badge():
    # ✅ 이 배지가 안 보이면, 다른 파일/다른 페이지를 보고 있는 겁니다.
    st.markdown(
        '<div style="position:fixed;top:6px;right:10px;z-index:1000000;'
        'padding:4px 10px;border-radius:999px;font-size:12px;font-weight:900;'
        'background:rgba(34,211,238,0.18);border:1px solid rgba(34,211,238,0.35);'
        'color:#ffffff;backdrop-filter: blur(10px);">'
        'P7 FINAL v1.1</div>',
        unsafe_allow_html=True,
    )


def soft_scroll_lock():
    """
    드리프트가 '조금씩 내려가는' 형태일 때, main 스크롤을 0으로 되돌려 누적을 차단.
    (완전 강제라기보다 main만 살짝 잡아줌)
    """
    components.html(
        """
<script>
(function(){
  try{
    const main = parent.document.querySelector('div[data-testid="stAppViewContainer"] > section > main');
    if(main){ main.scrollTop = 0; }
  }catch(e){}
})();
</script>
        """,
        height=0,
        width=0,
    )


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
    st.session_state.setdefault("p7_limit", 150)  # seconds
    st.session_state.setdefault("p7_t0", 0.0)


def reset_state():
    keep_limit = int(st.session_state.get("p7_limit", 150))
    for k in list(st.session_state.keys()):
        if str(k).startswith("p7_"):
            del st.session_state[k]
    st.session_state["p7_limit"] = keep_limit
    init_state()


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

    c1, c2, c3 = st.columns([6, 2, 2])
    with c2:
        if st.button("🏠 HUB", use_container_width=True, key="p7_hub"):
            hub_switch()
    with c3:
        if st.button("🔄 RESET", use_container_width=True, key="p7_reset"):
            reset_state()
            st.rerun()


def main():
    st.set_page_config(page_title="SnapQ P7 Reading Arena (Final Stable v1.1)", page_icon="🔥", layout="wide")
    init_state()

    inject_css()
    badge()
    soft_scroll_lock()

    # auto refresh (1s)
    if st_autorefresh and st.session_state.get("p7_started") and not st.session_state.get("p7_done"):
        st_autorefresh(interval=1000, key="p7_tick")

    rem = remaining()
    if rem <= 0:
        st.session_state["p7_done"] = True

    render_hud(rem)

    # spacer below fixed HUD
    st.markdown('<div class="p7spacer"></div>', unsafe_allow_html=True)

    # Start gate
    if not st.session_state.get("p7_started", False):
        st.markdown('<div class="box">🔥 P7 FINAL STABLE v1.1<br/>Start로 전장 돌입</div>', unsafe_allow_html=True)
        st.session_state["p7_limit"] = st.selectbox("⏱ 세트 제한시간(3문제 합산)", [120, 150, 180], index=1)
        if st.button("🚀 START", use_container_width=True, key="p7_start"):
            st.session_state["p7_started"] = True
            st.session_state["p7_t0"] = time.time()
            st.rerun()
        return

    # End state
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

    # Step content (stable Streamlit flow)
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
