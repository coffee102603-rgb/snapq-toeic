"""
SnapQ TOEIC V2 - Access Guard
로그인: 이름 + 전화번호 뒷 4자리 + 월별코드
"""
from __future__ import annotations

import json
import os
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import streamlit as st


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
    최초 접속 시 개인정보 수집 고지 및 동의 페이지.

    RETURNS:
        True:  동의 완료 (또는 이미 동의함)
        False: 아직 동의 전

    NOTE:
        - session_state에 'privacy_agreed' 저장 (세션 동안만 유효)
        - roster에 'privacy_agreed_at' 저장 (영구 기록)
        - IRB 승인 전 '예비 운영' 단계에서도 최소한의 고지 의무 충족
    """
    # 이미 동의 완료?
    if st.session_state.get("privacy_agreed"):
        return True

    st.markdown("""
    <style>
    .stApp { background: #0D0F1A !important; }
    .block-container { max-width: 720px !important; margin: 0 auto !important; padding-top: 40px !important; }
    .privacy-box {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(244,201,93,0.3);
        border-radius: 16px;
        padding: 28px;
        margin: 20px 0;
        color: rgba(255,255,255,0.85);
        line-height: 1.8;
        font-size: 15px;
    }
    .privacy-title {
        font-size: 22px;
        font-weight: 900;
        color: #F4C95D;
        margin-bottom: 16px;
    }
    .privacy-h3 {
        font-size: 16px;
        font-weight: 800;
        color: #7DD3FC;
        margin-top: 18px;
        margin-bottom: 8px;
    }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-bottom:24px;">
        <div style="font-size:48px;margin-bottom:8px;">⚡</div>
        <div style="font-size:28px;font-weight:900;color:#fff;letter-spacing:2px;">SnapQ TOEIC</div>
    </div>
    """, unsafe_allow_html=True)

    privacy_html = (
        '<div class="privacy-box">'
        '<div class="privacy-title">📋 SnapQ 이용 안내</div>'
        '<p style="font-size:15px;">안녕하세요! 😊<br>'
        'SnapQ는 최정은 쌤이 여러분을 위해 만든 토익 학습 플랫폼이에요.</p>'
        '<div class="privacy-h3">✏️ 무엇을 기록하나요?</div>'
        '<ul>'
        '<li>이름, 전화번호 뒷 4자리</li>'
        '<li>학습 기록 (문제 푼 내역, 반응 시간)</li>'
        '</ul>'
        '<p style="font-size:14px;color:rgba(255,255,255,0.7);">→ 여러분 맞춤 피드백을 위해서만 사용해요!</p>'
        '<div class="privacy-h3">💡 학습 개선 안내</div>'
        '<p>여러분이 푼 문제와 결과는 더 나은 학습 서비스를 만드는 데 '
        '활용될 수 있어요.<br>단, 이름이나 개인 정보는 절대 공개되지 않습니다.</p>'
        '<div class="privacy-h3">🔒 안전하게 보관해요</div>'
        '<ul>'
        '<li>모든 정보는 암호화되어 저장됩니다</li>'
        '<li>원하시면 언제든 삭제 요청하실 수 있어요</li>'
        '</ul>'
        '<p style="font-size:14px;color:rgba(255,255,255,0.6);margin-top:16px;">문의: 최정은 쌤</p>'
        '</div>'
    )
    st.markdown(privacy_html, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("❌ 동의하지 않음", use_container_width=True):
            st.info("안내를 확인해주셔서 감사합니다. 동의 시 다시 접속해주세요.")
            st.stop()
    with col2:
        if st.button("✅ 안내 확인 · 동의합니다", use_container_width=True, type="primary"):
            st.session_state["privacy_agreed"] = True
            st.session_state["privacy_agreed_at"] = _now_iso()
            st.rerun()

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
        # roster에 privacy_agreed_at 저장 (최초 1회)
        record = get_student_record(nickname, month_key)
        if record and not record.get("privacy_agreed_at"):
            update_student_record(nickname, month_key, {
                "privacy_agreed_at": st.session_state.get("privacy_agreed_at", _now_iso())
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
