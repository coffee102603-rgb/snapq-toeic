"""
SnapQ TOEIC V2 - 검사 게이트 시스템
1차(1~10일) / 2차(11~24일) / 3차(25~28일) 강제 검사
"""
from __future__ import annotations

import json
import os
import time
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import streamlit as st

# =========================================================
# 검사 일정 설정
# =========================================================
STAGE_1_DAYS = range(1, 11)    # 1일~10일: 1차 사전검사
STAGE_2_DAYS = range(11, 25)   # 11일~24일: 2차 중간검사
STAGE_3_DAYS = range(25, 29)   # 25일~28일: 3차 사후검사

# =========================================================
# 검사 문제 (TOEIC P5 형식, 10문제, 3분)
# =========================================================
TEST_QUESTIONS = [
    {
        "id": "T1",
        "text": "The new marketing strategy _______ a significant increase in sales last quarter.",
        "ch": ["(A) result", "(B) resulted", "(C) results", "(D) resulting"],
        "a": 1,
        "cat": "동사/시제"
    },
    {
        "id": "T2",
        "text": "All employees are required to submit their reports _______ the end of the month.",
        "ch": ["(A) by", "(B) until", "(C) during", "(D) while"],
        "a": 0,
        "cat": "전치사"
    },
    {
        "id": "T3",
        "text": "The manager asked that the project _______ completed before the deadline.",
        "ch": ["(A) is", "(B) was", "(C) be", "(D) being"],
        "a": 2,
        "cat": "가정법"
    },
    {
        "id": "T4",
        "text": "_______ the rain, the outdoor event was postponed until next week.",
        "ch": ["(A) Because of", "(B) Although", "(C) Despite", "(D) However"],
        "a": 0,
        "cat": "접속/연결"
    },
    {
        "id": "T5",
        "text": "The financial report was _______ reviewed by the board of directors.",
        "ch": ["(A) care", "(B) careful", "(C) carefully", "(D) carefulness"],
        "a": 2,
        "cat": "품사/수식"
    },
    {
        "id": "T6",
        "text": "Ms. Chen, _______ has worked here for ten years, will be promoted next month.",
        "ch": ["(A) who", "(B) whom", "(C) which", "(D) whose"],
        "a": 0,
        "cat": "관계절"
    },
    {
        "id": "T7",
        "text": "The company will _______ its annual conference in Seoul this year.",
        "ch": ["(A) hold", "(B) held", "(C) holding", "(D) holds"],
        "a": 0,
        "cat": "동사형태"
    },
    {
        "id": "T8",
        "text": "Please ensure that all documents are _______ before the meeting begins.",
        "ch": ["(A) prepare", "(B) preparation", "(C) prepared", "(D) preparing"],
        "a": 2,
        "cat": "수동태"
    },
    {
        "id": "T9",
        "text": "The new software _______ employees to manage their schedules more efficiently.",
        "ch": ["(A) allows", "(B) allow", "(C) allowed", "(D) allowing"],
        "a": 0,
        "cat": "주어-동사 일치"
    },
    {
        "id": "T10",
        "text": "The budget for next year has not _______ been finalized by the finance team.",
        "ch": ["(A) yet", "(B) already", "(C) still", "(D) ever"],
        "a": 0,
        "cat": "부사"
    },
]

# =========================================================
# 경로 유틸
# =========================================================
def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]

def _cohort_dir(month_key: str) -> Path:
    return _project_root() / "data" / "cohorts" / month_key

def _test_record_path(month_key: str) -> Path:
    return _cohort_dir(month_key) / "test_records.json"

def _get_nickname() -> str:
    for k in ("battle_nickname", "nickname"):
        v = st.session_state.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""

def _get_cohort_month() -> str:
    return st.session_state.get("cohort_month", date.today().strftime("%Y-%m"))

# =========================================================
# 검사 기록 읽기/쓰기
# =========================================================
def _read_records(month_key: str) -> dict:
    path = _test_record_path(month_key)
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def _write_records(month_key: str, data: dict) -> None:
    path = _test_record_path(month_key)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _get_student_tests(nickname: str, month_key: str) -> dict:
    records = _read_records(month_key)
    return records.get(nickname, {"stage1": None, "stage2": None, "stage3": None})

def _save_test_result(nickname: str, month_key: str, stage: int, score: int, answers: list) -> None:
    records = _read_records(month_key)
    if nickname not in records:
        records[nickname] = {"stage1": None, "stage2": None, "stage3": None}
    records[nickname][f"stage{stage}"] = {
        "score": score,
        "total": len(TEST_QUESTIONS),
        "answers": answers,
        "completed_at": datetime.now().isoformat(),
        "date": date.today().strftime("%Y-%m-%d")
    }
    _write_records(month_key, records)

# =========================================================
# 현재 필요한 검사 단계 확인
# =========================================================
def _get_required_stage() -> Optional[int]:
    today = date.today().day
    if today in STAGE_1_DAYS:
        return 1
    elif today in STAGE_2_DAYS:
        return 2
    elif today in STAGE_3_DAYS:
        return 3
    return None

def _stage_name(stage: int) -> str:
    names = {1: "1차 사전검사", 2: "2차 중간검사", 3: "3차 사후검사"}
    return names.get(stage, "검사")

def _stage_color(stage: int) -> str:
    colors = {1: "#00E5FF", 2: "#FFD600", 3: "#FF2D55"}
    return colors.get(stage, "#7C5CFF")

# =========================================================
# 검사 UI
# =========================================================
def _render_test(stage: int, nickname: str, month_key: str) -> None:
    color = _stage_color(stage)
    name = _stage_name(stage)

    st.markdown(f"""
    <style>
    .stApp {{ background: #0D0F1A !important; }}
    .block-container {{ max-width: 600px !important; margin: 0 auto !important; padding: 20px !important; }}
    div.stButton > button {{
        border-radius: 14px !important; font-size: 20px !important;
        font-weight: 900 !important; padding: 16px !important;
    }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

    # 초기화
    if "test_qi" not in st.session_state:
        st.session_state.test_qi = 0
        st.session_state.test_answers = []
        st.session_state.test_start = time.time()
        st.session_state.test_phase = "quiz"

    if st.session_state.get("test_phase") == "result":
        _render_result(stage, nickname, month_key)
        return

    qi = st.session_state.test_qi
    total = len(TEST_QUESTIONS)

    # 헤더
    st.markdown(f"""
    <div style="text-align:center;padding:20px 0 16px;">
        <div style="font-size:13px;font-weight:700;color:{color};letter-spacing:4px;margin-bottom:6px;">
            SnapQ TOEIC · {name}
        </div>
        <div style="font-size:28px;font-weight:900;color:#fff;">
            {qi+1} / {total}
        </div>
        <div style="background:rgba(255,255,255,0.1);border-radius:999px;height:6px;margin:10px 0;">
            <div style="background:{color};height:6px;border-radius:999px;width:{int((qi/total)*100)}%;transition:width 0.3s;"></div>
        </div>
        <div style="font-size:13px;color:rgba(255,255,255,0.4);">⏱ 약 3분 소요 · 편하게 풀어보세요</div>
    </div>
    """, unsafe_allow_html=True)

    q = TEST_QUESTIONS[qi]

    # 문제
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.05);border:2px solid {color}44;border-radius:20px;
                padding:24px;margin:12px 0;text-align:center;">
        <div style="font-size:13px;color:{color};font-weight:700;letter-spacing:2px;margin-bottom:12px;">
            {q['cat']}
        </div>
        <div style="font-size:22px;font-weight:700;color:#fff;line-height:1.6;">
            {q['text']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 선택지
    col1, col2 = st.columns(2)
    for idx, ch in enumerate(q["ch"]):
        col = col1 if idx % 2 == 0 else col2
        with col:
            if st.button(ch, key=f"tq_{qi}_{idx}", use_container_width=True):
                st.session_state.test_answers.append(idx)
                if qi + 1 >= total:
                    st.session_state.test_phase = "result"
                else:
                    st.session_state.test_qi = qi + 1
                st.rerun()

def _render_result(stage: int, nickname: str, month_key: str) -> None:
    answers = st.session_state.test_answers
    score = sum(1 for i, a in enumerate(answers) if a == TEST_QUESTIONS[i]["a"])
    total = len(TEST_QUESTIONS)
    color = _stage_color(stage)
    name = _stage_name(stage)

    # 저장
    _save_test_result(nickname, month_key, stage, score, answers)

    # 결과 화면
    pct = int(score / total * 100)
    emoji = "🏆" if pct >= 80 else "💪" if pct >= 60 else "📚"

    st.markdown(f"""
    <div style="text-align:center;padding:40px 20px;">
        <div style="font-size:72px;margin-bottom:16px;">{emoji}</div>
        <div style="font-size:14px;color:{color};font-weight:700;letter-spacing:4px;margin-bottom:8px;">
            {name} 완료!
        </div>
        <div style="font-size:56px;font-weight:900;color:#fff;margin-bottom:8px;">
            {score} / {total}
        </div>
        <div style="font-size:18px;color:rgba(255,255,255,0.6);margin-bottom:24px;">
            정답률 {pct}%
        </div>
        <div style="font-size:16px;color:rgba(255,255,255,0.5);">
            수고하셨어요! 이제 플랫폼을 이용할 수 있어요 😊
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("⚡ 플랫폼 입장하기", use_container_width=True, type="primary"):
        # 세션 초기화
        for k in ["test_qi", "test_answers", "test_start", "test_phase"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

    st.stop()

# =========================================================
# 강제 검사 안내 화면
# =========================================================
def _render_gate(stage: int, nickname: str) -> None:
    color = _stage_color(stage)
    name = _stage_name(stage)

    st.markdown(f"""
    <style>
    .stApp {{ background: #0D0F1A !important; }}
    .block-container {{ max-width: 500px !important; margin: 0 auto !important; padding: 60px 20px !important; }}
    div.stButton > button {{
        border-radius: 16px !important; font-size: 20px !important;
        font-weight: 900 !important; padding: 18px !important; height: 64px !important;
    }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style="text-align:center;padding:20px 0;">
        <div style="font-size:64px;margin-bottom:16px;">📋</div>
        <div style="font-size:14px;color:{color};font-weight:700;letter-spacing:4px;margin-bottom:8px;">
            MISSION REQUIRED
        </div>
        <div style="font-size:32px;font-weight:900;color:#fff;margin-bottom:12px;">
            {name}
        </div>
        <div style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);
                    border-radius:16px;padding:20px;margin:20px 0;text-align:left;">
            <div style="font-size:16px;color:rgba(255,255,255,0.8);line-height:1.8;">
                ✅ TOEIC P5 문법 10문제<br>
                ✅ 약 3분 소요<br>
                ✅ 완료 후 바로 입장 가능<br>
                ✅ 정답/오답 상관없이 완료만 하면 돼요
            </div>
        </div>
        <div style="font-size:14px;color:rgba(255,255,255,0.4);margin-bottom:24px;">
            안녕하세요 {nickname.split('_')[0]}님! 검사를 완료해야 플랫폼을 이용할 수 있어요.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button(f"📋 {name} 시작하기", use_container_width=True, type="primary"):
        st.session_state.test_qi = 0
        st.session_state.test_answers = []
        st.session_state.test_start = time.time()
        st.session_state.test_phase = "quiz"
        st.session_state.current_test_stage = stage
        st.rerun()

    st.stop()

# =========================================================
# 메인 게이트 함수 (main_hub.py에서 호출)
# =========================================================
def require_pretest_gate() -> None:
    nickname = _get_nickname()
    month_key = _get_cohort_month()

    if not nickname:
        return

    required_stage = _get_required_stage()
    if required_stage is None:
        return  # 검사 기간 아님

    student_tests = _get_student_tests(nickname, month_key)

    # 현재 검사 진행 중이면 계속
    if st.session_state.get("test_phase") in ("quiz", "result"):
        stage = st.session_state.get("current_test_stage", required_stage)
        _render_test(stage, nickname, month_key)
        st.stop()

    # 해당 단계 검사 완료 여부 확인
    stage_key = f"stage{required_stage}"
    if student_tests.get(stage_key) is not None:
        return  # 이미 완료

    # 검사 안 했으면 안내 화면
    _render_gate(required_stage, nickname)


# 하위 호환
def mark_pretest_done(nickname: str, cohort: str) -> None:
    pass
