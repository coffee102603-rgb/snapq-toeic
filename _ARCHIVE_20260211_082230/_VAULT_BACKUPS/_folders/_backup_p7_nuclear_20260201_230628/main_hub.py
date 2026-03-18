# === SNAPQ_MASTER_STAMP ===
import streamlit as st  # SNAPQ_MASTER_STAMP
st.sidebar.success("✅ RUNNING: A = snapq_toeic")  # SNAPQ_MASTER_STAMP
st.sidebar.caption("PWD(추정) : " + __file__)  # SNAPQ_MASTER_STAMP
# === /SNAPQ_MASTER_STAMP ===
# =========================================================
# SnapQ TOEIC :: MAIN HUB (Battle Lobby)
# - 구조/로직 0 변경
# - UI만: 버튼 글자 더 크고 더 진하게 (FINAL HUB VISIBILITY)
# =========================================================

import datetime
import streamlit as st

from app.core.access_guard import require_access
from app.core.pretest_gate import require_pretest_gate, mark_pretest_done

from app.core.attendance_engine import (
    mark_attendance_once,
    has_attended_today,
    is_today_mission_done,
    get_today_summary,
)

from app.core.battle_state import (
    load_profile,
    save_profile,
    record_activity_day,
)

from app.core.battle_theme import apply_battle_theme
from app.core.ui_shell import apply_ui_shell

st.set_page_config(
    page_title="SnapQ TOEIC · BATTLE HUB",
    page_icon="💣",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# SNAPQ_GLOBAL_CSS_LOADER
import os as _os
def _snapq_load_global_css():
    _candidates = [
        _os.path.join("styles","global.css"),
        _os.path.join("assets","global.css"),
    ]
    _css = ""
    for _p in _candidates:
        if _os.path.exists(_p):
            try:
                with open(_p, "r", encoding="utf-8") as _f:
                    _css = _f.read()
                break
            except Exception:
                pass
    if _css:
        st.markdown("<style>" + _css + "</style>", unsafe_allow_html=True)

_snapq_load_global_css()
# SNAPQ_GLOBAL_CSS_LOADER
apply_ui_shell(max_width_px=1040, pad_px=14)
apply_battle_theme()

# ---------------------------------------------------------
# ACCESS / PRETEST (SOFT)
# ---------------------------------------------------------
nickname = require_access()
require_pretest_gate()  # ✅ 여기서 절대 화면을 막지 않음


def today_str():
    return datetime.datetime.now().strftime("%Y-%m-%d")


def safe_switch(page: str):
    try:
        st.switch_page(page)
    except Exception:
        st.error("페이지 이동 실패")
        st.stop()


def ensure_profile_loaded() -> dict:
    if "profile" not in st.session_state or not isinstance(st.session_state.profile, dict):
        st.session_state.profile = load_profile()
    return st.session_state.profile


def safe_record_activity_day(nickname_str: str):
    profile = ensure_profile_loaded()

    try:
        record_activity_day(nickname_str)
        return
    except Exception:
        pass

    try:
        record_activity_day(profile)
        return
    except Exception:
        pass

    try:
        record_activity_day(nickname_str, profile)
        return
    except Exception:
        return


def render_sidebar():
    ensure_profile_loaded()
    profile = st.session_state.profile

    with st.sidebar:
        st.markdown("### 🎮 PLAYER HUD")
        name = st.text_input("배틀 닉네임", value=profile.get("pilot_name", ""), key="pilot_name_input")
        if name != profile.get("pilot_name", ""):
            profile["pilot_name"] = name
            save_profile(profile)


# ---------------------------------------------------------
# CSS (기존 유지 + ✅ HUB 버튼 가독성/크기 강화)
# ---------------------------------------------------------
st.markdown(
    """
<style>
:root{
  --bg:#0B0E14;
  --txt:rgba(255,255,255,.92);
  --muted:rgba(255,255,255,.70);
  --line:rgba(255,255,255,.12);

  --white:#FFFFFF;
  --ink:#0B0E14;

  --stripe-p7: linear-gradient(90deg, #00E5FF, #1B7CFF);
  --stripe-p5: linear-gradient(90deg, #FF2D55, #FF7A18);
  --stripe-arm: linear-gradient(90deg, #7C5CFF, #A78BFA);
  --stripe-stats: linear-gradient(90deg, #FFCC55, #2DD4BF);
  --stripe-p4: linear-gradient(90deg, #94A3B8, #E5E7EB);
}

/* ✅ 배경 */
html, body, .stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
[data-testid="stMainBlockContainer"]{
  background:
    radial-gradient(1000px 600px at 18% 0%, rgba(124,92,255,.18), transparent 55%),
    radial-gradient(900px 600px at 85% 10%, rgba(0,229,255,.16), transparent 55%),
    var(--bg) !important;
  color: var(--txt) !important;
}

/* 상단 크롬 제거 */
header, footer {display:none;}
[data-testid="stHeader"]{display:none !important;}
[data-testid="stToolbar"]{display:none !important;}
#MainMenu{display:none !important;}

.block-container{max-width:1040px; padding:0.9rem 0.9rem 1.2rem 0.9rem;}

/* ===== HERO ===== */
.hero-wrap{
  display:flex; align-items:center; gap:14px;
  margin: 0.2rem 0 0.6rem 0;
}
.hero-badge{
  width:50px; height:50px; border-radius:50%;
  border:2px solid #00E5FF;
  box-shadow: 0 0 18px rgba(0,229,255,.30);
  display:flex; align-items:center; justify-content:center;
  background: rgba(0,0,0,.12);
}
.hero-badge span{ font-size:22px; }

.hero-name{
  font-weight: 950;
  font-size: 20px;
  letter-spacing: .6px;
  transform: none !important;
  font-style: italic;
  font-family: "Segoe Script", "Brush Script MT", "Apple Chancery", "Comic Sans MS", cursive;
  text-shadow: 0 0 16px rgba(124,92,255,.22);
}
.hero-title{
  font-size: 11px;
  letter-spacing: 1.2px;
  color: rgba(255,255,255,.78);
  margin-top: 4px;
}
.hero-title .hackers{
  color: rgba(0,229,255,.92);
  font-weight: 950;
}

.ready-title{
  font-weight: 950;
  font-size: 46px;
  line-height: 1.0;
  text-shadow: 0 0 22px rgba(0,229,255,.16);
}
.ready-sub{
  color: var(--muted);
  font-size: 12px;
  letter-spacing: .4px;
  margin-top: 4px;
}

/* ===== PILL ===== */
.pill-row{
  display:flex; gap:10px; flex-wrap:wrap;
  margin: 0.65rem 0 1.0rem 0;
}
.pill{
  padding: 10px 14px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: rgba(255,255,255,.05);
  font-weight: 900;
  font-size: 13px;
}

/* ===== SECTION LABEL ===== */
.sec{
  margin: 0.4rem 0 0.35rem 0;
  font-size: 12px;
  letter-spacing: .28px;
  color: var(--muted);
  font-weight: 800;
}

/* ===== CARD FRAME (stripe only) ===== */
.card{
  position: relative;
  overflow: hidden;
  border-radius: 18px;
  border: 1px solid rgba(255,255,255,.10);
  background: rgba(255,255,255,.03);
  padding: 18px 12px 12px 12px;
  box-shadow: 0 14px 38px rgba(0,0,0,.34);
}
.card::before{
  content:"";
  position:absolute; left:0; top:0; right:0;
  height: 14px;
  border-bottom: 1px solid rgba(255,255,255,.10);
}
.card.p7::before{ background: var(--stripe-p7); }
.card.p5::before{ background: var(--stripe-p5); }
.card.arm::before{ background: var(--stripe-arm); }
.card.stats::before{ background: var(--stripe-stats); }
.card.p4::before{ background: var(--stripe-p4); }

/* ✅ P4 COMING SOON VISIBILITY */
.card.p4{
  border: 1.5px solid rgba(255,255,255,.85) !important;
  opacity: .88 !important;
}
.card.sub.p4 .p4-lock{
  border: 1.5px solid rgba(255,255,255,.85) !important;
  box-shadow: 0 10px 22px rgba(0,0,0,.28), 0 0 0 1px rgba(255,255,255,.10) inset !important;
}

/* =========================================================
   ✅✅ HUB BUTTON VISIBILITY + BIGGER (핵심)
   - Streamlit 버튼은 wrapper div(.card) 내부에 들어가지 않음
   - 허브에서는 st.button 자체를 흰 배경 + 검정 글자 고정
   - ✅ 크기/굵기 업 (요청 반영)
   ========================================================= */
div[data-testid="stButton"] > button{
  width: 100% !important;
  border-radius: 16px !important;
  border: 1px solid rgba(0,0,0,.10) !important;
  background: var(--white) !important;
  color: var(--ink) !important;

  font-weight: 1000 !important;      /* ✅ 더 진하게 */
  letter-spacing: .60px !important;
  text-transform: uppercase;
  white-space: pre-line !important;

  box-shadow: 0 10px 22px rgba(0,0,0,.28) !important;
  opacity: 1 !important;
  filter: none !important;
  text-shadow: none !important;

  height: 86px !important;           /* ✅ 더 크게 */
  font-size: 20px !important;        /* ✅ 더 크게 */
}
div[data-testid="stButton"] > button *{
  color: var(--ink) !important;
  opacity: 1 !important;
  text-shadow: none !important;
}
div[data-testid="stButton"] > button:hover{
  transform: translateY(-1px);
  border-color: rgba(0,229,255,.22) !important;
}

/* MAIN FIGHT (P5/P7) : 더 크게 */
.hub-mainfight div[data-testid="stButton"] > button{
  height: 176px !important;          /* ✅ 더 크게 */
  font-size: 34px !important;        /* ✅ 더 크게 */
  font-weight: 1100 !important;      /* ✅ 더 진하게 */
  letter-spacing: .80px !important;
}

/* ARMORY : 중간 크기 */
.hub-armory div[data-testid="stButton"] > button{
  height: 148px !important;          /* ✅ 더 크게 */
  font-size: 28px !important;        /* ✅ 더 크게 */
  font-weight: 1050 !important;      /* ✅ 더 진하게 */
  letter-spacing: .70px !important;
}

/* P4 LOCK (고정 박스) */
.card.sub.p4 .p4-lock{
  height: 86px;                      /* ✅ 버튼과 균형 */
  width: 100%;
  border-radius: 16px;
  border: 1px solid rgba(0,0,0,.10);
  background: var(--white);
  color: var(--ink);
  display:flex;
  align-items:center;
  justify-content:center;
  gap: 10px;
  font-weight: 1000;
  font-size: 20px;
  letter-spacing: .60px;
  text-transform: uppercase;
  box-shadow: 0 10px 22px rgba(0,0,0,.28);
  user-select: none;
}
.card.sub.p4 .p4-lock .p4-ico{font-size:18px; opacity:.9;}

.foot{
  margin-top: 0.9rem;
  text-align:center;
  font-size: 12px;
  color: var(--muted);
}

/* 모바일에서 과대 방지(그래도 크게 유지) */
@media (max-width: 768px){
  .hub-mainfight div[data-testid="stButton"] > button{
    height: 156px !important;
    font-size: 30px !important;
  }
  .hub-armory div[data-testid="stButton"] > button{
    height: 136px !important;
    font-size: 26px !important;
  }
  div[data-testid="stButton"] > button{
    height: 78px !important;
    font-size: 18px !important;
  }
}
</style>
""",
    unsafe_allow_html=True,
)

def render_lobby():
    render_sidebar()

    summary = get_today_summary(nickname)
    attended = has_attended_today(nickname)
    mission = is_today_mission_done(nickname)

    if st.session_state.get("pretest_needed") is True:
        st.info("📝 (최초 1회) 사전 설문이 아직 미완료 상태입니다. 아래에서 바로 처리하고 계속 플레이하세요.", icon="🧾")

        from app.core.pretest_gate import PRETEST_URL

        cols = st.columns([1, 1], gap="large")
        with cols[0]:
            if isinstance(PRETEST_URL, str) and PRETEST_URL.strip():
                try:
                    st.link_button("📝 PRETEST 설문 이동", PRETEST_URL, use_container_width=True)
                except Exception:
                    st.markdown(f"설문 링크: {PRETEST_URL}")
            else:
                st.warning("PRETEST_URL이 비어있습니다. (지금은 Hub 진입을 막지 않음)")

        with cols[1]:
            if st.button("✅ 설문 완료 체크(허브에서 처리)", use_container_width=True, key="hub_mark_pretest_done"):
                ok = mark_pretest_done()
                if ok:
                    st.success("✅ 완료 처리되었습니다. 이제 다시는 이 안내가 뜨지 않습니다.")
                    st.rerun()
                else:
                    st.error("닉네임을 찾지 못했습니다. 먼저 코드네임 인증을 확인하세요.")

        st.markdown("---")

    st.markdown(
        """
        <div class="hero-wrap">
          <div class="hero-badge"><span>👩‍🏫</span></div>
          <div>
            <div class="hero-name">최정은 선생님</div>
            <div class="hero-title"><span class="hackers">HACKERS</span> · SnapQ TOEIC · Battle Commander</div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="ready-title">🔥 READY</div>', unsafe_allow_html=True)
    st.markdown('<div class="ready-sub">SnapQ TOEIC · BATTLE LOBBY</div>', unsafe_allow_html=True)

    pills = []
    pills.append('<div class="pill">✅ ATTEND · DONE</div>' if attended else '<div class="pill">⚠️ ATTEND · NEED</div>')
    pills.append('<div class="pill">🎯 MISSION · DONE</div>' if mission else '<div class="pill">🎯 MISSION · READY</div>')
    pills.append(f'<div class="pill">⏱ TODAY · {summary["minutes"]}m · {summary["plays"]}x</div>')
    st.markdown(f'<div class="pill-row">{"".join(pills)}</div>', unsafe_allow_html=True)

    if not attended:
        if st.button("출석하고 출격", use_container_width=True, key="attend_start"):
            mark_attendance_once(nickname)
            st.rerun()

    st.markdown('<div class="sec">MAIN FIGHT</div>', unsafe_allow_html=True)
    colL, colR = st.columns(2, gap="large")

    # ✅ 구조/로직 0 변경: CSS 스코프용 wrapper만
    st.markdown('<div class="hub-mainfight">', unsafe_allow_html=True)
    with colL:
        st.markdown('<div class="card main p5">', unsafe_allow_html=True)
        if st.button("P5\nTIMEBOMB", use_container_width=True, key="go_p5"):
            safe_record_activity_day(nickname)
            safe_switch("pages/02_P5_Timebomb_Arena.py")
        st.markdown("</div>", unsafe_allow_html=True)

    with colR:
        st.markdown('<div class="card main p7">', unsafe_allow_html=True)
        if st.button("P7\nREADING", use_container_width=True, key="go_p7"):
            safe_record_activity_day(nickname)
            safe_switch("pages/07_P7_Reading_Arena_ZERO.py")
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sec">ARMORY</div>', unsafe_allow_html=True)
    st.markdown('<div class="hub-armory">', unsafe_allow_html=True)
    st.markdown('<div class="card main arm">', unsafe_allow_html=True)
    if st.button("ARMORY", use_container_width=True, key="go_arm"):
        safe_record_activity_day(nickname)
        safe_switch("pages/03_Secret_Armory_Main.py")
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="sec">SUB</div>', unsafe_allow_html=True)
    s1, s2 = st.columns(2, gap="large")

    with s1:
        st.markdown('<div class="card sub stats">', unsafe_allow_html=True)
        if st.button("🏆 STATS", use_container_width=True, key="go_stats"):
            safe_switch("pages/04_Scoreboard.py")
        st.markdown("</div>", unsafe_allow_html=True)

    with s2:
        st.markdown('<div class="card sub p4">', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="p4-lock" aria-disabled="true">
              <span class="p4-ico">🎧</span>
              <span class="p4-txt">P4 · COMING SOON</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(f'<div class="foot">오늘 출격: {summary["plays"]}회 · {summary["minutes"]}분</div>', unsafe_allow_html=True)


render_lobby()

# ================================
#


# ================================
#




