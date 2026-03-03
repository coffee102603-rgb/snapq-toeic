import datetime
from typing import Literal, Optional

import streamlit as st

ArenaCode = Literal["P7", "P5", "P4", "ARMORY", "MOCK"]

# SnapQ TOEIC에서 공통으로 관리할 기본 상태 값들
_DEFAULT_STATE = {
    "nickname": "",
    "today_runs": 0,
    "last_played": None,
    "selected_arena": None,

    # P7 진행 상태
    "p7_current_set_id": None,
    "p7_current_step": 1,

    # P5 진행 상태
    "p5_current_set_id": None,
    "p5_current_step": 1,

    # ✅ P5 혼합형 폭발 공통값(안전 기본값)
    "p5_wrong_limit": 3,
    "p5_wrong_count": 0,

    # P4 진행 상태
    "p4_current_set_id": None,
    "p4_current_step": 1,

    # Armory 카운트 키 이름 통합
    "armory_vocab_count": 0,
    "armory_wrong_count": 0,
}


def init_base_state() -> None:
    """SnapQ 모든 페이지 최상단에서 반드시 호출해야 하는 초기화."""
    for key, default_value in _DEFAULT_STATE.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def set_nickname(nickname: str) -> None:
    st.session_state["nickname"] = nickname.strip()


def get_nickname() -> str:
    return st.session_state.get("nickname", "")


def mark_run_started(arena_code: ArenaCode) -> None:
    """전장을 시작할 때 호출."""
    st.session_state["selected_arena"] = arena_code
    st.session_state["today_runs"] = st.session_state.get("today_runs", 0) + 1
    st.session_state["last_played"] = datetime.date.today().isoformat()


def get_last_played() -> Optional[str]:
    return st.session_state.get("last_played")


def reset_p7_progress() -> None:
    st.session_state["p7_current_set_id"] = None
    st.session_state["p7_current_step"] = 1


def reset_p5_progress() -> None:
    st.session_state["p5_current_set_id"] = None
    st.session_state["p5_current_step"] = 1
    st.session_state["p5_wrong_count"] = 0


def reset_p4_progress() -> None:
    st.session_state["p4_current_set_id"] = None
    st.session_state["p4_current_step"] = 1


def get_selected_arena() -> Optional[ArenaCode]:
    return st.session_state.get("selected_arena")


def set_selected_arena(arena_code: ArenaCode) -> None:
    st.session_state["selected_arena"] = arena_code


# --- compatibility entrypoint (used by main_hub.py) ---
def init_battle_state():
    import streamlit as st
    import datetime

    ss = st.session_state

    defaults = {
        "pilot_nickname": "",
        "selected_arena": "main_hub",
        "today_visits": 0,
        "last_login_date": "",
        "active_days": set(),

        # ✅ P5 혼합형 폭발 기본값(호환 구간에서도 안전)
        "p5_wrong_limit": 3,
        "p5_wrong_count": 0,
    }
    for k, v in defaults.items():
        if k not in ss:
            ss[k] = v

    today = datetime.date.today().isoformat()
    if ss.get("last_login_date") != today:
        ss["last_login_date"] = today
        try:
            ss["active_days"].add(today)
        except Exception:
            ss["active_days"] = {today}

    return ss


# --- compatibility entrypoints (used by main_hub.py) ---
from pathlib import Path
import json


def _profile_path():
    base = Path(__file__).resolve().parents[2]  # SNAPQ_TOEIC/app
    cand1 = base / "data" / "profiles" / "pilot_profile.json"
    cand2 = base.parents[0] / "data" / "profiles" / "pilot_profile.json"
    return cand1 if cand1.parent.exists() else cand2


def load_profile():
    p = _profile_path()
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        try:
            return json.loads(p.read_text(encoding="utf-8-sig"))
        except Exception:
            return {}


def save_profile(profile: dict):
    p = _profile_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")


def record_activity_day(profile: dict | None = None):
    if profile is None:
        profile = load_profile()

    today = datetime.date.today()
    ym = today.strftime("%Y-%m")
    day = today.strftime("%Y-%m-%d")

    active = profile.get("active_days", {})
    days = set(active.get(ym, []))
    days.add(day)
    active[ym] = sorted(days)

    profile["active_days"] = active
    save_profile(profile)
    return profile


def get_monthly_active_days(profile: dict | None = None, ym: str | None = None) -> int:
    if profile is None:
        profile = load_profile()
    if ym is None:
        ym = datetime.date.today().strftime("%Y-%m")

    active = profile.get("active_days", {})
    return len(active.get(ym, []))


def compute_monthly_active_days(profile: dict | None = None, ym: str | None = None) -> int:
    return get_monthly_active_days(profile=profile, ym=ym)
