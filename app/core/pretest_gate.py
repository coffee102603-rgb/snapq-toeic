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
.stApp{background:linear-gradient(160deg,#07090f 0%,#050810 60%,#000000 100%);}
.block-container{padding-top:1.5rem;max-width:600px;}
.diag-header{background:linear-gradient(135deg,rgba(255,170,0,0.15),rgba(255,60,0,0.1));border:1px solid rgba(255,170,0,0.3);border-radius:16px;padding:16px 20px;margin-bottom:1.2rem;}
.diag-title{font-size:1.4rem;font-weight:900;color:#ffaa00;margin-bottom:4px;}
.diag-sub{font-size:0.85rem;color:rgba(255,255,255,0.6);}
.progress-bar-wrap{background:rgba(255,255,255,0.08);border-radius:99px;height:8px;margin:12px 0 4px;overflow:hidden;}
.progress-bar-fill{height:8px;border-radius:99px;background:linear-gradient(90deg,#ffaa00,#ff6600);}
.q-box{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:14px;padding:18px 20px;margin-bottom:1rem;}
.q-num{font-size:0.9rem;font-weight:700;color:#ffaa00;margin-bottom:8px;}
.q-text{font-size:1.05rem;font-weight:700;color:#ffffff;line-height:1.5;}
.passage-box{background:rgba(255,255,255,0.04);border-left:3px solid rgba(255,170,0,0.5);border-radius:0 12px 12px 0;padding:14px 16px;font-size:0.88rem;color:rgba(255,255,255,0.8);line-height:1.7;margin-bottom:1.2rem;white-space:pre-line;}
.result-box{background:rgba(0,200,100,0.1);border:1px solid rgba(0,200,100,0.3);border-radius:16px;padding:24px;text-align:center;margin:1rem 0;}
.result-score{font-size:3rem;font-weight:900;color:#00ff88;}
.result-label{font-size:0.9rem;color:rgba(255,255,255,0.6);margin-top:4px;}
div[data-testid="stRadio"] label{color:rgba(255,255,255,0.85)!important;font-size:0.95rem!important;}
div[data-testid="stButton"] button{background:linear-gradient(135deg,#ffaa00,#ff6600)!important;color:#000!important;font-weight:900!important;font-size:1rem!important;border-radius:14px!important;border:none!important;padding:0.7rem!important;width:100%!important;}
</style>
""", unsafe_allow_html=True)

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
    if st.button("✅ 진단 제출 → 전장 입장", disabled=not all_answered, key="diag_submit_btn"):
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
        msg = "🏆 훌륭합니다! 상위권 실력이에요!"
    elif total_score >= 70:
        msg = "💪 좋아요! 조금만 더 노력하면 최상위권!"
    elif total_score >= 50:
        msg = "📚 기초를 잡아가고 있어요. 꾸준히 도전!"
    else:
        msg = "🔥 지금부터 시작이에요! 전장에서 실력을 키워요!"
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
    _render_diagnosis(day_needed, student_id, cohort_month)
    st.stop()

def mark_pretest_done(nickname: str, cohort: str) -> None:
    pass
