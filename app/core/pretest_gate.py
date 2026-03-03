"""
SnapQ TOEIC V2 - 검사 게이트 시스템
1차(1~10일) / 2차(11~24일) / 3차(25~28일) 강제 검사
P5 10문제 + P7 1지문 3문제 / 시간 측정 포함
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
# 검사 일정
# =========================================================
STAGE_1_DAYS = range(1, 11)
STAGE_2_DAYS = range(11, 25)
STAGE_3_DAYS = range(25, 29)

# =========================================================
# P5 문제 (10문제)
# =========================================================
P5_QUESTIONS = [
    {
        "id": "T1", "type": "P5",
        "text": "The new marketing strategy _______ a significant increase in sales last quarter.",
        "ch": ["(A) result", "(B) resulted", "(C) results", "(D) resulting"],
        "a": 1, "cat": "동사/시제"
    },
    {
        "id": "T2", "type": "P5",
        "text": "All employees are required to submit their reports _______ the end of the month.",
        "ch": ["(A) by", "(B) until", "(C) during", "(D) while"],
        "a": 0, "cat": "전치사"
    },
    {
        "id": "T3", "type": "P5",
        "text": "The manager asked that the project _______ completed before the deadline.",
        "ch": ["(A) is", "(B) was", "(C) be", "(D) being"],
        "a": 2, "cat": "가정법"
    },
    {
        "id": "T4", "type": "P5",
        "text": "_______ the heavy rain, the outdoor event proceeded as scheduled.",
        "ch": ["(A) Because of", "(B) Although", "(C) Despite", "(D) However"],
        "a": 2, "cat": "접속/연결"
    },
    {
        "id": "T5", "type": "P5",
        "text": "The financial report was _______ reviewed by the board of directors.",
        "ch": ["(A) care", "(B) careful", "(C) carefully", "(D) carefulness"],
        "a": 2, "cat": "품사/수식"
    },
    {
        "id": "T6", "type": "P5",
        "text": "Ms. Chen, _______ has worked here for ten years, will be promoted next month.",
        "ch": ["(A) who", "(B) whom", "(C) which", "(D) whose"],
        "a": 0, "cat": "관계절"
    },
    {
        "id": "T7", "type": "P5",
        "text": "The company will _______ its annual conference in Seoul this year.",
        "ch": ["(A) hold", "(B) held", "(C) holding", "(D) holds"],
        "a": 0, "cat": "동사형태"
    },
    {
        "id": "T8", "type": "P5",
        "text": "Please ensure that all documents are _______ before the meeting begins.",
        "ch": ["(A) prepare", "(B) preparation", "(C) prepared", "(D) preparing"],
        "a": 2, "cat": "수동태"
    },
    {
        "id": "T9", "type": "P5",
        "text": "The new software _______ employees to manage their schedules more efficiently.",
        "ch": ["(A) allows", "(B) allow", "(C) allowed", "(D) allowing"],
        "a": 0, "cat": "주어-동사 일치"
    },
    {
        "id": "T10", "type": "P5",
        "text": "The budget for next year has not _______ been finalized by the finance team.",
        "ch": ["(A) yet", "(B) already", "(C) still", "(D) ever"],
        "a": 0, "cat": "부사"
    },
]

# =========================================================
# P7 지문 + 문제 (1지문 3문제)
# =========================================================
P7_PASSAGE = {
    "title": "Notice",
    "text": """To: All Staff
From: Human Resources Department
Subject: Annual Performance Review Schedule

This year's annual performance reviews will be conducted during the month of March. All employees are required to complete a self-evaluation form by February 28. The forms are available on the company intranet.

Managers will schedule individual meetings with their team members between March 3 and March 21. Each meeting is expected to last approximately 30 minutes. Employees should come prepared to discuss their accomplishments and goals.

Final review documents must be submitted to the Human Resources Department by March 25. Any employee who has questions regarding the review process should contact HR at extension 4521.""",
    "questions": [
        {
            "id": "T11", "type": "P7",
            "text": "What is the purpose of this notice?",
            "ch": [
                "(A) To announce new company policies",
                "(B) To inform employees about performance reviews",
                "(C) To introduce a new HR manager",
                "(D) To explain changes to the intranet"
            ],
            "a": 1
        },
        {
            "id": "T12", "type": "P7",
            "text": "By when must employees submit their self-evaluation forms?",
            "ch": [
                "(A) March 3",
                "(B) March 21",
                "(C) February 28",
                "(D) March 25"
            ],
            "a": 2
        },
        {
            "id": "T13", "type": "P7",
            "text": "How long is each performance review meeting expected to last?",
            "ch": [
                "(A) 20 minutes",
                "(B) 30 minutes",
                "(C) 45 minutes",
                "(D) 60 minutes"
            ],
            "a": 1
        },
    ]
}

ALL_QUESTIONS = P5_QUESTIONS + P7_PASSAGE["questions"]

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
# 검사 기록
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

def _save_test_result(nickname: str, month_key: str, stage: int, score_p5: int, score_p7: int, answers: list, elapsed_sec: float) -> None:
    records = _read_records(month_key)
    if nickname not in records:
        records[nickname] = {"stage1": None, "stage2": None, "stage3": None}
    records[nickname][f"stage{stage}"] = {
        "score_p5": score_p5,
        "score_p7": score_p7,
        "score_total": score_p5 + score_p7,
        "total_p5": len(P5_QUESTIONS),
        "total_p7": len(P7_PASSAGE["questions"]),
        "total": len(ALL_QUESTIONS),
        "answers": answers,
        "elapsed_sec": round(elapsed_sec, 1),
        "completed_at": datetime.now().isoformat(),
        "date": date.today().strftime("%Y-%m-%d")
    }
    _write_records(month_key, records)

# =========================================================
# 단계 정보
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
    return {1: "1차 사전검사", 2: "2차 중간검사", 3: "3차 사후검사"}.get(stage, "검사")

def _stage_color(stage: int) -> str:
    return {1: "#00E5FF", 2: "#FFD600", 3: "#FF2D55"}.get(stage, "#7C5CFF")

# =========================================================
# 공통 CSS
# =========================================================
def _base_css(color: str) -> None:
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700;900&display=swap');
    .stApp {{ background: #0D0F1A !important; font-family: 'Noto Sans KR', sans-serif !important; }}
    .block-container {{ max-width: 640px !important; margin: 0 auto !important; padding: 16px 20px 40px !important; }}
    div.stButton > button {{
        border-radius: 16px !important;
        font-size: 22px !important;
        font-weight: 900 !important;
        padding: 20px !important;
        min-height: 70px !important;
        font-family: 'Noto Sans KR', sans-serif !important;
    }}
    div.stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, {color}, {color}cc) !important;
        border: none !important;
    }}
    div.stButton > button:not([kind="primary"]) {{
        background: rgba(255,255,255,0.06) !important;
        border: 2px solid rgba(255,255,255,0.15) !important;
        color: #fff !important;
    }}
    div.stButton > button:not([kind="primary"]):hover {{
        background: rgba(255,255,255,0.12) !important;
        border-color: {color} !important;
    }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)

# =========================================================
# 검사 안내 화면
# =========================================================
def _render_gate(stage: int, nickname: str) -> None:
    color = _stage_color(stage)
    name = _stage_name(stage)
    _base_css(color)

    student_name = nickname.split('_')[0] if '_' in nickname else nickname

    st.markdown(f"""
    <div style="text-align:center;padding:30px 0 20px;">
        <div style="font-size:80px;margin-bottom:16px;">📋</div>
        <div style="font-size:19px;color:{color};font-weight:900;letter-spacing:4px;margin-bottom:10px;">
            MISSION REQUIRED
        </div>
        <div style="font-size:40px;font-weight:900;color:#fff;margin-bottom:8px;">
            {name}
        </div>
        <div style="font-size:24px;color:rgba(255,255,255,0.8);margin-bottom:24px;font-weight:900;">
            {student_name}님, 검사를 완료해야 입장할 수 있어요!
        </div>
    </div>

    <div style="background:rgba(255,255,255,0.05);border:2px solid rgba(255,255,255,0.1);
                border-radius:20px;padding:28px;margin-bottom:24px;">
        <div style="font-size:26px;font-weight:900;color:#fff;margin-bottom:20px;">📌 검사 안내</div>
        <div style="font-size:24px;font-weight:900;color:rgba(255,255,255,0.95);line-height:2.4;">
            ✅ &nbsp;P5 문법 문제 · <b style="color:{color}">10문제</b><br>
            ✅ &nbsp;P7 독해 지문 · <b style="color:{color}">1지문 3문제</b><br>
            ✅ &nbsp;총 <b style="color:{color}">13문제</b> · 약 <b style="color:{color}">5분</b> 소요<br>
            ✅ &nbsp;풀이 시간이 자동으로 기록돼요<br>
            ✅ &nbsp;정답/오답 <b style="color:{color}">상관없이</b> 완료만 하면 돼요!
        </div>
    </div>
    """, unsafe_allow_html=True)

    # HTML 버튼으로 직접 렌더링
    st.markdown(f"""
    <style>
    .start-btn {{
        display: block; width: 100%; padding: 26px;
        background: linear-gradient(135deg, {color}, {color}cc);
        border: none; border-radius: 18px; cursor: pointer;
        font-size: 32px; font-weight: 900; color: #000000;
        text-align: center; margin-top: 8px;
    }}
    .start-btn:hover {{ opacity: 0.9; }}
    </style>
    <form method="get">
        <button class="start-btn" name="start_test" value="1" type="submit">
            📋 {name} 시작하기
        </button>
    </form>
    """, unsafe_allow_html=True)

    if st.query_params.get("start_test") == "1":
        st.query_params.clear()
        st.session_state.test_qi = 0
        st.session_state.test_answers = []
        st.session_state.test_start = time.time()
        st.session_state.test_phase = "p5"
        st.session_state.current_test_stage = stage
        st.rerun()

    st.stop()

# =========================================================
# P5 문제 화면
# =========================================================
def _render_p5(stage: int, nickname: str, month_key: str) -> None:
    color = _stage_color(stage)
    name = _stage_name(stage)
    _base_css(color)
    st.markdown(f"""
    <style>
    div.stButton > button {{
        font-size: 30px !important;
        font-weight: 900 !important;
        text-shadow: 0 1px 4px rgba(0,0,0,0.5) !important;
        min-height: 80px !important;
        letter-spacing: 0.5px !important;
    }}
    div.stButton > button[kind="primary"] {{
        color: #000 !important;
        text-shadow: none !important;
        font-size: 28px !important;
        font-weight: 900 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    qi = st.session_state.test_qi
    total_p5 = len(P5_QUESTIONS)
    elapsed = int(time.time() - st.session_state.test_start)

    # 진행바
    st.markdown(f"""
    <div style="text-align:center;padding:16px 0 12px;">
        <div style="font-size:15px;color:{color};font-weight:700;letter-spacing:3px;margin-bottom:6px;">
            SnapQ TOEIC · {name} · P5 문법
        </div>
        <div style="font-size:36px;font-weight:900;color:#fff;margin-bottom:8px;">
            {qi+1} / {total_p5}
        </div>
        <div style="background:rgba(255,255,255,0.1);border-radius:999px;height:8px;margin:0 0 8px;">
            <div style="background:{color};height:8px;border-radius:999px;width:{int((qi/total_p5)*100)}%;transition:width 0.3s;"></div>
        </div>
        <div style="font-size:16px;color:rgba(255,255,255,0.4);">⏱ {elapsed}초 경과</div>
    </div>
    """, unsafe_allow_html=True)

    q = P5_QUESTIONS[qi]

    # 문제 박스
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.05);border:2px solid {color}55;
                border-radius:20px;padding:28px;margin:12px 0 20px;text-align:center;">
        <div style="font-size:20px;color:{color};font-weight:900;letter-spacing:2px;margin-bottom:14px;">
            {q['cat']}
        </div>
        <div style="font-size:34px;font-weight:900;color:#fff;line-height:1.7;
                    text-shadow:0 1px 4px rgba(0,0,0,0.5);">
            {q['text']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 선택지 버튼 - components.html로 직접 렌더링
    import streamlit.components.v1 as components
    choices_html = ""
    for idx, ch in enumerate(q["ch"]):
        row = idx // 2
        choices_html += f"""
        <button onclick="window.parent.postMessage({{type:'p5_choice',idx:{idx},qi:{qi}}}, '*')"
                style="width:48%;margin:1%;padding:22px 10px;font-size:28px;font-weight:900;
                       background:rgba(255,255,255,0.06);border:2px solid rgba(255,255,255,0.15);
                       border-radius:16px;color:#fff;cursor:pointer;display:inline-block;
                       text-shadow:0 1px 4px rgba(0,0,0,0.5);">
            {ch}
        </button>"""

    for idx, ch in enumerate(q["ch"]):
        if st.button(ch, key=f"p5_{qi}_{idx}", use_container_width=False):
            st.session_state.test_answers.append({
                "q_id": q["id"],
                "type": "P5",
                "selected": idx,
                "correct": idx == q["a"],
                "time_sec": round(time.time() - st.session_state.test_start, 1)
            })
            if qi + 1 >= total_p5:
                st.session_state.test_phase = "p7_intro"
                st.session_state.test_qi = 0
            else:
                st.session_state.test_qi = qi + 1
            st.rerun()

    st.markdown("""
    <style>
    /* P5 선택지 버튼 강제 크기 */
    section[data-testid="stMain"] button p {
        font-size: 28px !important;
        font-weight: 900 !important;
        line-height: 1.4 !important;
    }
    section[data-testid="stMain"] button {
        min-height: 80px !important;
        font-size: 28px !important;
        font-weight: 900 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================================================
# P7 지문 소개 화면
# =========================================================
def _render_p7_intro(stage: int) -> None:
    color = _stage_color(stage)
    _base_css(color)
    st.markdown(f"""
    <style>
    div.stButton > button {{
        font-size: 34px !important;
        font-weight: 900 !important;
        min-height: 90px !important;
        letter-spacing: 0.5px !important;
        text-shadow: 0 1px 4px rgba(0,0,0,0.5) !important;
    }}
    div.stButton > button[kind="primary"] {{
        color: #000 !important;
        text-shadow: none !important;
        font-size: 34px !important;
        font-weight: 900 !important;
    }}
    div.stButton > button p {{
        font-size: 34px !important;
        font-weight: 900 !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    elapsed = int(time.time() - st.session_state.get("test_start", time.time()))
    minutes = elapsed // 60
    seconds = elapsed % 60

    st.markdown(f"""
    <div style="text-align:center;padding:16px 0 12px;">
        <div style="font-size:15px;color:{color};font-weight:700;letter-spacing:3px;margin-bottom:6px;">
            P5 완료! · 다음은 P7 독해
        </div>
        <div style="font-size:36px;font-weight:900;color:#fff;margin-bottom:6px;">
            📖 지문 읽기
        </div>
        <div style="font-size:16px;color:rgba(255,255,255,0.4);margin-bottom:16px;">
            ⏱ {minutes}분 {seconds}초 경과 · 타이머 압박 없어요, 천천히 읽으세요!
        </div>
    </div>
    """, unsafe_allow_html=True)

    # P7 전장 스타일 지문 박스
    passage_lines = P7_PASSAGE['text'].strip().replace('\n', '<br>')
    st.markdown(f"""
    <style>
    .block-container {{ padding-left: 8px !important; padding-right: 8px !important; max-width: 100% !important; }}
    </style>
    <div style="background:rgba(255,255,255,0.04);border:2px solid {color}55;
                border-radius:16px;padding:20px 16px;margin-bottom:16px;">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;
                    border-bottom:1px solid rgba(255,255,255,0.1);padding-bottom:12px;">
            <span style="font-size:30px;">📄</span>
            <span style="font-size:26px;color:{color};font-weight:900;letter-spacing:2px;">
                {P7_PASSAGE['title'].upper()}
            </span>
        </div>
        <div style="font-size:28px;font-weight:700;color:rgba(255,255,255,0.95);line-height:2.1;word-break:keep-all;text-shadow:0 1px 3px rgba(0,0,0,0.4);">
            {passage_lines}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("✅  지문 읽었어요 → 문제 풀기", use_container_width=True, type="primary"):
        st.session_state.test_phase = "p7"
        st.session_state.test_qi = 0
        st.rerun()

# =========================================================
# P7 문제 화면
# =========================================================
def _render_p7(stage: int, nickname: str, month_key: str) -> None:
    color = _stage_color(stage)
    name = _stage_name(stage)
    _base_css(color)
    st.markdown(f"""
    <style>
    div.stButton > button {{
        font-size: 30px !important;
        font-weight: 900 !important;
        min-height: 84px !important;
        text-shadow: 0 1px 4px rgba(0,0,0,0.5) !important;
        letter-spacing: 0.3px !important;
    }}
    div.stButton > button p {{
        font-size: 30px !important;
        font-weight: 900 !important;
    }}
    div.stButton > button[kind="primary"] {{
        color: #000 !important;
        text-shadow: none !important;
    }}
    </style>
    """, unsafe_allow_html=True)

    qi = st.session_state.test_qi
    questions = P7_PASSAGE["questions"]
    total_p7 = len(questions)
    elapsed = int(time.time() - st.session_state.test_start)

    # 진행바
    st.markdown(f"""
    <div style="text-align:center;padding:16px 0 12px;">
        <div style="font-size:15px;color:{color};font-weight:700;letter-spacing:3px;margin-bottom:6px;">
            SnapQ TOEIC · {name} · P7 독해
        </div>
        <div style="font-size:36px;font-weight:900;color:#fff;margin-bottom:8px;">
            {qi+1} / {total_p7}
        </div>
        <div style="background:rgba(255,255,255,0.1);border-radius:999px;height:8px;margin:0 0 8px;">
            <div style="background:{color};height:8px;border-radius:999px;width:{int(((qi)/total_p7)*100)}%;transition:width 0.3s;"></div>
        </div>
        <div style="font-size:16px;color:rgba(255,255,255,0.4);">⏱ {elapsed}초 경과 · P7 {qi+1}/{total_p7}</div>
    </div>
    """, unsafe_allow_html=True)

    q = questions[qi]

    # 문제
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.05);border:2px solid {color}55;
                border-radius:20px;padding:28px;margin:12px 0 20px;text-align:center;">
        <div style="font-size:30px;font-weight:900;color:#fff;line-height:1.7;
                    text-shadow:0 1px 4px rgba(0,0,0,0.5);">
            {q['text']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 선택지
    for idx, ch in enumerate(q["ch"]):
        if st.button(ch, key=f"p7_{qi}_{idx}", use_container_width=True):
            st.session_state.test_answers.append({
                "q_id": q["id"],
                "type": "P7",
                "selected": idx,
                "correct": idx == q["a"],
                "time_sec": round(time.time() - st.session_state.test_start, 1)
            })
            if qi + 1 >= total_p7:
                st.session_state.test_phase = "result"
            else:
                st.session_state.test_qi = qi + 1
            st.rerun()

# =========================================================
# 결과 화면
# =========================================================
def _render_result(stage: int, nickname: str, month_key: str) -> None:
    color = _stage_color(stage)
    name = _stage_name(stage)
    _base_css(color)

    answers = st.session_state.test_answers
    elapsed = round(time.time() - st.session_state.test_start, 1)

    p5_ans = [a for a in answers if a["type"] == "P5"]
    p7_ans = [a for a in answers if a["type"] == "P7"]
    score_p5 = sum(1 for a in p5_ans if a["correct"])
    score_p7 = sum(1 for a in p7_ans if a["correct"])
    total = score_p5 + score_p7
    max_total = len(ALL_QUESTIONS)

    # 저장
    _save_test_result(nickname, month_key, stage, score_p5, score_p7, answers, elapsed)

    pct = int(total / max_total * 100)
    emoji = "🏆" if pct >= 80 else "💪" if pct >= 60 else "📚"
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    student_name = nickname.split('_')[0] if '_' in nickname else nickname

    st.markdown(f"""
    <div style="text-align:center;padding:30px 0 20px;">
        <div style="font-size:80px;margin-bottom:16px;">{emoji}</div>
        <div style="font-size:22px;color:{color};font-weight:900;letter-spacing:4px;margin-bottom:10px;">
            {name} 완료!
        </div>
        <div style="font-size:56px;font-weight:900;color:#fff;margin-bottom:4px;">
            {total} / {max_total}
        </div>
        <div style="font-size:26px;color:rgba(255,255,255,0.7);font-weight:900;margin-bottom:24px;">
            정답률 {pct}%
        </div>
    </div>

    <div style="background:rgba(255,255,255,0.05);border:2px solid rgba(255,255,255,0.1);
                border-radius:20px;padding:28px;margin-bottom:24px;">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
            <div style="font-size:26px;color:rgba(255,255,255,0.9);font-weight:900;">P5 문법</div>
            <div style="font-size:30px;font-weight:900;color:{color};">{score_p5} / {len(P5_QUESTIONS)}</div>
        </div>
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
            <div style="font-size:26px;color:rgba(255,255,255,0.9);font-weight:900;">P7 독해</div>
            <div style="font-size:30px;font-weight:900;color:{color};">{score_p7} / {len(P7_PASSAGE['questions'])}</div>
        </div>
        <div style="border-top:1px solid rgba(255,255,255,0.1);padding-top:20px;
                    display:flex;justify-content:space-between;align-items:center;">
            <div style="font-size:26px;color:rgba(255,255,255,0.9);font-weight:900;">⏱ 풀이 시간</div>
            <div style="font-size:30px;font-weight:900;color:#fff;">{minutes}분 {seconds}초</div>
        </div>
    </div>

    <div style="text-align:center;font-size:22px;color:rgba(255,255,255,0.7);margin-bottom:20px;font-weight:900;">
        수고하셨어요, {student_name}님! 이제 플랫폼을 이용할 수 있어요 😊
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <style>
    div.stButton > button[kind="primary"] p {
        color: #000 !important;
        font-size: 26px !important;
        font-weight: 900 !important;
    }
    div.stButton > button[kind="primary"] {
        color: #000 !important;
        font-size: 26px !important;
        font-weight: 900 !important;
        min-height: 80px !important;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.button("⚡  플랫폼 입장하기", use_container_width=True, type="primary"):
        for k in ["test_qi", "test_answers", "test_start", "test_phase", "current_test_stage"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

    st.stop()

# =========================================================
# 메인 게이트 (main_hub.py에서 호출)
# =========================================================
def require_pretest_gate() -> None:
    nickname = _get_nickname()
    month_key = _get_cohort_month()

    if not nickname:
        return

    required_stage = _get_required_stage()
    if required_stage is None:
        return

    # 검사 진행 중
    phase = st.session_state.get("test_phase")
    stage = st.session_state.get("current_test_stage", required_stage)

    if phase == "p5":
        _render_p5(stage, nickname, month_key)
        st.stop()
    elif phase == "p7_intro":
        _render_p7_intro(stage)
        st.stop()
    elif phase == "p7":
        _render_p7(stage, nickname, month_key)
        st.stop()
    elif phase == "result":
        _render_result(stage, nickname, month_key)
        st.stop()

    # 완료 여부 확인
    student_tests = _get_student_tests(nickname, month_key)
    if student_tests.get(f"stage{required_stage}") is not None:
        return  # 이미 완료

    # 검사 안내 화면
    _render_gate(required_stage, nickname)


def mark_pretest_done(nickname: str, cohort: str) -> None:
    pass
