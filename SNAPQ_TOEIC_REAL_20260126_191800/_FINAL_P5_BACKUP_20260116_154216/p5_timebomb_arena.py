# -*- coding: utf-8 -*-
"""
SnapQ TOEIC — P5 Timebomb Arena (CORE)
=====================================
- This file is the *actual* battle logic renderer.
- It is called by: pages/02_P5_Timebomb_Arena.py -> p5_timebomb_arena.run()

Safety rules (user request):
- Do NOT import pages modules (prevents recursion).
- Keep logic simple + stable (no fancy dynamic imports).
- UI hooks: provide class names used by the page-level CSS:
  .p5-hudwrap, .p5-timer-card, .p5-hudtime, .p5-timerbar-wrap,
  plus p5-warm / p5-warn / p5-danger / p5-shake
"""

from __future__ import annotations

import random
import time
import streamlit as st


# -----------------------------
# Optional: autorefresh helper
# -----------------------------
def _autorefresh(ms: int) -> None:
    """Refresh the app periodically (best-effort)."""
    try:
        # common add-on used in many Streamlit apps
        from streamlit_autorefresh import st_autorefresh  # type: ignore
        st_autorefresh(interval=ms, key="p5_autorefresh")
        return
    except Exception:
        pass

    # Streamlit may provide st.autorefresh depending on version
    try:
        st.autorefresh(interval=ms, key="p5_autorefresh_builtin")  # type: ignore[attr-defined]
    except Exception:
        # If not available, silently skip (timer will update on interactions)
        return


# -----------------------------
# Question bank (safe default)
# -----------------------------
_DEFAULT_QUESTIONS = [
    {
        "sentence": "Please submit the form ____ Friday.",
        "choices": ["in", "on", "by", "at"],
        "answer": "by",
    },
    {
        "sentence": "All employees must ____ their badges at all times.",
        "choices": ["wear", "wearing", "wore", "to wear"],
        "answer": "wear",
    },
    {
        "sentence": "The manager ____ the report before the meeting.",
        "choices": ["review", "reviewing", "reviewed", "was review"],
        "answer": "reviewed",
    },
    {
        "sentence": "She will give ____ presentation tomorrow.",
        "choices": ["a", "an", "the", "no article"],
        "answer": "a",
    },
    {
        "sentence": "The shipment ____ arrive by noon, according to the tracking system.",
        "choices": ["must", "should", "might", "would"],
        "answer": "should",
    },
    {
        "sentence": "The new policy will take effect ____ January 1.",
        "choices": ["in", "on", "at", "by"],
        "answer": "on",
    },
    {
        "sentence": "If you have any questions, please contact ____ immediately.",
        "choices": ["we", "us", "our", "ours"],
        "answer": "us",
    },
]


# -----------------------------
# State helpers
# -----------------------------
def _ss_init() -> None:
    ss = st.session_state
    ss.setdefault("p5_set_seconds", 40)              # set timer (matches UI)
    ss.setdefault("p5_set_started_at", time.time()) # set start timestamp
    ss.setdefault("p5_idx", 0)                       # 0..(p5_total-1)
    ss.setdefault("p5_total", 5)                     # 5 questions per run
    ss.setdefault("p5_wrong", 0)                     # wrong count (max 3)
    ss.setdefault("p5_correct", 0)
    ss.setdefault("p5_combo", 0)
    ss.setdefault("p5_best_combo", 0)
    ss.setdefault("p5_bank", [])                     # chosen questions for this run
    ss.setdefault("p5_last_answered_key", "")        # prevents double-click resubmit


def _new_run() -> None:
    ss = st.session_state
    bank = random.sample(_DEFAULT_QUESTIONS, k=min(len(_DEFAULT_QUESTIONS), ss["p5_total"]))
    ss["p5_bank"] = bank
    ss["p5_idx"] = 0
    ss["p5_wrong"] = 0
    ss["p5_correct"] = 0
    ss["p5_combo"] = 0
    ss["p5_best_combo"] = 0
    ss["p5_last_answered_key"] = ""
    ss["p5_set_started_at"] = time.time()


def _remaining_set_seconds() -> int:
    ss = st.session_state
    elapsed = int(time.time() - ss["p5_set_started_at"])
    remain = max(int(ss["p5_set_seconds"]) - elapsed, 0)
    return remain


def _timer_classes(remain: int) -> tuple[str, str]:
    """Return (timer_card_cls, timerbar_cls)"""
    if remain <= 5:
        return "p5-timer-card p5-danger", "p5-timerbar-wrap p5-danger"
    if remain <= 10:
        return "p5-timer-card p5-warn", "p5-timerbar-wrap p5-shake"
    if remain <= 20:
        return "p5-timer-card p5-warm", "p5-timerbar-wrap p5-warm"
    return "p5-timer-card", "p5-timerbar-wrap"


def _progress_ratio(remain: int) -> float:
    ss = st.session_state
    total = max(int(ss["p5_set_seconds"]), 1)
    return max(min(remain / total, 1.0), 0.0)


# -----------------------------
# Main renderer
# -----------------------------
def run() -> None:
    """
    Render P5 battle zone.
    NOTE: page-level wrapper sets page_config + global CSS.
    """
    _ss_init()

    ss = st.session_state
    if not ss["p5_bank"] or ss["p5_idx"] >= ss["p5_total"]:
        # Initialize a fresh run when missing or ended
        _new_run()

    # Timer tick (1s)
    _autorefresh(1000)
    remain = _remaining_set_seconds()

    # If time out => auto fail the run (UI only; simple reset button)
    time_out = (remain <= 0)
    if time_out:
        ss["p5_wrong"] = min(ss["p5_wrong"] + 1, 3)
        ss["p5_combo"] = 0

    # Layout: main + HUD
    left, right = st.columns([2.2, 1.0], gap="large")

    # ---------------- LEFT: battle ----------------
    with left:
        # Combo banner (kept simple; page CSS will style overall)
        st.markdown(
            f"""
            <div class="p5-combo-banner">
              <div style="font-weight:900;">⚡ 명중! 콤보 +1 (현재 {ss['p5_combo']})</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        q = ss["p5_bank"][ss["p5_idx"]]
        sentence = q["sentence"]
        choices = list(q["choices"])
        answer = q["answer"]

        # Question card (use Streamlit markdown; page CSS already styles wrappers)
        st.markdown(
            f"""
            <div style="
                background:#fff;
                border-radius:18px;
                padding:22px 18px;
                border:4px solid rgba(70,120,255,0.75);
                text-align:center;
                font-size:44px;
                font-weight:950;
                line-height:1.15;
                color:#000;
                text-shadow:none;
              ">
              {sentence}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

        # Choice buttons (instant submit)
        # Keys are important to avoid Streamlit duplicate-id issues
        for i, c in enumerate(choices):
            key = f"p5_choice_{ss['p5_idx']}_{i}_{c}"
            if st.button(f"({chr(65+i)}) {c}", key=key, use_container_width=True):
                # prevent accidental double-submit on rerun
                if ss["p5_last_answered_key"] == key:
                    st.stop()
                ss["p5_last_answered_key"] = key

                if time_out:
                    # time-out treated as wrong; refresh next question
                    pass
                elif c == answer:
                    ss["p5_correct"] += 1
                    ss["p5_combo"] += 1
                    ss["p5_best_combo"] = max(ss["p5_best_combo"], ss["p5_combo"])
                else:
                    ss["p5_wrong"] = min(ss["p5_wrong"] + 1, 3)
                    ss["p5_combo"] = 0

                # next question or reset if ended
                ss["p5_idx"] += 1
                if ss["p5_idx"] >= ss["p5_total"]:
                    # set ends -> new run
                    _new_run()

                # reset set timer each question (keeps pace game-like)
                ss["p5_set_started_at"] = time.time()
                st.experimental_rerun()

        # Emergency controls (small)
        cols = st.columns([1, 1, 1])
        with cols[0]:
            if st.button("🔄 새 런(리셋)", key="p5_reset_run"):
                _new_run()
                st.experimental_rerun()
        with cols[1]:
            st.caption("TIP: 20초↓부터 타이머가 흔들/펄스합니다.")
        with cols[2]:
            st.caption("P5 CORE SAFE")

    # ---------------- RIGHT: HUD ----------------
    with right:
        st.markdown("<div class='p5-hudwrap'>", unsafe_allow_html=True)

        st.markdown(
            """
            <div style="
              background:#fff;
              border-radius:16px;
              padding:14px 14px;
              border:2px solid rgba(0,0,0,0.12);
              text-align:center;
              font-weight:950;
              color:#000;
              text-shadow:none;
            ">
              🧩 HUD<br/>전장 상태 모니터
            </div>
            """,
            unsafe_allow_html=True,
        )

        timer_cls, bar_cls = _timer_classes(remain)
        st.markdown(
            f"""
            <div class="{timer_cls}" style="
              background:#fff;
              border-radius:16px;
              padding:16px 14px;
              margin-top:14px;
              border:2px solid rgba(0,0,0,0.12);
              text-align:center;
              color:#000;
              text-shadow:none;
            ">
              ⏱ 남은 시간<br/>
              <span class="p5-hudtime" style="font-size:56px; font-weight:950;">{remain:02d}s</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        ratio = _progress_ratio(remain)
        bar_w = int(ratio * 100)
        st.markdown(
            f"""
            <div style="margin-top:10px; text-align:center; font-weight:900;">
              세트 타이머 {remain:02d}/{int(ss['p5_set_seconds'])}s
            </div>
            <div class="{bar_cls}" style="
              height:10px;
              background:rgba(255,255,255,0.14);
              border-radius:999px;
              overflow:hidden;
              margin-top:8px;
              border:1px solid rgba(255,255,255,0.22);
            ">
              <div style="
                width:{bar_w}%;
                height:100%;
                background:rgba(255,59,48,0.92);
              "></div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

        # Wrong box
        st.markdown(
            f"""
            <div style="
              background:#fff;
              border-radius:16px;
              padding:14px 14px;
              border:2px solid rgba(0,0,0,0.12);
              text-align:center;
              color:#000;
              text-shadow:none;
            ">
              💥 오답<br/>
              <div style="display:flex; justify-content:space-between; margin-top:8px;">
                <div style="font-weight:900;">누적</div>
                <div style="font-weight:950;">{ss['p5_wrong']} / 3</div>
              </div>
              <div style="margin-top:8px; font-weight:900; color:#000;">(3회면 폭발)</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

        # Progress box
        accuracy = int((ss["p5_correct"] / max(ss["p5_correct"] + ss["p5_wrong"], 1)) * 100)
        st.markdown(
            f"""
            <div style="
              background:#fff;
              border-radius:16px;
              padding:14px 14px;
              border:2px solid rgba(0,0,0,0.12);
              text-align:left;
              color:#000;
              text-shadow:none;
            ">
              📍 진행
              <div style="margin-top:10px; display:grid; grid-template-columns:1fr 1fr; gap:6px;">
                <div style="font-weight:900;">현재</div><div style="text-align:right; font-weight:950;">{ss['p5_idx']+1} / {ss['p5_total']}</div>
                <div style="font-weight:900;">정확도</div><div style="text-align:right; font-weight:950;">{accuracy}%</div>
                <div style="font-weight:900;">콤보</div><div style="text-align:right; font-weight:950;">{ss['p5_combo']}</div>
                <div style="font-weight:900;">최고</div><div style="text-align:right; font-weight:950;">{ss['p5_best_combo']}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

        # Status box
        status = "SAFE" if ss["p5_wrong"] < 2 else ("DANGER" if ss["p5_wrong"] >= 3 else "WARN")
        st.markdown(
            f"""
            <div style="
              background:#fff;
              border-radius:16px;
              padding:14px 14px;
              border:2px solid rgba(0,0,0,0.12);
              text-align:center;
              color:#000;
              text-shadow:none;
            ">
              🧪 상태<br/>
              <div style="
                margin-top:10px;
                display:inline-block;
                padding:10px 18px;
                border-radius:999px;
                border:2px solid rgba(0,0,0,0.15);
                font-weight:950;
                background:rgba(120,255,180,0.35);
              ">
                🧨 {status}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("</div>", unsafe_allow_html=True)


# Allow running directly (not used by Streamlit pages import)
if __name__ == "__main__":
    st.set_page_config(page_title="P5 Timebomb Arena", page_icon="💣", layout="wide")
    run()
