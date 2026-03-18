from __future__ import annotations
import time
from dataclasses import dataclass
from typing import List
import streamlit as st

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    st_autorefresh = None

st.set_page_config(page_title="SnapQ P7 Reading Arena", layout="wide", initial_sidebar_state="collapsed")

# -----------------------------
# DATA (demo 3 steps)
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
            "The team's working hours",
            "The team's manager",
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
# STATE
# -----------------------------
def init_state():
    st.session_state.setdefault("p7_started", True)
    st.session_state.setdefault("p7_t0", time.time())
    st.session_state.setdefault("p7_limit", 150)  # seconds
    st.session_state.setdefault("p7_step", 1)
    st.session_state.setdefault("p7_miss", 0)
    st.session_state.setdefault("p7_combo", 0)
    st.session_state.setdefault("p7_done", False)
    st.session_state.setdefault("p7_nonce", 0)

def reset_battle():
    keep = int(st.session_state.get("p7_limit", 150))
    for k in list(st.session_state.keys()):
        if str(k).startswith("p7_"):
            del st.session_state[k]
    init_state()
    st.session_state["p7_limit"] = keep
    st.session_state["p7_t0"] = time.time()

def remaining() -> int:
    lim = int(st.session_state.p7_limit)
    t0 = float(st.session_state.p7_t0)
    return max(0, lim - int(time.time() - t0))

def mmss(sec:int)->str:
    m,s = divmod(max(0,int(sec)),60)
    return f"{m:02d}:{s:02d}"

init_state()
rem = remaining()

# Tick
if st_autorefresh and (not st.session_state.p7_done) and rem > 0:
    st_autorefresh(interval=1000, key="p7_tick")

pct = max(0.0, min(1.0, rem / max(1,int(st.session_state.p7_limit))))

# Monster stage triggers (wider so you feel it earlier)
stage = "p7-ok"
if rem <= 5:
    stage = "p7-5"
elif rem <= 10:
    stage = "p7-10"
elif rem <= 20:
    stage = "p7-20"
elif rem <= 30:
    stage = "p7-30"
elif rem <= 60:
    stage = "p7-60"

# Auto fail on time
if rem <= 0 and not st.session_state.p7_done:
    st.session_state.p7_done = True

# -----------------------------
# CSS (ALL INSIDE STRING)
# -----------------------------
st.markdown("""
<style>





/* ===== P7 TIMER v6 (VISIBLE ALWAYS + CRAZY <=60s) ===== */
@keyframes p7_alive {
  0%{transform:translateX(0)}
  25%{transform:translateX(-3px)}
  50%{transform:translateX(3px)}
  75%{transform:translateX(-3px)}
  100%{transform:translateX(0)}
}
@keyframes p7_crazy {
  0%{transform:translateX(0)}
  20%{transform:translateX(-5px)}
  40%{transform:translateX(5px)}
  60%{transform:translateX(-5px)}
  80%{transform:translateX(5px)}
  100%{transform:translateX(0)}
}
@keyframes p7_pulse {
  0%{filter:brightness(1); transform:scaleY(1)}
  50%{filter:brightness(1.45); transform:scaleY(1.55)}
  100%{filter:brightness(1); transform:scaleY(1)}
}

/* ALWAYS visible movement */
.p7-hud .p7-time{
  display:inline-block;
  animation:p7_alive 1.2s infinite;
  text-shadow: 0 0 10px rgba(167,139,250,0.35);
}

/* <=60s: CRAZY TIME */
.p7-hud.p7-60 .p7-time,
.p7-hud.p7-30 .p7-time,
.p7-hud.p7-20 .p7-time,
.p7-hud.p7-10 .p7-time,
.p7-hud.p7-5  .p7-time{
  animation:p7_crazy 0.12s infinite;
  text-shadow: 0 0 14px rgba(255,99,132,0.55);
}

/* <=60s: HEART BAR */
.p7-timer-wrap.p7-60 .p7-timer-bar,
.p7-timer-wrap.p7-30 .p7-timer-bar,
.p7-timer-wrap.p7-20 .p7-timer-bar,
.p7-timer-wrap.p7-10 .p7-timer-bar,
.p7-timer-wrap.p7-5  .p7-timer-bar{
  animation:p7_pulse 0.65s infinite;
  box-shadow: 0 0 24px rgba(255,99,132,0.55);
}
/* ===== P7 TIMER V5 (ALWAYS ALIVE + MONSTER <=60s) ===== */
@keyframes p7_float_soft {
  0%{transform:translateX(0)}
  25%{transform:translateX(-0.6px)}
  50%{transform:translateX(0.6px)}
  75%{transform:translateX(-0.6px)}
  100%{transform:translateX(0)}
}
@keyframes p7_shake_hard {
  0%{transform:translateX(0)}
  20%{transform:translateX(-2px)}
  40%{transform:translateX(2px)}
  60%{transform:translateX(-2px)}
  80%{transform:translateX(2px)}
  100%{transform:translateX(0)}
}
@keyframes p7_pulse_bar {
  0%{filter:brightness(1); transform:scaleY(1)}
  50%{filter:brightness(1.35); transform:scaleY(1.45)}
  100%{filter:brightness(1); transform:scaleY(1)}
}

/* TIME은 항상 '살짝 살아있게' */
.p7-hud .p7-time{
  display:inline-block;
  animation:p7_float_soft 1.6s infinite;
}

/* <=60s부터는 '마구마구' */
.p7-hud.p7-60 .p7-time,
.p7-hud.p7-30 .p7-time,
.p7-hud.p7-20 .p7-time,
.p7-hud.p7-10 .p7-time,
.p7-hud.p7-5  .p7-time{
  animation:p7_shake_hard 0.12s infinite;
}

/* 바 심장펄스: <=60s부터 */
.p7-60.p7-timer-wrap .p7-timer-bar,
.p7-30.p7-timer-wrap .p7-timer-bar,
.p7-20.p7-timer-wrap .p7-timer-bar,
.p7-10.p7-timer-wrap .p7-timer-bar,
.p7-5.p7-timer-wrap  .p7-timer-bar{
  animation:p7_pulse_bar 0.7s infinite;
  box-shadow:0 0 22px rgba(255,99,132,0.55);
}
html, body { margin:0 !important; padding:0 !important; }

/* Streamlit top gap killers (THIS is the real gap) */
div[data-testid="stAppViewContainer"],
div[data-testid="stAppViewContainer"] > section,
div[data-testid="stAppViewContainer"] > section > main,
div[data-testid="stAppViewContainer"] > section > main > div,
div[data-testid="stAppViewBlockContainer"],
section.main, section.main > div,
div.block-container{
  padding-top:0rem !important;
  margin-top:0rem !important;
}

/* Some themes add extra padding here */
main .block-container{
  padding-top:0rem !important;
  margin-top:0rem !important;
}
header[data-testid="stHeader"],
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
footer{display:none !important; height:0 !important; margin:0 !important; padding:0 !important;}

html, body{ margin:0 !important; padding:0 !important; }

/* Streamlit containers that often add top space */
div[data-testid="stAppViewContainer"],
div[data-testid="stAppViewContainer"] > section,
div[data-testid="stAppViewContainer"] > section > main,
div[data-testid="stAppViewContainer"] > section > main > div,
div[data-testid="stAppViewBlockContainer"],
section.main,
section.main > div,
div.block-container{
  padding-top:0rem !important;
  margin-top:0rem !important;
}
header[data-testid="stHeader"],
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
footer{display:none !important; height:0 !important; margin:0 !important; padding:0 !important;}

div[data-testid="stAppViewContainer"] > section > main,
div[data-testid="stAppViewContainer"] > section > main > div,
section.main > div,
div.block-container{
  padding-top:0rem !important;
  margin-top:0rem !important;
}
header[data-testid="stHeader"],
div[data-testid="stToolbar"],
div[data-testid="stDecoration"],
footer{display:none !important; height:0 !important; margin:0 !important; padding:0 !important;}
*{overflow-anchor:none !important;}

:root{ --hudH:46px; --barH:10px; }

.p7-hud{
  position:fixed; top:0; left:0; right:0;
  height:var(--hudH);
  z-index:999999;
  display:flex; align-items:center; gap:14px;
  padding:6px 12px;
  background:rgba(20,25,40,0.92);
  color:#fff; font-weight:900;
}

.p7-timer-wrap{
  position:fixed; top:var(--hudH); left:0; right:0;
  height:var(--barH);
  z-index:999998;
  background:rgba(255,255,255,0.10);
}

.p7-timer-bar{
  height:100%;
  width:60%;
  background:linear-gradient(90deg,#30cfd0,#8b5cf6);
  transition:width 0.25s linear;
}

/* Body right under HUD+bar */
.p7-body{
  margin-top:28px;
  padding:2px
}

/* Cards */
.p7-card{
  background:rgba(15,20,35,0.95);
  border-radius:18px;
  padding:16px 18px;
  margin:6px 0;
  color:#fff;
  box-shadow:0 0 0 1px rgba(255,255,255,0.05);
  font-weight:900;
}

/* Radio cards */
.stRadio > label{display:none !important;}
div[role="radiogroup"] > label{
  width:100% !important;
  border-radius:16px !important;
  border:1px solid rgba(255,255,255,0.18) !important;
  background: rgba(255,255,255,0.96) !important;
  padding:14px 14px !important;
  margin:6px 0 !important;
  box-shadow:0 10px 28px rgba(0,0,0,0.18) !important;
}
div[role="radiogroup"] > label *{
  color:#000 !important;
  -webkit-text-fill-color:#000 !important;
  font-weight:900 !important;
}
div[role="radiogroup"] > label:has(input:checked){
  background: linear-gradient(135deg, rgba(34,211,238,0.92), rgba(167,139,250,0.88)) !important;
}
div[role="radiogroup"] > label:has(input:checked) *{
  color:#fff !important;
  -webkit-text-fill-color:#fff !important;
}

/* ===== TIMER MONSTER MODE (stage on wrapper) ===== */
.p7-60 .p7-timer-wrap{ height:12px; }
.p7-60 .p7-timer-bar { animation:pulse_soft 1.6s infinite; transform:translateY(3px); box-shadow:0 10px 18px rgba(255,152,0,0.18); }

.p7-30 .p7-timer-wrap{ height:14px; }
.p7-30 .p7-timer-bar { animation:pulse_soft 1.2s infinite; transform:translateY(4px); box-shadow:0 12px 22px rgba(255,152,0,0.22); }

.p7-20 .p7-timer-wrap{ height:14px; }
.p7-20 .p7-timer-bar { background:linear-gradient(90deg,#ff9800,#ff5722); animation:shake_soft 0.9s infinite; transform:translateY(5px); box-shadow:0 14px 24px rgba(255,87,34,0.28); }

.p7-10 .p7-timer-wrap{ height:16px; }
.p7-10 .p7-timer-bar { background:linear-gradient(90deg,#ff1744,#ff5252); animation:shake_hard 0.45s infinite, pulse_hard 0.9s infinite; transform:translateY(6px); box-shadow:0 18px 34px rgba(255,23,68,0.35); }

.p7-5 .p7-timer-wrap{ height:18px; }
.p7-5 .p7-timer-bar { background:linear-gradient(90deg,#ff0000,#ff5252,#ff0000); animation:heartbeat 0.55s infinite; transform:translateY(7px); box-shadow:0 22px 40px rgba(255,0,0,0.45); }

/* Animations */
@keyframes pulse_soft{ 0%{filter:brightness(1)} 50%{filter:brightness(1.25)} 100%{filter:brightness(1)} }
@keyframes pulse_hard{ 0%{filter:brightness(1)} 50%{filter:brightness(1.5)} 100%{filter:brightness(1)} }
@keyframes shake_soft{ 0%{transform:translateY(5px) translateX(0)} 50%{transform:translateY(5px) translateX(1px)} 100%{transform:translateY(5px) translateX(0)} }
@keyframes shake_hard{ 0%{transform:translateY(6px) translateX(0)} 25%{transform:translateY(6px) translateX(-2px)} 50%{transform:translateY(6px) translateX(2px)} 100%{transform:translateY(6px) translateX(0)} }
@keyframes heartbeat{ 0%{transform:translateY(7px) scaleY(1)} 25%{transform:translateY(7px) scaleY(1.25)} 40%{transform:translateY(7px) scaleY(0.9)} 60%{transform:translateY(7px) scaleY(1.35)} 100%{transform:translateY(7px) scaleY(1)} }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# HUD + TIMER (apply stage class to BOTH wrap and body)
# -----------------------------
st.markdown(f"""
<div class="p7-hud {stage}">
  <span>STEP {st.session_state.p7_step}/3</span>
  <span class="p7-time">TIME {mmss(rem)}</span>
  <span>MISS {st.session_state.p7_miss}/3</span>
  <span>COMBO {st.session_state.p7_combo}</span>
</div>

<div class="p7-timer-wrap {stage}">
  <div class="p7-timer-bar" style="width:{int(pct*100)}%"></div>
</div>
""", unsafe_allow_html=True)

# -----------------------------
# BODY + OPTIONS
# -----------------------------
st.markdown(f'<div class="p7-body {stage}">', unsafe_allow_html=True)

if st.session_state.p7_done:
    st.error("TIME BOMB! (time ended)")
    if st.button("RESET"):
        reset_battle()
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

step_idx = st.session_state.p7_step - 1
step = STEPS[step_idx]

st.markdown(f'<div class="p7-card">{step.passage}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="p7-card">{step.question}</div>', unsafe_allow_html=True)

nonce = int(st.session_state.p7_nonce)
key = f"p7_choice_{st.session_state.p7_step}_{nonce}"
choice = st.radio("choose", step.options, index=None, key=key, label_visibility="collapsed")

if choice is not None:
    picked = step.options.index(choice)
    if picked == step.answer_idx:
        st.session_state.p7_combo += 1
        if st.session_state.p7_step < 3:
            st.session_state.p7_step += 1
        else:
            st.success("CLEAR!")
            st.session_state.p7_done = True
    else:
        st.session_state.p7_miss += 1
        st.session_state.p7_combo = 0
        if st.session_state.p7_miss >= 3:
            st.error("FAILED (MISS 3)")
            st.session_state.p7_done = True

    # reset widget safely by changing nonce
    st.session_state.p7_nonce = nonce + 1
    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)







