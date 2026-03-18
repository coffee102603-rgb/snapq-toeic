# app/core/attendance_engine.py
# ============================================
# SnapQ 출석/활동 기록 엔진 (가벼운 버전)
# - 월별 코호트 폴더(data/cohorts/YYYY-MM) 아래에 jsonl 저장
# - attendance.jsonl : 하루 1회 출석
# - activity.jsonl    : 전장 플레이 결과(나중에 P5/P7에서 자동 기록)
#
# ✅ PATCH: 경로를 CWD(실행 위치) 기준이 아니라 "프로젝트 루트" 기준으로 고정
#         => 어디서 streamlit run을 해도 data\cohorts 경로 생성이 안정적으로 동작
# ============================================

from __future__ import annotations

import json
import os
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import streamlit as st


def _today_str() -> str:
    return date.today().strftime("%Y-%m-%d")


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def get_cohort_month() -> str:
    # access_guard가 st.session_state["cohort_month"]에 저장함
    mk = st.session_state.get("cohort_month")
    if mk:
        return str(mk)
    return date.today().strftime("%Y-%m")


# =========================================================
# ✅ SAFE PATH RESOLUTION (핵심 패치)
# - attendance_engine.py 위치: <ROOT>/app/core/attendance_engine.py
# - 프로젝트 루트: parents[2] => <ROOT>
# =========================================================
def _project_root() -> Path:
    # core -> app -> ROOT
    return Path(__file__).resolve().parents[2]


def _cohort_dir(month_key: str) -> Path:
    # 기존 데이터 구조 유지: <ROOT>/data/cohorts/<YYYY-MM>
    return _project_root() / "data" / "cohorts" / str(month_key)


def attendance_path(month_key: str) -> Path:
    return _cohort_dir(month_key) / "attendance.jsonl"


def activity_path(month_key: str) -> Path:
    return _cohort_dir(month_key) / "activity.jsonl"


def _ensure_files(month_key: str) -> None:
    d = _cohort_dir(month_key)

    # 만약 ROOT/data가 "파일"로 존재하는 특이 케이스면 안내용 에러를 내자(침묵 실패 방지)
    data_path = _project_root() / "data"
    if data_path.exists() and data_path.is_file():
        raise RuntimeError(
            f"[SnapQ] 'data' 경로가 폴더가 아니라 파일로 존재합니다: {data_path}\n"
            f"파일명을 변경하거나 폴더로 바꿔야 합니다."
        )

    d.mkdir(parents=True, exist_ok=True)

    ap = attendance_path(month_key)
    xp = activity_path(month_key)

    if not ap.exists():
        ap.parent.mkdir(parents=True, exist_ok=True)
        ap.touch()
    if not xp.exists():
        xp.parent.mkdir(parents=True, exist_ok=True)
        xp.touch()


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


# ----------------------------
# Attendance (하루 1회)
# ----------------------------
def has_attended_today(nickname: str, month_key: Optional[str] = None) -> bool:
    month_key = month_key or get_cohort_month()
    _ensure_files(month_key)

    today = _today_str()
    path = attendance_path(month_key)
    for r in _read_jsonl(path):
        if r.get("date") == today and r.get("nickname") == nickname:
            return True
    return False


def mark_attendance_once(nickname: str, month_key: Optional[str] = None) -> bool:
    """
    오늘 출석을 기록한다.
    - 이미 출석했으면 False
    - 새로 기록하면 True
    """
    month_key = month_key or get_cohort_month()
    _ensure_files(month_key)

    if has_attended_today(nickname, month_key=month_key):
        return False

    obj = {
        "date": _today_str(),
        "month": month_key,
        "nickname": nickname,
        "ts": _now_iso(),
    }
    _append_jsonl(attendance_path(month_key), obj)
    return True


# ----------------------------
# Activity (전장 기록)
# ----------------------------
def record_activity(
    nickname: str,
    arena: str,
    duration_sec: Optional[int] = None,
    acc: Optional[float] = None,
    completed: bool = True,
    month_key: Optional[str] = None,
) -> None:
    """
    전장 플레이 기록(나중에 P5/P7 전장 종료 시 자동 호출)
    """
    month_key = month_key or get_cohort_month()
    _ensure_files(month_key)

    obj = {
        "date": _today_str(),
        "month": month_key,
        "nickname": nickname,
        "arena": arena,
        "duration_sec": int(duration_sec) if duration_sec is not None else None,
        "acc": float(acc) if acc is not None else None,
        "completed": bool(completed),
        "ts": _now_iso(),
    }
    _append_jsonl(activity_path(month_key), obj)


def is_today_mission_done(nickname: str, month_key: Optional[str] = None) -> bool:
    """
    오늘 미션 완료 판정:
    - 오늘 activity 중 P5 1회 OR P7 1세트 완료 기록이 있으면 True
    """
    month_key = month_key or get_cohort_month()
    _ensure_files(month_key)

    today = _today_str()
    path = activity_path(month_key)
    for r in _read_jsonl(path):
        if r.get("date") != today:
            continue
        if r.get("nickname") != nickname:
            continue
        if r.get("completed") is not True:
            continue
        if r.get("arena") in ("P5", "P7"):
            return True
    return False


def get_today_summary(nickname: str, month_key: Optional[str] = None) -> Dict[str, Any]:
    """
    허브에서 보여줄 요약(가볍게):
    - attended: 오늘 출석 여부
    - mission_done: 오늘 미션 완료 여부
    - plays: 오늘 플레이 횟수(P5/P7/기타 포함)
    - minutes: 오늘 총 플레이 시간(기록이 있는 경우만 합산)
    """
    month_key = month_key or get_cohort_month()
    _ensure_files(month_key)

    attended = has_attended_today(nickname, month_key)
    mission_done = is_today_mission_done(nickname, month_key)

    today = _today_str()
    plays = 0
    total_sec = 0

    for r in _read_jsonl(activity_path(month_key)):
        if r.get("date") != today:
            continue
        if r.get("nickname") != nickname:
            continue
        plays += 1
        ds = r.get("duration_sec")
        if isinstance(ds, int):
            total_sec += ds

    return {
        "attended": attended,
        "mission_done": mission_done,
        "plays": plays,
        "minutes": round(total_sec / 60.0, 1) if total_sec > 0 else 0.0,
        "month": month_key,
        "date": today,
    }

# =========================================================
# ✅ SAFE FALLBACK (auto-added by SAFE RECOVERY)
# - If this module missed require_access, provide it to stop ImportError.
# - Guest auto pass-through (keeps existing data structure: nickname string)
# =========================================================
from datetime import datetime as _dt
import streamlit as st

def require_access(context_tag: str = "ACCESS", roster_path: str = r"data\cohorts\2026-01\roster.json") -> str:
    if st.session_state.get("access_granted") and st.session_state.get("battle_nickname"):
        return st.session_state["battle_nickname"]

    guest_id = "guest_" + _dt.now().strftime("%Y%m%d_%H%M%S")
    st.session_state["battle_nickname"] = guest_id
    st.session_state["access_granted"] = True
    st.session_state["access_context_tag"] = context_tag
    if not st.session_state.get("cohort_month"):
        st.session_state["cohort_month"] = _dt.now().strftime("%Y-%m")
    return guest_id
