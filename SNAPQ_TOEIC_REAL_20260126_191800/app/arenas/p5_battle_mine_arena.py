from __future__ import annotations

import random
import time
from typing import Any, Dict, List

import streamlit as st

from app.arenas import secret_armory as arena  # type: ignore[attr-defined]

BATTLE_SETS = 5
TIME_LIMIT_SEC = 30  # 5세트(문법+지뢰) 통합 30초


def _pick_str(q: Dict[str, Any], keys: List[str], default: str = "") -> str:
    for k in keys:
        v = q.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return default


def _get_p5_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [x for x in items if isinstance(x, dict) and x.get("source") == "P5"]


def _has_mine(q: Dict[str, Any]) -> bool:
    mw = _pick_str(q, ["mine_word"], "")
    mk = _pick_str(q, ["mine_ko"], "")
    mc = q.get("mine_choices", [])
    if not (mw and mk and isinstance(mc, list) and len(mc) == 4):
        return False
    return mk in mc


def _init_state() -> None:
    st.session_state.setdefault("p5m_active", False)
    st.session_state.setdefault("p5m_start_ts", 0.0)
    st.session_state.setdefault("p5m_score", 0)
    st.session_state.setdefault("p5m_set_idx", 0)      # 0..4
    st.session_state.setdefault("p5m_stage", "lobby")  # lobby|grammar|mine|done
    st.session_state.setdefault("p5m_pack", [])
    st.session_state.setdefault("p5m_grammar_orders", [])
    st.session_state.setdefault("p5m_mine_orders", [])


def reset_battle() -> None:
    for k in ["p5m_active","p5m_start_ts","p5m_score","p5m_set_idx","p5m_stage","p5m_pack","p5m_grammar_orders","p5m_mine_orders"]:
        if k in st.session_state:
            del st.session_state[k]
    _init_state()


def _remaining() -> int:
    start = float(st.session_state.get("p5m_start_ts", 0.0) or 0.0)
    if start <= 0:
        return TIME_LIMIT_SEC
    return int(TIME_LIMIT_SEC - (time.time() - start))


def _time_up() -> bool:
    return _remaining() <= 0


def _shuffle4(lst: List[str]) -> List[str]:
    out = lst[:]
    random.shuffle(out)
    return out


def _start_battle() -> None:
    items = arena._load_armory_items()  # type: ignore[attr-defined]
    p5 = _get_p5_items(items)
    mined = [q for q in p5 if _has_mine(q)]

    if len(mined) < BATTLE_SETS:
        st.error(f"💣 지뢰 탄약 부족: mine 설정된 P5 문제가 {len(mined)}개입니다. (최소 {BATTLE_SETS}개 필요)")
        st.info("TIP) 먼저 TRAIN/무기고에서 문제에 mine_word/mine_ko/mine_choices(4지선다)를 채워주세요.")
        st.stop()

    pack = random.sample(mined, BATTLE_SETS)

    g_orders = []
    m_orders = []
    for q in pack:
        ch = list(q.get("choices", []) or [])[:4]
        while len(ch) < 4:
            ch.append("")
        g_orders.append(_shuffle4(ch))

        mc = [str(x) for x in (q.get("mine_choices") or [])][:4]
        m_orders.append(_shuffle4(mc))

    st.session_state["p5m_pack"] = pack
    st.session_state["p5m_grammar_orders"] = g_orders
    st.session_state["p5m_mine_orders"] = m_orders

    st.session_state["p5m_active"] = True
    st.session_state["p5m_start_ts"] = time.time()
    st.session_state["p5m_score"] = 0
    st.session_state["p5m_set_idx"] = 0
    st.session_state["p5m_stage"] = "grammar"


def _inject_css() -> None:
    st.markdown(
        """
<style>
.p5m-hud{display:flex;align-items:center;justify-content:space-between;gap:12px;margin:6px 0 10px 0;}
.p5m-title{display:flex;align-items:center;gap:10px;font-weight:950;font-size:2.0rem;color:#f9fafb;}
.p5m-dot{width:16px;height:16px;border-radius:5px;background:linear-gradient(180deg,rgba(255,160,60,.95),rgba(255,80,90,.65));box-shadow:0 10px 18px rgba(0,0,0,.25);}
.p5m-timer{padding:6px 10px;border-radius:999px;background:rgba(0,0,0,0.28);border:1px solid rgba(255,255,255,0.22);color:#f9fafb;font-weight:950;}
.p5m-timer.danger{background:rgba(244,63,94,0.22);border-color:rgba(244,63,94,0.45);animation:p5mPulse .9s ease-in-out infinite;}
@keyframes p5mPulse{0%{transform:scale(1.00);}50%{transform:scale(1.05);}100%{transform:scale(1.00);}}

.p5m-hub div[data-testid="stButton"]>button{width:42px!important;min-width:42px!important;height:32px!important;min-height:32px!important;padding:0!important;border-radius:12px!important;font-weight:950!important;background:rgba(255,255,255,0.92)!important;border:2px solid rgba(203,213,225,0.95)!important;box-shadow:0 8px 16px rgba(0,0,0,.12)!important;}

.p5m-paper{background:rgba(255,255,255,0.96);border:3px solid rgba(203,213,225,0.92);border-radius:18px;padding:14px 16px;box-shadow:0 18px 40px rgba(0,0,0,.18);}
.p5m-q{color:#111827;font-weight:950;font-size:1.55rem;line-height:1.42;}
.p5m-sub{margin-top:10px;background:rgba(255,255,255,0.92);border:2px solid rgba(203,213,225,0.75);border-radius:16px;padding:12px 14px;box-shadow:0 14px 30px rgba(0,0,0,.14);}

.p5m-opt div[data-testid="stButton"]>button{background:linear-gradient(180deg,rgba(255,255,255,0.98),rgba(255,248,235,0.92))!important;border:2px solid rgba(203,213,225,0.95)!important;border-radius:18px!important;min-height:62px!important;box-shadow:0 16px 32px rgba(0,0,0,.14)!important;}
.p5m-opt div[data-testid="stButton"]>button,.p5m-opt div[data-testid="stButton"]>button *{color:#111827!important;-webkit-text-fill-color:#111827!important;font-weight:950!important;}
.p5m-opt div[data-testid="stButton"]{margin-top:1px!important;margin-bottom:1px!important;}

.p5m-card{background:rgba(255,255,255,0.92);border:2px solid rgba(203,213,225,0.9);border-radius:18px;padding:14px 16px;box-shadow:0 18px 40px rgba(0,0,0,.16);}
</style>
        """,
        unsafe_allow_html=True,
    )


def _go_hub() -> None:
    try:
        from streamlit_extras.switch_page_button import switch_page  # type: ignore
        switch_page("main_hub")
    except Exception:
        try:
            st.switch_page("main_hub.py")
        except Exception:
            st.warning("Main Hub 이동 실패: 좌측 사이드바에서 이동해주세요.")


def render() -> None:
    _init_state()
    _inject_css()

    remain = max(0, _remaining())
    danger = remain <= 10

    # HUD
    l, r = st.columns([12, 2])
    with l:
        st.markdown("<div class='p5m-hud'><div class='p5m-title'><span class='p5m-dot'></span> P5 BATTLE+MINE · 지뢰전</div></div>", unsafe_allow_html=True)
    with r:
        st.markdown(f"<div class='p5m-timer {'danger' if danger else ''}'>⏱ {remain}s</div>", unsafe_allow_html=True)
        st.markdown("<div class='p5m-hub'>", unsafe_allow_html=True)
        if st.button("🏠", key="p5m_go_hub"):
            _go_hub()
        st.markdown("</div>", unsafe_allow_html=True)

    if _time_up() and st.session_state.get("p5m_stage") not in ("lobby","done"):
        st.session_state["p5m_stage"] = "done"
        st.session_state["p5m_active"] = False

    stage = st.session_state.get("p5m_stage", "lobby")

    # Lobby
    if stage == "lobby":
        st.markdown(
            "<div class='p5m-card'>"
            "<h3 style='margin:0 0 6px 0'>💣 지뢰전 규칙</h3>"
            "<div>• 5세트 × (문법 1 + 지뢰단어 1) = 총 10문항</div>"
            "<div>• 통합 30초 / 선택 즉시 제출 / 자동 진행</div>"
            "<div style='opacity:.75;margin-top:6px'>※ mine 데이터가 있는 문제만 출제됩니다.</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        c1, c2 = st.columns([3, 2])
        with c1:
            if st.button("🚀 출격(Start)", use_container_width=True, key="p5m_start"):
                _start_battle()
                st.rerun()
        with c2:
            if st.button("🏠 Hub", use_container_width=True, key="p5m_hub2"):
                _go_hub()
        st.stop()

    # Done
    if stage == "done":
        score = int(st.session_state.get("p5m_score", 0))
        verdict = "✅ CLEAR" if score >= 8 else ("⚠️ CLOSE" if score >= 6 else "❌ FAIL")
        st.markdown(
            f"<div class='p5m-card'>"
            f"<h3 style='margin:0 0 6px 0'>{verdict}</h3>"
            f"<div style='font-weight:950;font-size:1.4rem'>Score: {score} / 10</div>"
            f"<div style='opacity:.75;margin-top:6px'>지뢰전은 중간 해설 없이 끝까지 달립니다.</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        b1, b2 = st.columns(2)
        with b1:
            if st.button("🔁 다시하기", use_container_width=True, key="p5m_retry"):
                reset_battle()
                st.rerun()
        with b2:
            if st.button("🏠 Hub", use_container_width=True, key="p5m_hub3"):
                _go_hub()
        st.stop()

    # Active battle
    pack: List[Dict[str, Any]] = st.session_state.get("p5m_pack", [])
    set_idx = int(st.session_state.get("p5m_set_idx", 0))
    if set_idx >= BATTLE_SETS:
        st.session_state["p5m_stage"] = "done"
        st.session_state["p5m_active"] = False
        st.rerun()

    q = pack[set_idx]
    sentence = _pick_str(q, ["sentence", "q", "question"], "(문제 없음)")
    answer = _pick_str(q, ["answer", "correct", "correct_answer", "ans"], "")
    g_choices = st.session_state.get("p5m_grammar_orders", [[]])[set_idx]

    # Paper header
    st.markdown(
        f"<div class='p5m-paper'><div class='p5m-q'>Set {set_idx+1}/{BATTLE_SETS} · "
        f"{'문법' if stage=='grammar' else '지뢰단어'}<br><span style='opacity:.9'>{sentence}</span></div></div>",
        unsafe_allow_html=True,
    )

    labels = ["(A)","(B)","(C)","(D)"]

    if stage == "grammar":
        cols1 = st.columns(2, gap="large")
        cols2 = st.columns(2, gap="large")
        grid = cols1 + cols2
        for i, opt in enumerate(g_choices[:4]):
            with grid[i]:
                st.markdown("<div class='p5m-opt'>", unsafe_allow_html=True)
                if st.button(f"{labels[i]} {opt}".strip(), key=f"p5m_g_{set_idx}_{i}", use_container_width=True):
                    if opt == answer:
                        st.session_state["p5m_score"] = int(st.session_state["p5m_score"]) + 1
                    st.session_state["p5m_stage"] = "mine"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    elif stage == "mine":
        mw = _pick_str(q, ["mine_word"], "")
        mk = _pick_str(q, ["mine_ko"], "")
        m_choices = st.session_state.get("p5m_mine_orders", [[]])[set_idx]

        st.markdown("<div class='p5m-sub'><h4 style='margin:0'>💣 Mine Word: <b>" + mw + "</b></h4>"
                    "<div style='margin-top:4px;font-weight:850'>뜻으로 가장 가까운 것은?</div></div>",
                    unsafe_allow_html=True)

        cols1 = st.columns(2, gap="large")
        cols2 = st.columns(2, gap="large")
        grid = cols1 + cols2

        for i, opt in enumerate(m_choices[:4]):
            with grid[i]:
                st.markdown("<div class='p5m-opt'>", unsafe_allow_html=True)
                if st.button(f"{labels[i]} {opt}".strip(), key=f"p5m_m_{set_idx}_{i}", use_container_width=True):
                    if opt == mk:
                        st.session_state["p5m_score"] = int(st.session_state["p5m_score"]) + 1
                    st.session_state["p5m_set_idx"] = set_idx + 1
                    st.session_state["p5m_stage"] = "grammar"
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)