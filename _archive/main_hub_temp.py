"""
SnapQ TOEIC V2 - Main Hub
게이미피케이션 디자인
"""

import streamlit as st
import os
from datetime import datetime

# Config
# config 제거됨

# V1 Core
from app.core.access_guard import require_access
from app.core.pretest_gate import require_pretest_gate
from app.core.attendance_engine import mark_attendance_once, has_attended_today
from app.core.battle_state import load_profile

# 페이지 설정
st.set_page_config(page_title='SnapQ TOEIC', page_icon='?', layout='centered', initial_sidebar_state='collapsed')

# CSS 로드 + 새로운 스타일
def load_all_css():
    # 기존 CSS
    css_files = ["styles/global.css", "styles/mobile.css", "styles/components.css"]
    for css_file in css_files:
        if os.path.exists(css_file):
            with open(css_file, "r", encoding="utf-8") as f:
                st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    # 메인 허브 전용 CSS
    st.markdown("""
    <style>
    /* 헤더 고정 */
    .main-header {
        background: rgba(26, 31, 46, 0.95);
        backdrop-filter: blur(10px);
        padding: 20px;
        border-radius: 0 0 16px 16px;
        margin-bottom: 20px;
        border: 1px solid rgba(0, 229, 255, 0.2);
    }
    
    .header-title {
        font-size: 20px;
        font-weight: 900;
        color: #FFFFFF;
        margin-bottom: 8px;
    }
    
    .header-subtitle {
        font-size: 14px;
        color: rgba(255, 255, 255, 0.7);
        margin-bottom: 12px;
    }
    
    .header-badges {
        display: flex;
        gap: 12px;
        flex-wrap: wrap;
    }
    
    .badge {
        padding: 6px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
        display: inline-block;
    }
    
    .badge-attend-need {
        background: #FF2D55;
        color: #FFFFFF;
    }
    
    .badge-attend-done {
        background: #10B981;
        color: #FFFFFF;
    }
    
    .badge-mission {
        background: #7C5CFF;
        color: #FFFFFF;
    }
    
    /* READY 타이틀 애니메이션 */
    .ready-title {
        text-align: center;
        padding: 40px 0;
        background: linear-gradient(135deg, #FF2D55, #7C5CFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    .ready-text {
        font-size: 48px;
        font-weight: 900;
        margin-bottom: 8px;
    }
    
    .lobby-text {
        font-size: 18px;
        color: rgba(255, 255, 255, 0.7);
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.05); }
    }
    
    /* 전장 카드 */
    .arena-card {
        height: 200px;
        border-radius: 20px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        margin: 20px 0;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .arena-card:hover {
        transform: scale(1.05);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.5);
    }
    
    .arena-card:active {
        transform: scale(0.98);
    }
    
    .arena-card-p5 {
        background: linear-gradient(135deg, #FF2D55, #FF6B35);
    }
    
    .arena-card-p7 {
        background: linear-gradient(135deg, #00E5FF, #0077FF);
    }
    
    .arena-card-armory {
        background: linear-gradient(135deg, #7C5CFF, #B794F6);
    }
    
    .arena-emoji {
        font-size: 80px;
        margin-bottom: 12px;
        animation: float 2s ease-in-out infinite;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .arena-title {
        font-size: 32px;
        font-weight: 900;
        color: #FFFFFF;
        margin-bottom: 8px;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }
    
    .arena-subtitle {
        font-size: 18px;
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 16px;
    }
    
    .arena-hint {
        font-size: 14px;
        color: rgba(255, 255, 255, 0.7);
        padding: 8px 16px;
        background: rgba(0, 0, 0, 0.2);
        border-radius: 999px;
    }
    
    /* 서브 메뉴 */
    .sub-menu {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 16px;
        margin-top: 40px;
    }
    
    .sub-card {
        height: 100px;
        background: rgba(26, 31, 46, 0.5);
        border-radius: 16px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* 모바일 최적화 */
    @media (max-width: 768px) {
        .ready-text { font-size: 42px; }
        .arena-emoji { font-size: 70px; }
        .arena-title { font-size: 28px; }
        .arena-subtitle { font-size: 16px; }
    }
    </style>
    """, unsafe_allow_html=True)

load_all_css()

# 로그인 체크
nickname = require_access()
require_pretest_gate()

# 프로필 로드
if "profile" not in st.session_state:
    st.session_state.profile = load_profile()

profile = st.session_state.profile

# 출석 체크
attended_today = has_attended_today(nickname)
if not attended_today:
    if st.button("?? 출석하기", key="attend_btn"):
        mark_attendance_once(nickname)
        st.success("출석 완료! ?? +10 XP")
        st.rerun()

# 헤더
st.markdown(f"""
<div class="main-header">
    <div class="header-title">?? {nickname}</div>
    <div class="header-subtitle">HACKERS · SnapQ TOEIC · Battle Commander</div>
    <div class="header-badges">
        <span class="badge {'badge-attend-done' if attended_today else 'badge-attend-need'}">
            {'? ATTEND · DONE' if attended_today else '?? ATTEND · NEED'}
        </span>
        <span class="badge badge-mission">?? MISSION · READY</span>
        <span class="badge" style="background: rgba(255,255,255,0.1);">
            ? XP: {profile.get('xp', 0)}
        </span>
        <span class="badge" style="background: rgba(255,255,255,0.1);">
            ?? Coin: {profile.get('coins', 0)}
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

# READY 타이틀
st.markdown("""
<div class="ready-title">
    <div class="ready-text">?? READY</div>
    <div class="lobby-text">SnapQ TOEIC · BATTLE LOBBY</div>
</div>
""", unsafe_allow_html=True)

# P5 TIMEBOMB 카드
st.markdown("""
<div class="arena-card arena-card-p5">
    <div class="arena-emoji">??</div>
    <div class="arena-title">P5 TIMEBOMB</div>
    <div class="arena-subtitle">40초 문법 전투</div>
    <div class="arena-hint">터치하여 입장</div>
</div>
""", unsafe_allow_html=True)

if st.button("", key="p5_arena", use_container_width=True, help="P5 Timebomb Arena"):
    st.session_state.phase = "lobby"
    st.session_state._p5_active = False
    st.switch_page("pages/02_P5_Timebomb_Arena.py")

# P7 READING 카드
st.markdown("""
<div class="arena-card arena-card-p7">
    <div class="arena-emoji">??</div>
    <div class="arena-title">P7 READING</div>
    <div class="arena-subtitle">60초 독해 전투</div>
    <div class="arena-hint">터치하여 입장</div>
</div>
""", unsafe_allow_html=True)

if st.button("", key="p7_arena", use_container_width=True, help="P7 Reading Arena"):
    st.switch_page("pages/01_P7_Reading_Arena.py")

# 저장고 카드
st.markdown("""
<div class="arena-card arena-card-armory">
    <div class="arena-emoji">??</div>
    <div class="arena-title">저장고</div>
    <div class="arena-subtitle">P5 학습 · VOCA 웨이브 · 콤보러시</div>
    <div class="arena-hint">터치하여 입장</div>
</div>
""", unsafe_allow_html=True)

if st.button("", key="armory", use_container_width=True, help="저장고"):
    st.session_state.sg_phase = "lobby"
    st.switch_page("pages/03_Secret_Armory_Main.py")

# 서브 메뉴 (관리자 접근)
col_stats, col_p4 = st.columns(2)

with col_stats:
    if st.button("?? STATS (관리자)", key="stats_admin", use_container_width=True):
        st.switch_page("pages/01_Admin.py")

with col_p4:
    st.button("?? P4 준비중", key="p4_soon", use_container_width=True, disabled=True)

st.stop()  # 아래 서브 메뉴 HTML은 표시 안 함
st.markdown("""
<div class="sub-menu">
    <div class="sub-card">
        <div style="font-size: 32px;">??</div>
        <div style="font-size: 16px; font-weight: 700; color: #FFFFFF;">STATS</div>
    </div>
    <div class="sub-card">
        <div style="font-size: 32px;">??</div>
        <div style="font-size: 16px; font-weight: 700; color: #FFFFFF;">P4 준비중</div>
    </div>
</div>
""", unsafe_allow_html=True)

# 푸터
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
<div style="text-align: center; padding: 20px; color: rgba(255,255,255,0.5);">
    <p style="font-size: 14px;">
        SnapQ TOEIC V2 | Made with ?? by Battle Commander 최정은
    </p>
</div>
""", unsafe_allow_html=True)








