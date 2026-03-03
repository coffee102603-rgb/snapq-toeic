# app/core/ui_shell.py
# SnapQ TOEIC - Global UI Shell (FINAL_PALETTE_v1 + VISIBILITY_HOTFIX)
#
# ✅ 구조/로직 0 변경
# ✅ 목적: "안 보이는 글자/버튼" 문제를 전역에서 해결
#   - disabled 버튼 opacity 강제 복구 (Access/ID 화면)
#   - 기본 텍스트 대비(글자 두께/그림자) 약간 강화
#   - main_hub.py의 "흰 버튼/검정 글자"를 ui_shell이 덮지 않게 예외 처리

from __future__ import annotations
import streamlit as st


THEMES = {
    "default": {
        "accent_a": "#9B7CFF",
        "accent_b": "#3AA0FF",
        "accent_a_fog": "rgba(155,124,255,0.26)",
        "accent_b_fog": "rgba(58,160,255,0.20)",
    },
    "p5": {
        "accent_a": "#E04545",
        "accent_b": "#FF6A6A",
        "accent_a_fog": "rgba(224,69,69,0.26)",
        "accent_b_fog": "rgba(255,106,106,0.18)",
    },
    "p7": {
        "accent_a": "#3AA0FF",
        "accent_b": "#6BC8FF",
        "accent_a_fog": "rgba(58,160,255,0.24)",
        "accent_b_fog": "rgba(107,200,255,0.18)",
    },
    "armory": {
        "accent_a": "#9B7CFF",
        "accent_b": "#B59CFF",
        "accent_a_fog": "rgba(155,124,255,0.24)",
        "accent_b_fog": "rgba(181,156,255,0.18)",
    },
    "stats": {
        "accent_a": "#F5C451",
        "accent_b": "#34D399",
        "accent_a_fog": "rgba(245,196,81,0.20)",
        "accent_b_fog": "rgba(52,211,153,0.18)",
    },
    "p4": {
        "accent_a": "#94A3B8",
        "accent_b": "#CBD5E1",
        "accent_a_fog": "rgba(148,163,184,0.18)",
        "accent_b_fog": "rgba(203,213,225,0.16)",
    },
}


def apply_ui_shell(
    *,
    theme: str = "default",
    max_width_px: int = 1080,
    pad_px: int = 12,
    hide_streamlit_header: bool = True,
    hide_streamlit_footer: bool = True,
) -> None:
    t = THEMES.get(theme, THEMES["default"])
    accent_a = t["accent_a"]
    accent_b = t["accent_b"]
    accent_a_fog = t["accent_a_fog"]
    accent_b_fog = t["accent_b_fog"]

    css = f"""
    <style>
      :root {{
        --snap-accent-a: {accent_a};
        --snap-accent-b: {accent_b};
        --snap-accent-a-fog: {accent_a_fog};
        --snap-accent-b-fog: {accent_b_fog};

        --snap-bg-a: #0E1620;
        --snap-bg-b: #16212E;
        --snap-bg-c: #101821;

        --snap-text: rgba(255,255,255,.95);
        --snap-dim: rgba(255,255,255,.74);

        --snap-card: rgba(255,255,255,.075);
        --snap-card-2: rgba(255,255,255,.10);
        --snap-stroke: rgba(255,255,255,.14);
        --snap-shadow: 0 12px 34px rgba(0,0,0,.34);

        --snap-input-bg: rgba(255,255,255,.92);
        --snap-input-text: #0b0d12;
        --snap-input-placeholder: rgba(11,13,18,.55);

        /* ✅ 가독성 HOTFIX 토큰 */
        --snap-text-strong: rgba(255,255,255,.98);
        --snap-shadow-text: 0 2px 10px rgba(0,0,0,.55);
      }}

      section[data-testid="stSidebar"] {{ display:none !important; }}
      div[data-testid="collapsedControl"] {{ display:none !important; }}

      {"header[data-testid='stHeader']{display:none !important;}" if hide_streamlit_header else ""}
      {"footer{display:none !important;}" if hide_streamlit_footer else ""}

      .stApp {{
        background:
          radial-gradient(1100px 720px at 12% 8%, var(--snap-accent-a-fog), transparent 62%),
          radial-gradient(980px 680px at 88% 10%, var(--snap-accent-b-fog), transparent 62%),
          radial-gradient(900px 900px at 50% 92%, rgba(255,255,255,0.04), transparent 68%),
          linear-gradient(135deg, var(--snap-bg-a) 0%, var(--snap-bg-b) 45%, var(--snap-bg-c) 100%);
        color: var(--snap-text);
      }}

      .main .block-container {{
        max-width: {max_width_px}px !important;
        padding-top: {pad_px}px !important;
        padding-bottom: {pad_px}px !important;
        padding-left: {pad_px}px !important;
        padding-right: {pad_px}px !important;
      }}

      /* ===== Typography ===== */
      h1 {{
        font-size: clamp(1.55rem, 2.2vw, 2.6rem) !important;
        margin: 0.25rem 0 0.75rem !important;
        color: var(--snap-text-strong) !important;
        text-shadow: var(--snap-shadow-text) !important;
        font-weight: 950 !important;
      }}
      h2 {{
        font-size: clamp(1.20rem, 1.7vw, 2.0rem) !important;
        margin: 0.20rem 0 0.60rem !important;
        color: var(--snap-text-strong) !important;
        text-shadow: var(--snap-shadow-text) !important;
        font-weight: 900 !important;
      }}
      h3 {{
        font-size: clamp(1.05rem, 1.3vw, 1.55rem) !important;
        margin: 0.18rem 0 0.45rem !important;
        color: var(--snap-text-strong) !important;
        text-shadow: var(--snap-shadow-text) !important;
        font-weight: 900 !important;
      }}

      /* ✅ 기본 텍스트 대비 소폭 강화(“안 보임” 방지) */
      p, li, label, span, div {{
        color: var(--snap-text) !important;
        text-shadow: 0 1px 10px rgba(0,0,0,.35);
      }}
      .snap-dim {{ color: var(--snap-dim) !important; }}

      .snap-card {{
        background: linear-gradient(180deg, var(--snap-card), rgba(255,255,255,.03));
        border: 1px solid var(--snap-stroke);
        border-radius: 20px;
        padding: 16px 16px;
        box-shadow: var(--snap-shadow);
        backdrop-filter: blur(10px);
      }}

      .snap-pill {{
        display:inline-flex;
        align-items:center;
        gap:8px;
        padding: 8px 12px;
        border-radius: 999px;
        background: rgba(255,255,255,.07);
        border: 1px solid rgba(255,255,255,.16);
        box-shadow: 0 10px 26px rgba(0,0,0,.22);
        backdrop-filter: blur(10px);
      }}

      /* ===== Inputs ===== */
      div[data-testid="stTextInput"] input {{
        background: var(--snap-input-bg) !important;
        color: var(--snap-input-text) !important;
        border: 1px solid rgba(255,255,255,.18) !important;
        border-radius: 14px !important;
        padding: 0.70rem 0.85rem !important;
        font-weight: 850 !important;
      }}
      div[data-testid="stTextInput"] input::placeholder {{
        color: var(--snap-input-placeholder) !important;
      }}

      div[data-testid="stTextArea"] textarea {{
        background: var(--snap-input-bg) !important;
        color: var(--snap-input-text) !important;
        border: 1px solid rgba(255,255,255,.18) !important;
        border-radius: 14px !important;
        padding: 0.70rem 0.85rem !important;
      }}
      div[data-testid="stTextArea"] textarea::placeholder {{
        color: var(--snap-input-placeholder) !important;
      }}

      div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
        background: var(--snap-input-bg) !important;
        color: var(--snap-input-text) !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,.18) !important;
      }}
      div[data-testid="stSelectbox"] * {{
        color: var(--snap-input-text) !important;
      }}

      div[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {{
        background: var(--snap-input-bg) !important;
        color: var(--snap-input-text) !important;
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,.18) !important;
      }}
      div[data-testid="stMultiSelect"] * {{
        color: var(--snap-input-text) !important;
      }}

      div[data-baseweb="input"] input {{
        background: var(--snap-input-bg) !important;
        color: var(--snap-input-text) !important;
      }}

      /* ==========================================================
         ✅ 버튼 기본(전역) — 허브는 main_hub.py에서 흰버튼으로 덮음
         - 그런데 ui_shell이 다시 덮어쓰면 안 되므로,
           hub가 넣는 CSS가 "나중에" 적용되도록 ui_shell은 과도한 !important를 줄인다.
         ========================================================== */
      .stButton > button {{
        border-radius: 16px;
        padding: 0.75rem 1.05rem;
        font-weight: 900;
        border: 1px solid rgba(255,255,255,.18);
        background: linear-gradient(180deg, rgba(255,255,255,.11), rgba(255,255,255,.06));
        color: rgba(255,255,255,.96);
        box-shadow: 0 14px 34px rgba(0,0,0,.28);
        backdrop-filter: blur(10px);
      }}
      .stButton > button:hover {{
        transform: translateY(-1px);
        border-color: rgba(255,255,255,.24);
        box-shadow: 0 18px 42px rgba(0,0,0,.34);
      }}

      /* ✅✅ (핵심) Disabled button이 “안 보이는 문제” 해결 */
      div[data-testid="stButton"] > button:disabled {{
        opacity: 1 !important;
        filter: none !important;
        color: rgba(255,255,255,0.92) !important;
        background: rgba(255,255,255,0.10) !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        box-shadow: 0 10px 26px rgba(0,0,0,.22) !important;
        text-shadow: none !important;
      }}
      div[data-testid="stButton"] > button:disabled * {{
        opacity: 1 !important;
        color: rgba(255,255,255,0.92) !important;
      }}

      hr {{
        border: none;
        border-top: 1px solid rgba(255,255,255,.10);
        margin: 0.9rem 0;
      }}

      ::-webkit-scrollbar {{ width: 10px; height: 10px; }}
      ::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, var(--snap-accent-a), var(--snap-accent-b));
        border-radius: 999px;
      }}
      ::-webkit-scrollbar-track {{ background: rgba(255,255,255,.04); }}

      /* ========== MOBILE TUNING (<=768px) ========== */
      @media (max-width: 768px) {{
        .main .block-container {{
          padding-top: 10px !important;
          padding-bottom: 12px !important;
          padding-left: 10px !important;
          padding-right: 10px !important;
        }}

        h1 {{ font-size: 1.50rem !important; }}
        h2 {{ font-size: 1.18rem !important; }}
        h3 {{ font-size: 1.05rem !important; }}

        div[data-testid="stTextInput"] input,
        div[data-testid="stTextArea"] textarea {{
          padding: 0.58rem 0.75rem !important;
          border-radius: 14px !important;
          font-size: 0.98rem !important;
        }}

        .stButton > button {{
          padding: 0.58rem 0.85rem !important;
          border-radius: 14px !important;
          font-size: 0.98rem !important;
        }}

        .stApp {{
          filter: brightness(1.06) saturate(1.02);
        }}
      }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def card(title: str, body: str = "") -> None:
    st.markdown(
        f"""
        <div class="snap-card">
          <div style="font-size:1.08rem;font-weight:950;margin-bottom:6px;">{title}</div>
          <div class="snap-dim" style="line-height:1.55rem;">{body}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
