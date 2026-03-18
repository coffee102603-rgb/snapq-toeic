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
    page_title="?윪 P5 TRAIN 쨌 SnapQ TOEIC",
    page_icon="?윪",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ============================================================
# CSS: 2x2 移대뱶??踰꾪듉 + 媛?낆꽦 媛뺤젣 + ?섎떒 3踰꾪듉 ??遺꾨━
# ============================================================
st.markdown(
    r"""
<style>
.block-container{ max-width: 1100px !important; padding-top: 1.1rem !important; padding-bottom: 1.6rem !important; }

/* 臾몄젣 諛뺤뒪 */
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

/* ???좏깮吏 移대뱶 踰꾪듉 */
.p5-optbtn div[data-testid="stButton"] > button{
  /* 燧놅툘 ????諛앷쾶 */
  background: rgba(255,255,255,.24) !important;
  border: 1px solid rgba(255,255,255,.46) !important;

  border-radius: 18px !important;
  min-height: 82px !important;           /* 紐⑤컮???곗튂 ?ш쾶 */
  box-shadow: 0 14px 30px rgba(0,0,0,.14) !important;
}
.p5-optbtn div[data-testid="stButton"] > button:hover{
  border: 1px solid rgba(255,255,255,.70) !important;
  transform: translateY(-1px);
}

/* ???좏깮吏 湲???좊챸 媛뺤젣(臾삵옒 諛⑹?) */
.p5-optbtn div[data-testid="stButton"] > button *,
.p5-bottom div[data-testid="stButton"] > button *{
  color:#f9fafb !important;
  opacity: 1 !important;
  text-shadow: none !important;
  filter: none !important;
  -webkit-text-fill-color:#f9fafb !important;
  font-weight: 950 !important;
}

/* ?좏깮 ???諛곕꼫 */
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

/* BRIEF 移대뱶 */
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

/* ?ㅻ떟 ???쒗뿕?ъ씤???꾩뒪 */
@keyframes p5pulse {
  0%   { box-shadow: 0 0 0 rgba(244,63,94,0.0); border-color: rgba(244,63,94,.22); }
  50%  { box-shadow: 0 0 0 6px rgba(244,63,94,0.10); border-color: rgba(244,63,94,.45); }
  100% { box-shadow: 0 0 0 rgba(244,63,94,0.0); border-color: rgba(244,63,94,.22); }
}
.p5-focus{ animation: p5pulse 1.2s ease-in-out infinite; border-width: 2px !important; }

/* BRIEF ?リ린 踰꾪듉 */
.p5-close-wrap div[data-testid="stButton"] > button{
  color:#111827 !important;
  background: rgba(255,255,255,.92) !important;
  border: 2px solid rgba(17,24,39,.24) !important;
  border-radius: 12px !important;
  font-weight: 950 !important;
  min-height: 40px !important;
  padding: 4px 10px !important;
}

/* ?섎떒 3踰꾪듉 ??遺꾨━ */
.p5-bottom div[data-testid="stButton"] > button{
  min-height: 72px !important;
  border-radius: 16px !important;
  font-size: 18px !important;

  /* 燧놅툘 ????諛앷쾶 */
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

/* ??踰꾪듉 ?띿뒪???좊챸???좏깮吏 + ?섎떒) : DOM 蹂?뺤뿉??癒밴쾶 *源뚯? */
.p5-optbtn div[data-testid="stButton"] > button *,
.p5-bottom div[data-testid="stButton"] > button *{
  color: #f9fafb !important;
  opacity: 1 !important;
  filter: none !important;
  -webkit-text-fill-color: #f9fafb !important;
  font-weight: 950 !important;

  /* ???ㅺ낸 ??媛뺥븯寃?+ ?뉗? stroke */
  text-shadow:
    0 1px 2px rgba(0,0,0,.75),
    0 3px 12px rgba(0,0,0,.55) !important;
  -webkit-text-stroke: 0.4px rgba(0,0,0,.35);
}

/* ???섎떒 3踰꾪듉: 以꾨컮轅?諛⑹? + ?믪씠 ?듭씪 */
.p5-bottom div[data-testid="stButton"] > button{
  min-height: 72px !important;
  border-radius: 16px !important;
}
.p5-bottom div[data-testid="stButton"] > button span{
  white-space: nowrap !important;       /* ??以꾨컮轅?諛⑹? */
  overflow: hidden !important;
  text-overflow: ellipsis !important;
}

/* ???섎떒 踰꾪듉 ?됯컧 遺꾨━(湲곕뒫蹂? */
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

/* ???좏깮吏 踰꾪듉 諛곌꼍/?뚮몢由щ룄 ?鍮??댁쭩 ??*/
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
   A-PATCH: "臾몄젣吏?媛?낆꽦" CSS ONLY (SAFE OVERRIDE)
   - ?좏깮吏 4媛? ?ㅽ봽?붿씠??醫낆씠 + 寃??湲??   - ?섎떒 3踰꾪듉: ?뚮옉/珥덈줉/蹂대씪濡?湲곕뒫 遺꾨━ + ??湲??   ============================================================ */

/* (1) ?좏깮吏 踰꾪듉(4媛? = 臾몄젣吏?醫낆씠 */
.p5-optbtn div[data-testid="stButton"] > button{
  background: rgba(248,250,252,0.98) !important;   /* 醫낆씠??*/
  border: 2px solid rgba(203,213,225,0.95) !important;
  box-shadow: 0 14px 30px rgba(0,0,0,.14) !important;
}

/* ?좏깮吏 湲??= 寃??+ 援듦쾶 (諛곌꼍怨?遺꾨━) */
.p5-optbtn div[data-testid="stButton"] > button,
.p5-optbtn div[data-testid="stButton"] > button *{
  color: #111827 !important;
  -webkit-text-fill-color: #111827 !important;
  text-shadow: none !important;
  -webkit-text-stroke: 0px transparent !important;
  font-weight: 900 !important;
  opacity: 1 !important;
}

/* hover: 臾몄젣吏??뺢킅???먮굦 ?댁쭩 */
.p5-optbtn div[data-testid="stButton"] > button:hover{
  background: rgba(254,249,195,0.98) !important;  /* ?곕끂??*/
  border: 2px solid rgba(251,191,36,0.95) !important;
}

/* (2) ?섎떒 3踰꾪듉(Brief/?먭린/?ㅼ쓬) = ?섎?媛 蹂댁씠寃??됱긽 遺꾨━ */
.p5-bottom div[data-testid="stButton"] > button{
  border-radius: 18px !important;
  min-height: 74px !important;
  font-size: 19px !important;
  font-weight: 950 !important;
  letter-spacing: 0.2px;
  box-shadow: 0 14px 30px rgba(0,0,0,.18) !important;
  border: 2px solid rgba(255,255,255,.18) !important;
}

/* ?섎떒 踰꾪듉 湲??= ?곗깋 + ?ㅺ낸 */
.p5-bottom div[data-testid="stButton"] > button,
.p5-bottom div[data-testid="stButton"] > button *{
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  text-shadow: 0 2px 10px rgba(0,0,0,.55) !important;
  -webkit-text-stroke: 0.35px rgba(0,0,0,.25);
  opacity: 1 !important;
}

/* BRIEF = ?뚮옉(?댁꽕/?숈뒿) */
.p5-bbtn-brief div[data-testid="stButton"] > button{
  background: linear-gradient(180deg, rgba(59,130,246,.92), rgba(37,99,235,.62)) !important;
  border: 2px solid rgba(147,197,253,.70) !important;
}

/* ?먭린 = 珥덈줉(?뺣━/愿由? */
.p5-bbtn-discard div[data-testid="stButton"] > button{
  background: linear-gradient(180deg, rgba(34,197,94,.92), rgba(22,163,74,.62)) !important;
  border: 2px solid rgba(134,239,172,.70) !important;
}

/* ?ㅼ쓬 = 蹂대씪(吏꾪뻾/異쒓꺽) */
.p5-bbtn-next div[data-testid="stButton"] > button{
  background: linear-gradient(180deg, rgba(168,85,247,.92), rgba(124,58,237,.62)) !important;
  border: 2px solid rgba(216,180,254,.70) !important;
}

/* (3) ?좏깮 ???諛??꾩옱 ??諛???湲???먮졆?섍쾶 */
.p5-pickbar, .p5-pickbar *{
  color:#111827 !important;
  text-shadow:none !important;
  font-weight: 950 !important;
}
/* ============================================================
   B2-PATCH: P5 TRAIN "?꾨━誘몄뾼 臾몄젣吏??꾩씠蹂대━)" + WHITE TEXT (SAFE OVERRIDE)
   - ?좏깮吏 4媛? ?꾩씠蹂대━ 醫낆씠??+ 湲???곗깋(?ㅺ낸 媛?
   - ?섎떒 3踰꾪듉: 湲곗〈 ???좎? + 湲???곗깋 ??媛?   ============================================================ */

/* (A) ?좏깮吏 諛뺤뒪 = ?꾩씠蹂대━(?꾨━誘몄뾼 醫낆씠) */
.p5-optbtn div[data-testid="stButton"] > button{
  background: rgba(255, 248, 235, 0.92) !important;  /* ?꾩씠蹂대━ 醫낆씠 */
  border: 2px solid rgba(226, 232, 240, 0.55) !important;
  box-shadow: 0 18px 34px rgba(0,0,0,.18) !important;
}

/* (B) ?좏깮吏 湲??= ?곗깋 媛뺤젣 + ?ㅺ낸/洹몃┝??臾몄젣吏?寃뚯엫 ?쇳빀) */
.p5-optbtn div[data-testid="stButton"] > button,
.p5-optbtn div[data-testid="stButton"] > button *{
  color: #ffffff !important;
  -webkit-text-fill-color: #ffffff !important;
  font-weight: 950 !important;
  opacity: 1 !important;

  /* ?ㅺ낸 媛뺥솕 */
  text-shadow:
    0 1px 2px rgba(0,0,0,.82),
    0 6px 18px rgba(0,0,0,.55) !important;
  -webkit-text-stroke: 0.55px rgba(0,0,0,.38);
}

/* hover = ?댁쭩 ??諛앹? 醫낆씠 + ?뚮몢由?媛뺤“ */
.p5-optbtn div[data-testid="stButton"] > button:hover{
  background: rgba(255, 252, 245, 0.96) !important;
  border: 2px solid rgba(148,163,184,0.65) !important;
}

/* (C) ?섎떒 3踰꾪듉 湲??= ?곗깋 ???먮졆(?대? ?곗깋?댁?留???媛뺥븯寃? */
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

/* (D) ?섎떒 踰꾪듉: ?댁쭩 ??夷랁븯寃??ㅼ뾽) */
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
   B-HYBRID PATCH: "臾몄젣吏?媛먯꽦 ?좎? + ???명븯寃?
   - ?좏깮吏 4媛? 諛앹? 醫낆씠 硫??꾩씠蹂대━/?ㅽ봽?붿씠?? + ???뚮몢由?+ ??湲???ㅺ낸
   - ?섎떒 3踰꾪듉: ?섎????좎? + 諛앷린/?鍮????뚮몢由?媛뺥솕
   ============================================================ */

/* (0) 怨듯넻: 踰꾪듉??諛곌꼍??臾삵엳吏 ?딄쾶 ?댁쭩 ?좊━???먮굦 */
.p5-optbtn div[data-testid="stButton"] > button,
.p5-bottom  div[data-testid="stButton"] > button{
  backdrop-filter: blur(6px);
}

/* (1) ?좏깮吏 4媛?諛뺤뒪 = "諛앹? 醫낆씠 硫? + ???뚮몢由?*/
.p5-optbtn div[data-testid="stButton"] > button{
  background: linear-gradient(180deg,
    rgba(255,252,245,0.55),
    rgba(255,248,235,0.28)
  ) !important; /* 醫낆씠??諛앹? 硫? */
  border: 2px solid rgba(255,255,255,0.72) !important; /* ???뚮몢由?*/
  box-shadow: 0 18px 34px rgba(0,0,0,.22) !important;
}

/* ?좏깮吏 hover: ??諛앷쾶 + ?뚮몢由???夷랁븯寃?*/
.p5-optbtn div[data-testid="stButton"] > button:hover{
  background: linear-gradient(180deg,
    rgba(255,252,245,0.70),
    rgba(255,248,235,0.40)
  ) !important;
  border: 2px solid rgba(255,255,255,0.92) !important;
}

/* (2) ?좏깮吏 湲??= ?곗깋 + ?ㅺ낸(媛? */
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

/* (3) ?섎떒 3踰꾪듉 = ?섎????좎? + 諛앷린 ??+ ???뚮몢由?*/
.p5-bottom div[data-testid="stButton"] > button{
  border: 2px solid rgba(255,255,255,0.70) !important;
  box-shadow: 0 18px 34px rgba(0,0,0,.24) !important;
  filter: brightness(1.14) saturate(1.08);
}

/* ?섎떒 湲??= ?곗깋 + ???먮졆 */
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

/* (4) ?좏깮 ???諛붾뒗 "臾몄젣吏?硫붾え吏"泥섎읆 ??諛앷쾶 */
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
   STEP1 PATCH: ?좏깮吏 諛뺤뒪 "臾몄젣吏묓솕" (OPTIONS ONLY)
   - 諛앹? 醫낆씠 硫?+ ???뚮몢由?+ 移대뱶 洹몃┝??+ hover ?뺢킅??   ============================================================ */

/* ?좏깮吏 踰꾪듉: 移대뱶(醫낆씠)泥섎읆 '諛앹? 硫? + ?먮졆?????뚮몢由?*/
.p5-optbtn div[data-testid="stButton"] > button{
  background: linear-gradient(180deg,
    rgba(255, 253, 248, 0.92),
    rgba(255, 248, 235, 0.70)
  ) !important; /* ?꾨━誘몄뾼 醫낆씠 */
  border: 2.5px solid rgba(255,255,255,0.92) !important; /* ???뚮몢由??좊챸 */
  box-shadow:
    0 18px 36px rgba(0,0,0,.22),
    inset 0 1px 0 rgba(255,255,255,.55) !important; /* 醫낆씠 吏덇컧 */
  border-radius: 20px !important;
}

/* ?좏깮吏 hover: ?뺢킅???먮굦(?????몃옉) + ?댁쭩 ?좎삤由?*/
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

/* ?좏깮吏 active(?대┃): ?뚮┝ ?④낵 */
.p5-optbtn div[data-testid="stButton"] > button:active{
  transform: translateY(0px);
  box-shadow:
    0 14px 28px rgba(0,0,0,.20),
    inset 0 2px 0 rgba(0,0,0,.06) !important;
}

/* ?좏깮吏 湲?? ?꾩옱 '?곗깋' 諛⑺뼢 ?좎? + ?ㅺ낸(寃???쇰줈 ?뺤떎??*/
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
   B-2 FINAL PATCH: "臾몄젣吏?理쒖쥌??
   - ?좏깮吏(4媛? = 諛앹? 醫낆씠 + 寃??湲??媛?낆꽦 理쒖슦??
   - hover = ?뺢킅???몃옉
   - ?섎떒 3踰꾪듉? 湲곗〈(??湲?? ?좎?
   ============================================================ */

/* (1) ?좏깮吏 諛뺤뒪: 嫄곗쓽 ??醫낆씠(?꾩씠蹂대━ ?댁쭩) + 源붾걫???뚮몢由?*/
.p5-optbtn div[data-testid="stButton"] > button{
  background: linear-gradient(180deg,
    rgba(255, 255, 255, 0.98),
    rgba(255, 248, 235, 0.92)
  ) !important; /* 醫낆씠 */
  border: 2px solid rgba(203,213,225,0.95) !important; /* ?고쉶???뚮몢由?*/
  box-shadow:
    0 18px 36px rgba(0,0,0,.18),
    inset 0 1px 0 rgba(255,255,255,.75) !important;
  border-radius: 20px !important;
}

/* (2) ?좏깮吏 湲?? 寃??臾몄젣吏?猷? */
.p5-optbtn div[data-testid="stButton"] > button,
.p5-optbtn div[data-testid="stButton"] > button *{
  color:#111827 !important;
  -webkit-text-fill-color:#111827 !important;
  font-weight: 950 !important;
  opacity: 1 !important;
  text-shadow: none !important;
  -webkit-text-stroke: 0px transparent !important;
}

/* (3) hover: ?뺢킅??*/
.p5-optbtn div[data-testid="stButton"] > button:hover{
  background: linear-gradient(180deg,
    rgba(254, 249, 195, 0.98),
    rgba(255, 248, 235, 0.92)
  ) !important; /* ?뺢킅???몃옉 */
  border: 2px solid rgba(251,191,36,0.95) !important;
  transform: translateY(-1px);
  box-shadow:
    0 22px 44px rgba(0,0,0,.22),
    inset 0 1px 0 rgba(255,255,255,.85) !important;
}

/* (4) active(?대┃): ?뚮┝ */
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

/* A) 湲곕낯: 紐⑤뱺 踰꾪듉???쇰떒 "臾몄젣吏?醫낆씠"濡?媛뺤젣 */
div[data-testid="stButton"] > button{
  background: linear-gradient(180deg,
    rgba(255,255,255,0.98),
    rgba(255,248,235,0.92)
  ) !important;
  border: 2px solid rgba(203,213,225,0.95) !important;
  border-radius: 20px !important;
  box-shadow: 0 18px 36px rgba(0,0,0,.18) !important;
}

/* 紐⑤뱺 踰꾪듉 湲??= 寃??臾몄젣吏?猷? */
div[data-testid="stButton"] > button,
div[data-testid="stButton"] > button *{
  color:#111827 !important;
  -webkit-text-fill-color:#111827 !important;
  font-weight: 950 !important;
  text-shadow: none !important;
  -webkit-text-stroke: 0px transparent !important;
  opacity: 1 !important;
}

/* hover: ?뺢킅??*/
div[data-testid="stButton"] > button:hover{
  background: linear-gradient(180deg,
    rgba(254,249,195,0.98),
    rgba(255,248,235,0.92)
  ) !important;
  border: 2px solid rgba(251,191,36,0.95) !important;
}

/* B) ?덉쇅: ?섎떒 3踰꾪듉(.p5-bottom)留??ㅼ떆 HUD濡?蹂듦뎄 */
.p5-bottom div[data-testid="stButton"] > button{
  background: rgba(17,24,39,0.38) !important;
  border: 2px solid rgba(255,255,255,0.55) !important;
  box-shadow: 0 18px 36px rgba(0,0,0,.24) !important;
}

/* ?섎떒 3踰꾪듉 湲??= ?곗깋 + ?ㅺ낸 */
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

/* mobile: 議곌툑 ??苑?李④쾶 */
@media (max-width: 768px){
  .p5-brief{
    width: calc(100vw - 16px) !important;
    bottom: 8px !important;
    max-height: 78vh !important;
  }
}

/* "?명듃 ??린"媛 ?ㅼ뼱?덈뒗 ?곷떒 以꾩쓣 ??긽 蹂댁씠寃??ㅽ겕濡?以묒뿉?? */
.p5-brief .p5-close-wrap{
  position: sticky;
  top: 8px;
  z-index: 10000;
}

/* BRIEF ?대? 泥?以??ㅻ뜑)??諛곌꼍??臾삵엳吏 ?딄쾶 */
.p5-brief{
  box-shadow: 0 24px 60px rgba(0,0,0,.35) !important;
}

/* ?섎떒 3踰꾪듉? z-index ??쾶 (BRIEF媛 ?꾩뿉 ?④쾶) */
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
  width: 42px !important;          /* ?꾩씠肄섎쭔 */
  min-width: 42px !important;
  max-width: 42px !important;
  min-height: 32px !important;
  height: 32px !important;
  padding: 0 !important;           /* 怨듦컙 理쒖냼 */
  border-radius: 12px !important;  /* ?덈Т ?κ?吏 ?딄쾶 */
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
   SPACING PATCH: 臾몄젣-?좏깮吏 媛꾧꺽??/ ?좏깮吏?쇰━ 媛꾧꺽??(臾몄젣吏??덉씠?꾩썐)
   ============================================================ */

/* 1) 臾몄젣 諛뺤뒪 ?꾨옒 ?щ갚???ш쾶: ?좏깮吏 ?쒖옉?????꾨옒濡?*/
.p5-qbox{
  margin-bottom: 42px !important;   /* 湲곕낯蹂대떎 ?ш쾶 (泥닿컧 3諛??먮굦) */
}

/* 2) ?좏깮吏 踰꾪듉(4媛? ?ъ씠 媛꾧꺽??以꾩씠湲?*/
.p5-optbtn div[data-testid="stButton"]{
  margin-top: 4px !important;
  margin-bottom: 4px !important;    /* 湲곗〈蹂대떎 1/3 ?섏??쇰줈 珥섏킌?섍쾶 */
}

/* 3) ?뱀떆 column wrapper媛 ?щ갚???≪쑝硫?媛숈씠 以꾩씠湲?*/
div[data-testid="column"] .stButton{
  margin-top: 4px !important;
  margin-bottom: 4px !important;
}
/* ============================================================
   ROW-GAP PATCH: ?좏깮吏 ?쀬쨪(2媛? ???꾨옯以?2媛? 媛꾧꺽????遺숈씠湲?   - 紐⑹쟻: 4媛??좏깮吏瑜?"???⑹뼱由?濡?蹂댁씠寃?   ============================================================ */

/* ?좏깮吏 踰꾪듉 wrapper 留덉쭊????珥섏킌?섍쾶 */
.p5-optbtn div[data-testid="stButton"]{
  margin-top: 2px !important;
  margin-bottom: 2px !important;
}

/* column ?대? 踰꾪듉 留덉쭊???④퍡 */
div[data-testid="column"] .stButton{
  margin-top: 2px !important;
  margin-bottom: 2px !important;
}

/* ??以??ъ씠瑜?踰뚮━???먯씤 以??섎굹: column wrapper??湲곕낯 gap/padding ?쒓굅 ?쒕룄 */
div[data-testid="stHorizontalBlock"]{
  row-gap: 6px !important;   /* (湲곕낯蹂대떎 以꾩씠湲? */
}

/* ?뱀떆 ??踰덉㎏ 以??쒖옉 ?꾩뿉 ?앷린???щ갚???덉쑝硫?以꾩씠湲?*/
div[data-testid="stHorizontalBlock"] > div{
  padding-top: 0px !important;
  margin-top: 0px !important;
}
/* ============================================================
   OPTIONS GAP x0.5 PATCH (?좏깮吏 ?꾩븘??媛꾧꺽 2諛???異뺤냼)
   ============================================================ */

/* ?좏깮吏 踰꾪듉 ?먯껜 留덉쭊 洹뱀냼??*/
.p5-optbtn div[data-testid="stButton"]{
  margin-top: 1px !important;
  margin-bottom: 1px !important;
}

/* column ?대??먯꽌 ?앷린???щ갚???④퍡 ?쒓굅 */
div[data-testid="column"] .stButton{
  margin-top: 1px !important;
  margin-bottom: 1px !important;
}

/* ?좏깮吏 ??以?ROW) ?ъ씠 媛꾧꺽????以꾩씠湲?*/
div[data-testid="stHorizontalBlock"]{
  row-gap: 3px !important;   /* ?댁쟾蹂대떎 1/2 */
}

/* ?뱀떆 ?⑥븘?덈뒗 padding/margin ?꾩쟾 ?쒓굅 */
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
        "  <div class='snapq-title'><span class='sq-dot'></span> P5 TRAIN 쨌 ?숈뒿 紐⑤뱶</div>"
        "</div>",
        unsafe_allow_html=True
    )
with c2:
    st.markdown("<div class='snapq-hubpill'>", unsafe_allow_html=True)
    if st.button("?룧", key="p5_train_go_mainhub_pill", use_container_width=False):
        try:
            from streamlit_extras.switch_page_button import switch_page  # type: ignore
            st.st.switch_page("main_hub.py")
        except Exception:
            try:
                st.st.switch_page("main_hub.py")
            except Exception:
                st.warning("Main Hub ?대룞 ?ㅽ뙣: 醫뚯륫 ?ъ씠?쒕컮?먯꽌 ?대룞?댁＜?몄슂.")
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
    st.info("P5 TRAIN ?꾩빟???놁뒿?덈떎. (蹂묎린怨좎뿉 ??λ맂 P5 臾몄젣媛 ?놁뼱??")
    st.stop()

# State
st.session_state.setdefault("p5_train_idx", random.randrange(len(p5_items)))
st.session_state.setdefault("p5_train_pick", None)
st.session_state.setdefault("p5_train_brief_open", False)

idx = int(st.session_state["p5_train_idx"]) % len(p5_items)
q = p5_items[idx]
qnum = idx + 1

sentence = _pick_str(q, ["sentence", "q", "question"], "(臾몄젣 ?놁쓬)")
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
        f"<div class='p5-pickbar'>???좏깮 ??? <b>{picked_now}</b> 쨌 ?댁젣 ?뱲 BRIEF?먯꽌 ?댁쑀瑜??뺤씤?섏꽭??</div>",
        unsafe_allow_html=True,
    )

# BRIEF (?숈뒿紐⑤뱶: BRIEF?먯꽌留??먯젙 怨듦컻)
if st.session_state.get("p5_train_brief_open", False):
    fun_lines = [
        "?뺣━ ?꾨즺. ?ㅼ쓬 ?섏씠吏濡?",
        "??臾몄젣???댁젣 ????",
        "釉뚮━??醫낅즺. ?꾩옣 蹂듦?.",
        "?명듃 ??퀬, ?ㅼ쓬 ??諛?",
        "?뺣떟 媛먭컖 ????꾨즺.",
        "?ш린源뚯?. ?ㅼ쓬 臾몄젣 異쒓꺽.",
        "?뺣━?덉쑝硫?吏?곌퀬 媛꾨떎.",
        "怨듬???吏㏐쾶, 諛섎났? 湲멸쾶.",
        "?닿굔 ?앸궗?? ?섍린??",
        "?뺣━ ?? ?먯뿉 ?듯엺??",
    ]
    st.session_state.setdefault("p5_train_funline", random.choice(fun_lines))
    funline = st.session_state.get("p5_train_funline", "")

    picked = st.session_state.get("p5_train_pick") or ""
    judged = bool(picked and answer)
    ok = bool(judged and picked == answer)
    status_cls = "neu" if not judged else ("ok" if ok else "bad")
    status_txt = "?뱦 ?좏깮 ??BRIEF濡??뺣━?섏꽭??" if not judged else ("???뺣떟 媛먭컖 ??? ?댁쑀源뚯? ?뺣━?섎㈃ ??" if ok else "???ㅻ떟. ?쒗뿕 ?ъ씤?몃????뺤씤!")

    focus_cls = "p5-focus" if (judged and (not ok)) else ""

    head = st.columns([7, 1])
    with head[0]:
        st.markdown(
            f"<div style='font-weight:950;color:#f9fafb;'>?뱦 BRIEF <span style='opacity:.75'>?뱷 {funline}</span></div>",
            unsafe_allow_html=True,
        )
    with head[1]:
        st.markdown("<div class='p5-close-wrap'>", unsafe_allow_html=True)
        if st.button("?뱯 ?명듃 ??린", key=f"p5_brief_close_{idx}"):
            st.session_state["p5_train_brief_open"] = False
            st.session_state.pop("p5_train_funline", None)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="p5-brief">
          <div class="p5-status {status_cls}">{status_txt}</div>

          <div class="p5-row">
            <div class="p5-k">?듭떖</div>
            <div>
              ?뺣떟: <span class="p5-hl">{answer or "(?뺣떟 ?놁쓬)"}</span>
              &nbsp;&nbsp;|&nbsp;&nbsp;
              ???좏깮: <span class="p5-hl">{picked or "-"}</span>
              &nbsp;&nbsp;|&nbsp;&nbsp;
              寃곌낵: <span class="p5-hl">{("???뺣떟" if ok else ("???ㅻ떟" if judged else "??))}</span>
            </div>
          </div>

          <div class="p5-row">
            <div class="p5-k">?댁꽍</div>
            <div class="p5-pencil">{ko or "(?댁꽍 ?놁쓬)"}</div>
          </div>

          <div class="p5-row {focus_cls}">
            <div class="p5-k">?쒗뿕 ?ъ씤??/div>
            <div class="p5-pen">{explain or "(?쒗뿕 ?ъ씤???놁쓬)"}</div>
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
    if st.button("?뱲 BRIEF", use_container_width=True, key=f"p5_brief_btn_{idx}"):
        st.session_state["p5_train_brief_open"] = (not st.session_state.get("p5_train_brief_open", False))
        if not st.session_state["p5_train_brief_open"]:
            st.session_state.pop("p5_train_funline", None)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with b2:
    st.markdown("<div class='p5-bbtn-discard'>", unsafe_allow_html=True)
    # ???붽뎄?ы빆 1) ?뺣━ -> ???먭린
    if st.button("?뿊截??먭린", use_container_width=True, key=f"p5_discard_{idx}"):
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
    if st.button("?∽툘 ?ㅼ쓬", use_container_width=True, key=f"p5_next_{idx}"):
        st.session_state["p5_train_idx"] = (int(st.session_state["p5_train_idx"]) + 1) % len(p5_items)
        st.session_state["p5_train_pick"] = None
        st.session_state["p5_train_brief_open"] = False
        st.session_state.pop("p5_train_funline", None)
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


