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

# 월말 잠금일 (이 날 이후 접속 불가)
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
    obj = {
        "nickname": nickname,
        "month": month_key,
        "registered_at": _now_iso(),
        "pre_test_done": False,
        "mid_test_done": False,
        "post_test_done": False,
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
# 메인 로그인 함수
# =========================================================
def require_access(context_tag: str = "ACCESS", roster_path: str = "") -> str:
    # 이미 로그인된 경우
    if st.session_state.get("access_granted") and st.session_state.get("battle_nickname") and st.session_state.get("_nick_verified"):
        return st.session_state["battle_nickname"]

    # 별명 입력 단계 (로그인 후, 별명 미입력시)
    if st.session_state.get("access_granted") and st.session_state.get("battle_nickname"):
        import re as _re
        _nick_key = "student_nickname"
        _sid = st.session_state["battle_nickname"]
        _mk = st.session_state.get("cohort_month", "")
        _rec = get_student_record(_sid, _mk) if _mk else {}
        if _rec.get(_nick_key):
            st.session_state[_nick_key] = _rec[_nick_key]
            st.session_state["_nick_verified"] = True
            st.rerun()
        st.markdown('''<style>.stApp{background:#0D0F1A!important;}.block-container{max-width:420px!important;margin:0 auto!important;padding-top:60px!important;}div.stTextInput>div>input{background:rgba(255,255,255,0.07)!important;border:1px solid rgba(255,255,255,0.15)!important;border-radius:12px!important;color:#fff!important;font-size:24px!important;padding:14px!important;text-align:center!important;letter-spacing:6px!important;}</style>''', unsafe_allow_html=True)
        st.markdown('''<div style="text-align:center;margin-bottom:32px;"><div style="font-size:56px;margin-bottom:8px;">😎</div><div style="font-size:22px;font-weight:900;color:#fff;letter-spacing:2px;">나만의 별명</div><div style="font-size:14px;color:rgba(255,255,255,0.4);margin-top:6px;">한글 2글자 · 딱 한 번만 등록해요!</div></div>''', unsafe_allow_html=True)
        _nk_input = st.text_input(label="별명", max_chars=2, placeholder="예: 보리", key="nick_input", label_visibility="collapsed")
        st.markdown('''<div style="text-align:center;color:rgba(255,255,255,0.4);font-size:12px;margin-top:8px;">한글 2글자로 입력해주세요</div>''', unsafe_allow_html=True)
        if st.button("입장 →", key="nick_btn", use_container_width=True):
            _nk = _nk_input.strip()
            if len(_nk) == 2 and all('\uAC00' <= _ch <= '\uD7A3' for _ch in _nk):
                update_student_record(_sid, _mk, {_nick_key: _nk})
                st.session_state[_nick_key] = _nk
                st.session_state["_nick_verified"] = True
                st.rerun()
            else:
                st.error("❌ 한글 2글자로 입력해주세요. 예: 보리")
        st.stop()

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
        st.session_state["_nick_verified"] = False
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
