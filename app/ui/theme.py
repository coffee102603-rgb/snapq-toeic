"""
SnapQ TOEIC V2 - 디자인 시스템
색상, 폰트, 간격 통일
"""

# 색상 팔레트
COLORS = {
    # 다크 베이스
    "bg_dark": "#0F1419",
    "bg_card": "#1A1F2E",
    
    # Arena 색상
    "p5_primary": "#FF2D55",
    "p7_primary": "#00E5FF",
    "armory_primary": "#7C5CFF",
    
    # 상태 색상
    "success": "#10B981",
    "danger": "#EF4444",
    "warning": "#F59E0B",
    
    # 텍스트
    "text_primary": "#FFFFFF",
    "text_secondary": "rgba(255, 255, 255, 0.70)",
    
    # 버튼
    "button_bg": "#FFFFFF",
    "button_text": "#0F1419",
    "button_hover": "#00E5FF",
}

# 타이포그래피 (모바일 우선!)
FONTS = {
    "mobile": {
        "title": "28px",
        "body": "22px",
        "button": "20px",
        "weight_black": 900,
        "weight_bold": 700,
    },
    "desktop": {
        "title": "24px",
        "body": "18px",
        "button": "16px",
        "weight_black": 900,
        "weight_bold": 700,
    }
}

# 간격
SPACING = {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px",
}

# 둥근 모서리
RADIUS = {
    "sm": "8px",
    "md": "12px",
    "lg": "16px",
    "round": "999px",
}
