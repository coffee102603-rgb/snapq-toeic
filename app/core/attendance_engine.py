"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE:     app/core/attendance_engine.py
ROLE:     출석·활동 자동 기록 엔진
VERSION:  SnapQ TOEIC V3 (2026.04 업데이트)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USAGE:
    from attendance_engine import mark_attendance_once, record_activity
    mark_attendance_once(nickname)
    record_activity(nickname, arena="POW_p5exam", acc=80.0, completed=True)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATA:
    로컬:      data/cohorts/YYYY-MM/attendance.json (구조적 사용자 DB)
              data/cohorts/YYYY-MM/activity.jsonl  (이벤트 로그 스트림)
    Sheets:   attendance 탭 (일별 출석 1회)
              activity 탭   (게임 종료 시마다)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CHANGELOG (2026.04):
  + record_activity() 신규 추가 — 2주간 사일런트 실패 문제 해결
    원인: 02_Firepower·03_POW_HQ 에서 import 시도하던 함수가 미구현
  + mark_attendance_once() — Sheets attendance 탭 저장 로직 추가
  + _storage 모듈 재사용으로 Google Sheets 저장 경로 통합
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PAPER LINKS:
  ⑤ 탐색적 로그 분석 (2026.12): activity — 이탈·완주 구분의 핵심 변수
  ② ADDIE 개발 사례 (2026.12): 이 버그 발견·수정 자체가 Implementation
                                  단계 자료 (silent failure 사례)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import os
import sys
from datetime import datetime, date
from pathlib import Path

import streamlit as st

BASE = Path(__file__).parent.parent.parent

# ── _storage 모듈을 import 가능하도록 pages 경로 추가 ──
# PURPOSE: Google Sheets 저장 경로를 _storage.save_to_sheets()로 통일
# rt_logs·forget_logs가 이미 이 경로로 정상 작동 중이므로 재사용
_PAGES_DIR = str(BASE / "pages")
if _PAGES_DIR not in sys.path:
    sys.path.insert(0, _PAGES_DIR)


def _get_month_key() -> str:
    return datetime.now().strftime("%Y-%m")


def _att_file() -> Path:
    return BASE / "data" / "cohorts" / _get_month_key() / "attendance.json"


def _load_att() -> dict:
    f = _att_file()
    if f.exists():
        try:
            return json.loads(f.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def _save_att(data: dict):
    f = _att_file()
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _save_to_sheets_safe(log_key: str, entry: dict):
    """
    _storage.save_to_sheets() 호출 래퍼 (안전).
    어떤 이유로든 실패해도 예외가 밖으로 전파되지 않음.
    """
    try:
        import _storage  # pages/_storage.py
        _storage.save_to_sheets(log_key, entry)
    except Exception:
        pass


def has_attended_today(nickname: str) -> bool:
    """오늘 이미 출석 기록이 있으면 True"""
    today = date.today().isoformat()
    data = _load_att()
    days = data.get(nickname, {}).get("days", [])
    return today in days


def mark_attendance_once(nickname: str):
    """
    세션당 1회만 출석 기록.

    - 로컬 attendance.json: 항상 갱신 (구조적 사용자 DB)
    - Google Sheets attendance 탭: 오늘 첫 출석인 경우만 1행 추가
    """
    if not nickname:
        return

    # 세션 내 중복 방지
    if st.session_state.get("_att_marked"):
        return

    today = date.today().isoformat()
    data = _load_att()

    user = data.get(nickname, {"days": [], "last_ts": ""})
    is_new_today = today not in user["days"]
    if is_new_today:
        user["days"].append(today)
    user["last_ts"] = datetime.now().isoformat()[:19]
    data[nickname] = user

    # 1. 로컬 파일 저장
    try:
        _save_att(data)
    except Exception:
        pass  # Cloud 환경에서 write 실패해도 앱 멈추지 않음

    # 2. Google Sheets attendance 탭 저장 (오늘 첫 출석만)
    if is_new_today:
        now = datetime.now()
        _save_to_sheets_safe("attendance", {
            "date":     today,
            "month":    now.strftime("%Y-%m"),
            "nickname": nickname,
            "ts":       now.isoformat()[:19],
        })

    st.session_state["_att_marked"] = True


def record_activity(nickname: str = "",
                    arena: str = "",
                    acc: float = 0.0,
                    completed: bool = False,
                    duration_sec: int = 0):
    """
    게임 결과 활동 기록 — activity.jsonl + Google Sheets activity 탭.

    PURPOSE:
        학습자가 어느 게임 영역을 언제 플레이했고, 어떤 정확도로, 완주했는지를
        이벤트 단위로 기록. 논문 ⑤ 탐색적 로그 분석의 종속변수(이탈·완주) 근거.

    PARAMS:
        nickname:     사용자 식별자 (빈 문자열/None이면 "guest"로 fallback)
        arena:        게임 영역 태그
                      - 02_Firepower:  "P5"
                      - 03_POW_HQ:     "POW_p5exam" / "POW_survival" /
                                       "POW_combo" / "POW_wordprison"
                      - 04_Decrypt_Op: "P7" (예정)
        acc:          정답률 (0-100, 소수 1자리)
        completed:    해당 모드의 대서사시 정의상 '완주' 조건 충족 여부
                      (각 호출부의 주석 참조)
        duration_sec: 게임 지속 시간(초) — 생략 시 0

    STORAGE (이중 저장):
        1. data/cohorts/YYYY-MM/activity.jsonl  (로컬 스트림, 빠른 분석용)
        2. Google Sheets "activity" 탭          (영구 보존, Cloud 재시작해도 유지)

    FAILURE MODE:
        두 저장 경로 모두 try/except로 감쌌음. 호출 자체가 실패해도
        게임은 멈추지 않음 (sg_phase 전환 등 이후 로직 계속 실행).

    HISTORY:
        2026.04 — 이 함수는 2주간 '정의되지 않은 상태'였음. 02_Firepower 등
        호출부에서 ImportError → except 블록 더미 함수로 fallback →
        사일런트 실패. 본 구현으로 해결.
    """
    if not nickname:
        nickname = "guest"

    now = datetime.now()
    entry = {
        "date":         now.strftime("%Y-%m-%d"),
        "month":        now.strftime("%Y-%m"),
        "nickname":     nickname,
        "arena":        arena or "unknown",
        "duration_sec": int(duration_sec) if duration_sec else 0,
        "acc":          round(float(acc), 1),
        "completed":    bool(completed),
        "ts":           now.isoformat()[:19],
    }

    # 1. 로컬 activity.jsonl (append-only 스트림)
    try:
        act_dir = BASE / "data" / "cohorts" / _get_month_key()
        act_dir.mkdir(parents=True, exist_ok=True)
        act_file = act_dir / "activity.jsonl"
        with open(act_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass  # Cloud 환경 write 실패해도 Sheets 경로로 계속

    # 2. Google Sheets activity 탭
    _save_to_sheets_safe("activity", entry)
