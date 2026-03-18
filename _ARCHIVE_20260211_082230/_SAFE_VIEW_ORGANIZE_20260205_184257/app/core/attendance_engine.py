# app/core/attendance_engine.py
# ============================================
# SnapQ 출석/활동 기록 엔진 (가벼운 버전)
# - 월별 코호트 폴더(data/cohorts/YYYY-MM) 아래에 jsonl 저장
# - attendance.jsonl : 하루 1회 출석
# - activity.jsonl    : 전장 플레이 결과(나중에 P5/P7에서 자동 기록)
#
# ✅ SAFE PATCH:
#   경로를 실행 위치(CWD) 기준이 아니라 "프로젝트 루트" 기준으로 고정
#   => snapq_toeic / SNAPQ_TOEIC 섞여도 data\cohorts 생성이 안정적으로 동작
# ============================================

from __future__ import annotations

import json
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

import streamlit as st


def _today_str() -> str:
    return date.today().strftime("%Y-%m-%d")


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def get_cohort_month() -> str:
    mk = st.session_state.get("cohort_month")
    if mk:
        return str(mk)
    return date.today().strftime("%Y-%m")


# =========================================================
# ✅ SAFE PATH RESOLUTION
# attendance_engine.py 위치: <ROOT>/app/core/attendance_engine.py
# ROOT = parents[2] (core -> app -> ROOT)
# =========================================================
def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _cohort_dir(month_key: str) -> Path:
    return _project_root() / "data" / "cohorts" / str(month_key)


def attendance_path(month_key: str) -> Path:
    return _cohort_dir(month_key) / "attendance.jsonl"


def activity_path(month_key: str) -> Path:
    return _cohort_dir(month_key) / "activity.jsonl"


def _ensure_files(month_key: str) -> None:
    root = _project_root()

    # 특이 케이스 방어: data가 "파일"이면 폴더 생성 불가
    data_path = root / "data"
    if data_path.exists() and data_path.is_file():
        raise RuntimeError(
            f"[SnapQ] 'data' 경로가 폴더가 아니라 파일로 존재합니다: {data_path}"
        )

    d = _cohort_dir(month_key)
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


def record_activity(
    nickname: str,
    arena: str,
    duration_sec: Optional[int] = None,
    acc: Optional[float] = None,
    completed: bool = True,
    month_key: Optional[str] = None,
) -> None:
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
    month_key = month_key or get_cohort_month()
    _ensure_files(month_key)

    today = _today_str()
    for r in _read_jsonl(activity_path(month_key)):
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
