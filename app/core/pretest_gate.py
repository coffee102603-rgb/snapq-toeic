# app/core/pretest_gate.py
from __future__ import annotations
import json
from datetime import datetime, date
from pathlib import Path
from typing import Optional
import streamlit as st

_ROOT = Path(__file__).resolve().parents[2]
COHORTS_DIR = _ROOT / "data" / "cohorts"
DIAGNOSIS_FILE = _ROOT / "data" / "diagnosis_sets.json"

def _load_diagnosis_sets() -> dict:
    try:
        if DIAGNOSIS_FILE.exists():
            return json.loads(DIAGNOSIS_FILE.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}

def _profile_path(student_id: str, cohort_month: str) -> Path:
    return COHORTS_DIR / cohort_month / "students" / f"{student_id}.json"

def _load_profile(student_id: str, cohort_month: str) -> dict:
    path = _profile_path(student_id, cohort_month)
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        pass
    return {}

def _save_profile(student_id: str, cohort_month: str, profile: dict) -> None:
    path = _profile_path(student_id, cohort_month)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")

def _which_diagnosis_needed(profile: dict) -> Optional[str]:
    diagnosis = profile.get("diagnosis", {})
    first_access_str = profile.get("first_access", "")
    if not diagnosis.get("day1"):
        return "day1"
    try:
        first_date = datetime.fromisoformat(first_access_str).date()
        elapsed = (date.today() - first_date).days
    except Exception:
        return None
    if not diagnosis.get("day10") and elapsed >= 10:
        return "day10"
    if not diagnosis.get("day20") and elapsed >= 20:
        return "day20"
    return None

def _apply_css() -> None:
    st.markdown("""
<style>
.stApp { background-color: #07090f !important; }
.block-container { padding-top: 1.5rem !important; max-width: 600px !important; background-color: #07090f !important; }
.diag-header { background: linear-gradient(135deg,rgba(255,170,0,0.15),rgba(255,60,0,0.1)); border: 1px solid rgba(255,170,0,0.3); border-radius: 16px; padding: 16px 20px; margin-bottom: 1.2rem; }
.diag-title { font-size: 1.4rem; font-weight: 900; color: #ffaa00 !important; margin-bottom: 4px; }
.diag-sub { font-size: 0.85rem; color: rgba(255,255,255,0.6) !important; }
.survey-header { background: linear-gradient(135deg,rgba(0,170,255,0.15),rgba(0,100,200,0.1)); border: 1px solid rgba(0,170,255,0.3); border-radius: 16px; padding: 16px 20px; margin-bottom: 1.2rem; }
.survey-title { font-size: 1.4rem; font-weight: 900; color: #00aaff !important; margin-bottom: 4px; }
.survey-sub { font-size: 0.85rem; color: rgba(255,255,255,0.6) !important; }
.progress-bar-wrap { background: rgba(255,255,255,0.08); border-radius: 99px; height: 8px; margin: 12px 0 4px; overflow: hidden; }
.progress-bar-fill { height: 8px; border-radius: 99px; background: linear-gradient(90deg,#ffaa00,#ff6600); }
.progress-bar-fill-blue { height: 8px; border-radius: 99px; background: linear-gradient(90deg,#00aaff,#0066ff); }
.q-box { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 14px; padding: 18px 20px; margin-bottom: 1rem; }
.q-num { font-size: 0.9rem; font-weight: 700; color: #ffaa00 !important; margin-bottom: 8px; }
.q-num-blue { font-size: 0.9rem; font-weight: 700; color: #00aaff !important; margin-bottom: 8px; }
.q-text { font-size: 1.05rem; font-weight: 700; color: #ffffff !important; line-height: 1.5; }
.passage-box { background: rgba(255,255,255,0.04); border-left: 3px solid rgba(255,170,0,0.5); border-radius: 0 12px 12px 0; padding: 14px 16px; font-size: 0.88rem; color: rgba(255,255,255,0.85) !important; line-height: 1.7; margin-bottom: 1.2rem; white-space: pre-line; }
.result-box { background: rgba(0,200,100,0.1); border: 1px solid rgba(0,200,100,0.3); border-radius: 16px; padding: 24px; text-align: center; margin: 1rem 0; }
.result-score { font-size: 3rem; font-weight: 900; color: #00ff88 !important; }
.result-label { font-size: 0.9rem; color: rgba(255,255,255,0.6) !important; margin-top: 4px; }
div[data-testid="stRadio"] { background: transparent !important; }
div[data-testid="stRadio"] > div { background: transparent !important; gap: 8px !important; }
div[data-testid="stRadio"] label { background: #1e2235 !important; border: 1.5px solid rgba(255,255,255,0.2) !important; border-radius: 10px !important; padding: 12px 16px !important; margin-bottom: 6px !important; width: 100% !important; cursor: pointer !important; display: flex !important; align-items: center !important; }
div[data-testid="stRadio"] label:hover { background: rgba(255,170,0,0.15) !important; border-color: rgba(255,170,0,0.6) !important; }
div[data-testid="stRadio"] label > div { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-size: 1rem !important; font-weight: 600 !important; }
div[data-testid="stRadio"] label p { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-size: 1rem !important; font-weight: 600 !important; margin: 0 !important; }
div[data-testid="stRadio"] input[type="radio"] { accent-color: #ffaa00 !important; width: 18px !important; height: 18px !important; margin-right: 10px !important; flex-shrink: 0 !important; }
div[data-testid="stButton"] button { background: linear-gradient(135deg,#ffaa00,#ff6600) !important; color: #000000 !important; -webkit-text-fill-color: #000000 !important; font-weight: 900 !important; font-size: 1rem !important; border-radius: 14px !important; border: none !important; padding: 0.7rem !important; width: 100% !important; }
div[data-testid="stButton"] button p { color: #000000 !important; -webkit-text-fill-color: #000000 !important; }
div[data-testid="stAlert"] p { color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# 설문 문항 정의
# ─────────────────────────────────────────
SURVEY_DAY1 = [
    {"id": "s1_q1", "question": "⚔️ 나의 현재 영어 전투력은?", "options": ["500점 미만", "500~650점", "650~750점", "750점 이상"]},
    {"id": "s1_q2", "question": "🎯 이번 달 정복 목표는?", "options": ["600점", "700점", "800점", "900점 이상"]},
    {"id": "s1_q3", "question": "⏱️ 하루 평균 훈련 시간은?", "options": ["30분 미만", "30분~1시간", "1~2시간", "2시간 이상"]},
    {"id": "s1_q4", "question": "🏹 지금까지 토익 실전 출전 횟수는?", "options": ["없음", "1~2회", "3~5회", "6회 이상"]},
    {"id": "s1_q5", "question": "📱 주로 사용할 전투 기기는?", "options": ["스마트폰", "태블릿", "노트북/PC", "번갈아 씀"]},
]

SURVEY_DAY10 = [
    {"id": "s10_q1", "question": "⚡ 지난 10일간 SnapQ 평균 접속 횟수는?", "options": ["거의 안 함 (1~2회)", "가끔 (3~5회)", "자주 (6~8회)", "매일 (9회 이상)"]},
    {"id": "s10_q2", "question": "🔥 지난 10일간 가장 많이 한 전장은?", "options": ["P5 전장", "P7 전장", "역전장", "비슷하게 했음"]},
    {"id": "s10_q3", "question": "⏰ P5 전장에서 주로 선택한 타이머는?", "options": ["30초 (극한모드)", "40초 (도전모드)", "50초 (안정모드)", "매번 달랐음"]},
    {"id": "s10_q4", "question": "💪 현재 전투 의지는 처음과 비교하면?", "options": ["많이 떨어짐", "비슷함", "조금 올라감", "훨씬 올라감"]},
]

SURVEY_DAY20 = [
    {"id": "s20_q1", "question": "🏆 SnapQ 훈련 후 실력이 올랐다고 느끼나요?", "options": ["전혀 그렇지 않다", "별로 그렇지 않다", "약간 그렇다", "많이 그렇다"]},
    {"id": "s20_q2", "question": "⚔️ 가장 도움이 된 전장은?", "options": ["P5 타이머 전장", "P7 단계별 독해", "역전장 (오답 재도전)", "전체 비슷하게 도움됨"]},
    {"id": "s20_q3", "question": "📱 모바일로 훈련할 때 화면 크기가 영향을 줬나요?", "options": ["전혀 영향 없음", "약간 불편했음", "보통", "화면이 커서 더 편했음"]},
    {"id": "s20_q4", "question": "🎖️ 이 플랫폼을 전우(친구)에게 추천하고 싶나요?", "options": ["전혀 아님", "별로", "보통", "적극 추천"]},
]

SURVEY_MAP = {"day1": SURVEY_DAY1, "day10": SURVEY_DAY10, "day20": SURVEY_DAY20}

# ─────────────────────────────────────────
# 설문 렌더링
# ─────────────────────────────────────────
def _render_survey(day_key: str, student_id: str, cohort_month: str) -> None:
    _apply_css()
    questions = SURVEY_MAP.get(day_key, [])
    total_q = len(questions)

    day_label = {"day1": "Day 1", "day10": "Day 10", "day20": "Day 20"}.get(day_key, day_key)

    st.markdown(f'''
<div class="survey-header">
    <div class="survey-title">🛡️ {day_label} 전투 준비 체크!</div>
    <div class="survey-sub">전장 입장 전 {total_q}가지만 체크하고 바로 출격!</div>
</div>
''', unsafe_allow_html=True)

    if "survey_answers" not in st.session_state:
        st.session_state["survey_answers"] = {}

    answers = st.session_state["survey_answers"]
    answered_count = len(answers)
    pct = int(answered_count / total_q * 100) if total_q > 0 else 0

    st.markdown(f'<div class="progress-bar-wrap"><div class="progress-bar-fill-blue" style="width:{pct}%;"></div></div><div style="font-size:0.78rem;color:rgba(255,255,255,0.4);text-align:right;margin-bottom:1rem;">{answered_count} / {total_q} 완료</div>', unsafe_allow_html=True)

    for i, q in enumerate(questions):
        qid = q["id"]
        st.markdown(f'<div class="q-box"><div class="q-num-blue">CHECK {i+1}</div><div class="q-text">{q["question"]}</div></div>', unsafe_allow_html=True)
        choice = st.radio(label=f"s_{qid}", options=q["options"], index=None, key=f"survey_{qid}", label_visibility="collapsed")
        if choice is not None:
            answers[qid] = choice

    st.session_state["survey_answers"] = answers
    st.markdown("---")
    all_answered = len(answers) >= total_q
    if not all_answered:
        st.warning(f"⚠️ {total_q - len(answers)}개 더 체크해야 출격할 수 있어요!")

    if st.button("✅ 체크 완료 → 진단 시작!", disabled=not all_answered, key="survey_submit_btn"):
        profile = _load_profile(student_id, cohort_month)
        if "surveys" not in profile:
            profile["surveys"] = {}
        profile["surveys"][day_key] = {
            "completed_at": datetime.now().isoformat(timespec="seconds"),
            "answers": dict(answers)
        }
        _save_profile(student_id, cohort_month, profile)
        st.session_state[f"survey_{day_key}_done"] = True
        st.session_state["survey_answers"] = {}
        st.rerun()

# ─────────────────────────────────────────
# 진단 렌더링
# ─────────────────────────────────────────
def _render_diagnosis(day_key: str, student_id: str, cohort_month: str) -> None:
    _apply_css()
    sets = _load_diagnosis_sets()
    day_data = sets.get(day_key, {})
    label = day_data.get("label", day_key.upper())
    p5_questions = day_data.get("p5", [])
    p7_data = day_data.get("p7", {})
    p7_passage = p7_data.get("passage", "")
    p7_questions = p7_data.get("questions", [])
    total_q = len(p5_questions) + len(p7_questions)

    st.markdown(f'<div class="diag-header"><div class="diag-title">📋 {label}</div><div class="diag-sub">전장 입장 전 필수 · P5 {len(p5_questions)}문제 + P7 {len(p7_questions)}문제 = 총 {total_q}문제</div></div>', unsafe_allow_html=True)

    if "diag_answers" not in st.session_state:
        st.session_state["diag_answers"] = {}
    if "diag_submitted" not in st.session_state:
        st.session_state["diag_submitted"] = False

    answers = st.session_state["diag_answers"]

    if st.session_state.get("diag_submitted"):
        _render_result(day_key, student_id, cohort_month, p5_questions, p7_questions, answers)
        return

    answered_count = len(answers)
    pct = int(answered_count / total_q * 100) if total_q > 0 else 0
    st.markdown(f'<div class="progress-bar-wrap"><div class="progress-bar-fill" style="width:{pct}%;"></div></div><div style="font-size:0.78rem;color:rgba(255,255,255,0.4);text-align:right;margin-bottom:1rem;">{answered_count} / {total_q} 답변 완료</div>', unsafe_allow_html=True)

    st.markdown("### ⚡ Part 5 — 문법 / 어휘")
    for i, q in enumerate(p5_questions):
        qid = q["id"]
        st.markdown(f'<div class="q-box"><div class="q-num">Q{i+1}</div><div class="q-text">{q["question"]}</div></div>', unsafe_allow_html=True)
        choice = st.radio(label=f"Q{i+1}", options=q["options"], index=None, key=f"diag_{qid}", label_visibility="collapsed")
        if choice is not None:
            answers[qid] = q["options"].index(choice)

    st.markdown("---")
    st.markdown("### 📖 Part 7 — 독해")
    st.markdown(f'<div class="passage-box">{p7_passage}</div>', unsafe_allow_html=True)
    for i, q in enumerate(p7_questions):
        qid = q["id"]
        st.markdown(f'<div class="q-box"><div class="q-num">Q{len(p5_questions)+i+1}</div><div class="q-text">{q["question"]}</div></div>', unsafe_allow_html=True)
        choice = st.radio(label=f"P7_Q{i+1}", options=q["options"], index=None, key=f"diag_{qid}", label_visibility="collapsed")
        if choice is not None:
            answers[qid] = q["options"].index(choice)

    st.session_state["diag_answers"] = answers
    st.markdown("---")
    all_answered = len(answers) >= total_q
    if not all_answered:
        st.warning(f"⚠️ {total_q - len(answers)}문제 더 답변해야 제출할 수 있어요!")
    if st.button("✅ 진단 제출 → 전장 입장!", disabled=not all_answered, key="diag_submit_btn"):
        st.session_state["diag_submitted"] = True
        st.rerun()

def _render_result(day_key, student_id, cohort_month, p5_questions, p7_questions, answers):
    p5_correct = sum(1 for q in p5_questions if answers.get(q["id"]) == q["answer_index"])
    p7_correct = sum(1 for q in p7_questions if answers.get(q["id"]) == q["answer_index"])
    total_correct = p5_correct + p7_correct
    total_q = len(p5_questions) + len(p7_questions)
    total_score = round(total_correct / total_q * 100) if total_q > 0 else 0

    profile = _load_profile(student_id, cohort_month)
    if "diagnosis" not in profile:
        profile["diagnosis"] = {}
    profile["diagnosis"][day_key] = {"date": date.today().isoformat(), "total_score": total_score, "p5_score": round(p5_correct / len(p5_questions) * 100) if p5_questions else 0, "p7_score": round(p7_correct / len(p7_questions) * 100) if p7_questions else 0, "total_correct": total_correct, "total_q": total_q, "completed_at": datetime.now().isoformat(timespec="seconds")}
    _save_profile(student_id, cohort_month, profile)
    st.session_state["student_profile"] = profile
    st.session_state[f"diagnosis_{day_key}_done"] = True

    day_label = {"day1": "Day 1", "day10": "Day 10", "day20": "Day 20"}.get(day_key, day_key)
    st.markdown(f'<div class="result-box"><div class="result-score">{total_score}점</div><div class="result-label">{day_label} 진단 완료 · P5 {p5_correct}/{len(p5_questions)} · P7 {p7_correct}/{len(p7_questions)}</div></div>', unsafe_allow_html=True)

    if total_score >= 85:
        msg = "🏆 훌륭합니다! 상위권 전투력이에요!"
    elif total_score >= 70:
        msg = "💪 좋아요! 조금만 더 훈련하면 최상위권!"
    elif total_score >= 50:
        msg = "📚 기초를 잡아가고 있어요. 꾸준히 출격!"
    else:
        msg = "🔥 지금부터 시작이에요! 전장에서 실력을 키워요!"
    st.markdown(f"**{msg}**")
    st.markdown("---")
    if st.button("⚡ 전장 로비 입장!", key="enter_lobby_btn"):
        for k in ["diag_answers", "diag_submitted"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

# ─────────────────────────────────────────
# 메인 게이트
# ─────────────────────────────────────────
def require_pretest_gate() -> None:
    student_id = st.session_state.get("student_id") or st.session_state.get("battle_nickname", "")
    cohort_month = st.session_state.get("cohort_month", date.today().strftime("%Y-%m"))
    if not student_id:
        return

    profile = _load_profile(student_id, cohort_month)
    if not profile:
        day_needed = "day1"
    else:
        day_needed = _which_diagnosis_needed(profile)

    if day_needed is None:
        return

    if st.session_state.get(f"diagnosis_{day_needed}_done"):
        return

    # 설문 먼저 → 진단 순서
    if not st.session_state.get(f"survey_{day_needed}_done"):
        survey_done = profile.get("surveys", {}).get(day_needed)
        if not survey_done:
            _render_survey(day_needed, student_id, cohort_month)
            st.stop()

    _render_diagnosis(day_needed, student_id, cohort_month)
    st.stop()

def mark_pretest_done(nickname: str, cohort: str) -> None:
    pass
