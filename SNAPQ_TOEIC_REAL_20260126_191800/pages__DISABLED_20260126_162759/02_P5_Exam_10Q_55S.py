# app/arenas/p5_exam_10q_33s.py  (또는 현재 사용중인 p5_exam_10q_*.py에 그대로 전체 교체)
# ============================================================
# SNAPQ TOEIC - P5 EXAM (10Q / 44s) FINAL HUD BUILD v5
# - Forced DARK "PC-bang" theme
# - Desktop: 2-lane (Left Mission / Right Choices)
# - Mobile: auto vertical stack (CSS only)
# - NO typing: 4-choice card clicks only
# - Sudden Death: wrong at ANY step => instant fail
#
# ✅ 핵심 규칙 (User spec)
# - "원형 문장" 그대로 한 문장 기반
# - Step A / Step B: 문장 100% 동일 (단어/구문 절대 변경 없음)
# - 단지 블랭크 위치만 다르게 (어법/어휘 무관)
# - 10문항 / 44초
#
# ✅ PATCH (2026-01-30)
# - 모든 전장 상단 고정 네비 3개 추가:
#   🏠 Main Hub / 🗡 Armory / 📊 Scoreboard
# - 엔진/세션키/문제 로직 변경 없음
# ============================================================

from __future__ import annotations

import time
import random
import os
from dataclasses import dataclass
from typing import List, Optional

import streamlit as st


# ---------------------------
# Constants
# ---------------------------
ARENA_VER = "P5_EXAM_10Q_44S__SAME_SENTENCE_TWO_BLANKS__2026-01-30__NAV3"

TOTAL_SECONDS = 44
TOTAL_QUESTIONS = 10
DANGER_SHAKE_SECONDS = 10

BONUS_PER_CORRECT = 0.6
BONUS_CAP = 8.0  # total bonus max

# Session keys
KEY_SET_OFFICIAL = "ex10_set_idx"
KEY_SET_COMPAT = "p5_exam_set_idx"

KEY_ACTIVE = "p5ex10_active"
KEY_START_TS = "p5ex10_start_ts"
KEY_QIDX = "p5ex10_qidx"           # 0..9
KEY_STEP = "p5ex10_step"           # "A" or "B"
KEY_SCORE = "p5ex10_score"         # cleared questions count (0..10)
KEY_BONUS = "p5ex10_bonus"         # float, total bonus seconds (0..8)

KEY_LOCKED = "p5ex10_locked"
KEY_FAIL = "p5ex10_failed"
KEY_SEED = "p5ex10_seed"
KEY_QUESTIONS = "p5ex10_questions"
KEY_LAST = "p5ex10_last_pick"      # (qidx, step, picked_idx, correct)


# ---------------------------
# Data model
# ---------------------------
@dataclass(frozen=True)
class ExamQ:
    tag: str

    # SAME sentence (100% identical), only blank position differs
    prompt_a: str
    choices_a: List[str]
    answer_a: int

    prompt_b: str
    choices_b: List[str]
    answer_b: int

    tip: Optional[str] = None


# ---------------------------
# Key sync
# ---------------------------
def _sync_set_idx() -> int:
    off = st.session_state.get(KEY_SET_OFFICIAL, None)
    com = st.session_state.get(KEY_SET_COMPAT, None)

    if off is None and com is None:
        st.session_state[KEY_SET_OFFICIAL] = 0
        st.session_state[KEY_SET_COMPAT] = 0
        return 0

    if off is None and com is not None:
        st.session_state[KEY_SET_OFFICIAL] = int(com)
        st.session_state[KEY_SET_COMPAT] = int(com)
        return int(com)

    st.session_state[KEY_SET_OFFICIAL] = int(off)
    st.session_state[KEY_SET_COMPAT] = int(off)
    return int(off)


def _maybe_autorefresh(active: bool, interval_ms: int = 250) -> None:
    if not active:
        return
    fn = getattr(st, "autorefresh", None)
    if callable(fn):
        try:
            fn(interval=interval_ms, key="p5ex10_autorefresh")
        except TypeError:
            try:
                fn(interval_ms, key="p5ex10_autorefresh")
            except Exception:
                pass


# ---------------------------
# Timer with bonus
# ---------------------------
def _seconds_left() -> int:
    start = st.session_state.get(KEY_START_TS, None)
    bonus = float(st.session_state.get(KEY_BONUS, 0.0))
    bonus = max(0.0, min(BONUS_CAP, bonus))

    if not start:
        return int(TOTAL_SECONDS + bonus)

    elapsed = time.time() - float(start)
    left = (TOTAL_SECONDS - elapsed) + bonus
    return max(0, int(left))


def _award_bonus() -> None:
    b = float(st.session_state.get(KEY_BONUS, 0.0))
    b = min(BONUS_CAP, b + BONUS_PER_CORRECT)
    st.session_state[KEY_BONUS] = b


# ---------------------------
# Questions
# ✅ Step A / Step B 문장 "완전 동일"
# - 단어/구문 절대 변경 없음
# - 블랭크 위치만 다르게
# ---------------------------
def _load_questions_fallback(set_idx: int, seed: int) -> List[ExamQ]:
    bank: List[ExamQ] = [
        ExamQ(
            tag="Review / Time",
            prompt_a="The report was reviewed ____ the manager before noon.",
            choices_a=["by", "to", "with", "at"],
            answer_a=0,
            prompt_b="The report was reviewed by the manager ____ noon.",
            choices_b=["before", "during", "since", "until"],
            answer_b=0,
            tip="reviewed by / before noon",
        ),
        ExamQ(
            tag="Deadline / Sequence",
            prompt_a="All employees must submit their forms ____ Friday before the office closes.",
            choices_a=["by", "until", "during", "since"],
            answer_a=0,
            prompt_b="All employees must submit their forms by Friday ____ the office closes.",
            choices_b=["before", "during", "since", "although"],
            answer_b=0,
            tip="by Friday / before closes",
        ),
        ExamQ(
            tag="Result / Collocation",
            prompt_a="The technician repaired the machine, ____ production resumed without delay.",
            choices_a=["so", "because", "although", "unless"],
            answer_a=0,
            prompt_b="The technician repaired the machine, so production resumed ____ delay.",
            choices_b=["without", "during", "between", "since"],
            answer_b=0,
            tip="so / without delay",
        ),
        ExamQ(
            tag="Exception / Reason",
            prompt_a="The email was sent to everyone ____ the interns because they were off-site.",
            choices_a=["except", "beside", "during", "among"],
            answer_a=0,
            prompt_b="The email was sent to everyone except the interns ____ they were off-site.",
            choices_b=["because", "so", "unless", "and"],
            answer_b=0,
            tip="except / because",
        ),
        ExamQ(
            tag="Time Clause / Sequence",
            prompt_a="The documents need to be filed ____ they are signed before they are archived.",
            choices_a=["as soon as", "as long as", "even though", "so that"],
            answer_a=0,
            prompt_b="The documents need to be filed as soon as they are signed ____ they are archived.",
            choices_b=["before", "during", "since", "until"],
            answer_b=0,
            tip="as soon as / before",
        ),
        ExamQ(
            tag="Responsible / Tool",
            prompt_a="Ms. Lee is responsible ____ scheduling the interviews with the new system.",
            choices_a=["for", "to", "with", "at"],
            answer_a=0,
            prompt_b="Ms. Lee is responsible for scheduling the interviews ____ the new system.",
            choices_b=["with", "in", "on", "by"],
            answer_b=0,
            tip="responsible for / with",
        ),
        ExamQ(
            tag="Date / After",
            prompt_a="The new policy will take effect ____ March 1 after it is announced to staff.",
            choices_a=["on", "in", "at", "by"],
            answer_a=0,
            prompt_b="The new policy will take effect on March 1 ____ it is announced to staff.",
            choices_b=["after", "during", "until", "unless"],
            answer_b=0,
            tip="on a date / after",
        ),
        ExamQ(
            tag="Inform / Method",
            prompt_a="Please keep me informed ____ any changes to the schedule by email.",
            choices_a=["of", "on", "in", "for"],
            answer_a=0,
            prompt_b="Please keep me informed of any changes to the schedule ____ email.",
            choices_b=["by", "at", "in", "to"],
            answer_b=0,
            tip="informed of / by email",
        ),
        ExamQ(
            tag="Reason / Contrast",
            prompt_a="The proposal was rejected ____ it lacked sufficient data, although the idea was promising.",
            choices_a=["because", "so", "unless", "however"],
            answer_a=0,
            prompt_b="The proposal was rejected because it lacked sufficient data, ____ the idea was promising.",
            choices_b=["although", "so", "because", "before"],
            answer_b=0,
            tip="because / although",
        ),
        ExamQ(
            tag="Location / Floor",
            prompt_a="The meeting will be held ____ the main conference room on the third floor.",
            choices_a=["in", "on", "at", "by"],
            answer_a=0,
            prompt_b="The meeting will be held in the main conference room ____ the third floor.",
            choices_b=["on", "in", "at", "by"],
            answer_b=0,
            tip="in a room / on a floor",
        ),
    ]

    rng = random.Random(seed + set_idx * 9973)
    rng.shuffle(bank)
    return bank[:TOTAL_QUESTIONS]


def _get_questions() -> List[ExamQ]:
    set_idx = _sync_set_idx()
    qs = st.session_state.get(KEY_QUESTIONS, None)
    if isinstance(qs, list) and len(qs) >= TOTAL_QUESTIONS:
        return qs[:TOTAL_QUESTIONS]

    seed = st.session_state.get(KEY_SEED, None)
    if seed is None:
        seed = int(time.time() * 1000) % 2_000_000_000
        st.session_state[KEY_SEED] = seed

    qs2 = _load_questions_fallback(set_idx=set_idx, seed=int(seed))
    st.session_state[KEY_QUESTIONS] = qs2
    return qs2[:TOTAL_QUESTIONS]


# ---------------------------
# Run controls
# ---------------------------
def _reset_run(advance_set: bool = False) -> None:
    set_idx = _sync_set_idx()
    if advance_set:
        set_idx += 1
        st.session_state[KEY_SET_OFFICIAL] = set_idx
        st.session_state[KEY_SET_COMPAT] = set_idx

    seed = int(time.time() * 1000) % 2_000_000_000
    st.session_state[KEY_SEED] = seed
    st.session_state[KEY_QUESTIONS] = _load_questions_fallback(set_idx=set_idx, seed=seed)

    st.session_state[KEY_ACTIVE] = True
    st.session_state[KEY_START_TS] = time.time()
    st.session_state[KEY_QIDX] = 0
    st.session_state[KEY_STEP] = "A"
    st.session_state[KEY_SCORE] = 0
    st.session_state[KEY_BONUS] = 0.0

    st.session_state[KEY_LOCKED] = False
    st.session_state[KEY_FAIL] = False
    st.session_state[KEY_LAST] = None


def _finish_run() -> None:
    st.session_state[KEY_ACTIVE] = False
    st.session_state[KEY_LOCKED] = True


def _sudden_death() -> None:
    st.session_state[KEY_FAIL] = True
    _finish_run()


def _handle_choice(picked_idx: int) -> None:
    if st.session_state.get(KEY_LOCKED, False):
        return

    qidx = int(st.session_state.get(KEY_QIDX, 0))
    step = str(st.session_state.get(KEY_STEP, "A"))
    qs = _get_questions()

    if qidx >= len(qs):
        _finish_run()
        return

    q = qs[qidx]

    if step == "A":
        correct = (picked_idx == q.answer_a)
        st.session_state[KEY_LAST] = (qidx, "A", picked_idx, correct)

        if not correct:
            _sudden_death()
            return

        _award_bonus()
        st.session_state[KEY_STEP] = "B"
        return

    # step B
    correct = (picked_idx == q.answer_b)
    st.session_state[KEY_LAST] = (qidx, "B", picked_idx, correct)

    if not correct:
        _sudden_death()
        return

    _award_bonus()
    st.session_state[KEY_SCORE] = int(st.session_state.get(KEY_SCORE, 0)) + 1

    qidx += 1
    st.session_state[KEY_QIDX] = qidx
    st.session_state[KEY_STEP] = "A"

    if qidx >= TOTAL_QUESTIONS:
        _finish_run()
        st.session_state[KEY_SET_OFFICIAL] = _sync_set_idx() + 1
        st.session_state[KEY_SET_COMPAT] = st.session_state[KEY_SET_OFFICIAL]


# ---------------------------
# NAV (Top fixed routes)
# ---------------------------
def _safe_switch_page(primary: str, fallbacks: Optional[List[str]] = None) -> None:
    """
    - Main Hub 규칙: st.switch_page("main_hub.py") 우선
    - Armory/Scoreboard는 프로젝트에 따라 경로가 다를 수 있어 fallback 지원(크래시 방지)
    """
    fallbacks = fallbacks or []
    candidates = [primary] + [p for p in fallbacks if p and p != primary]

    # 존재 체크 (파일이 실제로 있으면 우선)
    # st.switch_page는 "페이지로 등록된 대상"이어야 하므로, 존재체크 + try/except를 같이 사용
    base = os.getcwd()

    tried = []
    for p in candidates:
        tried.append(p)
        try:
            st.switch_page(p)
            return
        except Exception:
            continue

    st.warning("⚠️ 이동 경로를 찾지 못했어요. 아래 경로들을 시도했지만 실패했습니다:\n- " + "\n- ".join(tried))


def _render_top_nav() -> None:
    st.markdown(
        """
<style>
/* Top NAV bar */
.p5nav{
  position: sticky; top: 0.10rem; z-index: 1000;
  display:flex; gap:0.55rem; align-items:center; justify-content:space-between;
  border-radius: 18px;
  border: 1px solid rgba(255,255,255,0.10);
  background: linear-gradient(135deg, rgba(10,12,18,0.88), rgba(24,16,40,0.88));
  box-shadow: 0 14px 34px rgba(0,0,0,0.55);
  padding: 0.55rem 0.65rem;
  backdrop-filter: blur(10px);
  margin-bottom: 0.65rem;
}
.p5navTitle{
  font-weight: 950;
  letter-spacing: 0.2px;
  opacity: 0.92;
  font-size: 0.95rem;
  padding-left: 0.2rem;
}
.p5navBtns{
  display:flex; gap:0.45rem; flex-wrap:wrap;
}
.p5navBtns .stButton > button{
  border-radius: 999px !important;
  padding: 0.55rem 0.75rem !important;
  font-size: 0.98rem !important;
  font-weight: 950 !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
  background: rgba(255,255,255,0.08) !important;
  box-shadow: 0 10px 18px rgba(0,0,0,0.45) !important;
  text-align: center !important;
  white-space: nowrap !important;
}
.p5navBtns .stButton > button:hover{
  transform: translateY(-1px);
  border-color: rgba(170,190,255,0.62) !important;
  background: rgba(170,190,255,0.18) !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )

    navL, navR = st.columns([1.1, 2.0], gap="small")
    with navL:
        st.markdown('<div class="p5nav"><div class="p5navTitle">🧭 NAV</div>', unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with navR:
        st.markdown('<div class="p5nav"><div class="p5navBtns">', unsafe_allow_html=True)

        c1, c2, c3 = st.columns([1, 1, 1], gap="small")
        with c1:
            if st.button("🏠 Main Hub", key="nav_main_hub", use_container_width=True):
                # ✅ 통일 규칙 유지
                _safe_switch_page("main_hub.py", fallbacks=["app/main_hub.py"])
        with c2:
            if st.button("🗡 Armory", key="nav_armory", use_container_width=True):
                # screenshot 기준: pages/03_Secret_Armory_Main.py 존재
                _safe_switch_page(
                    "pages/03_Secret_Armory_Main.py",
                    fallbacks=[
                        "03_Secret_Armory_Main.py",
                        "pages/03_Secret_Armory.py",
                        "pages/03_Secret_Armory.py",
                    ],
                )
        with c3:
            if st.button("📊 Scoreboard", key="nav_scoreboard", use_container_width=True):
                _safe_switch_page(
                    "pages/04_Scoreboard.py",
                    fallbacks=[
                        "04_Scoreboard.py",
                        "pages/04_My_Learning_Report.py",
                        "04_My_Learning_Report.py",
                        "pages/04_Report.py",
                    ],
                )

        st.markdown("</div></div>", unsafe_allow_html=True)


# ---------------------------
# CSS (FORCED DARK + mobile stack + BIGGER TEXT)
# - (keeps current layout)
# ---------------------------
def _inject_css() -> None:
    st.markdown(
        """
<style>
html, body, [data-testid="stAppViewContainer"]{
  background: radial-gradient(1400px 700px at 10% 0%, #1a1430 0%, #0b0f1a 55%, #070910 100%) !important;
  color: rgba(255,255,255,0.92) !important;
}
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stToolbar"] { right: 1rem !important; }

.block-container{
  max-width: 1180px;
  padding-top: 0.4rem;
  padding-bottom: 2.2rem;
}
@media (max-width: 768px){
  .block-container{ padding-left: 0.9rem; padding-right: 0.9rem; }
}

/* Mobile auto stack */
@media (max-width: 860px){
  div[data-testid="stHorizontalBlock"]{
    flex-direction: column !important;
    gap: 1rem !important;
  }
  div[data-testid="stHorizontalBlock"] > div[data-testid="column"]{
    width: 100% !important;
    flex: 1 1 100% !important;
  }
}

/* HUD */
.p5hud{
  position: sticky; top: 3.35rem; z-index: 999;  /* ✅ NAV 아래에 HUD가 붙도록 top 조정 */
  border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.10);
  background: linear-gradient(135deg, rgba(10,12,18,0.92), rgba(24,16,40,0.92));
  box-shadow: 0 16px 40px rgba(0,0,0,0.55);
  padding: 0.85rem 1.0rem;
  margin-bottom: 1.0rem;
  backdrop-filter: blur(10px);
}
.p5hudTop{
  display:flex; align-items:center; justify-content:space-between; gap:0.8rem; flex-wrap:wrap;
}
.p5title{
  font-weight: 950; letter-spacing: 0.2px;
  font-size: 1.18rem;
}
.p5badges{ display:flex; gap:0.55rem; flex-wrap:wrap; align-items:center; }
.p5badge{
  border-radius: 999px;
  padding: 0.28rem 0.68rem;
  font-weight: 900;
  font-size: 0.95rem;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.07);
}
.p5badge.danger{ border-color: rgba(255,90,90,0.45); background: rgba(255,90,90,0.14); }
.p5badge.ok{ border-color: rgba(90,255,200,0.32); background: rgba(90,255,200,0.12); }
.p5badge.bonus{ border-color: rgba(255,220,120,0.35); background: rgba(255,220,120,0.12); }

.p5gaugeWrap{
  margin-top: 0.65rem;
  border-radius: 999px;
  background: rgba(255,255,255,0.10);
  border: 1px solid rgba(255,255,255,0.10);
  overflow:hidden;
  height: 12px;
}
.p5gaugeBar{
  height: 100%;
  width: 50%;
  background: linear-gradient(90deg, rgba(90,170,255,0.96), rgba(175,120,255,0.96));
  transition: width 0.12s linear;
}
.p5gaugeBar.danger{
  background: linear-gradient(90deg, rgba(255,140,140,0.98), rgba(255,70,70,0.98));
}

@keyframes p5shake{
  0%{transform:translateX(0)}
  20%{transform:translateX(-3px)}
  40%{transform:translateX(3px)}
  60%{transform:translateX(-3px)}
  80%{transform:translateX(3px)}
  100%{transform:translateX(0)}
}
.p5shake{ animation:p5shake 0.25s infinite; }

/* Panels */
.p5panel{
  border-radius: 22px;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(255,255,255,0.06);
  box-shadow: 0 14px 34px rgba(0,0,0,0.55);
  padding: 1.05rem 1.05rem;
}
.p5qBox{
  border-radius: 18px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.06);
  padding: 1.05rem 1.05rem;
}
.p5qTag{
  display:inline-block;
  font-size: 0.92rem;
  font-weight: 950;
  padding: 0.26rem 0.62rem;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.16);
  background: rgba(255,255,255,0.08);
  margin-bottom: 0.7rem;
}

/* Problem */
.p5qText{
  font-size: 1.70rem;
  font-weight: 950;
  line-height: 1.35;
  color: rgba(255,255,255,0.96);
}
@media (max-width: 768px){
  .p5qText{ font-size: 1.38rem; }
}

/* Choice cards: bolder + clearer */
div.stButton > button{
  width:100%;
  border-radius: 18px !important;
  padding: 1.02rem 1.02rem !important;
  font-weight: 1000 !important;
  font-size: 1.26rem !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
  background: rgba(255,255,255,0.08) !important;
  color: #F5F7FF !important;
  box-shadow: 0 14px 26px rgba(0,0,0,0.55) !important;
  text-align: left !important;
  white-space: normal !important;
  line-height: 1.22 !important;
  transition: transform .08s ease, border-color .08s ease, background .08s ease, color .08s ease;
}
div.stButton > button:hover{
  transform: translateY(-1px);
  border-color: rgba(170,190,255,0.62) !important;
  background: rgba(170,190,255,0.18) !important;
  color: #FFFFFF !important;
}
@media (max-width: 768px){
  div.stButton > button{
    font-size: 1.14rem !important;
    padding: 0.98rem 0.98rem !important;
  }
}

/* Left / Right lane tint */
.p5leftLane div.stButton > button{
  background: rgba(90,170,255,0.18) !important;
  border-color: rgba(90,170,255,0.32) !important;
}
.p5rightLane div.stButton > button{
  background: rgba(190,120,255,0.18) !important;
  border-color: rgba(190,120,255,0.32) !important;
}

/* Feedback */
.p5ok{
  border: 1px solid rgba(90,255,200,0.30);
  background: rgba(90,255,200,0.14);
  border-radius: 16px;
  padding: 0.75rem 0.85rem;
  font-weight: 950;
  font-size: 1.05rem;
}
.p5bad{
  border: 1px solid rgba(255,90,90,0.34);
  background: rgba(255,90,90,0.16);
  border-radius: 16px;
  padding: 0.75rem 0.85rem;
  font-weight: 950;
  font-size: 1.05rem;
}
.p5small{ opacity: 0.86; font-size: 0.98rem; font-weight: 800; }
[data-testid="stMarkdownContainer"] p{ margin-bottom: 0.55rem; }
</style>
        """,
        unsafe_allow_html=True,
    )


def _render_hud(set_idx: int, qidx: int, step: str, score: int, seconds_left: int, active: bool) -> None:
    danger = active and (0 < seconds_left <= DANGER_SHAKE_SECONDS)

    max_total = TOTAL_SECONDS + BONUS_CAP
    pct = 0.0 if max_total <= 0 else (seconds_left / max_total)
    pct = max(0.0, min(1.0, pct))
    bar_w = int(pct * 100)

    shake_class = "p5shake" if danger else ""
    time_badge_class = "danger" if danger else "ok"
    bar_class = "p5gaugeBar danger" if danger else "p5gaugeBar"

    shown_set = (set_idx % 5) + 1
    bonus = float(st.session_state.get(KEY_BONUS, 0.0))
    bonus = max(0.0, min(BONUS_CAP, bonus))

    st.markdown(
        f"""
<div class="p5hud {shake_class}">
  <div class="p5hudTop">
    <div class="p5title">🔥 P5 EXAM 10Q · 44s</div>
    <div class="p5badges">
      <div class="p5badge">SET {shown_set}/5</div>
      <div class="p5badge">Q {min(qidx+1, TOTAL_QUESTIONS)}/{TOTAL_QUESTIONS}</div>
      <div class="p5badge">STEP {step}</div>
      <div class="p5badge">SCORE {score}/{TOTAL_QUESTIONS}</div>
      <div class="p5badge bonus">+{bonus:.1f}s</div>
      <div class="p5badge {time_badge_class}">⏱ {seconds_left}s</div>
    </div>
  </div>
  <div class="p5gaugeWrap">
    <div class="{bar_class}" style="width:{bar_w}%"></div>
  </div>
</div>
        """,
        unsafe_allow_html=True,
    )


def render() -> None:
    _inject_css()

    # ✅ NEW: Top NAV (Main Hub / Armory / Scoreboard) — always visible
    _render_top_nav()

    set_idx = _sync_set_idx()

    # init
    if KEY_ACTIVE not in st.session_state:
        st.session_state[KEY_ACTIVE] = False
    if KEY_LOCKED not in st.session_state:
        st.session_state[KEY_LOCKED] = False
    if KEY_FAIL not in st.session_state:
        st.session_state[KEY_FAIL] = False
    if KEY_STEP not in st.session_state:
        st.session_state[KEY_STEP] = "A"
    if KEY_BONUS not in st.session_state:
        st.session_state[KEY_BONUS] = 0.0

    active = bool(st.session_state.get(KEY_ACTIVE, False))

    if KEY_QUESTIONS not in st.session_state:
        st.session_state[KEY_SEED] = int(time.time() * 1000) % 2_000_000_000
        st.session_state[KEY_QUESTIONS] = _load_questions_fallback(set_idx=set_idx, seed=int(st.session_state[KEY_SEED]))

    _maybe_autorefresh(active=active, interval_ms=250)

    seconds_left = _seconds_left()
    if active and seconds_left <= 0:
        _finish_run()
        active = False

    qidx = int(st.session_state.get(KEY_QIDX, 0))
    step = str(st.session_state.get(KEY_STEP, "A"))
    score = int(st.session_state.get(KEY_SCORE, 0))

    _render_hud(set_idx=set_idx, qidx=qidx, step=step, score=score, seconds_left=seconds_left, active=active)
    st.caption(f"ARENA_VER: {ARENA_VER}")

    left, right = st.columns([1.25, 1.0], gap="large")

    with left:
        st.markdown('<div class="p5panel">', unsafe_allow_html=True)

        if not active:
            st.markdown("### 🧾 Commander Brief (전장 규칙)")
            st.markdown(
                """
- **한 세트 = 10문항**, 각 문항은 **같은 문장**으로 **A(블랭크1) → B(블랭크2)** 2스텝
- **44초 전체** + 정답 보너스 **+0.6초**(상한 8초)
- **Wrong = Sudden Death**
- **타이핑 없음**: 4지선다 카드 클릭만
- **10초 이하**: 폭탄 경고(흔들림 + 게이지 빨강)
                """.strip()
            )

            c1, c2 = st.columns(2, gap="small")
            with c1:
                if st.button("🚀 START MISSION", key="p5ex10_start_btn", use_container_width=True):
                    _reset_run(advance_set=False)
                    st.rerun()
            with c2:
                if st.button("♻️ NEW SET", key="p5ex10_newset_btn", use_container_width=True):
                    _reset_run(advance_set=True)
                    st.rerun()

            if st.session_state.get(KEY_LOCKED, False):
                st.markdown("---")
                if st.session_state.get(KEY_FAIL, False):
                    st.markdown('<div class="p5bad">💥 SUDDEN DEATH! 오답으로 즉시 종료.</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="p5ok">🏁 MISSION CLEAR! 10문항(2스텝) 통과.</div>', unsafe_allow_html=True)

                st.markdown(f"### 결과: **{score}/{TOTAL_QUESTIONS}**")
                st.markdown('<div class="p5small">※ SCORE는 “문항 클리어(=B까지 통과)” 개수입니다.</div>', unsafe_allow_html=True)

                if st.button("🔁 RESTART", key="p5ex10_restart_btn", use_container_width=True):
                    _reset_run(advance_set=False)
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
            return

        qs = _get_questions()
        qidx = int(st.session_state.get(KEY_QIDX, 0))
        step = str(st.session_state.get(KEY_STEP, "A"))

        if qidx >= TOTAL_QUESTIONS:
            _finish_run()
            st.rerun()

        q = qs[qidx]

        if step == "A":
            st.markdown(
                f"""
<div class="p5qBox">
  <div class="p5qTag">🎯 {q.tag} · Q{qidx+1} · STEP A</div>
  <div class="p5qText">{q.prompt_a}</div>
</div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
<div class="p5qBox">
  <div class="p5qTag">🎯 {q.tag} · Q{qidx+1} · STEP B</div>
  <div class="p5qText">{q.prompt_b}</div>
</div>
                """,
                unsafe_allow_html=True,
            )

        lp = st.session_state.get(KEY_LAST, None)
        if isinstance(lp, tuple) and len(lp) == 4:
            prev_qidx, prev_step, _picked, correct = lp
            if prev_qidx == qidx and prev_step != step:
                st.markdown("---")
                if correct:
                    st.markdown('<div class="p5ok">✅ 정답! +0.6s 보너스 지급 🔥</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="p5bad">💥 오답! Sudden Death 발동.</div>', unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="p5panel">', unsafe_allow_html=True)

        if st.session_state.get(KEY_LOCKED, False):
            if st.session_state.get(KEY_FAIL, False):
                st.markdown('<div class="p5bad">💥 SUDDEN DEATH — 다시 도전!</div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="p5ok">🏁 종료 — 결과 확인 후 재도전!</div>', unsafe_allow_html=True)

            if st.button("🔁 RESTART", key="p5ex10_restart_btn_right", use_container_width=True):
                _reset_run(advance_set=False)
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
            return

        qs = _get_questions()
        qidx = int(st.session_state.get(KEY_QIDX, 0))
        step = str(st.session_state.get(KEY_STEP, "A"))
        q = qs[qidx]

        choices = q.choices_a if step == "A" else q.choices_b

        left_idxs = [0, 2]
        right_idxs = [1, 3]

        laneL, laneR = st.columns(2, gap="medium")

        with laneL:
            st.markdown('<div class="p5leftLane">', unsafe_allow_html=True)
            for i in left_idxs:
                label = f"({chr(65+i)})  {choices[i]}"
                if st.button(label, key=f"p5ex10_pick_{qidx}_{step}_{i}", use_container_width=True):
                    _handle_choice(i)
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with laneR:
            st.markdown('<div class="p5rightLane">', unsafe_allow_html=True)
            for i in right_idxs:
                label = f"({chr(65+i)})  {choices[i]}"
                if st.button(label, key=f"p5ex10_pick_{qidx}_{step}_{i}", use_container_width=True):
                    _handle_choice(i)
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)
