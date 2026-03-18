# pages/01_P7_Reading_Arena.py
# ============================================================
# SNAPQ P7 READING ARENA (REBUILT / NO DRIFT) v1.0
# - Fixed HUD + fixed Gauge
# - Content area is ONLY scroll container
# - No page scroll, no drift
# - 3 steps, 4 choices, miss 3 => fail
# - 150s total timebomb (set-wide)
# ============================================================

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List

import streamlit as st

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    st_autorefresh = None


# -----------------------------
# DATA (임시 데모)
# -----------------------------
# ✅ 여기만 나중에 "실제 세트 로더"로 교체하면 됨.
@dataclass
class Step:
    passage: str
    question: str
    options: List[str]
    answer_idx: int


STEPS = [
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
        passage="Dear staff, ... relocated next month. Starting May 3, the team will move from the 5th floor to the 9th floor of the same building.",
        question="What will NOT change after the relocation?",
        options=[
            "The building where the team works",
            "The floor where the team works",
            "The team’s packing deadline",
            "The team’s meeting schedule",
        ],
        answer_idx=0,
    ),
    Step(
        passage="Dear staff, ... We appreciate your cooperation during this transition period.",
        question="What can be inferred about the relocation?",
        options=[
            "It will happen without any preparation",
            "Employees must handle all technical tasks alone",
            "Preparation and support are planned for the move",
            "The team will move to another city",
        ],
        answer_idx=2,
    ),
]


# -----------------------------
# STYLE (NO DRIFT)
# -----------------------------
def css():
    st.markdown(
        r"""
<style>
header[data-testid="stHeader"],
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
footer{display:none !important; height:0 !important; margin:0 !important; padding:0 !important;}

html, body{height:100% !important; margin:0 !important; padding:0 !important; overflow:hidden !important;}
div[data-testid="stAppViewContainer"] > section > main{
  height:100vh !important;
  overflow:hidden !important;
  padding-top:0 !important;
  margin-top:0 !important;
}
.block-container{
  height:100vh !important;
  overflow:hidden !important;
  padding:0 10px !important;
  margin:0 !important;
  max-width:100% !important;
}
*{overflow-anchor:none !important;}

:root{
  --hudH: 56px;
  --gaugeH: 10px;
}

.p7hud{
  position: fixed;
  top:0; left:0; right:0;
  height: var(--hudH);
  z-index: 999999;
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 8px;
  padding: 10px 12px;
  background: rgba(0,0,0,0.22);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255,255,255,0.10);
}

.p7chips{display:flex; gap:10px; flex-wrap:wrap; align-items:center;}
.p7chip{
  padding: 6px 10px; border-radius: 999px;
  background: rgba(255,255,255,0.10);
  border: 1px solid rgba(255,255,255,0.14);
  color:#fff; font-weight:900; font-size:13px;
}

.p7gauge{
  position: fixed;
  top: var(--hudH);
  left:0; right:0;
  height: var(--gaugeH);
  z-index: 999998;
  background: rgba(255,255,255,0.10);
}
.p7gauge .fill{
  height:100%;
  background: linear-gradient(90deg, rgba(34,211,238,0.95), rgba(167,139,250,0.90));
  width: 50%;
}

.p7content{
  position: relative;
  margin-top: calc(var(--hudH) + var(--gaugeH) + 8px);
  height: calc(100vh - (var(--hudH) + var(--gaugeH) + 8px));
  overflow-y: auto;
  overflow-x: hidden;
  padding-bottom: 18px;
}

.box{
  border-radius: 18px;
  padding: 14px 16px;
  margin: 10px 0;
  background: rgba(10,16,28,0.78);
  border: 1px solid rgba(34,211,238,0.22);
  box-shadow: 0 14px 34px rgba(0,0,0,0.25);
  color:#fff;
  font-weight:900;
  font-size:19px;
  line-height:1.6;
}
.box.q{ border-color: rgba(167,139,250,0.22); }

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
  font-weight:950 !important;
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


# -----------------------------
# STATE
# -----------------------------
def init():
    st.session_state.setdefault("p7_step", 1)
    st.session_state.setdefault("p7_miss", 0)
    st.session_state.setdefault("p7_combo", 0)
    st.session_state.setdefault("p7_started", False)
    st.session_state.setdefault("p7_t0", 0.0)
    st.session_state.setdefault("p7_limit", 150)
    st.session_state.setdefault("p7_done", False)

def reset():
    for k in ["p7_step","p7_miss","p7_combo","p7_started","p7_t0","p7_done"]:
        if k in st.session_state: del st.session_state[k]
    for k in list(st.session_state.keys()):
        if str(k).startswith("p7_choice_"): del st.session_state[k]
    init()

def mmss(sec:int)->str:
    sec=max(0,int(sec)); m,s=divmod(sec,60); return f"{m:02d}:{s:02d}"

def remaining()->int:
    if not st.session_state.get("p7_started"): return st.session_state["p7_limit"]
    t0=float(st.session_state["p7_t0"])
    lim=int(st.session_state["p7_limit"])
    return max(0, lim - int(time.time()-t0))

def hub():
    # 프로젝트마다 허브 파일명이 다를 수 있어 후보 2개
    for p in ["main_hub.py","pages/00_Main_Hub.py"]:
        try:
            st.switch_page(p)
            return
        except Exception:
            pass


# -----------------------------
# UI
# -----------------------------
def render_hud(rem:int):
    step=st.session_state["p7_step"]
    miss=st.session_state["p7_miss"]
    combo=st.session_state["p7_combo"]

    pct = rem / max(1,int(st.session_state["p7_limit"]))
    pct = max(0.0, min(1.0, pct))

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

    c1,c2,c3 = st.columns([6,2,2])
    with c2:
        if st.button("🏠 HUB", use_container_width=True, key="p7_hub"):
            hub()
    with c3:
        if st.button("🔄 RESET", use_container_width=True, key="p7_reset"):
            reset(); st.rerun()


def main():
    st.set_page_config(page_title="P7 Reading Arena (Rebuilt)", page_icon="🔥", layout="wide")
    css()
    init()

    # 1초 갱신(드리프트 없음: 본문이 고정 컨테이너)
    if st_autorefresh and st.session_state.get("p7_started") and not st.session_state.get("p7_done"):
        st_autorefresh(interval=1000, key="p7_tick")

    # 시작 전
    if not st.session_state.get("p7_started"):
        rem = remaining()
        render_hud(rem)
        st.markdown('<div class="p7content">', unsafe_allow_html=True)
        st.markdown('<div class="box">🔥 P7 READING ARENA (REBUILT)<br/>아래 Start로 전장 돌입</div>', unsafe_allow_html=True)
        if st.button("🚀 START", use_container_width=True, key="p7_start"):
            st.session_state["p7_started"]=True
            st.session_state["p7_t0"]=time.time()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # 진행 중
    rem = remaining()
    if rem <= 0:
        st.session_state["p7_done"]=True

    render_hud(rem)

    st.markdown('<div class="p7content">', unsafe_allow_html=True)

    if st.session_state.get("p7_done"):
        st.error("💥 TIME BOMB! (시간 종료)")
        if st.button("🔥 REMATCH", use_container_width=True):
            reset(); st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        return

    step_idx = st.session_state["p7_step"] - 1
    step = STEPS[step_idx]

    st.markdown(f'<div class="box">{step.passage}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="box q">{step.question}</div>', unsafe_allow_html=True)

    key=f"p7_choice_{st.session_state['p7_step']}"
    choice = st.radio("choose", step.options, index=None, key=key, label_visibility="collapsed")

    if choice is not None:
        picked = step.options.index(choice)
        if picked == step.answer_idx:
            st.session_state["p7_combo"] += 1
            if st.session_state["p7_step"] < 3:
                st.session_state["p7_step"] += 1
            else:
                st.success("✅ CLEAR!")
                st.session_state["p7_done"]=True
        else:
            st.session_state["p7_miss"] += 1
            st.session_state["p7_combo"] = 0
            if st.session_state["p7_miss"] >= 3:
                st.error("❌ FAILED (MISS 3)")
                st.session_state["p7_done"]=True

        st.session_state[key] = None
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


main()
