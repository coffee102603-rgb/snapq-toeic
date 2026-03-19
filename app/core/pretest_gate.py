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
.survey-header { background: linear-gradient(135deg,rgba(0,150,255,0.15),rgba(0,80,200,0.1)); border: 1px solid rgba(0,150,255,0.3); border-radius: 16px; padding: 16px 20px; margin-bottom: 1.2rem; }
.survey-title { font-size: 1.4rem; font-weight: 900; color: #4fc3f7 !important; margin-bottom: 4px; }
.survey-sub { font-size: 0.85rem; color: rgba(255,255,255,0.6) !important; }
.progress-bar-wrap { background: rgba(255,255,255,0.08); border-radius: 99px; height: 8px; margin: 12px 0 4px; overflow: hidden; }
.progress-bar-fill { height: 8px; border-radius: 99px; background: linear-gradient(90deg,#ffaa00,#ff6600); }
.q-box { background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 14px; padding: 18px 20px; margin-bottom: 1rem; }
.q-num { font-size: 0.9rem; font-weight: 700; color: #ffaa00 !important; margin-bottom: 8px; }
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

# ── 설문 문항 정의 ──
SURVEY_DAY1 = {
    "title": "⚔️ 전사 프로필 등록",
    "sub": "전장 입장 전 나의 전투력을 등록하세요!",
    "questions": [
        {"id": "s1_q1", "text": "🏆 나의 현재 영어 전투력은?", "options": ["500 미만 (훈련병)", "500~650 (일반병)", "650~750 (하사)", "750 이상 (장교)"]},
        {"id": "s1_q2", "text": "🎯 이번 달 정복 목표는?", "options": ["600점 돌파", "700점 돌파", "800점 돌파", "900점 이상 정복"]},
        {"id": "s1_q3", "text": "⏱️ 하루 훈련 시간은?", "options": ["30분 미만", "30분~1시간", "1~2시간", "2시간 이상"]},
        {"id": "s1_q4", "text": "🎖️ 지금까지 실전 출전 횟수는? (토익 응시)", "options": ["없음 (첫 출전 준비중)", "1~2회", "3~5회", "6회 이상"]},
        {"id": "s1_q5", "text": "📱 주로 사용할 무기(기기)는?", "options": ["스마트폰", "태블릿", "노트북", "PC"]}
    ]
}

SURVEY_DAY10 = {
    "title": "⚡ 중간 전투 보고",
    "sub": "10일간의 전투 기록을 보고하라!",
    "questions": [
        {"id": "s10_q1", "text": "📅 지난 10일간 SnapQ 출격 횟수는?", "options": ["거의 안 함 (1~2회)", "가끔 출격 (3~5회)", "자주 출격 (6~8회)", "매일 출격 (9회 이상)"]},
        {"id": "s10_q2", "text": "⚔️ 가장 많이 출전한 전장은?", "options": ["P5 전장 (문법/어휘)", "P7 전장 (독해)", "역전장 (오답 재도전)", "비슷하게 출전"]},
        {"id": "s10_q3", "text": "⏰ P5 전장에서 주로 선택한 시간 압박은?", "options": ["30초 (극한 압박)", "40초 (중간 압박)", "50초 (여유 압박)", "매번 달랐음"]},
        {"id": "s10_q4", "text": "🔥 현재 전투 의지는 처음과 비교하면?", "options": ["많이 떨어짐", "비슷함", "조금 올라감", "불타오름!"]}
    ]
}

SURVEY_DAY20 = {
    "title": "🏆 최종 전투 결산",
    "sub": "20일간의 전투를 마무리하라!",
    "questions": [
        {"id": "s20_q1", "text": "💪 SnapQ 훈련 후 실력이 올랐다고 느끼나요?", "options": ["전혀 모르겠음", "약간 오른 것 같음", "확실히 올랐음", "엄청 올랐음!"]},
        {"id": "s20_q2", "text": "🎖️ 가장 도움이 된 전장은?", "options": ["P5 타이머 전장", "P7 단계별 독해", "역전장 (오답 재도전)", "전체 비슷하게 도움됨"]},
        {"id": "s20_q3", "text": "📱 모바일 화면 크기가 학습에 영향을 줬나요?", "options": ["전혀 영향 없음", "약간 불편했음", "보통이었음", "화면이 커서 더 편했음"]},
        {"id": "s20_q4", "text": "📣 이 플랫폼을 전우에게 추천하고 싶나요?", "options": ["비추천", "글쎄요", "추천!", "무조건 추천!"]}
    ]
}

def _render_survey(survey: dict, student_id: str, cohort_month: str, day_key: str) -> None:
    _apply_css()
    st.markdown(f'<div class="survey-header"><div class="survey-title">{survey["title"]}</div><div class="survey-sub">{survey["sub"]}</div></div>', unsafe_allow_html=True)

    if "survey_answers" not in st.session_state:
        st.session_state["survey_answers"] = {}
    if "survey_submitted" not in st.session_state:
        st.session_state["survey_submitted"] = False

    if st.session_state.get("survey_submitted"):
        profile = _load_profile(student_id, cohort_month)
        if "surveys" not in profile:
            profile["surveys"] = {}
        profile["surveys"][day_key] = {
            "answers": st.session_state["survey_answers"],
            "completed_at": datetime.now().isoformat(timespec="seconds")
        }
        _save_profile(student_id, cohort_month, profile)
        st.session_state["student_profile"] = profile
        st.session_state[f"survey_{day_key}_done"] = True
        for k in ["survey_answers", "survey_submitted"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()
        return

    answers = st.session_state["survey_answers"]
    questions = survey["questions"]
    total_q = len(questions)

    answered = len(answers)
    pct = int(answered / total_q * 100) if total_q > 0 else 0
    st.markdown(f'<div class="progress-bar-wrap"><div class="progress-bar-fill" style="width:{pct}%;"></div></div><div style="font-size:0.78rem;color:rgba(255,255,255,0.4);text-align:right;margin-bottom:1rem;">{answered} / {total_q} 완료</div>', unsafe_allow_html=True)

    for i, q in enumerate(questions):
        qid = q["id"]
        st.markdown(f'<div class="q-box"><div class="q-num">Q{i+1}</div><div class="q-text">{q["text"]}</div></div>', unsafe_allow_html=True)
        choice = st.radio(label=f"SQ{i+1}", options=q["options"], index=None, key=f"survey_{qid}", label_visibility="collapsed")
        if choice is not None:
            answers[qid] = choice

    st.session_state["survey_answers"] = answers
    st.markdown("---")
    all_answered = len(answers) >= total_q
    if not all_answered:
        st.warning(f"⚠️ {total_q - len(answers)}개 더 선택해야 진행할 수 있어요!")
    if st.button("✅ 등록 완료 → 입장 테스트 시작!", disabled=not all_answered, key="survey_submit_btn"):
        st.session_state["survey_submitted"] = True
        st.rerun()

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

    day_labels = {"day1": "⚔️ 입장 자격 테스트", "day10": "⚡ 중간 전투 테스트", "day20": "🏆 최종 전투 테스트"}
    display_label = day_labels.get(day_key, label)

    st.markdown(f'<div class="diag-header"><div class="diag-title">📋 {display_label}</div><div class="diag-sub">전장 입장 전 필수 · P5 {len(p5_questions)}문제 + P7 {len(p7_questions)}문제 = 총 {total_q}문제</div></div>', unsafe_allow_html=True)

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
    if st.button("✅ 테스트 제출 → 전장 입장!", disabled=not all_answered, key="diag_submit_btn"):
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

    if total_score >= 85:
        msg = "🏆 전설급 전사! 최상위 전투력 확인!"
        color = "#ffd700"
    elif total_score >= 70:
        msg = "💪 우수 전사! 조금만 더 훈련하면 최강!"
        color = "#00ff88"
    elif total_score >= 50:
        msg = "⚔️ 훈련중인 전사! 전장에서 실력을 키워라!"
        color = "#4fc3f7"
    else:
        msg = "🔥 신병 입대! 지금부터 시작이다!"
        color = "#ff6600"

    st.markdown(f'<div class="result-box"><div class="result-score" style="color:{color}!important;">{total_score}점</div><div class="result-label">P5 {p5_correct}/{len(p5_questions)} · P7 {p7_correct}/{len(p7_questions)}</div></div>', unsafe_allow_html=True)
    st.markdown(f"**{msg}**")
    st.markdown("---")
    if st.button("⚡ 전장 로비 입장!", key="enter_lobby_btn"):
        for k in ["diag_answers", "diag_submitted"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

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
    surveys = {"day1": SURVEY_DAY1, "day10": SURVEY_DAY10, "day20": SURVEY_DAY20}
    survey_data = surveys.get(day_needed)

    if survey_data:
        survey_done = (profile.get("surveys", {}).get(day_needed) or st.session_state.get(f"survey_{day_needed}_done"))
        if not survey_done:
            _render_survey(survey_data, student_id, cohort_month, day_needed)
            st.stop()

    _render_diagnosis(day_needed, student_id, cohort_month)
    st.stop()

def mark_pretest_done(nickname: str, cohort: str) -> None:
    pass
