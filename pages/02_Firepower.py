"""
FILE: 02_Firepower.py  (구: 02_P5_Arena.py)
ROLE: 화력전 — 문법·어휘 5문제 서바이벌 전장
PHASES: LOBBY → BATTLE → BRIEFING → RESULT
DATA:   storage_data.json → rt_logs(논문D), adp_logs(논문A), word_prison(오답 자동 포획)
LINKS:  main_hub.py (작전사령부 귀환) | 03_POW_HQ.py (포로사령부)
PAPERS: 논문D(rt_logs 반응속도), 논문A(adp_logs 적응형 난이도)
EXTEND: P5 포로수용소 자동저장 재구현 예정 (안전한 옵션A 방식)
EXTEND: Adaptive 난이도 고도화 예정
"""
import streamlit as st
        _css = """<style data-fp>
        /* ── 전장 버튼 래퍼 여백 완전 제거 ── */
        .stMarkdown{margin:0!important;padding:0!important;}
        .element-container{margin:0!important;padding:0!important;}
        div[data-testid="stVerticalBlock"]{gap:3px!important;}
        /* ── 답 버튼 공통 ── */
        div[data-testid="stButton"] button{
            min-height:50px!important;font-size:0.95rem!important;
            font-weight:800!important;border-radius:10px!important;
            text-align:left!important;padding:0.45rem 0.9rem!important;
            margin:0!important;
        }
        div[data-testid="stButton"] button p{font-size:0.95rem!important;font-weight:800!important;}
        """
        if st.session_state.get("ans", False):
         pass
        for _aid, _col, _bg, _sh in _ans_cfg if st.session_state.get("ans", False) else []:
            _css += (
                f'.q-{_qi} #btn-{_aid} div[data-testid="stButton"] button{{' 
                f'border-left:5px solid {_col}!important;background:{_bg}!important;'
                f'border-color:{_col}!important;color:{_col}!important;'
                f'-webkit-appearance:none!important;-webkit-text-fill-color:{_col}!important;}}'
                f'#btn-{_aid}-{_qi} div[data-testid="stButton"] button p{{color:{_col}!important;}}'
                f'#btn-{_aid}-{_qi} div[data-testid="stButton"] button:hover{{box-shadow:0 0 22px {_sh}!important;}}'
            )
        _css += "</style>"
        st.markdown(_css, unsafe_allow_html=True)
