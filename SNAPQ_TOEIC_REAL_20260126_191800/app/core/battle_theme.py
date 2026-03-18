import streamlit as st


def apply_battle_theme():
    """
    main_hub.py, p7/p5/armory 등 모든 페이지에서 호출되는
    전역 전투 테마 적용 함수.

    목표(이번 패치):
    - '상단 잘림' 현상 제거 (헤더 레이어 충돌 방지)
    - 여백 최소화 + 최대 폭 유지
    - 모바일에서도 문제 화면이 주인공이 되게(안전 패딩/가독성)
    - 로직(세션/타이머/채점)은 절대 불변
    """
    st.markdown(
        """
        <style>
        /* ===============================
           0) Streamlit 상단 레이어(헤더) 처리: "잘림 방지"
           - height:0 으로 누르지 말고, 레이어 충돌이 안 나게 숨김
           =============================== */

        /* Streamlit 헤더는 sticky 레이어라 height:0 만 주면 겹침(잘림) 발생 가능 */
        header[data-testid="stHeader"] {
          visibility: hidden !important;
          pointer-events: none !important;
        }

        /* 툴바/메뉴 쪽도 최소화(남아있어도 클릭 방지) */
        [data-testid="stToolbar"] {
          visibility: hidden !important;
          pointer-events: none !important;
        }

        /* 하단 푸터 제거 */
        footer { visibility: hidden !important; height: 0 !important; }

        /* 전체 페이지 바디 여백 최소화 */
        html, body { height: 100%; }
        body {
          margin: 0 !important;
          padding: 0 !important;
          overflow-x: hidden !important;
        }

        /* 메인 컨테이너: 좌우/하단은 최소,
           상단은 "안전 패딩"으로 잘림 방지 (모바일 safe-area 반영) */
        .block-container {
            padding-top: calc(0.75rem + env(safe-area-inset-top)) !important;
            padding-bottom: 0.65rem !important;
            padding-left: 0.45rem !important;
            padding-right: 0.45rem !important;
            max-width: 100% !important;
        }

        /* ===============================
           1) 전역 가독성 (기본 유지)
           =============================== */
        body, p, span, div, li { font-weight: 600; }
        .stMarkdown strong { font-weight: 800; }

        /* P7 결과 브리핑(grid) 영역 예외 처리 */
        .sq-p7-feedback p {
            width: auto !important;
            max-width: none !important;
            display: inline-block !important;
        }

        /* ===============================
           2) 사이드바 "최소화"
           =============================== */
        [data-testid="stSidebar"]{
          min-width: 220px !important;
          max-width: 220px !important;
        }

        [data-testid="stSidebar"] [data-testid="stVerticalBlock"]{
          gap: 0.35rem !important;
        }
        [data-testid="stSidebar"] .block-container{
          padding-top: 0.35rem !important;
          padding-left: 0.55rem !important;
          padding-right: 0.55rem !important;
        }

        [data-testid="stSidebar"] [data-testid="stSidebarHeader"]{
          padding-top: 0.2rem !important;
          padding-bottom: 0.2rem !important;
        }

        /* ===============================
           3) HUD 패널 공통
           =============================== */
        .sq-notice {
            background: linear-gradient(
                180deg,
                rgba(255,255,255,0.96),
                rgba(245,248,252,0.96)
            );
            color: #0F172A;

            border-style: solid;
            border-color: #2B3646;
            border-left-width: 6px;
            border-top-width: 2px;
            border-right-width: 1px;
            border-bottom-width: 1px;

            border-radius: 10px;
            padding: 0.55rem 0.75rem;
            margin: 0.2rem 0 0.45rem 0;

            position: relative;
            box-shadow: 0 3px 10px rgba(0,0,0,0.07);
        }

        /* ===============================
           4) 전장별 색상
           =============================== */
        .sq-notice-p7 { display: none !important; }
        .sq-notice.sq-notice-p7 { display: none !important; }

        .sq-notice.sq-notice-p5 {
            border-left-color: #A855F7;
            border-top-color: #A855F7;
        }

        .sq-notice.sq-notice-armory {
            border-left-color: #EF4444;
            border-top-color: #EF4444;
        }

        .sq-notice.sq-notice-report {
            border-left-color: #38BDF8;
            border-top-color: #38BDF8;
        }

        /* ===============================
           5) 텍스트 스케일: clamp로 자동 조절
           =============================== */
        [data-testid="stMarkdownContainer"] p {
            font-size: clamp(16px, 1.15vw, 20px) !important;
            line-height: 1.75 !important;
            color: #0F172A !important;
            margin-top: 0.25rem !important;
            margin-bottom: 0.25rem !important;
        }

        h3, h4 {
            font-size: clamp(18px, 1.25vw, 22px) !important;
            line-height: 1.35 !important;
            margin-top: 0.55rem !important;
            margin-bottom: 0.35rem !important;
        }

        label {
            font-size: clamp(16px, 1.15vw, 20px) !important;
            line-height: 1.6 !important;
        }

        [data-testid="stRadio"] > div {
            gap: 0.35rem !important;
        }

        hr {
          margin: 0.55rem 0 !important;
        }

        /* ===============================
           6) 모바일
           =============================== */
        @media (max-width: 768px) {
            .block-container {
                padding-top: calc(0.9rem + env(safe-area-inset-top)) !important;
                padding-left: 0.55rem !important;
                padding-right: 0.55rem !important;
            }
            [data-testid="stMarkdownContainer"] p {
                font-size: 18px !important;
            }
            h3, h4 {
                font-size: 20px !important;
            }
            label {
                font-size: 18px !important;
            }
            [data-testid="stRadio"] > div {
                gap: 0.35rem !important;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def neon_header(title: str, subtitle: str = ""):
    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)


def section_box(title: str, body_md: str):
    st.markdown(f"### {title}")
    st.markdown(body_md)
