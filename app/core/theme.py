"""
SnapQ TOEIC V2 - 통합 디자인 시스템
올 블랙 + 네온 테마

사용법:
    from app.core.theme import apply_global_css
    apply_global_css()
"""

# =========================================================
# 색상 팔레트 (전체 플랫폼 공통)
# =========================================================
COLORS = {
    # 배경
    "bg":        "#0A0A0F",   # 메인 배경 (거의 블랙)
    "bg_card":   "#111118",   # 카드 배경
    "bg_input":  "#1A1A24",   # 입력창 배경

    # 네온 포인트 (각 섹션별 1색만 사용)
    "neon_blue":   "#00D4FF",  # P5 Arena / 기본 포인트
    "neon_green":  "#00FF88",  # 성공 / 정답
    "neon_red":    "#FF3355",  # 위험 / 오답
    "neon_yellow": "#FFD600",  # 경고 / 강조
    "neon_purple": "#A855F7",  # 무기고 / 기타

    # 텍스트
    "text":      "#FFFFFF",
    "text_sub":  "rgba(255,255,255,0.55)",
    "text_dim":  "rgba(255,255,255,0.30)",

    # 테두리
    "border":    "rgba(255,255,255,0.08)",
    "border_glow": "rgba(0,212,255,0.4)",
}

# =========================================================
# 전역 CSS (모든 페이지 공통 적용)
# =========================================================
def global_css() -> str:
    c = COLORS
    return f"""
    <style>
    /* ── 기본 리셋 ── */
    #MainMenu, footer, header {{ visibility: hidden; }}
    .stApp {{
        background: {c['bg']} !important;
        color: {c['text']} !important;
    }}
    .block-container {{
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
    }}

    /* ── 버튼 공통 ── */
    div.stButton > button {{
        background: transparent !important;
        border: 2px solid {c['neon_blue']} !important;
        color: {c['neon_blue']} !important;
        font-weight: 900 !important;
        border-radius: 12px !important;
        transition: all 0.2s ease !important;
        -webkit-text-fill-color: {c['neon_blue']} !important;
    }}
    div.stButton > button:hover {{
        background: {c['neon_blue']} !important;
        color: {c['bg']} !important;
        -webkit-text-fill-color: {c['bg']} !important;
        box-shadow: 0 0 20px {c['border_glow']} !important;
    }}
    div.stButton > button[kind="primary"] {{
        background: {c['neon_blue']} !important;
        border: 2px solid {c['neon_blue']} !important;
        color: {c['bg']} !important;
        -webkit-text-fill-color: {c['bg']} !important;
        box-shadow: 0 0 20px {c['border_glow']} !important;
    }}
    div.stButton > button[kind="primary"]:hover {{
        box-shadow: 0 0 35px {c['border_glow']} !important;
        transform: translateY(-1px) !important;
    }}

    /* ── 입력창 ── */
    .stTextInput input,
    [data-testid="stTextInput"] input {{
        background: {c['bg_input']} !important;
        color: {c['text']} !important;
        -webkit-text-fill-color: {c['text']} !important;
        border: 1.5px solid {c['border']} !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
    }}
    .stTextInput input:focus,
    [data-testid="stTextInput"] input:focus {{
        border-color: {c['neon_blue']} !important;
        box-shadow: 0 0 12px {c['border_glow']} !important;
    }}
    .stTextInput label p,
    [data-testid="stTextInput"] label p {{
        color: {c['text_sub']} !important;
        font-weight: 700 !important;
    }}

    /* ── 알림 ── */
    div.stAlert {{
        background: {c['bg_card']} !important;
        border-radius: 12px !important;
    }}

    /* ── 구분선 ── */
    hr {{
        border-color: {c['border']} !important;
    }}
    </style>
    """

# =========================================================
# 로그인 페이지 전용 CSS
# =========================================================
def login_css() -> str:
    c = COLORS
    return global_css() + f"""
    <style>
    .block-container {{
        max-width: 420px !important;
        margin: 0 auto !important;
        padding: 30px 16px !important;
    }}
    .stTextInput input,
    [data-testid="stTextInput"] input {{
        font-size: 20px !important;
        padding: 16px 20px !important;
        min-height: 60px !important;
        background: #ffffff !important;
        color: #000000 !important;
        -webkit-text-fill-color: #000000 !important;
        caret-color: #000000 !important;
    }}
    .stTextInput input:-webkit-autofill,
    [data-testid="stTextInput"] input:-webkit-autofill {{
        -webkit-text-fill-color: #000000 !important;
        -webkit-box-shadow: 0 0 0px 1000px #ffffff inset !important;
    }}
    .stTextInput label p,
    [data-testid="stTextInput"] label p {{
        font-size: 20px !important;
        color: rgba(255,255,255,0.9) !important;
    }}
    div.stButton > button {{
        font-size: 24px !important;
        font-weight: 900 !important;
        height: 72px !important;
    }}
    div.stAlert p {{ font-size: 18px !important; font-weight: 700 !important; }}
    </style>
    """

# =========================================================
# 메인허브 전용 CSS
# =========================================================
def hub_css() -> str:
    c = COLORS
    return global_css() + f"""
    <style>
    /* 카드 */
    .sq-card {{
        background: {c['bg_card']};
        border: 1.5px solid {c['border']};
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 12px;
    }}
    .sq-card:hover {{
        border-color: {c['neon_blue']};
        box-shadow: 0 0 16px {c['border_glow']};
    }}
    /* 네온 타이틀 */
    .sq-title {{
        font-size: 28px;
        font-weight: 900;
        color: {c['neon_blue']};
        text-shadow: 0 0 20px {c['border_glow']};
        letter-spacing: 2px;
    }}
    /* 배지 */
    .sq-badge {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 13px;
        font-weight: 700;
        border: 1px solid {c['neon_blue']};
        color: {c['neon_blue']};
    }}
    </style>
    """

# =========================================================
# 전투 페이지 전용 CSS
# =========================================================
def battle_css() -> str:
    c = COLORS
    return global_css() + f"""
    <style>
    /* 문제박스 */
    .sq-qbox {{
        background: {c['bg_card']};
        border: 2px solid {c['neon_blue']};
        border-radius: 16px;
        padding: 24px;
        margin: 12px 0;
        box-shadow: 0 0 20px {c['border_glow']};
    }}
    /* 정답 버튼 */
    div.stButton > button[kind="primary"] {{
        font-size: 18px !important;
        height: 60px !important;
    }}
    /* 정답 표시 */
    .sq-correct {{ color: {c['neon_green']}; font-weight: 900; }}
    .sq-wrong   {{ color: {c['neon_red']};   font-weight: 900; }}
    </style>
    """

# =========================================================
# CSS 적용 헬퍼 함수
# =========================================================
def apply_global_css():
    """일반 페이지에서 사용"""
    import streamlit as st
    st.markdown(global_css(), unsafe_allow_html=True)

def apply_login_css():
    """로그인 페이지에서 사용"""
    import streamlit as st
    st.markdown(login_css(), unsafe_allow_html=True)

def apply_hub_css():
    """메인허브에서 사용"""
    import streamlit as st
    st.markdown(hub_css(), unsafe_allow_html=True)

def apply_battle_css():
    """전투 페이지에서 사용"""
    import streamlit as st
    st.markdown(battle_css(), unsafe_allow_html=True)
