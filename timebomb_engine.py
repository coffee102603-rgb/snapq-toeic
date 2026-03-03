import datetime

"""
SnapQ Timebomb Engine
----------------------
전장(Arena) 공통 제한시간 판정 엔진.

- UI(카운트다운 표기)는 Streamlit이 담당
- 이 엔진은 "논리 시간 계산"만 담당

상태:
- SAFE / BOOM
"""


def start_timebomb(state_dict: dict, duration_sec: int) -> None:
    """
    세트 시작 시 호출.
    """
    now = datetime.datetime.now()
    state_dict["tb_start"] = now.timestamp()
    state_dict["tb_duration"] = int(duration_sec)
    state_dict["tb_status"] = "SAFE"


def check_timebomb(state_dict: dict):
    """
    현재 시각 기준 폭발 여부 판정.
    return: (status, remaining_sec_int_or_None)
    """
    if "tb_start" not in state_dict or "tb_duration" not in state_dict:
        return "SAFE", None

    try:
        start_ts = float(state_dict["tb_start"])
        duration = int(state_dict["tb_duration"])
    except Exception:
        # 키가 깨졌으면 안전모드
        return "SAFE", None

    now_ts = datetime.datetime.now().timestamp()
    elapsed = now_ts - start_ts
    remaining = duration - elapsed

    if remaining <= 0:
        state_dict["tb_status"] = "BOOM"
        return "BOOM", 0

    state_dict["tb_status"] = "SAFE"
    return "SAFE", int(remaining)


def get_timebomb_message(status: str) -> str:
    if status == "SAFE":
        return "🧨 아직 SAFE! 집중 유지하고 한 문제 더 밀어붙이자!"
    elif status == "BOOM":
        return "💥 시간 초과! 이번 세트는 여기까지, 다음 판에서 만회하자!"
    else:
        return "⏱ 타임어택 준비 중… 버튼을 누르면 카운트다운이 시작됩니다."
