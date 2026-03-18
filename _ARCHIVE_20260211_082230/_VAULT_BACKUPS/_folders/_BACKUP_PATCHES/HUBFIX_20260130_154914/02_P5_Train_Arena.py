# pages/02_P5_Train_Arena.py
import random
from typing import Any, Dict, List

import streamlit as st
from app.core.ui_shell import apply_ui_shell

apply_ui_shell(theme="armory")

try:
    from app.core.battle_theme import apply_battle_theme
    apply_battle_theme()
except Exception:
    pass

from app.arenas import secret_armory as arena  # type: ignore[attr-defined]

st.set_page_config(
    page_title="🟩 P5 TRAIN · SnapQ TOEIC",
    page_icon="🟩",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CSS: 2x2 카드형 버튼 + 가독성 강제 + 하단 3버튼 색 분리
# ============================================================
st.markdown(
    r"""
<style>
.block-container{ max-width: 1100px !important; padding-top: 1.1rem !important; padding-bottom: 1.6rem !important; }

/* 문제 박스 */
.p5-qbox{
  background: rgba(255,255,255,.97);
  border: 3px solid rgba(17,24,39,.26);
  border-radius: 18px;
  padding: 14px 16px;
  box-shadow: 0 18px 40px rgba(0,0,0,.16);
}
.p5-qtext{
  color:#111827 !important;
  font-weight: 950 !important;
  font-size: 26px !important;
  line-height: 1.48 !important;
  text-shadow:none !important;
}

/* ✅ 선택지 카드 버튼 */
.p5-optbtn div[data-testid="stButton"] > button{
  /* ⬆️ 한 톤 밝게 */
  background: rgba(255,255,255,.24) !important;
  border: 1px solid rgba(255,255,255,.46) !important;

  border-radius: 18px !important;
  min-height: 82px !important;           /* 모바일 터치 크게 */
  box-shadow: 0 14px 30px rgba(0,0,0,.14) !important;
}
.p5-optbtn div[data-testid="stButton"] > button:hover{
  border: 1px solid rgba(255,255,255,.70) !important;
  transform: translateY(-1px);
}

/* ✅ 선택지 글자 선명 강제(묻힘 방지) */
.p5-optbtn div[data-testid="stButton"] > button *,
.p5-bottom div[data-testid="stButton"] > button *{
  color:#f9fafb !important;
  opacity: 1 !important;
  text-shadow: none !important;
  filter: none !important;
  -webkit-text-fill-color:#f9fafb !important;
  font-weight: 950 !important;
}

/* 선택 저장 배너 */
.p5-pickbar{
  margin-top: 12px;
  padding: 10px 12px;
  border-radius: 14px;
  background: rgba(255,255,255,.94);
  border: 1px solid rgba(17,24,39,.14);
  font-weight: 950;
  color:#111827 !important;
  box-shadow: 0 10px 24px rgba(0,0,0,.10);
}

/* BRIEF 카드 */
.p5-brief{
  margin-top: 10px;
  background: rgba(255,255,255,.97) !important;
  border: 2px solid rgba(17,24,39,.12);
  border-radius: 18px;
  padding: 12px 14px;
  box-shadow: 0 16px 36px rgba(0,0,0,.12);
}
.p5-brief, .p5-brief *{ color:#111827 !important; text-shadow:none !important; }
.p5-status{
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid rgba(17,24,39,.14);
  box-shadow: 0 10px 22px rgba(0,0,0,.10);
  font-weight: 950;
  margin-bottom: 10px;
}
.p5-status.ok{ background: rgba(34,197,94,.14); border-color: rgba(34,197,94,.35); }
.p5-status.bad{ background: rgba(244,63,94,.12); border-color: rgba(244,63,94,.30); }
.p5-status.neu{ background: rgba(148,163,184,.16); border-color: rgba(148,163,184,.28); }

.p5-row{
  margin: 9px 0;
  padding: 10px 12px;
  border-radius: 14px;
  border: 1px solid rgba(17,24,39,.10);
  background: rgba(255,255,255,.78);
}
.p5-k{ font-weight: 950; margin-bottom: 6px; }
.p5-hl{
  display:inline-block;
  padding: 2px 7px;
  border-radius: 10px;
  background: rgba(255,230,0,.35);
  border: 1px solid rgba(255,230,0,.45);
  font-weight: 950;
}
.p5-pencil{ color: rgba(17,24,39,.85) !important; font-weight: 850; }
.p5-pen{ color: rgba(30,64,175,.95) !important; font-weight: 900; }

/* 오답 시 시험포인트 펄스 */
@keyframes p5pulse {
  0%   { box-shadow: 0 0 0 rgba(244,63,94,0.0); border-color: rgba(244,63,94,.22); }
  50%  { box-shadow: 0 0 0 6px rgba(244,63,94,0.10); border-color: rgba(244,63,94,.45); }
  100% { box-shadow: 0 0 0 rgba(244,63,94,0.0); border-color: rgba(244,63,94,.22); }
}
.p5-focus{ animation: p5pulse 1.2s ease-in-out infinite; border-width: 2px !important; }

/* BRIEF 닫기 버튼 */
.p5-close-wrap div[data-testid="stButton"] > button{
  color:#111827 !important;
  background: rgba(255,255,255,.92) !important;
  border: 2px solid rgba(17,24,39,.24) !important;
  border-radius: 12px !important;
  font-weight: 950 !important;
  min-height: 40px !important;
  padding: 4px 10px !important;
}

/* 하단 3버튼 색 분리 */
.p5-bottom div[data-testid="stButton"] > button{
  min-height: 72px !important;
  border-radius: 16px !important;
  font-size: 18px !important;

  /* ⬆️ 한 톤 밝게 */
  border: 1px solid rgba(255,255,255,.34) !important;
  box-shadow: 0 14px 30px rgba(0,0,0,.16) !important;
}
.p5-bbtn-brief  div[data-testid="stButton"] > button{
  background: linear-gradient(180deg, rgba(96,165,250,.46), rgba(59,130,246,.26)) !important;
}
.p5-bbtn-discard div[data-testid="stButton"] > button{
  background: linear-gradient(180deg, rgba(74,222,128,.44), rgba(34,197,94,.26)) !important;
}
.p5-bbtn-next   div[data-testid="stButton"] > button{
  background: linear-gradient(180deg, rgba(168,85,247,.44), rgba(236,72,153,.20)) !important;
}

/* ============================================================
   P5 TRAIN UI FIX: Visibility + Bottom Colors + No Wrap
   ============================================================ */

/* ✅ 버튼 텍스트 선명화(선택지 + 하단) : DOM 변형에도 먹게 *까지 */
.p5-optbtn div[data-testid="stButton"] > button *,
.p5-bottom div[data-testid="stButton"] > button *{
  color: #f9fafb !important;
  opacity: 1 !important;
  filter: none !important;
  -webkit-text-fill-color: #f9fafb !important;
  font-weight: 950 !important;

  /* ✅ 윤곽 더 강하게 + 얇은 stroke */
  text-shadow:
    0 1px 2px rgba(0,0,0,.75),
    0 3px 12px rgba(0,0,0,.55) !important;
  -webkit-text-stroke: 0.4px rgba(0,0,0,.35);
}

/* ✅ 하단 3버튼: 줄바꿈 방지 + 높이 통일 */
.p5-bottom div[data-testid="stButton"] > button{
  min-height: 72px !important;
  border-radius: 16px !important;
}
.p5-bottom div[data-testid="stButton"] > button span{
  white-space: nowrap !important;       /* ✅ 줄바꿈 방지 */
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

/* ✅ 하단 버튼 색감 분리(기능별) */
.p5-bbtn-brief  div[data-testid="stButton"] > button{
  background: linear-gradient(180deg, rgba(96,165,250,.50), rgba(59,130,246,.26)) !important;
  border: 1px solid rgba(147,197,253,.65) !important;
}
.p5-bbtn-discard div[data-testid="stButton"] > button{
  background: linear-gradient(180deg, rgba(74,222,128,.48), rgba(34,197,94,.26)) !important;
  border: 1px solid rgba(134,239,172,.65) !important;
}
.p5-bbtn-next   div[data-testid="stButton"] > button{
  background: linear-gradient(180deg, rgba(168,85,247,.48), rgba(236,72,153,.20)) !important;
  border: 1px solid rgba(216,180,254,.65) !important;
}

/* ✅ 선택지 버튼 배경/테두리도 대비 살짝 업 */
.p5-optbtn div[data-testid="stButton"] > button{
  background: rgba(255,255,255,.24) !important;
  border: 1px solid rgba(255,255,255,.46) !important;
}
.p5-optbtn div[data-testid="stButton"] > button:hover{
  border: 1px solid rgba(255,255,255,.70) !important;
}

/* =========================
   P5 TRAIN READABILITY OVERRIDE (SAFE APPEND)
   ========================= */
.p5-optbtn div[data-testid="stButton"] > button,
.p5-bottom div[data-testid="stButton"] > button{
  background: rgba(255,255,255,.24) !important;
  border: 1px solid rgba(255,255,255,.46) !important;
}

.p5-optbtn div[data-testid="stButton"] > button:hover,
.p5-bottom div[data-testid="stButton"] > button:hover{
  background: rgba(255,255,255,.30) !important;
  border: 1px solid rgba(255,255,255,.70) !important;
}

.p5-optbtn div[data-testid="stButton"] > button *,
.p5-bottom div[data-testid="stButton"] > button *{
  color:#ffffff !important;
  opacity: 1 !important;
  -webkit-text-fill-color:#ffffff !important;
  font-weight: 950 !important;
  text-shadow:
    0 1px 2px rgba(0,0,0,.78),
    0 3px 12px rgba(0,0,0,.55) !important;
  -webkit-text-stroke: 0.45px rgba(0,0,0,.35);
}
/* ============================================================
   A-PATCH: "문제집 가독성" CSS ONLY (SAFE OVERRIDE)
   - 선택지 4개: 오프화이트 종이 + 검정 글자
   - 하단 3버튼: 파랑/초록/보라로 기능 분리 + 흰 글자
   ============================================================ */

/* (1) 선택지 버튼(4개) = 문제집 종이 */
.p5-optbtn div[data-testid="stButton"] > button{
  background: rgba(248,250,252,0.98) !important;   /* 종이톤 */
  border: 2px solid rgba(203,213,225,0.95) !important;
  box-shadow: 0 14px 30px rgba(0,0,0,.14) !important;
}

/* 선택지 글자 = 검정 + 굵게 (배경과 분리) */
.p5-optbtn div[data-testid="stButton"] > button,
.p5-optbtn div[data-testid="stButton"] > button *{
  color: #111827 !important;
  -webkit-text-fill-color: #111827 !important;
  text-shadow: none !important;
  -webkit-text-stroke: 0px transparent !important;
  font-weight: 900 !important;
  opacity: 1 !important;
}

/* hover: 문제집 형광펜 느낌 살짝 */
.p5-optbtn div[data-testid="stButton"] > button:hover{
  background: rgba(254,249,195,0.98) !important;  /* 연노랑 */
  border: 2px solid rgba(251,191,36,0.95) !important;
}

/* (2) 하단 3버튼(Brief/폐기/다음) = 의미가 보이게 색상 분리 */
.p5-bottom div[data-testid="stButton"] > button{
  border-radius: 18px !important;
  min-height: 74px !important;
  font-size: 19px !important;
  font-weight: 950 !important;
  letter-spacing: 0.2px;
  box-shadow: 0 14px 30px rgba(0,0,0,.18) !important;
  border: 2px solid rgba(255,255,255,.18) !important;
}

/* 하단 버튼 글자 = 흰색 + 윤곽 */
.p5-bottom div[data-testid="stButton"] > button,
.p5-bottom div[data-testid="stButton"] > button *{
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  text-shadow: 0 2px 10px rgba(0,0,0,.55) !important;
  -webkit-text-stroke: 0.35px rgba(0,0,0,.25);
  opacity: 1 !important;
}

/* BRIEF = 파랑(해설/학습) */
.p5-bbtn-brief div[data-testid="stButton"] > button{
  background: linear-gradient(180deg, rgba(59,130,246,.92), rgba(37,99,235,.62)) !important;
  border: 2px solid rgba(147,197,253,.70) !important;
}

/* 폐기 = 초록(정리/관리) */
.p5-bbtn-discard div[data-testid="stButton"] > button{
  background: linear-gradient(180deg, rgba(34,197,94,.92), rgba(22,163,74,.62)) !important;
  border: 2px solid rgba(134,239,172,.70) !important;
}

/* 다음 = 보라(진행/출격) */
.p5-bbtn-next div[data-testid="stButton"] > button{
  background: linear-gradient(180deg, rgba(168,85,247,.92), rgba(124,58,237,.62)) !important;
  border: 2px solid rgba(216,180,254,.70) !important;
}

/* (3) 선택 저장 바(현재 흰 바)도 글자 또렷하게 */
.p5-pickbar, .p5-pickbar *{
  color:#111827 !important;
  text-shadow:none !important;
  font-weight: 950 !important;
}
/* ============================================================
   B2-PATCH: P5 TRAIN "프리미엄 문제집(아이보리)" + WHITE TEXT (SAFE OVERRIDE)
   - 선택지 4개: 아이보리 종이톤 + 글자 흰색(윤곽 강)
   - 하단 3버튼: 기존 색 유지 + 글자 흰색 더 강
   ============================================================ */

/* (A) 선택지 박스 = 아이보리(프리미엄 종이) */
.p5-optbtn div[data-testid="stButton"] > button{
  background: rgba(255, 248, 235, 0.92) !important;  /* 아이보리 종이 */
  border: 2px solid rgba(226, 232, 240, 0.55) !important;
  box-shadow: 0 18px 34px rgba(0,0,0,.18) !important;
}

/* (B) 선택지 글자 = 흰색 강제 + 윤곽/그림자(문제집+게임 혼합) */
.p5-optbtn div[data-testid="stButton"] > button,
.p5-optbtn div[data-testid="stButton"] > button *{
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  font-weight: 950 !important;
  opacity: 1 !important;

  /* 윤곽 강화 */
  text-shadow:
    0 1px 2px rgba(0,0,0,.82),
    0 6px 18px rgba(0,0,0,.55) !important;
  -webkit-text-stroke: 0.55px rgba(0,0,0,.38);
}

/* hover = 살짝 더 밝은 종이 + 테두리 강조 */
.p5-optbtn div[data-testid="stButton"] > button:hover{
  background: rgba(255, 252, 245, 0.96) !important;
  border: 2px solid rgba(148,163,184,0.65) !important;
}

/* (C) 하단 3버튼 글자 = 흰색 더 또렷(이미 흰색이지만 더 강하게) */
.p5-bottom div[data-testid="stButton"] > button,
.p5-bottom div[data-testid="stButton"] > button *{
  color:#ffffff !important;
  -webkit-text-fill-color:#ffffff !important;
  font-weight: 950 !important;
  opacity: 1 !important;
  text-shadow:
    0 2px 12px rgba(0,0,0,.60),
    0 1px 2px rgba(0,0,0,.70) !important;
  -webkit-text-stroke: 0.45px rgba(0,0,0,.28);
}

/* (D) 하단 버튼: 살짝 더 쨍하게(톤업) */
.p5-bbtn-brief div[data-testid="stButton"] > button{
  filter: brightness(1.08) saturate(1.05);
}
.p5-bbtn-discard div[data-testid="stButton"] > button{
  filter: brightness(1.08) saturate(1.05);
}
.p5-bbtn-next div[data-testid="stButton"] > button{
  filter: brightness(1.08) saturate(1.05);
}
/* ============================================================
   B-HYBRID PATCH: "문제집 감성 유지 + 눈 편하게"
   - 선택지 4개: 밝은 종이 면(아이보리/오프화이트) + 흰 테두리 + 흰 글자 윤곽
   - 하단 3버튼: 의미색 유지 + 밝기/대비/흰 테두리 강화
   ============================================================ */

/* (0) 공통: 버튼이 배경에 묻히지 않게 살짝 유리판 느낌 */
.p5-optbtn div[data-testid="stButton"] > button,
.p5-bottom  div[data-testid="stButton"] > button{
  backdrop-filter: blur(6px);
}

/* (1) 선택지 4개 박스 = "밝은 종이 면" + 흰 테두리 */
.p5-optbtn div[data-testid="stButton"] > button{
  background: linear-gradient(180deg,
    rgba(255,252,245,0.55),
    rgba(255,248,235,0.28)
  ) !important; /* 종이톤(밝은 면) */
  border: 2px solid rgba(255,255,255,0.72) !important; /* 흰 테두리 */
  box-shadow: 0 18px 34px rgba(0,0,0,.22) !important;
}

/* 선택지 hover: 더 밝게 + 테두리 더 쨍하게 */
.p5-optbtn div[data-testid="stButton"] > button:hover{
  background: linear-gradient(180deg,
    rgba(255,252,245,0.70),
    rgba(255,248,235,0.40)
  ) !important;
  border: 2px solid rgba(255,255,255,0.92) !important;
}

/* (2) 선택지 글자 = 흰색 + 윤곽(강) */
.p5-optbtn div[data-testid="stButton"] > button,
.p5-optbtn div[data-testid="stButton"] > button *{
  color:#ffffff !important;
  -webkit-text-fill-color:#ffffff !important;
  font-weight: 950 !important;
  opacity: 1 !important;
  text-shadow:
    0 2px 14px rgba(0,0,0,.65),
    0 1px 2px rgba(0,0,0,.80) !important;
  -webkit-text-stroke: 0.55px rgba(0,0,0,.40);
}

/* (3) 하단 3버튼 = 의미색 유지 + 밝기 업 + 흰 테두리 */
.p5-bottom div[data-testid="stButton"] > button{
  border: 2px solid rgba(255,255,255,0.70) !important;
  box-shadow: 0 18px 34px rgba(0,0,0,.24) !important;
  filter: brightness(1.14) saturate(1.08);
}

/* 하단 글자 = 흰색 + 더 또렷 */
.p5-bottom div[data-testid="stButton"] > button,
.p5-bottom div[data-testid="stButton"] > button *{
  color:#ffffff !important;
  -webkit-text-fill-color:#ffffff !important;
  font-weight: 950 !important;
  opacity: 1 !important;
  text-shadow:
    0 2px 14px rgba(0,0,0,.62),
    0 1px 2px rgba(0,0,0,.78) !important;
  -webkit-text-stroke: 0.45px rgba(0,0,0,.30);
}

/* (4) 선택 저장 바는 "문제집 메모지"처럼 더 밝게 */
.p5-pickbar{
  background: rgba(255,255,255,0.96) !important;
  border: 2px solid rgba(255,255,255,0.85) !important;
  box-shadow: 0 16px 30px rgba(0,0,0,.14) !important;
}
.p5-pickbar, .p5-pickbar *{
  color:#111827 !important;
  -webkit-text-fill-color:#111827 !important;
  text-shadow: none !important;
  font-weight: 950 !important;
}
/* ============================================================
   STEP1 PATCH: 선택지 박스 "문제집화" (OPTIONS ONLY)
   - 밝은 종이 면 + 흰 테두리 + 카드 그림자 + hover 형광펜
   ============================================================ */

/* 선택지 버튼: 카드(종이)처럼 '밝은 면' + 또렷한 흰 테두리 */
.p5-optbtn div[data-testid="stButton"] > button{
  background: linear-gradient(180deg,
    rgba(255, 253, 248, 0.92),
    rgba(255, 248, 235, 0.70)
  ) !important; /* 프리미엄 종이 */
  border: 2.5px solid rgba(255,255,255,0.92) !important; /* 흰 테두리 선명 */
  box-shadow:
    0 18px 36px rgba(0,0,0,.22),
    inset 0 1px 0 rgba(255,255,255,.55) !important; /* 종이 질감 */
  border-radius: 20px !important;
}

/* 선택지 hover: 형광펜 느낌(은은한 노랑) + 살짝 떠오름 */
.p5-optbtn div[data-testid="stButton"] > button:hover{
  background: linear-gradient(180deg,
    rgba(254, 249, 195, 0.92),
    rgba(255, 248, 235, 0.74)
  ) !important;
  border: 2.5px solid rgba(255,255,255,1.00) !important;
  transform: translateY(-1px);
  box-shadow:
    0 22px 44px rgba(0,0,0,.26),
    inset 0 1px 0 rgba(255,255,255,.65) !important;
}

/* 선택지 active(클릭): 눌림 효과 */
.p5-optbtn div[data-testid="stButton"] > button:active{
  transform: translateY(0px);
  box-shadow:
    0 14px 28px rgba(0,0,0,.20),
    inset 0 2px 0 rgba(0,0,0,.06) !important;
}

/* 선택지 글자: 현재 '흰색' 방향 유지 + 윤곽(검정)으로 확실히 */
.p5-optbtn div[data-testid="stButton"] > button,
.p5-optbtn div[data-testid="stButton"] > button *{
  color:#ffffff !important;
  -webkit-text-fill-color:#ffffff !important;
  font-weight: 950 !important;
  opacity: 1 !important;
  text-shadow:
    0 2px 16px rgba(0,0,0,.70),
    0 1px 2px rgba(0,0,0,.85) !important;
  -webkit-text-stroke: 0.60px rgba(0,0,0,.42);
}
/* ============================================================
   B-2 FINAL PATCH: "문제집 최종안"
   - 선택지(4개) = 밝은 종이 + 검정 글자(가독성 최우선)
   - hover = 형광펜 노랑
   - 하단 3버튼은 기존(흰 글자) 유지
   ============================================================ */

/* (1) 선택지 박스: 거의 흰 종이(아이보리 살짝) + 깔끔한 테두리 */
.p5-optbtn div[data-testid="stButton"] > button{
  background: linear-gradient(180deg,
    rgba(255, 255, 255, 0.98),
    rgba(255, 248, 235, 0.92)
  ) !important; /* 종이 */
  border: 2px solid rgba(203,213,225,0.95) !important; /* 연회색 테두리 */
  box-shadow:
    0 18px 36px rgba(0,0,0,.18),
    inset 0 1px 0 rgba(255,255,255,.75) !important;
  border-radius: 20px !important;
}

/* (2) 선택지 글자: 검정(문제집 룰) */
.p5-optbtn div[data-testid="stButton"] > button,
.p5-optbtn div[data-testid="stButton"] > button *{
  color:#111827 !important;
  -webkit-text-fill-color:#111827 !important;
  font-weight: 950 !important;
  opacity: 1 !important;
  text-shadow: none !important;
  -webkit-text-stroke: 0px transparent !important;
}

/* (3) hover: 형광펜 */
.p5-optbtn div[data-testid="stButton"] > button:hover{
  background: linear-gradient(180deg,
    rgba(254, 249, 195, 0.98),
    rgba(255, 248, 235, 0.92)
  ) !important; /* 형광펜 노랑 */
  border: 2px solid rgba(251,191,36,0.95) !important;
  transform: translateY(-1px);
  box-shadow:
    0 22px 44px rgba(0,0,0,.22),
    inset 0 1px 0 rgba(255,255,255,.85) !important;
}

/* (4) active(클릭): 눌림 */
.p5-optbtn div[data-testid="stButton"] > button:active{
  transform: translateY(0px);
  box-shadow:
    0 14px 28px rgba(0,0,0,.16),
    inset 0 2px 0 rgba(0,0,0,.06) !important;
}
/* ============================================================
   FORCE-PAPER PATCH (OPTIONS MUST WIN)
   - Default ALL buttons -> Paper + BLACK text
   - Then .p5-bottom buttons -> HUD + WHITE text (restore)
   ============================================================ */

/* A) 기본: 모든 버튼을 일단 "문제집 종이"로 강제 */
div[data-testid="stButton"] > button{
  background: linear-gradient(180deg,
    rgba(255,255,255,0.98),
    rgba(255,248,235,0.92)
  ) !important;
  border: 2px solid rgba(203,213,225,0.95) !important;
  border-radius: 20px !important;
  box-shadow: 0 18px 36px rgba(0,0,0,.18) !important;
}

/* 모든 버튼 글자 = 검정(문제집 룰) */
div[data-testid="stButton"] > button,
div[data-testid="stButton"] > button *{
  color:#111827 !important;
  -webkit-text-fill-color:#111827 !important;
  font-weight: 950 !important;
  text-shadow: none !important;
  -webkit-text-stroke: 0px transparent !important;
  opacity: 1 !important;
}

/* hover: 형광펜 */
div[data-testid="stButton"] > button:hover{
  background: linear-gradient(180deg,
    rgba(254,249,195,0.98),
    rgba(255,248,235,0.92)
  ) !important;
  border: 2px solid rgba(251,191,36,0.95) !important;
}

/* B) 예외: 하단 3버튼(.p5-bottom)만 다시 HUD로 복구 */
.p5-bottom div[data-testid="stButton"] > button{
  background: rgba(17,24,39,0.38) !important;
  border: 2px solid rgba(255,255,255,0.55) !important;
  box-shadow: 0 18px 36px rgba(0,0,0,.24) !important;
}

/* 하단 3버튼 글자 = 흰색 + 윤곽 */
.p5-bottom div[data-testid="stButton"] > button,
.p5-bottom div[data-testid="stButton"] > button *{
  color:#ffffff !important;
  -webkit-text-fill-color:#ffffff !important;
  text-shadow: 0 2px 12px rgba(0,0,0,.60) !important;
  -webkit-text-stroke: 0.35px rgba(0,0,0,.25);
}
/* ============================================================
   BRIEF BOTTOM SHEET PATCH (Mobile-first)
   - .p5-brief becomes a bottom sheet (fixed)
   - backdrop shown when injected div exists
   - close area sticky
   ============================================================ */

/* backdrop (we will inject a div when brief is open) */
.p5-sheet-backdrop{
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.45);
  backdrop-filter: blur(3px);
  z-index: 9990;
}

/* BRIEF card as bottom sheet */
.p5-brief{
  position: fixed !important;
  left: 50% !important;
  transform: translateX(-50%) !important;

  /* bottom sheet placement */
  bottom: 14px !important;

  /* size */
  width: min(980px, calc(100vw - 22px)) !important;
  max-height: 72vh !important;
  overflow: auto !important;

  /* visual */
  border-radius: 20px !important;
  z-index: 9999 !important;
}

/* mobile: 조금 더 꽉 차게 */
@media (max-width: 768px){
  .p5-brief{
    width: calc(100vw - 16px) !important;
    bottom: 8px !important;
    max-height: 78vh !important;
  }
}

/* "노트 덮기"가 들어있는 상단 줄을 항상 보이게(스크롤 중에도) */
.p5-brief .p5-close-wrap{
  position: sticky;
  top: 8px;
  z-index: 10000;
}

/* BRIEF 내부 첫 줄(헤더)이 배경에 묻히지 않게 */
.p5-brief{
  box-shadow: 0 24px 60px rgba(0,0,0,.35) !important;
}

/* 하단 3버튼은 z-index 낮게 (BRIEF가 위에 뜨게) */
.p5-bottom{
  position: relative;
  z-index: 1;
}
/* NAVPILL_CSS: tiny Main Hub pill */
.snapq-navpill-row{ display:flex; align-items:center; justify-content:space-between; gap:10px; margin-top: 2px; }
.snapq-navpill-title{ font-size: 2.0rem; font-weight: 900; letter-spacing: .2px; }
.snapq-navpill-wrap div[data-testid="stButton"] > button{
  width: auto !important;
  min-height: 36px !important;
  padding: 6px 10px !important;
  border-radius: 999px !important;
  font-size: 0.95rem !important;
  font-weight: 900 !important;
  background: rgba(255,255,255,0.92) !important;
  border: 2px solid rgba(203,213,225,0.95) !important;
  box-shadow: 0 10px 22px rgba(0,0,0,.14) !important;
}
.snapq-navpill-wrap div[data-testid="stButton"] > button:hover{
  background: rgba(254,249,195,0.98) !important;
  border-color: rgba(251,191,36,0.95) !important;
}
/* HEADER_ALIGN_CSS: one-line header (title left + hub pill right) */
.snapq-header{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap: 12px;
  margin-top: 6px;
  margin-bottom: 10px;
}
.snapq-title{
  display:flex;
  align-items:center;
  gap: 10px;
  color:#f9fafb;
  font-weight: 950;
  font-size: 2.15rem;
  letter-spacing: .2px;
  line-height: 1.05;
}
.snapq-title .sq-dot{
  width: 18px;
  height: 18px;
  border-radius: 5px;
  background: linear-gradient(180deg, rgba(34,197,94,.95), rgba(16,185,129,.65));
  box-shadow: 0 8px 18px rgba(0,0,0,.25);
  flex: 0 0 auto;
}
.snapq-hubpill div[data-testid="stButton"] > button{
  width: auto !important;
  min-height: 36px !important;
  padding: 6px 12px !important;
  border-radius: 999px !important;
  font-size: 0.95rem !important;
  font-weight: 950 !important;
  background: rgba(255,255,255,0.92) !important;
  border: 2px solid rgba(203,213,225,0.95) !important;
  box-shadow: 0 10px 22px rgba(0,0,0,.14) !important;
}
.snapq-hubpill div[data-testid="stButton"] > button:hover{
  background: rgba(254,249,195,0.98) !important;
  border-color: rgba(251,191,36,0.95) !important;
}
/* HUB_ULTRAMINI_CSS: make hub button as tiny icon, no extra header height */
.snapq-header{ margin-top: 4px !important; margin-bottom: 8px !important; }
.snapq-title{ font-size: 2.10rem !important; line-height: 1.02 !important; }

.snapq-hubpill div[data-testid="stButton"] > button{
  width: 42px !important;          /* 아이콘만 */
  min-width: 42px !important;
  max-width: 42px !important;
  min-height: 32px !important;
  height: 32px !important;
  padding: 0 !important;           /* 공간 최소 */
  border-radius: 12px !important;  /* 너무 둥글지 않게 */
  font-size: 18px !important;
  font-weight: 950 !important;
  background: rgba(255,255,255,0.92) !important;
  border: 2px solid rgba(203,213,225,0.95) !important;
  box-shadow: 0 8px 16px rgba(0,0,0,.12) !important;
}
.snapq-hubpill div[data-testid="stButton"] > button:hover{
  background: rgba(254,249,195,0.98) !important;
  border-color: rgba(251,191,36,0.95) !important;
}
/* ============================================================
   SPACING PATCH: 문제-선택지 간격↑ / 선택지끼리 간격↓ (문제집 레이아웃)
   ============================================================ */

/* 1) 문제 박스 아래 여백을 크게: 선택지 시작을 더 아래로 */
.p5-qbox{
  margin-bottom: 42px !important;   /* 기본보다 크게 (체감 3배 느낌) */
}

/* 2) 선택지 버튼(4개) 사이 간격을 줄이기 */
.p5-optbtn div[data-testid="stButton"]{
  margin-top: 4px !important;
  margin-bottom: 4px !important;    /* 기존보다 1/3 수준으로 촘촘하게 */
}

/* 3) 혹시 column wrapper가 여백을 잡으면 같이 줄이기 */
div[data-testid="column"] .stButton{
  margin-top: 4px !important;
  margin-bottom: 4px !important;
}
/* ============================================================
   ROW-GAP PATCH: 선택지 윗줄(2개) ↔ 아랫줄(2개) 간격을 더 붙이기
   - 목적: 4개 선택지를 "한 덩어리"로 보이게
   ============================================================ */

/* 선택지 버튼 wrapper 마진을 더 촘촘하게 */
.p5-optbtn div[data-testid="stButton"]{
  margin-top: 2px !important;
  margin-bottom: 2px !important;
}

/* column 내부 버튼 마진도 함께 */
div[data-testid="column"] .stButton{
  margin-top: 2px !important;
  margin-bottom: 2px !important;
}

/* 두 줄 사이를 벌리는 원인 중 하나: column wrapper의 기본 gap/padding 제거 시도 */
div[data-testid="stHorizontalBlock"]{
  row-gap: 6px !important;   /* (기본보다 줄이기) */
}

/* 혹시 두 번째 줄 시작 전에 생기는 여백이 있으면 줄이기 */
div[data-testid="stHorizontalBlock"] > div{
  padding-top: 0px !important;
  margin-top: 0px !important;
}
/* ============================================================
   OPTIONS GAP x0.5 PATCH (선택지 위아래 간격 2배 더 축소)
   ============================================================ */

/* 선택지 버튼 자체 마진 극소화 */
.p5-optbtn div[data-testid="stButton"]{
  margin-top: 1px !important;
  margin-bottom: 1px !important;
}

/* column 내부에서 생기는 여백도 함께 제거 */
div[data-testid="column"] .stButton{
  margin-top: 1px !important;
  margin-bottom: 1px !important;
}

/* 선택지 두 줄(ROW) 사이 간격을 더 줄이기 */
div[data-testid="stHorizontalBlock"]{
  row-gap: 3px !important;   /* 이전보다 1/2 */
}

/* 혹시 남아있는 padding/margin 완전 제거 */
div[data-testid="stHorizontalBlock"] > div{
  padding-top: 0px !important;
  padding-bottom: 0px !important;
  margin-top: 0px !important;
  margin-bottom: 0px !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# --- SNAPQ_HEADER_ALIGN (single row) ---
c1, c2 = st.columns([12, 2])
with c1:
    st.markdown(
        "<div class='snapq-header'>"
        "  <div class='snapq-title'><span class='sq-dot'></span> P5 TRAIN · 학습 모드</div>"
        "</div>",
        unsafe_allow_html=True
    )
with c2:
    st.markdown("<div class='snapq-hubpill'>", unsafe_allow_html=True)
    if st.button("🏠", key="p5_train_go_mainhub_pill", use_container_width=False):
        try:
            from streamlit_extras.switch_page_button import switch_page  # type: ignore
            switch_page("main_hub")
        except Exception:
            try:
                st.switch_page("main_hub.py")
            except Exception:
                st.warning("Main Hub 이동 실패: 좌측 사이드바에서 이동해주세요.")
    st.markdown("</div>", unsafe_allow_html=True)
# --- /SNAPQ_HEADER_ALIGN ---

# ============================================================
# Helpers
# ============================================================
def _pick_str(q: Dict[str, Any], keys: List[str], default: str = "") -> str:
    for k in keys:
        v = q.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return default

def _get_p5_items(all_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [x for x in all_items if x.get("source") == "P5"]

def _remove_one_p5_item(all_items: List[Dict[str, Any]], target_q: Dict[str, Any]) -> int:
    sentence = _pick_str(target_q, ["sentence", "q", "question"], "")
    answer = _pick_str(target_q, ["answer", "correct", "correct_answer", "ans"], "")
    choices = target_q.get("choices", []) or []
    t_key = (sentence.strip(), answer.strip(), tuple(choices))

    new_items: List[Dict[str, Any]] = []
    removed = 0
    for it in all_items:
        if it.get("source") == "P5":
            it_sentence = _pick_str(it, ["sentence", "q", "question"], "")
            it_answer = _pick_str(it, ["answer", "correct", "correct_answer", "ans"], "")
            it_choices = it.get("choices", []) or []
            key = (it_sentence.strip(), it_answer.strip(), tuple(it_choices))
            if key == t_key:
                removed += 1
                continue
        new_items.append(it)

    if removed > 0:
        arena._save_armory_items(new_items)  # type: ignore[attr-defined]
    return removed

# ============================================================
# Load
# ============================================================
all_items = arena._load_armory_items()  # type: ignore[attr-defined]
p5_items = _get_p5_items(all_items)
if not p5_items:
    st.info("P5 TRAIN 탄약이 없습니다. (병기고에 저장된 P5 문제가 없어요)")
    st.stop()

# State
st.session_state.setdefault("p5_train_idx", random.randrange(len(p5_items)))
st.session_state.setdefault("p5_train_pick", None)
st.session_state.setdefault("p5_train_brief_open", False)

idx = int(st.session_state["p5_train_idx"]) % len(p5_items)
q = p5_items[idx]
qnum = idx + 1

sentence = _pick_str(q, ["sentence", "q", "question"], "(문제 없음)")
choices: List[str] = list(q.get("choices", []) or [])[:4]
while len(choices) < 4:
    choices.append("")

answer = _pick_str(q, ["answer", "correct", "correct_answer", "ans"], "")
ko = _pick_str(q, ["ko", "korean", "translation", "kr", "meaning_ko"], "")
explain = _pick_str(q, ["explain", "explanation", "commentary", "note"], "")

labels = ["(A)", "(B)", "(C)", "(D)"]

# Problem
st.markdown(
    f"""
    <div class="p5-qbox">
      <div class="p5-qtext">Q{qnum}. {sentence}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Choices 2x2 buttons
r1 = st.columns(2, gap="large")
r2 = st.columns(2, gap="large")
grid = r1 + r2

for i, opt in enumerate(choices[:4]):
    with grid[i]:
        st.markdown('<div class="p5-optbtn">', unsafe_allow_html=True)
        if st.button(f"{labels[i]}  {opt}".strip(), key=f"p5_opt_{idx}_{i}", use_container_width=True):
            st.session_state["p5_train_pick"] = opt
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

picked_now = st.session_state.get("p5_train_pick")
if picked_now:
    st.markdown(
        f"<div class='p5-pickbar'>✅ 선택 저장: <b>{picked_now}</b> · 이제 📘 BRIEF에서 이유를 확인하세요.</div>",
        unsafe_allow_html=True,
    )

# BRIEF (학습모드: BRIEF에서만 판정 공개)
if st.session_state.get("p5_train_brief_open", False):
    fun_lines = [
        "정리 완료. 다음 페이지로.",
        "이 문제는 이제 내 편.",
        "브리핑 종료. 전장 복귀.",
        "노트 덮고, 다음 한 방.",
        "정답 감각 저장 완료.",
        "여기까지. 다음 문제 출격.",
        "정리했으면 지우고 간다.",
        "공부는 짧게, 반복은 길게.",
        "이건 끝났다. 넘기자.",
        "정리 끝. 손에 익힌다.",
    ]
    st.session_state.setdefault("p5_train_funline", random.choice(fun_lines))
    funline = st.session_state.get("p5_train_funline", "")

    picked = st.session_state.get("p5_train_pick") or ""
    judged = bool(picked and answer)
    ok = bool(judged and picked == answer)
    status_cls = "neu" if not judged else ("ok" if ok else "bad")
    status_txt = "📌 선택 후 BRIEF로 정리하세요." if not judged else ("✅ 정답 감각 저장! 이유까지 정리하면 끝." if ok else "❗ 오답. 시험 포인트부터 확인!")

    focus_cls = "p5-focus" if (judged and (not ok)) else ""

    head = st.columns([7, 1])
    with head[0]:
        st.markdown(
            f"<div style='font-weight:950;color:#f9fafb;'>📌 BRIEF <span style='opacity:.75'>📝 {funline}</span></div>",
            unsafe_allow_html=True,
        )
    with head[1]:
        st.markdown("<div class='p5-close-wrap'>", unsafe_allow_html=True)
        if st.button("📕 노트 덮기", key=f"p5_brief_close_{idx}"):
            st.session_state["p5_train_brief_open"] = False
            st.session_state.pop("p5_train_funline", None)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="p5-brief">
          <div class="p5-status {status_cls}">{status_txt}</div>

          <div class="p5-row">
            <div class="p5-k">핵심</div>
            <div>
              정답: <span class="p5-hl">{answer or "(정답 없음)"}</span>
              &nbsp;&nbsp;|&nbsp;&nbsp;
              내 선택: <span class="p5-hl">{picked or "-"}</span>
              &nbsp;&nbsp;|&nbsp;&nbsp;
              결과: <span class="p5-hl">{("✅ 정답" if ok else ("❌ 오답" if judged else "—"))}</span>
            </div>
          </div>

          <div class="p5-row">
            <div class="p5-k">해석</div>
            <div class="p5-pencil">{ko or "(해석 없음)"}</div>
          </div>

          <div class="p5-row {focus_cls}">
            <div class="p5-k">시험 포인트</div>
            <div class="p5-pen">{explain or "(시험 포인트 없음)"}</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

# Bottom buttons
st.markdown('<div class="p5-bottom">', unsafe_allow_html=True)
b1, b2, b3 = st.columns(3, gap="large")

with b1:
    st.markdown("<div class='p5-bbtn-brief'>", unsafe_allow_html=True)
    if st.button("📘 BRIEF", use_container_width=True, key=f"p5_brief_btn_{idx}"):
        st.session_state["p5_train_brief_open"] = (not st.session_state.get("p5_train_brief_open", False))
        if not st.session_state["p5_train_brief_open"]:
            st.session_state.pop("p5_train_funline", None)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with b2:
    st.markdown("<div class='p5-bbtn-discard'>", unsafe_allow_html=True)
    # ✅ 요구사항 1) 정리 -> ✅ 폐기
    if st.button("🗑️ 폐기", use_container_width=True, key=f"p5_discard_{idx}"):
        _remove_one_p5_item(all_items, q)
        all2 = arena._load_armory_items()  # type: ignore[attr-defined]
        p52 = _get_p5_items(all2)
        if not p52:
            st.stop()
        st.session_state["p5_train_idx"] = random.randrange(len(p52))
        st.session_state["p5_train_pick"] = None
        st.session_state["p5_train_brief_open"] = False
        st.session_state.pop("p5_train_funline", None)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with b3:
    st.markdown("<div class='p5-bbtn-next'>", unsafe_allow_html=True)
    if st.button("➡️ 다음", use_container_width=True, key=f"p5_next_{idx}"):
        st.session_state["p5_train_idx"] = (int(st.session_state["p5_train_idx"]) + 1) % len(p5_items)
        st.session_state["p5_train_pick"] = None
        st.session_state["p5_train_brief_open"] = False
        st.session_state.pop("p5_train_funline", None)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

