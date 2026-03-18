from __future__ import annotations
import time
from dataclasses import dataclass
from typing import List
import streamlit as st

try:
    import streamlit as st
    st.markdown(f'''
    <style>
      /* 화면 전체가 바뀌었는지 0.1초에 확인용 */
      .stApp {{
        outline: 8px solid rgba(255,0,200,0.75) !important;
        outline-offset: -8px !important;
      }}
      /* 상단 배너 */
      .p7-build-probe {{
        position: sticky; top: 0; z-index: 99999;
        padding: 10px 12px; margin: 6px 0 10px 0;
        border-radius: 14px;
        background: rgba(0,0,0,0.75);
        border: 3px solid rgba(0,255,120,0.95);
        color: #fff;
        font-weight: 900;
        letter-spacing: 0.5px;
      }}
    
/* ===== P7_OPTION_A_TUNE_V1 (TOP GAP + PADDING TUNE ONLY) ===== */
main .block-container{
  padding-top: 0.6rem !important;   /* 상단 빈공간 줄이기 */
  padding-bottom: 1.2rem !important;
}

/* 카드 내부 여백만 살짝 줄여서 '답답함' 제거 */
.p7-card{
  padding: 18px 18px !important;    /* 기존보다 살짝 */
}
.p7-q-title{
  padding: 12px 16px !important;
  margin-top: 10px !important;
}

/* 불필요한 실험 흔적(혹시 남아있으면 숨김) */
.p7-probe, .p7-build-tag{ display:none !important; }
/* ===== /P7_OPTION_A_TUNE_V1 ===== */
/* ===== P7_TEXT_SHRINK_PASSAGE_QUESTION_V1 ===== */
:root{{
  $125px;
  $128px;
  --p7-lh  : 1.45;
}}

.p7-card,
.p7-card *{{
  font-size: var(--p7-pass) !important;
  line-height: var(--p7-lh) !important;
}}

.p7-q-title,
.p7-q-title *{{
  font-size: var(--p7-qtit) !important;
  line-height: var(--p7-lh) !important;
}}

.p7-question, .p7-question *,
.p7-qtext, .p7-qtext *{{
  font-size: var(--p7-qtit) !important;
  line-height: var(--p7-lh) !important;
}}
/* ===== /P7_TEXT_SHRINK_PASSAGE_QUESTION_V1 ===== */</style>
    ''', unsafe_allow_html=True)
except Exception:
    pass
# --- P7_TEXT_TUNE_-15 (CSS ONLY) ---
st.markdown("""
<style>
/* P7_TEXT_TUNE_-15: Passage + Question only */

/* 지문 카드 */
.p7-card{
  font-size:0.85em !important;
  line-height:1.45 !important;
}

/* 문제 문장 */
.p7-question,
.p7-qtext,
.p7-question-card{
  font-size:0.85em !important;
  line-height:1.45 !important;
}
        
/* ===== P7_TEXT_FORCE_-15 (PASSAGE + QUESTION ONLY) ===== */
.p7-card, .p7-card *,
.p7-zone-body, .p7-zone-body *,
.p7-q-title, .p7-q-title *{
  font-size: 0.85em !important;
  line-height: 1.45 !important;
}
/* ===== /P7_TEXT_FORCE_-15 ===== */</style>
""", unsafe_allow_html=True)
# --- /P7_TEXT_TUNE_-15 ---
# P7_BUILD_BADGE_V5
import streamlit as st
try:
    import streamlit as st
    st.markdown(f'''
    <style>
      /* 화면 전체가 바뀌었는지 0.1초에 확인용 */
      .stApp {{
        outline: 8px solid rgba(255,0,200,0.75) !important;
        outline-offset: -8px !important;
      }}
      /* 상단 배너 */
      .p7-build-probe {{
        position: sticky; top: 0; z-index: 99999;
        padding: 10px 12px; margin: 6px 0 10px 0;
        border-radius: 14px;
        background: rgba(0,0,0,0.75);
        border: 3px solid rgba(0,255,120,0.95);
        color: #fff;
        font-weight: 900;
        letter-spacing: 0.5px;
      }}
    </style>
    ''', unsafe_allow_html=True)
except Exception:
    pass
st.caption('🧩 BUILD: P7_PATCH_V5__20260205_155452 | PAGE=' + __file__)

# SNAPQ_BUILD_BADGE__ (do not remove)
try:
    import streamlit as st
    st.caption('🧩 BUILD: P7_PATCH_V4__20260205_155007 | PAGE=' + __file__)
except Exception:
    pass

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    st_autorefresh = None

st.set_page_config(page_title="SnapQ P7 Reading Arena", layout="wide", initial_sidebar_state="collapsed")

# === P7_GLOBAL_FONT_FORCE_32PX_v3 (AUTO INSERT) ===
try:
    import streamlit as st
    st.markdown("""
<style>
/* ===== P7_GLOBAL_FONT_FORCE_32PX_v3 (DO NOT MOVE) =====
   Goal: Passage / Question / Options = EXACT SAME SIZE
   Tune: 35px -> 32px (about -10%)
====================================================== */

.p7-card, .p7-card * ,
.p7-zone-body, .p7-zone-body * ,
.p7-q-title, .p7-q-title * ,
[data-testid="stMarkdownContainer"] * ,
div[role="radiogroup"] label,
div[role="radiogroup"] label * ,
label[data-baseweb="radio"],
label[data-baseweb="radio"] * ,
.stRadio label, .stRadio label * {
  font-size: 32px !important;
  font-weight: 900 !important;
}

/* line-height */
.p7-card, .p7-zone-body { line-height: 1.55 !important; }
div[role="radiogroup"] label { line-height: 1.20 !important; }

/* ===== /P7_GLOBAL_FONT_FORCE_32PX_v3 ===== */
</style>
""", unsafe_allow_html=True)
except Exception:
    pass
# === /P7_GLOBAL_FONT_FORCE_32PX_v3 ===


# === P7_FONT_FORCE_35PX_v1 (AUTO INSERT) ===
try:
    import streamlit as st
    st.markdown(r"""
<style>
/* ===== P7_FONT_FORCE_35PX_v1 (DO NOT MOVE) =====
   Goal: Passage / Question / Options font = 35px, bold
   Inserted as python st.markdown => safest method
================================================= */
.p7-body, .p7-zone { --p7-font: 35px; }

/* P7 영역 안 텍스트를 최대한 넓게 잡는다 */
.p7-body [data-testid="stMarkdownContainer"] *,
.p7-zone [data-testid="stMarkdownContainer"] *,
.p7-body .p7-card, .p7-body .p7-card *,
.p7-zone .p7-zone-body, .p7-zone .p7-zone-body *,
.p7-body .p7-q-title, .p7-body .p7-q-title *,
.p7-zone .p7-q-title, .p7-zone .p7-q-title *,
.p7-body div[role="radiogroup"] label,
.p7-body div[role="radiogroup"] label *,
.p7-zone div[role="radiogroup"] label,
.p7-zone div[role="radiogroup"] label *,
label[data-baseweb="radio"], label[data-baseweb="radio"] *,
.stRadio label, .stRadio label * {
  font-size: var(--p7-font) !important;
  font-weight: 900 !important;
}

/* 줄간격: 지문은 넉넉, 선택지는 컴팩트 */
.p7-body .p7-card, .p7-zone .p7-zone-body { line-height: 1.55 !important; }
.p7-body div[role="radiogroup"] label, .p7-zone div[role="radiogroup"] label { line-height: 1.20 !important; }
/* ===== /P7_FONT_FORCE_35PX_v1 ===== */
</style>
""", unsafe_allow_html=True)
except Exception:
    pass
# === /P7_FONT_FORCE_35PX_v1 ===


# -----------------------------
# DATA (demo 3 steps)
# -----------------------------
@dataclass
class Step:
    passage: str
    question: str
    options: List[str]
    answer_idx: int

# -----------------------------
# CUMULATIVE PASSAGE (2→5→8) ✅ LOGIC ONLY
# -----------------------------
P7_FULL_SENTENCES_EN = [
    "Dear staff, This is to inform you that our customer support team will be relocated next month.",
    "Starting from May 3, the team will move from the 5th floor to the 9th floor of the same building.",
    "The new workspace will include additional meeting areas for faster coordination.",
    "Employees will receive updated access instructions for the 9th floor before the move.",
    "Further details will be shared in a follow-up notice next week.",
    "Dear staff, please pack your personal belongings by April 28.",
    "IT staff will assist you with moving your desktop computers.",
    "We appreciate your cooperation during this transition period.",
]

def build_cumulative_passage(step_num: int) -> str:
    n = 2 if step_num == 1 else (5 if step_num == 2 else 8)
    return " ".join(P7_FULL_SENTENCES_EN[:n])

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








/* ===== P7 ARENA FONT x1.2 FIX v2 (NO LAYOUT / NO TIMER) ===== */

/* Strong base: apply to this page's main container */
section.main > div,
div.block-container{
  font-size: 120% !important;
}

/* Readability */
div[data-testid="stMarkdownContainer"] p,
div[data-testid="stMarkdownContainer"] li{
  line-height: 1.56 !important;
  letter-spacing: 0.10px !important;
}

/* Options/labels: ensure they scale too */
div[role="radiogroup"] > label span{
  font-size: 1.05em !important; /* scales with 120% base */
  font-weight: 850 !important;
}
/* ===== P7 ARENA FONT+COLOR v1 (NO LAYOUT / NO TIMER) ===== */
:root{
  --p7-accent-cyan: rgba(0,229,255,0.95);
  --p7-accent-blue: rgba(27,124,255,0.95);
  --p7-glow: rgba(56,189,248,0.18);
}

/* (1) Font size up x1.2 — scope to body contents only */
.p7-body{
  font-size: 120% !important; /* 핵심: 1.2배 */
}

/* (2) Make reading text + question a touch sharper (still safe) */
.p7-body div[data-testid="stMarkdownContainer"] p,
.p7-body div[data-testid="stMarkdownContainer"] li{
  line-height: 1.55;
  letter-spacing: 0.1px;
}

/* (3) Option/radio labels: slightly bigger + more "game button" feel */
.p7-body div[role="radiogroup"] > label{
  border-color: rgba(148,163,184,0.18) !important;
  box-shadow: 0 0 0 1px rgba(56,189,248,0.06) !important;
}
.p7-body div[role="radiogroup"] > label:hover{
  border-color: rgba(0,229,255,0.35) !important;
  box-shadow: 0 0 0 1px rgba(0,229,255,0.10), 0 10px 28px rgba(0,0,0,0.22) !important;
}
.p7-body div[role="radiogroup"] > label:has(input:checked){
  border-color: rgba(0,229,255,0.55) !important;
  box-shadow: 0 0 0 1px rgba(0,229,255,0.16), 0 12px 34px rgba(0,0,0,0.28) !important;
}

/* (4) Subtle cyan/blue highlight strip for "P7 theme consistency" (safe) */
.p7-body .p7-card,
.p7-body .p7-qcard,
.p7-body .p7-panel{
  box-shadow: 0 0 18px var(--p7-glow);
}
/* ===== P7 BAR HEARTBEAT (LOW-LOGIC, HIGH-TENSION) ===== */

/* baseline thickness: 조금 더 굵게 */
.p7-timer-wrap{
  margin-bottom: 6px !important; /* 바-지문 사이 여백 살짝 줄이기 */
}
.p7-timer-track{
  height: 12px !important;       /* 트랙 자체를 굵게 */
  border-radius: 999px !important;
  overflow: hidden !important;
}

/* bar: 스트라이프 + 호흡(약) */
@keyframes p7_bar_stripes {
  0%   { background-position: 0 0; }
  100% { background-position: 160px 0; }
}
@keyframes p7_bar_breath {
  0%   { transform: scaleY(1.00); filter: brightness(1.02); }
  50%  { transform: scaleY(1.22); filter: brightness(1.18); }
  100% { transform: scaleY(1.00); filter: brightness(1.02); }
}

/* 기본 상태(>60초): 약하게 살아있게 */
.p7-timer-bar{
  transform-origin: center;
  border-radius: 999px !important;

  /* 움직이는 줄무늬 + 그라데이션 */
  background-image:
    linear-gradient(90deg, rgba(99,102,241,0.95), rgba(167,139,250,0.95)),
    repeating-linear-gradient(45deg,
      rgba(255,255,255,0.18) 0px,
      rgba(255,255,255,0.18) 8px,
      rgba(255,255,255,0.00) 8px,
      rgba(255,255,255,0.00) 16px
    );
  background-blend-mode: overlay;
  background-size: 100% 100%, 180px 100%;
  background-position: 0 0, 0 0;

  /* 기본 애니메이션: 줄무늬 흐름 + 약한 호흡 */
  animation: p7_bar_stripes 1.6s linear infinite, p7_bar_breath 1.35s ease-in-out infinite;
  box-shadow: 0 0 18px rgba(167,139,250,0.35);
}

/* <=60초: 더 빠르고 더 크게 (심장 쫄림) */
@keyframes p7_bar_heart {
  0%   { transform: scaleY(1.05); filter: brightness(1.10); }
  35%  { transform: scaleY(1.55); filter: brightness(1.45); }
  70%  { transform: scaleY(1.15); filter: brightness(1.18); }
  100% { transform: scaleY(1.05); filter: brightness(1.10); }
}

/* stage 클래스는 이미 p7-60/p7-30/p7-10/p7-5로 들어오고 있음 */
.p7-timer-wrap.p7-60 .p7-timer-bar{
  animation: p7_bar_stripes 0.85s linear infinite, p7_bar_heart 0.60s ease-in-out infinite;
  background-image:
    linear-gradient(90deg, rgba(255,99,132,0.95), rgba(255,159,64,0.95)),
    repeating-linear-gradient(45deg,
      rgba(255,255,255,0.22) 0px,
      rgba(255,255,255,0.22) 8px,
      rgba(255,255,255,0.00) 8px,
      rgba(255,255,255,0.00) 16px
    );
  box-shadow: 0 0 26px rgba(255,99,132,0.45);
}

/* <=30초: 더 미친 속도 */
.p7-timer-wrap.p7-30 .p7-timer-bar{
  animation: p7_bar_stripes 0.55s linear infinite, p7_bar_heart 0.42s ease-in-out infinite;
}

/* <=10초 / <=5초: 최종 폭탄 */
.p7-timer-wrap.p7-10 .p7-timer-bar{
  animation: p7_bar_stripes 0.40s linear infinite, p7_bar_heart 0.33s ease-in-out infinite;
}
.p7-timer-wrap.p7-5 .p7-timer-bar{
  animation: p7_bar_stripes 0.28s linear infinite, p7_bar_heart 0.26s ease-in-out infinite;
}
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

/* ===== P7 ARENA FINAL VISUAL v1 (NO TIMER / NO LAYOUT) ===== */

/* Strong base font scaling: apply to main content container */
section.main, section.main > div, div.block-container{
  font-size: 120% !important;
}

/* Make HUD text clearly visible */
.p7-hud, .p7-hud *{
  color: rgba(255,255,255,0.98) !important;
  font-weight: 950 !important;
  text-shadow: 0 2px 14px rgba(0,0,0,0.45) !important;
  letter-spacing: 0.35px !important;
}

/* Reading / question / option text: stronger */
div[data-testid="stMarkdownContainer"] p,
div[data-testid="stMarkdownContainer"] li{
  line-height: 1.58 !important;
  letter-spacing: 0.10px !important;
  font-weight: 750 !important;
  color: rgba(226,232,240,0.96) !important;
}

/* Options: bold + readable */
div[role="radiogroup"] > label span{
  font-size: 1.05em !important; /* scales with 120% base */
  font-weight: 900 !important;
  color: rgba(15,23,42,0.92) !important; /* 선택지 카드 위 텍스트는 어두운 글씨가 더 선명 */
}

/* Theme accent: subtle cyan/blue glow on main cards (safe) */
:root{
  --p7-cyan: rgba(0,229,255,0.95);
  --p7-blue: rgba(27,124,255,0.95);
  --p7-glow: rgba(56,189,248,0.16);
}
.p7-body .p7-card,
.p7-body .p7-qcard{
  box-shadow: 0 0 20px var(--p7-glow) !important;
}

/* ===== P7 ARENA CLEAN COLOR + FONT x1.2 (LOCK) ===== */

/* 0) Font: 무조건 1.2배 (구조 영향 없음) */
.p7-body{
  font-size: 120% !important;
}

/* HUD 텍스트: 깔끔하게 흰색 + 굵게 */
.p7-hud, .p7-hud *{
  color: rgba(255,255,255,0.98) !important;
  font-weight: 950 !important;
  letter-spacing: 0.35px !important;
  text-shadow: 0 2px 12px rgba(0,0,0,0.45) !important;
}

/* 1) PASSAGE(지문) 카드: 조금 더 밝은 네이비 */
.p7-body .p7-card{
  background: rgba(15, 23, 42, 0.94) !important;      /* slate/navy */
  border: 1px solid rgba(148,163,184,0.14) !important;
  box-shadow: 0 0 0 1px rgba(255,255,255,0.04) !important;
  color: rgba(255,255,255,0.98) !important;
  font-weight: 900 !important;
  line-height: 1.58 !important;
}

/* 2) QUESTION(문제) 카드: 더 어둡게 + 상단 얇은 스트립 */
.p7-body .p7-card + .p7-card{
  background: rgba(2, 6, 23, 0.92) !important;        /* deeper */
  border: 1px solid rgba(0,229,255,0.18) !important;
  box-shadow: 0 0 18px rgba(56,189,248,0.12) !important;
  position: relative;
}
.p7-body .p7-card + .p7-card::before{
  content:"";
  position:absolute; left:14px; right:14px; top:10px; height:2px;
  background: linear-gradient(90deg, rgba(0,229,255,0.80), rgba(27,124,255,0.85));
  opacity: 0.85;
  border-radius: 99px;
}

/* 3) OPTIONS(선택지): 밝게 유지하되 톤 통일 + 구분감 */
.p7-body div[role="radiogroup"] > label{
  border: 1px solid rgba(148,163,184,0.26) !important;
  background: rgba(255,255,255,0.98) !important;
  box-shadow: 0 10px 26px rgba(0,0,0,0.14) !important;
}
.p7-body div[role="radiogroup"] > label *{
  color: rgba(2,6,23,0.92) !important; /* 읽기 좋게 진한 글씨 */
  -webkit-text-fill-color: rgba(2,6,23,0.92) !important;
  font-weight: 900 !important;
}

/* 선택지 글자 크기도 확실히 */
.p7-body div[role="radiogroup"] > label span{
  font-size: 1.05em !important;
}

/* 선택지 hover/selected: 너무 과하지 않게, ‘깔끔한 전장’ */
.p7-body div[role="radiogroup"] > label:hover{
  border-color: rgba(0,229,255,0.35) !important;
  box-shadow: 0 0 0 1px rgba(0,229,255,0.10), 0 12px 30px rgba(0,0,0,0.18) !important;
}
.p7-body div[role="radiogroup"] > label:has(input:checked){
  border-color: rgba(0,229,255,0.65) !important;
  box-shadow: 0 0 0 2px rgba(0,229,255,0.12), 0 14px 36px rgba(0,0,0,0.22) !important;
}

/* ===== P7 ARENA VERIFY + FORCE v1 ===== */

/* (A) DIAG WATERMARK: top-right tiny tag (CSS only, no layout change) */
body::after{
  content:"P7_ARENA_PATCHED_v1";
  position: fixed;
  top: 6px;
  right: 10px;
  z-index: 999999;
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.6px;
  color: rgba(0,229,255,0.85);
  text-shadow: 0 2px 10px rgba(0,0,0,0.55);
  pointer-events: none;
}

/* (B) FORCE FONT x1.2 : strongest scope */
html, body, section.main, section.main *{
  font-size: 100%;
}
.p7-body, .p7-body *{
  font-size: 120% !important;
}

/* (C) PASSAGE / QUESTION separation (NO structure change) */
.p7-body .p7-card{
  background: rgba(15,23,42,0.94) !important;
  border: 1px solid rgba(148,163,184,0.16) !important;
  color: rgba(255,255,255,0.98) !important;
  font-weight: 900 !important;
}
.p7-body .p7-card + .p7-card{
  background: rgba(2,6,23,0.92) !important;
  border: 1px solid rgba(0,229,255,0.22) !important;
  box-shadow: 0 0 20px rgba(56,189,248,0.12) !important;
  position: relative;
}
.p7-body .p7-card + .p7-card::before{
  content:"";
  position:absolute; left:14px; right:14px; top:10px; height:2px;
  background: linear-gradient(90deg, rgba(0,229,255,0.85), rgba(27,124,255,0.85));
  opacity: 0.9;
  border-radius: 999px;
}

/* (D) OPTIONS readable */
.p7-body div[role="radiogroup"] > label{
  background: rgba(255,255,255,0.98) !important;
  border: 1px solid rgba(148,163,184,0.26) !important;
  box-shadow: 0 10px 26px rgba(0,0,0,0.14) !important;
}
.p7-body div[role="radiogroup"] > label *{
  color: rgba(2,6,23,0.92) !important;
  -webkit-text-fill-color: rgba(2,6,23,0.92) !important;
  font-weight: 900 !important;
}

/* ===== P7 ARENA STREAMLIT TARGET v2 (FONT 1.25 + CLEAN) ===== */

/* 0) Base scale (p7-body only) */
.p7-body, .p7-body *{
  font-size: 125% !important;   /* <-- 핵심: 무조건 1.25배 */
}

/* 1) HUD: white + very bold (readable) */
.p7-hud, .p7-hud *{
  color: rgba(255,255,255,0.98) !important;
  font-weight: 950 !important;
  letter-spacing: 0.35px !important;
  text-shadow: 0 2px 14px rgba(0,0,0,0.45) !important;
}

/* 2) PASSAGE / QUESTION: Streamlit markdown blocks inside p7-body
      - 첫 번째 stMarkdown = 지문
      - 두 번째 stMarkdown = 문제
   (구조 변경 없이 nth-of-type으로만 구분)
*/
.p7-body div[data-testid="stMarkdown"]:nth-of-type(1){
  background: rgba(15,23,42,0.94) !important;
  border: 1px solid rgba(148,163,184,0.16) !important;
  border-radius: 22px !important;
  padding: 18px 18px 18px 18px !important;
  box-shadow: 0 0 0 1px rgba(255,255,255,0.04) !important;
}
.p7-body div[data-testid="stMarkdown"]:nth-of-type(1) *{
  color: rgba(255,255,255,0.98) !important;
  font-weight: 900 !important;
  line-height: 1.58 !important;
}

/* QUESTION block */
.p7-body div[data-testid="stMarkdown"]:nth-of-type(2){
  background: rgba(2,6,23,0.92) !important;
  border: 1px solid rgba(0,229,255,0.22) !important;
  border-radius: 22px !important;
  padding: 18px 18px 18px 18px !important;
  box-shadow: 0 0 18px rgba(56,189,248,0.12) !important;
  position: relative !important;
}
.p7-body div[data-testid="stMarkdown"]:nth-of-type(2)::before{
  content:"";
  position:absolute; left:18px; right:18px; top:12px; height:2px;
  background: linear-gradient(90deg, rgba(0,229,255,0.85), rgba(27,124,255,0.85));
  opacity: 0.9;
  border-radius: 999px;
}
.p7-body div[data-testid="stMarkdown"]:nth-of-type(2) *{
  color: rgba(255,255,255,0.98) !important;
  font-weight: 950 !important;
  line-height: 1.55 !important;
}

/* 3) OPTIONS: radio group labels -> clean white card + bold dark text */
.p7-body div[role="radiogroup"] > label{
  background: rgba(255,255,255,0.98) !important;
  border: 1px solid rgba(148,163,184,0.28) !important;
  border-radius: 18px !important;
  box-shadow: 0 12px 28px rgba(0,0,0,0.14) !important;
}
.p7-body div[role="radiogroup"] > label *{
  color: rgba(2,6,23,0.92) !important;
  -webkit-text-fill-color: rgba(2,6,23,0.92) !important;
  font-weight: 900 !important;
}

/* Hover / Selected: 깔끔한 강조 (과하지 않게) */
.p7-body div[role="radiogroup"] > label:hover{
  border-color: rgba(0,229,255,0.38) !important;
  box-shadow: 0 0 0 1px rgba(0,229,255,0.10), 0 14px 34px rgba(0,0,0,0.18) !important;
}
.p7-body div[role="radiogroup"] > label:has(input:checked){
  border-color: rgba(0,229,255,0.75) !important;
  box-shadow: 0 0 0 2px rgba(0,229,255,0.12), 0 16px 38px rgba(0,0,0,0.22) !important;
}

/* 4) spacing safety: keep structure (no layout change), just tighten readability */
.p7-body div[data-testid="stMarkdown"]{ margin-bottom: 14px !important; }

/* ===== P7 FINAL OVERRIDE v3 (GUARANTEED) ===== */

/* 1) FONT: 실제로 보이는 텍스트들을 강제로 키운다 (체감 100%) */
.p7-body{
  font-size: 125% !important;
}

/* Streamlit markdown / labels are often fixed-size -> override directly */
.p7-body p,
.p7-body li,
.p7-body span,
.p7-body label,
.p7-body div[data-testid="stMarkdownContainer"] *{
  font-size: 1.08em !important;   /* 125% * 1.08 = 확실히 커짐 */
  font-weight: 850 !important;
  line-height: 1.58 !important;
}

/* 2) PASSAGE / QUESTION / OPTIONS "분리"는 과하지 않게 톤으로만 */
.p7-body div[data-testid="stMarkdownContainer"]{
  border-radius: 22px !important;
  padding: 18px 18px 18px 18px !important;
  margin-bottom: 14px !important;
}

/* Passage 느낌(조금 밝은 네이비) */
.p7-body div[data-testid="stMarkdownContainer"]{
  background: rgba(15,23,42,0.94) !important;
  border: 1px solid rgba(148,163,184,0.16) !important;
  box-shadow: 0 0 0 1px rgba(255,255,255,0.04) !important;
  color: rgba(255,255,255,0.98) !important;
}

/* Question 느낌: 질문 텍스트는 보통 짧고 굵음 → 컨테이너 위에 얇은 스트립만 추가 */
.p7-body div[data-testid="stMarkdownContainer"]::before{
  content:"";
  display:block;
  height:2px;
  width:100%;
  margin-bottom:10px;
  background: linear-gradient(90deg, rgba(0,229,255,0.80), rgba(27,124,255,0.85));
  opacity:0.35;                 /* 기본은 약하게(깔끔) */
  border-radius: 999px;
}

/* 3) OPTIONS: 밝은 카드 + 진한 글씨(구분감) */
.p7-body div[role="radiogroup"] > label{
  background: rgba(255,255,255,0.985) !important;
  border: 1px solid rgba(148,163,184,0.28) !important;
  border-radius: 18px !important;
  box-shadow: 0 12px 28px rgba(0,0,0,0.14) !important;
}
.p7-body div[role="radiogroup"] > label *{
  color: rgba(2,6,23,0.92) !important;
  -webkit-text-fill-color: rgba(2,6,23,0.92) !important;
  font-weight: 900 !important;
}

/* 4) HUD 텍스트는 더 선명하게 */
.p7-hud, .p7-hud *{
  color: rgba(255,255,255,0.98) !important;
  font-weight: 950 !important;
  text-shadow: 0 2px 14px rgba(0,0,0,0.45) !important;
}

/* 5) 선택 강조는 깔끔하게 */
.p7-body div[role="radiogroup"] > label:hover{
  border-color: rgba(0,229,255,0.38) !important;
  box-shadow: 0 0 0 1px rgba(0,229,255,0.10), 0 14px 34px rgba(0,0,0,0.18) !important;
}
.p7-body div[role="radiogroup"] > label:has(input:checked){
  border-color: rgba(0,229,255,0.78) !important;
  box-shadow: 0 0 0 2px rgba(0,229,255,0.12), 0 16px 38px rgba(0,0,0,0.22) !important;
}

/* ===== P7 ARENA BATTLE THEME v1 (PC-BANG) ===== */

/* 0) global tokens */
:root{
  --p7-bgA: rgba(6, 12, 24, 0.96);
  --p7-bgB: rgba(15, 23, 42, 0.94);
  --p7-bgC: rgba(2, 6, 23, 0.94);

  --p7-cyan: rgba(0,229,255,0.92);
  --p7-blue: rgba(27,124,255,0.92);
  --p7-glow: rgba(56,189,248,0.18);
  --p7-line: rgba(148,163,184,0.14);

  --p7-text: rgba(255,255,255,0.96);
  --p7-sub: rgba(226,232,240,0.86);
}

/* 1) FONT: 무조건 1.2배 (전장만) */
.p7-body, .p7-body *{
  font-size: 120% !important;
}

/* 2) HUD: 전장 텍스트 가독성 MAX (타이머 로직/구조 무변경) */
.p7-hud, .p7-hud *{
  color: var(--p7-text) !important;
  font-weight: 950 !important;
  letter-spacing: 0.35px !important;
  text-shadow: 0 2px 14px rgba(0,0,0,0.45) !important;
}

/* 3) PASSAGE / QUESTION: Streamlit markdown container를 패널화
   - 구조 변경 없이 스타일만
*/
.p7-body div[data-testid="stMarkdownContainer"]{
  border-radius: 22px !important;
  padding: 18px 18px 18px 18px !important;
  margin-bottom: 14px !important;
  border: 1px solid var(--p7-line) !important;
}

/* 기본(지문): navy */
.p7-body div[data-testid="stMarkdownContainer"]{
  background: linear-gradient(180deg, var(--p7-bgB), var(--p7-bgC)) !important;
  box-shadow: 0 0 0 1px rgba(255,255,255,0.03) !important;
}

/* 지문 텍스트 */
.p7-body div[data-testid="stMarkdownContainer"] p,
.p7-body div[data-testid="stMarkdownContainer"] li{
  color: var(--p7-text) !important;
  font-weight: 900 !important;
  line-height: 1.58 !important;
}

/* 문제(질문): 보통 두 번째 markdown이 질문이므로, 더 어둡게 + 네온 스트립 */
.p7-body div[data-testid="stMarkdownContainer"]:nth-of-type(2){
  background: linear-gradient(180deg, rgba(2,6,23,0.98), rgba(2,6,23,0.90)) !important;
  border-color: rgba(0,229,255,0.20) !important;
  box-shadow: 0 0 22px var(--p7-glow) !important;
  position: relative !important;
}
.p7-body div[data-testid="stMarkdownContainer"]:nth-of-type(2)::before{
  content:"";
  position:absolute; left:18px; right:18px; top:12px; height:2px;
  background: linear-gradient(90deg, var(--p7-cyan), var(--p7-blue));
  opacity: 0.90;
  border-radius: 999px;
}

/* 4) OPTIONS: white 카드 → 전장형 다크 카드로 전환 */
.p7-body div[role="radiogroup"] > label{
  background: linear-gradient(180deg, rgba(15,23,42,0.92), rgba(2,6,23,0.96)) !important;
  border: 1px solid rgba(148,163,184,0.22) !important;
  border-radius: 18px !important;
  box-shadow: 0 14px 32px rgba(0,0,0,0.22) !important;
  overflow: hidden !important;
}

/* 선택지 텍스트: 흰색/굵게 */
.p7-body div[role="radiogroup"] > label *{
  color: rgba(255,255,255,0.94) !important;
  -webkit-text-fill-color: rgba(255,255,255,0.94) !important;
  font-weight: 900 !important;
}

/* 선택지 위쪽 얇은 네온 라인(게임 버튼 느낌) */
.p7-body div[role="radiogroup"] > label::before{
  content:"";
  position:absolute; left:14px; right:14px; top:10px; height:2px;
  background: linear-gradient(90deg, rgba(0,229,255,0.55), rgba(27,124,255,0.55));
  opacity: 0.55;
  border-radius: 999px;
}

/* Hover: 더 또렷하게 */
.p7-body div[role="radiogroup"] > label:hover{
  border-color: rgba(0,229,255,0.38) !important;
  box-shadow: 0 0 0 1px rgba(0,229,255,0.10), 0 16px 38px rgba(0,0,0,0.28) !important;
  transform: translateY(-1px);
}

/* Selected: 네온 강조 (임팩트) */
.p7-body div[role="radiogroup"] > label:has(input:checked){
  border-color: rgba(0,229,255,0.78) !important;
  box-shadow: 0 0 0 2px rgba(0,229,255,0.12), 0 18px 44px rgba(0,0,0,0.34) !important;
}

/* 5) (선택) 워터마크 숨김: 디버그 글씨만 안 보이게 (코드 삭제 아님) */
body::after{ display:none !important; }
/* ===== P7_TEXT_ONLY_X12_BOLD_FINAL ===== */
/* Scope strictly to P7 BODY + options only (NO HUD, NO layout) */

/* (1) Passage + Question (both are .p7-card) : text only */
.p7-body .p7-card,
.p7-body .p7-card p,
.p7-body .p7-card span,
.p7-body .p7-card li,
.p7-body .p7-card strong,
.p7-body .p7-card em,
.p7-body .p7-card div[data-testid="stMarkdownContainer"] p,
.p7-body .p7-card div[data-testid="stMarkdownContainer"] span{
  font-size: 1.2em !important;      /* +20% */
  font-weight: 900 !important;      /* thicker */
  -webkit-text-stroke: 0px transparent !important;
}

/* (2) Options (radio cards) : text only */
.p7-body div[role="radiogroup"] > label *,
.p7-body div[role="radiogroup"] > label p,
.p7-body div[role="radiogroup"] > label span,
.p7-body div[role="radiogroup"] > label strong,
.p7-body div[role="radiogroup"] > label em,
.p7-body div[role="radiogroup"] > label div[data-testid="stMarkdownContainer"] p,
.p7-body div[role="radiogroup"] > label div[data-testid="stMarkdownContainer"] span{
  font-size: 1.2em !important;      /* +20% */
  font-weight: 900 !important;      /* thicker */
}

/* Safety: do NOT scale HUD */
.p7-hud, .p7-hud *{
  font-size: inherit !important;
}
/* ===== /P7_TEXT_ONLY_X12_BOLD_FINAL ===== */
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

st.markdown(f'<div class="p7-card">{build_cumulative_passage(st.session_state.p7_step)}</div>', unsafe_allow_html=True)
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






















# ===== P7_FORCE_TEXT_X12_BOLD (DO NOT EDIT) =====
try:
    import streamlit as st
    st.markdown(r'''<style>
/* ===== P7_FORCE_TEXT_X12_BOLD_CSS ===== */
/* Passage / Question (p7-zone body text) */
.p7-pack .p7-zone .p7-zone-body{
  font-size: 26px !important;   /* ~18px * 1.2 = 21.6 -> 22px */
  font-weight: 900 !important;
}

/* Some variants may use mission zone */
.p7-pack .p7-zone.mission .p7-zone-body{
  font-size: 31px !important;
  font-weight: 900 !important;
}

/* Options (radio style) */
.p7-pack div[role="radiogroup"] > label,
.p7-pack div[role="radiogroup"] > label *{
  font-size: 26px !important;   /* ~16px * 1.2 = 19.2 -> 19px */
  font-weight: 900 !important;
}

/* Options (button style fallback, if ever used) */
.p7-pack .p7-opt-wrap div[data-testid="stButton"] > button,
.p7-pack .p7-opt-wrap div[data-testid="stButton"] > button *{
  font-size: 26px !important;
  font-weight: 900 !important;
}

/* HUD는 절대 건드리지 않음(보호막) */
.p7-pack .p7-hud,
.p7-pack .p7-hud *{
  font-size: inherit !important;
  font-weight: inherit !important;
}
/* ===== /P7_FORCE_TEXT_X12_BOLD_CSS ===== */
</style>''', unsafe_allow_html=True)
except Exception:
    pass
# ===== /P7_FORCE_TEXT_X12_BOLD =====

# ===== P7_TEXT_FORCE_X1P2_V3 (CSS ONLY / LAST WINS) =====
try:
    import streamlit as st
    st.markdown(r"""
    <style>
    /* === P7_TEXT_FORCE_X1P2_V3 === */
    /* 1) Passage + Question text only */
    .p7-zone .p7-zone-body,
    .p7-zone .p7-zone-body p,
    .p7-zone .p7-zone-body span,
    .p7-zone .p7-zone-body strong,
    .p7-zone .p7-zone-body em{
      font-size: 26px !important;   /* 18px * 1.2 ~= 21.6px -> 22px */
      font-weight: 900 !important;  /* thicker */
    }

    /* 2) Options (radio) text only - scoped to p7-opt-wrap to avoid other radios */
    .p7-opt-wrap div[role="radiogroup"] > label{
      font-size: 1em !important;    /* reset base to prevent double scaling */
      font-weight: 400 !important;  /* label itself normal */
    }

    .p7-opt-wrap div[role="radiogroup"] > label p,
    .p7-opt-wrap div[role="radiogroup"] > label span,
    .p7-opt-wrap div[role="radiogroup"] > label strong,
    .p7-opt-wrap div[role="radiogroup"] > label em,
    .p7-opt-wrap div[role="radiogroup"] > label [data-testid="stMarkdownContainer"] p,
    .p7-opt-wrap div[role="radiogroup"] > label [data-testid="stMarkdownContainer"] span{
      font-size: 1.2em !important;  /* +20% exactly once */
      font-weight: 900 !important;  /* thicker */
    }

    /* (If options are buttons in some modes) */
    .p7-opt-wrap div[data-testid="stButton"] > button,
    .p7-opt-wrap div[data-testid="stButton"] > button *{
      font-size: 1.2em !important;
      font-weight: 900 !important;
    }
    /* === /P7_TEXT_FORCE_X1P2_V3 === */
    /* ===== P7_TEXT_FORCE_V3_X1P2 (TEXT ONLY) ===== */
/* Passage text */
.p7-zone .p7-zone-body{
  font-size: 26px !important;
  font-weight: 800 !important;
}
.p7-zone .p7-zone-body p,
.p7-zone .p7-zone-body span,
.p7-zone .p7-zone-body strong,
.p7-zone .p7-zone-body em{
  font-size: 26px !important;
  font-weight: 800 !important;
}

/* Question text (title area inside zone) */
.p7-zone .p7-q-title,
.p7-zone .p7-q-title *{
  font-size: 26px !important;
  font-weight: 900 !important;
}

/* Options text (radio) */
.p7-zone div[role="radiogroup"] label,
.p7-zone div[role="radiogroup"] label *{
  font-size: 26px !important;
  font-weight: 900 !important;
}

/* Options text (button type, if any) */
.p7-opt-wrap div[data-testid="stButton"] > button,
.p7-opt-wrap div[data-testid="stButton"] > button *{
  font-size: 26px !important;
  font-weight: 900 !important;
}
/* ===== /P7_TEXT_FORCE_V3_X1P2 ===== */
/* ===== P7_TEXT_FORCE_FINAL (BIGGER) ===== */
/* Passage */
.p7-zone .p7-zone-body,
.p7-zone .p7-zone-body *{
  font-size: 30px !important;
  line-height: 1.65 !important;
  font-weight: 900 !important;
}
/* Question */
.p7-q-title,
.p7-q-title *{
  font-size: 28px !important;
  line-height: 1.55 !important;
  font-weight: 900 !important;
}
/* Options */
.p7-zone div[role="radiogroup"] label,
.p7-zone div[role="radiogroup"] label *{
  font-size: 26px !important;
  font-weight: 900 !important;
}
/* ===== /P7_TEXT_FORCE_FINAL ===== */
/* ===== P7_TEXT_FORCE_FINAL_OVERRIDE (DO NOT EDIT) ===== */
.p7-zone-body,
.p7-zone-body *{
  font-size: 30px !important;
  line-height: 1.65 !important;
  font-weight: 900 !important;
}
div[role="radiogroup"] > label,
div[role="radiogroup"] > label *{
  font-size: 26px !important;
  font-weight: 900 !important;
}
/* ===== /P7_TEXT_FORCE_FINAL_OVERRIDE ===== */
/* ===== P7_TEXT_FORCE_FINAL_UNIFIED_v3 ===== */
/* PASSAGE + QUESTION + OPTIONS -> SAME SIZE */
.p7-zone .p7-zone-body,
.p7-zone .p7-zone-body *{
  font-size: 30px !important;
  line-height: 1.65 !important;
  font-weight: 900 !important;
}
.p7-q-title,
.p7-q-title *{
  font-size: 30px !important;
  line-height: 1.55 !important;
  font-weight: 900 !important;
}
.p7-zone div[role="radiogroup"] > label{
  padding: 10px 12px !important;
  margin: 10px 0 !important;
  min-height: 52px !important;
}
.p7-zone div[role="radiogroup"] > label,
.p7-zone div[role="radiogroup"] > label *{
  font-size: 30px !important;
  font-weight: 900 !important;
  line-height: 1.25 !important;
}
/* ===== /P7_TEXT_FORCE_FINAL_UNIFIED_v3 ===== */
/* ===== P7_TEXT_FORCE_FINAL_UNIFIED_V4 ===== */
/* PASSAGE + QUESTION + OPTIONS -> SAME SIZE + FLAT CARDS */
.p7-zone .p7-zone-body,
.p7-zone .p7-zone-body *{
  font-size: 30px !important;
  line-height: 1.65 !important;
  font-weight: 900 !important;
}
.p7-q-title,
.p7-q-title *{
  font-size: 30px !important;
  line-height: 1.55 !important;
  font-weight: 900 !important;
}
.p7-zone div[role="radiogroup"] > label{
  padding: 8px 12px !important;
  margin: 8px 0 !important;
  min-height: 46px !important;
}
.p7-zone div[role="radiogroup"] > label,
.p7-zone div[role="radiogroup"] > label *{
  font-size: 30px !important;
  font-weight: 900 !important;
  line-height: 1.20 !important;
}
/* ===== /P7_TEXT_FORCE_FINAL_UNIFIED_V4 ===== */
/* ===== P7_TEXT_FORCE_FINAL_UNIFIED_V5 ===== */
/* PASSAGE + QUESTION + OPTIONS : SAME SIZE (폰에서 안 작게) */
.p7-zone .p7-zone-body,
.p7-zone .p7-zone-body *{
  font-size: 30px !important;
  line-height: 1.65 !important;
  font-weight: 900 !important;
}
.p7-q-title,
.p7-q-title *{
  font-size: 30px !important;
  line-height: 1.55 !important;
  font-weight: 900 !important;
}
/* OPTION cards: flatter (space saver) */
.p7-zone div[role="radiogroup"] > label{
  padding: 6px 12px !important;
  margin: 8px 0 !important;
  min-height: 40px !important;
  border-radius: 16px !important;
}
.p7-zone div[role="radiogroup"] > label,
.p7-zone div[role="radiogroup"] > label *{
  font-size: 30px !important;
  font-weight: 900 !important;
  line-height: 1.15 !important;
}
/* ===== /P7_TEXT_FORCE_FINAL_UNIFIED_V5 ===== */


/* ===== P7_TEXT_UNIFY_PLUS15_v2 (DO NOT MOVE) =====
   Goal: Passage + Question + Options = SAME SIZE (+15%)
================================================== */
.p7-body .p7-card,
.p7-body .p7-card *,
.p7-body .p7-q-title,
.p7-body .p7-q-title *,
.p7-body [data-testid="stMarkdownContainer"] *,
.p7-body div[role="radiogroup"] label,
.p7-body div[role="radiogroup"] label *,

.p7-zone .p7-zone-body,
.p7-zone .p7-zone-body *,
.p7-zone .p7-q-title,
.p7-zone .p7-q-title *,
.p7-zone [data-testid="stMarkdownContainer"] *,
.p7-zone div[role="radiogroup"] label,
.p7-zone div[role="radiogroup"] label *,

/* streamlit/baseweb radio 안전 타겟 */
label[data-baseweb="radio"],
label[data-baseweb="radio"] *{
  font-size: 35px !important;
  font-weight: 900 !important;
}

.p7-body .p7-card,
.p7-zone .p7-zone-body{
  line-height: 1.55 !important;
}

.p7-body div[role="radiogroup"] label,
.p7-zone div[role="radiogroup"] label{
  line-height: 1.20 !important;
}
/* ===== /P7_TEXT_UNIFY_PLUS15_v2 ===== */


/* ===== P7_TEXT_UNIFY_PLUS15_ONESHOT_v1 (DO NOT MOVE) =====
   Goal: Passage + Question + Options = SAME SIZE (+15%)
   Base: ~30px * 1.15 = 35px
================================= */
.p7-body,
.p7-zone{
  --p7-font: 35px;
}

/* 가장 안전한 타겟: P7 컨테이너 안의 마크다운/라디오/라벨 전체 */
.p7-body [data-testid="stMarkdownContainer"] *,
.p7-zone [data-testid="stMarkdownContainer"] *,
.p7-body div[role="radiogroup"] label,
.p7-body div[role="radiogroup"] label *,
.p7-zone div[role="radiogroup"] label,
.p7-zone div[role="radiogroup"] label *,
label[data-baseweb="radio"],
label[data-baseweb="radio"] *{
  font-size: var(--p7-font) !important;
  font-weight: 900 !important;
}

/* 카드/지문 영역 */
.p7-body .p7-card,
.p7-body .p7-card *,
.p7-zone .p7-zone-body,
.p7-zone .p7-zone-body *{
  font-size: var(--p7-font) !important;
  font-weight: 900 !important;
  line-height: 1.55 !important;
}

/* 문제(질문) */
.p7-body .p7-q-title,
.p7-body .p7-q-title *,
.p7-zone .p7-q-title,
.p7-zone .p7-q-title *{
  font-size: var(--p7-font) !important;
  font-weight: 900 !important;
}

/* 선택지: 줄간격만 약간 컴팩트 */
.p7-body div[role="radiogroup"] label,
.p7-zone div[role="radiogroup"] label{
  line-height: 1.20 !important;
}
/* ===== /P7_TEXT_UNIFY_PLUS15_ONESHOT_v1 ===== */

/* ===== P7_TEXT_UNIFY_PLUS15_FINAL_v1 (DO NOT MOVE) =====
   Goal: Passage + Question + Options = SAME SIZE
   Base: current passage size +15%  -> fixed to 35px (strong override)
================================== */
.p7-body, .p7-zone { --p7-font: 35px; }

/* 가장 넓게 잡는 안전 타겟: P7 영역 안 텍스트 전부 */
.p7-body [data-testid="stMarkdownContainer"] *,
.p7-zone [data-testid="stMarkdownContainer"] *,
.p7-body .p7-card, .p7-body .p7-card *,
.p7-zone .p7-zone-body, .p7-zone .p7-zone-body *,
.p7-body .p7-q-title, .p7-body .p7-q-title *,
.p7-zone .p7-q-title, .p7-zone .p7-q-title *,
.p7-body div[role="radiogroup"] label,
.p7-body div[role="radiogroup"] label *,
.p7-zone div[role="radiogroup"] label,
.p7-zone div[role="radiogroup"] label *,
/* streamlit radio fallback */
.stRadio label, .stRadio label * {
  font-size: var(--p7-font) !important;
  font-weight: 900 !important;
}

/* 줄간격: 지문은 넉넉, 선택지는 컴팩트 */
.p7-body .p7-card, .p7-zone .p7-zone-body { line-height: 1.55 !important; }
.p7-body div[role="radiogroup"] label, .p7-zone div[role="radiogroup"] label { line-height: 1.20 !important; }

/* ===== /P7_TEXT_UNIFY_PLUS15_FINAL_v1 ===== */
</style>
    """, unsafe_allow_html=True)
except Exception:
    pass
# ===== /P7_TEXT_FORCE_X1P2_V3 =====








# === P7_FINAL_TUNE_FONT32_GAPCUT_v1 (AUTO APPEND / LAST WINS) ===
try:
    import streamlit as st
    st.markdown(r"""
<style>
/* ===== P7_FINAL_TUNE_FONT32_GAPCUT_v1 =====
   1) Font: Passage / Question / Options = EXACT SAME (32px, bold)
   2) Top gap: reduce whitespace above first card
   3) Safety: only CSS override (no session / logic touch)
======================================== */

/* (A) 전체 상단 여백(스트림릿 기본 padding) 최소화 */
.stAppViewContainer .main .block-container{
  padding-top: .25rem !important;
  padding-bottom: 0rem !important;
}

/* (B) 블록 간 기본 간격(gap) 줄이기 */
div[data-testid="stVerticalBlock"]{
  gap: .35rem !important;
}

/* (C) BUILD/DEBUG caption이 공간 먹으면 숨김(원하면 주석처리 가능) */
[data-testid="stCaptionContainer"],
[data-testid="stCaption"]{
  display:none !important;
  margin:0 !important;
  padding:0 !important;
}

/* (D) P7 컨텐츠를 위로 당김 (과하게 당기면 - 값 줄이기) */
.p7-pack, .p7-body, .p7-zone{
  margin-top: 0px !important;
}

/* (E) ✅ “지문/문제/선택지” 폰트 크기 완전 통일 */
.p7-pack { --p7-font: 32px; } /* 35px에서 약 10% down */

/* 지문/문제 카드(마크다운/HTML 포함) */
.p7-pack .p7-card,
.p7-pack .p7-card *,

/* 지문/문제 body 영역 */
.p7-pack .p7-zone-body,
.p7-pack .p7-zone-body *,

/* 라디오 선택지(라벨/내부 텍스트) */
.p7-pack div[role="radiogroup"] label,
.p7-pack div[role="radiogroup"] label *,

/* baseweb fallback */
.p7-pack label[data-baseweb="radio"],
.p7-pack label[data-baseweb="radio"] *,

/* streamlit radio fallback */
.p7-pack .stRadio label,
.p7-pack .stRadio label *{
  font-size: var(--p7-font) !important;
  font-weight: 900 !important;
}

/* 줄간격: 지문은 조금 넉넉, 선택지는 살짝 컴팩트 */
.p7-pack .p7-card, .p7-pack .p7-zone-body{ line-height: 1.275 !important; }
.p7-pack div[role="radiogroup"] label{ line-height: 1.20 !important; }

/* HUD는 보호(건드리지 않음) */
.p7-pack .p7-hud, .p7-pack .p7-hud *{
  font-size: inherit !important;
  font-weight: inherit !important;
}

/* ===== /P7_FINAL_TUNE_FONT32_GAPCUT_v1 ===== */
</style>
""", unsafe_allow_html=True)
except Exception:
    pass
# === /P7_FINAL_TUNE_FONT32_GAPCUT_v1 ===


# === P7_OPTION_SLIM_PACK_v1 (AUTO APPEND / LAST WINS) ===
try:
    import streamlit as st
    st.markdown(r"""
<style>
/* ===== P7_OPTION_SLIM_PACK_v1 =====
   Keep font size SAME.
   Only reduce option card height/padding/margins to save space.
======================================== */

/* 1) 선택지(라디오) 전체 래퍼 간격 줄이기 */
.p7-pack div[role="radiogroup"]{
  margin-top: .10rem !important;
  margin-bottom: .10rem !important;
}

/* 2) 각 선택지 "카드"를 더 얇게 (padding/height/spacing) */
.p7-pack div[role="radiogroup"] label{
  padding-top: .35rem !important;
  padding-bottom: .35rem !important;
  margin-top: .20rem !important;
  margin-bottom: .20rem !important;
  border-radius: 14px !important;
}

/* 3) 라디오 원/텍스트 정렬이 붕 뜨면 중앙정렬 */
.p7-pack div[role="radiogroup"] label{
  display: flex !important;
  align-items: center !important;
}

/* 4) 라디오 원과 텍스트 사이 간격 약간 줄이기 */
.p7-pack div[role="radiogroup"] label > div{
  margin-right: .55rem !important;
}

/* 5) 선택지 내부 텍스트 줄간격 약간 더 컴팩트 (폰트는 건드리지 않음) */
.p7-pack div[role="radiogroup"] label{
  line-height: 1.10 !important;
}

/* 6) 맨 아래 여백도 조금 절약 */
.p7-pack{
  padding-bottom: .25rem !important;
}
</style>
""", unsafe_allow_html=True)
except Exception:
    pass
# === /P7_OPTION_SLIM_PACK_v1 ===


# === P7_PASSAGE_COMPACT_v1 (AUTO APPEND / LAST WINS) ===
try:
    import streamlit as st
    st.markdown(r"""
<style>
/* ===== P7_PASSAGE_COMPACT_v1 =====
   Goal: Save vertical space above/between passage & question
   IMPORTANT: DO NOT change font-size (only spacing)
======================================== */

/* 카드(지문/문제) 자체 위아래 패딩 줄이기 */
.p7-pack .p7-card{
  padding-top: .70rem !important;
  padding-bottom: .70rem !important;
}

/* 지문/문제 텍스트 줄간격 살짝 압축 (너무 빡빡하지 않게) */
.p7-pack .p7-card [data-testid="stMarkdownContainer"] *{
  line-height: 1.27 !important;
}

/* 지문 카드와 문제 카드 사이 간격 줄이기 */
.p7-pack .p7-card + .p7-card{
  margin-top: .55rem !important;
}

/* (혹시) radiogroup 위쪽 여백도 조금 더 줄이기 */
.p7-pack div[role="radiogroup"]{
  margin-top: .10rem !important;
}
</style>
""", unsafe_allow_html=True)
except Exception:
    pass
# === /P7_PASSAGE_COMPACT_v1 ===








# --- P7_TEXT_SHRINK_LAST_FORCE_V2 ---
try:
    import streamlit as st
    st.markdown(r"""
<style>
/* === P7_TEXT_SHRINK_LAST_FORCE_V2 : PASSAGE + QUESTION ONLY === */

/* 1) 지문 카드(본문) 글자 줄이기 */
.p7-card, .p7-card *{
  font-size: 18px !important;   /* 필요하면 17px로 */
  line-height: 1.45 !important;
}

/* 2) 문제(질문) 영역 줄이기 */
.p7-q-title, .p7-q-title *,
.p7-question, .p7-question *,
.p7-qtext, .p7-qtext *{
  font-size: 19px !important;   /* 질문은 19px 추천 */
  line-height: 1.45 !important;
}

/* 3) Streamlit markdown 컨테이너까지 확실히 */
.p7-card div[data-testid="stMarkdownContainer"] *,
.p7-q-title div[data-testid="stMarkdownContainer"] *,
.p7-question div[data-testid="stMarkdownContainer"] *{
  font-size: inherit !important;
  line-height: inherit !important;
}

/* === /P7_TEXT_SHRINK_LAST_FORCE_V2 === */
</style>
""", unsafe_allow_html=True)
except Exception:
    pass
# --- /P7_TEXT_SHRINK_LAST_FORCE_V2 ---

# --- P7_TEXT_SCALE_UP_40_V1 ---
try:
    import streamlit as st
    st.markdown(r"""
<style>
/* === P7 TEXT SCALE UP +40% (COMBAT READABLE) === */

/* 지문 */
.p7-card, .p7-card *{
  font-size: 25px !important;
  line-height: 1.55 !important;
}

/* 문제 질문 */
.p7-q-title, .p7-q-title *,
.p7-question, .p7-question *{
  font-size: 26px !important;
  line-height: 1.55 !important;
}

/* 선택지 */
.p7-qtext, .p7-qtext *,
.p7-options, .p7-options *{
  font-size: 25px !important;
  line-height: 1.55 !important;
}

/* markdown 컨테이너까지 강제 */
.p7-card div[data-testid="stMarkdownContainer"] *,
.p7-q-title div[data-testid="stMarkdownContainer"] *,
.p7-question div[data-testid="stMarkdownContainer"] *{
  font-size: inherit !important;
}

/* === /P7 TEXT SCALE UP +40% === */
</style>
""", unsafe_allow_html=True)
except Exception:
    pass
# --- /P7_TEXT_SCALE_UP_40_V1 ---

# --- P7_FORCE_LAST_CSS_V1 (LAST OVERRIDE) ---
import streamlit as st

st.markdown("""
<style>
/* ===== P7_FORCE_LAST_CSS_V1 ===== */

/* (A) 분홍 테두리/외곽선/박스섀도우 싹 제거: 전체 앱 컨테이너를 강제 초기화 */
html, body { margin:0 !important; padding:0 !important; }
div[data-testid="stAppViewContainer"],
section.main,
main,
.stApp,
div.block-container{
  background: #ffffff !important;
  border: 0 !important;
  outline: 0 !important;
  box-shadow: none !important;
}

/* 혹시 테마가 사이드에 테두리/그라데이션을 주는 경우도 강제 제거 */
div[data-testid="stAppViewContainer"] *{
  outline-color: transparent !important;
}

/* (B) 지문/문제 글자 크게(지금 상태 대비 확실히 큼)
   - 지문: 26px
   - 문제(질문바): 30px
   - 보기(선택지): 24px (너무 커지면 카드 터져서 조금 낮게)
*/
.p7-card, .p7-card *{
  font-size: 26px !important;
  line-height: 1.45 !important;
}

.p7-q-title, .p7-q-title *,
.p7-question, .p7-question *,
.p7-qtext, .p7-qtext *{
  font-size: 30px !important;
  line-height: 1.40 !important;
}

/* 선택지(라디오/카드) 쪽은 살짝만 */
div[role="radiogroup"] label,
div[role="radiogroup"] label *{
  font-size: 24px !important;
  line-height: 1.35 !important;
}

/* ===== /P7_FORCE_LAST_CSS_V1 ===== */
</style>
""", unsafe_allow_html=True)

# --- /P7_FORCE_LAST_CSS_V1 ---
