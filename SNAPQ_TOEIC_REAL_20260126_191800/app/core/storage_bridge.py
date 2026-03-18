import json
from pathlib import Path
import streamlit as st
from datetime import date
from typing import Optional, Dict, Any

# 이 파일 위치: app/core/storage_bridge.py
APP_DIR = Path(__file__).resolve().parents[1]

# 실제 JSON 파일 위치들
P7_PATH = APP_DIR / "data" / "p7_bank" / "p7_demo_sets.json"
P5_PATH = APP_DIR / "data" / "p5_bank" / "p5_demo_sets.json"

# ⭐ 수정: secret_armory.json 로 통합된 무기고 파일 사용
ARMORY_PATH = APP_DIR / "data" / "armory" / "secret_armory.json"

# ✅ 연구용 프로필 저장 경로 (학생별 파일)
PROFILE_DIR = APP_DIR / "data" / "profiles"


# ---------------------------------------------------------
# 공통 JSON 로더 / 세이버
# ---------------------------------------------------------
def _load_json(path: Path, label: str):
    """공통 JSON 로더. 실패하면 Streamlit 에러 메시지 출력."""

    try:
        if not path.exists():
            st.error(f"[{label}] 파일을 찾을 수 없습니다.\n경로: {path.as_posix()}")
            return None

        with path.open("r", encoding="utf-8-sig") as f:
            return json.load(f)

    except json.JSONDecodeError as e:
        st.error(f"[{label}] JSON 형식 오류: {e}\n경로: {path.as_posix()}")
        return None
    except Exception as e:
        st.error(f"[{label}] 파일 로딩 중 오류 발생: {e}\n경로: {path.as_posix()}")
        return None


def _save_json(path: Path, data, label: str):
    """공통 JSON 세이버."""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"[{label}] 데이터 저장 중 오류: {e}\n경로: {path.as_posix()}")


# ---------------------------------------------------------
# User Profile (연구용: 최소 필드 저장)
# ---------------------------------------------------------
def _profile_path(user_id: str) -> Path:
    """
    학생별 프로필 파일 경로.
    - 파일명에 사용할 수 없는 문자는 _ 로 치환(Windows 안전)
    """
    safe_id = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in user_id.strip())
    return PROFILE_DIR / f"{safe_id}.json"


def load_user_profile(user_id: str) -> Dict[str, Any]:
    """
    사용자 프로필 로드.
    없으면 빈 dict 반환.

    최소 필드(권장):
    - user_id
    - start_date (YYYY-MM-DD)
    - baseline_toeic_score (선택)
    - baseline_toeic_date (선택, YYYY-MM-DD)
    """
    if not user_id or not user_id.strip():
        return {}

    path = _profile_path(user_id)
    data = _load_json(path, "사용자 프로필")
    return data if isinstance(data, dict) else {}


def save_user_profile(
    user_id: str,
    start_date: Optional[str] = None,
    baseline_toeic_score: Optional[int] = None,
    baseline_toeic_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    사용자 프로필 저장(덮어쓰기).
    - start_date 기본값: 오늘
    - 점수/시험일은 None 허용(모르면 건너뛰기)

    반환: 저장된 profile dict
    """
    if not user_id or not user_id.strip():
        st.error("[사용자 프로필] user_id가 비어 있습니다.")
        return {}

    if start_date is None:
        start_date = date.today().isoformat()

    profile: Dict[str, Any] = {
        "user_id": user_id.strip(),
        "start_date": start_date,
        "baseline_toeic_score": baseline_toeic_score,
        "baseline_toeic_date": baseline_toeic_date,
    }

    path = _profile_path(user_id)
    _save_json(path, profile, "사용자 프로필")
    return profile


def upsert_user_profile(
    user_id: str,
    start_date: Optional[str] = None,
    baseline_toeic_score: Optional[int] = None,
    baseline_toeic_date: Optional[str] = None,
) -> Dict[str, Any]:
    """
    사용자 프로필 '있으면 유지, 없으면 생성' (현장 운영에 가장 안전).
    - 이미 파일이 있으면 기존 값을 우선 유지
    - 전달된 값은 None이 아닐 때만 업데이트

    반환: 최종 profile dict
    """
    existing = load_user_profile(user_id)

    # 없으면 새로 생성
    if not existing:
        return save_user_profile(
            user_id=user_id,
            start_date=start_date,
            baseline_toeic_score=baseline_toeic_score,
            baseline_toeic_date=baseline_toeic_date,
        )

    # 있으면 필요한 값만 업데이트
    updated = dict(existing)

    if start_date is not None:
        updated["start_date"] = start_date
    else:
        updated.setdefault("start_date", date.today().isoformat())

    if baseline_toeic_score is not None:
        updated["baseline_toeic_score"] = baseline_toeic_score
    else:
        updated.setdefault("baseline_toeic_score", None)

    if baseline_toeic_date is not None:
        updated["baseline_toeic_date"] = baseline_toeic_date
    else:
        updated.setdefault("baseline_toeic_date", None)

    updated["user_id"] = user_id.strip()

    path = _profile_path(user_id)
    _save_json(path, updated, "사용자 프로필")
    return updated


# ---------------------------------------------------------
# P7 Reading Arena
# ---------------------------------------------------------
def load_p7_set(set_id: int = 1):
    data = _load_json(P7_PATH, "P7 문제은행")
    if not data:
        return None

    sets = data.get("sets", [])
    for s in sets:
        if s.get("set_id") == set_id:
            return s
    return None


# ---------------------------------------------------------
# P5 Timebomb Arena
# ---------------------------------------------------------
def load_p5_sets():
    """
    ⚠️ 주의: 데모 모드용. 최신 P5 전장(p5_timebomb_arena)은 JSON을 직접 로딩함.
    이 함수는 예전 구조(easy/hard 기준)를 유지하기 위해 남겨둔다.
    """

    raw = _load_json(P5_PATH, "P5 문제은행")
    if not raw:
        return {
            "grammar": {"easy": [], "hard": []},
            "vocab": {"easy": [], "hard": []},
        }

    def add_answer(item: dict) -> dict:
        options = item.get("options", [])
        idx = item.get("answer_index", 0)
        answer = options[idx] if 0 <= idx < len(options) else ""
        new_item = dict(item)
        new_item["answer"] = answer
        return new_item

    grammar_easy = [
        add_answer(it)
        for it in raw
        if it.get("mode") == "grammar" and it.get("level") == "easy"
    ]
    grammar_hard = [
        add_answer(it)
        for it in raw
        if it.get("mode") == "grammar" and it.get("level") == "hard"
    ]
    vocab_easy = [
        add_answer(it)
        for it in raw
        if it.get("mode") == "vocab" and it.get("level") == "easy"
    ]
    vocab_hard = [
        add_answer(it)
        for it in raw
        if it.get("mode") == "vocab" and it.get("level") == "hard"
    ]

    return {
        "grammar": {"easy": grammar_easy, "hard": grammar_hard},
        "vocab": {"easy": vocab_easy, "hard": vocab_hard},
    }


# ---------------------------------------------------------
# Secret Armory (비밀 병기고)
# ---------------------------------------------------------
def load_armory() -> dict:
    """비밀 병기고 전체 데이터 로딩."""
    data = _load_json(ARMORY_PATH, "비밀 병기고")
    if data is None:
        return {}
    return data


def save_armory(data: dict):
    """비밀 병기고 저장."""
    _save_json(ARMORY_PATH, data, "비밀 병기고")

