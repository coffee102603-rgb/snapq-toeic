# === P7_CUM_SENTENCES_SAFE_V3 applied at 20260203_194717 ===

# === P7_FONT20_LOCK_V1 applied at 20260203_184513 ===# ===== P7_B1_FORCE_TOPSPACE_KILL =====
try:
    import streamlit as st
    st.markdown('<div class="p7-root">', unsafe_allow_html=True)
    st.markdown(r"""
    <style>
    /* Streamlit 기본 상단 공간 제거 */
    section.main > div { padding-top: 0rem !important; }
    div.block-container { padding-top: 0rem !important; }
    header[data-testid="stHeader"] { display: none !important; }

    /* P7 전용: (주의) 너무 과하면 화면 깨질 수 있어 최소만 유지 */
    .p7-pack { margin-top: 0px !important; }
    
/* ===== P7_TEXT_FORCE_MINUS15_FINAL (PASSAGE + QUESTION ONLY) ===== */
.p7-card, .p7-card *,
.p7-zone-body, .p7-zone-body *,
.p7-q-title, .p7-q-title *,
.p7-question, .p7-question *,
.p7-qtext, .p7-qtext *{
  font-size: 0.85em !important;
  line-height: 1.45 !important;
}
/* ===== /P7_TEXT_FORCE_MINUS15_FINAL ===== */


/* ===== P7_TEXT_SHRINK_FINAL_PASSAGE_QUESTION_ONLY ===== */
/* ✅ 지문/문제 텍스트만 -15% 강제 (옵션/선택지는 건드리지 않음) */

/* (거슬리지 않게) 적용 확인용: 지문 카드에만 얇은 점선 */
.p7-card{ outline: 1px dashed rgba(255,255,255,0.20) !important; outline-offset: -6px !important; }

/* 지문/문제 영역으로 추정되는 컨테이너들만 타겟 */
.p7-card .p7-zone-body *,
.p7-card .p7-q-title *,
.p7-card .p7-question *,
.p7-card .p7-qtext *,
.p7-zone-body *,
.p7-q-title *,
.p7-question *,
.p7-qtext *,

/* Streamlit markdown 래퍼까지 강제 */
.p7-card div[data-testid="stMarkdownContainer"] *,
.p7-zone-body div[data-testid="stMarkdownContainer"] *,
.p7-q-title div[data-testid="stMarkdownContainer"] *,
.p7-question div[data-testid="stMarkdownContainer"] *,
.p7-qtext div[data-testid="stMarkdownContainer"] *,

/* 혹시 stText로 렌더링될 때까지 커버 */
.p7-card .stText *,
.p7-zone-body .stText *,
.p7-q-title .stText *,
.p7-question .stText *,
.p7-qtext .stText *{
  font-size: 19px !important;   /* 약 -15% */
  line-height: 1.45 !important;
}

/* ✅ 옵션(선택지) 영역은 원래 크기 유지: 흔한 패턴들만 보호 */
.p7-options *, .p7-option *, .p7-choice *, .p7-choices *{
  font-size: inherit !important;
}

/* ===== /P7_TEXT_SHRINK_FINAL_PASSAGE_QUESTION_ONLY ===== */

</style>
    """, unsafe_allow_html=True)
except Exception:
    pass
# ===== /P7_B1_FORCE_TOPSPACE_KILL =====# ============================================
# LOSTLOCK_PATCHED_v2: wrong answer immediately ends set (YOU LOST screen); no answer reveal
# Timebomb + Vocab Save(클릭 세이브) + Level System
# ============================================
# FINAL_PATCHED_LOST_SCREEN_V4: fail -> YOU LOST only; analysis/armory unlock only on 3/3

# === A_STRUCT_TOPHUD_PATCH_APPLIED ===
# === P7_TOPHUD_MAINHUB_INLINE_PATCH_V1 ===
# === P7_TOPHUD_MAINHUB_ONLY_PATCH_V1 ===
# === P7_TIME_RING_WRAPPER_HEART_PATCH_A1 ===
# === P7_UI_TWEAKS_A2 ===
# === P7_UI_TWEAKS_A3 ===
import time
import random
import textwrap
import json
import os
from dataclasses import dataclass, field
from typing import List, Dict

import streamlit as st

# === P7_HAS_FLAG ===
import streamlit.components.v1 as components
components.html('<div id="p7-flag" style="display:none"></div>', height=0)

P7_PATCH_V2_VER = 'P7_PATCH_V2_20260131_204309'

def inject_css():
    """
    ✅ P7 CSS STABILIZER (SAFE)
    - CRITICAL CSS: 매 rerun마다 주입 (1초 후 붕괴/흰 화면 방지)
    - Streamlit 상단 여백 최소화 (P7 전장 공간 확보)
    """
    # ---- CRITICAL CSS (ALWAYS) ----
    st.markdown(
        """
        <style>
        /* ===== P7 CRIT (ALWAYS) ===== */
        /* Streamlit 기본 상단/하단 여백 최소화 */
        .block-container { padding-top: 0.15rem !important; padding-bottom: 0.85rem !important; }
        header[data-testid="stHeader"] { display: none !important; }
        footer { display: none !important; }

        /* HUD 관련 최소 스타일(깨짐 방지) */
        .p7-hudbar { margin: 0 0 6px 0 !important; padding: 6px 10px !important; border-radius: 14px !important; }
        .p7-hud-left { display: flex !important; gap: 10px !important; align-items: center !important; flex-wrap: wrap !important; }
        .p7-hud-right { display: flex !important; justify-content: flex-end !important; align-items: center !important; }
        .p7-hud-gauge { height: 10px !important; border-radius: 999px !important; overflow: hidden !important; margin: 6px 0 10px 0 !important; }
        .p7-hud-gauge .fill { height: 100% !important; }

        /* 보기(버튼) 터치감 개선(기본 유지) */
        div[data-testid="stButton"] > button { border-radius: 12px !important; }

        
  /*  (FINAL WINNER) */
  .p7-zone .p7-zone-body{
    font-size: 30px !important;   /* 18px -> +20% 이상 */
    font-weight: 900 !important;  /* 더 굵게 */
    line-height: 1.55 !important;
    letter-spacing: 0.10px !important;
  }
  @media (max-width: 520px){
    .p7-zone .p7-zone-body{
      font-size: 26px !important; /* 모바일도 크게 */
      font-weight: 900 !important;
    }
  }
</style>
        """,
        unsafe_allow_html=True,
    )
    # ---- P7 FORCE SKIN (ALWAYS) ----
    st.markdown(
        """
        <style>
        /* P7_FORCE_SKIN_V2 (ALWAYS, LAST-WINS via !important) */

        .stApp{
          background:
            radial-gradient(900px 650px at 18% 16%, rgba(34,211,238,0.22), transparent 60%),
            radial-gradient(900px 650px at 72% 14%, rgba(167,139,250,0.18), transparent 62%),
            radial-gradient(900px 900px at 50% 78%, rgba(56,189,248,0.12), transparent 70%),
            linear-gradient(180deg, #141C2B 0%, #0E1624 55%, #0B1020 100%) !important;
          color: #E5E7EB !important;
        }

        .p7-zone{
          border-radius: 18px !important;
          padding: 16px 18px !important;
          border: 1px solid rgba(34,211,238,0.26) !important;
          background: rgba(10,16,28,0.78) !important;
          box-shadow: 0 14px 34px rgba(0,0,0,0.25) !important;
          backdrop-filter: blur(8px) !important;
          margin: 10px 0 !important;
          overflow: hidden !important;
        }
        .p7-zone:before{
          content:"" !important;
          position:absolute !important;
          left:0 !important; top:0 !important; bottom:0 !important;
          width: 6px !important;
          border-radius: 18px 0 0 18px !important;
          background: rgba(34,211,238,0.92) !important;
        }
        .p7-zone .p7-zone-body{
          color:#ffffff !important;
          font-weight: 850 !important;
          line-height: 1.65 !important;
          text-shadow: 0 2px 12px rgba(0,0,0,0.55) !important;
          font-size: 30px !important;
        }

        .p7-opt-wrap{
          display:grid !important;
          gap: 14px !important;
          margin-top: 12px !important;
        }
        .p7-opt-wrap div[data-testid="stButton"] > button{
          width: 100% !important;
          min-height: 76px !important;
          padding: 18px 18px !important;
          border-radius: 18px !important;

          font-size: 18px !important;
          font-weight: 900 !important;
          line-height: 1.20 !important;

          background: rgba(255,255,255,0.96) !important;
          color: #0F172A !important;
          border: 1px solid rgba(255,255,255,0.22) !important;
          box-shadow: 0 14px 34px rgba(0,0,0,0.22) !important;

          white-space: normal !important;
          text-align: center !important;

          transition: transform .10s ease, box-shadow .10s ease, filter .10s ease !important;
        }
        .p7-opt-wrap div[data-testid="stButton"] > button:hover{
          transform: translateY(-2px) !important;
          filter: brightness(1.04) saturate(1.06) !important;
          box-shadow: 0 18px 42px rgba(0,0,0,0.28) !important;
          background: linear-gradient(135deg, rgba(34,211,238,0.95), rgba(167,139,250,0.90)) !important;
          color:#ffffff !important;
        }
        .p7-opt-wrap div[data-testid="stButton"] > button:hover *{ color:#ffffff !important; }
        .p7-opt-wrap div[data-testid="stButton"] > button:active{
          transform: translateY(1px) scale(0.995) !important;
          box-shadow: 0 10px 22px rgba(0,0,0,0.18) !important;
        }

        /* 타이머(심장 박동 + 구간별 강화) */
        .p7-time-chip{ font-weight: 1000 !important; }
        .p7-time-chip b{ font-size: 26px !important; font-weight: 1100 !important; }

        @keyframes p7AlivePulse{
          0%{transform:scale(1); filter:brightness(1.00)}
          50%{transform:scale(1.05); filter:brightness(1.16)}
          100%{transform:scale(1); filter:brightness(1.00)}
        }
        @keyframes p7Blink{
          0%{filter:brightness(1.0)}
          50%{filter:brightness(1.55)}
          100%{filter:brightness(1.0)}
        }
        @keyframes p7Jitter{
          0%{transform:translateX(0)}
          20%{transform:translateX(-2px)}
          40%{transform:translateX(2px)}
          60%{transform:translateX(-2px)}
          80%{transform:translateX(2px)}
          100%{transform:translateX(0)}
        }

        .p7-time-alive{ animation: p7AlivePulse 1.05s ease-in-out infinite !important; }
        .p7-time-warn{
          background: rgba(255,204,0,0.18) !important;
          border-color: rgba(255,204,0,0.50) !important;
          box-shadow: 0 0 0 1px rgba(255,204,0,0.18) inset, 0 0 24px rgba(255,204,0,0.12) !important;
          animation: p7AlivePulse .85s ease-in-out infinite !important;
        }
        .p7-time-danger2{
          background: rgba(255,45,45,0.22) !important;
          border-color: rgba(255,45,45,0.60) !important;
          box-shadow: 0 0 0 1px rgba(255,45,45,0.20) inset, 0 0 34px rgba(255,45,45,0.22) !important;
          animation: p7Blink .65s infinite !important;
        }
        .p7-time-final2{
          background: rgba(255,0,0,0.26) !important;
          border-color: rgba(255,0,0,0.75) !important;
          box-shadow: 0 0 0 1px rgba(255,0,0,0.22) inset, 0 0 46px rgba(255,0,0,0.30) !important;
          animation: p7Jitter .22s linear infinite, p7Blink .33s infinite !important;
        }

        @media (max-width: 640px){
          .p7-zone .p7-zone-body{ font-size: 30px !important; }
          .p7-opt-wrap div[data-testid="stButton"] > button{
            min-height: 86px !important;
            font-size: 18px !important;
            padding: 18px 14px !important;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


    # ---- NOTE ----
    # 여기서는 '항상 주입되는 최소 CSS'만 둡니다.
    # 기존의 거대한 테마 CSS는 다른 함수/블록에서 이미 처리되어도 되고,
    # 없더라도 최소한 UI가 "1초 후 붕괴"하지 않게 하는 것이 목적입니다.


    # ---- P7 SAFE UI PACK V1 ----
    st.markdown(
        r"""
        <style>
        /* P7_SAFE_UI_PACK_V1 */

        /* (1) 선택지 글자: 흰 버튼이면 검정 글자 */
        .p7-opt-wrap div[data-testid="stButton"] > button,
        .p7-opt-wrap div[data-testid="stButton"] > button *{
          color: #111827 !important;
        }
        /* hover 시에는 흰 글자(락온) */
        .p7-opt-wrap div[data-testid="stButton"] > button:hover,
        .p7-opt-wrap div[data-testid="stButton"] > button:hover *{
          color:#ffffff !important;
        }

        /* (2) 글자 크기 1.2배 */
        .p7-zone .p7-zone-body{ font-size: 30px !important; }
        .p7-zone.mission .p7-zone-body{ font-size: 23px !important; }
        .p7-opt-wrap div[data-testid="stButton"] > button{
          font-size: 21px !important;
          font-weight: 950 !important;
        }
        @media (max-width: 640px){
          .p7-zone .p7-zone-body{ font-size: 26px !important; }
          .p7-zone.mission .p7-zone-body{ font-size: 26px !important; }
          .p7-opt-wrap div[data-testid="stButton"] > button{ font-size: 26px !important; }
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


    # ---- P7 SAFE UI PACK V2 ----
    st.markdown(
        r"""
        <style>
        /* P7_SAFE_UI_PACK_V2 */

        /* (A) 선택지: 흰 버튼이면 글자는 검정 (가독성) */
        .p7-opt-wrap div[data-testid="stButton"] > button{
          color:#111827 !important;
          font-size: 30px !important;   /* 1.2배 업 */
          font-weight: 950 !important;
        }
        .p7-opt-wrap div[data-testid="stButton"] > button *{
          color:#111827 !important;
        }

        /* hover(락온)에서는 흰 글자 유지 */
        .p7-opt-wrap div[data-testid="stButton"] > button:hover,
        .p7-opt-wrap div[data-testid="stButton"] > button:hover *{
          color:#ffffff !important;
        }

        /* (A-2) 모바일에서도 크게 */
        @media (max-width: 640px){
          .p7-opt-wrap div[data-testid="stButton"] > button{
            font-size: 21px !important;
            min-height: 92px !important;
          }
        }

        /* (B) 게이지(막대) 연출: 30초 단계 + 마지막 60/30/10 */
        @keyframes p7_gauge_wiggle {
          0%{ transform:translateX(0); }
          25%{ transform:translateX(-2px); }
          50%{ transform:translateX(0); }
          75%{ transform:translateX(2px); }
          100%{ transform:translateX(0); }
        }
        @keyframes p7_gauge_shake {
          0%{ transform:translateX(0); }
          20%{ transform:translateX(-4px); }
          40%{ transform:translateX(4px); }
          60%{ transform:translateX(-3px); }
          80%{ transform:translateX(3px); }
          100%{ transform:translateX(0); }
        }
        @keyframes p7_gauge_flash {
          0%{ filter:brightness(1.0); }
          50%{ filter:brightness(1.55); }
          100%{ filter:brightness(1.0); }
        }

        /* 30초마다 색 변화 (stage 0~5) */
        .p7-hud-gauge.stage5 .fill{ background: linear-gradient(90deg, rgba(34,211,238,0.95), rgba(124,58,237,0.95)) !important; }
        .p7-hud-gauge.stage4 .fill{ background: linear-gradient(90deg, rgba(56,189,248,0.95), rgba(167,139,250,0.95)) !important; }
        .p7-hud-gauge.stage3 .fill{ background: linear-gradient(90deg, rgba(45,212,191,0.95), rgba(34,211,238,0.95)) !important; }
        .p7-hud-gauge.stage2 .fill{ background: linear-gradient(90deg, rgba(250,204,21,0.95), rgba(34,211,238,0.95)) !important; }
        .p7-hud-gauge.stage1 .fill{ background: linear-gradient(90deg, rgba(251,146,60,0.95), rgba(250,204,21,0.95)) !important; }
        .p7-hud-gauge.stage0 .fill{ background: linear-gradient(90deg, rgba(239,68,68,0.98), rgba(220,38,38,0.98)) !important; }

        /* 마지막 60초: 요동 시작 */
        .p7-hud-gauge.last60{
          animation: p7_gauge_wiggle 0.9s linear infinite;
        }

        /* 마지막 30초: 빨간색 + 흔들 + 번쩍 */
        .p7-hud-gauge.last30{
          animation: p7_gauge_shake 0.35s linear infinite, p7_gauge_flash 0.55s ease-in-out infinite;
          border-color: rgba(239,68,68,0.55) !important;
          box-shadow: 0 0 26px rgba(239,68,68,0.18) !important;
        }

        /* 마지막 10초: 더 강하게 */
        .p7-hud-gauge.final{
          animation: p7_gauge_shake 0.24s linear infinite, p7_gauge_flash 0.35s ease-in-out infinite;
          box-shadow: 0 0 40px rgba(239,68,68,0.25) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


    # ---- P7_HUD_GAUGE_OPTIONS_CSS_V1 ----
    st.markdown(
        r"""
        <style>
        /* P7_HUD_GAUGE_OPTIONS_CSS_V1 */

        /* (1) 선택지 1.1배 + 더 굵게 */
        .p7-opt-wrap div[data-testid="stButton"] > button{
          font-size: 26px !important;   /* 기존보다 1.1배 */
          font-weight: 950 !important;
        }

        /* (선택지 글자색은 이미 검정 패치가 있을 수 있어 유지) */
        .p7-opt-wrap div[data-testid="stButton"] > button,
        .p7-opt-wrap div[data-testid="stButton"] > button *{
          color:#0B1020 !important;
          opacity:1 !important;
          text-shadow:none !important;
        }
        .p7-opt-wrap div[data-testid="stButton"] > button:hover,
        .p7-opt-wrap div[data-testid="stButton"] > button:hover *{
          color:#ffffff !important;
        }

        /* (2) 게이지: 30초 단계색 + last60 wiggle + last30 red shake + final stronger */
        @keyframes p7_gauge_wiggle{
          0%{transform:translateX(0)}25%{transform:translateX(-2px)}50%{transform:translateX(0)}75%{transform:translateX(2px)}100%{transform:translateX(0)}
        }
        @keyframes p7_gauge_shake{
          0%{transform:translateX(0)}20%{transform:translateX(-4px)}40%{transform:translateX(4px)}60%{transform:translateX(-3px)}80%{transform:translateX(3px)}100%{transform:translateX(0)}
        }
        @keyframes p7_gauge_flash{
          0%{filter:brightness(1.0)}50%{filter:brightness(1.55)}100%{filter:brightness(1.0)}
        }

        .p7-hud-gauge.stage5 .fill{ background:linear-gradient(90deg, rgba(34,211,238,.95), rgba(124,58,237,.95)) !important; }
        .p7-hud-gauge.stage4 .fill{ background:linear-gradient(90deg, rgba(56,189,248,.95), rgba(167,139,250,.95)) !important; }
        .p7-hud-gauge.stage3 .fill{ background:linear-gradient(90deg, rgba(45,212,191,.95), rgba(34,211,238,.95)) !important; }
        .p7-hud-gauge.stage2 .fill{ background:linear-gradient(90deg, rgba(250,204,21,.95), rgba(34,211,238,.95)) !important; }
        .p7-hud-gauge.stage1 .fill{ background:linear-gradient(90deg, rgba(251,146,60,.95), rgba(250,204,21,.95)) !important; }
        .p7-hud-gauge.stage0 .fill{ background:linear-gradient(90deg, rgba(239,68,68,.98), rgba(220,38,38,.98)) !important; }

        .p7-hud-gauge.last60{ animation:p7_gauge_wiggle .9s linear infinite; }
        .p7-hud-gauge.last30{
          animation:p7_gauge_shake .35s linear infinite, p7_gauge_flash .55s ease-in-out infinite;
          border-color: rgba(239,68,68,.55) !important;
          box-shadow: 0 0 26px rgba(239,68,68,.18) !important;
        }
        .p7-hud-gauge.final{
          animation:p7_gauge_shake .24s linear infinite, p7_gauge_flash .35s ease-in-out infinite;
          box-shadow: 0 0 40px rgba(239,68,68,.25) !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


    # ---- P7_UI_TUNE_V1 (CSS ONLY) ----
    st.markdown(
        r"""
        <style>
        /* P7_UI_TUNE_V1 */

        /* (3) 상단 공간 더 위로: 전장 HUD/게이지를 위로 당김 */
        .block-container{ padding-top: 0.10rem !important; padding-bottom: 0.85rem !important; }
        /* HUD/게이지 마진을 조금 줄여 본문이 위로 올라오게 */
        .p7-hud-left{ margin-top: -6px !important; }
        .p7-hud-gauge{ margin-top: -4px !important; margin-bottom: 8px !important; }

        /* (1) 선택지: 더 크고(1.1배) 더 진하게, 검정으로, 흐림 제거 */
        /* 버튼 자체 + 내부 모든 텍스트를 강제 */
        .p7-opt-wrap div[data-testid="stButton"] > button{
          font-size: 30px !important;         /* 기존 20~21에서 +1.1배 느낌 */
          font-weight: 1000 !important;
          color:#0B1020 !important;
          opacity: 1 !important;
          text-shadow:none !important;
        }
        .p7-opt-wrap div[data-testid="stButton"] > button *{
          font-size: 30px !important;
          font-weight: 1000 !important;
          color:#0B1020 !important;
          opacity: 1 !important;
          text-shadow:none !important;
        }

        /* hover(락온) 시에는 흰 글자 유지(게임 느낌) */
        .p7-opt-wrap div[data-testid="stButton"] > button:hover,
        .p7-opt-wrap div[data-testid="stButton"] > button:hover *{
          color:#ffffff !important;
        }

        /* 모바일은 약간만 다운 */
        @media (max-width: 640px){
          .p7-opt-wrap div[data-testid="stButton"] > button,
          .p7-opt-wrap div[data-testid="stButton"] > button *{
            font-size: 26px !important;
          }
        }

        /* (2) 게이지 30초마다 색 변화가 “눈에 띄게”:
           fill 뿐 아니라 border/글로우도 stage별로 강하게 */
        .p7-hud-gauge{ border-width: 1px !important; }

        .p7-hud-gauge.stage5{ border-color: rgba(34,211,238,0.35) !important; box-shadow: 0 0 18px rgba(34,211,238,0.12) !important; }
        .p7-hud-gauge.stage4{ border-color: rgba(56,189,248,0.35) !important; box-shadow: 0 0 18px rgba(56,189,248,0.12) !important; }
        .p7-hud-gauge.stage3{ border-color: rgba(45,212,191,0.35) !important; box-shadow: 0 0 18px rgba(45,212,191,0.12) !important; }
        .p7-hud-gauge.stage2{ border-color: rgba(250,204,21,0.40) !important; box-shadow: 0 0 18px rgba(250,204,21,0.14) !important; }
        .p7-hud-gauge.stage1{ border-color: rgba(251,146,60,0.45) !important; box-shadow: 0 0 22px rgba(251,146,60,0.16) !important; }
        .p7-hud-gauge.stage0{ border-color: rgba(239,68,68,0.55) !important; box-shadow: 0 0 26px rgba(239,68,68,0.20) !important; }

        /* last60/last30/final은 이미 흔들림이 동작하니 그대로 두고,
           “색 변화가 더 티나게”만 강화함 */

        </style>
        """,
        unsafe_allow_html=True,
    )


    # ---- P7 TOP SPACE KILL V1 (CSS ONLY) ----
    st.markdown(
        r"""
        <style>
        /* P7_TOP_SPACE_KILL_V1 */

        /* Streamlit 상단 빈공간 제거 (헤더/툴바 영향 최소화) */
        header[data-testid="stHeader"] { display: none !important; }
        footer { display: none !important; }

        /* 메인 컨테이너 패딩 최소 */
        .block-container{
          padding-top: 0rem !important;
          padding-bottom: 0.7rem !important;
        }

        /* 첫 블록(세로 블록) 위쪽 마진 제거 */
        .block-container > div:first-child{
          margin-top: 0rem !important;
          padding-top: 0rem !important;
        }

        /* HUD 줄을 위로 당김 (과하지 않게 -8px) */
        .p7-hud-left{
          margin-top: -8px !important;
        }

        /* 게이지도 위로 살짝 당김 */
        .p7-hud-gauge{
          margin-top: -8px !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )


    # ---- P7_TOP_SPACE_KILL_V2 (CSS ONLY) ----
    st.markdown(
        r"""
        <style>
        /* P7_TOP_SPACE_KILL_V2 */

        /* ✅ Streamlit 상단 여백/헤더/메인 패딩을 “강제 0” */
        header[data-testid="stHeader"]{ display:none !important; }
        footer{ display:none !important; }

        /* 최상위 컨테이너들에 강제 패딩 0 */
        div[data-testid="stAppViewContainer"] > section > div,
        div[data-testid="stAppViewContainer"] > section > main,
        div[data-testid="stAppViewContainer"] > section > main > div{
          padding-top: 0rem !important;
          margin-top: 0rem !important;
        }

        /* block-container (메인) */
        .block-container{
          padding-top: 0rem !important;
          padding-bottom: 0.7rem !important;
          margin-top: 0rem !important;
        }

        /* 첫 VerticalBlock/HorizontalBlock 위 마진 제거 */
        div[data-testid="stVerticalBlock"]{ margin-top:0 !important; padding-top:0 !important; }
        div[data-testid="stHorizontalBlock"]{ margin-top:0 !important; }

        /* HUD/게이지를 살짝 위로 당김 (최대 안전치) */
        .p7-hud-left{ margin-top:-12px !important; }
        .p7-hud-gauge{ margin-top:-10px !important; margin-bottom:8px !important; }

        </style>
        """,
        unsafe_allow_html=True,
    )


    # ---- P7_FINAL_UI_FORCE_V1 ----
    st.markdown(
        r"""
        <style>
        /* === P7_FINAL_UI_FORCE_V1 === */

        /* 1️⃣ 상단 빈 공간 제거 */
        header[data-testid="stHeader"]{ display:none !important; }
        .block-container{
          padding-top:0.2rem !important;
          margin-top:0 !important;
        }
        div[data-testid="stVerticalBlock"]{
          margin-top:0 !important;
          padding-top:0 !important;
        }

        /* HUD / 게이지 위로 당김 */
        .p7-hud-left{ margin-top:-16px !important; }
        .p7-hud-gauge{ margin-top:-14px !important; margin-bottom:10px !important; }

        /* 2️⃣ 선택지 글자: 1.1배 + 검정 + 진하게 */
        .p7-opt-wrap div[data-testid="stButton"] > button{
          font-size:1.1em !important;
          font-weight:900 !important;
          color:#000000 !important;
        }
        .p7-opt-wrap div[data-testid="stButton"] > button *{
          color:#000000 !important;
        }

        /* 3️⃣ 타이머 게이지 30초 단계 색 */
        .p7-hud-gauge.stage3 .fill{ background:#22d3ee !important; } /* 90~60 */
        .p7-hud-gauge.stage2 .fill{ background:#38bdf8 !important; } /* 60~30 */
        .p7-hud-gauge.stage1 .fill{ background:#facc15 !important; } /* 30~10 */
        .p7-hud-gauge.stage0 .fill{ background:#ef4444 !important; } /* last */

        

/* === P7_TEXT_FORCE_X12 (TEXT ONLY) === */
.p7-zone .p7-zone-body,
.p7-zone .p7-zone-body *{
  font-size: 30px !important;   /* 기존 18px 기준 +20% */
  font-weight: 800 !important;
}
.p7-zone .p7-zone-q,
.p7-zone .p7-zone-q *{
  font-size: 30px !important;
  font-weight: 800 !important;
}

/* 선택지(라디오) 텍스트 강제: Streamlit DOM 대응 */
div[data-testid="stRadio"] label,
div[role="radiogroup"] > label{
  font-weight: 800 !important;
}
div[data-testid="stRadio"] label p,
div[data-testid="stRadio"] label span,
div[data-testid="stRadio"] label strong,
div[role="radiogroup"] > label p,
div[role="radiogroup"] > label span,
div[role="radiogroup"] > label strong,
div[data-testid="stRadio"] label [data-testid="stMarkdownContainer"] p,
div[role="radiogroup"] > label [data-testid="stMarkdownContainer"] p{
  font-size: 19px !important;   /* 기본 16px 기준 +20% */
  font-weight: 800 !important;
}
/* === /P7_TEXT_FORCE_X12 === */

</style>
        """,
        unsafe_allow_html=True,
    )


    # ---- P7 TOP SPACE FINAL V1 (MAX SAVE) ----
    st.markdown(
        r"""
        <style>
        /* P7_TOP_SPACE_FINAL_V1 */

        /* ✅ 최대한 위로 당김 (HUD+게이지) */
        .p7-hud-left{ margin-top:-22px !important; }
        .p7-hud-gauge{ margin-top:-22px !important; margin-bottom:8px !important; }

        /* 혹시 다른 래퍼가 있으면 같이 당김 */
        div[data-testid="stHorizontalBlock"]{ margin-top:0 !important; }
        div[data-testid="stVerticalBlock"]{ margin-top:0 !important; padding-top:0 !important; }

        </style>
        """,
        unsafe_allow_html=True,
    )


    # ---- P7_SAFE_FINAL_PACK_V1 ----
    st.markdown(
        r"""
        <style>
        /* P7_SAFE_FINAL_PACK_V1 */

        /* (1) TOP SPACE: 두번째 캡쳐 상단 공간 압축 */
        header[data-testid="stHeader"]{ display:none !important; }
        footer{ display:none !important; }

        div[data-testid="stAppViewContainer"] > section > main,
        div[data-testid="stAppViewContainer"] > section > main > div,
        div[data-testid="stAppViewContainer"] > section > div{
          padding-top: 0rem !important;
          margin-top: 0rem !important;
        }
        .block-container{
          padding-top: 0.05rem !important;
          margin-top: 0 !important;
          padding-bottom: 0.8rem !important;
        }
        /* HUD+게이지를 더 위로 (과하지 않게) */
        .p7-hud-left{ margin-top:-18px !important; }
        .p7-hud-gauge{ margin-top:-16px !important; margin-bottom:10px !important; }

        /* (2) OPTIONS: 첫번째 캡쳐 기준 선택지 글자 1.1배 + 검정 + 더 진하게 + 흐림 제거 */
        .p7-opt-wrap div[data-testid="stButton"] > button{
          font-size: 30px !important;
          font-weight: 1000 !important;
          color:#000 !important;
          opacity:1 !important;
          text-shadow:none !important;
        }
        .p7-opt-wrap div[data-testid="stButton"] > button *{
          font-size: 30px !important;
          font-weight: 1000 !important;
          color:#000 !important;
          opacity:1 !important;
          text-shadow:none !important;
        }
        /* hover(락온)은 흰 글자 유지 */
        .p7-opt-wrap div[data-testid="stButton"] > button:hover,
        .p7-opt-wrap div[data-testid="stButton"] > button:hover *{
          color:#ffffff !important;
        }

        @media (max-width: 640px){
          .p7-opt-wrap div[data-testid="stButton"] > button,
          .p7-opt-wrap div[data-testid="stButton"] > button *{
            font-size: 26px !important;
          }
        }

        /* (3) GAUGE: 30초마다 색 변화 + last60/last30/final 흔들/빨강은 유지 */
        @keyframes p7_gauge_wiggle{
          0%{transform:translateX(0)}25%{transform:translateX(-2px)}50%{transform:translateX(0)}75%{transform:translateX(2px)}100%{transform:translateX(0)}
        }
        @keyframes p7_gauge_shake{
          0%{transform:translateX(0)}20%{transform:translateX(-4px)}40%{transform:translateX(4px)}60%{transform:translateX(-3px)}80%{transform:translateX(3px)}100%{transform:translateX(0)}
        }
        @keyframes p7_gauge_flash{
          0%{filter:brightness(1.0)}50%{filter:brightness(1.55)}100%{filter:brightness(1.0)}
        }

        /* stage5~0: 30초 단위 */
        .p7-hud-gauge.stage5 .fill{ background:linear-gradient(90deg, rgba(34,211,238,.95), rgba(124,58,237,.95)) !important; }
        .p7-hud-gauge.stage4 .fill{ background:linear-gradient(90deg, rgba(56,189,248,.95), rgba(167,139,250,.95)) !important; }
        .p7-hud-gauge.stage3 .fill{ background:linear-gradient(90deg, rgba(45,212,191,.95), rgba(34,211,238,.95)) !important; }
        .p7-hud-gauge.stage2 .fill{ background:linear-gradient(90deg, rgba(250,204,21,.95), rgba(34,211,238,.95)) !important; }
        .p7-hud-gauge.stage1 .fill{ background:linear-gradient(90deg, rgba(251,146,60,.95), rgba(250,204,21,.95)) !important; }
        .p7-hud-gauge.stage0 .fill{ background:linear-gradient(90deg, rgba(239,68,68,.98), rgba(220,38,38,.98)) !important; }

        .p7-hud-gauge.last60{ animation:p7_gauge_wiggle .9s linear infinite; }
        .p7-hud-gauge.last30{
          animation:p7_gauge_shake .35s linear infinite, p7_gauge_flash .55s ease-in-out infinite;
          border-color: rgba(239,68,68,.55) !important;
          box-shadow: 0 0 26px rgba(239,68,68,.18) !important;
        }
        .p7-hud-gauge.final{
          animation:p7_gauge_shake .24s linear infinite, p7_gauge_flash .35s ease-in-out infinite;
          box-shadow: 0 0 40px rgba(239,68,68,.25) !important;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )

    # ---- P7_DENSITY_FINAL_V2 (AUTO, LAST WINS) ----
    st.markdown(r"""
    <style>
    /* === P7_DENSITY_FINAL_V2 === */

    /* (1) 좌/우/상/하 빈 공간 최소화: 화면 꽉 채우기 */
    .block-container{
      max-width: 100% !important;
      padding-left: 0.22rem !important;
      padding-right: 0.22rem !important;
      padding-top: 0.02rem !important;
      padding-bottom: 0.30rem !important;
      margin-top: 0 !important;
    }

    /* (2) 지문/문제 카드 위아래 여백 압축 */
    .p7-zone{
      margin: 6px 0 !important;
      padding: 12px 12px !important;
      border-radius: 16px !important;
    }
    .p7-zone:before{ width: 6px !important; }

    /* (3) 선택지 영역: 간격 더 타이트 */
    .p7-opt-wrap{
      gap: 8px !important;
      margin-top: 8px !important;
    }

    /* (4) 선택지 글씨: 1.1배 + 굵게 + 진한 검정 */
    .p7-opt-wrap button,
    .p7-opt-wrap button *{
      font-size: 1.32em !important;
      font-weight: 900 !important;
      color: #000000 !important;
      opacity: 1 !important;
      text-shadow: none !important;
    }

    /* (5) TIME 단계별 드라마 */
    @keyframes p7TimePulse{0%{filter:brightness(1)}50%{filter:brightness(1.18)}100%{filter:brightness(1)}}
    .p7-time-alive{animation:p7TimePulse 1.2s ease-in-out infinite !important;}

    @keyframes p7TimeWarn{0%{filter:brightness(1)}50%{filter:brightness(1.30)}100%{filter:brightness(1)}}
    .p7-time-warn{
      border-color: rgba(255,210,80,.45) !important;
      box-shadow: 0 0 18px rgba(255,210,80,.12) !important;
      animation: p7TimeWarn .95s ease-in-out infinite !important;
    }

    @keyframes p7TimeDanger2{0%{filter:brightness(1)}50%{filter:brightness(1.55)}100%{filter:brightness(1)}}
    .p7-time-danger2{
      border-color: rgba(255,110,110,.60) !important;
      box-shadow: 0 0 22px rgba(255,110,110,.16) !important;
      animation: p7TimeDanger2 .75s ease-in-out infinite !important;
    }

    @keyframes p7TimeFinal2{0%{transform:translateY(0)}50%{transform:translateY(-1px)}100%{transform:translateY(0)}}
    .p7-time-final2{
      border-color: rgba(255,60,60,.75) !important;
      box-shadow: 0 0 26px rgba(255,60,60,.22) !important;
      animation: p7TimeFinal2 .35s ease-in-out infinite !important;
    }

    /* (6) MISS: 1 이상이면 흔들림 */
    @keyframes p7MissShake{0%{transform:translateX(0)}20%{transform:translateX(-2px)}40%{transform:translateX(2px)}60%{transform:translateX(-2px)}80%{transform:translateX(2px)}100%{transform:translateX(0)}}
    .p7-miss-warn{
      border-color: rgba(255,80,80,0.55) !important;
      box-shadow: 0 0 18px rgba(255,80,80,0.14) !important;
      animation: p7MissShake .35s ease-in-out 1 !important;
    }

    /* (7) COMBO: 1 이상이면 glow */
    @keyframes p7ComboGlow{0%{filter:brightness(1.00)}50%{filter:brightness(1.18)}100%{filter:brightness(1.00)}}
    .p7-combo-live{
      border-color: rgba(160,120,255,0.55) !important;
      box-shadow: 0 0 22px rgba(160,120,255,0.14) !important;
      animation: p7ComboGlow 1.05s ease-in-out infinite !important;
    }

    </style>
    """, unsafe_allow_html=True)
    # ---- /P7_DENSITY_FINAL_V2 ----


    # ---- P7_FORCE_TOP_OPTIONS_V1 (AUTO, LAST WINS) ----
    try:
        st.markdown(r"""
        <style>
        /* === P7_FORCE_TOP_OPTIONS_V1 === */

        /* 1) 위 공간(상단) 최대 압축 */
        header[data-testid="stHeader"]{ display:none !important; height:0 !important; }
        div[data-testid="stAppViewContainer"] > .main{ padding-top:0 !important; margin-top:0 !important; }
        section.main > div{ padding-top:0 !important; margin-top:0 !important; }
        .block-container{
          max-width: 100% !important;
          padding-top: 0.00rem !important;
          padding-bottom: 0.25rem !important;
          padding-left: 0.22rem !important;
          padding-right: 0.22rem !important;
          margin-top: 0 !important;
        }

        /* HUD 자체도 조금 더 얇게 (내용을 위로) */
        .p7-hudbar{ margin:0 0 2px 0 !important; padding:4px 8px !important; }
        .p7-hud-gauge{ margin:3px 0 6px 0 !important; height:10px !important; }

        /* 카드들 위로 더 당기기 */
        .p7-zone{ margin:6px 0 !important; padding:12px 12px !important; }
        .p7-opt-wrap{ gap:8px !important; margin-top:8px !important; }

        /* 2) 선택지 글씨 강제: 1.1배 + 초굵게 + 진한 검정 + 흐림 방지 */
        .p7-opt-wrap div[data-testid="stButton"] > button,
        .p7-opt-wrap div[data-testid="stButton"] > button * {
          font-size: 1.32em !important;
          font-weight: 950 !important;
          color: #000000 !important;
          opacity: 1 !important;
          filter: none !important;
          text-shadow: none !important;
          -webkit-text-fill-color: #000000 !important;
        }
        .p7-opt-wrap div[data-testid="stButton"] > button:disabled,
        .p7-opt-wrap div[data-testid="stButton"] > button:disabled * {
          color: #000000 !important;
          opacity: 1 !important;
          filter: none !important;
          -webkit-text-fill-color: #000000 !important;
        }

        /* 3) 적용 확인 배지 (안 뜨면 inject_css()가 호출 안 됨) */
        .p7-force-badge {
          position: fixed;
          right: 12px;
          bottom: 12px;
          z-index: 999999;
          padding: 10px 12px;
          border-radius: 14px;
          background: rgba(255,255,255,0.92);
          border: 3px solid rgba(0,255,170,0.70);
          color: #111827;
          font-weight: 900;
          font-size: 12px;
          line-height: 1.15;
          box-shadow: 0 14px 30px rgba(0,0,0,0.25);
        }
        .p7-force-badge b { color: #00b894; }

        </style>

        """, unsafe_allow_html=True)
    except Exception:
        pass
    # ---- /P7_FORCE_TOP_OPTIONS_V1 ----



    # ---- P7_FORCE_GAP_BLACK_V2 (AUTO, LAST WINS) ----
    try:
        st.markdown(r"""
        <style>
        /* === P7_FORCE_GAP_BLACK_V2 === */

        /* A) 위 공간(=HUD 아래 큰 gap) 원인: Streamlit 블록/마크다운 기본 마진 */
        /* element-container / markdown / columns 사이 간격을 강제로 압축 */
        div[data-testid="stVerticalBlock"] > div,
        div[data-testid="stHorizontalBlock"] > div,
        div.element-container,
        div.stMarkdown,
        div.stMarkdownContainer {
          margin-top: 0 !important;
          margin-bottom: 0 !important;
          padding-top: 0 !important;
          padding-bottom: 0 !important;
        }

        /* HUD + 게이지 + 전장 시작을 위로 붙임 */
        .p7-hud-left{ margin: 0 !important; padding: 0 !important; }
        .p7-hud-gauge{ margin: 2px 0 4px 0 !important; }
        .p7-battlefield{ margin-top: 0 !important; padding-top: 0 !important; }
        .p7-zone{ margin-top: 6px !important; }

        /* B) 선택지 텍스트가 회색처럼 보이는 진짜 원인: disabled 시 wrapper opacity */
        /* stButton wrapper 자체를 1로 고정 */
        .p7-opt-wrap div[data-testid="stButton"] {
          opacity: 1 !important;
          filter: none !important;
        }

        /* 버튼 & 내부 텍스트 강제: 1.1배 + 초굵게 + #000 + 흐림 금지 */
        .p7-opt-wrap div[data-testid="stButton"] > button,
        .p7-opt-wrap div[data-testid="stButton"] > button * {
          font-size: 1.32em !important;
          font-weight: 950 !important;
          color: #000000 !important;
          opacity: 1 !important;
          filter: none !important;
          text-shadow: none !important;
          -webkit-text-fill-color: #000000 !important;
        }

        /* disabled 상태에서도 동일(Streamlit default override 차단) */
        .p7-opt-wrap div[data-testid="stButton"] > button:disabled,
        .p7-opt-wrap div[data-testid="stButton"] > button:disabled * {
          opacity: 1 !important;
          color: #000000 !important;
          filter: none !important;
          -webkit-text-fill-color: #000000 !important;
        }

        </style>
        """, unsafe_allow_html=True)
    except Exception:
        pass
    # ---- /P7_FORCE_GAP_BLACK_V2 ----
    # ---- P7_HARD_FORCE_V1 (AUTO, LAST WINS) ----
    try:
        st.markdown(r"""
        <style>
        /* === P7_HARD_FORCE_V1 === */

        /* TOP SPACE: pull everything up */
        .p7-viewport-shift {
          position: relative;
          top: -28px;
        }

        /* OPTIONS: style ALL buttons inside battlefield (disabled 포함) */
        .p7-battlefield div[data-testid="stButton"] {
          opacity: 1 !important;
          filter: none !important;
        }

        .p7-battlefield div[data-testid="stButton"] > button,
        .p7-battlefield div[data-testid="stButton"] > button * {
          font-size: 1.32em !important;
          font-weight: 950 !important;
          color: #000000 !important;
          opacity: 1 !important;
          filter: none !important;
          text-shadow: none !important;
          -webkit-text-fill-color: #000000 !important;
        }

        .p7-battlefield div[data-testid="stButton"] > button:disabled,
        .p7-battlefield div[data-testid="stButton"] > button:disabled * {
          opacity: 1 !important;
          color: #000000 !important;
          -webkit-text-fill-color: #000000 !important;
        }

        </style>

        
        """, unsafe_allow_html=True)
    except Exception:
        pass
    # DISABLED_BY_VIEWPORT_LOCK[P7_HARD_FORCE_V1] # ---- /P7_HARD_FORCE_V1 ----




    try:
        st.markdown(r"""
        <style>

        /* (A) TOP SPACE: wrapper를 위로 당김 (값 조절 가능) */
        .p7-viewport-shift {
          position: relative;
          top: -70px;   /* ← 더 위로: -90 / 덜 위로: -50 */
        }

        /* (B) OPTIONS: 전장(.p7-battlefield) 안 모든 버튼 텍스트를 강제 */
        .p7-battlefield div[data-testid="stButton"] {
          opacity: 1 !important;
          filter: none !important;
        }
        .p7-battlefield div[data-testid="stButton"] > button {
          font-size: 1.32em !important;
          font-weight: 950 !important;
          color: #000000 !important;
          opacity: 1 !important;
          -webkit-text-fill-color: #000000 !important;
        }
        /* Streamlit 내부 span/p까지 박살내기(disabled 회색 깨기) */
        .p7-battlefield div[data-testid="stButton"] > button span,
        .p7-battlefield div[data-testid="stButton"] > button p,
        .p7-battlefield div[data-testid="stButton"] > button div,
        .p7-battlefield div[data-testid="stButton"] > button * {
          font-size: 1.32em !important;
          font-weight: 950 !important;
          color: #000000 !important;
          opacity: 1 !important;
          filter: none !important;
          text-shadow: none !important;
          -webkit-text-fill-color: #000000 !important;
        }
        .p7-battlefield div[data-testid="stButton"] > button:disabled,
        .p7-battlefield div[data-testid="stButton"] > button:disabled * {
          opacity: 1 !important;
          color: #000000 !important;
          -webkit-text-fill-color: #000000 !important;
        }

        </style>

        
        """, unsafe_allow_html=True)
    except Exception:
        pass


    try:
        st.markdown("""
        <style>

        /* 1) 위 공간(블록 간 간격) 강제 압축 */
        div[data-testid="stVerticalBlock"] > div,
        div[data-testid="stHorizontalBlock"] > div,
        div.element-container,
        div.stMarkdown,
        div.stMarkdownContainer{
          margin-top: 0 !important;
          margin-bottom: 0 !important;
          padding-top: 0 !important;
          padding-bottom: 0 !important;
        }

        /* 2) HUD/게이지/전장 사이 간격 줄이기 + 전장 위로 당기기 */
        .p7-hud-gauge{ margin: 2px 0 4px 0 !important; }
        .p7-battlefield{ margin-top: -85px !important; padding-top: 0 !important; }
        .p7-zone{ margin-top: 6px !important; margin-bottom: 6px !important; }

        /* 3) 선택지: 회색 금지 (disabled 포함) */
        .p7-battlefield div[data-testid="stButton"]{
          opacity: 1 !important;
          filter: none !important;
        }

        .p7-battlefield div[data-testid="stButton"] > button{
          opacity: 1 !important;
          filter: none !important;
          font-size: 1.32em !important;
          font-weight: 950 !important;
          color: #000000 !important;
          -webkit-text-fill-color: #000000 !important;
        }

        .p7-battlefield div[data-testid="stButton"] > button *,
        .p7-battlefield div[data-testid="stButton"] > button span,
        .p7-battlefield div[data-testid="stButton"] > button p{
          opacity: 1 !important;
          filter: none !important;
          font-size: 1.32em !important;
          font-weight: 950 !important;
          color: #000000 !important;
          -webkit-text-fill-color: #000000 !important;
          text-shadow: none !important;
        }

        .p7-battlefield div[data-testid="stButton"] > button:disabled,
        .p7-battlefield div[data-testid="stButton"] > button:disabled *{
          opacity: 1 !important;
          color: #000000 !important;
          -webkit-text-fill-color: #000000 !important;
          filter: none !important;
        }
        </style>

        
        """, unsafe_allow_html=True)
    except Exception:
        pass


    # DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9] # ---- TOPSPACE_FORCE_V9 (AUTO, LAST WINS) ----
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]     try:
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]         st.markdown("""
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]         <style>
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]         /* === TOPSPACE_FORCE_V9 === */
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]         header[data-testid="stHeader"], div[data-testid="stToolbar"], div[data-testid="stDecoration"], footer {
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]           display:none !important; height:0 !important;
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]         }
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]         div[data-testid="stAppViewContainer"] > .main{ padding-top:0 !important; margin-top:0 !important; }
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]         section.main > div{ padding-top:0 !important; margin-top:0 !important; }
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]         .block-container{ max-width:100% !important; padding-top:0 !important; margin-top:0 !important; padding-left:.25rem !important; padding-right:.25rem !important; }
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9] 
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]         /* ⭐ 핵심: 극단값으로 확 당겨서 “체감” 먼저 만들기 */
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]         :root{ --p7-topshift: -160px; }  /* 나중에 -120 / -90으로 미세조정 */
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9] 
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]         .p7-hud-gauge{ margin: 2px 0 4px 0 !important; }
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]         .p7-battlefield{ margin-top: var(--p7-topshift) !important; padding-top:0 !important; }
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9] 
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]         /* 적용 증명 배지 */
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]         .p7-force-badge{
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]           position:fixed; right:12px; bottom:12px; z-index:999999;
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]           padding:10px 12px; border-radius:14px; background:rgba(255,255,255,0.92);
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]           border:3px solid rgba(0,255,170,0.70); color:#111827; font-weight:900; font-size:12px;
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]           box-shadow:0 14px 30px rgba(0,0,0,0.25);
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]         }
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]         .p7-force-badge b{ color:#00b894; }
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]         </style>
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]         """, unsafe_allow_html=True)
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]     except Exception:
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]         pass
# DISABLED_BY_VIEWPORT_LOCK[TOPSPACE_FORCE_V9]     # ---- /TOPSPACE_FORCE_V9 ----



# DISABLED_BY_VIEWPORT_LOCK[P7_FORCE_TOP_KILL] # ================== P7_FORCE_TOP_KILL ==================
# DISABLED_BY_VIEWPORT_LOCK[P7_FORCE_TOP_KILL] try:
# DISABLED_BY_VIEWPORT_LOCK[P7_FORCE_TOP_KILL]     st.markdown(r"""
# DISABLED_BY_VIEWPORT_LOCK[P7_FORCE_TOP_KILL]     <style>
# DISABLED_BY_VIEWPORT_LOCK[P7_FORCE_TOP_KILL]       /* 전장 자체를 위로 끌어올림 — Streamlit 무시 불가 */
# DISABLED_BY_VIEWPORT_LOCK[P7_FORCE_TOP_KILL]       .p7-battlefield {
# DISABLED_BY_VIEWPORT_LOCK[P7_FORCE_TOP_KILL]         margin-top: -160px !important;
# DISABLED_BY_VIEWPORT_LOCK[P7_FORCE_TOP_KILL]       }
# DISABLED_BY_VIEWPORT_LOCK[P7_FORCE_TOP_KILL] 
# DISABLED_BY_VIEWPORT_LOCK[P7_FORCE_TOP_KILL]       /* 모바일 안전 보정 */
# DISABLED_BY_VIEWPORT_LOCK[P7_FORCE_TOP_KILL]       @media (max-width: 768px) {
# DISABLED_BY_VIEWPORT_LOCK[P7_FORCE_TOP_KILL]         .p7-battlefield {
# DISABLED_BY_VIEWPORT_LOCK[P7_FORCE_TOP_KILL]           margin-top: -120px !important;
# DISABLED_BY_VIEWPORT_LOCK[P7_FORCE_TOP_KILL]         }
# DISABLED_BY_VIEWPORT_LOCK[P7_FORCE_TOP_KILL]       }
# DISABLED_BY_VIEWPORT_LOCK[P7_FORCE_TOP_KILL]     </style>
# DISABLED_BY_VIEWPORT_LOCK[P7_FORCE_TOP_KILL]     """, unsafe_allow_html=True)
# DISABLED_BY_VIEWPORT_LOCK[P7_FORCE_TOP_KILL] except Exception:
# DISABLED_BY_VIEWPORT_LOCK[P7_FORCE_TOP_KILL]     pass
# DISABLED_BY_VIEWPORT_LOCK[P7_FORCE_TOP_KILL] # ================== /P7_FORCE_TOP_KILL ==================


    # DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10] # ---- P7_LAYOUT_V10 (AUTO, LAST WINS) ----
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]     try:
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]         st.markdown("""
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]         <style>
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]         /* === P7_LAYOUT_V10 === */
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10] 
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]         /* 전장을 화면 높이로 쓰고(빈 공간 체감 제거) 내부를 flex로 배치 */
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]         .p7-battlefield{
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]           min-height: calc(100vh - 140px) !important;  /* HUD 높이 고려 */
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]           display: flex !important;
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]           flex-direction: column !important;
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]         }
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10] 
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]         /* radiogroup(선택지 묶음)을 아래로 밀기: 남는 공간을 흡수 */
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]         .p7-battlefield div[role="radiogroup"]{
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]           margin-top: auto !important;
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]           padding-top: 10px !important;
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]         }
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10] 
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]         /* 선택지 카드 간격 조금 안정화(너무 퍼지지 않게) */
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]         .p7-battlefield div[role="radiogroup"] > label{
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]           margin: 6px 0 !important;
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]         }
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10] 
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]         /* 적용 배지 */
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]         .p7-force-badge{
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]           position:fixed; right:12px; bottom:12px; z-index:999999;
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]           padding:10px 12px; border-radius:14px; background:rgba(255,255,255,0.92);
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]           border:3px solid rgba(0,255,170,0.70); color:#111827; font-weight:900; font-size:12px;
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]           box-shadow:0 14px 30px rgba(0,0,0,0.25);
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]         }
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]         .p7-force-badge b{ color:#00b894; }
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]         </style>
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10] 
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]         # DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]         """, unsafe_allow_html=True)
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]     except Exception:
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]         pass
# DISABLED_BY_VIEWPORT_LOCK[P7_LAYOUT_V10]     # ---- /P7_LAYOUT_V10 ----















# ===== P7_REALFILE_BADGE_BEGIN =====
try:
    import os
    st.caption("🔎 P7 REAL FILE: " + os.path.abspath(__file__))
except Exception:
    pass
# ===== P7_REALFILE_BADGE_END =====





    # ===== P7_SAFE_TOPPIN_BEGIN =====
    try:
        import os as _os
        st.markdown(r"""
        <style>
        /* P7 SAFE TOPPIN (LAST WINS) */
        :root{ --p7-hud-h: 64px; }

        header[data-testid="stHeader"],
        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"],
        footer{ display:none !important; height:0 !important; margin:0 !important; padding:0 !important; }

        html, body{ margin:0 !important; padding:0 !important; }
        .block-container{ padding-top:0 !important; margin-top:0 !important; }

        .p7-hudbar{
          position: fixed !important;
          top: 0 !important;
          left: 0 !important;
          right: 0 !important;
          z-index: 999999 !important;
          margin: 0 !important;
          border-radius: 0 !important;
        }
        .p7-battlefield{
          margin-top: var(--p7-hud-h) !important;
          padding-top: 0 !important;
        }

          position: fixed;
          top: 4px;
          left: 8px;
          z-index: 1000000;
          font-size: 11px;
          opacity: 0.75;
          padding: 2px 8px;
          border-radius: 999px;
          border: 1px solid rgba(255,255,255,0.18);
          background: rgba(0,0,0,0.15);
          backdrop-filter: blur(6px);
          white-space: nowrap;
        }
        </style>
        """.replace("{REAL}", _os.path.abspath(__file__).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")),
        unsafe_allow_html=True)
    except Exception:
        pass
    # ===== P7_SAFE_TOPPIN_END =====

    # ===== P7_FINAL_CLEAN_BEGIN =====
    try:
        st.markdown(r"""
        <style>
        /* =========================================================
           P7 FINAL CLEAN (ONE SOURCE OF TRUTH)
           - (A) 오른쪽 아래 겹친 배지/오버레이: 전부 숨김
           - (B) 2번째 캡처(아래 빈 그라데이션): body 스크롤 OFF, 전장 내부만 스크롤
           ========================================================= */

        :root{
          --p7-hud-h: 64px; /* 필요하면 56~72 */
        }

        /* (A) 모든 오버레이/배지 숨김 */
        .p7-probe-badge,
        .p7-realfile-overlay,
        .p7-badge,
        .p7-debug,
        .p7-debug-badge,
        .p7-bottom-badge,
        .p7-bottom-right,
        .p7-floating-badge{
          display:none !important;
          visibility:hidden !important;
          opacity:0 !important;
        }

        /* Streamlit 상단 장식/패딩 최소화 */
        header[data-testid="stHeader"],
        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"],
        footer{
          display:none !important;
          height:0 !important;
          margin:0 !important;
          padding:0 !important;
        }

        /* (B) 문서(body) 스크롤 OFF => 아래 빈 배경 원천 차단 */
        html, body{
          height:100% !important;
          overflow:hidden !important;
          margin:0 !important;
          padding:0 !important;
        }

        .stApp,
        div[data-testid="stAppViewContainer"],
        div[data-testid="stAppViewContainer"] > section,
        div[data-testid="stAppViewContainer"] > section > main,
        .block-container{
          height:100vh !important;
          overflow:hidden !important;
          padding-top:0 !important;
          margin-top:0 !important;
        }

        /* 전장만 스크롤 */
        .p7-battlefield{
          margin-top: 0 !important;
          height: 100vh !important;
          overflow-y:auto !important;
          overflow-x:hidden !important;
          padding-bottom: 24px !important;
        }
        </style>
        """, unsafe_allow_html=True)
    except Exception:
        pass
    # ===== P7_FINAL_CLEAN_END =====

    # ===== P7_NO_BLANK_BELOW_BEGIN =====
    try:
        st.markdown(r"""
        <style>
        /* FINAL: NO BLANK BELOW (LAST WINS) */

        :root{ --p7-hud-h: 64px; }

        html, body{
          height:100% !important;
          overflow:hidden !important;
          margin:0 !important;
          padding:0 !important;
          overscroll-behavior: none !important;
        }

        .stApp,
        div[data-testid="stAppViewContainer"],
        div[data-testid="stAppViewContainer"] > section,
        div[data-testid="stAppViewContainer"] > section > main,
        .block-container{
          height:100vh !important;
          overflow:hidden !important;
          padding-top:0 !important;
          margin-top:0 !important;
        }

        /* 전장만 스크롤 */
        .p7-battlefield{
          margin-top: var(--p7-hud-h) !important;
          height: calc(100vh - var(--p7-hud-h)) !important;
          overflow-y:auto !important;
          overflow-x:hidden !important;
          padding-bottom:24px !important;
        }

        /* 우하단 배지류(혹시 남아있으면) 표시 제거 */
        .p7-force-badge, .p7-probe-badge, .p7-realfile-overlay{
          display:none !important;
          visibility:hidden !important;
          opacity:0 !important;
        }
        </style>
        """, unsafe_allow_html=True)
    except Exception:
        pass
    # ===== P7_NO_BLANK_BELOW_END =====

    # ===== P7_FINAL_VIEWPORT_LOCK_BEGIN =====
    try:
        st.markdown(r"""
        <style>
        /* =========================================================
           P7 FINAL VIEWPORT LOCK (NO SECOND SCREEN)
           - html/body 스크롤 OFF  -> 아래 빈 그라데이션 원천 차단
           - .p7-battlefield만 스크롤
           ========================================================= */

        :root{ --p7-hud-h: 72px; } /* HUD 높이(필요시 64~80 범위로만 조절) */

        /* Streamlit 상단 장식 최소화 */
        header[data-testid="stHeader"],
        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"],
        footer{
          display:none !important;
          height:0 !important;
          margin:0 !important;
          padding:0 !important;
        }

        /* body 자체 스크롤 완전 차단 (2번째 캡쳐 원천 차단) */
        html, body{
          height:100% !important;
          overflow:hidden !important;
          margin:0 !important;
          padding:0 !important;
          overscroll-behavior: none !important;
        }

        /* Streamlit 상위 컨테이너도 뷰포트에 고정 */
        .stApp,
        div[data-testid="stAppViewContainer"],
        div[data-testid="stAppViewContainer"] > section,
        div[data-testid="stAppViewContainer"] > section > main,
        .block-container{
          height:100vh !important;
          overflow:hidden !important;
          padding-top:0 !important;
          padding-bottom:0 !important;
          margin-top:0 !important;
          margin-bottom:0 !important;
        }

        /* ✅ 전장만 스크롤 */
        .p7-battlefield{
          height: calc(100vh - var(--p7-hud-h)) !important;
          overflow-y: auto !important;
          overflow-x: hidden !important;
          padding-bottom: 24px !important;
          margin-top: 0 !important;
        }

        /* ✅ 남아있는 우하단 배지/스티커(혹시 남아도 표시만 숨김) */
        .p7-force-badge,
        .p7-probe-badge,
        .p7-realfile-overlay,
        [class*="FORCE"],
        [class*="HARD"]{
          display:none !important;
          visibility:hidden !important;
          opacity:0 !important;
        }
        
        /* P7_TOPGAP_MICRO_TUNE (SAFE) */
        .p7-hud-left{ margin-top:-18px !important; }
        .p7-hud-gauge{ margin-top:-14px !important; margin-bottom:6px !important; }

</style>
        """, unsafe_allow_html=True)
    except Exception:
        pass
    # ===== P7_FINAL_VIEWPORT_LOCK_END =====

    # ===== P7_SAFE_TOPGAP_AB_BEGIN =====
    try:
        st.markdown(r"""
        <style>
        /* =========================================================
           P7 SAFE TOP GAP (A+B) — CSS ONLY
           A) Streamlit 상단 여백/패딩 제거
           B) 첫 블록만 translateY로 살짝 위로
           ========================================================= */

        /* A) Streamlit 상단/컨테이너 여백 최소화 */
        header[data-testid="stHeader"],
        div[data-testid="stToolbar"],
        div[data-testid="stDecoration"],
        footer{
          display:none !important;
          height:0 !important;
          margin:0 !important;
          padding:0 !important;
        }

        div[data-testid="stAppViewContainer"] > section > main,
        div[data-testid="stAppViewContainer"] > section > main > div,
        section.main > div,
        .block-container{
          padding-top: 0rem !important;
          margin-top: 0rem !important;
        }

        /* B) 첫 블록만 살짝 위로 (SAFE) */
        main .block-container > div:first-child{
          transform: translateY(-18px) !important; /* -12 ~ -26 조절 */
        }
        </style>
        """, unsafe_allow_html=True)
    except Exception:
        pass
    # ===== P7_SAFE_TOPGAP_AB_END =====

    # ===== P7_TOPSPACE0_BEGIN =====
# ---- P7_TOPSPACE_FINAL_V3 (AUTO, LAST WINS) ----
    st.markdown(r"""
    <style>
    /* === P7_TOPSPACE_FINAL_V3 === */

    /* 0) Streamlit 기본 상단 여백(헤더/컨테이너) 최대한 압축 */
    header[data-testid="stHeader"]{ height: 0px !important; }
    header[data-testid="stHeader"] *{ display:none !important; }

    /* 앱 상단 패딩/마진 제거 (위 공간 아끼기) */
    div[data-testid="stAppViewContainer"] > .main{
      padding-top: 0rem !important;
      margin-top: 0rem !important;
    }
    section.main > div{
      padding-top: 0rem !important;
      margin-top: 0rem !important;
    }

    /* block-container 위 공간 확 줄이기 */
    .block-container{
      max-width: 100% !important;
      padding-left: 0.22rem !important;
      padding-right: 0.22rem !important;
      padding-top: 0.00rem !important;
      padding-bottom: 0.28rem !important;
      margin-top: 0 !important;
    }

    /* HUD 아래 간격도 압축 (있으면 적용) */
    .p7-topbar, .p7-hud, .p7-hud-wrap{
      margin-top: 0 !important;
      padding-top: 0 !important;
      margin-bottom: 6px !important;
      padding-bottom: 0 !important;
    }

    /* 1) 지문/문제 카드 위로 더 끌어올리기 */
    .p7-zone{
      margin: 6px 0 !important;
      padding: 12px 12px !important;
      border-radius: 16px !important;
    }
    .p7-zone:before{ width: 6px !important; }

    /* 2) 선택지 영역: 간격 타이트 */
    .p7-opt-wrap{
      gap: 8px !important;
      margin-top: 8px !important;
    }

    /* 3) 선택지 글씨: 1.1배 + 초굵게 + 진한 검정(흐림 방지) */
    .p7-opt-wrap button,
    .p7-opt-wrap button *{
      font-size: 1.32em !important;
      font-weight: 950 !important;
      color: #000000 !important;
      opacity: 1 !important;
      text-shadow: none !important;
      filter: none !important;
    }
    /* Streamlit 버튼이 disable 처리될 때도 흐려지지 않게 */
    .p7-opt-wrap button:disabled,
    .p7-opt-wrap button:disabled *{
      color: #000000 !important;
      opacity: 1 !important;
      -webkit-text-fill-color: #000000 !important;
    }

    /* 모바일에서 더 확실히(폰 체감) */
    @media (max-width: 640px){
      .block-container{
        padding-left: 0.18rem !important;
        padding-right: 0.18rem !important;
        padding-top: 0.00rem !important;
      }
      .p7-opt-wrap button,
      .p7-opt-wrap button *{
        font-size: 26px !important;
        font-weight: 950 !important;
      }
    }

    </style>
    """, unsafe_allow_html=True)
    # ===== P7_TOPSPACE0_END =====
def _safe_switch_page(candidates, fallback_hint: str = "") -> bool:
    """
    st.switch_page()를 안전하게 호출한다.
    - candidates: 시도할 페이지 경로 후보 리스트
    - 성공하면 True / 모두 실패하면 False
    """
    for p in candidates:
        try:
            st.switch_page(p)
            return True
        except Exception:
            continue
    if fallback_hint:
        st.warning(f"이동 경로를 찾지 못했습니다. ({fallback_hint}) 페이지 파일명/경로를 확인해주세요.")
    else:
        st.warning("이동 경로를 찾지 못했습니다. 페이지 파일명/경로를 확인해주세요.")
    return False


# --------------------------------------------
# 🔗 P7 / Vocab 기록 & 비밀무기고 카운트 연동
#   - record_p7_result(...)
#   - update_secret_armory_count(reason="add_from_p7")
# --------------------------------------------
try:
    # app 패키지 안에 있을 때 (예: app/stats_p7_vocab.py)
    from app.stats_p7_vocab import record_p7_result, update_secret_armory_count
except Exception:
    try:
        # 프로젝트 루트에 있을 때 (예: stats_p7_vocab.py)
        from stats_p7_vocab import record_p7_result, update_secret_armory_count
    except Exception:
        # 개발 중 import 에러가 나도 화면이 완전히 죽지 않게 방어
        record_p7_result = None
        update_secret_armory_count = None

IS_DIRECT_RUN = __name__ == "__main__"

if IS_DIRECT_RUN:
    st.set_page_config(
        page_title="SnapQ P7 Reading + Armory",
        page_icon="🔥",
        layout="wide",
    )



# === P7_HAS_FLAG_CSS ===
P7_TEXT_SCALE = 1.20  # 지문 기준 +20%

st.markdown('''
<style>
/* P7 HAS-FLAG TEXT UNIFY */
/* P7 ONLY */
body:has(#p7-flag) {{
  --p7-scale: 1.2;
}}

/* unified text size */
body:has(#p7-flag) .p7-zone-body,
body:has(#p7-flag) .p7-passage,
body:has(#p7-flag) .p7-question,
body:has(#p7-flag) .p7-choice,
body:has(#p7-flag) div[data-testid="stMarkdownContainer"] p,
body:has(#p7-flag) div[data-testid="stMarkdownContainer"] li {{
  font-size: calc(1rem * var(--p7-scale)) !important;
  font-weight: 750 !important;
  line-height: 1.45 !important;
  letter-spacing: 0.1px !important;
}}

/* radio labels (choices) forced to same size */
body:has(#p7-flag) div[role="radiogroup"] label,
body:has(#p7-flag) div[role="radiogroup"] label * {{
  font-size: calc(1rem * var(--p7-scale)) !important;
  font-weight: 800 !important;
  line-height: 1.35 !important;
}}

/* flatten cards */
body:has(#p7-flag) div[role="radiogroup"] label {{
  padding: 10px 12px !important;
  margin: 8px 0 !important;
  border-radius: 14px !important;
}}

body:has(#p7-flag) div[role="radiogroup"] label > div {{
  padding: 0 !important;
  margin: 0 !important;
}}
body:has(#p7-flag) div[role="radiogroup"] label p {{
  margin: 0 !important;
  padding: 0 !important;
}}
</style>
''', unsafe_allow_html=True)
# === P7 TEXT UNIFY INJECTED ===
P7_TEXT_SCALE = 1.20  # ✅ 지문 기준 +20%

st.markdown("""
<style>
/* P7 TEXT UNIFY (PASSAGE/Q/CHOICE) */
.p7-root {
  --p7-scale: 1.2;
  font-size: calc(1rem * var(--p7-scale)) !important;
}

.p7-root .p7-zone-body,
.p7-root .p7-passage,
.p7-root .p7-question,
.p7-root .p7-choice,
.p7-root div[data-testid="stMarkdownContainer"] p,
.p7-root div[data-testid="stMarkdownContainer"] li {
  font-size: 1em !important;
  font-weight: 750 !important;
  line-height: 1.45 !important;
  letter-spacing: 0.1px !important;
}

.p7-root div[role="radiogroup"] label,
.p7-root div[role="radiogroup"] label * {
  font-size: 1em !important;
  font-weight: 800 !important;
  line-height: 1.35 !important;
}

.p7-root div[role="radiogroup"] label {
  padding: 10px 12px !important;
  margin: 8px 0 !important;
  border-radius: 14px !important;
}

.p7-root div[role="radiogroup"] label > div {
  padding: 0 !important;
  margin: 0 !important;
}

.p7-root div[role="radiogroup"] label p {
  margin: 0 !important;
  padding: 0 !important;
}
</style>
""", unsafe_allow_html=True)
# ---------- 점수/랭킹 통계 파일 설정 ----------

STATS_FILE = "p7_vocab_stats.json"


def _get_stats_path() -> str:
    base_dir = os.path.dirname(__file__) if "__file__" in globals() else os.getcwd()
    return os.path.join(base_dir, STATS_FILE)


def _get_default_stats() -> Dict:
    return {
        "p7": {
            "total_sets": 0,
            "total_correct": 0,
            "total_questions": 0,
            "best_combo": 0,
            "last_played": "",
        },
        "vocab": {
            "total_sets": 0,
            "total_correct": 0,
            "total_questions": 0,
            "best_score": 0,
            "last_played": "",
        },
    }


def load_stats() -> Dict:
    path = _get_stats_path()
    if not os.path.exists(path):
        return _get_default_stats()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return _get_default_stats()

    base = _get_default_stats()
    for key in base:
        if key not in data or not isinstance(data[key], dict):
            data[key] = base[key]
        else:
            for sub_k, sub_v in base[key].items():
                if sub_k not in data[key]:
                    data[key][sub_k] = sub_v
    return data


def save_stats(stats: Dict) -> None:
    path = _get_stats_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def update_stats_after_p7_set(correct_count: int, total_questions: int, max_combo: int) -> None:
    stats = load_stats()
    p7 = stats.get("p7", {})
    p7["total_sets"] = p7.get("total_sets", 0) + 1
    p7["total_correct"] = p7.get("total_correct", 0) + int(correct_count)
    p7["total_questions"] = p7.get("total_questions", 0) + int(total_questions)
    prev_best = p7.get("best_combo", 0)
    p7["best_combo"] = max(prev_best, int(max_combo))
    p7["last_played"] = time.strftime("%Y-%m-%d %H:%M", time.localtime())
    stats["p7"] = p7
    save_stats(stats)


def update_stats_after_vocab_set(score: int, total_questions: int) -> None:
    stats = load_stats()
    vocab = stats.get("vocab", {})
    vocab["total_sets"] = vocab.get("total_sets", 0) + 1
    vocab["total_correct"] = vocab.get("total_correct", 0) + int(score)
    vocab["total_questions"] = vocab.get("total_questions", 0) + int(total_questions)
    prev_best = vocab.get("best_score", 0)
    vocab["best_score"] = max(prev_best, int(score))
    vocab["last_played"] = time.strftime("%Y-%m-%d %H:%M", time.localtime())
    stats["vocab"] = vocab
    save_stats(stats)

# ---------- P7 레벨 시스템 파일 설정 ----------

LEVEL_FILE = "p7_level_progress.json"


def _get_level_path() -> str:
    base_dir = os.path.dirname(__file__) if "__file__" in globals() else os.getcwd()
    return os.path.join(base_dir, LEVEL_FILE)


def _default_level_progress() -> Dict:
    return {
        "categories": {},
        "last_updated": "",
    }


def load_level_progress() -> Dict:
    path = _get_level_path()
    if not os.path.exists(path):
        return _default_level_progress()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return _default_level_progress()

    if "categories" not in data or not isinstance(data["categories"], dict):
        data["categories"] = {}
    if "last_updated" not in data:
        data["last_updated"] = ""
    return data


def save_level_progress(progress: Dict) -> None:
    path = _get_level_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def _ensure_category(progress: Dict, category: str) -> Dict:
    cat = progress["categories"].get(category)
    if not cat:
        cat = {
            "level": 1,         # Lv1 시작
            "streak": 0,        # 현재 레벨에서 연속 클리어 횟수
            "cleared_sets": 0,  # 클리어한 세트 수
            "total_sets": 0,    # 전체 세트 수
        }
    else:
        # 누락 필드 보정
        cat.setdefault("level", 1)
        cat.setdefault("streak", 0)
        cat.setdefault("cleared_sets", 0)
        cat.setdefault("total_sets", 0)
    progress["categories"][category] = cat
    return cat


def update_p7_level(category: str, cleared: bool):
    """
    한 세트가 끝났을 때 레벨/연승 정보를 업데이트.
    - cleared=True: 연승 +1, 5연승이면 레벨업(Lv5까지), streak 0으로 리셋
    - cleared=False: streak 0으로 리셋
    """
    progress = load_level_progress()
    cat = _ensure_category(progress, category)

    prev_level = cat["level"]

    cat["total_sets"] += 1
    if cleared:
        cat["cleared_sets"] += 1
        cat["streak"] += 1
        if cat["streak"] >= 5 and cat["level"] < 5:
            cat["level"] += 1
            cat["streak"] = 0
    else:
        cat["streak"] = 0

    progress["categories"][category] = cat
    progress["last_updated"] = time.strftime("%Y-%m-%d %H:%M", time.localtime())
    save_level_progress(progress)

    leveled_up = cat["level"] > prev_level
    return cat, leveled_up, prev_level


def get_p7_level_info(category: str) -> Dict:
    """
    특정 카테고리의 현재 레벨 정보 반환.
    없으면 기본값(Lv1, streak 0)으로 초기화한 뒤 반환.
    """
    progress = load_level_progress()
    cat = _ensure_category(progress, category)
    save_level_progress(progress)
    return cat


def get_all_p7_levels() -> Dict[str, Dict]:
    """전체 카테고리의 레벨 정보를 반환."""
    progress = load_level_progress()
    return progress.get("categories", {})

# ---------- 데이터 구조 정의 ----------

@dataclass
class StepData:
    sentences: List[str]
    question_en: str
    options_en: List[str]
    answer_index: int
    question_ko: str = ""
    options_ko: List[str] = field(default_factory=list)


@dataclass
class P7Set:
    set_id: str
    title: str
    category: str
    step1: StepData
    step2: StepData
    step3: StepData
    all_sentences_en: List[str]
    all_sentences_ko: List[str]


@dataclass
class P7Result:
    step: int
    is_correct: bool
    user_choice: int
    correct_choice: int


@dataclass
class TimebombState:
    total_limit: int = 150
    start_time: float = 0.0
    remaining: int = 150
    is_over: bool = False


@dataclass
class ComboState:
    current_combo: int = 0
    max_combo: int = 0
    timebomb_gauge: int = 0

# ---------- 데모용 P7 세트 ----------

P7_DEMO_SET = P7Set(
    set_id="DEMO_01",
    title="[공지] 고객지원팀 사무실 이전 안내",
    category="공지 / 안내",
    step1=StepData(
        sentences=[
            "Dear staff,",
            "This is to inform you that our customer support team will be relocated next month.",
        ],
        question_en="What is the main purpose of this message?",
        options_en=[
            "To ask employees to work overtime this weekend",
            "To notify staff about a team relocation",
            "To announce a new product for customers",
            "To invite staff to a training workshop",
        ],
        answer_index=1,
        question_ko="이 메시지의 주요 목적은 무엇입니까?",
        options_ko=[
            "직원들에게 이번 주말 야근을 요청하기",
            "팀 이전에 대해 직원들에게 알리기",
            "고객에게 신규 제품을 발표하기",
            "직원들을 연수 워크숍에 초대하기",
        ],
    ),
    step2=StepData(
        sentences=[
            "Dear staff,",
            "This is to inform you that our customer support team will be relocated next month.",
            "Starting from May 3, the team will move from the 5th floor to the 9th floor of the same building.",
            "The new office will have a larger meeting room and upgraded computer equipment.",
            "Please make sure to pack all personal belongings by April 28.",
        ],
        question_en="According to the notice, what will NOT change after the relocation?",
        options_en=[
            "The building where the team works",
            "The floor where the team works",
            "The size of the meeting room",
            "The quality of the computer equipment",
        ],
        answer_index=0,
        question_ko="안내문에 따르면, 이전 후에도 변하지 않는 것은 무엇입니까?",
        options_ko=[
            "팀이 근무하는 건물",
            "팀이 근무하는 층",
            "회의실의 크기",
            "컴퓨터 장비의 품질",
        ],
    ),
    step3=StepData(
        sentences=[
            "Dear staff,",
            "This is to inform you that our customer support team will be relocated next month.",
            "Starting from May 3, the team will move from the 5th floor to the 9th floor of the same building.",
            "The new office will have a larger meeting room and upgraded computer equipment.",
            "Please make sure to pack all personal belongings by April 28.",
            "IT staff will assist you with moving your desktop computers on April 30.",
            "If you need temporary storage boxes, please contact Ms. Rivera in the HR department.",
            "We appreciate your cooperation during this transition period.",
        ],
        question_en="What can be inferred about the relocation?",
        options_en=[
            "The move will be completed in one day without any preparation.",
            "Employees are expected to handle all technical tasks by themselves.",
            "Some preparation and support are planned before and during the move.",
            "The team will move to a different company building in another city.",
        ],
        answer_index=2,
        question_ko="사무실 이전에 대해 알 수 있는 사실은 무엇입니까?",
        options_ko=[
            "사전 준비 없이 하루 만에 이전이 끝난다.",
            "직원들이 모든 기술적인 일을 스스로 처리해야 한다.",
            "이전 전과 진행 중에 어느 정도 준비와 지원이 계획되어 있다.",
            "팀이 다른 도시의 다른 회사 건물로 옮겨 간다.",
        ],
    ),
    all_sentences_en=[
        "Dear staff,",
        "This is to inform you that our customer support team will be relocated next month.",
        "Starting from May 3, the team will move from the 5th floor to the 9th floor of the same building.",
        "The new office will have a larger meeting room and upgraded computer equipment.",
        "Please make sure to pack all personal belongings by April 28.",
        "IT staff will assist you with moving your desktop computers on April 30.",
        "If you need temporary storage boxes, please contact Ms. Rivera in the HR department.",
        "We appreciate your cooperation during this transition period.",
    ],
    all_sentences_ko=[
        "전 직원 여러분께,",
        "다음 달에 고객지원팀 사무실이 이전될 예정임을 알려드립니다.",
        "5월 3일부터 해당 팀은 같은 건물 5층에서 9층으로 이동합니다.",
        "새 사무실에는 더 큰 회의실과 업그레이드된 컴퓨터 장비가 마련될 예정입니다.",
        "개인 소지품은 4월 28일까지 모두 정리해 주시기 바랍니다.",
        "IT팀은 4월 30일에 데스크톱 컴퓨터 이동을 도울 예정입니다.",
        "임시 보관 박스가 필요하신 분은 인사부 리베라 씨에게 문의해 주세요.",
        "이전 기간 동안 협조해 주셔서 감사드립니다.",
    ],
)

# ---------- Armory용 P5 / 단어 구조 ----------

@dataclass
class P5Problem:
    problem_id: str
    question: str
    options: List[str]
    answer_index: int


@dataclass
class ArmoryVocabItem:
    word: str
    meaning: str
    source: str = "P7"


P5_SAMPLE_PROBLEMS: List[P5Problem] = [
    P5Problem(
        problem_id="P5_001",
        question="The manager _______ the report before the meeting.",
        options=["review", "reviewed", "reviewing", "to review"],
        answer_index=1,
    ),
    P5Problem(
        problem_id="P5_002",
        question="The new policy will be effective _______ July 1.",
        options=["in", "at", "on", "for"],
        answer_index=2,
    ),
    P5Problem(
        problem_id="P5_003",
        question="Employees must _______ their ID cards at all times.",
        options=["carry", "carried", "carries", "carrying"],
        answer_index=0,
    ),
]

SAMPLE_VOCAB_ITEMS: List[ArmoryVocabItem] = [
    ArmoryVocabItem(word="relocate", meaning="이전하다, 옮기다", source="P7-DEMO"),
    ArmoryVocabItem(word="transition", meaning="전환, 변화", source="P7-DEMO"),
    ArmoryVocabItem(word="assist", meaning="돕다, 지원하다", source="P7-DEMO"),
    ArmoryVocabItem(word="temporary", meaning="일시적인", source="P7-DEMO"),
    ArmoryVocabItem(word="effective", meaning="시행되는, 유효한", source="DEV"),
    ArmoryVocabItem(word="upgrade", meaning="업그레이드하다, 개선하다", source="DEV"),
    ArmoryVocabItem(word="department", meaning="부서, 부문", source="DEV"),
]

# ============================================
# 세션 상태 초기화
# ============================================

def init_session_state():
    if "p7_selected_category" not in st.session_state:
        st.session_state.p7_selected_category = "공지 / 안내"
    if "p7_selected_set_id" not in st.session_state:
        st.session_state.p7_selected_set_id = P7_DEMO_SET.set_id
    if "p7_current_step" not in st.session_state:
        st.session_state.p7_current_step = 1
    if "p7_results" not in st.session_state:
        st.session_state.p7_results: List[P7Result] = []
    if "p7_miss_count" not in st.session_state:
        st.session_state.p7_miss_count = 0
    if "p7_has_started" not in st.session_state:
        st.session_state.p7_has_started = False
    if "p7_has_finished" not in st.session_state:
        st.session_state.p7_has_finished = False

    if "p7_timebomb" not in st.session_state:
        st.session_state.p7_timebomb = TimebombState()
    if "p7_combo" not in st.session_state:
        st.session_state.p7_combo = ComboState()

    if "p7_stats_updated" not in st.session_state:
        st.session_state.p7_stats_updated = False

    if "p7_vocab_candidates" not in st.session_state:
        st.session_state.p7_vocab_candidates: List[Dict] = []

    if "p7_vocab_saved_this_set" not in st.session_state:
        st.session_state.p7_vocab_saved_this_set = False

    if "secret_armory_p5" not in st.session_state:
        st.session_state.secret_armory_p5: List[P5Problem] = []
    if "secret_armory_vocab" not in st.session_state:
        st.session_state.secret_armory_vocab: List[Dict] = []

    if "armory_section" not in st.session_state:
        st.session_state.armory_section = "hub"

    if "vocab_quiz_index" not in st.session_state:
        st.session_state.vocab_quiz_index = 0
    if "vocab_quiz_order" not in st.session_state:
        st.session_state.vocab_quiz_order: List[int] = []

    if "vocab_armory_mode" not in st.session_state:
        st.session_state.vocab_armory_mode = "study"
    if "vocab_current_set" not in st.session_state:
        st.session_state.vocab_current_set: List[Dict] = []

    # ✅ 플립 카드 학습 모드용 상태
    if "vocab_study_index" not in st.session_state:
        st.session_state.vocab_study_index = 0
    if "vocab_study_show_kor" not in st.session_state:
        st.session_state.vocab_study_show_kor = False

    if "vocab_lives" not in st.session_state:
        st.session_state.vocab_lives = 3
    if "vocab_score" not in st.session_state:
        st.session_state.vocab_score = 0
    if "vocab_stats_updated" not in st.session_state:
        st.session_state.vocab_stats_updated = False

    if "p5_quiz_index" not in st.session_state:
        st.session_state.p5_quiz_index = 0
    if "p5_quiz_order" not in st.session_state:
        st.session_state.p5_quiz_order: List[int] = []
    if "p5_quiz_started" not in st.session_state:
        st.session_state.p5_quiz_started = False

    # 현재 카테고리 레벨
    if "p7_level" not in st.session_state:
        st.session_state.p7_level = 1

    # ✅ P7 세트 전체 제한시간(초) - 전장 입장 전 선택
    if "p7_time_limit_choice" not in st.session_state:
        st.session_state.p7_time_limit_choice = 150

# ============================================
# Timebomb / 콤보 관련
# ============================================

def start_timebomb():
    tb = st.session_state.p7_timebomb
    # ✅ 전장 입장 전 선택한 시간(세트 전체 제한시간)을 반영
    tb.total_limit = int(st.session_state.get("p7_time_limit_choice", 150))
    tb.start_time = time.time()
    tb.remaining = tb.total_limit
    tb.is_over = False
    st.session_state.p7_timebomb = tb


def update_timebomb():
    tb: TimebombState = st.session_state.p7_timebomb
    if tb.is_over or tb.start_time == 0:
        return
    elapsed = int(time.time() - tb.start_time)
    remaining = tb.total_limit - elapsed
    if remaining <= 0:
        tb.remaining = 0
        tb.is_over = True
    else:
        tb.remaining = remaining
    st.session_state.p7_timebomb = tb


def get_time_display(sec: int) -> str:
    if sec < 0:
        sec = 0
    m, s = divmod(sec, 60)
    return f"{m:02d}:{s:02d}"


def add_combo(is_correct: bool):
    combo: ComboState = st.session_state.p7_combo
    if is_correct:
        combo.current_combo += 1
        if combo.current_combo > combo.max_combo:
            combo.max_combo = combo.current_combo
        combo.timebomb_gauge = min(100, combo.timebomb_gauge + 15)
    else:
        combo.current_combo = 0
        combo.timebomb_gauge = max(0, combo.timebomb_gauge - 20)
    st.session_state.p7_combo = combo


def render_timebomb_and_combo(compact: bool = False):
    update_timebomb()

    # ---- finish/timeout handling ----
    tb: TimebombState = st.session_state.p7_timebomb
    if tb.is_over and not st.session_state.get("p7_has_finished", False):
        st.session_state["p7_has_finished"] = True

    if st.session_state.get("p7_has_finished", False):
        render_p7_feedback()
        return

    tb: TimebombState = st.session_state.p7_timebomb
    combo: ComboState = st.session_state.p7_combo

    # ✅ 타이머 현장감: 전투 중에는 자동 리프레시로 초 단위 카운트다운이 보이게
    if st.session_state.get("p7_has_started", False) and not st.session_state.get("p7_has_finished", False) and not tb.is_over:
        try:
            from streamlit_autorefresh import st_autorefresh
            pass  # [AUTO-DISABLED duplicate P7 timebomb tick]

        except ModuleNotFoundError:
            pass

    # ✅ COMPACT 모드: 위쪽 자리 차지 최소화
    if compact:
        # 타이머/콤보 영역의 위아래 여백을 줄이는 CSS
        st.markdown(
        """
        <style>
          .p7-hud-sticky{
            position: sticky;
            top: 0.75rem;
          }

          /* =========================
             P7 Reading Arena - UI v2.2.5 (A안-전투구역 분리)
             - 로직 0 변경 / CSS+마크업만
             ========================= */

          /* Compact topbar */
          .p7-topbar{
            display:flex;
            align-items:baseline;
            justify-content:space-between;
            gap:12px;
            margin: 0.15rem 0 0.35rem 0;
          }
          .p7-topbar .ttl{
            font-size: 20px;
            font-weight: 900;
            letter-spacing: -0.2px;
          }
          .p7-topbar .meta{
            font-size: 12px;
            font-weight: 700;
            color: #6b7280;
            white-space: nowrap;
          }
          .p7-divider{
            height:1px;
            background: rgba(17,24,39,0.10);
            margin: 0.35rem 0 0.6rem 0;
          }

          /* --- Zone cards (Intel / Mission) --- */
          .p7-zone{
            position: relative;
            border-radius: 16px;
            padding: 14px 16px;
            border: 1px solid rgba(17,24,39,0.10);
            background: #ffffff;
            box-shadow: 0 8px 22px rgba(15,23,42,0.06);
            margin: 10px 0;
            overflow: hidden;
          }
          .p7-zone:before{
            content:"";
            position:absolute;
            left:0; top:0; bottom:0;
            width: 6px;
            border-radius: 16px 0 0 16px;
            background: rgba(59,130,246,0.75);
          }
          .p7-zone .p7-zone-title{
            display:flex;
            align-items:center;
            gap:10px;
            font-size: 12px;
            font-weight: 900;
            letter-spacing: 0.6px;
            text-transform: uppercase;
            color: rgba(17,24,39,0.70);
            margin-bottom: 8px;
          }
          .p7-zone .p7-zone-body{
            font-size: 16px;
            font-weight: 700;
            color: #111827;
            line-height: 1.55;
          }
          .p7-zone.intel{
            background: linear-gradient(180deg, rgba(37,99,235,0.10), rgba(37,99,235,0.03));
            border-color: rgba(37,99,235,0.20);
          }
          .p7-zone.intel:before{ background: rgba(37,99,235,0.85); }
          .p7-zone.mission{
            background: linear-gradient(180deg, rgba(147,51,234,0.10), rgba(147,51,234,0.03));
            border-color: rgba(147,51,234,0.18);
            box-shadow: 0 10px 26px rgba(147,51,234,0.08);
          }
          .p7-zone.mission:before{ background: rgba(147,51,234,0.85); }

          /* --- Combat options label --- */
          .p7-combat-caption{
            display:flex;
            align-items:center;
            gap:10px;
            margin: 12px 0 8px 0;
            font-size: 12px;
            font-weight: 900;
            letter-spacing: 0.5px;
            color: rgba(17,24,39,0.75);
            text-transform: uppercase;
          }

          /* --- Radio -> Card options (Streamlit/BaseWeb) --- */
          div[role="radiogroup"]{ gap: 0 !important; }
          div[role="radiogroup"] > label{
            width: 100% !important;
            border-radius: 14px !important;
            border: 1px solid rgba(17,24,39,0.12) !important;
            background: linear-gradient(180deg, rgba(2,6,23,0.02), rgba(2,6,23,0.00)) !important;
            padding: 10px 12px !important;
            margin: 3px 0 !important; /* ✅ 위아래 간격 최대한 압축 */
            box-shadow: 0 8px 18px rgba(15,23,42,0.05) !important;
            transition: transform .12s ease, box-shadow .12s ease, border-color .12s ease, background .12s ease;
          }
          div[role="radiogroup"] > label:hover{
            transform: translateY(-1px);
            box-shadow: 0 12px 28px rgba(15,23,42,0.08) !important;
          }
          /* 선택됨: 파란 강조 + '잠김' 느낌 */
          div[role="radiogroup"] > label:has(input:checked){
            border-color: rgba(59,130,246,0.65) !important;
            background: linear-gradient(180deg, rgba(59,130,246,0.12), rgba(59,130,246,0.05)) !important;
            box-shadow: 0 10px 26px rgba(37,99,235,0.10) !important;
          }

          /* 라디오 원(기본) 공간을 조금 줄이기 */
          div[role="radiogroup"] > label > div{
            margin-top: 0 !important;
            margin-bottom: 0 !important;
          }

          /* 상단의 불필요한 빈 라벨/여백 최소화 */
          .stRadio > label{ display:none !important; }
          .stRadio{ margin-top: 0.15rem !important; }

          /* HUD '병기고' 버튼(세로) */
          .p7-armory-vert button{
            padding: 8px 10px !important;
            border-radius: 12px !important;
            border: 1px solid rgba(17,24,39,0.14) !important;
            background: #ffffff !important;
            font-weight: 900 !important;
          }

        
/* =========================================================
   P7 FULL WIDTH + ONE-LINE HUD (NO columns) + TIME PRESSURE
   ========================================================= */
.block-container{
  max-width: 100% !important;
  padding-left: 0.85rem !important;
  padding-right: 0.85rem !important;
  padding-top: 0.25rem !important;
}

/* HUD: 한 줄 FLEX (오른쪽 빈 공간 방지) */
.p7-hudbar{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 18px;
  background: rgba(255,255,255,0.18);
  border: 1px solid rgba(255,255,255,0.20);
  box-shadow: 0 10px 30px rgba(0,0,0,0.12);
  margin: 0 0 10px 0;
}
.p7-hud-left{
  display:flex;
  align-items:center;
  gap: 10px;
  flex-wrap: wrap;
}
.p7-hud-right{
  display:flex;
  align-items:center;
  justify-content:flex-end;
  gap: 8px;
}

/* MAIN HUB 버튼: HUD 높이에 맞춰 compact */
.p7-hud-right div[data-testid="stButton"] > button{
  padding: 10px 12px !important;
  border-radius: 14px !important;
  font-weight: 900 !important;
  line-height: 1.0 !important;
  border: 1px solid rgba(0,0,0,0.06) !important;
}

/* CHIP size 타이트 */
.p7-chip{ padding: 6px 10px !important; font-size: 12.8px !important; }
.p7-chip b{ font-size: 13.8px !important; }

/* TIME 압박 효과 */
.p7-time-chip{ display:inline-flex; align-items:center; gap:8px; }
.p7-time-svg{ width:18px; height:18px; display:inline-block; vertical-align:middle; }

@keyframes p7Pulse60 { 0%{transform:scale(1)} 50%{transform:scale(1.12)} 100%{transform:scale(1)} }
@keyframes p7Pulse30 { 0%{transform:scale(1)} 50%{transform:scale(1.18)} 100%{transform:scale(1)} }
@keyframes p7Shake10 {
  0%{transform:translateX(0)}
  20%{transform:translateX(-1px)}
  40%{transform:translateX(1px)}
  60%{transform:translateX(-1px)}
  80%{transform:translateX(1px)}
  100%{transform:translateX(0)}
}

.p7-chip.p7-time-danger{
  background: rgba(255,45,45,0.18) !important;
  border-color: rgba(255,45,45,0.35) !important;
  box-shadow: 0 0 14px rgba(255,45,45,0.15) !important;
}
.p7-time-danger .p7-time-svg{
  filter: drop-shadow(0 0 7px rgba(255,45,45,.55));
  animation: p7Pulse60 .9s ease-in-out infinite;
}

.p7-chip.p7-time-critical{
  background: rgba(255,45,45,0.26) !important;
  border-color: rgba(255,45,45,0.48) !important;
  box-shadow: 0 0 18px rgba(255,45,45,0.22) !important;
}
.p7-time-critical .p7-time-svg{
  filter: drop-shadow(0 0 9px rgba(255,45,45,.65));
  animation: p7Pulse30 .75s ease-in-out infinite;
}

.p7-chip.p7-time-final{
  animation: p7Shake10 .35s linear infinite;
}

/* --- P7 HUD MAIN HUB (HTML button) --- */
.p7-hub-btn{
  padding: 10px 14px;
  border-radius: 14px;
  font-weight: 900;
  border: 1px solid rgba(0,0,0,0.08);
  background: rgba(255,255,255,0.92);
  cursor: pointer;
  line-height: 1.0;
}
.p7-hub-btn:hover{
  background: rgba(255,255,255,1.0);
  transform: translateY(-1px);
}

/* === P7 밀도 패치: HUD ↔ 지문 간격 축소 === */
.p7-hudbar{
  margin-bottom: 8px !important;
  padding-bottom: 6px !important;
}

/* HUD 바로 아래 첫 지문 카드 */
.p7-passage-card,
.p7-reading-card,
.p7-passage{
  margin-top: 6px !important;
  padding-top: 14px !important;
}

/* === 지문 글씨 가독성 업 (1.3배) === */
.p7-passage-text,
.p7-reading-text{
  font-size: 1.3rem !important;
  line-height: 1.6 !important;
}

/* =========================================================
   P7 B-2 OPTIONS (Card Buttons)
   - p7-opt-wrap 안의 버튼만 통일
   ========================================================= */
.p7-opt-wrap{
  display: grid;
  gap: 14px;
  margin-top: 10px;
}

/* ✅ 핵심: 모든 선택지 버튼 "같은 높이" */
.p7-opt-wrap div[data-testid="stButton"] > button{
  width: 100% !important;

  /* 높이 통일 */
  min-height: 74px !important;

  /* 터치감 */
  padding: 18px 18px !important;
  border-radius: 18px !important;
  font-size: 30px !important;
  font-weight: 800 !important;
  line-height: 1.25 !important;

  /* 카드 느낌 */
  background: rgba(255,255,255,0.98) !important;
  border: 1px solid rgba(255,255,255,0.25) !important;
  box-shadow: 0 10px 28px rgba(0,0,0,0.14) !important;

  /* 긴 문장도 보기 좋게 */
  white-space: normal !important;
  text-align: center !important;

  /* 반응성 */
  transition: transform .08s ease, box-shadow .08s ease, filter .08s ease;
}

/* Hover = "타겟 락온" 느낌 */
.p7-opt-wrap div[data-testid="stButton"] > button:hover{
  transform: translateY(-1px);
  box-shadow: 0 14px 32px rgba(0,0,0,0.18) !important;
  filter: brightness(1.02);
}

/* Press = "LOCK IN" */
.p7-opt-wrap div[data-testid="stButton"] > button:active{
  transform: translateY(1px) scale(0.995);
  box-shadow: 0 8px 18px rgba(0,0,0,0.12) !important;
}

/* 모바일에서 더 잘 눌리게(폭 좁으면 높이 조금 증가) */
@media (max-width: 640px){
  .p7-opt-wrap div[data-testid="stButton"] > button{
    min-height: 82px !important;
    font-size: 17px !important;
    padding: 18px 16px !important;
  }
}

/* =========================================================
   P7 B-3 TIME PRESSURE
   ========================================================= */

.p7-time-chip{
  font-weight: 900 !important;
  transition: all .15s ease;
}

/* 60s ↓ WARNING */
.p7-time-warn{
  background: #ffcc00 !important;
  color: #1a1a1a !important;
}

/* 30s ↓ DANGER */
.p7-time-danger{
  background: #ff3b3b !important;
  color: #fff !important;
  animation: p7-blink .8s infinite;
}

@keyframes p7-blink{
  0%{filter:brightness(1)}
  50%{filter:brightness(1.25)}
  100%{filter:brightness(1)}
}

/* 15s ↓ SCREEN VIGNETTE */
.p7-vignette{
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9999;
  box-shadow: inset 0 0 120px rgba(255,0,0,.45);
  animation: p7-pulse 1.2s infinite;
}

@keyframes p7-pulse{
  0%{box-shadow: inset 0 0 80px rgba(255,0,0,.35)}
  50%{box-shadow: inset 0 0 140px rgba(255,0,0,.55)}
  100%{box-shadow: inset 0 0 80px rgba(255,0,0,.35)}
}

/* =========================
   P7 HUD ONE-LINE + TIME PRESSURE + VIGNETTE (FINAL)
   ========================= */
.p7-hudbar{
  display:flex; align-items:center; justify-content:space-between; gap:10px;
  padding:8px 10px; border-radius:18px;
  background: rgba(255,255,255,0.10);
  border: 1px solid rgba(255,255,255,0.14);
  box-shadow: 0 10px 26px rgba(0,0,0,0.20);
  backdrop-filter: blur(10px);
  margin: 0 0 8px 0;
}
.p7-hud-left{ display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
.p7-hud-right{ display:flex; align-items:center; justify-content:flex-end; }

.p7-hub-btn{
  padding:10px 14px; border-radius:14px; font-weight:900;
  border: 1px solid rgba(0,0,0,0.10);
  background: rgba(255,255,255,0.95);
  cursor:pointer; line-height:1.0;
}
.p7-hub-btn:hover{ transform: translateY(-1px); background:#fff; }

.p7-time-chip{ display:inline-flex; align-items:center; gap:8px; }
.p7-time-svg{ width:18px; height:18px; display:inline-block; vertical-align:middle; }

/* 60s ↓ warning(노랑) */
.p7-time-warn{ background: rgba(255,204,0,0.22) !important; border-color: rgba(255,204,0,0.45) !important; }
/* 30s ↓ danger(빨강 + 깜빡) */
@keyframes p7Blink{ 0%{filter:brightness(1)} 50%{filter:brightness(1.25)} 100%{filter:brightness(1)} }
.p7-time-danger2{ background: rgba(255,45,45,0.22) !important; border-color: rgba(255,45,45,0.55) !important; animation: p7Blink .85s infinite; }
/* 10s ↓ final(흔들림) */
@keyframes p7Shake10{
  0%{transform:translateX(0)} 20%{transform:translateX(-1px)} 40%{transform:translateX(1px)}
  60%{transform:translateX(-1px)} 80%{transform:translateX(1px)} 100%{transform:translateX(0)}
}
.p7-time-final2{ animation: p7Shake10 .35s linear infinite; }

/* 15s ↓ 비네팅 */
.p7-vignette{
  position: fixed; inset: 0; pointer-events:none; z-index: 9999;
  box-shadow: inset 0 0 140px rgba(255,0,0,.45);
  animation: p7Vig 1.1s infinite;
}
@keyframes p7Vig{
  0%{box-shadow: inset 0 0 90px rgba(255,0,0,.32)}
  50%{box-shadow: inset 0 0 170px rgba(255,0,0,.55)}
  100%{box-shadow: inset 0 0 90px rgba(255,0,0,.32)}
}

/* =========================
   P7 C-1 WRONG PRESSURE FX
   ========================= */
@keyframes p7Heart{
  0%{transform:scale(1); filter:brightness(1)}
  20%{transform:scale(1.02); filter:brightness(1.05)}
  40%{transform:scale(0.995); filter:brightness(1)}
  60%{transform:scale(1.03); filter:brightness(1.08)}
  100%{transform:scale(1); filter:brightness(1)}
}
@keyframes p7ScreenShake2{
  0%{transform:translate(0,0)}
  20%{transform:translate(-2px,0)}
  40%{transform:translate(2px,0)}
  60%{transform:translate(-2px,1px)}
  80%{transform:translate(2px,-1px)}
  100%{transform:translate(0,0)}
}
@keyframes p7ScreenShake3{
  0%{transform:translate(0,0)}
  10%{transform:translate(-3px,1px)}
  20%{transform:translate(3px,-1px)}
  30%{transform:translate(-3px,0)}
  40%{transform:translate(3px,1px)}
  50%{transform:translate(-2px,-1px)}
  60%{transform:translate(2px,1px)}
  70%{transform:translate(-3px,0)}
  80%{transform:translate(3px,-1px)}
  90%{transform:translate(-2px,1px)}
  100%{transform:translate(0,0)}
}

/* 화면 전체에 걸리는 오버레이(전장 압박) */
.p7-wrongfx{
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9998;
}

/* 오답 2회: 심장박동 + 약한 흔들림 */
.p7-wrongfx.w2{
  animation:
    p7Heart 0.9s ease-in-out infinite,
    p7ScreenShake2 0.55s linear infinite;
}

/* 오답 3회: 더 강한 흔들림 */
.p7-wrongfx.w3{
  animation:
    p7Heart 0.75s ease-in-out infinite,
    p7ScreenShake3 0.45s linear infinite;
}

/* HUD 안 MISS 칩도 같이 붉게(시선 고정) */
.p7-miss-danger{
  background: rgba(255,45,45,0.20) !important;
  border-color: rgba(255,45,45,0.50) !important;
  box-shadow: 0 0 16px rgba(255,45,45,0.18) !important;
}

/* =========================
   P7 TOP GAP FIX (hide top panel)
   ========================= */

/* 1) 페이지 최상단 여백 제거 */
.block-container{
  padding-top: 0.2rem !important;
}

/* 2) 지문 위에 남아있는 큰 패널/빈 컨테이너를 압축
   - Streamlit이 만든 빈 element container가 위를 차지하는 경우가 많아서
     p7에서만 안전하게 '높이/패딩'을 줄임
*/
.p7-top-panel,
.p7-prepanel,
.p7-stage-panel,
.p7-upper-panel{
  display: none !important;
}

/* 3) 혹시 클래스가 없더라도, "p7-hudbar 위에 남는 첫 큰 박스"를 줄이기
   - main 영역 초반 container들이 과하게 커지는 상황 대응
*/
main .block-container > div:first-child{
  margin-top: 0 !important;
  padding-top: 0 !important;
}

/* 4) HUD 바로 아래부터 본문이 붙도록 */
.p7-hudbar{ margin-bottom: 6px !important; }

/* =========================
   A-HUDBAR-HARD-FIX
   - 상단 HUD가 '큰 패널'처럼 커지는 현상 방지
   ========================= */
.p7-hudbar{
  max-height: 64px !important;
  overflow: hidden !important;
}
.p7-hud-left, .p7-hud-right{
  align-items: center !important;
}
.p7-hudbar *{
  line-height: 1.0 !important;
}
main .block-container{
  padding-top: 0.10rem !important;
}

/* =========================
   A-HUD-VISIBILITY-FIX
   - HUD 바/칩/텍스트가 '하얀 바' 위에서 안 보이는 문제 강제 해결
   ========================= */
.p7-hudbar{
  background: rgba(0,0,0,0.22) !important;
  border: 1px solid rgba(255,255,255,0.18) !important;
  box-shadow: 0 10px 26px rgba(0,0,0,0.22) !important;
  color: #ffffff !important;
}
.p7-hudbar *{
  color: #ffffff !important;
  opacity: 1 !important;
  filter: none !important;
  text-shadow: 0 2px 6px rgba(0,0,0,0.55) !important;
}

/* HUD 칩들( STEP / TIME / MISS / COMBO ) */
.p7-chip{
  background: rgba(0,0,0,0.35) !important;
  border: 1px solid rgba(255,255,255,0.20) !important;
  color: #ffffff !important;
}
.p7-chip b{ color:#ffffff !important; }

/* TIME 칩 내부 SVG 링도 확실히 보이게 */
.p7-time-svg circle{
  opacity: 1 !important;
}

/* MAIN HUB 버튼(HTML)도 대비 확보 */
.p7-hub-btn{
  background: rgba(255,255,255,0.92) !important;
  color: #111111 !important;
  border: 1px solid rgba(0,0,0,0.12) !important;
}
.p7-hub-btn:hover{
  background: rgba(255,255,255,1.0) !important;
}
/* =========================================================
   P7 TIME ONLY — "HEART-CLENCH" PATCH (C-1)
   ========================================================= */
.p7-time-chip{position:relative;font-weight:950!important;letter-spacing:.02em;}
.p7-time-chip b{display:inline-block;letter-spacing:.06em;animation:p7TimeTick 1s steps(1) infinite;}
.p7-time-chip,.p7-time-chip b,.p7-time-chip .p7-time-svg{
 transition:filter .15s,transform .15s,box-shadow .15s,background .15s;
}
@keyframes p7TimeTick{0%{transform:translateY(0)}35%{transform:translateY(-.6px)}70%{transform:translateY(0)}}
@keyframes p7TimeBeat60{
 0%{transform:scale(1)}35%{transform:scale(1.04)}70%{transform:scale(1)}
}
@keyframes p7TimeBeat30{
 0%{transform:scale(1)}
 18%{transform:scale(1.06)}
 30%{transform:scale(.995)}
 52%{transform:scale(1.075)}
 70%{transform:scale(1)}
}
@keyframes p7TimeJitter10{
 0%{transform:translateX(0)}
 20%{transform:translateX(-.8px)}
 40%{transform:translateX(.8px)}
 60%{transform:translateX(-.6px)}
 80%{transform:translateX(.6px)}
}
@keyframes p7RingGlow{
 0%{filter:drop-shadow(0 0 5px rgba(255,45,45,.25))}
 50%{filter:drop-shadow(0 0 11px rgba(255,45,45,.65))}
 100%{filter:drop-shadow(0 0 5px rgba(255,45,45,.25))}
}
.p7-time-warn b{
 animation:p7TimeTick 1s steps(1) infinite,p7TimeBeat60 1.15s infinite;
}
.p7-time-danger2 b{
 animation:p7TimeBeat30 .78s infinite;
 text-shadow:0 0 10px rgba(255,45,45,.2);
}
.p7-time-danger2 .p7-time-svg{
 animation:p7TimeBeat30 .78s infinite,p7RingGlow .78s infinite;
}
.p7-time-final2{
 animation:p7TimeJitter10 .33s linear infinite;
}
.p7-time-final2 b{
 animation:p7TimeBeat30 .62s infinite;
}
/* ===== P7 TIME ONLY: ALWAYS-ON "ALIVE" (SAFE) ===== */
@keyframes p7AliveTick { 0%{transform:translateY(0)} 35%{transform:translateY(-0.6px)} 70%{transform:translateY(0)} 100%{transform:translateY(0)} }
@keyframes p7AlivePulse { 0%{transform:scale(1)} 40%{transform:scale(1.02)} 80%{transform:scale(1)} 100%{transform:scale(1)} }

.p7-time-alive{
  animation: p7AlivePulse 1.6s ease-in-out infinite;
}
.p7-time-alive .p7-time-svg{
  animation: p7AlivePulse 1.6s ease-in-out infinite;
}
.p7-time-alive *{
  /* 숫자 텍스트가 어떤 태그여도 미세 tick이 먹게 */
  animation: p7AliveTick 1s steps(1) infinite;
}
/* ===== EXECUTION CHECK WATERMARK ===== */
.p7-exec-check::after{
  content:" ⛔LIVE ";
  color:#ff2d2d;
  font-weight:900;
  margin-left:8px;
  animation:p7ExecBlink .8s steps(1) infinite;
}
@keyframes p7ExecBlink{
  0%{opacity:1}
  50%{opacity:.2}
  100%{opacity:1}
}
/* ===== P7 TIME FINAL HEART-CLENCH ===== */

@keyframes p7PulseSoft {
  0%{
    transform:scale(1);
    filter:brightness(1);
    box-shadow: 0 0 0 1px rgba(255,255,255,.10) inset, 0 0 10px rgba(160,140,255,.10);
  }
  50%{
    transform:scale(1.03);
    filter:brightness(1.10);
    box-shadow: 0 0 0 1px rgba(255,255,255,.16) inset, 0 0 18px rgba(160,140,255,.22);
  }
  100%{
    transform:scale(1);
    filter:brightness(1);
    box-shadow: 0 0 0 1px rgba(255,255,255,.10) inset, 0 0 10px rgba(160,140,255,.10);
  }
}



@keyframes p7Beat60 {
  0%{transform:scale(1)}
  40%{transform:scale(1.04)}
  100%{transform:scale(1)}
}

@keyframes p7Beat30 {
  0%{transform:scale(1)}
  20%{transform:scale(1.06)}
  40%{transform:scale(.99)}
  60%{transform:scale(1.075)}
  100%{transform:scale(1)}
}

@keyframes p7Shake10 {
  0%{transform:translateX(0)}
  25%{transform:translateX(-1px)}
  50%{transform:translateX(1px)}
  75%{transform:translateX(-0.8px)}
  100%{transform:translateX(0)}
}

/* always alive */
.p7-time-chip{
  animation:p7PulseSoft 1.8s ease-in-out infinite;
}

/* C-1 ≤60s */
.p7-time-warn{
  animation:p7Beat60 1.1s infinite;
}

/* C-2 ≤30s */
.p7-time-danger{
  animation:p7Beat30 .75s infinite;
  filter:drop-shadow(0 0 10px rgba(255,60,60,.45));
}

/* C-3 ≤10s */
.p7-time-final{
  animation:p7Shake10 .28s linear infinite;
  filter:drop-shadow(0 0 18px rgba(255,40,40,.85));
}
/* =========================================================
   P7 TIME FINAL TUNING v2 (MATCH CLASS NAMES)
   - TIME ONLY
   ========================================================= */

@keyframes p7PulseSoft {
  0%{
    transform:scale(1);
    filter:brightness(1);
    box-shadow: 0 0 0 1px rgba(255,255,255,.10) inset, 0 0 10px rgba(160,140,255,.10);
  }
  50%{
    transform:scale(1.03);
    filter:brightness(1.10);
    box-shadow: 0 0 0 1px rgba(255,255,255,.16) inset, 0 0 18px rgba(160,140,255,.22);
  }
  100%{
    transform:scale(1);
    filter:brightness(1);
    box-shadow: 0 0 0 1px rgba(255,255,255,.10) inset, 0 0 10px rgba(160,140,255,.10);
  }
}



@keyframes p7Beat60 {
  0%{transform:scale(1)}
  38%{transform:scale(1.05)}
  100%{transform:scale(1)}
}

@keyframes p7Beat30 {
  0%{transform:scale(1)}
  20%{transform:scale(1.06)}
  38%{transform:scale(.99)}
  58%{transform:scale(1.085)}
  100%{transform:scale(1)}
}

@keyframes p7Shake10 {
  0%{transform:translateX(0)}
  25%{transform:translateX(-1px)}
  50%{transform:translateX(1px)}
  75%{transform:translateX(-0.8px)}
  100%{transform:translateX(0)}
}

/* 항상: "살아있음" (눈에 보이게 조금 더) */
.p7-time-chip{
  animation: p7PulseSoft 1.6s ease-in-out infinite !important;
}

/* 60초↓: C-1 */
.p7-time-warn{
  animation: p7Beat60 1.05s ease-in-out infinite !important;
  box-shadow: 0 0 0 1px rgba(255,204,0,.18) inset, 0 0 18px rgba(255,204,0,.10) !important;
}

/* 30초↓: C-2 (du-dum) */
.p7-time-danger2{
  animation: p7Beat30 .74s ease-in-out infinite !important;
  filter: drop-shadow(0 0 10px rgba(255,60,60,.45)) !important;
  box-shadow: 0 0 0 1px rgba(255,60,60,.20) inset, 0 0 26px rgba(255,60,60,.16) !important;
}

/* 10초↓: C-3 (TIME 칩만 떨림) */
.p7-time-final2{
  animation: p7Shake10 .26s linear infinite !important;
  filter: drop-shadow(0 0 18px rgba(255,40,40,.85)) !important;
  box-shadow: 0 0 0 1px rgba(255,40,40,.22) inset, 0 0 34px rgba(255,40,40,.22) !important;
}

/* 눈으로 확인 가능한 아주 작은 표시(개발 중만) */
.p7-time-chip::after{
  content:"";
  opacity:.0;
}
/* =========================================================
   TIME_FORCE_VISIBLE_V1  (DEBUG — remove later)
   - strongest selector + !important
   ========================================================= */

@keyframes p7TimeAliveGlowV1{
  0%{
    filter: brightness(1);
    box-shadow: 0 0 0 1px rgba(255,255,255,.12) inset,
                0 0 10px rgba(120,90,255,.18);
    background: rgba(0,0,0,0.22);
  }
  50%{
    filter: brightness(1.22);
    box-shadow: 0 0 0 1px rgba(255,255,255,.22) inset,
                0 0 22px rgba(120,90,255,.38);
    background: rgba(0,0,0,0.34);
  }
  100%{
    filter: brightness(1);
    box-shadow: 0 0 0 1px rgba(255,255,255,.12) inset,
                0 0 10px rgba(120,90,255,.18);
    background: rgba(0,0,0,0.22);
  }
}

/* ✅ 가장 강하게: HUD 안 TIME 칩(=실제 사용 영역)만 */
.p7-hudbar .p7-time-chip.p7-time-alive{
  animation: p7TimeAliveGlowV1 1.05s ease-in-out infinite !important;
  border-color: rgba(255,255,255,0.30) !important;
}

/* TIME 글자도 같이 “숨쉬게” */
.p7-hudbar .p7-time-chip.p7-time-alive b{
  animation: p7TimeAliveGlowV1 1.05s ease-in-out infinite !important;
}

/* 60/30/10 구간은 더 강하게(기존 클래스명 그대로 사용) */
.p7-hudbar .p7-time-chip.p7-time-warn{
  animation-duration: .90s !important;
}
.p7-hudbar .p7-time-chip.p7-time-danger2{
  animation-duration: .72s !important;
  box-shadow: 0 0 0 1px rgba(255,60,60,.22) inset,
              0 0 26px rgba(255,60,60,.22) !important;
}
.p7-hudbar .p7-time-chip.p7-time-final2{
  animation-duration: .55s !important;
  box-shadow: 0 0 0 1px rgba(255,40,40,.28) inset,
              0 0 34px rgba(255,40,40,.32) !important;
}
/* =========================================================
   TIME_FORCE_TUNING_V2
   - overrides TIME_FORCE_VISIBLE_V1 (last wins)
   ========================================================= */

@keyframes p7TimeAliveGlowV2{
  0%{
    filter: brightness(1.02) saturate(1.02);
    box-shadow: 0 0 0 1px rgba(255,255,255,.14) inset,
                0 0 14px rgba(120,90,255,.22);
    background: rgba(0,0,0,0.26);
  }
  50%{
    filter: brightness(1.32) saturate(1.10);
    box-shadow: 0 0 0 1px rgba(255,255,255,.26) inset,
                0 0 30px rgba(120,90,255,.46);
    background: rgba(0,0,0,0.40);
  }
  100%{
    filter: brightness(1.02) saturate(1.02);
    box-shadow: 0 0 0 1px rgba(255,255,255,.14) inset,
                0 0 14px rgba(120,90,255,.22);
    background: rgba(0,0,0,0.26);
  }
}

/* baseline (2분대에서도 "예고 경보") */
.p7-hudbar .p7-time-chip.p7-time-alive{
  animation: p7TimeAliveGlowV2 .88s ease-in-out infinite !important;
  border-color: rgba(255,255,255,0.34) !important;
}

/* text emphasis */
.p7-hudbar .p7-time-chip.p7-time-alive b{
  animation: p7TimeAliveGlowV2 .88s ease-in-out infinite !important;
}

/* C-1 <=60s : faster + warmer edge */
.p7-hudbar .p7-time-chip.p7-time-warn{
  animation-duration: .74s !important;
  box-shadow: 0 0 0 1px rgba(255,204,0,.20) inset,
              0 0 26px rgba(255,204,0,.16) !important;
}

/* C-2 <=30s : du-dum feel stronger */
.p7-hudbar .p7-time-chip.p7-time-danger2{
  animation-duration: .62s !important;
  box-shadow: 0 0 0 1px rgba(255,60,60,.24) inset,
              0 0 36px rgba(255,60,60,.28) !important;
}

/* C-3 <=10s : TIME-only jitter */
@keyframes p7TimeJitterV2{
  0%{transform:translateX(0)}
  25%{transform:translateX(-1px)}
  50%{transform:translateX(1px)}
  75%{transform:translateX(-1px)}
  100%{transform:translateX(0)}
}
.p7-hudbar .p7-time-chip.p7-time-final2{
  animation: p7TimeJitterV2 .24s linear infinite !important;
  box-shadow: 0 0 0 1px rgba(255,40,40,.30) inset,
              0 0 44px rgba(255,40,40,.34) !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([3, 2] if not compact else [2.2, 1.3])

    with col1:
        if compact:
            st.caption("⏱ TIMEBOMB")
        else:
            st.markdown("### ⏱ 시간폭탄 타이머")

        # 🔥 긴장감 연출(60/30/10초 구간)
        if tb.remaining <= 10:
            tone = ("#ffebee", "#c62828", "💥 폭발 임박! 10초!")
        elif tb.remaining <= 30:
            tone = ("#fff3e0", "#ef6c00", "🔥 30초 이하!")
        elif tb.remaining <= 60:
            tone = ("#fffde7", "#9e9d24", "⚠️ 60초 이하!")
        else:
            tone = ("#e8f5e9", "#2e7d32", "🟢 안정권")

        pad = "10px 12px" if compact else "12px 14px"
        title_fs = "12px" if compact else "14px"
        time_fs = "18px" if compact else "22px"

        st.markdown("""
            <div class="p7-hud-compact" style="padding:{pad}; border-radius:12px; background:{tone[0]}; border:1px solid {tone[1]};">
              <div style="font-size:{title_fs}; font-weight:800; color:{tone[1]}; margin-bottom:2px;">{tone[2]}</div>
              <div style="font-size:{time_fs}; font-weight:900; color:#111827;">
                {get_time_display(tb.remaining)}
                <span style="font-size:12px; font-weight:700; color:#6b7280;"> / {get_time_display(tb.total_limit)}</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        ratio = tb.remaining / tb.total_limit if tb.total_limit > 0 else 0
        st.progress(max(0.0, min(1.0, ratio)))

    with col2:
        if compact:
            st.caption("💣 COMBO")
        else:
            st.markdown("### 💣 콤보 게이지")

        if compact:
            st.write(f"현재 **{combo.current_combo}**  ·  최고 **{combo.max_combo}**")
        else:
            st.write(f"현재 콤보: **{combo.current_combo}연속**  |  최고 콤보: **{combo.max_combo}연속**")

        st.progress(max(0.0, min(1.0, combo.timebomb_gauge / 100)))



def render_top_hud():
    """
    ✅ HUD 복구 + 게이지 드라마
    - STEP/TIME/MISS/COMBO 표시 복구
    - 게이지: stage(30초) + last60/last30/final 클래스 부여
    - 로직 변화 0 (표시/클래스만)
    """
    update_timebomb()
    tb: TimebombState = st.session_state.p7_timebomb
    combo: ComboState = st.session_state.p7_combo

    # HUD 전용 tick (전투 중만)
    if st.session_state.get("p7_has_started", False) and not st.session_state.get("p7_has_finished", False) and not tb.is_over:
        try:
            from streamlit_autorefresh import st_autorefresh
            st_autorefresh(interval=1000, key="p7_top_hud_tick")
        except ModuleNotFoundError:
            pass

    wrong = int(st.session_state.get("p7_miss_count", 0))
    step = int(st.session_state.get("p7_current_step", 1))
    total = max(1, int(getattr(tb, "total_limit", 150) or 150))
    remaining = max(0, int(getattr(tb, "remaining", 0)))

    # === P7_HUD_CLASS_DRAMA_V2 ===
    time_cls = "p7-time-alive"
    if remaining <= 10:
        time_cls = "p7-time-final2"
    elif remaining <= 30:
        time_cls = "p7-time-danger2"
    elif remaining <= 60:
        time_cls = "p7-time-warn"
    miss_cls = "p7-miss-warn" if wrong > 0 else ""
    combo_cls = "p7-combo-live" if getattr(combo, "current_combo", 0) > 0 else ""
    # === /P7_HUD_CLASS_DRAMA_V2 ===

    # HUD bar
    colL, colR = st.columns([12, 2], gap="small")
    with colL:
        st.markdown("""
            <div class="p7-hud-left">
              <span class="p7-chip">🔥 STEP <b>{step}</b>/3</span>
              <span class="p7-chip p7-time-chip {time_cls}">⏱ TIME <b>{get_time_display(remaining)}</b></span>
              <span class="p7-chip {miss_cls}">❌ MISS <b>{wrong}</b>/3</span>
              <span class="p7-chip {combo_cls}">💣 COMBO <b>{combo.current_combo}</b></span>
            </div>
            """,
            unsafe_allow_html=True
        )
    with colR:
        if st.button("🏠 HUB", key="p7_hud_mainhub_btn", use_container_width=True):
            _safe_switch_page(
                ["main_hub.py", "./main_hub.py", "pages/00_Main_Hub.py", "pages\\00_Main_Hub.py"],
                fallback_hint="메인 허브",
            )

    # Gauge drama
    pct = max(0.0, min(1.0, remaining / total))
    w = int(pct * 100)

    stage = int(remaining // 30)  # 0~5
    gauge_cls = f"p7-hud-gauge stage{stage}"
    if remaining <= 60:
        gauge_cls += " last60"
    if remaining <= 30:
        gauge_cls += " last30"
    if remaining <= 10:
        gauge_cls += " final"

    st.markdown("""
        <div class="{gauge_cls}">
          <div class="fill" style="width:{w}%"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def format_sentences_to_paragraph(sentences: List[str]) -> str:
    return " ".join(sentences)


def get_current_p7_set() -> P7Set:
    return P7_DEMO_SET


def render_step_intro(step: int):
    if step == 1:
        st.caption("Step 1 [정찰 단계] · 2문장으로 누가 / 누구에게 / 왜 쓴 글인지 먼저 스캔하는 단계입니다.")
    elif step == 2:
        st.caption("Step 2 [분석 단계] · 5문장으로 회사·사람·제품·날짜·요청 등 구체 정보를 정리하는 단계입니다.")
    else:
        st.caption("Step 3 [최종 전투] · 8문장 전체를 바탕으로 관계·의도·암시·추론을 잡아내는 단계입니다.")



def render_p7_step(step: int):
    current_set = get_current_p7_set()
    if step == 1:
        data = current_set.step1
    elif step == 2:
        data = current_set.step2
    else:
        data = current_set.step3

    # ✅ STEP 색(1/2/3) — 정적 테두리(확실히)용
    # Step1=SKY, Step2=PURPLE, Step3=AMBER(FINAL)
    step_color = {1: '#38BDF8', 2: '#A78BFA', 3: '#FBBF24'}.get(step, '#38BDF8')
    step_glow  = {1: 'rgba(56,189,248,0.35)', 2: 'rgba(167,139,250,0.32)', 3: 'rgba(251,191,36,0.30)'}.get(step, 'rgba(56,189,248,0.35)')

    # --- Battlefield cards (passage / question) ---

    # --- TEXT MEGA FORCE (V5, size guaranteed) ---
    st.markdown(r"""
    <style>
      /* P7_TEXT_MEGA_FORCE_V5_FINAL */

      /* ✅ 1) P7 본문 영역 기본 폰트 크기 자체를 올려버림(상속 기반) */
      .p7-zone{
        font-size: 30px !important;
        font-weight: 900 !important;
        line-height: 1.65 !important;
      }

      /* ✅ 2) Streamlit 텍스트 컨테이너들(진짜 표적) 전부 타격 */
      .p7-zone div[data-testid="stMarkdownContainer"],
      .p7-zone div[data-testid="stMarkdownContainer"] *{
        font-size: 30px !important;
        font-weight: 900 !important;
        line-height: 1.65 !important;
      }

      .p7-zone div[data-testid="stText"],
      .p7-zone div[data-testid="stText"] *{
        font-size: 30px !important;
        font-weight: 900 !important;
        line-height: 1.65 !important;
      }

      .p7-zone div[data-testid="stTextContent"],
      .p7-zone div[data-testid="stTextContent"] *{
        font-size: 30px !important;
        font-weight: 900 !important;
        line-height: 1.65 !important;
      }

      /* ✅ 3) 혹시 p 태그로 떨어지는 경우 */
      .p7-zone p, .p7-zone span, .p7-zone li{
        font-size: 30px !important;
        font-weight: 900 !important;
        line-height: 1.65 !important;
      }

      /* ✅ 4) 선택지(라디오) 글자: 더 크게 */
      .p7-zone div[role="radiogroup"] label,
      .p7-zone div[role="radiogroup"] label *{
        font-size: 1.55em !important;
        font-weight: 900 !important;
        line-height: 1.35 !important;
      }

      /* ✅ 5) 모바일에서 한 단계 더 크게 */
      @media (max-width: 520px){
        .p7-zone,
        .p7-zone div[data-testid="stMarkdownContainer"],
        .p7-zone div[data-testid="stMarkdownContainer"] *,
        .p7-zone div[data-testid="stText"],
        .p7-zone div[data-testid="stText"] *,
        .p7-zone div[data-testid="stTextContent"],
        .p7-zone div[data-testid="stTextContent"] *,
        .p7-zone p, .p7-zone span, .p7-zone li{
          font-size: 32px !important;
          font-weight: 900 !important;
        }

        .p7-zone div[role="radiogroup"] label,
        .p7-zone div[role="radiogroup"] label *{
          font-size: 2.0em !important;
          font-weight: 900 !important;
        }
      }
    </style>
    """, unsafe_allow_html=True)
        # === P7_CUM_SENTENCES_SAFE_V4 (2→5→8 cumulative render / RENDER ONLY) ===
    s1 = list(getattr(current_set.step1, "sentences", []) or [])
    s2 = list(getattr(current_set.step2, "sentences", []) or [])
    s3 = list(getattr(current_set.step3, "sentences", []) or [])

    if step == 1:
        # === P7_CUMULATIVE_ALLSENTS_V1 (2->5->8 GUARANTEED) ===
        # step3가 '+3문장만' 들고 있어도 all_sentences_en(8문장 완성본)으로 누적을 보장합니다.
        all_master = list(getattr(current_set, 'all_sentences_en', []) or [])
        if not all_master:
            # fallback: unique merge
            all_master=[]
            for part in (s1, s2, s3):
                for sent in (part or []):
                    if sent not in all_master:
                        all_master.append(sent)
        need = 2 if step == 1 else (5 if step == 2 else 8)
        cum_sentences = all_master[:need]
        # === /P7_CUMULATIVE_ALLSENTS_V1 ===
    elif step == 2:
        cum_sentences = s1 + s2
    else:
        cum_sentences = s1 + s2 + s3

    cum_text = " ".join([str(x) for x in cum_sentences])
    cum_text = cum_text.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

        # === P7_CUM_SENTENCES_SAFE_V4 (2→5→8 cumulative render / RENDER ONLY / P7V4_PARSE_20260205_083643) ===
    s1 = list(getattr(current_set.step1, "sentences", []) or [])
    s2 = list(getattr(current_set.step2, "sentences", []) or [])
    s3 = list(getattr(current_set.step3, "sentences", []) or [])

    if step == 1:
        cum_sentences = s1
    elif step == 2:
        cum_sentences = s1 + s2
    else:
        cum_sentences = s1 + s2 + s3

    cum_text = " ".join([str(x) for x in cum_sentences])
    cum_text = cum_text.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

    st.markdown("""
        <div style='padding:10px 12px;margin:10px 0;border:3px solid #ff2d2d;border-radius:14px;background:rgba(255,45,45,.12);font-weight:900;font-size:18px;'>✅ P7 HTML PROBE HIT: P7_HTML_PROBE_20260205_084552</div>\n<div style='padding:10px 12px;margin:10px 0;border:3px solid #ff2d2d;border-radius:14px;background:rgba(255,45,45,.12);font-weight:900;font-size:18px;'>✅ P7 PASSAGE PROBE HIT: P7_BUILD_20260205_145812</div>\n<div class='p7-zone intel p7-step' data-build='P7V4_PARSE_20260205_083643' style='--p7-step-color:{step_color}; --p7-step-glow:{step_glow};'>
          <div style="opacity:.85;font-weight:900;font-size:12px;margin-bottom:6px;">BUILD: P7V4_PARSE_20260205_083643</div>
          <div class='p7-zone-body p7-textboost' style="font-size:clamp(26px,5.4vw,38px);font-weight:900;line-height:1.65;letter-spacing:0.1px">{cum_text}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


    st.markdown("""
        <div class='p7-zone mission p7-step' style='--p7-step-color:{step_color}; --p7-step-glow:{step_glow};'>
          <div class='p7-zone-body p7-textboost' style="font-size:clamp(26px,5.4vw,38px);font-weight:900;line-height:1.65;letter-spacing:0.1px">{(data.question_en).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


    # --- Options: tap = submit (A안: radio card + 즉시 제출) ---
    st.markdown(r"""
    <style>
      /* P7_OPTION_RADIO_CARDS_V1 */
      .stRadio > label{ display:none !important; }
      div[role="radiogroup"]{ gap: 0 !important; }
      div[role="radiogroup"] > label{
        width: 100% !important;
        border-radius: 18px !important;
        border: 1px solid rgba(255,255,255,0.18) !important;
        background: rgba(255,255,255,0.96) !important;
        padding: 16px 16px !important;
        margin: 6px 0 !important;
        box-shadow: 0 12px 26px rgba(0,0,0,0.18) !important;
        transition: transform .10s ease, filter .10s ease, box-shadow .10s ease !important;
      }
      div[role="radiogroup"] > label *{
        font-size: 1.32em !important;
        font-weight: 950 !important;
        color:#000000 !important;
        opacity:1 !important;
        -webkit-text-fill-color:#000000 !important;
      }
      div[role="radiogroup"] > label:hover{
        transform: translateY(-1px);
        filter: brightness(1.03);
        box-shadow: 0 16px 34px rgba(0,0,0,0.24) !important;
      }
      /* 선택됨(락온) */
      div[role="radiogroup"] > label:has(input:checked){
        background: linear-gradient(135deg, rgba(34,211,238,0.92), rgba(167,139,250,0.88)) !important;
        border-color: rgba(255,255,255,0.22) !important;
      }
      div[role="radiogroup"] > label:has(input:checked) *{ color:#ffffff !important; -webkit-text-fill-color:#ffffff !important; }
    
      /*  */
      /* ✅ 지문/문제 카드 글자: 무조건 크게/진하게 (최후 적용) */
      .p7-zone .p7-zone-body,
      .p7-zone .p7-zone-body *{
        font-size: 30px !important;
        font-weight: 900 !important;
        line-height: 1.55 !important;
        letter-spacing: 0.10px !important;
      }
      @media (max-width: 520px){
        .p7-zone .p7-zone-body,
        .p7-zone .p7-zone-body *{
          font-size: 26px !important;
          font-weight: 900 !important;
        }
      }

      /* ✅ 선택지(라디오 카드) 글자도 최후 재강제 */
      div[role="radiogroup"] > label *{
        font-size: 1.25em !important;
        font-weight: 900 !important;
      }
/* ===== P7_RADIO_FLAT_FINAL_v3 ===== */
.p7-zone div[role="radiogroup"] > label{
  padding: 10px 12px !important;
  margin: 10px 0 !important;
  min-height: 52px !important;
}
.p7-zone div[role="radiogroup"] > label *{
  font-size: 30px !important;
  font-weight: 900 !important;
  line-height: 1.25 !important;
}
/* ===== /P7_RADIO_FLAT_FINAL_v3 ===== */
</style>
    """, unsafe_allow_html=True)

    key_choice = f"p7_choice_{step}"
    if key_choice not in st.session_state:
        st.session_state[key_choice] = None

    choice = st.radio(
        label="",
        options=data.options_en,
        index=None,
        key=key_choice,
        label_visibility="collapsed",
    )

    if choice is not None:
        chosen_index = data.options_en.index(choice)
        evaluate_step(step, chosen_index, data)

        # 정답이면 다음 스텝 / 오답이면 MISS 누적만 하고 계속
        if chosen_index == data.answer_index:
            if step < 3:
                max_reached = st.session_state.get("p7_max_step_reached", 0)
                st.session_state["p7_max_step_reached"] = max(max_reached, step + 1)
                st.session_state["p7_current_step"] = step + 1
            else:
                st.session_state["p7_has_finished"] = True
        else:
            if int(st.session_state.get("p7_miss_count", 0)) >= 3:
                st.session_state["p7_has_finished"] = True

        # 다음 문제에서 라디오 선택 초기화
        st.session_state[key_choice] = None
        st.rerun()
    return data


def evaluate_step(step: int, chosen_index: int, data: StepData):
    is_correct = (chosen_index == data.answer_index)

    # === C1_MISSCOUNT_APPLIED_CORE ===
    if not is_correct:
        st.session_state.p7_miss_count = int(st.session_state.get("p7_miss_count", 0)) + 1
    # === C1_MISSCOUNT_APPLIED ===
    if not is_correct:
        st.session_state.p7_miss_count = int(st.session_state.get("p7_miss_count", 0)) + 1
    add_combo(is_correct)

    result = P7Result(
        step=step,
        is_correct=is_correct,
        user_choice=chosen_index,
        correct_choice=data.answer_index,
    )

    results_list: List[P7Result] = st.session_state.p7_results
    replaced = False
    for i, r in enumerate(results_list):
        if r.step == step:
            results_list[i] = result
            replaced = True
            break
    if not replaced:
        results_list.append(result)
    st.session_state.p7_results = results_list

    # 단어 후보 모으기 (정오답 관계없이)
    step_vocab_candidates: List[Dict] = []
    if step == 1:
        step_vocab_candidates = [
            {"word": "relocate", "meaning": "이전하다, 옮기다", "source": "P7-Step1"},
            {"word": "inform", "meaning": "알리다, 통지하다", "source": "P7-Step1"},
        ]
    elif step == 2:
        step_vocab_candidates = [
            {"word": "effective", "meaning": "시행되는, 유효한", "source": "P7-Step2"},
            {"word": "upgrade", "meaning": "업그레이드하다, 개선하다", "source": "P7-Step2"},
        ]
    else:
        step_vocab_candidates = [
            {"word": "transition", "meaning": "전환, 변화", "source": "P7-Step3"},
            {"word": "assist", "meaning": "돕다, 지원하다", "source": "P7-Step3"},
            {"word": "temporary", "meaning": "일시적인", "source": "P7-Step3"},
        ]

    pool: List[Dict] = st.session_state.get("p7_vocab_candidates", [])
    for item in step_vocab_candidates:
        if not any(v["word"] == item["word"] for v in pool):
            pool.append(item)
    st.session_state.p7_vocab_candidates = pool


def _add_vocab_to_armory(word: str, meaning: str, source: str = "P7", sentence: str | None = None):
    """
    ✅ P7 VOCA 저장(핵심):
    - 기존 동작(세션 내 단어무기고 리스트 유지)은 그대로
    - 추가로 app/data/armory/secret_armory.json 에 'p7_vocab' 포맷으로 영구 저장
      -> Secret Armory(별도 파일) VOCA 저장고가 바로 이 포맷만 안정적으로 인식
    """
    # 1) 기존: 세션 내 단어 무기고 유지(이 파일 내부 UX 유지)
    vocab_list: List[Dict] = st.session_state.secret_armory_vocab
    for v in vocab_list:
        if v.get("word") == word and v.get("meaning") == meaning:
            break
    else:
        vocab_list.append({"word": word, "meaning": meaning, "source": source, "sentence": sentence} if sentence else {"word": word, "meaning": meaning, "source": source})
        st.session_state.secret_armory_vocab = vocab_list

    # 2) ✅ 영구 저장: Secret Armory 공용 JSON에 p7_vocab 형태로 추가
    try:
        # 표준 저장 모듈이 있으면 그걸 우선 사용
        from app.core.armory_store import append_p7_vocab  # type: ignore
        append_p7_vocab(str(word), str(meaning), extra={"source": "P7", **({"sentence": str(sentence).strip()} if isinstance(sentence, str) and str(sentence).strip() else {})})
        return
    except Exception:
        pass

    # fallback: 직접 JSON에 추가 (모듈이 없거나 import 실패 시)
    try:
        from pathlib import Path
        import json

        armory_path = Path("app/data/armory/secret_armory.json")
        if armory_path.exists():
            raw = json.loads(armory_path.read_text(encoding="utf-8-sig"))
        else:
            raw = []

        items = raw if isinstance(raw, list) else raw.get("items", [])
        if not isinstance(items, list):
            items = []

        word_s = (str(word) if word is not None else "").strip()
        meaning_s = (str(meaning) if meaning is not None else "").strip()
        if not word_s or not meaning_s:
            return

        # 중복 방지
        for it in items:
            if (
                isinstance(it, dict)
                and it.get("mode") == "p7_vocab"
                and it.get("word") == word_s
                and it.get("meaning") == meaning_s
            ):
                return

        items.append({
            "source": "P7",
            "mode": "p7_vocab",
            "word": word_s,
            "meaning": meaning_s,
            **({"sentence": str(sentence).strip()} if isinstance(sentence, str) and str(sentence).strip() else {}),
        })

        armory_path.parent.mkdir(parents=True, exist_ok=True)
        armory_path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

    except Exception:
        # 저장 실패해도 전투 진행은 막지 않음(UX 보호)
        return


def _add_p5_to_armory(problem: P5Problem):
    p5_list: List[P5Problem] = st.session_state.secret_armory_p5
    for p in p5_list:
        if p.problem_id == problem.problem_id:
            return
    p5_list.append(problem)
    st.session_state.secret_armory_p5 = p5_list

# ============================================
# P7 결과 / 해설 / 단어 저장 + 레벨업
# ============================================

def render_p7_feedback():
    # === RESULT / FEEDBACK SCREEN (neon skin: purple + cyan) ===
    st.markdown(
        """
        <style>
        /* tighten vertical gaps on the debrief screen */
        .block-container { padding-top: 1.0rem; padding-bottom: 2.0rem; }
        h1, h2, h3 { margin-top: 0.2rem !important; margin-bottom: 0.5rem !important; }

        /* Neon card vibe (purple + cyan) */
        .p7-neon-banner {
            border: 1px solid rgba(140, 120, 255, 0.35);
            background: linear-gradient(90deg, rgba(120, 90, 255, 0.10), rgba(0, 255, 255, 0.07));
            border-radius: 14px;
            padding: 10px 14px;
            box-shadow:
                0 0 0 1px rgba(0, 255, 255, 0.10) inset,
                0 0 18px rgba(120, 90, 255, 0.10),
                0 0 18px rgba(0, 255, 255, 0.08);
        }

        /* Metrics: smaller + boxed */
        div[data-testid="stMetric"] {
            border: 1px solid rgba(0, 255, 255, 0.18);
            border-radius: 14px;
            padding: 8px 10px;
            background: rgba(10, 15, 25, 0.02);
            box-shadow: 0 0 14px rgba(0, 255, 255, 0.06);
        }
        div[data-testid="stMetricValue"] { font-size: 2.0rem !important; }
        div[data-testid="stMetricLabel"] { font-size: 0.95rem !important; opacity: 0.9; }

        /* Expanders: neon outline */
        div[data-testid="stExpander"] {
            border: 1px solid rgba(120, 90, 255, 0.32) !important;
            border-radius: 16px !important;
            box-shadow: 0 0 16px rgba(120, 90, 255, 0.12), 0 0 12px rgba(0, 255, 255, 0.08);
        }
        div[data-testid="stExpander"] > details {
            border-radius: 16px !important;
        }

        /* Reduce extra whitespace around dividers */
        hr { margin: 0.8rem 0 !important; opacity: 0.25; }
        
/* =========================================================
   P7 FULL WIDTH + ONE-LINE HUD (NO columns) + TIME PRESSURE
   ========================================================= */
.block-container{
  max-width: 100% !important;
  padding-left: 0.85rem !important;
  padding-right: 0.85rem !important;
  padding-top: 0.25rem !important;
}

/* HUD: 한 줄 FLEX (오른쪽 빈 공간 방지) */
.p7-hudbar{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 18px;
  background: rgba(255,255,255,0.18);
  border: 1px solid rgba(255,255,255,0.20);
  box-shadow: 0 10px 30px rgba(0,0,0,0.12);
  margin: 0 0 10px 0;
}
.p7-hud-left{
  display:flex;
  align-items:center;
  gap: 10px;
  flex-wrap: wrap;
}
.p7-hud-right{
  display:flex;
  align-items:center;
  justify-content:flex-end;
  gap: 8px;
}

/* MAIN HUB 버튼: HUD 높이에 맞춰 compact */
.p7-hud-right div[data-testid="stButton"] > button{
  padding: 10px 12px !important;
  border-radius: 14px !important;
  font-weight: 900 !important;
  line-height: 1.0 !important;
  border: 1px solid rgba(0,0,0,0.06) !important;
}

/* CHIP size 타이트 */
.p7-chip{ padding: 6px 10px !important; font-size: 12.8px !important; }
.p7-chip b{ font-size: 13.8px !important; }

/* TIME 압박 효과 */
.p7-time-chip{ display:inline-flex; align-items:center; gap:8px; }
.p7-time-svg{ width:18px; height:18px; display:inline-block; vertical-align:middle; }

@keyframes p7Pulse60 { 0%{transform:scale(1)} 50%{transform:scale(1.12)} 100%{transform:scale(1)} }
@keyframes p7Pulse30 { 0%{transform:scale(1)} 50%{transform:scale(1.18)} 100%{transform:scale(1)} }
@keyframes p7Shake10 {
  0%{transform:translateX(0)}
  20%{transform:translateX(-1px)}
  40%{transform:translateX(1px)}
  60%{transform:translateX(-1px)}
  80%{transform:translateX(1px)}
  100%{transform:translateX(0)}
}

.p7-chip.p7-time-danger{
  background: rgba(255,45,45,0.18) !important;
  border-color: rgba(255,45,45,0.35) !important;
  box-shadow: 0 0 14px rgba(255,45,45,0.15) !important;
}
.p7-time-danger .p7-time-svg{
  filter: drop-shadow(0 0 7px rgba(255,45,45,.55));
  animation: p7Pulse60 .9s ease-in-out infinite;
}

.p7-chip.p7-time-critical{
  background: rgba(255,45,45,0.26) !important;
  border-color: rgba(255,45,45,0.48) !important;
  box-shadow: 0 0 18px rgba(255,45,45,0.22) !important;
}
.p7-time-critical .p7-time-svg{
  filter: drop-shadow(0 0 9px rgba(255,45,45,.65));
  animation: p7Pulse30 .75s ease-in-out infinite;
}

.p7-chip.p7-time-final{
  animation: p7Shake10 .35s linear infinite;
}

/* --- P7 HUD MAIN HUB (HTML button) --- */
.p7-hub-btn{
  padding: 10px 14px;
  border-radius: 14px;
  font-weight: 900;
  border: 1px solid rgba(0,0,0,0.08);
  background: rgba(255,255,255,0.92);
  cursor: pointer;
  line-height: 1.0;
}
.p7-hub-btn:hover{
  background: rgba(255,255,255,1.0);
  transform: translateY(-1px);
}

/* === P7 밀도 패치: HUD ↔ 지문 간격 축소 === */
.p7-hudbar{
  margin-bottom: 8px !important;
  padding-bottom: 6px !important;
}

/* HUD 바로 아래 첫 지문 카드 */
.p7-passage-card,
.p7-reading-card,
.p7-passage{
  margin-top: 6px !important;
  padding-top: 14px !important;
}

/* === 지문 글씨 가독성 업 (1.3배) === */
.p7-passage-text,
.p7-reading-text{
  font-size: 1.3rem !important;
  line-height: 1.6 !important;
}

/* =========================================================
   P7 B-2 OPTIONS (Card Buttons)
   - p7-opt-wrap 안의 버튼만 통일
   ========================================================= */
.p7-opt-wrap{
  display: grid;
  gap: 14px;
  margin-top: 10px;
}

/* ✅ 핵심: 모든 선택지 버튼 "같은 높이" */
.p7-opt-wrap div[data-testid="stButton"] > button{
  width: 100% !important;

  /* 높이 통일 */
  min-height: 74px !important;

  /* 터치감 */
  padding: 18px 18px !important;
  border-radius: 18px !important;
  font-size: 30px !important;
  font-weight: 800 !important;
  line-height: 1.25 !important;

  /* 카드 느낌 */
  background: rgba(255,255,255,0.98) !important;
  border: 1px solid rgba(255,255,255,0.25) !important;
  box-shadow: 0 10px 28px rgba(0,0,0,0.14) !important;

  /* 긴 문장도 보기 좋게 */
  white-space: normal !important;
  text-align: center !important;

  /* 반응성 */
  transition: transform .08s ease, box-shadow .08s ease, filter .08s ease;
}

/* Hover = "타겟 락온" 느낌 */
.p7-opt-wrap div[data-testid="stButton"] > button:hover{
  transform: translateY(-1px);
  box-shadow: 0 14px 32px rgba(0,0,0,0.18) !important;
  filter: brightness(1.02);
}

/* Press = "LOCK IN" */
.p7-opt-wrap div[data-testid="stButton"] > button:active{
  transform: translateY(1px) scale(0.995);
  box-shadow: 0 8px 18px rgba(0,0,0,0.12) !important;
}

/* 모바일에서 더 잘 눌리게(폭 좁으면 높이 조금 증가) */
@media (max-width: 640px){
  .p7-opt-wrap div[data-testid="stButton"] > button{
    min-height: 82px !important;
    font-size: 17px !important;
    padding: 18px 16px !important;
  }
}

/* =========================================================
   P7 B-3 TIME PRESSURE
   ========================================================= */

.p7-time-chip{
  font-weight: 900 !important;
  transition: all .15s ease;
}

/* 60s ↓ WARNING */
.p7-time-warn{
  background: #ffcc00 !important;
  color: #1a1a1a !important;
}

/* 30s ↓ DANGER */
.p7-time-danger{
  background: #ff3b3b !important;
  color: #fff !important;
  animation: p7-blink .8s infinite;
}

@keyframes p7-blink{
  0%{filter:brightness(1)}
  50%{filter:brightness(1.25)}
  100%{filter:brightness(1)}
}

/* 15s ↓ SCREEN VIGNETTE */
.p7-vignette{
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9999;
  box-shadow: inset 0 0 120px rgba(255,0,0,.45);
  animation: p7-pulse 1.2s infinite;
}

@keyframes p7-pulse{
  0%{box-shadow: inset 0 0 80px rgba(255,0,0,.35)}
  50%{box-shadow: inset 0 0 140px rgba(255,0,0,.55)}
  100%{box-shadow: inset 0 0 80px rgba(255,0,0,.35)}
}

/* =========================
   P7 HUD ONE-LINE + TIME PRESSURE + VIGNETTE (FINAL)
   ========================= */
.p7-hudbar{
  display:flex; align-items:center; justify-content:space-between; gap:10px;
  padding:8px 10px; border-radius:18px;
  background: rgba(255,255,255,0.10);
  border: 1px solid rgba(255,255,255,0.14);
  box-shadow: 0 10px 26px rgba(0,0,0,0.20);
  backdrop-filter: blur(10px);
  margin: 0 0 8px 0;
}
.p7-hud-left{ display:flex; align-items:center; gap:10px; flex-wrap:wrap; }
.p7-hud-right{ display:flex; align-items:center; justify-content:flex-end; }

.p7-hub-btn{
  padding:10px 14px; border-radius:14px; font-weight:900;
  border: 1px solid rgba(0,0,0,0.10);
  background: rgba(255,255,255,0.95);
  cursor:pointer; line-height:1.0;
}
.p7-hub-btn:hover{ transform: translateY(-1px); background:#fff; }

.p7-time-chip{ display:inline-flex; align-items:center; gap:8px; }
.p7-time-svg{ width:18px; height:18px; display:inline-block; vertical-align:middle; }

/* 60s ↓ warning(노랑) */
.p7-time-warn{ background: rgba(255,204,0,0.22) !important; border-color: rgba(255,204,0,0.45) !important; }
/* 30s ↓ danger(빨강 + 깜빡) */
@keyframes p7Blink{ 0%{filter:brightness(1)} 50%{filter:brightness(1.25)} 100%{filter:brightness(1)} }
.p7-time-danger2{ background: rgba(255,45,45,0.22) !important; border-color: rgba(255,45,45,0.55) !important; animation: p7Blink .85s infinite; }
/* 10s ↓ final(흔들림) */
@keyframes p7Shake10{
  0%{transform:translateX(0)} 20%{transform:translateX(-1px)} 40%{transform:translateX(1px)}
  60%{transform:translateX(-1px)} 80%{transform:translateX(1px)} 100%{transform:translateX(0)}
}
.p7-time-final2{ animation: p7Shake10 .35s linear infinite; }

/* 15s ↓ 비네팅 */
.p7-vignette{
  position: fixed; inset: 0; pointer-events:none; z-index: 9999;
  box-shadow: inset 0 0 140px rgba(255,0,0,.45);
  animation: p7Vig 1.1s infinite;
}
@keyframes p7Vig{
  0%{box-shadow: inset 0 0 90px rgba(255,0,0,.32)}
  50%{box-shadow: inset 0 0 170px rgba(255,0,0,.55)}
  100%{box-shadow: inset 0 0 90px rgba(255,0,0,.32)}
}

/* =========================
   P7 C-1 WRONG PRESSURE FX
   ========================= */
@keyframes p7Heart{
  0%{transform:scale(1); filter:brightness(1)}
  20%{transform:scale(1.02); filter:brightness(1.05)}
  40%{transform:scale(0.995); filter:brightness(1)}
  60%{transform:scale(1.03); filter:brightness(1.08)}
  100%{transform:scale(1); filter:brightness(1)}
}
@keyframes p7ScreenShake2{
  0%{transform:translate(0,0)}
  20%{transform:translate(-2px,0)}
  40%{transform:translate(2px,0)}
  60%{transform:translate(-2px,1px)}
  80%{transform:translate(2px,-1px)}
  100%{transform:translate(0,0)}
}
@keyframes p7ScreenShake3{
  0%{transform:translate(0,0)}
  10%{transform:translate(-3px,1px)}
  20%{transform:translate(3px,-1px)}
  30%{transform:translate(-3px,0)}
  40%{transform:translate(3px,1px)}
  50%{transform:translate(-2px,-1px)}
  60%{transform:translate(2px,1px)}
  70%{transform:translate(-3px,0)}
  80%{transform:translate(3px,-1px)}
  90%{transform:translate(-2px,1px)}
  100%{transform:translate(0,0)}
}

/* 화면 전체에 걸리는 오버레이(전장 압박) */
.p7-wrongfx{
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9998;
}

/* 오답 2회: 심장박동 + 약한 흔들림 */
.p7-wrongfx.w2{
  animation:
    p7Heart 0.9s ease-in-out infinite,
    p7ScreenShake2 0.55s linear infinite;
}

/* 오답 3회: 더 강한 흔들림 */
.p7-wrongfx.w3{
  animation:
    p7Heart 0.75s ease-in-out infinite,
    p7ScreenShake3 0.45s linear infinite;
}

/* HUD 안 MISS 칩도 같이 붉게(시선 고정) */
.p7-miss-danger{
  background: rgba(255,45,45,0.20) !important;
  border-color: rgba(255,45,45,0.50) !important;
  box-shadow: 0 0 16px rgba(255,45,45,0.18) !important;
}

/* =========================
   P7 TOP GAP FIX (hide top panel)
   ========================= */

/* 1) 페이지 최상단 여백 제거 */
.block-container{
  padding-top: 0.2rem !important;
}

/* 2) 지문 위에 남아있는 큰 패널/빈 컨테이너를 압축
   - Streamlit이 만든 빈 element container가 위를 차지하는 경우가 많아서
     p7에서만 안전하게 '높이/패딩'을 줄임
*/
.p7-top-panel,
.p7-prepanel,
.p7-stage-panel,
.p7-upper-panel{
  display: none !important;
}

/* 3) 혹시 클래스가 없더라도, "p7-hudbar 위에 남는 첫 큰 박스"를 줄이기
   - main 영역 초반 container들이 과하게 커지는 상황 대응
*/
main .block-container > div:first-child{
  margin-top: 0 !important;
  padding-top: 0 !important;
}

/* 4) HUD 바로 아래부터 본문이 붙도록 */
.p7-hudbar{ margin-bottom: 6px !important; }

/* =========================
   A-HUDBAR-HARD-FIX
   - 상단 HUD가 '큰 패널'처럼 커지는 현상 방지
   ========================= */
.p7-hudbar{
  max-height: 64px !important;
  overflow: hidden !important;
}
.p7-hud-left, .p7-hud-right{
  align-items: center !important;
}
.p7-hudbar *{
  line-height: 1.0 !important;
}
main .block-container{
  padding-top: 0.10rem !important;
}

/* =========================
   A-HUD-VISIBILITY-FIX
   - HUD 바/칩/텍스트가 '하얀 바' 위에서 안 보이는 문제 강제 해결
   ========================= */
.p7-hudbar{
  background: rgba(0,0,0,0.22) !important;
  border: 1px solid rgba(255,255,255,0.18) !important;
  box-shadow: 0 10px 26px rgba(0,0,0,0.22) !important;
  color: #ffffff !important;
}
.p7-hudbar *{
  color: #ffffff !important;
  opacity: 1 !important;
  filter: none !important;
  text-shadow: 0 2px 6px rgba(0,0,0,0.55) !important;
}

/* HUD 칩들( STEP / TIME / MISS / COMBO ) */
.p7-chip{
  background: rgba(0,0,0,0.35) !important;
  border: 1px solid rgba(255,255,255,0.20) !important;
  color: #ffffff !important;
}
.p7-chip b{ color:#ffffff !important; }

/* TIME 칩 내부 SVG 링도 확실히 보이게 */
.p7-time-svg circle{
  opacity: 1 !important;
}

/* MAIN HUB 버튼(HTML)도 대비 확보 */
.p7-hub-btn{
  background: rgba(255,255,255,0.92) !important;
  color: #111111 !important;
  border: 1px solid rgba(0,0,0,0.12) !important;
}
.p7-hub-btn:hover{
  background: rgba(255,255,255,1.0) !important;
}
/* =========================================================
   P7 TIME ONLY — "HEART-CLENCH" PATCH (C-1)
   ========================================================= */
.p7-time-chip{position:relative;font-weight:950!important;letter-spacing:.02em;}
.p7-time-chip b{display:inline-block;letter-spacing:.06em;animation:p7TimeTick 1s steps(1) infinite;}
.p7-time-chip,.p7-time-chip b,.p7-time-chip .p7-time-svg{
 transition:filter .15s,transform .15s,box-shadow .15s,background .15s;
}
@keyframes p7TimeTick{0%{transform:translateY(0)}35%{transform:translateY(-.6px)}70%{transform:translateY(0)}}
@keyframes p7TimeBeat60{
 0%{transform:scale(1)}35%{transform:scale(1.04)}70%{transform:scale(1)}
}
@keyframes p7TimeBeat30{
 0%{transform:scale(1)}
 18%{transform:scale(1.06)}
 30%{transform:scale(.995)}
 52%{transform:scale(1.075)}
 70%{transform:scale(1)}
}
@keyframes p7TimeJitter10{
 0%{transform:translateX(0)}
 20%{transform:translateX(-.8px)}
 40%{transform:translateX(.8px)}
 60%{transform:translateX(-.6px)}
 80%{transform:translateX(.6px)}
}
@keyframes p7RingGlow{
 0%{filter:drop-shadow(0 0 5px rgba(255,45,45,.25))}
 50%{filter:drop-shadow(0 0 11px rgba(255,45,45,.65))}
 100%{filter:drop-shadow(0 0 5px rgba(255,45,45,.25))}
}
.p7-time-warn b{
 animation:p7TimeTick 1s steps(1) infinite,p7TimeBeat60 1.15s infinite;
}
.p7-time-danger2 b{
 animation:p7TimeBeat30 .78s infinite;
 text-shadow:0 0 10px rgba(255,45,45,.2);
}
.p7-time-danger2 .p7-time-svg{
 animation:p7TimeBeat30 .78s infinite,p7RingGlow .78s infinite;
}
.p7-time-final2{
 animation:p7TimeJitter10 .33s linear infinite;
}
.p7-time-final2 b{
 animation:p7TimeBeat30 .62s infinite;
}
/* ===== P7 TIME ONLY: ALWAYS-ON "ALIVE" (SAFE) ===== */
@keyframes p7AliveTick { 0%{transform:translateY(0)} 35%{transform:translateY(-0.6px)} 70%{transform:translateY(0)} 100%{transform:translateY(0)} }
@keyframes p7AlivePulse { 0%{transform:scale(1)} 40%{transform:scale(1.02)} 80%{transform:scale(1)} 100%{transform:scale(1)} }

.p7-time-alive{
  animation: p7AlivePulse 1.6s ease-in-out infinite;
}
.p7-time-alive .p7-time-svg{
  animation: p7AlivePulse 1.6s ease-in-out infinite;
}
.p7-time-alive *{
  /* 숫자 텍스트가 어떤 태그여도 미세 tick이 먹게 */
  animation: p7AliveTick 1s steps(1) infinite;
}
/* ===== EXECUTION CHECK WATERMARK ===== */
.p7-exec-check::after{
  content:" ⛔LIVE ";
  color:#ff2d2d;
  font-weight:900;
  margin-left:8px;
  animation:p7ExecBlink .8s steps(1) infinite;
}
@keyframes p7ExecBlink{
  0%{opacity:1}
  50%{opacity:.2}
  100%{opacity:1}
}
/* ===== P7 TIME FINAL HEART-CLENCH ===== */

@keyframes p7PulseSoft {
  0%{
    transform:scale(1);
    filter:brightness(1);
    box-shadow: 0 0 0 1px rgba(255,255,255,.10) inset, 0 0 10px rgba(160,140,255,.10);
  }
  50%{
    transform:scale(1.03);
    filter:brightness(1.10);
    box-shadow: 0 0 0 1px rgba(255,255,255,.16) inset, 0 0 18px rgba(160,140,255,.22);
  }
  100%{
    transform:scale(1);
    filter:brightness(1);
    box-shadow: 0 0 0 1px rgba(255,255,255,.10) inset, 0 0 10px rgba(160,140,255,.10);
  }
}



@keyframes p7Beat60 {
  0%{transform:scale(1)}
  40%{transform:scale(1.04)}
  100%{transform:scale(1)}
}

@keyframes p7Beat30 {
  0%{transform:scale(1)}
  20%{transform:scale(1.06)}
  40%{transform:scale(.99)}
  60%{transform:scale(1.075)}
  100%{transform:scale(1)}
}

@keyframes p7Shake10 {
  0%{transform:translateX(0)}
  25%{transform:translateX(-1px)}
  50%{transform:translateX(1px)}
  75%{transform:translateX(-0.8px)}
  100%{transform:translateX(0)}
}

/* always alive */
.p7-time-chip{
  animation:p7PulseSoft 1.8s ease-in-out infinite;
}

/* C-1 ≤60s */
.p7-time-warn{
  animation:p7Beat60 1.1s infinite;
}

/* C-2 ≤30s */
.p7-time-danger{
  animation:p7Beat30 .75s infinite;
  filter:drop-shadow(0 0 10px rgba(255,60,60,.45));
}

/* C-3 ≤10s */
.p7-time-final{
  animation:p7Shake10 .28s linear infinite;
  filter:drop-shadow(0 0 18px rgba(255,40,40,.85));
}
/* =========================================================
   P7 TIME FINAL TUNING v2 (MATCH CLASS NAMES)
   - TIME ONLY
   ========================================================= */

@keyframes p7PulseSoft {
  0%{
    transform:scale(1);
    filter:brightness(1);
    box-shadow: 0 0 0 1px rgba(255,255,255,.10) inset, 0 0 10px rgba(160,140,255,.10);
  }
  50%{
    transform:scale(1.03);
    filter:brightness(1.10);
    box-shadow: 0 0 0 1px rgba(255,255,255,.16) inset, 0 0 18px rgba(160,140,255,.22);
  }
  100%{
    transform:scale(1);
    filter:brightness(1);
    box-shadow: 0 0 0 1px rgba(255,255,255,.10) inset, 0 0 10px rgba(160,140,255,.10);
  }
}



@keyframes p7Beat60 {
  0%{transform:scale(1)}
  38%{transform:scale(1.05)}
  100%{transform:scale(1)}
}

@keyframes p7Beat30 {
  0%{transform:scale(1)}
  20%{transform:scale(1.06)}
  38%{transform:scale(.99)}
  58%{transform:scale(1.085)}
  100%{transform:scale(1)}
}

@keyframes p7Shake10 {
  0%{transform:translateX(0)}
  25%{transform:translateX(-1px)}
  50%{transform:translateX(1px)}
  75%{transform:translateX(-0.8px)}
  100%{transform:translateX(0)}
}

/* 항상: "살아있음" (눈에 보이게 조금 더) */
.p7-time-chip{
  animation: p7PulseSoft 1.6s ease-in-out infinite !important;
}

/* 60초↓: C-1 */
.p7-time-warn{
  animation: p7Beat60 1.05s ease-in-out infinite !important;
  box-shadow: 0 0 0 1px rgba(255,204,0,.18) inset, 0 0 18px rgba(255,204,0,.10) !important;
}

/* 30초↓: C-2 (du-dum) */
.p7-time-danger2{
  animation: p7Beat30 .74s ease-in-out infinite !important;
  filter: drop-shadow(0 0 10px rgba(255,60,60,.45)) !important;
  box-shadow: 0 0 0 1px rgba(255,60,60,.20) inset, 0 0 26px rgba(255,60,60,.16) !important;
}

/* 10초↓: C-3 (TIME 칩만 떨림) */
.p7-time-final2{
  animation: p7Shake10 .26s linear infinite !important;
  filter: drop-shadow(0 0 18px rgba(255,40,40,.85)) !important;
  box-shadow: 0 0 0 1px rgba(255,40,40,.22) inset, 0 0 34px rgba(255,40,40,.22) !important;
}

/* 눈으로 확인 가능한 아주 작은 표시(개발 중만) */
.p7-time-chip::after{
  content:"";
  opacity:.0;
}
/* =========================================================
   TIME_FORCE_VISIBLE_V1  (DEBUG — remove later)
   - strongest selector + !important
   ========================================================= */

@keyframes p7TimeAliveGlowV1{
  0%{
    filter: brightness(1);
    box-shadow: 0 0 0 1px rgba(255,255,255,.12) inset,
                0 0 10px rgba(120,90,255,.18);
    background: rgba(0,0,0,0.22);
  }
  50%{
    filter: brightness(1.22);
    box-shadow: 0 0 0 1px rgba(255,255,255,.22) inset,
                0 0 22px rgba(120,90,255,.38);
    background: rgba(0,0,0,0.34);
  }
  100%{
    filter: brightness(1);
    box-shadow: 0 0 0 1px rgba(255,255,255,.12) inset,
                0 0 10px rgba(120,90,255,.18);
    background: rgba(0,0,0,0.22);
  }
}

/* ✅ 가장 강하게: HUD 안 TIME 칩(=실제 사용 영역)만 */
.p7-hudbar .p7-time-chip.p7-time-alive{
  animation: p7TimeAliveGlowV1 1.05s ease-in-out infinite !important;
  border-color: rgba(255,255,255,0.30) !important;
}

/* TIME 글자도 같이 “숨쉬게” */
.p7-hudbar .p7-time-chip.p7-time-alive b{
  animation: p7TimeAliveGlowV1 1.05s ease-in-out infinite !important;
}

/* 60/30/10 구간은 더 강하게(기존 클래스명 그대로 사용) */
.p7-hudbar .p7-time-chip.p7-time-warn{
  animation-duration: .90s !important;
}
.p7-hudbar .p7-time-chip.p7-time-danger2{
  animation-duration: .72s !important;
  box-shadow: 0 0 0 1px rgba(255,60,60,.22) inset,
              0 0 26px rgba(255,60,60,.22) !important;
}
.p7-hudbar .p7-time-chip.p7-time-final2{
  animation-duration: .55s !important;
  box-shadow: 0 0 0 1px rgba(255,40,40,.28) inset,
              0 0 34px rgba(255,40,40,.32) !important;
}
/* =========================================================
   TIME_FORCE_TUNING_V2
   - overrides TIME_FORCE_VISIBLE_V1 (last wins)
   ========================================================= */

@keyframes p7TimeAliveGlowV2{
  0%{
    filter: brightness(1.02) saturate(1.02);
    box-shadow: 0 0 0 1px rgba(255,255,255,.14) inset,
                0 0 14px rgba(120,90,255,.22);
    background: rgba(0,0,0,0.26);
  }
  50%{
    filter: brightness(1.32) saturate(1.10);
    box-shadow: 0 0 0 1px rgba(255,255,255,.26) inset,
                0 0 30px rgba(120,90,255,.46);
    background: rgba(0,0,0,0.40);
  }
  100%{
    filter: brightness(1.02) saturate(1.02);
    box-shadow: 0 0 0 1px rgba(255,255,255,.14) inset,
                0 0 14px rgba(120,90,255,.22);
    background: rgba(0,0,0,0.26);
  }
}

/* baseline (2분대에서도 "예고 경보") */
.p7-hudbar .p7-time-chip.p7-time-alive{
  animation: p7TimeAliveGlowV2 .88s ease-in-out infinite !important;
  border-color: rgba(255,255,255,0.34) !important;
}

/* text emphasis */
.p7-hudbar .p7-time-chip.p7-time-alive b{
  animation: p7TimeAliveGlowV2 .88s ease-in-out infinite !important;
}

/* C-1 <=60s : faster + warmer edge */
.p7-hudbar .p7-time-chip.p7-time-warn{
  animation-duration: .74s !important;
  box-shadow: 0 0 0 1px rgba(255,204,0,.20) inset,
              0 0 26px rgba(255,204,0,.16) !important;
}

/* C-2 <=30s : du-dum feel stronger */
.p7-hudbar .p7-time-chip.p7-time-danger2{
  animation-duration: .62s !important;
  box-shadow: 0 0 0 1px rgba(255,60,60,.24) inset,
              0 0 36px rgba(255,60,60,.28) !important;
}

/* C-3 <=10s : TIME-only jitter */
@keyframes p7TimeJitterV2{
  0%{transform:translateX(0)}
  25%{transform:translateX(-1px)}
  50%{transform:translateX(1px)}
  75%{transform:translateX(-1px)}
  100%{transform:translateX(0)}
}
.p7-hudbar .p7-time-chip.p7-time-final2{
  animation: p7TimeJitterV2 .24s linear infinite !important;
  box-shadow: 0 0 0 1px rgba(255,40,40,.30) inset,
              0 0 44px rgba(255,40,40,.34) !important;
}

        /* === P7 RESULT VISIBILITY OVERRIDE (FINAL) === */

        /* === P7 RESULT VISIBILITY OVERRIDE (FINAL) === */
        .p7-neon-banner{
            border: 1px solid rgba(140, 120, 255, 0.55) !important;
            background: linear-gradient(90deg, rgba(120, 90, 255, 0.18), rgba(0, 255, 255, 0.10)) !important;
        }
        div[data-testid="stMetric"] {
            background: rgba(0, 0, 0, 0.18) !important;
            border: 1px solid rgba(255, 255, 255, 0.16) !important;
            box-shadow: 0 10px 26px rgba(0,0,0,0.18) !important;
        }
        div[data-testid="stMetricValue"] { color:#ffffff !important; text-shadow: 0 2px 10px rgba(0,0,0,.35) !important; }
        div[data-testid="stMetricLabel"] { color: rgba(255,255,255,0.90) !important; opacity: 1 !important; }



        /* =========================================================
           ✅ P7 RESULT CLEAN + VISIBILITY (FINAL)
           - 흐림 제거 / 카드 대비 강화 / 꼭 필요한 것만 잘 보이게
           ========================================================= */
        .p7-neon-banner{
          background: rgba(0,0,0,0.22) !important;
          border: 1px solid rgba(255,255,255,0.16) !important;
        }
        div[data-testid="stMetric"]{
          background: rgba(0,0,0,0.28) !important;
          border: 1px solid rgba(255,255,255,0.18) !important;
          box-shadow: 0 10px 24px rgba(0,0,0,0.18) !important;
        }
        div[data-testid="stMetricLabel"]{ opacity:1 !important; color:rgba(255,255,255,.92) !important; }
        div[data-testid="stMetricValue"]{ color:#ffffff !important; text-shadow: 0 2px 10px rgba(0,0,0,.30) !important; }

        /* 결과 화면의 불필요한 “희미함” 제거 */
        [data-testid="stMarkdownContainer"], .stMarkdown, .stMarkdown *{
          opacity:1 !important;
          filter:none !important;
        }



        /* =========================================================
           ✅ P7 RESULT CLEAN BOARD (FINAL)
           - 흐림 제거 / 카드 정돈 / 텍스트 선명 / 보상 화면 느낌
           ========================================================= */

        /* 화면 전체 흐림 제거 */
        [data-testid="stMarkdownContainer"], .stMarkdown, .stMarkdown *{
          opacity:1 !important;
          filter:none !important;
          text-shadow: 0 2px 10px rgba(0,0,0,.28) !important;
        }

        /* 상단 배너(공지/안내): 작게 + 더 또렷하게 */
        .p7-neon-banner{
          background: rgba(0,0,0,0.26) !important;
          border: 1px solid rgba(255,255,255,0.16) !important;
          box-shadow: 0 10px 24px rgba(0,0,0,0.18) !important;
        }

        /* 메트릭 박스: 진하게(흐림 방지) */
        div[data-testid="stMetric"]{
          background: rgba(0,0,0,0.30) !important;
          border: 1px solid rgba(255,255,255,0.18) !important;
          border-radius: 16px !important;
        }
        div[data-testid="stMetricLabel"]{ opacity:1 !important; color:rgba(255,255,255,.92) !important; }
        div[data-testid="stMetricValue"]{ color:#ffffff !important; font-weight:900 !important; }

        /* 요약 브리핑: 글씨 또렷하게 */
        h3, h2, h1 { opacity:1 !important; }

        /* 버튼: 깔끔하게 동일한 높이 */
        div[data-testid="stButton"] > button{
          border-radius: 16px !important;
          font-weight: 900 !important;
        }



        /* =========================================================
           ✅ P7 RESULT ULTRA CLEAN (NO FOG)
           - blur 제거 / 투명도 낮추기 / 카드 선명하게
           ========================================================= */

        /* 결과 화면에서만: 텍스트 흐림/필터/불필요 그림자 제거 */
        [data-testid="stMarkdownContainer"], .stMarkdown, .stMarkdown *{
          opacity:1 !important;
          filter:none !important;
          text-shadow:none !important;
        }

        /* 배경: 더 진하고 단순하게 (안개 제거) */
        .stApp{
          background: linear-gradient(180deg, rgba(2,6,23,1) 0%, rgba(2,6,23,1) 55%, rgba(1,3,12,1) 100%) !important;
        }

        /* 상단 타이틀/섹션 글자: 선명하게 */
        h1, h2, h3{
          color:#ffffff !important;
          text-shadow:none !important;
          opacity:1 !important;
        }

        /* 공지 배너: 불투명 카드로(뿌연 그라데이션 제거) */
        .p7-neon-banner{
          background: rgba(15,23,42,0.92) !important;
          border: 1px solid rgba(255,255,255,0.18) !important;
          box-shadow: 0 10px 22px rgba(0,0,0,0.22) !important;
          backdrop-filter: none !important;
        }

        /* 메트릭 카드: 확실히 진하게 */
        div[data-testid="stMetric"]{
          background: rgba(15,23,42,0.92) !important;
          border: 1px solid rgba(255,255,255,0.18) !important;
          border-radius: 16px !important;
          box-shadow: 0 10px 22px rgba(0,0,0,0.22) !important;
          backdrop-filter: none !important;
        }
        div[data-testid="stMetricLabel"]{ color: rgba(255,255,255,0.92) !important; opacity:1 !important; }
        div[data-testid="stMetricValue"]{ color:#ffffff !important; font-weight:900 !important; opacity:1 !important; }

        /* Expander도 선명 카드로 */
        div[data-testid="stExpander"]{
          background: rgba(15,23,42,0.70) !important;
          border: 1px solid rgba(255,255,255,0.14) !important;
          border-radius: 16px !important;
          backdrop-filter: none !important;
        }



        /* =========================================================
           ✅ P7 RESULT CENTER + METRIC STYLE (FINAL)
           ========================================================= */

        /* 결과 화면 전체 텍스트는 중앙 정렬 */
        [data-testid="stMarkdownContainer"], .stMarkdown, .stMarkdown *{
          text-align: center !important;
        }
        h1,h2,h3{ text-align:center !important; }

        /* 메트릭 박스: 조금 작게 + 중앙 정렬 */
        div[data-testid="stMetric"]{
          padding: 10px 12px !important;
          border-radius: 16px !important;
          min-height: 86px !important;
        }
        div[data-testid="stMetricLabel"], div[data-testid="stMetricValue"]{
          text-align:center !important;
          width:100% !important;
        }
        div[data-testid="stMetricValue"]{
          font-size: 1.75rem !important;
          font-weight: 950 !important;
        }

        /* 3개 박스 색 살짝 구분(좌측 인셋 컬러) */
        div[data-testid="stMetric"]:nth-of-type(1){
          box-shadow: inset 0 0 0 2px rgba(0,255,255,0.22), 0 10px 22px rgba(0,0,0,0.18) !important;
        }
        div[data-testid="stMetric"]:nth-of-type(2){
          box-shadow: inset 0 0 0 2px rgba(167,139,250,0.22), 0 10px 22px rgba(0,0,0,0.18) !important;
        }
        div[data-testid="stMetric"]:nth-of-type(3){
          box-shadow: inset 0 0 0 2px rgba(255,204,0,0.18), 0 10px 22px rgba(0,0,0,0.18) !important;
        }

        /* Step 1~3 영역도 가운데로 */
        .stMarkdown p, .stMarkdown div{ text-align:center !important; }

        /* ✅ 열람 패널(Expander) : 유닉 컬러 + 조금 더 크게 */
        div[data-testid="stExpander"] summary{
          background: linear-gradient(135deg, rgba(110,231,255,0.18), rgba(167,139,250,0.16)) !important;
          border: 1px solid rgba(255,255,255,0.16) !important;
          border-radius: 18px !important;
          padding: 14px 16px !important;
          font-weight: 950 !important;
        }
        div[data-testid="stExpander"]{
          border-radius: 18px !important;
        }



        /* =========================================================
           ✅ P7 ANALYSIS BUTTONS (4 COLORS, SAFE)
           - expander 안의 4개 분석 버튼을 "확실히 다른 색"으로
           - 중앙정렬 + 살짝 크게 + hover 강조
           ========================================================= */

        /* 버튼 공통: 중앙정렬 + 크기 */
        div[data-testid="stExpander"] div[data-testid="stButton"] > button{
          border-radius: 18px !important;
          font-weight: 950 !important;
          text-align: center !important;
          justify-content: center !important;
          padding: 16px 14px !important;
          min-height: 62px !important;
          box-shadow: 0 10px 24px rgba(0,0,0,0.18) !important;
          border: 1px solid rgba(255,255,255,0.14) !important;
          transition: transform .10s ease, filter .10s ease, box-shadow .10s ease !important;
        }
        div[data-testid="stExpander"] div[data-testid="stButton"] > button:hover{
          transform: translateY(-2px) !important;
          filter: brightness(1.06) !important;
          box-shadow: 0 14px 30px rgba(0,0,0,0.22) !important;
        }

        /* ✅ 4개 버튼 색상 (expander 내부 버튼 중 '처음 4개'를 컬러 분리) */
        div[data-testid="stExpander"] div[data-testid="stButton"]:nth-of-type(1) > button{
          background: linear-gradient(135deg, rgba(34,211,238,0.22), rgba(59,130,246,0.20)) !important; /* Blue/Cyan */
          color: #ffffff !important;
        }
        div[data-testid="stExpander"] div[data-testid="stButton"]:nth-of-type(2) > button{
          background: linear-gradient(135deg, rgba(167,139,250,0.22), rgba(147,51,234,0.20)) !important; /* Purple */
          color: #ffffff !important;
        }
        div[data-testid="stExpander"] div[data-testid="stButton"]:nth-of-type(3) > button{
          background: linear-gradient(135deg, rgba(251,191,36,0.22), rgba(249,115,22,0.20)) !important; /* Amber/Orange */
          color: #ffffff !important;
        }
        div[data-testid="stExpander"] div[data-testid="stButton"]:nth-of-type(4) > button{
          background: linear-gradient(135deg, rgba(248,113,113,0.22), rgba(239,68,68,0.20)) !important; /* Red */
          color: #ffffff !important;
        }



        /* =========================================================
           ✅ P7 ANALYSIS BUTTONS ULTRA (4 COLORS + HIGH CONTRAST)
           - ONLY .p7-analysis-row 안 4개 버튼에만 적용
           ========================================================= */

        .p7-analysis-row div[data-testid="stButton"] > button{
          width: 100% !important;
          border-radius: 20px !important;
          padding: 18px 16px !important;
          min-height: 72px !important;
          font-weight: 950 !important;
          font-size: 18px !important;
          text-align: center !important;
          justify-content: center !important;
          border: 1px solid rgba(255,255,255,0.18) !important;
          box-shadow: 0 12px 26px rgba(0,0,0,0.22) !important;
          transition: transform .12s ease, filter .12s ease, box-shadow .12s ease !important;
        }
        /* 버튼 내부 글자/아이콘 전부 흰색(가독성) */
        .p7-analysis-row div[data-testid="stButton"] > button,
        .p7-analysis-row div[data-testid="stButton"] > button *{
          color:#ffffff !important;
          opacity:1 !important;
          filter:none !important;
          text-shadow: 0 2px 10px rgba(0,0,0,0.25) !important;
        }
        .p7-analysis-row div[data-testid="stButton"] > button:hover{
          transform: translateY(-2px) scale(1.01) !important;
          filter: brightness(1.08) !important;
          box-shadow: 0 18px 34px rgba(0,0,0,0.28) !important;
        }
        .p7-analysis-row div[data-testid="stButton"] > button:active{
          transform: translateY(1px) scale(0.995) !important;
        }

        /* ✅ 4색 확실히 분리 (wrapper 내부 stButton 순서 기준: 1~4) */
        .p7-analysis-row div[data-testid="stButton"]:nth-of-type(1) > button{
          background: linear-gradient(135deg, rgba(34,211,238,0.55), rgba(59,130,246,0.45)) !important; /* 지문 분석: Blue/Cyan */
        }
        .p7-analysis-row div[data-testid="stButton"]:nth-of-type(2) > button{
          background: linear-gradient(135deg, rgba(167,139,250,0.55), rgba(147,51,234,0.45)) !important; /* 문제 해설: Purple */
        }
        .p7-analysis-row div[data-testid="stButton"]:nth-of-type(3) > button{
          background: linear-gradient(135deg, rgba(251,191,36,0.55), rgba(249,115,22,0.45)) !important; /* 선지 분석: Orange */
        }
        .p7-analysis-row div[data-testid="stButton"]:nth-of-type(4) > button{
          background: linear-gradient(135deg, rgba(248,113,113,0.55), rgba(239,68,68,0.45)) !important; /* 단어 무기: Red */
        }



        /* =========================================================
           ✅ P7 ANALYSIS BUTTONS — BRIGHT & MOBILE FIRST
           - 버튼이 주인공: 밝은 카드 + 진한 글자
           ========================================================= */

        /* 안내문 배너(원하는 분석...)는 조연으로 작게 */
        .p7-analysis-row + div, .p7-analysis-row + div *{
          opacity: 0.85 !important;
          font-size: 14px !important;
        }

        /* 공통: 밝은 카드 + 검정 텍스트 */
        .p7-analysis-row div[data-testid="stButton"] > button{
          width:100% !important;
          border-radius: 22px !important;
          padding: 18px 14px !important;
          min-height: 74px !important;
          font-weight: 950 !important;
          font-size: 18px !important;
          text-align:center !important;
          justify-content:center !important;

          /* 밝은 카드 */
          background: rgba(255,255,255,0.94) !important;
          color:#0b1220 !important;

          border: 1px solid rgba(0,0,0,0.10) !important;
          box-shadow: 0 14px 30px rgba(0,0,0,0.20) !important;
          transition: transform .12s ease, filter .12s ease, box-shadow .12s ease !important;
        }
        .p7-analysis-row div[data-testid="stButton"] > button *{
          color:#0b1220 !important;
          opacity:1 !important;
          text-shadow:none !important;
        }

        /* Hover = 락온 느낌 */
        .p7-analysis-row div[data-testid="stButton"] > button:hover{
          transform: translateY(-2px) !important;
          filter: brightness(1.05) saturate(1.05) !important;
          box-shadow: 0 18px 36px rgba(0,0,0,0.26) !important;
        }
        .p7-analysis-row div[data-testid="stButton"] > button:active{
          transform: translateY(1px) scale(0.995) !important;
        }

        /* 4색 “상단 라이트 바”로 기능 구분 (너무 어둡지 않게) */
        .p7-analysis-row div[data-testid="stButton"] > button{
          position: relative !important;
          overflow: hidden !important;
        }
        .p7-analysis-row div[data-testid="stButton"] > button::before{
          content:"";
          position:absolute; left:0; top:0; right:0;
          height: 6px;
          opacity: 0.95;
        }
        .p7-analysis-row div[data-testid="stButton"]:nth-of-type(1) > button::before{ background: linear-gradient(90deg,#22d3ee,#3b82f6); } /* 지문 */
        .p7-analysis-row div[data-testid="stButton"]:nth-of-type(2) > button::before{ background: linear-gradient(90deg,#a78bfa,#9333ea); } /* 해설 */
        .p7-analysis-row div[data-testid="stButton"]:nth-of-type(3) > button::before{ background: linear-gradient(90deg,#fbbf24,#f97316); } /* 선지 */
        .p7-analysis-row div[data-testid="stButton"]:nth-of-type(4) > button::before{ background: linear-gradient(90deg,#fb7185,#ef4444); } /* 단어 */

        /* 모바일: 버튼 더 크게 + 줄바꿈 허용 */
        @media (max-width: 640px){
          .p7-analysis-row div[data-testid="stButton"] > button{
            min-height: 84px !important;
            font-size: 18px !important;
            padding: 18px 12px !important;
            white-space: normal !important;
          }
        }



        /* =========================================================
           ✅ P7 ANALYSIS BUTTONS — BRIGHT FORCE (WRAPPER ONLY)
           - .p7-analysis-row 안 4개 버튼만 확실히 밝게
           ========================================================= */

        .p7-analysis-row div[data-testid="stButton"] > button{
          background: rgba(255,255,255,0.96) !important;
          color:#0b1220 !important;
          border: 1px solid rgba(0,0,0,0.12) !important;
          border-radius: 22px !important;
          padding: 18px 14px !important;
          min-height: 74px !important;
          font-weight: 950 !important;
          font-size: 18px !important;
          text-align:center !important;
          justify-content:center !important;
          box-shadow: 0 14px 30px rgba(0,0,0,0.22) !important;
          position: relative !important;
          overflow: hidden !important;
          transition: transform .12s ease, filter .12s ease, box-shadow .12s ease !important;
        }
        .p7-analysis-row div[data-testid="stButton"] > button *{
          color:#0b1220 !important;
          opacity:1 !important;
          text-shadow:none !important;
        }
        .p7-analysis-row div[data-testid="stButton"] > button:hover{
          transform: translateY(-2px) !important;
          filter: brightness(1.06) saturate(1.05) !important;
          box-shadow: 0 18px 36px rgba(0,0,0,0.28) !important;
        }
        .p7-analysis-row div[data-testid="stButton"] > button:active{
          transform: translateY(1px) scale(0.995) !important;
        }

        /* 4색 라인 (눈에 확 띄게) */
        .p7-analysis-row div[data-testid="stButton"] > button::before{
          content:"";
          position:absolute; left:0; top:0; right:0;
          height: 7px;
          opacity: 1;
        }
        .p7-analysis-row div[data-testid="stButton"]:nth-of-type(1) > button::before{ background: linear-gradient(90deg,#22d3ee,#3b82f6); } /* 지문 */
        .p7-analysis-row div[data-testid="stButton"]:nth-of-type(2) > button::before{ background: linear-gradient(90deg,#a78bfa,#9333ea); } /* 해설 */
        .p7-analysis-row div[data-testid="stButton"]:nth-of-type(3) > button::before{ background: linear-gradient(90deg,#fbbf24,#f97316); } /* 선지 */
        .p7-analysis-row div[data-testid="stButton"]:nth-of-type(4) > button::before{ background: linear-gradient(90deg,#fb7185,#ef4444); } /* 단어 */

        /* 모바일 더 크게 */
        @media (max-width: 640px){
          .p7-analysis-row div[data-testid="stButton"] > button{
            min-height: 86px !important;
            font-size: 18px !important;
            padding: 18px 12px !important;
            white-space: normal !important;
          }
        }



        /* =========================================================
           ✅ P7 ANALYSIS BUTTONS — WHITE LOBBY (WRAPPER ONLY)
           ========================================================= */

        /* 버튼 4개를 '게임 로비' 흰 카드로 */
        .p7-analysis-row div[data-testid="stButton"] > button{
          width:100% !important;
          border-radius: 22px !important;
          padding: 18px 14px !important;
          min-height: 76px !important;

          background: rgba(255,255,255,0.98) !important; /* 완전 흰 카드 */
          color:#0b1220 !important;

          border: 1px solid rgba(0,0,0,0.10) !important;
          box-shadow: 0 14px 30px rgba(0,0,0,0.22) !important;

          text-align:center !important;
          justify-content:center !important;
          font-weight: 950 !important;
          font-size: 18px !important;

          position: relative !important;
          overflow: hidden !important;
          transition: transform .12s ease, filter .12s ease, box-shadow .12s ease !important;
        }
        .p7-analysis-row div[data-testid="stButton"] > button *{
          color:#0b1220 !important;
          opacity:1 !important;
          text-shadow:none !important;
        }

        /* hover/active: 눌림감 */
        .p7-analysis-row div[data-testid="stButton"] > button:hover{
          transform: translateY(-2px) !important;
          filter: brightness(1.03) saturate(1.05) !important;
          box-shadow: 0 18px 36px rgba(0,0,0,0.28) !important;
        }
        .p7-analysis-row div[data-testid="stButton"] > button:active{
          transform: translateY(1px) scale(0.995) !important;
        }

        /* 4색 라이트 바(기능 구분) */
        .p7-analysis-row div[data-testid="stButton"] > button::before{
          content:"";
          position:absolute; left:0; top:0; right:0;
          height: 7px;
          opacity: 1;
        }
        .p7-analysis-row div[data-testid="stButton"]:nth-of-type(1) > button::before{ background: linear-gradient(90deg,#22d3ee,#3b82f6); } /* 지문 */
        .p7-analysis-row div[data-testid="stButton"]:nth-of-type(2) > button::before{ background: linear-gradient(90deg,#a78bfa,#9333ea); } /* 해설 */
        .p7-analysis-row div[data-testid="stButton"]:nth-of-type(3) > button::before{ background: linear-gradient(90deg,#fbbf24,#f97316); } /* 선지 */
        .p7-analysis-row div[data-testid="stButton"]:nth-of-type(4) > button::before{ background: linear-gradient(90deg,#fb7185,#ef4444); } /* 단어 */

        /* 모바일: 더 크게 */
        @media (max-width: 640px){
          .p7-analysis-row div[data-testid="stButton"] > button{
            min-height: 88px !important;
            font-size: 18px !important;
            padding: 18px 12px !important;
            white-space: normal !important;
          }
        }



        /* =========================================================
           ✅ P7 ANALYSIS WHITE LOBBY (WRAPPER ONLY)
           ========================================================= */
        .p7-analysis-row div[data-testid="stButton"] > button{
          background: rgba(255,255,255,0.98) !important;
          color:#0b1220 !important;
          border: 1px solid rgba(0,0,0,0.10) !important;
          border-radius: 22px !important;
          padding: 18px 14px !important;
          min-height: 76px !important;
          font-weight: 950 !important;
          font-size: 18px !important;
          text-align:center !important;
          justify-content:center !important;
          box-shadow: 0 14px 30px rgba(0,0,0,0.22) !important;
          position: relative !important;
          overflow: hidden !important;
        }
        .p7-analysis-row div[data-testid="stButton"] > button *{
          color:#0b1220 !important;
          opacity:1 !important;
          text-shadow:none !important;
        }

        /* 상단 4색 라인 */
        .p7-analysis-row div[data-testid="stButton"] > button::before{
          content:"";
          position:absolute; left:0; top:0; right:0;
          height: 7px;
        }
        .p7-analysis-row div[data-testid="stButton"]:nth-of-type(1) > button::before{ background: linear-gradient(90deg,#22d3ee,#3b82f6); }
        .p7-analysis-row div[data-testid="stButton"]:nth-of-type(2) > button::before{ background: linear-gradient(90deg,#a78bfa,#9333ea); }
        .p7-analysis-row div[data-testid="stButton"]:nth-of-type(3) > button::before{ background: linear-gradient(90deg,#fbbf24,#f97316); }
        .p7-analysis-row div[data-testid="stButton"]:nth-of-type(4) > button::before{ background: linear-gradient(90deg,#fb7185,#ef4444); }

        /* hover */
        .p7-analysis-row div[data-testid="stButton"] > button:hover{
          transform: translateY(-2px) !important;
          filter: brightness(1.03) saturate(1.05) !important;
          box-shadow: 0 18px 36px rgba(0,0,0,0.28) !important;
        }

        @media (max-width: 640px){
          .p7-analysis-row div[data-testid="stButton"] > button{
            min-height: 88px !important;
            font-size: 18px !important;
            padding: 18px 12px !important;
            white-space: normal !important;
          }
        }



        /* =========================================================
           ✅ P7 ANALYSIS ROW FINAL CONTRAST
           - 4개 버튼 텍스트가 "항상" 잘 보이게 최종 오버라이드
           ========================================================= */
        .p7-analysis-row div[data-testid="stButton"] > button{
          background: rgba(255,255,255,0.98) !important;
          color:#0b1220 !important;
          font-weight: 950 !important;
        }
        .p7-analysis-row div[data-testid="stButton"] > button *{
          color:#0b1220 !important;
          opacity:1 !important;
          text-shadow:none !important;
          font-weight: 950 !important;
        }


/* =========================================================
   SNAPQ A PALETTE — P7 (ICE / STRATEGY) FINAL OVERRIDE
   - UI/CSS only (last-wins)
   - Mobile-first readability
   ========================================================= */
:root{
  --bg-base:#0E1624;
  --bg-grad-1:#141C2B;
  --bg-grad-2:#1B2333;
  --text-main:#E5E7EB;
  --text-sub:#9CA3AF;

  --p7-main:#22D3EE;   /* cyan */
  --p7-accent:#5EEAD4; /* mint */
  --p7-info:#38BDF8;   /* sky */
}

.stApp{
  background:
    radial-gradient(900px 650px at 18% 16%, rgba(34,211,238,0.14), transparent 60%),
    radial-gradient(900px 650px at 72% 14%, rgba(94,234,212,0.10), transparent 62%),
    radial-gradient(900px 900px at 50% 78%, rgba(56,189,248,0.10), transparent 70%),
    linear-gradient(180deg, var(--bg-grad-1) 0%, var(--bg-base) 55%, #0B1020 100%) !important;
  color: var(--text-main) !important;
}

.block-container{
  max-width: 100% !important;
  padding-left: 0.85rem !important;
  padding-right: 0.85rem !important;
  padding-top: 0.20rem !important;
}

.p7-hudbar{
  background: rgba(255,255,255,0.10) !important;
  border: 1px solid rgba(34,211,238,0.22) !important;
  box-shadow: 0 10px 26px rgba(0,0,0,0.22), 0 0 0 1px rgba(34,211,238,0.10) inset !important;
}
.p7-chip{
  border-color: rgba(34,211,238,0.22) !important;
}

.p7-time-svg circle:last-child{ stroke: var(--p7-main) !important; }
.p7-time-warn .p7-time-svg circle:last-child{ stroke: #ffcc00 !important; }
.p7-time-danger2 .p7-time-svg circle:last-child{ stroke: #ff2d2d !important; }

.p7-zone{
  background: rgba(10,16,28,0.74) !important;
  border: 1px solid rgba(34,211,238,0.22) !important;
  box-shadow: 0 14px 34px rgba(0,0,0,0.22) !important;
  backdrop-filter: blur(8px) !important;
}
.p7-zone:before{ background: rgba(34,211,238,0.90) !important; }
.p7-zone .p7-zone-body{
  color:#ffffff !important;
  font-weight: 800 !important;
  text-shadow: 0 2px 10px rgba(0,0,0,0.55) !important;
}

.p7-opt-wrap div[data-testid="stButton"] > button{
  background: rgba(255,255,255,0.98) !important;
  color: #0F172A !important;
  border: 1px solid rgba(0,0,0,0.10) !important;
}
.p7-opt-wrap div[data-testid="stButton"] > button *{ color:#0F172A !important; }
.p7-opt-wrap div[data-testid="stButton"] > button:hover{
  background: linear-gradient(135deg, var(--p7-main), #4DA3FF) !important;
  color:#ffffff !important;
  border-color: rgba(255,255,255,0.22) !important;
}
.p7-opt-wrap div[data-testid="stButton"] > button:hover *{ color:#ffffff !important; }

@media (max-width: 640px){
  .p7-zone .p7-zone-body{ font-size: 30px !important; line-height: 1.6 !important; }
  .p7-zone.mission .p7-zone-body{ font-size: 16px !important; }
  .p7-opt-wrap div[data-testid="stButton"] > button{
    min-height: 82px !important;
    font-size: 17px !important;
    padding: 18px 16px !important;
    white-space: normal !important;
  }
}

</style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("## 📊 전투 결과 브리핑 · 해설 & 단어 저장")

    tb: TimebombState = st.session_state.p7_timebomb
    results: List[P7Result] = st.session_state.p7_results
    # --- HOTFIX: support both dict-style and object-style result items (P7Result) ---
    def _rg(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    correct_count = sum(1 for r in results if r.is_correct)
    wrong_count = len(results) - correct_count
    total_questions = len(results)
    step_reached = total_questions
    time_used = tb.total_limit - tb.remaining if tb.total_limit > 0 else 0
    if time_used < 0:
        time_used = 0
    cleared = (
        total_questions == 3
        and correct_count == total_questions
        and step_reached == 3
        and not tb.is_over
    )

    if not st.session_state.get("p7_stats_updated", False):
        if record_p7_result is not None:
            try:
                record_p7_result(
                    category=st.session_state.get("p7_selected_category", "P7"),
                    level=st.session_state.get("p7_level", 1),
                    correct_count=correct_count,
                    total_questions=total_questions,
                    time_used=time_used,
                    step_reached=step_reached,
                    cleared=cleared,
                )
            except Exception as e:
                st.warning(f"기록 저장 중 오류가 발생했습니다 (record_p7_result): {e}")

        # ✅ 레벨 시스템 업데이트
        try:
            cat_name = st.session_state.get("p7_selected_category", "P7")
            cat_info, leveled_up, prev_level = update_p7_level(cat_name, cleared)
            st.session_state.p7_level = cat_info["level"]
            if leveled_up:
                st.success(
                    f"🎉 랭크 업! [{cat_name}] 카테고리에서 Lv{prev_level} → Lv{cat_info['level']} 로 상승했습니다."
                )
            else:
                st.info(
                    f"[{cat_name}] 현재 레벨: Lv{cat_info['level']} · "
                    f"연속 클리어: {cat_info['streak']}/5"
                )
        except Exception as e:
            st.warning(f"레벨 기록을 업데이트하는 중 오류가 발생했습니다: {e}")

        st.session_state.p7_stats_updated = True

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("정답 개수", f"{correct_count} / 3")
    with col2:
        st.metric("오답 개수", f"{wrong_count}")
    with col3:
        st.metric("남은 시간", get_time_display(tb.remaining))

    # --- (A) 요약 브리핑: 기본 화면의 주인공 ---
    can_open = (correct_count == 3) and (not tb.is_over)

    if not can_open:
        st.markdown("<div class=\"p7-divider\"></div>", unsafe_allow_html=True)
        st.markdown("""
            <div style="padding:18px;border-radius:16px;border:2px solid #ff4d4f;background:rgba(255,77,79,0.06);">
              <div style="font-size:26px;font-weight:800;letter-spacing:0.5px;">💀 YOU LOST!</div>
              <div style="margin-top:6px;font-size:15px;">
                이번 세트는 <b>올클리어</b> 실패. (정답 {correct_count}/3 · 오답 {wrong_count})
              </div>
              <div style="margin-top:4px;font-size:13px;opacity:0.85;">
                해석/정답/단어 보상은 <b>3/3 올클리어</b>일 때만 해금됩니다.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2, gap="small")
        with c1:
            if st.button("🔥 다시 도전!", use_container_width=True, key="p7_lost_retry"):
                _reset_p7_battle(keep_time_choice=True)
                st.session_state["p7_started"] = False
                st.session_state["p7_phase"] = "setup"
                st.session_state["p7_show_feedback"] = False
                st.rerun()

        with c2:
            if st.button("🏠 메인 허브로", use_container_width=True, key="p7_lost_to_hub"):
                _safe_switch_page(
                    ["main_hub.py", "./main_hub.py", "pages/00_Main_Hub.py", "pages\\00_Main_Hub.py"],
                    fallback_hint="메인 허브",
                )
        return
    st.markdown("### 🧾 요약 브리핑 (Step 1~3)")
    # ✅ HOTFIX: steps_results가 로컬 스코프에 없어서 NameError가 발생했음
    # p7_results는 각 Step 결과(정답/오답/선택/정답 등)를 누적 저장하는 세션 키
    steps_results = st.session_state.get('p7_results', []) or []

    def _choice_letter(idx: int) -> str:
        letters = ["A", "B", "C", "D"]
        return letters[idx] if isinstance(idx, int) and 0 <= idx < 4 else "-"

    # step별 결과 조회
    r_by_step = {r.step: r for r in results}

    c1, c2, c3 = st.columns(3)
    for _col, _step in [(c1, 1), (c2, 2), (c3, 3)]:
        with _col:
            r = r_by_step.get(_step)
            if r is None:
                st.markdown(f"**Step {_step}**")
                st.caption("미진입")
                st.write("—")
            else:
                badge = "✅ CLEAR" if r.is_correct else "❌ MISS"
                st.markdown(f"**Step {_step} · {badge}**")
                st.write(f"내 선택: **{_choice_letter(r.user_choice)}**  |  정답: **{_choice_letter(r.correct_choice)}**")
    st.success("✅ 축하합니다! 이번 세트는 해석/정답/어휘 화면이 열립니다.")

    # ✅ 결과 브리핑 하단 이동 버튼(항상 노출) — Expander 밖
    st.markdown("---")
    b1, b2, b3 = st.columns(3, gap="small")
    with b1:
        if st.button("🧰 비밀 무기고로 이동", use_container_width=True, key="p7_result_to_armory"):
            _safe_switch_page(["pages/03_Secret_Armory_Main.py"], fallback_hint="비밀 무기고")
    with b2:
        if st.button("🔥 P7 게임 한 판 더!", use_container_width=True, key="p7_result_rematch"):
            _reset_p7_battle(keep_time_choice=False)
            st.session_state["p7_started"] = False
            st.session_state["p7_phase"] = "setup"
            st.session_state["p7_show_feedback"] = False
            st.session_state.pop("p7_feedback_open", None)
            st.rerun()
    with b3:
        if st.button("🏠 MAIN HUB", use_container_width=True, key="p7_result_to_mainhub"):
            _safe_switch_page(
                ["main_hub.py", "./main_hub.py", "pages/00_Main_Hub.py", "pages\\00_Main_Hub.py"],
                fallback_hint="메인 허브",
            )
    current_set = get_current_p7_set()

    # ✅ 전투 로그(해석/정답/단어) — 결과 브리핑에서만 열람 가능
    st.markdown("### 🧾 전투 기록 열람 (클릭해서 보기)")
    # ✅ 열람 패널은 '항상 닫힘'으로 시작해야 함.
    # Streamlit expander는 key를 받지 않으므로,
    # 새 전투(세트)마다 nonce를 올려 토글 상태를 안전하게 초기화합니다.
    set_id = st.session_state.get("p7_selected_set_id", "P7")
    # ✅ SAFE: 패널 nonce는 "세트가 바뀔 때만" 증가 (매 rerun마다 증가하면 버튼 선택이 초기화됨)
    if st.session_state.get("p7_panel_nonce_lock") != set_id:
        st.session_state["p7_panel_nonce"] = int(st.session_state.get("p7_panel_nonce", 0)) + 1
        st.session_state["p7_panel_nonce_lock"] = set_id
    panel_nonce = int(st.session_state.get("p7_panel_nonce", 0))
    _p7_panel_label = "🔓 열람 패널 열기" + ("\\u200b" * panel_nonce)
    with st.expander(locals().get("_p7_panel_label","🔓 열람 패널 열기"), expanded=False):
        tab_labels = [
            "🛰️ 지문 분석",
            "🎯 문제 해설",
            "🧩 선지 분석",
            "🧨 단어 무기",
        ]
        _panel_choice_key = f"p7_panel_choice_{st.session_state.get('p7_selected_set_id','P7')}_{panel_nonce}"
        if _panel_choice_key not in st.session_state:
            st.session_state[_panel_choice_key] = None

        st.caption("🔓 분석 모드를 선택하세요")
        st.markdown("<div class=\"p7-analysis-row\">", unsafe_allow_html=True)
        cols = st.columns(4)
        for _idx, _lbl in enumerate(tab_labels):
            with cols[_idx]:
                if st.button(_lbl, use_container_width=True, key=f"{_panel_choice_key}_{_idx}"):
                    st.session_state[_panel_choice_key] = _lbl
                    st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

        panel_choice = st.session_state[_panel_choice_key]
        if panel_choice is None:
            pass  # (dedupe) hide duplicate hint
        else:
            # 선택 해제(초기화) 버튼
            if st.button("🧹 카테고리 닫기(초기화)", key=f"{_panel_choice_key}_clear"):
                st.session_state[_panel_choice_key] = None
                st.rerun()

            # 아래부터 선택된 카테고리 내용만 표시
        if panel_choice == tab_labels[0]:
            st.caption("문장을 클릭하면(펼치기) 한글 해석이 보입니다.")
            # NOTE: P7Set 필드명 호환 (sentences/translations vs all_sentences_en/all_sentences_ko)
            en_list = getattr(current_set, "sentences", None)
            if not isinstance(en_list, list):
                en_list = getattr(current_set, "all_sentences_en", [])
            ko_list = getattr(current_set, "translations", None)
            if not isinstance(ko_list, list):
                ko_list = getattr(current_set, "all_sentences_ko", [])

            for i, s in enumerate(en_list):
                ko = ko_list[i] if i < len(ko_list) else ""
                with st.expander(f"{i+1}. {s}", expanded=False):
                    st.write(ko if ko else "(해석 데이터 없음)")

                    # 2) 문제 해설

        elif panel_choice == tab_labels[1]:
            for step_idx in range(3):
                if step_idx < len(steps_results):
                    r = steps_results[step_idx]
                    st.markdown(f"#### Step {step_idx+1} — {'✅ CLEAR' if _rg(r, 'is_correct') else '❌ MISS'}")
                    if _rg(r, 'question'):
                        st.write(f"Q. {r['question']}")
                    if _rg(r, 'explanation'):
                        st.info(r['explanation'])
                    else:
                        st.caption("(해설 데이터 없음)")
                    st.markdown("---")

                    # 3) 선택지 분석

        elif panel_choice == tab_labels[2]:
            for step_idx in range(3):
                if step_idx < len(steps_results):
                    r = steps_results[step_idx]
                    st.markdown(f"#### Step {step_idx+1} — 선택지 분석")
                    choices = _rg(r, 'choices', [])
                    correct = _rg(r, 'correct_choice')
                    picked = _rg(r, 'selected_choice')
                    if choices:
                        for ci, ctext in enumerate(choices):
                            label = chr(ord('A') + ci)
                            tag = ""
                            if correct == label:
                                tag = "✅ 정답"
                            elif picked == label:
                                tag = "❌ 선택"
                            st.write(f"- **{label})** {ctext} {tag}")
                    if _rg(r, 'choice_explanations'):
                        st.caption("선택지 해설")
                        for k, v in r['choice_explanations'].items():
                            st.write(f"- **{k})** {v}")
                    else:
                        st.caption("(선택지 해설 데이터 없음)")
                    st.markdown("---")

                    # 4) 핵심 단어 무기고

        elif panel_choice == tab_labels[3]:
            st.caption("지문에서 헷갈렸던 단어를 무기고에 저장해두고, 나중에 VOCA 모드에서 복습하세요.")

            # ✅ SAFE: 후보 단어는 전투 중 누적된 p7_vocab_candidates 사용
            candidates = st.session_state.get("p7_vocab_candidates", [])
            if not isinstance(candidates, list):
                candidates = []

            cleaned = []
            for it in candidates:
                if isinstance(it, dict) and it.get("word") and it.get("meaning"):
                    cleaned.append(it)

            if not cleaned:
                st.info("이번 전투에서 저장 후보 단어가 아직 없습니다. (전투 중 자동 후보가 쌓입니다)")
            else:
                st.markdown("##### 📌 저장 후보 단어 (P7 전장 → VOCA 무기고)")
                options = [f"{d.get('word')} — {d.get('meaning')}" for d in cleaned]
                pick = st.multiselect("저장할 단어 선택", options, key="p7_vocab_pick")

                # 원문 문장(그대로) — 현재 세트 전체 문장 합치기
                en_list = getattr(current_set, "all_sentences_en", [])
                if not isinstance(en_list, list):
                    en_list = []
                sentence_full = " ".join([str(s).strip() for s in en_list if str(s).strip()])

                if st.button("💾 선택 단어 무기고에 저장", use_container_width=True, key="p7_vocab_save_btn"):
                    saved = 0
                    for opt in pick:
                        try:
                            w, mm = opt.split("—", 1)
                            w = w.strip()
                            mm = mm.strip()
                        except Exception:
                            continue
                        _add_vocab_to_armory(w, mm, source="P7", sentence=(sentence_full if sentence_full else None))
                        saved += 1

                    try:
                        if callable(update_secret_armory_count):
                            update_secret_armory_count(reason="add_from_p7")
                    except Exception:
                        pass

                    st.success(f"저장 완료: {saved}개 (VOCA 무기고로 이동해서 확인하세요)")
                    st.session_state.pop("p7_vocab_pick", None)
                    st.rerun()

        # ============================================

            # P7 Reading Arena 메인 페이지 (시간카드 선택 → 전투 → 피드백)
            # ============================================

def _reset_p7_battle(keep_time_choice: bool = True):
    """P7 전투 상태를 안전하게 초기화합니다. (기록 파일/무기고는 유지)"""
    time_choice = st.session_state.get("p7_time_limit_choice", 150) if keep_time_choice else 150
    st.session_state["p7_panel_nonce"] = int(st.session_state.get("p7_panel_nonce", 0)) + 1


    st.session_state.p7_current_step = 1
    st.session_state.p7_results = []
    st.session_state.p7_has_started = False
    st.session_state.p7_has_finished = False
    st.session_state.p7_stats_updated = False
    st.session_state.p7_vocab_candidates = []
    st.session_state.p7_vocab_saved_this_set = False

    # 콤보/타임봄 리셋
    st.session_state.p7_combo = ComboState()
    st.session_state.p7_timebomb = TimebombState(total_limit=int(time_choice), remaining=int(time_choice))

    # 체크박스 키(단어 저장 선택) 정리
    for k in list(st.session_state.keys()):
        if isinstance(k, str) and k.startswith("p7_save_"):
            del st.session_state[k]



def reading_arena_page():
    """Render the P7 Reading Arena (battle only).
    Layout: 80% battlefield (passage/question/choices) + 20% HUD (step/timer/combo).
    """
    inject_css()
    st.markdown("<!-- p7_hud_title -->", unsafe_allow_html=True)

    # ---- ensure state ----
    init_session_state()

    if not st.session_state.get("p7_has_started", False):
        # Auto-start: no lobby in this module.
        st.session_state["p7_has_started"] = True
        st.session_state.setdefault("p7_current_step", 1)
        st.session_state.setdefault("p7_max_step_reached", 1)
        start_timebomb()

    update_timebomb()

    # ✅ TIMEBOMB 종료 or 3/3 종료 시: 전장 화면을 더 그리지 말고 결과 브리핑으로 전환
    tb: TimebombState = st.session_state.p7_timebomb
    if tb.is_over and not st.session_state.get("p7_has_finished", False):
        st.session_state["p7_has_finished"] = True

    if st.session_state.get("p7_has_finished", False):
        render_p7_feedback()
        return

    # ---- header removed for mobile focus (title stays in HUD) ----

    # ---- layout: 80/20 ----

    def _get_step_data(_step: int) -> StepData:
        _set = get_current_p7_set()
        if _step == 1:
            return _set.step1
        elif _step == 2:
            return _set.step2
        return _set.step3

    # ✅ A안: 오른쪽 HUD 제거 → TOP HUD + 전장만
    current_step = int(st.session_state.get("p7_current_step", 1))
    max_reached = int(st.session_state.get("p7_max_step_reached", current_step))

    
    # --- finish gate (3/3 완료 or 시간폭탄 종료면 즉시 브리핑으로 전환) ---
    tb: TimebombState = st.session_state.p7_timebomb
    # tick()은 매 rerun마다 호출되어 남은 시간이 갱신됨
    try:
        tb.tick()
    except Exception:
        pass

    if getattr(tb, "is_over", False) and not st.session_state.get("p7_has_finished", False):
        st.session_state["p7_has_finished"] = True

    if st.session_state.get("p7_has_finished", False):
        render_p7_feedback()
        return

# 1) TOP HUD 먼저 (무조건 보이게)

    # 2) 전장(지문/문제/선택지)만 렌더
    st.markdown("<div class='p7-battlefield'>", unsafe_allow_html=True)
    render_top_hud()
    render_p7_step(current_step)
    st.markdown("</div>", unsafe_allow_html=True)
def init_armory_state():
    if not st.session_state.secret_armory_p5:
        for p in P5_SAMPLE_PROBLEMS:
            _add_p5_to_armory(p)
    if not st.session_state.secret_armory_vocab:
        for item in SAMPLE_VOCAB_ITEMS:
            _add_vocab_to_armory(item.word, item.meaning, item.source)


def render_armory_hub():
    st.markdown("## 📕 Secret Armory – 비밀 병기고 허브")
    st.write("P5에서 저장된 문제들과 P7에서 SAVE한 단어들이 모여 있는 개인 무기고입니다.")
    st.write("여기서 다시 학습하거나, 미니 전투(퀴즈)를 통해 불필요한 무기들을 정리할 수 있습니다.")

    col_p5, col_vocab = st.columns(2)

    with col_p5:
        st.markdown("### 💣 P5 문제 무기고")
        p5_list: List[P5Problem] = st.session_state.secret_armory_p5
        st.write(f"현재 쌓인 P5 문제: **{len(p5_list)}개**")

        if p5_list:
            st.write("예시로 몇 문제만 보여드릴게요:")
            for p in p5_list[:3]:
                st.write(f"- ({p.problem_id}) {p.question}")

        if st.button("⚔ P5 미니 전투 실행 (랜덤 5문제)", use_container_width=True):
            start_p5_quiz()
            st.session_state.armory_section = "p5"
            st.rerun()

    with col_vocab:
        st.markdown("### 📚 단어 무기고 (P7 + P5)")
        vocab_list: List[Dict] = st.session_state.secret_armory_vocab
        st.write(f"현재 저장된 단어: **{len(vocab_list)}개**")

        if vocab_list:
            st.write("예시로 몇 단어만 보여드릴게요:")
            for v in vocab_list[:5]:
                st.write(f"- {v['word']} : {v['meaning']} ({v['source']})")

        if st.button("🧠 Vocab Timebomb (학습 + 퀴즈 모드)", use_container_width=True):
            prepare_vocab_quiz_set()
            st.session_state.armory_section = "vocab"
            st.rerun()

    st.info(
        "비밀 병기고는 마구 저장만 하는 창고가 아니라, "
        "매일 들어와서 청소하고 강화하는 전투 무기고입니다."
    )

# ---------- P5 미니 전투 ----------

def start_p5_quiz():
    p5_list: List[P5Problem] = st.session_state.secret_armory_p5
    if not p5_list:
        return
    indices = list(range(len(p5_list)))
    random.shuffle(indices)
    indices = indices[:5]
    st.session_state.p5_quiz_order = indices
    st.session_state.p5_quiz_index = 0
    st.session_state.p5_quiz_started = True


def render_p5_armory():
    st.markdown("## 💣 P5 Timebomb – 무기고 미니 전투")

    p5_list: List[P5Problem] = st.session_state.secret_armory_p5
    if not p5_list:
        st.info("현재 비밀 병기고에 저장된 P5 문제가 없습니다.")
        if st.button("⬅ 허브로 돌아가기"):
            st.session_state.armory_section = "hub"
            st.rerun()
            return
        return

    if not st.session_state.p5_quiz_started:
        st.warning("먼저 허브에서 미니 전투를 시작해 주세요.")
        if st.button("⬅ 허브로 돌아가기"):
            st.session_state.armory_section = "hub"
            st.rerun()
        return

    order = st.session_state.p5_quiz_order
    idx = st.session_state.p5_quiz_index

    if idx >= len(order):
        st.success("🎉 P5 미니 전투를 모두 마쳤습니다!")
        if st.button("⬅ 허브로 돌아가기"):
            st.session_state.armory_section = "hub"
            st.session_state.p5_quiz_started = False
            st.rerun()
        return

    problem = p5_list[order[idx]]

    st.write(f"문제 {idx+1} / {len(order)}")
    st.write(problem.question)

    key = f"p5_quiz_answer_{idx}"
    chosen = st.radio(
        "",
        options=list(range(len(problem.options))),
        format_func=lambda i: problem.options[i],
        key=key,
        label_visibility="collapsed",
    )

    if st.button("정답 확인 및 다음 문제로 ➡", use_container_width=True):
        if chosen == problem.answer_index:
            st.success("정답입니다!")
            if st.checkbox("이 문제는 이제 무기고에서 삭제하기", key=f"p5_delete_{idx}"):
                to_delete_id = problem.problem_id
                new_list = [p for p in p5_list if p.problem_id != to_delete_id]
                st.session_state.secret_armory_p5 = new_list
                st.info(f"문제 {to_delete_id} 가 비밀 병기고에서 삭제되었습니다.")
        else:
            st.error("오답입니다. 다시 복습해 주세요.")

        st.session_state.p5_quiz_index = idx + 1
        st.rerun()

    if st.button("⚓ 전투 중단하고 허브로 돌아가기", use_container_width=True):
        st.session_state.armory_section = "hub"
        st.session_state.p5_quiz_started = False
        st.rerun()

# ---------- Vocab Timebomb (학습 + 퀴즈) ----------

def prepare_vocab_quiz_set():
    vocab_list: List[Dict] = st.session_state.secret_armory_vocab
    if not vocab_list:
        st.session_state.vocab_current_set = []
        st.session_state.vocab_quiz_order = []
        st.session_state.vocab_quiz_index = 0
        st.session_state.vocab_lives = 3
        st.session_state.vocab_score = 0
        st.session_state.vocab_stats_updated = False
        # ✅ 플립 카드 인덱스도 초기화
        st.session_state.vocab_study_index = 0
        st.session_state.vocab_study_show_kor = False
        return

    indices = list(range(len(vocab_list)))
    random.shuffle(indices)
    indices = indices[:10]
    current_set = [vocab_list[i] for i in indices]
    st.session_state.vocab_current_set = current_set

    # ✅ 학습 모드(플립 카드)도 첫 카드부터 시작
    st.session_state.vocab_study_index = 0
    st.session_state.vocab_study_show_kor = False

    order = list(range(len(current_set)))
    random.shuffle(order)
    st.session_state.vocab_quiz_order = order
    st.session_state.vocab_quiz_index = 0
    st.session_state.vocab_lives = 3
    st.session_state.vocab_score = 0
    st.session_state.vocab_stats_updated = False


def _generate_distractors(correct_word: str, all_words: List[str], num_choices: int = 4) -> List[str]:
    distractors = set()

    def tweak_word(w: str) -> str:
        if len(w) <= 2:
            return w.swapcase()
        mode = random.choice(["swap_case", "replace_char", "delete_char", "insert_char"])
        chars = list(w)
        if mode == "swap_case":
            return w.swapcase()
        elif mode == "replace_char":
            idx = random.randint(0, len(chars) - 1)
            chars[idx] = random.choice("abcdefghijklmnopqrstuvwxyz")
            return "".join(chars)
        elif mode == "delete_char":
            idx = random.randint(0, len(chars) - 1)
            return "".join(chars[:idx] + chars[idx + 1 :])
        else:
            idx = random.randint(0, len(chars))
            c = random.choice("abcdefghijklmnopqrstuvwxyz")
            return "".join(chars[:idx] + [c] + chars[idx:])

    pool = [w for w in all_words if w != correct_word]
    while len(distractors) < num_choices - 1 and pool:
        base = random.choice(pool)
        pool.remove(base)
        d = tweak_word(base)
        if d != correct_word:
            distractors.add(d)
    while len(distractors) < num_choices - 1:
        d = tweak_word(correct_word)
        if d != correct_word:
            distractors.add(d)
    return list(distractors)


def render_vocab_study_mode():
    st.markdown("### 🧠 Vocab Timebomb – 학습 모드 (플립 카드)")

    vocab_set: List[Dict] = st.session_state.vocab_current_set
    if not vocab_set:
        st.info("현재 비밀 병기고에 저장된 단어가 없어 학습할 내용이 없습니다.")
        if st.button("⬅ 허브로 돌아가기"):
            st.session_state.armory_section = "hub"
            st.rerun()
        return

    # 인덱스 / 앞뒤면 상태 보정
    if "vocab_study_index" not in st.session_state:
        st.session_state.vocab_study_index = 0
    if "vocab_study_show_kor" not in st.session_state:
        st.session_state.vocab_study_show_kor = False

    idx = st.session_state.vocab_study_index
    show_kor = st.session_state.vocab_study_show_kor

    if idx < 0:
        idx = len(vocab_set) - 1
    if idx >= len(vocab_set):
        idx = 0
    st.session_state.vocab_study_index = idx

    item = vocab_set[idx]
    eng_word = item["word"]
    kor_meaning = item["meaning"]

    st.caption(f"카드 {idx + 1} / {len(vocab_set)}")

    # 앞면/뒷면 텍스트
    if show_kor:
        main_text = kor_meaning
        sub_text = f"= {eng_word}"
    else:
        main_text = eng_word
        sub_text = "카드를 뒤집어 한국어 뜻을 확인해 보세요."

    st.markdown("""
        <div style="
            width: 100%;
            max-width: 480px;
            margin: 16px auto 24px auto;
            padding: 30px 24px;
            border-radius: 18px;
            background: linear-gradient(135deg, #fff9e6, #ffe8f0);
            box-shadow: 0 6px 18px rgba(0,0,0,0.08);
            text-align: center;
        ">
            <div style="font-size: 34px; font-weight: 700; margin-bottom: 10px;">
                {main_text}
            </div>
            <div style="font-size: 18px; color: #555;">
                {sub_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_prev, col_flip, col_next = st.columns(3)

    with col_prev:
        if st.button("⬅ 이전 카드", use_container_width=True):
            st.session_state.vocab_study_index = (idx - 1) % len(vocab_set)
            st.session_state.vocab_study_show_kor = False
            st.rerun()

    with col_flip:
        if st.button("🔄 카드 뒤집기", use_container_width=True):
            st.session_state.vocab_study_show_kor = not show_kor
            st.rerun()

    with col_next:
        if st.button("다음 카드 ➡", use_container_width=True):
            st.session_state.vocab_study_index = (idx + 1) % len(vocab_set)
            st.session_state.vocab_study_show_kor = False
            st.rerun()

    st.markdown("---")
    st.info(
        "플립 카드로 충분히 눈에 익힌 뒤, 아래 버튼을 눌러 "
        "같은 단어들로 타임어택 4지선다 퀴즈에 도전해 보세요."
    )

    if st.button("🎯 이 단어들로 퀴즈 모드 돌입 (KOR → ENG 4지선다)", use_container_width=True):
        st.session_state.vocab_armory_mode = "quiz"
        st.session_state.vocab_quiz_index = 0
        st.session_state.vocab_stats_updated = False
        st.rerun()


def render_vocab_quiz_mode():
    import time as _time
    try:
        from streamlit_autorefresh import st_autorefresh
    except ModuleNotFoundError:
        st_autorefresh = None
        st.warning(
            "자동 타이머를 사용하려면 'pip install streamlit-autorefresh' 후 다시 실행해 주세요. "
            "지금은 일반 카드 배틀 모드로 동작합니다."
        )

    st.markdown("### 🎮 Vocab Timebomb – 타임어택 카드 배틀 (ENG → KOR 4지선다)")

    vocab_set: List[Dict] = st.session_state.vocab_current_set
    if not vocab_set:
        st.info("현재 비밀 병기고에 저장된 단어가 없어 퀴즈를 진행할 수 없습니다.")
        if st.button("⬅ 허브로 돌아가기", use_container_width=True):
            st.session_state.armory_section = "hub"
            st.session_state.vocab_armory_mode = "study"
            st.rerun()
        return

    if "vocab_lives" not in st.session_state:
        st.session_state.vocab_lives = 3
    if "vocab_score" not in st.session_state:
        st.session_state.vocab_score = 0
    if "vocab_quiz_index" not in st.session_state:
        st.session_state.vocab_quiz_index = 0
    if "vocab_stats_updated" not in st.session_state:
        st.session_state.vocab_stats_updated = False
    if "vocab_last_result" not in st.session_state:
        st.session_state.vocab_last_result = None

    order = st.session_state.vocab_quiz_order
    idx = st.session_state.vocab_quiz_index
    total_q = len(order)
    lives = st.session_state.vocab_lives
    score = st.session_state.vocab_score

    if total_q == 0:
        st.info("이번 세트에 포함된 단어가 없습니다. 허브에서 다시 세트를 준비해 주세요.")
        if st.button("⬅ 허브로 돌아가기", use_container_width=True):
            st.session_state.armory_section = "hub"
            st.session_state.vocab_armory_mode = "study"
            st.rerun()
        return

    last = st.session_state.get("vocab_last_result")
    if last:
        if last["type"] == "correct":
            st.success(f"직전 카드 정답! {last['word']} : {last['meaning']}")
        elif last["type"] == "wrong":
            st.error(f"직전 카드 오답! {last['word']} : {last['meaning']}")
        elif last["type"] == "timeout":
            st.warning(f"시간초과! {last['word']} 카드를 놓쳤어요.")

        if last["type"] == "correct":
            if st.button(
                f"🧹 이제 '{last['word']}' 단어는 무기고에서 삭제하기",
                key="delete_last_vocab",
                use_container_width=True,
            ):
                new_list = [
                    v for v in st.session_state.secret_armory_vocab
                    if v["word"] != last["word"]
                ]
                st.session_state.secret_armory_vocab = new_list
                st.success(f"'{last['word']}' 단어가 무기고에서 삭제되었습니다.")
                st.session_state.vocab_last_result = None
                st.rerun()

    lives_clamped = max(0, min(3, lives))
    hearts = "❤️" * lives_clamped + "🤍" * (3 - lives_clamped)
    st.markdown(f"**{hearts} | 현재 점수 {score}/{total_q}**")

    if lives_clamped <= 0:
        st.error("목숨이 모두 소진되었습니다! 이번 세트는 여기까지예요.")
        st.info(f"최종 점수: {score} / {total_q}")

        col_retry, col_home = st.columns(2)
        with col_retry:
            if st.button("🔁 같은 무기고 단어로 다시 도전하기", use_container_width=True):
                prepare_vocab_quiz_set()
                st.session_state.vocab_armory_mode = "quiz"
                st.rerun()
        with col_home:
            if st.button("🏠 허브로 돌아가기", use_container_width=True):
                st.session_state.armory_section = "hub"
                st.session_state.vocab_armory_mode = "study"
                st.rerun()
        return

    if idx >= total_q:
        if not st.session_state.get("vocab_stats_updated", False):
            update_stats_after_vocab_set(score, total_q)
            st.session_state.vocab_stats_updated = True

        st.success("이번 Vocab Timebomb 타임어택 세트를 모두 마쳤습니다!")
        st.info(f"최종 점수: {score} / {total_q}")

        col_retry, col_home = st.columns(2)
        with col_retry:
            if st.button("🔁 같은 무기고 단어로 다시 도전하기", use_container_width=True):
                prepare_vocab_quiz_set()
                st.session_state.vocab_armory_mode = "quiz"
                st.rerun()
        with col_home:
            if st.button("🏠 허브로 돌아가기", use_container_width=True):
                st.session_state.armory_section = "hub"
                st.session_state.vocab_armory_mode = "study"
                st.rerun()
        return

    q_index = order[idx]
    target = vocab_set[q_index]
    eng_word = target["word"]
    kor_correct = target["meaning"]
    current_q_id = f"{idx}_{eng_word}"

    if st.session_state.get("vocab_q_current_id") != current_q_id:
        st.session_state.vocab_q_current_id = current_q_id
        st.session_state.vocab_q_start_time = _time.time()
        st.session_state.vocab_q_timeout_handled = False

    if st_autorefresh is not None:
        st_autorefresh(interval=1000, key="vocab_quiz_tick")

    start_time = st.session_state.get("vocab_q_start_time", _time.time())
    elapsed = _time.time() - start_time
    limit_sec = 3.0
    remaining = max(0.0, limit_sec - elapsed)

    st.markdown(f"⏱ 남은 시간: **{remaining:0.1f}초**")
    st.progress(remaining / limit_sec if limit_sec > 0 else 0)

    if remaining <= 0 and not st.session_state.get("vocab_q_timeout_handled", False):
        st.session_state.vocab_q_timeout_handled = True
        st.session_state.vocab_lives = max(0, lives_clamped - 1)
        st.session_state.vocab_quiz_index = idx + 1
        st.session_state.vocab_last_result = {
            "type": "timeout",
            "word": eng_word,
            "meaning": kor_correct,
        }
        st.warning("시간 초과! 이 카드는 자동으로 지나갔습니다.")
        st.rerun()

    st.write(f"문제 {idx + 1} / {total_q}")

    st.markdown("""
        <div style="
            font-size: 28px; font-weight: 700;
            padding: 10px 18px; border-radius: 14px;
            background-color: #fff3cd; display: inline-block;
            margin-top: 6px; margin-bottom: 12px;">
            🃏 {eng_word}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("👉 이 단어의 뜻 카드를 하나 골라보세요. (3초 안에 선택!)")

    meanings_pool = [v["meaning"] for v in vocab_set if v["meaning"] != kor_correct]
    seed = q_index * 7919 + len(kor_correct)
    rng = random.Random(seed)
    rng.shuffle(meanings_pool)

    distractors = meanings_pool[:3]
    options = [kor_correct] + distractors
    rng.shuffle(options)

    for j, opt in enumerate(options):
        label = f"🃏 {opt}"
        if st.button(label, key=f"vocab_opt_{idx}_{j}", use_container_width=True):
            if opt == kor_correct:
                st.session_state.vocab_score = score + 1
                st.session_state.vocab_last_result = {
                    "type": "correct",
                    "word": eng_word,
                    "meaning": kor_correct,
                }
            else:
                st.session_state.vocab_lives = max(0, lives_clamped - 1)
                st.session_state.vocab_last_result = {
                    "type": "wrong",
                    "word": eng_word,
                    "meaning": kor_correct,
                }

            st.session_state.vocab_quiz_index = idx + 1
            st.session_state.vocab_q_start_time = _time.time()
            st.session_state.vocab_q_timeout_handled = False
            st.rerun()

    if st.button("⚓ 퀴즈 중단하고 허브로 돌아가기", use_container_width=True):
        st.session_state.armory_section = "hub"
        st.session_state.vocab_armory_mode = "study"
        st.rerun()


def render_vocab_armory():
    st.markdown("## 📚 Vocab Timebomb – 단어 무기고 전장")

    vocab_set: List[Dict] = st.session_state.vocab_current_set

    if not st.session_state.secret_armory_vocab:
        st.info("현재 비밀 병기고에 저장된 단어가 없습니다.")
        if st.button("⬅ 허브로 돌아가기"):
            st.session_state.armory_section = "hub"
            st.rerun()
        return

    if not vocab_set:
        st.warning("먼저 허브에서 Vocab Timebomb 세트를 준비해 주세요.")
        if st.button("⬅ 허브로 돌아가기"):
            st.session_state.armory_section = "hub"
            st.rerun()
        return

    mode = st.session_state.vocab_armory_mode

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📖 학습 모드로 보기", use_container_width=True):
            st.session_state.vocab_armory_mode = "study"
            st.rerun()

    with col2:
        if st.button("🎯 퀴즈 모드로 도전", use_container_width=True):
            st.session_state.vocab_armory_mode = "quiz"
            st.rerun()

    st.markdown("---")

    if mode == "study":
        render_vocab_study_mode()
    else:
        render_vocab_quiz_mode()

# ============================================
# Score & Ranking 화면
# ============================================

def score_ranking_page():
    st.markdown("## 🏆 Score & Ranking – P7 + Vocab 종합 기록")

    stats = load_stats()
    p7 = stats.get("p7", {})
    vocab = stats.get("vocab", {})

    p7_sets = p7.get("total_sets", 0)
    p7_correct = p7.get("total_correct", 0)
    p7_total_q = p7.get("total_questions", 0)
    p7_acc = (p7_correct / p7_total_q * 100.0) if p7_total_q > 0 else 0.0
    p7_best_combo = p7.get("best_combo", 0)
    p7_last = p7.get("last_played", "")

    v_sets = vocab.get("total_sets", 0)
    v_correct = vocab.get("total_correct", 0)
    v_total_q = vocab.get("total_questions", 0)
    v_acc = (v_correct / v_total_q * 100.0) if v_total_q > 0 else 0.0
    v_best_score = vocab.get("best_score", 0)
    v_last = vocab.get("last_played", "")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📖 P7 Reading Arena 기록")
        st.metric("총 플레이 세트 수", p7_sets)
        st.metric("총 정답 수 / 총 문항 수", f"{p7_correct} / {p7_total_q}")
        st.metric("평균 정답률(%)", f"{p7_acc:.1f}%")
        st.metric("최고 콤보", f"{p7_best_combo} 연속")
        if p7_last:
            st.caption(f"마지막 플레이: {p7_last}")
        else:
            st.caption("아직 기록된 세트가 없습니다.")

        # ✅ 레벨 현황 테이블
        levels = get_all_p7_levels()
        if levels:
            st.markdown("#### 카테고리별 레벨 현황")
            rows = []
            for cat, info in levels.items():
                rows.append({
                    "Category": cat,
                    "Level": f"Lv{info.get('level', 1)}",
                    "Streak": f"{info.get('streak', 0)}/5",
                    "Cleared Sets": info.get("cleared_sets", 0),
                    "Total Sets": info.get("total_sets", 0),
                })
            st.table(rows)

    with col2:
        st.markdown("### 💣 Vocab Timebomb 기록")
        st.metric("총 퀴즈 세트 수", v_sets)
        st.metric("총 정답 수 / 총 문항 수", f"{v_correct} / {v_total_q}")
        st.metric("평균 정답률(%)", f"{v_acc:.1f}%")
        st.metric("한 세트 최고 점수", v_best_score)
        if v_last:
            st.caption(f"마지막 플레이: {v_last}")
        else:
            st.caption("아직 기록된 Vocab 세트가 없습니다.")

    st.markdown("---")
    st.info(
        "이 화면은 나만 보는 개인 랭킹 보드입니다. "
        "P7 세트와 Vocab Timebomb를 플레이할수록 기록과 레벨이 함께 쌓입니다."
    )

# ============================================
# Secret Armory 전체 페이지
# ============================================

def secret_armory_page():
    st.markdown("## 🧨 Secret Armory – 개인 비밀 무기고")

    init_armory_state()

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🏠 허브", use_container_width=True):
            st.session_state.armory_section = "hub"
    with col2:
        if st.button("💣 P5 무기고", use_container_width=True):
            st.session_state.armory_section = "p5"
    with col3:
        if st.button("📚 단어 무기고", use_container_width=True):
            st.session_state.armory_section = "vocab"

    st.markdown("---")

    section = st.session_state.armory_section
    if section == "hub":
        render_armory_hub()
    elif section == "p5":
        render_p5_armory()
    else:
        render_vocab_armory()

# ============================================
# 메인 엔트리
# ============================================

def run():
    """Entry point used by pages/01_P7_Reading_Arena.py and main_hub.py.
    This module renders ONLY the P7 Reading Arena battle screen (80% battlefield + 20% HUD).
    """
    init_session_state()
    return reading_arena_page()


# direct run safety (dev only)
if __name__ == "__main__":
    try:
        st.set_page_config(page_title="SnapQ P7 Reading Arena", page_icon="🔥", layout="wide", initial_sidebar_state="collapsed")
    except Exception:
        pass
    run()
    
    # ---- /P7_TOPSPACE_FINAL_V3 ----
















# ===== P7_FORCE_TEXT_X12_BOLD (DO NOT EDIT) =====
try:
    import streamlit as st
    st.markdown(r'''<style>
/* ===== P7_FORCE_TEXT_X12_BOLD_CSS ===== */
/* Passage / Question (p7-zone body text) */
.p7-pack .p7-zone .p7-zone-body{
  font-size: 30px !important;   /* ~18px * 1.2 = 21.6 -> 22px */
  font-weight: 900 !important;
}

/* Some variants may use mission zone */
.p7-pack .p7-zone.mission .p7-zone-body{
  font-size: 23px !important;
  font-weight: 900 !important;
}

/* Options (radio style) */
.p7-pack div[role="radiogroup"] > label,
.p7-pack div[role="radiogroup"] > label *{
  font-size: 19px !important;   /* ~16px * 1.2 = 19.2 -> 19px */
  font-weight: 950 !important;
}

/* Options (button style fallback, if ever used) */
.p7-pack .p7-opt-wrap div[data-testid="stButton"] > button,
.p7-pack .p7-opt-wrap div[data-testid="stButton"] > button *{
  font-size: 19px !important;
  font-weight: 900 !important;
}

/* HUD는 절대 건드리지 않음(보호막) */
.p7-pack .p7-hud,
.p7-pack .p7-hud *{
  font-size: inherit !important;
  font-weight: inherit !important;
}
/* ===== /P7_FORCE_TEXT_X12_BOLD_CSS ===== */
</style>''', unsafe_allow_html=True)
except Exception:
    pass
# ===== /P7_FORCE_TEXT_X12_BOLD =====

# ===== P7_TEXT_FORCE_X1P2_V3 (CSS ONLY / LAST WINS) =====
try:
    import streamlit as st
    st.markdown(r"""
    <style>
    /* === P7_TEXT_FORCE_X1P2_V3 === */
    /* 1) Passage + Question text only */
    .p7-zone .p7-zone-body,
    .p7-zone .p7-zone-body p,
    .p7-zone .p7-zone-body span,
    .p7-zone .p7-zone-body strong,
    .p7-zone .p7-zone-body em{
      font-size: 30px !important;   /* 18px * 1.2 ~= 21.6px -> 22px */
      font-weight: 900 !important;  /* thicker */
    }

    /* 2) Options (radio) text only - scoped to p7-opt-wrap to avoid other radios */
    .p7-opt-wrap div[role="radiogroup"] > label{
      font-size: 1em !important;    /* reset base to prevent double scaling */
      font-weight: 400 !important;  /* label itself normal */
    }

    .p7-opt-wrap div[role="radiogroup"] > label p,
    .p7-opt-wrap div[role="radiogroup"] > label span,
    .p7-opt-wrap div[role="radiogroup"] > label strong,
    .p7-opt-wrap div[role="radiogroup"] > label em,
    .p7-opt-wrap div[role="radiogroup"] > label [data-testid="stMarkdownContainer"] p,
    .p7-opt-wrap div[role="radiogroup"] > label [data-testid="stMarkdownContainer"] span{
      font-size: 1.2em !important;  /* +20% exactly once */
      font-weight: 900 !important;  /* thicker */
    }

    /* (If options are buttons in some modes) */
    .p7-opt-wrap div[data-testid="stButton"] > button,
    .p7-opt-wrap div[data-testid="stButton"] > button *{
      font-size: 1.2em !important;
      font-weight: 900 !important;
    }
    /* === /P7_TEXT_FORCE_X1P2_V3 === */
    
/* ===== P7_TEXTBOOST_FORCE_V1 (TEXT ONLY) =======================
   - No layout change, only typography boost
   ============================================================ */

/* Passage + Question: we will target by adding .p7-textboost class */
.p7-zone .p7-textboost{
  font-size: 1.20em !important;
  font-weight: 900 !important;
  line-height: 1.25 !important;
  letter-spacing: 0.1px !important;
}
.p7-zone .p7-textboost *{
  font-size: inherit !important;
  font-weight: inherit !important;
}

/* Options (st.radio / BaseWeb) — text only */
div[role="radiogroup"] label[data-baseweb="radio"] span,
div[role="radiogroup"] label[data-baseweb="radio"] p{
  font-size: 1.20em !important;
  font-weight: 900 !important;
  letter-spacing: 0.1px !important;
}

/* Mobile safety */
@media (max-width: 540px){
  .p7-zone .p7-textboost{ font-size: 1.15em !important; }
}
/* ===== /P7_TEXTBOOST_FORCE_V1 ================================ */
</style>
    """, unsafe_allow_html=True)
except Exception:
    pass
# ===== /P7_TEXT_FORCE_X1P2_V3 =====

























