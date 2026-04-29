"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE:     config/settings.py
ROLE:     전역 설정값 (페이지 설정, 타이머, 점수 등)
VERSION:  Snap 토익 V3
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
AI-AGENT NOTES:
  - PAGE_CONFIG: 모든 페이지에서 st.set_page_config(**PAGE_CONFIG) 호출
  - 타이머/점수 변경 시 이 파일만 수정하면 전체 반영
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

# 프로젝트 정보
PROJECT_NAME = "Snap 토익"
VERSION      = "3.0.0"
AUTHOR       = "최정은 (대구교육대학교 AI교육학과 박사과정)"

# 페이지 설정
PAGE_CONFIG = {
    "page_title": "Snap 토익",
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
