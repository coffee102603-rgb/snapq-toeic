"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE:     app/core/attendance_engine.py
ROLE:     출석·활동 자동 기록 엔진
VERSION:  SnapQ TOEIC V3 — 2026.04 (v3)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USAGE:
    from attendance_engine import mark_attendance_once, record_activity
    mark_attendance_once(nickname)
    record_activity(nickname, arena="POW_p5exam", acc=80.0, completed=True)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CHANGELOG:
  v1 (~2026.03): 초기 — has_attended_today, mark_attendance_once만 존재
                 → record_activity 미구현으로 2주간 사일런트 실패
  v2 (2026.04):  record_activity 추가했으나 pages/_storage.py 재호출 방식
                 → Streamlit Cloud 환경에서 sys.path 의존성 실패 추정
  v3 (2026.04):  _storage 의존성 제거, gspread 직접 호출로 단순화
                 + 실패 시 st.session_state에 에러 기록 (디버깅용)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATA:
    로컬:    data/cohorts/YYYY-MM/attendance.json
            data/cohorts/YYYY-MM/activity.jsonl
    Sheets: attendance 탭, activity 탭
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PAPER LINKS:
  ⑤ 탐색적 로그 분석 (2026.12): activity — 이탈·완주 구분의 핵심 변수
  ② ADDIE 개발 사례 (2026.12): v1→v2→v3 진화 자체가 Implementation 사례
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import os
from datetime import datetime, date
from pathlib import Path

import streamlit as st

BASE = Path(__file__).parent.parent.parent

# Google Sheets 헤더 스키마 (self-contained, _storage 의존 없음)
_SHEETS_HEADERS = {
    "attendance": ["date", "month", "nickname", "ts"],
    "activity":   ["date", "month", "nickname", "arena", "duration_sec",
                   "acc", "completed", "ts"],
    "session_events": ["timestamp", "user_id", "arena", "event",
                      "duration_sec", "extra_info", "research_phase"],
}


# ─────────────────────────────────────────────────────────────
# 내부 유틸
# ─────────────────────────────────────────────────────────────

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


def _save_to_sheets(log_key: str, entry: dict) -> bool:
    """
    Google Sheets에 직접 저장 (gspread 직접 호출, _storage 의존 없음).

    PURPOSE: Streamlit secrets에서 credentials 가져와 gspread로 시트에 append
    FAILURE: 실패 시 session_state에 에러 기록 (디버깅 가능)
    RETURNS: 성공 True, 실패 False
    """
    try:
        import gspread
        gc = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
        sh = gc.open_by_key(st.secrets["SPREADSHEET_ID"])
        headers = _SHEETS_HEADERS.get(log_key, list(entry.keys()))
        try:
            ws = sh.worksheet(log_key)
        except Exception:
            ws = sh.add_worksheet(title=log_key, rows=5000, cols=len(headers))
            ws.append_row(headers)
        if not ws.row_values(1):
            ws.append_row(headers)
        row = [str(entry.get(h, "")) if entry.get(h) is not None else "" for h in headers]
        ws.append_row(row)
        # 성공 기록 (디버깅용 — 최소 1회 성공 여부 체크)
        try:
            st.session_state[f"_sheets_ok_{log_key}"] = datetime.now().isoformat()[:19]
        except Exception:
            pass
        return True
    except Exception as e:
        # 디버깅용: 마지막 에러를 session_state에 기록
        try:
            st.session_state[f"_sheets_err_{log_key}"] = str(e)[:300]
        except Exception:
            pass
        return False


# ─────────────────────────────────────────────────────────────
# 공개 API
# ─────────────────────────────────────────────────────────────

def has_attended_today(nickname: str) -> bool:
    """오늘 이미 출석 기록이 있으면 True"""
    today = date.today().isoformat()
    data = _load_att()
    days = data.get(nickname, {}).get("days", [])
    return today in days


def mark_attendance_once(nickname: str):
    """
    세션당 1회만 출석 기록.

    - 로컬 attendance.json: 항상 갱신
    - Google Sheets attendance 탭: 오늘 첫 출석만 1행 추가
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
        pass

    # 2. Google Sheets attendance 탭 (오늘 첫 출석만)
    if is_new_today:
        now = datetime.now()
        _save_to_sheets("attendance", {
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
        nickname:     사용자 식별자 (빈 문자열이면 "guest"로 fallback)
        arena:        게임 영역 태그
                      - 02_Firepower:  "P5"
                      - 03_POW_HQ:     "POW_p5exam" / "POW_survival" /
                                       "POW_combo" / "POW_wordprison"
                      - 04_Decrypt_Op: "P7" (예정)
        acc:          정답률 (0-100, 소수 1자리)
        completed:    해당 모드의 대서사시 정의상 '완주' 조건 충족 여부
        duration_sec: 게임 지속 시간(초) — 생략 시 0

    STORAGE (이중 저장):
        1. data/cohorts/YYYY-MM/activity.jsonl  (로컬 append-only)
        2. Google Sheets "activity" 탭          (영구 보존)

    FAILURE MODE:
        실패해도 예외 전파 안 함 (try/except). Sheets 실패 시 에러는
        st.session_state["_sheets_err_activity"] 에 기록 (디버깅 가능).
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

    # 1. 로컬 activity.jsonl
    try:
        act_dir = BASE / "data" / "cohorts" / _get_month_key()
        act_dir.mkdir(parents=True, exist_ok=True)
        act_file = act_dir / "activity.jsonl"
        with open(act_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass

    # 2. Google Sheets activity 탭 (독립적 gspread 호출)
    _save_to_sheets("activity", entry)


def record_session_event(nickname: str = "",
                         arena: str = "",
                         event: str = "enter",
                         duration_sec: int = 0,
                         extra_info: str = ""):
    """
    세션 이벤트 기록 — session_events 시트.

    PURPOSE:
        학습자의 페이지 진입·이탈 등 미시적 세션 이벤트 추적.
        논문 ⑤ 탐색적 로그 분석의 "이탈 지점 식별" 변수.

    PARAMS:
        nickname:     사용자 식별자 (빈 문자열이면 "guest")
        arena:        페이지/영역 태그 ("MAIN_HUB", "P5", "POW_HQ", "P7" 등)
        event:        이벤트 종류
                      - "enter": 페이지 진입
                      - "leave": 페이지 떠남
                      - "quit":  중도 포기
                      - "play":  일반 이벤트
        duration_sec: 이벤트가 체류/완료까지 걸린 시간 (선택)
        extra_info:   부가 정보 (마지막 문항 번호 등, 최대 200자)

    STORAGE:
        Google Sheets "session_events" 탭 — 활동 흐름 분석용 append-only

    USAGE:
        # 페이지 진입 시 (각 페이지 상단, idempotent)
        if not st.session_state.get("_arena_entered_P5"):
            record_session_event(nickname, "P5", "enter")
            st.session_state["_arena_entered_P5"] = True

        # 중도 이탈 시
        record_session_event(nickname, "POW_p5exam", "quit",
                            extra_info=f"last_q={qi}")
    """
    if not nickname:
        nickname = "guest"

    now = datetime.now()
    entry = {
        "timestamp":      now.isoformat()[:19],
        "user_id":        nickname,
        "arena":          arena or "unknown",
        "event":          event,
        "duration_sec":   int(duration_sec) if duration_sec else 0,
        "extra_info":     str(extra_info)[:200] if extra_info else "",
        "research_phase": "pre_irb",  # TODO: IRB 승인 후 "main"으로 변경
    }

    _save_to_sheets("session_events", entry)
