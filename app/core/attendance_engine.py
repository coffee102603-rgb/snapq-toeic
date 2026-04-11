"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE:     app/core/attendance_engine.py
ROLE:     출석 자동 기록 엔진
VERSION:  SnapQ TOEIC V3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USAGE:
    from app.core.attendance_engine import mark_attendance_once, has_attended_today
    mark_attendance_once(nickname)
    attended = has_attended_today(nickname)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATA:
    data/cohorts/YYYY-MM/attendance.json
    {
      "nickname": {
        "days": ["2026-04-01", "2026-04-02", ...],
        "last_ts": "2026-04-12T08:30:00"
      }
    }
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import os
from datetime import datetime, date
from pathlib import Path

import streamlit as st

BASE = Path(__file__).parent.parent.parent


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


def has_attended_today(nickname: str) -> bool:
    """오늘 이미 출석 기록이 있으면 True"""
    today = date.today().isoformat()
    data = _load_att()
    days = data.get(nickname, {}).get("days", [])
    return today in days


def mark_attendance_once(nickname: str):
    """
    세션당 1회만 출석 기록.
    오늘 날짜가 이미 있으면 스킵.
    """
    if not nickname:
        return

    # 세션 내 중복 방지
    if st.session_state.get("_att_marked"):
        return

    today = date.today().isoformat()
    data = _load_att()

    user = data.get(nickname, {"days": [], "last_ts": ""})
    if today not in user["days"]:
        user["days"].append(today)
    user["last_ts"] = datetime.now().isoformat()[:19]
    data[nickname] = user

    try:
        _save_att(data)
    except Exception:
        pass  # Cloud 환경에서 write 실패해도 앱 멈추지 않음

    st.session_state["_att_marked"] = True
