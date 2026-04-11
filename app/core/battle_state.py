"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE:     app/core/battle_state.py
ROLE:     학생 프로필 / 전투 상태 로드 유틸
VERSION:  SnapQ TOEIC V3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USAGE:
    from app.core.battle_state import load_profile
    profile = load_profile(nickname)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DATA SOURCE:
    storage_data.json  (word_prison, rt_logs, saved_expressions)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
from pathlib import Path

BASE = Path(__file__).parent.parent.parent
STORAGE_FILE = BASE / "storage_data.json"


def _load_storage() -> dict:
    if STORAGE_FILE.exists():
        try:
            return json.loads(STORAGE_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


def load_profile(nickname: str) -> dict:
    """
    학생의 전투 프로필 반환.

    Returns:
        {
            "nickname": str,
            "word_prison": list,       # 단어수용소 포로 목록
            "rt_logs": list,           # 연구 로그
            "saved_expressions": list, # 저장된 표현
            "pretest": dict,           # 사전검사 결과
        }
    """
    data = _load_storage()

    word_prison = data.get("word_prison", [])
    # word_prison이 dict(닉네임 키) 구조일 수도 있음
    if isinstance(word_prison, dict):
        word_prison = word_prison.get(nickname, [])

    rt_logs = data.get("rt_logs", [])
    if isinstance(rt_logs, dict):
        rt_logs = rt_logs.get(nickname, [])

    saved_expressions = data.get("saved_expressions", [])
    if isinstance(saved_expressions, dict):
        saved_expressions = saved_expressions.get(nickname, [])

    pretest = data.get("pretest", {})
    if isinstance(pretest, dict):
        pretest = pretest.get(nickname, {})

    return {
        "nickname": nickname,
        "word_prison": word_prison,
        "rt_logs": rt_logs,
        "saved_expressions": saved_expressions,
        "pretest": pretest,
    }
