"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE:     pretest_gate.py
ROLE:     검사·설문 게이트 — 사전/중간/사후 TOEIC 검사 + 리커트 설문
VERSION:  SnapQ TOEIC V3 — 2026.04.23 전면 재작성
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FLOW:
    1차 (1~10일):  설문 A~F (24문항) → TOEIC 검사 (10문항) → 입장
    2차 (11~24일): TOEIC 검사만 (10문항) → 입장
    3차 (25~28일): TOEIC 검사 (10문항) → 설문 A~G (29문항) → 입장

DATA OUT:
    로컬:   data/cohorts/YYYY-MM/test_records.json
    Sheets: survey_responses 시트, pretest_scores 시트

PAPERS:
    ① 설계원리:    A+B → 학습자 요구 분석 근거
    ② ADDIE:       B+F+G5 → 사용자 피드백
    ④ AI 분류:     D → 자기 효능감 vs rt_logs 교차 검증
    ⑤ 탐색적 분석: A~F 전체 → 로그와 인식 변화 교차 (핵심!)
    ⑥ 크로스스킬:  E4 → "독해→문법 전이" 자기 인식 vs cross_logs
    ⑦ ZPD:         D4+G3 → 시간 압박 효능감 + 적응형 만족도
    ⑧ 교사 AI:     C3+G4 → AI 피드백 인식 변화
    ⑨ 수업 통합:   C → 기술 수용성
    ⑩ SSCI 통합:   A~F 사전사후 변화량 (대규모)
    ⑪ 박사논문:    전체 + G5 질적 데이터

AI-AGENT NOTES:
    [핵심 설계 — 임계값(Threshold) 포커스]
    설문 B3, B4, D4, E2는 임계값 철학의 핵심 변수:
    - B3: "틀린 문제를 다시 풀면 실력이 오를 것 같다" → 재도전 임계값
    - B4: "도전적인 목표가 있으면 더 몰입한다" → 목표 임계값
    - D4: "시간 압박 속에서도 정답을 고를 수 있다" → RT 임계값 효능감
    - E2: "틀린 문제를 반드시 다시 확인한다" → 망각곡선 임계값

    [수정 주의사항]
    - SURVEY_ITEMS 순서 변경 시 survey_responses 시트 헤더도 변경 필수
    - _save_to_sheets() 실패해도 게임 계속 (try/except)
    - stage 1/2/3 흐름은 require_pretest_gate()에서 제어
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
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
# 검사 일정 설정 — 개인 첫 접속일 기준 Day 카운트
# ─────────────────────────────────────────────────────────
# AI-AGENT NOTE:
#   기존: 매월 1~10일=사전, 11~24일=중간, 25~28일=사후 (달력 하드코딩)
#   변경: 개인 첫 접속(registered_at) 기준으로 Day N 계산
#
#   DAY 1          → 사전 (설문 A~F + 검사 10문제)
#   DAY 8 ~ 14     → 중간 (검사만, 7일 창)
#   DAY 21 ~       → 사후 (검사 + 설문 A~G, 마감 없음)
#
#   근거 (논문별):
#   - 7일+7일 대칭 → ⑤⑩ 1주 단위 변화량 비교 깔끔
#   - 중간 7일 창  → 매일 안 오는 학생도 놓치지 않음
#   - 사후 마감 없음 → 23일/28일 학원 모두 커버
#   - 사전 100% 확보 → ⑤⑩ paired t-test 표본 손실 0
#
#   장기 수강생: 사전/중간/사후 각 1회만 (완료 플래그)
#   이후에는 게이트 없이 바로 입장 → rt_logs만 계속 누적
# =========================================================
PRE_DAY     = 1          # Day 1: 사전 (첫 접속일)
MID_START   = 8          # Day 8~14: 중간 검사 창
MID_END     = 14
POST_START  = 21         # Day 21~: 사후 (마감 없음)


# =========================================================
# 설문 문항 — 임계값(Threshold) 중심 설계
# ─────────────────────────────────────────────────────────
# 카테고리별 4문항 × 6카테고리 = 24문항 (사전+사후 공통)
# + 사후 전용 G 5문항 = 총 29문항 (사후)
# =========================================================
SURVEY_ITEMS = {
    # ── A. 영어 학습 동기·태도 → ①⑤⑩⑪ ──
    "A1": "영어 문법 공부가 재미있다",
    "A2": "TOEIC 점수를 올리고 싶은 마음이 강하다",
    "A3": "혼자서도 영어 공부를 꾸준히 할 수 있다",
    "A4": "영어 공부에 자신감이 있다",
    # ── B. 게이미피케이션·임계값 인식 → ①②⑤⑩ ── ★ THRESHOLD CORE
    "B1": "게임처럼 점수·랭킹이 있으면 더 열심히 공부한다",
    "B2": "시간 제한이 있으면 더 집중된다",
    "B3": "틀린 문제를 다시 풀면 실력이 오를 것 같다",          # 재도전 임계값
    "B4": "도전적인 목표가 있으면 더 몰입한다",                 # 목표 임계값
    # ── C. AI·기술 학습 환경 인식 → ⑤⑧⑨⑪ ──
    "C1": "AI가 내 수준에 맞춰주면 더 효과적일 것 같다",
    "C2": "앱이나 웹으로 공부하는 것이 교재보다 편하다",
    "C3": "AI가 내 약점을 알려주면 도움이 될 것 같다",
    "C4": "기술(앱/AI)을 활용한 학습에 거부감이 없다",
    # ── D. 자기 효능감 → ④⑦⑩⑪ ── ★ THRESHOLD CORE
    "D1": "나는 TOEIC P5 문법 문제를 잘 풀 수 있다",
    "D2": "어려운 문법이라도 연습하면 이해할 수 있다",
    "D3": "영어 독해 지문을 정확히 읽을 수 있다",
    "D4": "시간 압박 속에서도 정답을 고를 수 있다",              # RT 임계값 효능감
    # ── E. 학습 전략·습관 → ⑤⑥⑦ ── ★ THRESHOLD CORE
    "E1": "모르는 단어를 만나면 바로 찾아보는 편이다",
    "E2": "틀린 문제를 반드시 다시 확인한다",                    # 망각곡선 임계값
    "E3": "문법 문제를 풀 때 문장 전체를 읽고 푼다",
    "E4": "독해에서 배운 표현을 문법에 적용해본 적이 있다",      # 크로스스킬
    # ── F. 몰입·지속 의향 → ②⑤⑩⑪ ──
    "F1": "한 번 시작하면 쉽게 멈추기 어렵다",
    "F2": "매일 조금씩이라도 영어 공부를 하고 싶다",
    "F3": "이런 학습 앱을 계속 사용하고 싶다",
    "F4": "친구에게도 추천하고 싶다",
}

# 사후 전용 (G) — 리커트 4문항 + 주관식 1문항
SURVEY_POST_ONLY = {
    "G1": "SnapQ가 영어 실력 향상에 도움이 되었다",
    "G2_choice": "가장 도움이 된 모드는?",  # 선택형
    "G3": "난이도가 자동으로 바뀌는 것이 도움이 되었다",        # 논문 ⑦
    "G4": "NPC(토리/해이) 메시지가 동기부여에 도움이 되었다",   # 논문 ⑧
    "G5_open": "한 줄 소감을 자유롭게 적어주세요",               # 질적 데이터
}

LIKERT_OPTIONS = ["전혀 아니다", "아니다", "보통이다", "그렇다", "매우 그렇다"]
G2_CHOICES = ["⚡ 화력전 (문법 5문제)", "📡 암호해독 (독해 3문제)", "💀 포로사령부 (오답 복습)"]


# =========================================================
# TOEIC 검사 문제 (10문제)
# =========================================================
TEST_QUESTIONS = [
    {"id": "T1", "text": "The new marketing strategy _______ a significant increase in sales last quarter.",
     "ch": ["(A) result", "(B) resulted", "(C) results", "(D) resulting"], "a": 1, "cat": "동사/시제"},
    {"id": "T2", "text": "All employees are required to submit their reports _______ the end of the month.",
     "ch": ["(A) by", "(B) until", "(C) during", "(D) while"], "a": 0, "cat": "전치사"},
    {"id": "T3", "text": "The manager asked that the project _______ completed before the deadline.",
     "ch": ["(A) is", "(B) was", "(C) be", "(D) being"], "a": 2, "cat": "가정법"},
    {"id": "T4", "text": "_______ the rain, the outdoor event was postponed until next week.",
     "ch": ["(A) Because of", "(B) Although", "(C) Despite", "(D) However"], "a": 0, "cat": "접속/연결"},
    {"id": "T5", "text": "The financial report was _______ reviewed by the board of directors.",
     "ch": ["(A) care", "(B) careful", "(C) carefully", "(D) carefulness"], "a": 2, "cat": "품사/수식"},
    {"id": "T6", "text": "Ms. Chen, _______ has worked here for ten years, will be promoted next month.",
     "ch": ["(A) who", "(B) whom", "(C) which", "(D) whose"], "a": 0, "cat": "관계절"},
    {"id": "T7", "text": "The company will _______ its annual conference in Seoul this year.",
     "ch": ["(A) hold", "(B) held", "(C) holding", "(D) holds"], "a": 0, "cat": "동사형태"},
    {"id": "T8", "text": "Please ensure that all documents are _______ before the meeting begins.",
     "ch": ["(A) prepare", "(B) preparation", "(C) prepared", "(D) preparing"], "a": 2, "cat": "수동태"},
    {"id": "T9", "text": "The new software _______ employees to manage their schedules more efficiently.",
     "ch": ["(A) allows", "(B) allow", "(C) allowed", "(D) allowing"], "a": 0, "cat": "주어-동사 일치"},
    {"id": "T10", "text": "The budget for next year has not _______ been finalized by the finance team.",
     "ch": ["(A) yet", "(B) already", "(C) still", "(D) ever"], "a": 0, "cat": "부사"},
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
# 기록 읽기/쓰기 (로컬 JSON)
# =========================================================
def _read_records(month_key: str) -> dict:
    path = _test_record_path(month_key)
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def _write_records(month_key: str, data: dict) -> None:
    path = _test_record_path(month_key)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def _get_student_tests(nickname: str, month_key: str) -> dict:
    records = _read_records(month_key)
    return records.get(nickname, {
        "stage1": None, "stage2": None, "stage3": None,
        "survey_pre": None, "survey_post": None,
    })


# =========================================================
# Google Sheets 저장 (이중 기록 — 원칙 5)
# ─────────────────────────────────────────────────────────
# AI-AGENT NOTE:
#   실패해도 게임 계속 (try/except).
#   survey_responses / pretest_scores 시트에 자동 저장.
# =========================================================
def _save_to_sheets(sheet_name: str, entry: dict) -> bool:
    try:
        import gspread
        gc = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
        sh = gc.open_by_key(st.secrets["SPREADSHEET_ID"])
        headers = list(entry.keys())
        try:
            ws = sh.worksheet(sheet_name)
        except Exception:
            ws = sh.add_worksheet(title=sheet_name, rows=5000, cols=len(headers))
            ws.append_row(headers)
        if not ws.row_values(1):
            ws.append_row(headers)
        row = [str(entry.get(h, "")) if entry.get(h) is not None else "" for h in headers]
        ws.append_row(row)
        return True
    except Exception:
        return False


# =========================================================
# 검사 결과 저장 (로컬 + Sheets)
# =========================================================
def _save_test_result(nickname: str, month_key: str, stage: int,
                      score: int, answers: list) -> None:
    # 1) 로컬 JSON
    records = _read_records(month_key)
    if nickname not in records:
        records[nickname] = {
            "stage1": None, "stage2": None, "stage3": None,
            "survey_pre": None, "survey_post": None,
        }
    records[nickname][f"stage{stage}"] = {
        "score": score,
        "total": len(TEST_QUESTIONS),
        "answers": answers,
        "completed_at": datetime.now().isoformat(),
        "date": date.today().strftime("%Y-%m-%d"),
    }
    _write_records(month_key, records)

    # 2) Sheets 이중 저장
    try:
        _save_to_sheets("pretest_scores", {
            "timestamp": datetime.now().isoformat(),
            "user_id": nickname,
            "stage": stage,
            "score": score,
            "total": len(TEST_QUESTIONS),
            "pct": round(score / len(TEST_QUESTIONS) * 100, 1),
            "answers": json.dumps(answers),
            "month": month_key,
            "research_phase": "pre_irb",
        })
    except Exception:
        pass


# =========================================================
# 설문 결과 저장 (로컬 + Sheets)
# =========================================================
def _save_survey_result(nickname: str, month_key: str,
                        survey_type: str, responses: dict) -> None:
    """
    survey_type: "pre" or "post"
    responses: {"A1": 4, "A2": 5, ..., "G5_open": "재밌었어요"}
    """
    # 1) 로컬 JSON
    records = _read_records(month_key)
    if nickname not in records:
        records[nickname] = {
            "stage1": None, "stage2": None, "stage3": None,
            "survey_pre": None, "survey_post": None,
        }
    records[nickname][f"survey_{survey_type}"] = {
        "responses": responses,
        "completed_at": datetime.now().isoformat(),
        "date": date.today().strftime("%Y-%m-%d"),
    }
    _write_records(month_key, records)

    # 2) Sheets 이중 저장
    try:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "user_id": nickname,
            "survey_type": survey_type,  # pre / post
            "month": month_key,
            "research_phase": "pre_irb",
        }
        # 각 문항 응답을 개별 컬럼으로
        for key, val in responses.items():
            entry[key] = val
        _save_to_sheets("survey_responses", entry)
    except Exception:
        pass


# =========================================================
# 단계 판별 — 개인 첫 접속일 기준
# ─────────────────────────────────────────────────────────
# AI-AGENT NOTE:
#   _get_user_day(): roster.jsonl에서 registered_at 읽어서
#   오늘이 첫 접속으로부터 며칠째인지 계산.
#   roster 파일 못 찾으면 Day 1 (첫 접속) 처리.
#
#   _get_required_stage(): Day 카운트로 stage 1/2/3 반환.
#   Day 1 = 사전, Day 8~14 = 중간, Day 21~ = 사후
#   그 사이(Day 2~7, 15~20)는 None → 게이트 없이 입장.
# =========================================================
def _get_user_day(nickname: str, month_key: str) -> int:
    """개인 첫 접속일(registered_at) 기준 오늘이 며칠째인지 반환."""
    try:
        roster_path = _cohort_dir(month_key) / "roster.jsonl"
        if not roster_path.exists():
            return 1  # roster 없음 = 첫 접속
        with open(roster_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line.strip())
                    if r.get("nickname") == nickname:
                        reg = r.get("registered_at", "")
                        if reg:
                            reg_date = datetime.fromisoformat(reg).date()
                            delta = (date.today() - reg_date).days
                            return max(1, delta + 1)  # Day 1부터 시작
                except Exception:
                    continue
    except Exception:
        pass
    return 1  # fallback = 첫 접속 취급


def _get_required_stage(nickname: str = "", month_key: str = "") -> Optional[int]:
    """개인 Day 기준으로 필요한 검사 단계 반환."""
    day = _get_user_day(nickname, month_key)

    if day == PRE_DAY:
        return 1   # Day 1: 사전
    elif MID_START <= day <= MID_END:
        return 2   # Day 8~14: 중간
    elif day >= POST_START:
        return 3   # Day 21~: 사후
    return None    # Day 2~7, 15~20: 검사 없음 → 바로 입장

def _stage_name(stage: int) -> str:
    names = {1: "사전검사", 2: "중간검사", 3: "사후검사"}
    return names.get(stage, "검사")

def _stage_color(stage: int) -> str:
    colors = {1: "#00E5FF", 2: "#FFD600", 3: "#FF2D55"}
    return colors.get(stage, "#7C5CFF")


# =========================================================
# 공통 CSS
# =========================================================
def _inject_gate_css(color: str = "#7C5CFF") -> None:
    st.markdown(f"""
    <style>
    .stApp {{ background: #0D0F1A !important; }}
    .block-container {{ max-width: 600px !important; margin: 0 auto !important; padding: 20px !important; }}
    div.stButton > button {{
        border-radius: 14px !important; font-size: 18px !important;
        font-weight: 900 !important; padding: 14px !important;
        touch-action: manipulation !important;
    }}
    div.stRadio > label {{ color: #ffffff !important; font-size: 16px !important; }}
    div[data-testid="stRadio"] label span {{ color: #ffffff !important; }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)


# =========================================================
# 설문 UI
# =========================================================
def _render_survey(survey_type: str, nickname: str, month_key: str) -> None:
    """
    survey_type: "pre" (사전) or "post" (사후)
    사전: A~F 24문항 | 사후: A~F + G 29문항
    """
    color = "#00E5FF" if survey_type == "pre" else "#FF2D55"
    _inject_gate_css(color)

    # 초기화
    if "survey_qi" not in st.session_state:
        st.session_state.survey_qi = 0
        st.session_state.survey_responses = {}
        st.session_state.survey_phase = "answering"

    # 문항 리스트 구성
    items = list(SURVEY_ITEMS.items())
    if survey_type == "post":
        items += list(SURVEY_POST_ONLY.items())
    total = len(items)
    qi = st.session_state.survey_qi

    # 완료 체크
    if qi >= total:
        _save_survey_result(nickname, month_key, survey_type,
                            st.session_state.survey_responses)
        # 세션 정리
        for k in ["survey_qi", "survey_responses", "survey_phase"]:
            if k in st.session_state:
                del st.session_state[k]
        # 플래그 설정 (검사로 넘어가거나 완료)
        st.session_state[f"_survey_{survey_type}_done"] = True
        st.rerun()
        return

    key, text = items[qi]
    cat_letter = key[0]
    cat_names = {"A": "영어 학습 동기", "B": "게이미피케이션 인식",
                 "C": "AI 학습 환경", "D": "자기 효능감",
                 "E": "학습 전략", "F": "몰입·지속", "G": "사용 경험"}
    cat_name = cat_names.get(cat_letter, "설문")
    label_type = "사전 설문" if survey_type == "pre" else "사후 설문"

    # 헤더
    st.markdown(f"""
    <div style="text-align:center;padding:16px 0 12px;">
        <div style="font-size:12px;font-weight:700;color:{color};letter-spacing:4px;margin-bottom:4px;">
            SnapQ TOEIC · {label_type}
        </div>
        <div style="font-size:24px;font-weight:900;color:#fff;">
            {qi + 1} / {total}
        </div>
        <div style="background:rgba(255,255,255,0.1);border-radius:999px;height:6px;margin:8px 0;">
            <div style="background:{color};height:6px;border-radius:999px;
                        width:{int((qi / total) * 100)}%;transition:width 0.3s;"></div>
        </div>
        <div style="font-size:12px;color:rgba(255,255,255,0.4);">
            📝 {cat_name} · 편하게 답해주세요
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 문항 카드
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.05);border:2px solid {color}44;border-radius:20px;
                padding:20px;margin:8px 0;text-align:center;">
        <div style="font-size:11px;color:{color};font-weight:700;letter-spacing:2px;margin-bottom:8px;">
            {cat_name} · {key}
        </div>
        <div style="font-size:20px;font-weight:700;color:#fff;line-height:1.6;">
            {text}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 응답 UI
    if key == "G2_choice":
        # 선택형 (가장 도움이 된 모드)
        for ci, choice in enumerate(G2_CHOICES):
            if st.button(choice, key=f"sv_{qi}_{ci}", use_container_width=True):
                st.session_state.survey_responses[key] = choice
                st.session_state.survey_qi = qi + 1
                st.rerun()

    elif key == "G5_open":
        # 주관식
        answer = st.text_area("", placeholder="자유롭게 적어주세요 (선택사항)",
                              key=f"sv_open_{qi}", height=100)
        if st.button("✅ 제출하기", key=f"sv_submit_{qi}", use_container_width=True):
            st.session_state.survey_responses[key] = answer.strip() if answer else ""
            st.session_state.survey_qi = qi + 1
            st.rerun()

    else:
        # 5점 리커트
        cols = st.columns(5)
        for li, label in enumerate(LIKERT_OPTIONS):
            score = li + 1  # 1~5
            with cols[li]:
                if st.button(f"{score}\n{label}", key=f"sv_{qi}_{li}",
                             use_container_width=True):
                    st.session_state.survey_responses[key] = score
                    st.session_state.survey_qi = qi + 1
                    st.rerun()


# =========================================================
# TOEIC 검사 UI
# =========================================================
def _render_test(stage: int, nickname: str, month_key: str) -> None:
    color = _stage_color(stage)
    name = _stage_name(stage)
    _inject_gate_css(color)

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
    <div style="text-align:center;padding:16px 0 12px;">
        <div style="font-size:12px;font-weight:700;color:{color};letter-spacing:4px;margin-bottom:4px;">
            SnapQ TOEIC · {name}
        </div>
        <div style="font-size:24px;font-weight:900;color:#fff;">
            {qi + 1} / {total}
        </div>
        <div style="background:rgba(255,255,255,0.1);border-radius:999px;height:6px;margin:8px 0;">
            <div style="background:{color};height:6px;border-radius:999px;
                        width:{int((qi / total) * 100)}%;transition:width 0.3s;"></div>
        </div>
        <div style="font-size:12px;color:rgba(255,255,255,0.4);">
            ⏱ 약 3분 · 편하게 풀어보세요
        </div>
    </div>
    """, unsafe_allow_html=True)

    q = TEST_QUESTIONS[qi]

    # 문제 카드
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.05);border:2px solid {color}44;border-radius:20px;
                padding:20px;margin:8px 0;text-align:center;">
        <div style="font-size:11px;color:{color};font-weight:700;letter-spacing:2px;margin-bottom:8px;">
            {q['cat']}
        </div>
        <div style="font-size:20px;font-weight:700;color:#fff;line-height:1.6;">
            {q['text']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 선택지 (2×2)
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


# =========================================================
# 검사 결과 화면
# =========================================================
def _render_result(stage: int, nickname: str, month_key: str) -> None:
    answers = st.session_state.test_answers
    score = sum(1 for i, a in enumerate(answers) if a == TEST_QUESTIONS[i]["a"])
    total = len(TEST_QUESTIONS)
    color = _stage_color(stage)
    name = _stage_name(stage)

    # 저장
    _save_test_result(nickname, month_key, stage, score, answers)

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
            수고하셨어요! 😊
        </div>
    </div>
    """, unsafe_allow_html=True)

    # stage 3 사후 → 설문으로 이동
    if stage == 3 and not st.session_state.get("_survey_post_done"):
        btn_label = "📝 마지막 설문 → 입장!"
    else:
        btn_label = "⚡ 플랫폼 입장하기"

    if st.button(btn_label, use_container_width=True, type="primary"):
        for k in ["test_qi", "test_answers", "test_start", "test_phase"]:
            if k in st.session_state:
                del st.session_state[k]
        st.rerun()

    st.stop()


# =========================================================
# 게이트 안내 화면
# =========================================================
def _render_gate(stage: int, nickname: str) -> None:
    color = _stage_color(stage)
    name = _stage_name(stage)
    _inject_gate_css(color)

    # 닉네임에서 표시용 이름 추출
    display_name = nickname.split('_')[0] if '_' in nickname else nickname

    # stage별 안내 내용
    if stage == 1:
        desc = "📝 간단한 설문 (3분) + 📋 문법 검사 (3분)"
        detail = "설문 → 검사 순서로 진행돼요"
    elif stage == 3:
        desc = "📋 문법 검사 (3분) + 📝 마지막 설문 (4분)"
        detail = "검사 → 설문 순서로 진행돼요"
    else:
        desc = "📋 문법 검사 (3분)"
        detail = "TOEIC P5 문법 10문제"

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
                ✅ {desc}<br>
                ✅ 완료 후 바로 입장 가능<br>
                ✅ 정답/오답 상관없이 완료만 하면 돼요
            </div>
        </div>
        <div style="font-size:14px;color:rgba(255,255,255,0.4);margin-bottom:24px;">
            안녕하세요 {display_name}님! {detail}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button(f"📋 {name} 시작하기", use_container_width=True, type="primary"):
        if stage == 1:
            # 사전: 설문 먼저
            st.session_state.survey_qi = 0
            st.session_state.survey_responses = {}
            st.session_state.survey_phase = "answering"
            st.session_state.current_gate_flow = "pre_survey"
        elif stage == 3:
            # 사후: 검사 먼저
            st.session_state.test_qi = 0
            st.session_state.test_answers = []
            st.session_state.test_start = time.time()
            st.session_state.test_phase = "quiz"
            st.session_state.current_gate_flow = "post_test"
        else:
            # 중간: 검사만
            st.session_state.test_qi = 0
            st.session_state.test_answers = []
            st.session_state.test_start = time.time()
            st.session_state.test_phase = "quiz"
            st.session_state.current_gate_flow = "mid_test"
        st.session_state.current_test_stage = stage
        st.rerun()

    st.stop()


# =========================================================
# 메인 게이트 함수 (main_hub.py에서 호출)
# ─────────────────────────────────────────────────────────
# AI-AGENT NOTE:
#   이 함수가 전체 흐름을 제어한다.
#   stage 1: 설문(pre) → 검사 → 입장
#   stage 2: 검사 → 입장
#   stage 3: 검사 → 설문(post) → 입장
#
#   current_gate_flow 상태로 현재 어디에 있는지 추적:
#     pre_survey → pre_test → done
#     mid_test → done
#     post_test → post_survey → done
# =========================================================
def require_pretest_gate() -> None:
    nickname = _get_nickname()
    month_key = _get_cohort_month()

    if not nickname:
        return

    required_stage = _get_required_stage(nickname, month_key)
    if required_stage is None:
        return  # 검사 기간 아님 (Day 2~7, 15~20 → 바로 입장)

    student_tests = _get_student_tests(nickname, month_key)

    # 이미 완료 여부 확인
    stage_key = f"stage{required_stage}"
    stage_done = student_tests.get(stage_key) is not None

    if required_stage == 1:
        survey_done = student_tests.get("survey_pre") is not None
        if stage_done and survey_done:
            return  # 둘 다 완료
    elif required_stage == 3:
        survey_done = student_tests.get("survey_post") is not None
        if stage_done and survey_done:
            return  # 둘 다 완료
    else:
        if stage_done:
            return  # 검사만 완료면 OK

    # ── 진행 중인 흐름 처리 ──
    flow = st.session_state.get("current_gate_flow", "")
    stage = st.session_state.get("current_test_stage", required_stage)

    # --- STAGE 1: 사전 설문 → 검사 ---
    if flow == "pre_survey":
        if st.session_state.get("_survey_pre_done"):
            # 설문 완료 → 검사로 전환
            st.session_state.current_gate_flow = "pre_test"
            st.session_state.test_qi = 0
            st.session_state.test_answers = []
            st.session_state.test_start = time.time()
            st.session_state.test_phase = "quiz"
            st.rerun()
        else:
            _render_survey("pre", nickname, month_key)
            st.stop()

    if flow == "pre_test":
        if st.session_state.get("test_phase") in ("quiz", "result"):
            _render_test(stage, nickname, month_key)
            st.stop()
        else:
            return  # 검사 완료 → 입장

    # --- STAGE 2: 검사만 ---
    if flow == "mid_test":
        if st.session_state.get("test_phase") in ("quiz", "result"):
            _render_test(stage, nickname, month_key)
            st.stop()
        else:
            return

    # --- STAGE 3: 검사 → 사후 설문 ---
    if flow == "post_test":
        if st.session_state.get("test_phase") in ("quiz", "result"):
            _render_test(stage, nickname, month_key)
            st.stop()
        else:
            # 검사 완료 → 설문으로 전환
            if not st.session_state.get("_survey_post_done"):
                st.session_state.current_gate_flow = "post_survey"
                st.session_state.survey_qi = 0
                st.session_state.survey_responses = {}
                st.session_state.survey_phase = "answering"
                st.rerun()
            else:
                return

    if flow == "post_survey":
        if st.session_state.get("_survey_post_done"):
            return  # 설문 완료 → 입장
        else:
            _render_survey("post", nickname, month_key)
            st.stop()

    # ── 아직 시작 안 한 경우 → 게이트 안내 화면 ──
    _render_gate(required_stage, nickname)


# 하위 호환
def mark_pretest_done(nickname: str, cohort: str) -> None:
    pass
