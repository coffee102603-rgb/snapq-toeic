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

/* --- SNAPQ HEADER ALIGN --- */
.snapq-header{
  display:flex; align-items:center; justify-content:space-between;
  margin: 0.0rem 0 0.35rem 0;
}
.snapq-title{
  font-weight: 950; font-size: 18px; letter-spacing: .2px;
  color: rgba(255,255,255,0.92);
  text-shadow: 0 10px 30px rgba(0,0,0,0.25);
}
.sq-dot{
  display:inline-block;
  width:10px; height:10px; border-radius:50%;
  background: rgba(255,255,255,0.92);
  margin-right: 8px;
  box-shadow: 0 0 16px rgba(255,255,255,0.24);
}
.snapq-hubpill{
  display:flex; align-items:center; justify-content:flex-end;
}
.snapq-hubpill div[data-testid="stButton"] > button{
  width: 46px !important;
  height: 42px !important;
  border-radius: 14px !important;
  background: rgba(255,255,255,0.90) !important;
  border: 1px solid rgba(0,0,0,0.10) !important;
  color:#111827 !important;
  font-weight: 950 !important;
}
.snapq-hubpill div[data-testid="stButton"] > button:hover{
  transform: translateY(-1px);
}
/* --- /SNAPQ HEADER ALIGN --- */

/* (기존 파일의 끝부분이 길어져도 안전하도록, 아래부터 추가 패치가 더 있어도 OK) */
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
        # ✅ SAFE HUB RETURN (single source of truth)
        try:
            st.switch_page("main_hub.py")
        except Exception:
            st.info("이 환경에선 페이지 이동이 제한될 수 있어요. (좌측 사이드바에서 Main Hub 선택 / 브라우저 뒤로가기)")
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
st.markdown('<div class="p5-qbox">', unsafe_allow_html=True)
st.markdown(
    f'<div class="p5-qtext">{qnum}. {sentence}</div>',
    unsafe_allow_html=True,
)
st.markdown("</div>", unsafe_allow_html=True)

# Options (2x2)
st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
st.markdown('<div class="p5-optbtn">', unsafe_allow_html=True)
r1c1, r1c2 = st.columns(2, gap="medium")
r2c1, r2c2 = st.columns(2, gap="medium")

def _pick(i: int):
    st.session_state["p5_train_pick"] = i

with r1c1:
    if st.button(f"{labels[0]}  {choices[0]}", use_container_width=True, key="p5_train_opt_0"):
        _pick(0)
with r1c2:
    if st.button(f"{labels[1]}  {choices[1]}", use_container_width=True, key="p5_train_opt_1"):
        _pick(1)
with r2c1:
    if st.button(f"{labels[2]}  {choices[2]}", use_container_width=True, key="p5_train_opt_2"):
        _pick(2)
with r2c2:
    if st.button(f"{labels[3]}  {choices[3]}", use_container_width=True, key="p5_train_opt_3"):
        _pick(3)

st.markdown("</div>", unsafe_allow_html=True)

pick = st.session_state.get("p5_train_pick", None)
if isinstance(pick, int) and 0 <= pick < 4:
    st.markdown(
        f"<div class='p5-pickbar'>✅ 선택: <b>{labels[pick]}</b> {choices[pick]}</div>",
        unsafe_allow_html=True,
    )

# Bottom actions
st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
b1, b2, b3 = st.columns(3, gap="medium")

with b1:
    st.markdown('<div class="p5-bottom p5-bbtn-brief">', unsafe_allow_html=True)
    if st.button("🧾 BRIEF", use_container_width=True, key="p5_train_open_brief"):
        st.session_state["p5_train_brief_open"] = True
    st.markdown("</div>", unsafe_allow_html=True)

with b2:
    st.markdown('<div class="p5-bottom p5-bbtn-discard">', unsafe_allow_html=True)
    if st.button("🧹 폐기", use_container_width=True, key="p5_train_discard"):
        removed = _remove_one_p5_item(all_items, q)
        st.session_state["p5_train_pick"] = None
        st.session_state["p5_train_brief_open"] = False
        if removed > 0:
            st.success("✅ 1개 폐기 완료 (병기고에서 제거)")
        else:
            st.warning("⚠️ 폐기할 항목을 찾지 못했습니다.")
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

with b3:
    st.markdown('<div class="p5-bottom p5-bbtn-next">', unsafe_allow_html=True)
    if st.button("➡️ 다음", use_container_width=True, key="p5_train_next"):
        st.session_state["p5_train_idx"] = (idx + 1) % len(p5_items)
        st.session_state["p5_train_pick"] = None
        st.session_state["p5_train_brief_open"] = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# Brief panel
if st.session_state.get("p5_train_brief_open", False):
    # status
    picked_ok = False
    if isinstance(pick, int) and answer and isinstance(answer, str):
        try:
            correct_idx = choices.index(answer)
            picked_ok = (pick == correct_idx)
        except Exception:
            picked_ok = False

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="p5-brief">', unsafe_allow_html=True)

    if isinstance(pick, int):
        if picked_ok:
            st.markdown('<div class="p5-status ok">✅ 정답 추정</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="p5-status bad p5-focus">❌ 오답 추정</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="p5-status neu">ℹ️ 선택 후 BRIEF를 보면 더 좋아요</div>', unsafe_allow_html=True)

    # rows
    st.markdown(
        f"<div class='p5-row'><div class='p5-k'>정답</div><div class='p5-pen'><span class='p5-hl'>{answer or '(미등록)'}</span></div></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='p5-row'><div class='p5-k'>해석</div><div class='p5-pencil'>{ko or '(해석 없음)'}</div></div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<div class='p5-row'><div class='p5-k'>설명</div><div class='p5-pencil'>{explain or '(설명 없음)'}</div></div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div class='p5-close-wrap'>", unsafe_allow_html=True)
    if st.button("닫기", use_container_width=False, key="p5_train_close_brief"):
        st.session_state["p5_train_brief_open"] = False
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
