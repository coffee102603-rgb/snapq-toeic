from __future__ import annotations







# --- P7_FORCE_TOPCSS_V1 START ---
import streamlit as st
st.markdown(r"""
<style>
/* ===== P7_FORCE_TOPCSS_V1 V2 ===== */

/* ✅ 최상위 컨테이너 "배경/가장자리"까지 강제 흰색 + 테두리 제거 */
html, body, .stApp,
[data-testid="stAppViewContainer"], [data-testid="stMain"], .main, .block-container{
  background: #ffffff !important;
  background-image: none !important;
  outline: none !important;
  box-shadow: none !important;
}

/* ✅ Streamlit 기본 padding 줄이기(상단 여백 압축) */
.block-container{
  padding-top: 0.35rem !important;
  padding-bottom: 0.85rem !important;
  padding-left: 0.85rem !important;
  padding-right: 0.85rem !important;
  max-width: 100% !important;
}

/* ✅ 헤더/푸터 제거(상단 빈 공간 감소) */
header, footer{ display:none !important; }

/* ✅ 사이드바 완전 숨김 */
[data-testid="stSidebar"]{ display:none !important; }

/* ✅ 기본 경고/성공 카드가 END 화면을 어지럽히지 않게(일반 구간은 그대로) */
</style>
""", unsafe_allow_html=True)
# --- P7_FORCE_TOPCSS_V1 END ---


import os
import json
import time
from dataclasses import dataclass
from typing import List


# =============================
# P7 Demo Data (2 → 5 → 8)
# =============================

P7_FULL_SENTENCES_EN = [
    "Dear staff, we would like to inform you that the customer support team will be relocated next month.",
    "Starting May 3, the team will move from the 5th floor to the 9th floor in the same building.",
    "The new workspace will include additional meeting areas for faster coordination.",
    "Employees will receive updated access instructions for the 9th floor prior to the move.",
    "Further details will be shared in a follow-up notice next week.",
    "Please pack your personal belongings by April 28.",
    "IT staff will assist with moving your desktop computers.",
    "We appreciate your cooperation during this transition period.",
]

@dataclass
class Step:
    question: str
    options: List[str]
    answer_idx: int

STEPS = [
    Step(
        question="What is the main purpose of the message?",
        options=[
            "To announce a team relocation",
            "To request a vacation schedule",
            "To introduce a new product",
            "To change salary policies",
        ],
        answer_idx=0,
    ),
    Step(
        question="Where will the team move?",
        options=[
            "To another building across town",
            "From the 5th floor to the 9th floor",
            "From the 9th floor to the 5th floor",
            "To an external office",
        ],
        answer_idx=1,
    ),
    Step(
        question="What will be included in the new workspace?",
        options=[
            "A larger cafeteria",
            "Additional meeting areas",
            "A gym for employees",
            "A new parking lot",
        ],
        answer_idx=1,
    ),
]

# =============================
# Session init / reset
# =============================

def init_session():
    st.session_state.setdefault("p7_started_at", time.time())
    st.session_state.setdefault("p7_time_limit", 150)  # set 전체 제한(기본 150s)
    st.session_state.setdefault("p7_step", 1)          # 1~3
    st.session_state.setdefault("p7_combo", 0)
    st.session_state.setdefault("p7_miss", 0)
    st.session_state.setdefault("p7_done", False)
    st.session_state.setdefault("p7_nonce", 0)

def reset_battle():
    keep_limit = st.session_state.get("p7_time_limit", 150)
    for k in ["p7_started_at","p7_step","p7_combo","p7_miss","p7_done","p7_nonce",
              "p7_end_show_solution","p7_end_show_vocab"]:
        if k in st.session_state:
            del st.session_state[k]
    st.session_state["p7_time_limit"] = keep_limit
    init_session()

def mmss(sec: int) -> str:
    sec = max(0, int(sec))
    return f"{sec//60:02d}:{sec%60:02d}"

def build_cumulative_passage(step: int) -> str:
    if step <= 1:
        need = 2
    elif step == 2:
        need = 5
    else:
        need = 8
    return " ".join(P7_FULL_SENTENCES_EN[:need])

# =============================
# Page config
# =============================

try:
    st.set_page_config(page_title="SnapQ TOEIC · P7 Reading Arena", page_icon="🔥", layout="wide", initial_sidebar_state="collapsed")
except Exception:
    pass

init_session()

# =============================
# Time / stage 계산
# =============================

elapsed = int(time.time() - st.session_state.p7_started_at)
rem = int(st.session_state.p7_time_limit) - elapsed
pct = max(0.0, min(1.0, rem / float(st.session_state.p7_time_limit)))

# stage class(색/압박)
if rem <= 10:
    stage = "stage10"
elif rem <= 30:
    stage = "stage30"
elif rem <= 60:
    stage = "stage60"
else:
    stage = "stageOK"

# =============================
# CSS (P7 Battle Theme)
# =============================

st.markdown(r"""
<style>
/* ===== P7 BATTLE THEME (MOBILE FIRST) ===== */

:root{
  --p7-bgA: rgba(6, 12, 24, 0.96);
  --p7-bgB: rgba(15, 23, 42, 0.94);
  --p7-bgC: rgba(2, 6, 23, 0.94);
  --p7-cyan: rgba(0,229,255,0.92);
  --p7-blue: rgba(27,124,255,0.92);
  --p7-line: rgba(148,163,184,0.14);
  --p7-text: rgba(255,255,255,0.96);
  --p7-sub: rgba(226,232,240,0.86);
}

/* wrapper */
.p7-pack{ width:100%; }

/* HUD */
.p7-hud{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:10px;
  padding: 8px 10px;
  border-radius: 18px;
  background: rgba(255,255,255,0.10);
  border: 1px solid rgba(255,255,255,0.14);
  box-shadow: 0 10px 26px rgba(0,0,0,0.20);
  margin: 0 0 8px 0;
  color: var(--p7-text);
  font-weight: 950;
}

.p7-timer-wrap{
  height: 10px;
  border-radius: 999px;
  background: rgba(255,255,255,0.12);
  overflow:hidden;
  border: 1px solid rgba(255,255,255,0.14);
  margin: 0 0 10px 0;
}
.p7-timer-bar{
  height: 100%;
  background: linear-gradient(90deg, rgba(0,229,255,0.90), rgba(27,124,255,0.92));
}

/* BODY container */
.p7-body{
  background: linear-gradient(180deg, var(--p7-bgB), var(--p7-bgC));
  border-radius: 22px;
  padding: 14px;
  border: 1px solid rgba(148,163,184,0.16);
  box-shadow: 0 14px 34px rgba(0,0,0,0.16);
}

/* 카드 */
.p7-card{
  border-radius: 22px;
  padding: 16px;
  border: 1px solid rgba(148,163,184,0.16);
  background: rgba(255,255,255,0.06);
  box-shadow: 0 0 0 1px rgba(255,255,255,0.03);
  margin-bottom: 12px;
}

/* 텍스트: 전장만 1.2배 */
.p7-body, .p7-body *{
  font-size: 120% !important;
  font-weight: 900 !important;
  color: var(--p7-text) !important;
}

/* 선택지(라디오) 카드화 */
.p7-body div[role="radiogroup"] > label{
  background: rgba(255,255,255,0.985) !important;
  border: 1px solid rgba(148,163,184,0.28) !important;
  border-radius: 18px !important;
  box-shadow: 0 12px 28px rgba(0,0,0,0.14) !important;
  margin: 8px 0 !important;
}
.p7-body div[role="radiogroup"] > label *{
  color: rgba(2,6,23,0.92) !important;
  -webkit-text-fill-color: rgba(2,6,23,0.92) !important;
  font-weight: 900 !important;
}

/* 시간 압박 stage */
.stage60 .p7-hud{ box-shadow: 0 0 0 2px rgba(255,153,0,0.10), 0 10px 26px rgba(0,0,0,0.22); }
.stage30 .p7-hud{ box-shadow: 0 0 0 2px rgba(255,45,45,0.14), 0 10px 26px rgba(0,0,0,0.24); }
.stage10 .p7-hud{ box-shadow: 0 0 0 2px rgba(255,45,45,0.22), 0 10px 26px rgba(0,0,0,0.28); }

</style>
""", unsafe_allow_html=True)

st.markdown('<div class="p7-pack">', unsafe_allow_html=True)

# -----------------------------
# HUD + TIMER
# -----------------------------
if not st.session_state.get("p7_done", False):
    st.markdown(f"""
    <div class="p7-hud {stage}">
      <span>STEP {st.session_state.p7_step}/3</span>
      <span>TIME {mmss(rem)}</span>
      <span>MISS {st.session_state.p7_miss}/3</span>
      <span>COMBO {st.session_state.p7_combo}</span>
    </div>

    <div class="p7-timer-wrap {stage}">
      <div class="p7-timer-bar" style="width:{int(pct*100)}%"></div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------
# BODY + OPTIONS
# -----------------------------
st.markdown(f'<div class="p7-body {stage}">', unsafe_allow_html=True)


# ==========================================================
# ✅ END SCREEN (LAYOUT REPLACED)  — 요청 사항 반영
# ==========================================================
if st.session_state.p7_done:
    # ==========================================================
    # P7 END SCREEN (LAYOUT REPLACED)
    # - Mobile first / action-first
    # - CASE1: 올클리어(=step3 도달 + 실패조건 아님)만 보상 노출
    # - CASE2: 실패/시간초과는 재도전 중심
    # ==========================================================
    status = "TIMEOVER" if rem <= 0 else ("FAILED" if int(st.session_state.get("p7_miss", 0)) >= 3 else "CLEAR")
    miss = int(st.session_state.get("p7_miss", 0))
    combo = int(st.session_state.get("p7_combo", 0))
    step = int(st.session_state.get("p7_step", 1))

    # ---- END CSS (no st.success/st.error) ----
    st.markdown(r"""
    <style>
      /* END: HUD/TIMER 숨김 (전장 끝) */
      .p7-hud, .p7-timer-wrap { display:none !important; }

      /* END: compact layout */
      .p7-end-wrap{
        border-radius: 22px;
        border: 1px solid rgba(148,163,184,0.24);
        background: linear-gradient(180deg, rgba(15,23,42,0.98), rgba(2,6,23,0.98));
        box-shadow: 0 18px 46px rgba(0,0,0,0.25);
        padding: 16px 16px 14px 16px;
        margin: 8px 0 12px 0;
      }
      .p7-end-title{
        font-weight: 950;
        letter-spacing: 0.4px;
        font-size: clamp(22px, 5.2vw, 32px);
        line-height: 1.15;
        color: rgba(255,255,255,0.98);
      }
      .p7-end-sub{
        margin-top: 6px;
        font-weight: 900;
        font-size: clamp(14px, 3.6vw, 18px);
        line-height: 1.35;
        color: rgba(226,232,240,0.90);
      }
      .p7-end-banner-clear{
        border: 1px solid rgba(0,229,255,0.34);
        background: linear-gradient(180deg, rgba(0,229,255,0.13), rgba(27,124,255,0.10));
      }
      .p7-end-banner-fail{
        border: 1px solid rgba(255,45,45,0.30);
        background: linear-gradient(180deg, rgba(255,45,45,0.14), rgba(15,23,42,0.10));
      }

      /* Action cards (2-up) */
      .p7-end-actions div[data-testid="stButton"]>button{
        border-radius: 18px !important;
        padding: 14px 14px !important;
        font-weight: 950 !important;
        border: 1px solid rgba(0,229,255,0.25) !important;
        background: rgba(255,255,255,0.96) !important;
        color: rgba(2,6,23,0.92) !important;
      }
      .p7-end-actions div[data-testid="stButton"]>button:hover{
        border-color: rgba(0,229,255,0.55) !important;
        box-shadow: 0 0 0 2px rgba(0,229,255,0.10), 0 14px 38px rgba(0,0,0,0.18) !important;
      }

      /* Bottom nav */
      .p7-end-nav div[data-testid="stButton"]>button{
        border-radius: 18px !important;
        padding: 12px 14px !important;
        font-weight: 950 !important;
        border: 1px solid rgba(148,163,184,0.22) !important;
        background: rgba(15,23,42,0.92) !important;
        color: rgba(255,255,255,0.96) !important;
      }
      .p7-end-nav div[data-testid="stButton"]>button:hover{
        border-color: rgba(0,229,255,0.55) !important;
      }

      /* Reward panels: tight */
      .p7-end-panel{
        border-radius: 20px;
        border: 1px solid rgba(148,163,184,0.22);
        background: rgba(255,255,255,0.96);
        padding: 14px;
        margin: 10px 0 12px 0;
      }
      .p7-end-panel *{
        color: rgba(2,6,23,0.92) !important;
      }
      .p7-end-panel hr{ margin: 10px 0 !important; }
    </style>
    """, unsafe_allow_html=True)

    # ---- tiny helpers (keep local to END) ----
    def _go_hub():
        try:
            st.switch_page("main_hub.py")
        except Exception:
            try:
                st.switch_page("pages/00_Main_Hub.py")
            except Exception:
                st.warning("main_hub.py / pages/00_Main_Hub.py 경로를 찾지 못했습니다.")

    def _go_armory():
        try:
            st.switch_page("pages/03_Secret_Armory_Main.py")
        except Exception:
            st.warning("pages/03_Secret_Armory_Main.py 경로를 찾지 못했습니다.")

    def _render_bottom_nav(include_retry: bool):
        cols = st.columns([1, 1, 1] if include_retry else [1, 1], gap="small")
        if include_retry:
            with cols[0]:
                if st.button("🔁 RETRY", use_container_width=True, key="p7_end_retry"):
                    reset_battle()
                    st.rerun()
            with cols[1]:
                if st.button("🏠 HUB", use_container_width=True, key="p7_end_hub"):
                    _go_hub()
            with cols[2]:
                if st.button("📦 ARMORY", use_container_width=True, key="p7_end_armory"):
                    _go_armory()
        else:
            with cols[0]:
                if st.button("🏠 HUB", use_container_width=True, key="p7_end_hub"):
                    _go_hub()
            with cols[1]:
                if st.button("📦 ARMORY", use_container_width=True, key="p7_end_armory"):
                    _go_armory()

    # ---- CASE DECISION ----
    is_case1_clear = (status == "CLEAR" and step >= 3)

    if is_case1_clear:
        # =============================
        # CASE 1 – 올클리어
        # =============================
        st.markdown(
            """
            <div class="p7-end-wrap p7-end-banner-clear">
              <div class="p7-end-title">MISSION CLEAR 🎁 UNLOCKED</div>
              <div class="p7-end-sub">완전 격파. ALL TARGETS DOWN.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # action cards (2-up)
        if "p7_end_show_solution" not in st.session_state:
            st.session_state.p7_end_show_solution = False
        if "p7_end_show_vocab" not in st.session_state:
            st.session_state.p7_end_show_vocab = False

        st.markdown('<div class="p7-end-actions">', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1], gap="small")
        with c1:
            if st.button("📘 해석 & 정답 보기", use_container_width=True, key="p7_end_btn_solution"):
                st.session_state.p7_end_show_solution = True
                st.session_state.p7_end_show_vocab = False
        with c2:
            if st.button("📦 단어 선택 저장", use_container_width=True, key="p7_end_btn_vocab"):
                st.session_state.p7_end_show_vocab = True
                st.session_state.p7_end_show_solution = False
        st.markdown("</div>", unsafe_allow_html=True)

        # --- REWARD PANELS (only for CASE1) ---
        if st.session_state.p7_end_show_solution:
            st.markdown('<div class="p7-end-panel">', unsafe_allow_html=True)
            t1, t2 = st.tabs(["🈯 해석", "✅ 정답"])

            # (A) 해석: 샘플(8문장) — 기존 데이터 그대로 사용
            P7_FULL_SENTENCES_KO = [
                "직원 여러분, 다음 달 고객 지원팀이 이전될 예정임을 알려드립니다.",
                "5월 3일부터 팀은 같은 건물 5층에서 9층으로 이동합니다.",
                "새 작업 공간에는 더 빠른 협업을 위한 추가 회의 구역이 포함됩니다.",
                "직원들은 이동 전에 9층 출입 관련 안내를 새로 받게 됩니다.",
                "추가 세부 사항은 다음 주 후속 공지로 공유하겠습니다.",
                "직원 여러분, 4월 28일까지 개인 소지품을 정리해 주세요.",
                "IT 담당자가 데스크톱 컴퓨터 이동을 도와드릴 예정입니다.",
                "이번 이전 기간 동안 협조해 주셔서 감사합니다.",
            ]

            with t1:
                # 항상 8문장(올클리어 보상) 공개
                for i in range(8):
                    st.markdown(f"**{i+1}. EN** {P7_FULL_SENTENCES_EN[i]}")
                    st.markdown(f"  **KO** {P7_FULL_SENTENCES_KO[i]}")
                    if i != 7:
                        st.markdown("<hr/>", unsafe_allow_html=True)

            with t2:
                for i, s in enumerate(STEPS, start=1):
                    correct = s.options[s.answer_idx]
                    st.markdown(f"**Q{i}.** {s.question}")
                    st.markdown(f"✅ **정답:** {correct}")
                    if i != 3:
                        st.markdown("<hr/>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.p7_end_show_vocab:
            st.markdown('<div class="p7-end-panel">', unsafe_allow_html=True)

            # (C) 단어: 기존 리스트 유지 + 선택 저장
            vocab_entries = [
                {"word":"relocate", "meaning":"이전하다/이전시키다", "core":"be relocated to + 장소", "example":"The team will be relocated next month."},
                {"word":"workspace", "meaning":"작업 공간", "core":"workspace includes + 시설", "example":"The new workspace will include meeting areas."},
                {"word":"coordination", "meaning":"조정/협업", "core":"for faster coordination", "example":"Meeting areas help faster coordination."},
                {"word":"access", "meaning":"출입/접근", "core":"access instructions", "example":"Employees will receive updated access instructions."},
                {"word":"follow-up", "meaning":"후속(조치/공지)", "core":"follow-up notice", "example":"Details will be shared in a follow-up notice."},
                {"word":"belongings", "meaning":"소지품", "core":"personal belongings", "example":"Please pack your personal belongings."},
                {"word":"assist", "meaning":"돕다", "core":"assist + 사람 + with ~", "example":"IT staff will assist you with moving computers."},
                {"word":"cooperation", "meaning":"협조", "core":"appreciate your cooperation", "example":"We appreciate your cooperation."},
                {"word":"transition", "meaning":"전환/이행 기간", "core":"during this transition period", "example":"during this transition period"},
            ]

            st.markdown("**저장할 단어를 선택하세요 (최대 5개 추천)**")
            picks = []
            for i, v in enumerate(vocab_entries, start=1):
                label = f"{v['word']} — {v['meaning']}  |  {v['core']}"
                ck = st.checkbox(label, value=False, key=f"p7_end_save_{i}")
                if ck:
                    picks.append(v)

            st.markdown("<hr/>", unsafe_allow_html=True)

            if st.button("💾 선택 단어 저장", use_container_width=True, key="p7_end_vocab_save_btn"):
                if not picks:
                    st.warning("선택된 단어가 없습니다.")
                else:
                    # 저장고 파일 경로(프로젝트 루트 기준)
                    arm_dir = os.path.join("data", "armory")
                    arm_file = os.path.join(arm_dir, "p7_vocab.jsonl")
                    os.makedirs(arm_dir, exist_ok=True)
                    saved = 0
                    try:
                        with open(arm_file, "a", encoding="utf-8") as f:
                            for v in picks:
                                row = {
                                    "word": v["word"],
                                    "meaning": v["meaning"],
                                    "core": v["core"],
                                    "example": v.get("example", ""),
                                    "source": "P7",
                                }
                                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                                saved += 1
                    except Exception as e:
                        st.error(f"저장 실패: {e}")
                        saved = 0

                    if saved:
                        st.session_state.p7_end_show_vocab = False
                        st.success(f"저장 완료: {saved}개 (📦 ARMORY에서 확인)")
                        st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

        # bottom nav (HUB / ARMORY)
        st.markdown('<div class="p7-end-nav">', unsafe_allow_html=True)
        _render_bottom_nav(include_retry=False)
        st.markdown("</div>", unsafe_allow_html=True)

    else:
        # =============================
        # CASE 2 – 실패/시간초과
        # =============================
        st.markdown(
            """
            <div class="p7-end-wrap p7-end-banner-fail">
              <div class="p7-end-title">MISSION FAILED ☠</div>
              <div class="p7-end-sub">NO REWARD. RETRY?</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="p7-end-nav">', unsafe_allow_html=True)
        _render_bottom_nav(include_retry=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.stop()


# =============================
# step render
# =============================
step_idx = st.session_state.p7_step - 1
step = STEPS[step_idx]

st.markdown(f'<div class="p7-card">{build_cumulative_passage(st.session_state.p7_step)}</div>', unsafe_allow_html=True)
st.markdown(f'<div class="p7-card">{step.question}</div>', unsafe_allow_html=True)

nonce = int(st.session_state.p7_nonce)
key = f"p7_choice_{st.session_state.p7_step}_{nonce}"
choice = st.radio("choose", step.options, index=None, key=key, label_visibility="collapsed")

if choice is not None:
    picked = step.options.index(choice)
    if picked == step.answer_idx:
        st.session_state.p7_combo += 1
        if st.session_state.p7_step < 3:
            st.session_state.p7_step += 1
        else:
            st.session_state.p7_done = True
    else:
        st.session_state.p7_miss += 1
        st.session_state.p7_combo = 0
        if st.session_state.p7_miss >= 3:
            st.session_state.p7_done = True

    # reset widget safely by changing nonce
    st.session_state.p7_nonce = nonce + 1
    st.rerun()

st.markdown("</div>", unsafe_allow_html=True)  # .p7-body
st.markdown("</div>", unsafe_allow_html=True)  # .p7-pack
