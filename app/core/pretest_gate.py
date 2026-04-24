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
# =========================================================
# 🎯 옵션 A: 완전한 종단 연구 설계 (2026.05 연구 개시)
# =========================================================
# MILESTONE 관문검사: Day 1, 11, 21, 31, 41... (10일마다, 30문항)
# DAILY 게이트: 매일 첫 접속 시 5문항 (2분)
#
# 설계 철학:
#   - 개인 Day 기준 (달력 날짜 무관)
#   - 10일 간격 = 학원 현실 (1~2개월 이탈자 패턴) 대응
#   - 매일 데이터 수집으로 임계값 돌파 미세 궤적 포착
#
# 논문 연결:
#   ① 설계원리: Day 1 사전 설문 (B3·B4·D4·E2 임계값 변수)
#   ⑤ 탐색적 분석: 매일 RT 변화 + 관문검사 성장 곡선
#   ⑩ SSCI: 10일 간격 반복측정 ANOVA
#   ⑪ 자기문화기술지: 전체 사용 패턴 질적 데이터
# =========================================================

# --- 관문검사 (Milestone) — 재설계 2026.04.24 ---
# 학원 월 사이클(안정 20일)에 맞춘 3회 고정 측정
PRE_SURVEY_DAY   = 1     # ⭐ Day 1:  사전 설문 A~F만 (검사 X, 온보딩)
PRETEST_DAY      = 2     # ⭐ Day 2:  pretest baseline (검사 30만)
MIDTEST_DAY      = 11    # ⭐ Day 11: midtest (검사 30만)
POSTTEST_DAY     = 20    # ⭐ Day 20: posttest (검사 30 + 사후 설문 G)
MILESTONE_DAYS   = {PRETEST_DAY, MIDTEST_DAY, POSTTEST_DAY}  # {2, 11, 20}

# 레거시 호환 (기존 코드/로그에서 참조)
PRE_DAY          = PRE_SURVEY_DAY
MILESTONE_EVERY  = 10
POST_SURVEY_DAY  = POSTTEST_DAY

# --- 데일리 게이트 ---
DAILY_GATE_QUESTIONS     = 5     # 매일 아침 첫 접속 시 5문항
DAILY_GATE_TIME_SEC      = 33    # ⭐ 모닝팩 P5: 5문제 33초 (속도 훈련)
DAILY_GATE_SECONDS       = 20    # (레거시, 참고용)
MILESTONE_GATE_QUESTIONS = 30    # ⭐ 관문검사 30문항
MILESTONE_GATE_TIME_SEC  = 900   # ⭐ 관문검사 총 제한: 15분

# --- 레거시 호환 (기존 코드에서 참조되는 경우 대비) ---
MID_START   = 11         # Day 11: 1차 중간 (레거시)
MID_END     = 11         # 단일 날짜로 변경
POST_START  = 21         # Day 21~: 사후 (레거시)


def is_milestone_day(day: int) -> bool:
    """개인 Day가 관문검사 날인지 판정. Day 2, 11, 20 = True"""
    return day in MILESTONE_DAYS


def get_milestone_round(day: int) -> int:
    """관문검사 회차 계산 (Day 2=1회 pretest, Day 11=2회 mid, Day 20=3회 post)"""
    mapping = {PRETEST_DAY: 1, MIDTEST_DAY: 2, POSTTEST_DAY: 3}
    return mapping.get(day, 0)


# =========================================================
# 설문 문항 — 임계값(Threshold) 중심 설계
# ─────────────────────────────────────────────────────────
# 카테고리별 4문항 × 6카테고리 = 24문항 (사전+사후 공통)
# + 사후 전용 G 5문항 = 총 29문항 (사후)
# =========================================================
# ═════════════════════════════════════════════════════════════════
# 설문 문항 v3 — 재구조화 2026.04.24 (PPT 대서사시 × 11개 논문 매핑)
# ═════════════════════════════════════════════════════════════════
# 🔥 TH (7) · 임계값 지향 ← 박사논문 철학 핵심, ★★★
# 🤖 AL (4) · AI 알고리즘 수용 ← Layer 1+2 · 논문 ④⑤⑥
# 💪 EF (4) · 자기 효능감 ← Bandura · 논문 ④⑦⑩⑪
# 🧠 MG (3) · 메타인지·전략 ← Layer 1 · 논문 ⑤⑥
# ⚡ MO (5) · 동기·몰입 ← Flow+ARCS+SDT+Grit+NPS
# 🎮 GA (3) · 게이미피케이션 반응 ← Layer 4 · 논문 ①②⑩
# 합계: 리커트 26
# ═════════════════════════════════════════════════════════════════
SURVEY_ITEMS = {
    # ── 🔥 TH · 임계값 지향 (7) ── ★★★ 박사논문 축
    "TH1": "나는 지금 내 실력보다 조금 어려운 문제를 푸는 것이 좋다",    # ZPD
    "TH2": "틀린 문제를 다시 풀면 실력이 한 단계 오를 것 같다",          # 재도전 임계
    "TH3": "도전적인 목표가 있으면 더 몰입해서 공부한다",                # Flow Challenge
    "TH4": "시간 압박 속에서도 집중해서 정답을 고를 수 있다",            # RT 효능
    "TH5": "레벨·단계가 올라가는 느낌이 있으면 계속하고 싶다",           # Mastery
    "TH6": "실력이 확 늘었을 때의 뿌듯함을 생생히 기억한다",             # Bandura 성공경험
    "TH7": "쉬운 문제만 반복하는 것보다 도전하다 틀리는 게 낫다",        # 성장 마인드셋
    # ── 🤖 AL · AI 알고리즘 수용 (4) ──
    "AL1": "내가 얼마나 빨리 푸는지 기록되는 것에 거부감이 없다",        # 논문 ④
    "AL2": "AI가 내 약점을 스스로 찾아서 알려주면 도움이 될 것 같다",     # 논문 ④⑥
    "AL3": "내 학습 기록이 쌓이면 내 실력 변화를 볼 수 있을 것 같다",     # 논문 ⑤
    "AL4": "AI가 다음 문제를 알아서 골라주는 방식을 신뢰한다",           # 논문 ④⑥⑨
    # ── 💪 EF · 자기 효능감 (4) ──
    "EF1": "나는 TOEIC 문법 문제를 대체로 잘 풀 수 있다",               # 문법 효능
    "EF2": "어려운 문법이라도 연습하면 이해할 수 있다",                  # 숙달 효능
    "EF3": "모르는 단어가 많아도 문장 의미를 추측할 수 있다",            # 독해 전략 효능
    "EF4": "시험에서 긴장되어도 실력을 발휘할 수 있다",                  # 심리생리 효능
    # ── 🧠 MG · 메타인지·전략 (3) ──
    "MG1": "틀린 문제는 반드시 다시 확인하고 넘어간다",                  # 망각곡선 임계
    "MG2": "문법·독해·어휘를 서로 연결해서 공부한다",                    # 크로스스킬
    "MG3": "문제를 풀 때 왜 틀렸는지 스스로 분석한다",                   # 메타인지
    # ── ⚡ MO · 동기·몰입 (5) ──
    "MO1": "영어 문법을 새로 배울 때 흥미를 느낀다",                     # 내재동기
    "MO2": "TOEIC 점수 목표를 꼭 달성하고 싶다",                        # 외재동기 (공변량)
    "MO3": "공부하다 시간 가는 줄 모를 때가 있다",                       # Flow 시간왜곡
    "MO4": "매일 조금씩이라도 꾸준히 공부하고 싶다",                     # Grit
    "MO5": "이 앱을 친구에게 추천하고 싶다",                            # NPS
    # ── 🎮 GA · 게이미피케이션 반응 (3) ──
    "GA1": "점수·포인트가 있으면 더 열심히 하게 된다",                   # Points
    "GA2": "캐릭터·스토리가 있으면 몰입이 잘 된다",                      # Narrative (TORI/HAE)
    "GA3": "다른 사람과 경쟁·비교하는 것이 동기부여가 된다",             # Leaderboard
}

# ── 📋 기초 변수 (사전만, 선택형) — 종단분석 공변량 ──
BASE_VARS = {
    "Q_LEVEL": "현재 예상 TOEIC 점수대는?",
    "Q_YEARS": "영어 학습 기간은?",
}
Q_LEVEL_CHOICES = ["400점 이하", "400~600점", "600~800점", "800점 이상", "잘 모르겠어요"]
Q_YEARS_CHOICES = ["1년 미만", "1~3년", "3~5년", "5년 이상"]

# ── 🖊 사전 추가 주관식 (선택 입력) — 논문 ⑪ 자기문화기술지 pre-post 쌍 ──
SURVEY_PRE_EXTRA = {
    "G0_open": "지금 TOEIC 공부에서 가장 막히는 부분이나 어려운 점을 한 문장으로 적어주세요. (선택 입력)",
}

# ── 📝 사후 전용 (G) ──
SURVEY_POST_ONLY = {
    "G1": "SnapQ가 영어 실력 향상에 도움이 되었다",
    "G2_choice": "가장 도움이 된 모드는?",
    "G3": "난이도가 자동으로 바뀌는 것이 도움이 되었다",        # 논문 ⑦
    "G4": "NPC(토리/해이) 메시지가 동기부여에 도움이 되었다",   # 논문 ⑧
    "G5_open": "한 줄 소감을 자유롭게 적어주세요",               # 질적 데이터
}

LIKERT_OPTIONS = ["전혀 아니다", "아니다", "보통이다", "그렇다", "매우 그렇다"]
G2_CHOICES = ["⚡ 화력전 (문법 5문제)", "📡 암호해독 (독해 3문제)", "💀 포로사령부 (오답 복습)"]

# ── 카테고리 prefix → 한글 이름 매핑 (명시적 순서 = G0 먼저 매치) ──
CATEGORY_NAMES = [
    ("Q_",  "📋 기초 정보"),
    ("TH",  "🔥 도전과 성장"),
    ("AL",  "🤖 AI 학습"),
    ("EF",  "💪 자기 효능감"),
    ("MG",  "🧠 학습 전략"),
    ("MO",  "⚡ 학습 동기"),
    ("GA",  "🎮 게임 요소"),
    ("G0",  "🖊 자유 응답"),
    ("G5",  "🖊 자유 응답"),
    ("G2",  "📝 사용 경험"),
    ("G1",  "📝 사용 경험"),
    ("G3",  "📝 사용 경험"),
    ("G4",  "📝 사용 경험"),
]

def _get_category_name(key: str) -> str:
    """설문 key의 prefix에 따라 카테고리 이름 반환"""
    for prefix, name in CATEGORY_NAMES:
        if key.startswith(prefix):
            return name
    return "설문"


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
    # ─────── 옵션 A 확장: 관문검사 30문항 (T11~T30) ───────
    {"id": "T11", "text": "The seminar will be held _______ the conference room on the third floor.",
     "ch": ["(A) at", "(B) in", "(C) on", "(D) by"], "a": 1, "cat": "전치사"},
    {"id": "T12", "text": "Employees who _______ the training last week should contact HR.",
     "ch": ["(A) miss", "(B) missing", "(C) missed", "(D) misses"], "a": 2, "cat": "동사/시제"},
    {"id": "T13", "text": "The director _______ the proposal yesterday during the board meeting.",
     "ch": ["(A) approve", "(B) approved", "(C) approving", "(D) approval"], "a": 1, "cat": "동사/시제"},
    {"id": "T14", "text": "_______ the weather is bad tomorrow, the event will be held indoors.",
     "ch": ["(A) Unless", "(B) If", "(C) Because", "(D) Since"], "a": 1, "cat": "접속/연결"},
    {"id": "T15", "text": "The company's new product line has been _______ received by customers.",
     "ch": ["(A) warm", "(B) warmth", "(C) warmly", "(D) warmer"], "a": 2, "cat": "품사/수식"},
    {"id": "T16", "text": "Neither the manager _______ the employees were informed about the changes.",
     "ch": ["(A) or", "(B) nor", "(C) and", "(D) but"], "a": 1, "cat": "상관접속사"},
    {"id": "T17", "text": "Please ensure that your ID badge is _______ visible at all times.",
     "ch": ["(A) clear", "(B) clearly", "(C) clearing", "(D) clearness"], "a": 1, "cat": "품사/수식"},
    {"id": "T18", "text": "The documents _______ on the shared drive are confidential.",
     "ch": ["(A) stored", "(B) storing", "(C) store", "(D) stores"], "a": 0, "cat": "분사구"},
    {"id": "T19", "text": "Mr. Kim has been with our company _______ more than fifteen years.",
     "ch": ["(A) since", "(B) from", "(C) for", "(D) during"], "a": 2, "cat": "전치사"},
    {"id": "T20", "text": "The training session was _______ than expected, so we ended early.",
     "ch": ["(A) short", "(B) shorter", "(C) shortest", "(D) shortly"], "a": 1, "cat": "비교급"},
    # ─────── 어휘 10문항 (T21~T30) ───────
    {"id": "T21", "text": "The company plans to _______ into Southeast Asian markets next year.",
     "ch": ["(A) extend", "(B) expand", "(C) exceed", "(D) expose"], "a": 1, "cat": "어휘"},
    {"id": "T22", "text": "All visitors must _______ at the reception desk upon arrival.",
     "ch": ["(A) register", "(B) registry", "(C) registration", "(D) registered"], "a": 0, "cat": "어휘"},
    {"id": "T23", "text": "The new policy will take _______ starting next Monday.",
     "ch": ["(A) affect", "(B) effect", "(C) effective", "(D) effectively"], "a": 1, "cat": "어휘"},
    {"id": "T24", "text": "Please _______ from using mobile phones during the presentation.",
     "ch": ["(A) refrain", "(B) refer", "(C) reflect", "(D) refuse"], "a": 0, "cat": "어휘"},
    {"id": "T25", "text": "The committee will _______ the candidates based on their qualifications.",
     "ch": ["(A) evaluate", "(B) evacuate", "(C) elevate", "(D) elaborate"], "a": 0, "cat": "어휘"},
    {"id": "T26", "text": "We need to _______ the issue before it becomes a bigger problem.",
     "ch": ["(A) address", "(B) advance", "(C) admit", "(D) adjust"], "a": 0, "cat": "어휘"},
    {"id": "T27", "text": "The report provides a _______ analysis of the current market trends.",
     "ch": ["(A) comprehensive", "(B) compensate", "(C) component", "(D) component"], "a": 0, "cat": "어휘"},
    {"id": "T28", "text": "Our team has _______ remarkable progress in the past six months.",
     "ch": ["(A) make", "(B) made", "(C) making", "(D) makes"], "a": 1, "cat": "어휘"},
    {"id": "T29", "text": "The invoice must be paid within 30 days of _______.",
     "ch": ["(A) receive", "(B) receipt", "(C) receiver", "(D) receiving"], "a": 1, "cat": "어휘"},
    {"id": "T30", "text": "Customer feedback is _______ to improving our products.",
     "ch": ["(A) essential", "(B) essence", "(C) essentially", "(D) essentials"], "a": 0, "cat": "어휘"},
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
    """개인 Day 기준 필요한 stage 반환. — 재설계 2026.04.24

        Day 1  → stage 1 (사전 설문 A~F만, 검사 X)
        Day 2  → stage 2 (pretest baseline 30문항)
        Day 11 → stage 2 (midtest 30문항)
        Day 20 → stage 3 (posttest 30문항 + 사후 설문 G)
        그 외  → None (게이트 없이 자유 입장, 데일리 5문항만)
    """
    day = _get_user_day(nickname, month_key)

    # Day 1: 사전 설문만 (관문검사 없음)
    if day == PRE_SURVEY_DAY:
        return 1

    # Day 20: posttest (관문 + 사후 설문 G)
    if day == POSTTEST_DAY:
        return 3

    # Day 2, 11: 관문검사만
    if day in (PRETEST_DAY, MIDTEST_DAY):
        return 2

    return None

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
    """v9 — button 내부 <p> 태그까지 font-size 강제 적용"""
    st.markdown(f"""
    <style>
    /* 앱 기본 */
    .stApp {{ background: #0D0F1A !important; }}
    .block-container {{
        max-width: 600px !important;
        margin: 0 auto !important;
        padding: 2.5rem 1rem 2rem 1rem !important;
    }}
    /* iOS 자동 축소 방지 */
    html, body {{
        -webkit-text-size-adjust: none !important;
        text-size-adjust: none !important;
    }}
    /* 박스 크기 (원래대로 복원) */
    button,
    div.stButton > button,
    .stButton > button,
    [data-testid*="Button"] button {{
        border-radius: 14px !important;
        padding: 14px !important;
        font-weight: 900 !important;
        touch-action: manipulation !important;
    }}
    /* ⭐⭐⭐ 핵심: button 안의 모든 자식 요소(p, span 등)에 font-size 직접 적용 */
    button,
    button *,
    button p,
    button span,
    button div,
    div.stButton > button,
    div.stButton > button *,
    div.stButton button p,
    div.stButton button span,
    .stButton button,
    .stButton button *,
    .stButton button p,
    [data-testid*="Button"] button,
    [data-testid*="Button"] button *,
    [data-testid*="Button"] button p {{
        font-size: 20px !important;
        line-height: 1.3 !important;
        font-weight: 900 !important;
    }}
    /* 관문검사 2x2 그리드만 작게 유지 */
    div[data-testid="column"] button,
    div[data-testid="column"] button *,
    div[data-testid="column"] button p,
    [data-testid="column"] button,
    [data-testid="column"] button * {{
        font-size: 22px !important;
        line-height: 1.25 !important;
    }}
    /* 입력창 */
    div.stTextArea textarea,
    div.stTextInput input {{
        font-size: 24px !important;
        line-height: 1.5 !important;
    }}
    /* 라디오 */
    div.stRadio > label {{ color: #ffffff !important; font-size: 18px !important; }}
    div[data-testid="stRadio"] label span {{ color: #ffffff !important; }}
    /* Streamlit UI 숨김 */
    #MainMenu {{ display: none !important; }}
    footer {{ display: none !important; }}
    header {{ visibility: hidden !important; }}
    [data-testid="stHeader"] {{ visibility: hidden !important; }}
    [data-testid="stToolbar"] {{ display: none !important; }}
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

    # 문항 리스트 구성 — v3 재설계
    if survey_type == "pre":
        # 사전: 기초변수 2개 → 리커트 26 → 사전 주관식 1 = 29문항
        items = list(BASE_VARS.items()) + list(SURVEY_ITEMS.items()) + list(SURVEY_PRE_EXTRA.items())
    else:
        # 사후: 리커트 26 → 사후 G 5개 = 31문항
        items = list(SURVEY_ITEMS.items()) + list(SURVEY_POST_ONLY.items())
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
    cat_name = _get_category_name(key)
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
        <div style="font-size:26px;font-weight:700;color:#fff;line-height:1.6;">
            {text}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 응답 UI — v3 재설계 (기초변수 Q_LEVEL, Q_YEARS + 주관식 G0/G5 통합)
    if key == "Q_LEVEL":
        # 선택형: TOEIC 점수대
        for ci, choice in enumerate(Q_LEVEL_CHOICES):
            if st.button(choice, key=f"sv_{qi}_{ci}", use_container_width=True):
                st.session_state.survey_responses[key] = choice
                st.session_state.survey_qi = qi + 1
                st.rerun()

    elif key == "Q_YEARS":
        # 선택형: 영어 학습 기간
        for ci, choice in enumerate(Q_YEARS_CHOICES):
            if st.button(choice, key=f"sv_{qi}_{ci}", use_container_width=True):
                st.session_state.survey_responses[key] = choice
                st.session_state.survey_qi = qi + 1
                st.rerun()

    elif key == "G2_choice":
        # 선택형: 가장 도움이 된 모드
        for ci, choice in enumerate(G2_CHOICES):
            if st.button(choice, key=f"sv_{qi}_{ci}", use_container_width=True):
                st.session_state.survey_responses[key] = choice
                st.session_state.survey_qi = qi + 1
                st.rerun()

    elif key.endswith("_open"):
        # 주관식 (G0_open 사전 · G5_open 사후 모두 해당)
        placeholder_text = "자유롭게 적어주세요 (선택 입력 — 생략 가능)"
        answer = st.text_area("", placeholder=placeholder_text,
                              key=f"sv_open_{qi}", height=100)
        btn_label = "⏭ 건너뛰기" if not answer.strip() else "✅ 제출하기"
        if st.button(btn_label, key=f"sv_submit_{qi}", use_container_width=True):
            st.session_state.survey_responses[key] = answer.strip() if answer else ""
            st.session_state.survey_qi = qi + 1
            st.rerun()

    else:
        # 5점 리커트 — 세로 1열 (v5 모바일 최적, 2026.04.24)
        for li, label in enumerate(LIKERT_OPTIONS):
            score = li + 1  # 1~5
            if st.button(f"{score}. {label}", key=f"sv_{qi}_{li}",
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

    # ─── ⏱ 시간 초과 → 서버측 강제 완료 (JS 실패해도 안전) ───
    _ts_start = st.session_state.get("test_start", time.time())
    _test_elapsed = time.time() - _ts_start
    _test_remaining = max(0, MILESTONE_GATE_TIME_SEC - int(_test_elapsed))
    if _test_remaining <= 0 and st.session_state.get("test_phase") == "quiz":
        st.session_state.test_time_spent_sec = int(_test_elapsed)
        st.session_state.test_phase = "result"
        st.rerun()

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
    </div>
    """, unsafe_allow_html=True)

    # ─── ⏱ JS 카운트다운 타이머 (60초 이하 빨간 깜빡임) ───
    import streamlit.components.v1 as _components
    _mm, _ss = divmod(_test_remaining, 60)
    _components.html(f"""
    <div style="text-align:center;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
      <div id="snapq-test-timer-box" style="
           font-size:20px;font-weight:900;color:{color};
           padding:8px 22px;border-radius:24px;display:inline-block;
           background:rgba(0,229,255,0.10);
           border:1.5px solid {color}99;
           transition:all 0.3s ease;">
        ⏱ <span id="snapq-test-time">{_mm}:{_ss:02d}</span>
      </div>
    </div>
    <script>
    (function() {{
        let rem = {_test_remaining};
        const timeEl = document.getElementById('snapq-test-time');
        const boxEl  = document.getElementById('snapq-test-timer-box');
        if (!timeEl || !boxEl) return;
        function fmt(n) {{ return n < 10 ? '0' + n : '' + n; }}
        function render() {{
            const m = Math.floor(rem / 60);
            const s = rem % 60;
            timeEl.textContent = m + ':' + fmt(s);
            if (rem <= 60) {{
                boxEl.style.color = '#EF4444';
                boxEl.style.background = 'rgba(239,68,68,0.15)';
                boxEl.style.borderColor = 'rgba(239,68,68,0.6)';
                boxEl.style.animation = 'snapq-test-pulse 0.9s ease-in-out infinite';
            }}
        }}
        render();
        const iv = setInterval(function() {{
            rem -= 1;
            if (rem < 0) {{
                clearInterval(iv);
                try {{ window.parent.location.reload(); }} catch(e) {{ location.reload(); }}
                return;
            }}
            render();
        }}, 1000);
    }})();
    </script>
    <style>
    @keyframes snapq-test-pulse {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50%      {{ opacity: 0.55; transform: scale(1.04); }}
    }}
    body {{ margin:0; padding:0; background:transparent; }}
    </style>
    """, height=62)

    q = TEST_QUESTIONS[qi]

    # 문제 카드
    st.markdown(f"""
    <div style="background:rgba(255,255,255,0.05);border:2px solid {color}44;border-radius:20px;
                padding:20px;margin:8px 0;text-align:center;">
        <div style="font-size:11px;color:{color};font-weight:700;letter-spacing:2px;margin-bottom:8px;">
            {q['cat']}
        </div>
        <div style="font-size:26px;font-weight:700;color:#fff;line-height:1.6;">
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
# =========================================================
# 🌅 데일리 게이트 (옵션 A 핵심) — 매일 첫 접속 시 5문항
# =========================================================
DAILY_POOL_PATH = Path(__file__).parent.parent / "content" / "daily_gate_pool.json"


def _load_daily_pool() -> list:
    """데일리 게이트용 문항 풀 로드. 파일 없으면 내장 기본 풀 사용."""
    try:
        if DAILY_POOL_PATH.exists():
            with open(DAILY_POOL_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    # 폴백: 내장 기본 풀 (30문항 샘플)
    return _BUILTIN_DAILY_POOL


def _needs_daily_gate(nickname: str, month_key: str) -> bool:
    """오늘 데일리 게이트 아직 안 풀었으면 True."""
    if not nickname:
        return False
    try:
        roster_path = _cohort_dir(month_key) / "roster.jsonl"
        if not roster_path.exists():
            return True
        today = date.today().isoformat()
        with open(roster_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line.strip())
                    if r.get("nickname") == nickname:
                        last = r.get("daily_gate_last_date", "")
                        return last != today
                except Exception:
                    continue
    except Exception:
        pass
    return True


def _mark_daily_gate_done(nickname: str, month_key: str) -> None:
    """roster에 오늘 날짜로 데일리 게이트 완료 기록."""
    try:
        roster_path = _cohort_dir(month_key) / "roster.jsonl"
        if not roster_path.exists():
            return
        today = date.today().isoformat()
        lines = []
        with open(roster_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line.strip())
                    if r.get("nickname") == nickname:
                        r["daily_gate_last_date"] = today
                        r["daily_gate_total_count"] = r.get("daily_gate_total_count", 0) + 1
                    lines.append(json.dumps(r, ensure_ascii=False))
                except Exception:
                    lines.append(line.strip())
        with open(roster_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    except Exception:
        pass


def _save_daily_gate_log(user_id: str, personal_day: int,
                         q: dict, is_correct: bool, rt_ms: int) -> None:
    """데일리 게이트 문항 응답 → Google Sheets gate_daily_logs"""
    entry = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "personal_day": personal_day,
        "q_id": q.get("id", ""),
        "is_correct": bool(is_correct),
        "response_time_ms": int(rt_ms) if rt_ms else 0,
        "q_type": q.get("type", "grammar"),
        "difficulty": q.get("diff", ""),
        "research_phase": "pre_irb",  # IRB 승인 후 "main"으로 변경
    }
    _save_to_sheets("gate_daily_logs", entry)


def _render_daily_gate(nickname: str, month_key: str) -> None:
    """
    데일리 게이트 UI 렌더링.
    5문항 연속 → 결과 요약 → 입장 허용
    """
    _inject_gate_css(color="#3B82F6")  # 파란색 (데일리 = 아침)

    # 세션 상태 초기화
    if "daily_qi" not in st.session_state:
        st.session_state.daily_qi = 0
        st.session_state.daily_pool = _load_daily_pool()
        # 랜덤 5문항 선택
        import random
        pool = st.session_state.daily_pool
        if len(pool) >= DAILY_GATE_QUESTIONS:
            st.session_state.daily_questions = random.sample(pool, DAILY_GATE_QUESTIONS)
        else:
            st.session_state.daily_questions = pool[:DAILY_GATE_QUESTIONS]
        st.session_state.daily_correct = 0
        st.session_state.daily_start_time = time.time()
        st.session_state.daily_q_start_time = time.time()
        st.session_state.daily_phase = "quiz"

    questions = st.session_state.daily_questions
    qi = st.session_state.daily_qi
    phase = st.session_state.daily_phase

    # --- 완료 화면 ---
    if phase == "done":
        st.markdown(f"""
        <div style="text-align:center;padding:60px 20px;">
            <div style="font-size:64px;margin-bottom:16px;">🌅</div>
            <div style="font-size:28px;font-weight:900;color:#fff;margin-bottom:12px;">
                모닝팩 P5 완료!
            </div>
            <div style="font-size:20px;color:#3B82F6;margin-bottom:8px;">
                {st.session_state.daily_correct} / {DAILY_GATE_QUESTIONS} 정답
            </div>
            <div style="font-size:16px;color:rgba(255,255,255,0.6);margin-bottom:32px;">
                좋아요! 이제 SnapQ로 들어가세요 🚀
            </div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("⚡ SnapQ 입장하기", use_container_width=True, type="primary"):
            # 세션 상태 정리
            for k in ["daily_qi", "daily_pool", "daily_questions",
                      "daily_correct", "daily_start_time",
                      "daily_q_start_time", "daily_phase"]:
                st.session_state.pop(k, None)
            st.rerun()
        st.stop()

    # --- 퀴즈 화면 ---
    if qi >= len(questions):
        # 모든 문항 완료 → 기록 & done 전환
        _mark_daily_gate_done(nickname, month_key)
        st.session_state.daily_phase = "done"
        st.rerun()

    q = questions[qi]
    day = _get_user_day(nickname, month_key)

    # ─── ⏱ 타이머 시작 시각 (오늘 날짜 key: 매일 자동 리셋) ───
    _today_key = date.today().isoformat()
    _ts_key = f"daily_gate_start_ts_{_today_key}"
    if _ts_key not in st.session_state:
        st.session_state[_ts_key] = time.time()
    _elapsed = time.time() - st.session_state[_ts_key]
    _remaining = max(0, DAILY_GATE_TIME_SEC - int(_elapsed))

    # ─── 시간 초과 → 서버측 강제 완료 (JS 실패해도 안전장치) ───
    if _remaining <= 0:
        st.session_state.daily_time_spent_sec = int(_elapsed)
        st.session_state.daily_qi = DAILY_GATE_QUESTIONS
        st.rerun()

    # ─── 헤더 ───
    st.markdown(f"""
    <div style="text-align:center;margin-top:8px;margin-bottom:12px;">
        <div style="font-size:22px;color:#3B82F6;font-weight:900;margin-bottom:4px;">
            🌅 모닝팩 P5 · Day {day}
        </div>
        <div style="font-size:13px;color:rgba(255,255,255,0.5);">
            문항 {qi+1} / {DAILY_GATE_QUESTIONS}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ─── ⏱ JS 카운트다운 타이머 (30초 이하 빨간 깜빡임) ───
    import streamlit.components.v1 as _components
    _m, _s = divmod(_remaining, 60)
    _components.html(f"""
    <div style="text-align:center;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
      <div id="snapq-timer-box" style="
           font-size:22px;font-weight:900;color:#3B82F6;
           padding:8px 22px;border-radius:24px;display:inline-block;
           background:rgba(59,130,246,0.12);
           border:1.5px solid rgba(59,130,246,0.4);
           transition:all 0.3s ease;">
        ⏱ <span id="snapq-time">{_m}:{_s:02d}</span>
      </div>
    </div>
    <script>
    (function() {{
        let remaining = {_remaining};
        const timeEl = document.getElementById('snapq-time');
        const boxEl  = document.getElementById('snapq-timer-box');
        if (!timeEl || !boxEl) return;
        function render() {{
            const m = Math.floor(remaining / 60);
            const s = remaining % 60;
            timeEl.textContent = m + ':' + (s < 10 ? '0' : '') + s;
            if (remaining <= 30) {{
                boxEl.style.color = '#EF4444';
                boxEl.style.background = 'rgba(239,68,68,0.15)';
                boxEl.style.borderColor = 'rgba(239,68,68,0.6)';
                boxEl.style.animation = 'snapq-pulse 0.9s ease-in-out infinite';
            }}
        }}
        render();
        const iv = setInterval(function() {{
            remaining -= 1;
            if (remaining < 0) {{
                clearInterval(iv);
                try {{ window.parent.location.reload(); }} catch(e) {{ location.reload(); }}
                return;
            }}
            render();
        }}, 1000);
    }})();
    </script>
    <style>
    @keyframes snapq-pulse {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50%      {{ opacity: 0.55; transform: scale(1.04); }}
    }}
    body {{ margin:0; padding:0; background:transparent; }}
    </style>
    """, height=70)

    # 문제
    st.markdown(f"""
    <div style="background:rgba(59,130,246,0.08);border:1px solid rgba(59,130,246,0.3);
                border-radius:12px;padding:24px;margin-bottom:20px;">
        <div style="font-size:22px;color:#fff;line-height:1.6;font-weight:700;">
            {q.get("question", "")}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 선택지
    choices = q.get("choices", [])
    for idx, choice in enumerate(choices):
        if st.button(f"{chr(65+idx)}. {choice}", key=f"daily_c{qi}_{idx}",
                     use_container_width=True):
            # 응답 처리
            rt_ms = int((time.time() - st.session_state.daily_q_start_time) * 1000)
            is_correct = (idx == q.get("answer_idx", 0))
            if is_correct:
                st.session_state.daily_correct += 1
            # 로그 저장 (실패해도 진행)
            try:
                _save_daily_gate_log(nickname, day, q, is_correct, rt_ms)
            except Exception:
                pass
            # 다음 문항
            st.session_state.daily_qi += 1
            st.session_state.daily_q_start_time = time.time()
            st.rerun()

    st.stop()


# --- 데일리 게이트용 내장 기본 문항 풀 (30문항) ---
_BUILTIN_DAILY_POOL = [
    # ═══ 어법 15문항 (TOEIC P5 수준, 15-18단어) ═══
    {"id":"D001","type":"grammar","diff":"medium",
     "question":"The manager announced that the quarterly report ___ by the accounting department before Friday.",
     "choices":["completing","completed","will be completed","was completing"],"answer_idx":2},
    {"id":"D002","type":"grammar","diff":"easy",
     "question":"All documents submitted to the legal department must be ___ reviewed before the signing ceremony.",
     "choices":["thorough","thoroughly","thoroughness","more thorough"],"answer_idx":1},
    {"id":"D003","type":"grammar","diff":"medium",
     "question":"The new marketing strategy ___ last month has already increased sales by over twenty percent.",
     "choices":["implement","implemented","implementing","to implement"],"answer_idx":1},
    {"id":"D004","type":"grammar","diff":"hard",
     "question":"Unless the proposal ___ by the board next week, the project will be postponed indefinitely.",
     "choices":["approved","approves","is approved","approving"],"answer_idx":2},
    {"id":"D005","type":"grammar","diff":"medium",
     "question":"The senior engineers ___ on the new prototype have requested additional funding from the director this month.",
     "choices":["work","works","working","worked"],"answer_idx":2},
    {"id":"D006","type":"grammar","diff":"easy",
     "question":"Mr. Chen, ___ has been with the company for fifteen years, will retire this December.",
     "choices":["who","whom","which","whose"],"answer_idx":0},
    {"id":"D007","type":"grammar","diff":"medium",
     "question":"The training session will begin promptly at nine AM ___ all participants arrive on time.",
     "choices":["as long as","in spite of","because of","due to"],"answer_idx":0},
    {"id":"D008","type":"grammar","diff":"hard",
     "question":"Not only ___ the annual revenue exceeded expectations, but customer satisfaction also improved quite significantly.",
     "choices":["have","has","did","does"],"answer_idx":1},
    {"id":"D009","type":"grammar","diff":"medium",
     "question":"The company's decision to expand into Asian markets ___ by many analysts as highly strategic.",
     "choices":["views","viewing","viewed","is viewed"],"answer_idx":3},
    {"id":"D010","type":"grammar","diff":"easy",
     "question":"Before finalizing the annual budget, the finance team consulted with senior management for three days.",
     "choices":["Before","While","During","Since"],"answer_idx":0},
    {"id":"D011","type":"grammar","diff":"hard",
     "question":"Had the contract been signed yesterday afternoon, the project ___ started on schedule this morning.",
     "choices":["will","would","would have","had"],"answer_idx":2},
    {"id":"D012","type":"grammar","diff":"medium",
     "question":"The research findings, ___ were published last month, have attracted significant attention from industry experts.",
     "choices":["who","which","that","what"],"answer_idx":1},
    {"id":"D013","type":"grammar","diff":"easy",
     "question":"The newly released software is significantly faster ___ the previous version in almost every aspect.",
     "choices":["as","than","to","from"],"answer_idx":1},
    {"id":"D014","type":"grammar","diff":"medium",
     "question":"Employees ___ training programs regularly tend to show higher productivity than those who do not.",
     "choices":["attend","attending","attended","have attended"],"answer_idx":1},
    {"id":"D015","type":"grammar","diff":"hard",
     "question":"Please ensure that all visitors ___ at the reception desk immediately upon entering the building.",
     "choices":["register","registers","to register","registered"],"answer_idx":0},

    # ═══ 어휘 15문항 (TOEIC P5 수준, 15-18단어) ═══
    {"id":"D016","type":"vocab","diff":"easy",
     "question":"The board of directors will ___ the new proposal during tomorrow's executive meeting at headquarters.",
     "choices":["retain","replace","reject","review"],"answer_idx":3},
    {"id":"D017","type":"vocab","diff":"medium",
     "question":"Customer complaints have ___ quite significantly after the implementation of the new quality control system.",
     "choices":["increased","released","decreased","expressed"],"answer_idx":2},
    {"id":"D018","type":"vocab","diff":"medium",
     "question":"The company's financial position has become much more ___ since the merger was completed last year.",
     "choices":["stabled","stable","stability","stably"],"answer_idx":1},
    {"id":"D019","type":"vocab","diff":"hard",
     "question":"Please kindly ___ from using mobile devices during the presentation in the main conference hall.",
     "choices":["refrain","refer","refresh","reduce"],"answer_idx":0},
    {"id":"D020","type":"vocab","diff":"medium",
     "question":"The marketing team will ___ a comprehensive new strategy to attract international clients next quarter.",
     "choices":["divide","deliver","decline","devise"],"answer_idx":3},
    {"id":"D021","type":"vocab","diff":"medium",
     "question":"The factory's production capacity has already ___ the limit set by current industry regulations this month.",
     "choices":["exhausted","extracted","exceeded","extended"],"answer_idx":2},
    {"id":"D022","type":"vocab","diff":"hard",
     "question":"All staff members are expected to ___ to the company's strict code of conduct at all times.",
     "choices":["adhere","adjust","address","admit"],"answer_idx":0},
    {"id":"D023","type":"vocab","diff":"medium",
     "question":"The CEO expressed her ___ for the team's outstanding performance during the difficult economic period.",
     "choices":["hesitation","explanation","appreciation","limitation"],"answer_idx":2},
    {"id":"D024","type":"vocab","diff":"easy",
     "question":"The supplier failed to ___ the shipment as promised, causing significant delays in our production schedule.",
     "choices":["divide","deliver","declare","devote"],"answer_idx":1},
    {"id":"D025","type":"vocab","diff":"hard",
     "question":"The new company policy will ___ every employee across all departments starting from next Monday.",
     "choices":["effect","infect","reflect","affect"],"answer_idx":3},
    {"id":"D026","type":"vocab","diff":"medium",
     "question":"The conference attendees ___ from various industries around the world gathered for the keynote speech.",
     "choices":["representing","represented","represent","representation"],"answer_idx":0},
    {"id":"D027","type":"vocab","diff":"medium",
     "question":"The research team will need to ___ the data very carefully before publishing the final findings.",
     "choices":["apologize","announce","analyze","anticipate"],"answer_idx":2},
    {"id":"D028","type":"vocab","diff":"easy",
     "question":"The proposal submitted by our competitor is ___ to ours in terms of technical specifications.",
     "choices":["simulated","similar","stimulating","strategic"],"answer_idx":1},
    {"id":"D029","type":"vocab","diff":"hard",
     "question":"The client's detailed requirements have been clearly ___ in the technical specifications document distributed last Friday.",
     "choices":["outlined","outlaid","outsourced","outlawed"],"answer_idx":0},
    {"id":"D030","type":"vocab","diff":"medium",
     "question":"Due to unexpected circumstances, the launch event has been ___ until further notice from management.",
     "choices":["postponed","prospected","promoted","preserved"],"answer_idx":0},
]

def require_pretest_gate() -> None:
    nickname = _get_nickname()
    month_key = _get_cohort_month()

    if not nickname:
        return

    # ═══ 옵션 A: 데일리 게이트 체크 (매일 첫 접속) ═══
    # 관문검사보다 우선 실행 — 학생이 오늘 아직 안 풀었으면 5문항 먼저
    if _needs_daily_gate(nickname, month_key):
        _render_daily_gate(nickname, month_key)
        st.stop()  # 데일리 게이트 완료 후 재진입

    # ═══ 관문검사 체크 (Day 1, 11, 21, 31...) ═══
    required_stage = _get_required_stage(nickname, month_key)
    if required_stage is None:
        return  # 관문검사 날 아님 → 바로 입장

    student_tests = _get_student_tests(nickname, month_key)

    # 이미 완료 여부 확인
    stage_key = f"stage{required_stage}"
    stage_done = student_tests.get(stage_key) is not None

    if required_stage == 1:
        # ⭐ 재설계: Day 1은 설문만. 검사 없음.
        survey_done = student_tests.get("survey_pre") is not None
        if survey_done:
            return  # 설문 완료 → 입장
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

    # --- STAGE 1: 사전 설문만 (검사 없음) — 재설계 2026.04.24 ---
    if flow == "pre_survey":
        if st.session_state.get("_survey_pre_done"):
            return  # 설문 완료 → 바로 입장 (검사 X)
        else:
            _render_survey("pre", nickname, month_key)
            st.stop()

    # flow == "pre_test" 레거시 경로: 혹시 남은 세션 있으면 통과 처리
    if flow == "pre_test":
        return

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
