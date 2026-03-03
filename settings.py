"""
SnapQ TOEIC V2 - 전역 설정
"""

# 프로젝트 정보
PROJECT_NAME = "SnapQ TOEIC V2"
VERSION = "2.0.0"
AUTHOR = "최정은 선생님"

# 페이지 설정
PAGE_CONFIG = {
    "page_title": "SnapQ TOEIC",
    "page_icon": "💣",
    "layout": "wide",
    "initial_sidebar_state": "expanded"  # collapsed → expanded
}

# 타이머 설정
TIMER_SETTINGS = {
    "p5_timebomb": 40,
    "p7_reading": 60,
}

# HP 설정
HP_MAX = 3

# 점수 설정
SCORE_SETTINGS = {
    "correct_xp": 10,
    "correct_coin": 5,
    "perfect_bonus_xp": 50,
    "perfect_bonus_coin": 20,
}
