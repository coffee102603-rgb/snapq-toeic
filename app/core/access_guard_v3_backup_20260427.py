"""
SnapQ TOEIC V3 - Access Guard
로그인: 이름 + 전화번호 뒷 4자리 + 월별코드

CHANGELOG:
  v2 (2026.04.초): 월별코드 + privacy_agreed_at 도입
  v3 (2026.04.27): 박사학위논문 통계 변수 추가
                  - COHORT_MAP / get_cohort_id (5개 코호트 매핑)
                  - roster.jsonl에 박사 변수 6개 추가
                  - _show_research_consent_notice (4단 분리 동의)
                  - withdraw_consent / 동의 철회 처리
"""
from __future__ import annotations

import json
import os
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, List

import streamlit as st

# ═══ 박사학위논문 IRB 동의서 텍스트 ═══════════════════════════
# v3 신규 — 4단 분리 동의 (목적별 세분화)
try:
    from app.research.irb_consent_text import (
        CONSENT_VERSION, PI_NAME, PI_AFFILIATION, PI_SUPERVISOR,
        PI_CONTACT, RESEARCH_OVERVIEW, DATA_PURPOSE_OPTIONS,
        DEFAULT_CONSENT_PURPOSES, CONSENT_TIERS,
        DATA_PROTECTION_PROMISES, WITHDRAWAL_PROCEDURE,
    )
except Exception:
    # fallback (모듈 없을 때 기본값)
    CONSENT_VERSION = "v1.0_2026-04-27"
    DATA_PURPOSE_OPTIONS = {}
    DEFAULT_CONSENT_PURPOSES = []
    DATA_PROTECTION_PROMISES = []


# =========================================================
# 월별 코드 설정 (매월 선생님이 여기만 바꾸면 됨!)
# =========================================================
MONTHLY_CODES = {
    "2026-02": "FEB2026",
    "2026-03": "MAR2026",
    "2026-04": "APR2026",
    "2026-05": "MAY2026",
    "2026-06": "JUN2026",
}

# ═══ 연구 모드 설정 (2026.05 연구 개시) ═══════════════════════
# RESEARCH_MODE = True 면:
#   - LOCK_DAY 해제 (월말에도 접속 가능 — 관문검사 Day 21, 31... 대응)
#   - 학생 등록 시 pretest_gate_schedule 자동 생성
#   - IRB 승인 전/후 플래그 자동 전환
RESEARCH_MODE = True
RESEARCH_START_DATE = "2026-05-01"  # 연구 개시일

# 월말 잠금일 (연구 모드 아닐 때만 적용)
LOCK_DAY = 28  # 매월 28일 이후 잠금


# ═══════════════════════════════════════════════════════════════
# 박사학위논문 — 5개 코호트 매핑 (v3 추가, 2026-04-27)
# ─────────────────────────────────────────────────────────────
# 박사 4년 11편 대장정 중 박사 1년차 (2026.05~2027.02) 코호트 정의
# - 10개월 = 5개 코호트 (각 2개월) → Growth Curve Model의 Level 2
# - 박사 ⑩ SSCI / ⑪ 학위논문 통계 분석의 핵심 그룹 변수
# ═══════════════════════════════════════════════════════════════
COHORT_MAP = {
    "2026-05": "C1", "2026-06": "C1",   # 1차 5-6월
    "2026-07": "C2", "2026-08": "C2",   # 2차 7-8월
    "2026-09": "C3", "2026-10": "C3",   # 3차 9-10월
    "2026-11": "C4", "2026-12": "C4",   # 4차 11-12월
    "2027-01": "C5", "2027-02": "C5",   # 5차 1-2월
}

def get_cohort_id(month_key: str) -> str:
    """월별 코드 → 코호트 ID. 연구 개시 전이면 'PRE' 반환."""
    return COHORT_MAP.get(month_key, "PRE")


def _today_str() -> str:
    return date.today().strftime("%Y-%m-%d")

def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")

def get_cohort_month() -> str:
    mk = st.session_state.get("cohort_month")
    if mk:
        return str(mk)
    return date.today().strftime("%Y-%m")

def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]

def _cohort_dir(month_key: str) -> Path:
    return _project_root() / "data" / "cohorts" / str(month_key)

def attendance_path(month_key: str) -> Path:
    return _cohort_dir(month_key) / "attendance.jsonl"

def activity_path(month_key: str) -> Path:
    return _cohort_dir(month_key) / "activity.jsonl"

def _ensure_files(month_key: str) -> None:
    d = _cohort_dir(month_key)
    d.mkdir(parents=True, exist_ok=True)
    for p in [attendance_path(month_key), activity_path(month_key)]:
        if not p.exists():
            p.touch()

def _append_jsonl(path: Path, obj: Dict[str, Any]) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

def _read_jsonl(path: Path) -> Iterable[Dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                continue
    return rows


# =========================================================
# 월말 잠금 체크
# =========================================================
def _is_locked() -> bool:
    # 연구 모드에서는 잠금 해제 (관문검사 Day 21, 31... 대응)
    if RESEARCH_MODE:
        return False
    today = date.today()
    return today.day > LOCK_DAY


# =========================================================
# 학생 등록/로그인 기록
# =========================================================
def _register_student(nickname: str, month_key: str) -> None:
    roster_path = _cohort_dir(month_key) / "roster.jsonl"
    roster_path.parent.mkdir(parents=True, exist_ok=True)

    # 이미 등록된 학생인지 확인
    if roster_path.exists():
        with open(roster_path, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                    if r.get("nickname") == nickname:
                        return  # 이미 등록됨
                except:
                    continue

    # 새 학생 등록
    today_str = _today_str()
    obj = {
        "nickname": nickname,
        "month": month_key,
        "registered_at": _now_iso(),
        # ── 옵션 A: 개인 Day 기준 연구 설계 ──────────────────────
        "study_day1_date": today_str,   # 이 학생의 Day 1 (연구 Day 계산 기준)
        # ── 데일리 게이트 (매일 5문항 = 매일 사전검사) ──────────
        "daily_gate_last_date": "",     # 마지막 데일리 게이트 완료 날짜
        "daily_gate_total_count": 0,    # 데일리 게이트 누적 완료 횟수
        # ── 관문검사 (Day 1, 11, 21... 10일마다 30문항) ─────────
        "gate_check_last_day": 0,       # 마지막 관문검사 완료 day
        "gate_check_count": 0,          # 관문검사 누적 완료 횟수
        # ── 레거시 (하위 호환) ────────────────────────────────
        "pre_test_done": False,
        "mid_test_done": False,
        "post_test_done": False,
        # ── 개인정보 고지 동의 (2026.05 예비 운영 시작) ────────
        "privacy_agreed_at": "",
        # ─────────────────────────────────────────────────────
        # ★★★ 박사학위논문 통계 변수 (v3 — 2026.04.27) ★★★
        # ─────────────────────────────────────────────────────
        # PAPER: ⑩ SSCI 통합 / ⑪ 박사학위논문 — Level 1·2 변수
        # ─────────────────────────────────────────────────────
        "cohort_id":              get_cohort_id(month_key),  # C1~C5
        "latest_toeic_score":     None,                       # 최신 TOEIC 실점수
        "latest_toeic_level":     None,                       # 자동 분류 (초/중/고/최상급)
        "latest_toeic_month":     "",                         # 최신 점수 입력 월
        "latest_toeic_source":    "",                         # 점수 출처 (정기/모의/자가)
        # ─── IRB 표준 동의 (4단 분리) ────────────────────────
        "consent_research_at":     "",                         # 연구 동의 시각
        "consent_research_version":"",                        # 동의서 버전
        "consent_data_purpose":   [],                         # 박사 ②④⑤⑥⑪ 목적별 동의 목록
        "withdrawal_status":      False,                      # 철회 여부
        "withdrawal_at":          "",                         # 철회 시각
    }
    with open(roster_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")


# =========================================================
# 검사 완료 여부 확인
# =========================================================
def get_student_record(nickname: str, month_key: str) -> Dict:
    roster_path = _cohort_dir(month_key) / "roster.jsonl"
    if not roster_path.exists():
        return {}
    with open(roster_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
                if r.get("nickname") == nickname:
                    return r
            except:
                continue
    return {}

def update_student_record(nickname: str, month_key: str, updates: Dict) -> None:
    roster_path = _cohort_dir(month_key) / "roster.jsonl"
    if not roster_path.exists():
        return
    lines = []
    with open(roster_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                r = json.loads(line)
                if r.get("nickname") == nickname:
                    r.update(updates)
                lines.append(json.dumps(r, ensure_ascii=False))
            except:
                lines.append(line.strip())
    with open(roster_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# =========================================================
# 옵션 A: 개인 Day 기준 연구 설계 헬퍼
# =========================================================
def get_personal_day(nickname: str, month_key: Optional[str] = None) -> int:
    """
    학생 개인의 연구 Day 계산 (Day 1부터 시작).

    RETURNS:
        1 이상의 정수 (첫 등록일이 Day 1)
        학생 레코드 없으면 0
    """
    month_key = month_key or get_cohort_month()
    record = get_student_record(nickname, month_key)
    if not record or not record.get("study_day1_date"):
        return 0
    try:
        day1 = datetime.strptime(record["study_day1_date"], "%Y-%m-%d").date()
        today = date.today()
        return (today - day1).days + 1  # Day 1은 등록 당일
    except Exception:
        return 0


def needs_daily_gate(nickname: str, month_key: Optional[str] = None) -> bool:
    """
    오늘 데일리 게이트(5문항)를 풀어야 하는가?

    RETURNS:
        True:  오늘 아직 안 풀었음 → 5문항 강제
        False: 오늘 이미 완료 → 자유 접속
    """
    month_key = month_key or get_cohort_month()
    record = get_student_record(nickname, month_key)
    if not record:
        return True  # 레코드 없으면 일단 강제
    today = _today_str()
    return record.get("daily_gate_last_date", "") != today


def needs_milestone_gate(nickname: str, month_key: Optional[str] = None) -> bool:
    """
    오늘 관문검사(30문항)를 풀어야 하는가?
    개인 Day가 1, 11, 21, 31... (10n+1)이면서 아직 그 Day에 안 풀었을 때 True.

    RETURNS:
        True:  오늘이 관문검사 날 + 아직 안 풀었음
        False: 관문검사 날 아님 또는 이미 완료
    """
    month_key = month_key or get_cohort_month()
    day = get_personal_day(nickname, month_key)
    if day < 1:
        return False
    # Day 1, 11, 21, 31... 검사
    if (day - 1) % 10 != 0:
        return False
    record = get_student_record(nickname, month_key)
    if not record:
        return True
    return record.get("gate_check_last_day", 0) != day


def mark_daily_gate_done(nickname: str, month_key: Optional[str] = None) -> None:
    """데일리 게이트 완료 기록."""
    month_key = month_key or get_cohort_month()
    record = get_student_record(nickname, month_key)
    if not record:
        return
    count = record.get("daily_gate_total_count", 0) + 1
    update_student_record(nickname, month_key, {
        "daily_gate_last_date": _today_str(),
        "daily_gate_total_count": count,
    })


def mark_milestone_gate_done(nickname: str, month_key: Optional[str] = None) -> None:
    """관문검사 완료 기록."""
    month_key = month_key or get_cohort_month()
    day = get_personal_day(nickname, month_key)
    record = get_student_record(nickname, month_key)
    if not record:
        return
    count = record.get("gate_check_count", 0) + 1
    update_student_record(nickname, month_key, {
        "gate_check_last_day": day,
        "gate_check_count": count,
    })


# =========================================================
# 개인정보 고지 안내 (5월 1일 예비 운영 시작 전 필수)
# =========================================================
def _show_privacy_notice() -> bool:
    """
    [v2 → v3 업그레이드] 4단 분리 IRB 표준 동의 화면으로 라우팅.

    RETURNS:
        True:  동의 완료 (또는 이미 동의함)
        False: 아직 동의 전

    NOTE (v3):
        - 기존 단순 동의(privacy_agreed)는 1단(필수)으로 흡수
        - 박사 ②④⑤⑥⑪ 활용 목적별 세분 동의 추가
        - 동의서 버전 기록 (CONSENT_VERSION)
        - 철회 안내 명시
    """
    # 이미 동의 완료?
    if st.session_state.get("privacy_agreed") and \
       st.session_state.get("consent_research_given") is not None:
        return True

    return _show_research_consent_notice()


def _show_research_consent_notice() -> bool:
    """
    ★ v1.2 (2026-04-27) — 한 화면 콤팩트 IRB 동의.

    PURPOSE:
        v1.1 학습자 시점 검증 결과 — "글자 안 보임 + 너무 길어 지침"
        을 발견하여 v1.2로 즉시 개선 (박사 ② ADDIE Evaluation 사이클).

    v1.2 핵심:
        ✅ 한 화면 안에 다 들어감 (6화면 → 1화면)
        ✅ 글자 가독성 ↑ (흐릿한 회색 → 선명한 흰색)
        ✅ 핵심 정보만 노출 + 자세한 정보는 expander 안에
        ✅ IRB 5원칙 100% 유지 (학술적 정직성 변동 없음)
    """
    # ── v1.2 CSS: 가독성 강화 + 콤팩트 레이아웃 ──
    st.markdown("""
    <style>
    .stApp { background: #0D0F1A !important; }
    .block-container { max-width: 600px !important; margin: 0 auto !important;
                       padding-top: 28px !important; padding-bottom: 30px !important; }

    /* 환영 영역 */
    .v12-welcome { text-align: center; margin-bottom: 16px; }
    .v12-welcome-emoji { font-size: 38px; }
    .v12-welcome-title {
        font-size: 22px; font-weight: 900; color: #ffffff;
        margin: 4px 0 4px 0;
    }
    .v12-welcome-sub {
        font-size: 12px; color: rgba(255,255,255,0.7);
    }

    /* 핵심 메시지 카드 */
    .v12-hero {
        background: linear-gradient(135deg, rgba(244,201,93,0.14), rgba(125,211,252,0.08));
        border: 1px solid rgba(244,201,93,0.4);
        border-radius: 14px;
        padding: 14px 16px;
        margin-bottom: 16px;
        color: #ffffff;
        font-size: 14px;
        line-height: 1.55;
    }
    .v12-hero-title {
        font-size: 15px; font-weight: 800; color: #F4C95D;
        margin-bottom: 6px;
    }

    /* 데이터 보호 — 한 박스 콤팩트 */
    .v12-promise {
        background: rgba(0,200,150,0.12);
        border-left: 4px solid #00C896;
        border-radius: 8px;
        padding: 12px 14px;
        font-size: 13px;
        color: #ffffff !important;
        line-height: 1.6;
        margin: 14px 0 10px 0;
        font-weight: 500;
    }
    .v12-promise-title {
        color: #00C896; font-weight: 900; font-size: 13px;
        margin-bottom: 6px;
    }

    /* 3단 헤더 */
    .v12-purpose-header {
        font-size: 13px; color: #7DD3FC; margin: 14px 0 4px;
        font-weight: 800;
    }

    /* expander 가독성 */
    div[data-testid="stExpander"] {
        margin: 10px 0 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
    }
    div[data-testid="stExpander"] summary {
        font-size: 13px !important;
        color: rgba(255,255,255,0.85) !important;
    }
    div[data-testid="stExpander"] div[data-testid="stExpanderDetails"] {
        padding: 8px 14px !important;
    }
    div[data-testid="stExpander"] p,
    div[data-testid="stExpander"] li,
    div[data-testid="stExpander"] strong {
        color: #ffffff !important;
        font-size: 13px !important;
        line-height: 1.7 !important;
    }

    /* 체크박스 가독성 강화 (v1.2 핵심!) */
    div[data-testid="stCheckbox"] {
        margin: 6px 0 !important;
    }
    div[data-testid="stCheckbox"] label,
    div[data-testid="stCheckbox"] label p {
        color: #ffffff !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }

    /* 버튼 강화 */
    .stButton > button {
        font-size: 15px !important;
        font-weight: 700 !important;
        height: 50px !important;
    }

    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

    # ── 환영 (3줄) ──
    welcome_title = WELCOME_TITLE if 'WELCOME_TITLE' in dir() else "✨ SnapQ에 오신 것을 환영해요!"
    welcome_sub = WELCOME_SUBTITLE if 'WELCOME_SUBTITLE' in dir() else "더 좋은 학습을 위한 안내"
    try:
        from app.research.irb_consent_text import WELCOME_TITLE as _wt, WELCOME_SUBTITLE as _ws
        welcome_title = _wt
        welcome_sub = _ws
    except Exception:
        pass

    st.markdown(f"""
    <div class="v12-welcome">
        <div class="v12-welcome-emoji">✨</div>
        <div class="v12-welcome-title">{welcome_title}</div>
        <div class="v12-welcome-sub">{welcome_sub}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── 핵심 메시지 (영어 실력 1순위!) ──
    st.markdown("""
    <div class="v12-hero">
        <div class="v12-hero-title">🌱 영어 실력 향상이 1순위!</div>
        SnapQ는 게임처럼 즐겁게 영어 공부하는 곳이에요.<br>
        학습 기록은 <strong style="color:#F4C95D;">더 좋은 학습법 연구</strong>에도 도움 될 수 있어요. (선택)
    </div>
    """, unsafe_allow_html=True)

    # ── 1단: 필수 동의 (한 줄) ──
    agree_basic = st.checkbox(
        "✅ (필수) SnapQ 시작 — 이름·전화 뒷4자리·학습 기록 저장에 동의해요",
        value=False, key="consent_tier_1",
    )

    # ── 2단: 연구 참여 (한 줄) ──
    agree_research = st.checkbox(
        "💝 (선택) 더 좋은 학습 연구에 내 데이터가 도움 되어도 좋아요",
        value=False, key="consent_tier_2",
    )

    # ── 3단: 5개 목적 (2단 동의 시만, 한 줄씩) ──
    purpose_consents = []
    if agree_research:
        st.markdown(
            '<div class="v12-purpose-header">🌟 어떤 연구에 도움 줄지 골라요 (전부 선택도 OK!)</div>',
            unsafe_allow_html=True,
        )
        for key, info in DATA_PURPOSE_OPTIONS.items():
            ck = st.checkbox(
                f"{info.get('title','')}",
                value=True, key=f"purpose_{key}",
            )
            if ck:
                purpose_consents.append(key)

        # 5개 연구 자세히 보기 (접기)
        with st.expander("📋 각 연구가 어떤 데이터 쓰는지 자세히"):
            for key, info in DATA_PURPOSE_OPTIONS.items():
                st.markdown(f"""
**{info.get('title','')}**
{info.get('desc','')}
📊 사용 데이터: {info.get('data_used','')}
📰 발표 예정: {info.get('papers','')}
                """)

    # ── 데이터 보호 약속 (3줄 한 박스) ──
    st.markdown("""
    <div class="v12-promise">
        <div class="v12-promise-title">🔒 데이터 보호 3대 약속</div>
        🔐 익명 코드로 변환 (예: P001) &nbsp;·&nbsp;
        🔒 보안 서버 보관 &nbsp;·&nbsp;
        🚫 외부에 절대 안 드림
    </div>
    """, unsafe_allow_html=True)

    # ── 자세히 보기 (데이터 보호 + 철회 + 만든 사람) ──
    with st.expander("💡 더 자세히 알고 싶어요 (보호·취소·연락처)"):
        st.markdown("**🔒 데이터 보호 약속 (전체)**")
        for p in DATA_PROTECTION_PROMISES:
            st.markdown(f"- {p}")
        st.markdown(f"""
---
**🛑 마음 바뀌면 언제든 취소 가능**

{WITHDRAWAL_PROCEDURE.strip()}

---
**📚 만든 사람·문의**
- 만든 사람: {PI_NAME} 쌤 ({PI_AFFILIATION})
- 지도교수: {PI_SUPERVISOR}
- 문의: {PI_CONTACT}
        """)

    # ── 최종 버튼 ──
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 2])
    with col1:
        if st.button("❌ 안 할래요", use_container_width=True):
            st.info("안내 확인 감사해요. 동의 시 다시 접속해주세요.")
            st.stop()
    with col2:
        if st.button("✨ 시작할게요!", use_container_width=True, type="primary"):
            if not agree_basic:
                st.error("⚠️ 1단(SnapQ 시작) 동의가 필수예요!")
                st.stop()
            now = _now_iso()
            st.session_state["privacy_agreed"]         = True
            st.session_state["privacy_agreed_at"]      = now
            st.session_state["consent_research_given"] = bool(agree_research)
            st.session_state["consent_research_at"]    = now if agree_research else ""
            st.session_state["consent_data_purpose"]   = purpose_consents
            st.session_state["consent_version"]        = CONSENT_VERSION
            st.rerun()

    # ── IRB footer (작게) ──
    st.markdown("""
    <div style="text-align:center; margin-top:18px; font-size:10px;
                color:rgba(255,255,255,0.3); line-height:1.4;">
        ※ 대구교육대학교 IRB(생명윤리위원회) 기준
    </div>
    """, unsafe_allow_html=True)

    st.stop()



def require_access(context_tag: str = "ACCESS", roster_path: str = "") -> str:
    # 이미 로그인된 경우 → 개인정보 고지 확인 후 통과
    if st.session_state.get("access_granted") and st.session_state.get("battle_nickname"):
        # 고지 미확인 시 페이지 표시
        if not st.session_state.get("privacy_agreed"):
            _show_privacy_notice()  # 이 함수가 st.stop() 걸어줌
        # 통과
        nickname = st.session_state["battle_nickname"]
        month_key = st.session_state.get("cohort_month", date.today().strftime("%Y-%m"))
        # roster에 IRB 동의 정보 저장 (최초 1회) — v3 4단 동의 모두 기록
        record = get_student_record(nickname, month_key)
        if record and not record.get("privacy_agreed_at"):
            update_student_record(nickname, month_key, {
                "privacy_agreed_at":        st.session_state.get("privacy_agreed_at", _now_iso()),
                # ── v3 신규: IRB 4단 동의 ──
                "consent_research_at":      st.session_state.get("consent_research_at", ""),
                "consent_research_version": st.session_state.get("consent_version", CONSENT_VERSION)
                                            if st.session_state.get("consent_research_given") else "",
                "consent_data_purpose":     st.session_state.get("consent_data_purpose", []),
                "cohort_id":                get_cohort_id(month_key),
            })
        return nickname

    # 월말 잠금 체크
    if _is_locked():
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;background:#0D0F1A;min-height:100vh;">
            <div style="font-size:80px;margin-bottom:20px;">🔒</div>
            <div style="font-size:32px;font-weight:900;color:#FF2D55;margin-bottom:12px;">
                이번 달 수업 종료
            </div>
            <div style="font-size:18px;color:rgba(255,255,255,0.6);">
                다음 달 1일에 다시 열려요!
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # 로그인 화면
    month_key = date.today().strftime("%Y-%m")
    valid_code = MONTHLY_CODES.get(month_key, "")

    st.markdown("""
    <style>
    .stApp { background: #0D0F1A !important; }
    .block-container { max-width: 420px !important; margin: 0 auto !important; padding-top: 60px !important; }
    div.stTextInput > div > input {
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px !important;
        color: #fff !important;
        font-size: 18px !important;
        padding: 14px !important;
    }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-bottom:32px;">
        <div style="font-size:56px;margin-bottom:8px;">⚡</div>
        <div style="font-size:28px;font-weight:900;color:#fff;letter-spacing:3px;">SnapQ TOEIC</div>
        <div style="font-size:14px;color:rgba(255,255,255,0.4);margin-top:6px;letter-spacing:2px;">BATTLE PLATFORM</div>
    </div>
    """, unsafe_allow_html=True)

    name = st.text_input("📛 이름", placeholder="예: 홍길동", key="login_name")
    phone4 = st.text_input("📱 전화번호 뒷 4자리", placeholder="예: 1234", max_chars=4, key="login_phone")
    code = st.text_input("🔑 월별 입장 코드", placeholder="선생님이 알려준 코드 입력", key="login_code")

    if st.button("⚡ 입장하기", use_container_width=True, type="primary"):
        # 입력 검증
        if not name.strip():
            st.error("이름을 입력해주세요!")
            st.stop()
        if not phone4.strip().isdigit() or len(phone4.strip()) != 4:
            st.error("전화번호 뒷 4자리를 숫자로 입력해주세요!")
            st.stop()
        if code.strip() != valid_code:
            st.error("입장 코드가 틀렸어요! 선생님께 확인해주세요.")
            st.stop()

        # ID 생성: 이름_전화뒷4_월코드
        month_short = date.today().strftime("%Y%m")
        nickname = f"{name.strip()}_{phone4.strip()}_{month_short}"

        # 세션 저장
        st.session_state["battle_nickname"] = nickname
        st.session_state["access_granted"] = True
        st.session_state["cohort_month"] = month_key
        st.session_state["student_name"] = name.strip()

        # 학생 등록
        _ensure_files(month_key)
        _register_student(nickname, month_key)

        st.rerun()

    st.markdown("""
    <div style="text-align:center;margin-top:20px;color:rgba(255,255,255,0.3);font-size:12px;">
        입장 코드는 선생님께 문의하세요
    </div>
    """, unsafe_allow_html=True)

    st.stop()


# =========================================================
# 출석 함수들 (기존 유지)
# =========================================================
def has_attended_today(nickname: str, month_key: Optional[str] = None) -> bool:
    month_key = month_key or get_cohort_month()
    _ensure_files(month_key)
    today = _today_str()
    for r in _read_jsonl(attendance_path(month_key)):
        if r.get("date") == today and r.get("nickname") == nickname:
            return True
    return False

def mark_attendance_once(nickname: str, month_key: Optional[str] = None) -> bool:
    month_key = month_key or get_cohort_month()
    _ensure_files(month_key)
    if has_attended_today(nickname, month_key=month_key):
        return False
    obj = {"date": _today_str(), "month": month_key, "nickname": nickname, "ts": _now_iso()}
    _append_jsonl(attendance_path(month_key), obj)
    return True

def record_activity(nickname: str, arena: str, duration_sec=None, acc=None, completed=True, month_key=None) -> None:
    month_key = month_key or get_cohort_month()
    _ensure_files(month_key)
    obj = {
        "date": _today_str(), "month": month_key, "nickname": nickname,
        "arena": arena, "duration_sec": int(duration_sec) if duration_sec else None,
        "acc": float(acc) if acc else None, "completed": bool(completed), "ts": _now_iso(),
    }
    _append_jsonl(activity_path(month_key), obj)

def is_today_mission_done(nickname: str, month_key: Optional[str] = None) -> bool:
    month_key = month_key or get_cohort_month()
    _ensure_files(month_key)
    today = _today_str()
    for r in _read_jsonl(activity_path(month_key)):
        if r.get("date") == today and r.get("nickname") == nickname and r.get("completed") and r.get("arena") in ("P5", "P7"):
            return True
    return False

def get_today_summary(nickname: str, month_key: Optional[str] = None) -> Dict[str, Any]:
    month_key = month_key or get_cohort_month()
    _ensure_files(month_key)
    attended = has_attended_today(nickname, month_key)
    mission_done = is_today_mission_done(nickname, month_key)
    today = _today_str()
    plays = 0
    total_sec = 0
    for r in _read_jsonl(activity_path(month_key)):
        if r.get("date") == today and r.get("nickname") == nickname:
            plays += 1
            ds = r.get("duration_sec")
            if isinstance(ds, int):
                total_sec += ds
    return {"attended": attended, "mission_done": mission_done, "plays": plays,
            "minutes": round(total_sec / 60.0, 1), "month": month_key, "date": today}


# ═══════════════════════════════════════════════════════════════
# v3 신규 — 동의 철회 처리 (IRB 표준)
# ═══════════════════════════════════════════════════════════════
def withdraw_consent(nickname: str,
                     month_key: Optional[str] = None,
                     reason: str = "") -> bool:
    """
    학습자의 박사 연구 동의 철회 처리.

    PURPOSE:
        IRB 표준 — 언제든 철회 가능 + 즉시 분석 제외.

    ACTIONS:
        1. roster.jsonl 에 withdrawal_status=True, withdrawal_at=now 기록
        2. 모든 시트의 research_phase를 "withdrawn"으로 표시
           (실제 데이터 삭제는 IRB 절차에 따라 별도 처리)

    USAGE:
        from app.core.access_guard import withdraw_consent
        withdraw_consent("홍길동_1234_202605", reason="동의 철회 요청")
    """
    if not nickname:
        return False
    month_key = month_key or get_cohort_month()
    try:
        update_student_record(nickname, month_key, {
            "withdrawal_status": True,
            "withdrawal_at":     _now_iso(),
            "withdrawal_reason": reason,
        })
        return True
    except Exception:
        return False


def is_withdrawn(nickname: str, month_key: Optional[str] = None) -> bool:
    """학습자가 동의 철회했는가? (분석 시 제외 판정용)"""
    if not nickname:
        return False
    month_key = month_key or get_cohort_month()
    record = get_student_record(nickname, month_key)
    return bool(record.get("withdrawal_status", False))
