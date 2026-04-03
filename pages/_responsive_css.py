"""
SnapQ TOEIC — 공유 반응형 CSS 모듈
적용 내용:
  1. iOS Safari 버튼 클릭 무반응 수정
  2. PC(1024px↑) 글씨·버튼 자동 확대
  3. 갤럭시/안드로이드 기존 동작 유지

사용법 (각 파일 상단):
    import sys, os
    sys.path.insert(0, os.path.dirname(__file__))
    from _responsive_css import inject_css
    inject_css()
"""
import streamlit as st

def inject_css():
    st.markdown("""
<style>
/* ══════════════════════════════════════════════════
   1. iOS Safari 버튼 클릭 무반응 수정
   - touch-action: manipulation → 더블탭 줌 방지 + 단탭 즉시 인식
   - cursor: pointer → Safari 클릭 이벤트 강제 활성화
   - -webkit-tap-highlight-color → 탭 시 깜빡임 제거
   - -webkit-appearance: none → iOS 기본 스타일 제거
══════════════════════════════════════════════════ */
button[kind="primary"],
button[kind="secondary"],
button[data-testid="stBaseButton-primary"],
button[data-testid="stBaseButton-secondary"],
div[data-testid="stButton"] > button,
div.stButton > button {
    touch-action: manipulation !important;
    cursor: pointer !important;
    -webkit-tap-highlight-color: transparent !important;
    -webkit-appearance: none !important;
    user-select: none !important;
    -webkit-user-select: none !important;
}

button[kind="primary"] p,
button[kind="secondary"] p,
button[data-testid="stBaseButton-primary"] p,
button[data-testid="stBaseButton-secondary"] p {
    touch-action: manipulation !important;
}

/* radio, selectbox 등 기타 인터랙티브 요소 */
div[data-testid="stRadio"] label,
div[data-testid="stRadio"] > div > label {
    touch-action: manipulation !important;
    cursor: pointer !important;
    -webkit-tap-highlight-color: transparent !important;
}

/* ══════════════════════════════════════════════════
   2. PC 대형 화면 (1024px 이상) — 글씨·버튼 자동 확대
   모바일 기준으로 설계된 UI를 PC에서도 읽기 좋게
══════════════════════════════════════════════════ */
@media (min-width: 1024px) {
    /* 공통 버튼 */
    button[kind="primary"],
    button[kind="secondary"],
    div.stButton > button {
        font-size: 1.15rem !important;
        padding: 0.6rem 1.2rem !important;
        min-height: 48px !important;
    }
    button[kind="primary"] p,
    button[kind="secondary"] p,
    div.stButton > button p {
        font-size: 1.15rem !important;
    }

    /* P5 전장 — 문제 텍스트 */
    .qt  { font-size: 1.25rem !important; line-height: 1.7 !important; }
    .qk  { font-size: 1.3rem !important; }
    .qc  { font-size: 0.85rem !important; }
    .bq  { font-size: 2rem !important; }
    .bs  { font-size: 1.3rem !important; }
    .ct  { font-size: 2rem !important; }
    .cd  { font-size: 1.5rem !important; }

    /* P5 브리핑 */
    .wb-s  { font-size: 1.35rem !important; line-height: 1.9 !important; }
    .wb-h,
    .wb-hn { font-size: 1.5rem !important; }
    .wb-k  { font-size: 1.2rem !important; }
    .wb-e  { font-size: 1.1rem !important; }

    /* P7 독해 */
    .p7-sent { font-size: 1.05rem !important; line-height: 1.7 !important; }
    .p7-new  { font-size: 1.05rem !important; }
    .p7-q    { font-size: 1.15rem !important; line-height: 1.9 !important; }
    .p7-hud-l { font-size: 1.5rem !important; }
    .p7-hud-r { font-size: 1.3rem !important; }

    /* P7 브리핑 */
    .p7-br-s  { font-size: 1.3rem !important; }
    .p7-br-hl { font-size: 1.4rem !important; }
    .p7-br-kr { font-size: 1.1rem !important; }
    .p7-br-ex { font-size: 1.05rem !important; }

    /* 오답전장 */
    .exam-q   { font-size: 1.2rem !important; line-height: 1.7 !important; }
    .note-sent{ font-size: 1.2rem !important; line-height: 1.7 !important; }
    .note-hl  { font-size: 1.2rem !important; }
    .note-kr  { font-size: 1.15rem !important; }
    .note-ex  { font-size: 1.1rem !important; }
    .sg-rmt-t { font-size: 1.3rem !important; }

    /* main_hub 배너·타이틀 */
    .banner-name  { font-size: 28px !important; }
    .banner-item  { font-size: 20px !important; }
    .banner-rank  { font-size: 22px !important; }
    .hub-title-text { font-size: 52px !important; }
    .hub-subtitle   { font-size: 16px !important; }
    .arena-icon-title { font-size: 30px !important; }
    .arena-rate       { font-size: 52px !important; }
    .arena-enter-btn  { font-size: 28px !important; }
    .hub-msg-title    { font-size: 1.4rem !important; }
    .hub-msg-sub      { font-size: 1.15rem !important; }
}

/* ══════════════════════════════════════════════════
   3. 초대형 화면 (1440px 이상) — 추가 확대
══════════════════════════════════════════════════ */
@media (min-width: 1440px) {
    button[kind="primary"],
    button[kind="secondary"],
    div.stButton > button {
        font-size: 1.25rem !important;
        min-height: 52px !important;
    }
    button[kind="primary"] p,
    button[kind="secondary"] p {
        font-size: 1.25rem !important;
    }
    .qt   { font-size: 1.4rem !important; }
    .p7-sent { font-size: 1.15rem !important; }
    .p7-q    { font-size: 1.25rem !important; }
    .exam-q  { font-size: 1.3rem !important; }
}
/* iOS 화력전 버튼 tap highlight 완전 제거 */
@media (hover:none) and (pointer:coarse){
    div[data-testid="stButton"] button {
        -webkit-tap-highlight-color: rgba(0,0,0,0) !important;
        -webkit-touch-callout: none !important;
        transition: none !important;
        -webkit-transition: none !important;
        animation: none !important;
        -webkit-animation: none !important;
    }
    div[data-testid="stButton"] button:active,
    div[data-testid="stButton"] button:focus {
        -webkit-tap-highlight-color: rgba(0,0,0,0) !important;
        outline: none !important;
        box-shadow: none !important;
    }
}
</style>
""", unsafe_allow_html=True)
