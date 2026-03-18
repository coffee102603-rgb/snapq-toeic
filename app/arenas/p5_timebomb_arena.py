# app/arenas/p5_timebomb_arena.py
# === P5_PASSFIX_FINAL_LOCK ===
# PASS(SAVE) 화면:
# - 밑으로 내려가도 절대 어두워지지 않게(Expander 내부 div까지 WHITE 강제)
# - 표시 순서: 정답 -> 해석 -> 해설
# - "내답" 제거
# - 모바일: PASS 글자 1.1배 + line-height 1.6 + 체크박스 텍스트 굵게
# 저장:
# - 기존 data/armory/p5_saved.jsonl 백업 유지
# - app/data/armory/secret_armory.json 에 source="P5"로 append하여 Secret Armory와 연결

from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import streamlit as st

# --- SNAPQ_MAIN_HUB_NAV (auto) ---
try:
    _hub_col, _hub_spacer = st.columns([1.4, 8.6])
    with _hub_col:
        if st.button("🏠 MAIN HUB", key=f"hub_{__file__}", use_container_width=True):
            try:
                st.switch_page("main_hub.py")
            except Exception:
                st.info("좌측 메뉴(사이드바)에서 Main Hub로 이동해주세요.")
except Exception:
    pass
# --- /SNAPQ_MAIN_HUB_NAV ---



def _rerun() -> None:
    if hasattr(st, "rerun"):
        st.rerun()
        return
    if hasattr(st, "experimental_rerun"):
        st.experimental_rerun()  # type: ignore[attr-defined]


def _autorefresh(ms: int) -> None:
    try:
        from streamlit_autorefresh import st_autorefresh  # type: ignore
        st_autorefresh(interval=ms, key="p5_autorefresh")
        return
    except Exception:
        pass
    try:
        st.autorefresh(interval=ms, key="p5_autorefresh_builtin")  # type: ignore[attr-defined]
    except Exception:
        return


def _inject_p5_css() -> None:
    st.markdown(
        """
        <style>
        :root{
          --p5-accent:#FF2D55;
          --p5-accent-soft: rgba(255, 45, 85, 0.26);
          --p5-accent-softer: rgba(255, 45, 85, 0.14);
        }

        [data-testid="stAppViewContainer"]{
          background: radial-gradient(1100px 700px at 28% 20%,
            rgba(255, 60, 80, 0.32),
            rgba(80, 0, 20, 0.58),
            rgba(0,0,0,0.92)) !important;
        }
        .block-container{ max-width:1200px !important; padding-top: 0.9rem !important; }

        .p5-hudwrap{
          display:flex; flex-direction:column; gap:14px;
          position: sticky; top: 0.9rem;
        }
        .p5-hud-bottom{ margin-top:auto; }

        .p5-card{
          background: rgba(255,255,255,0.92);
          border: 2px solid rgba(0,0,0,0.10);
          border-radius: 18px;
          padding: 18px 16px;
          box-shadow: 0 10px 30px rgba(0,0,0,0.30);
        }

        .p5-hudtime{
          font-size:56px; font-weight:950; letter-spacing:-1px;
          color:#000;
        }
        .p5-hudtime-accent{ color: var(--p5-accent) !important; }

        .p5-combo-banner{
          margin: 0.15rem 0 0.65rem 0;
          color:#fff; font-size:18px; font-weight:900;
          text-shadow: 0 2px 10px rgba(0,0,0,0.65);
        }

        div[data-testid="stButton"] > button{
          width: 100%;
          padding: 14px 16px !important;
          border-radius: 14px !important;
          border: 1px solid rgba(0,0,0,0.18) !important;
          background: rgba(255,255,255,0.92) !important;
          color: #111 !important;
          font-size: 20px !important;
          font-weight: 900 !important;
        }
        div[data-testid="stButton"] > button:hover{
          border-color: rgba(255,45,85,0.90) !important;
          transform: translateY(-1px);
        }

        .p5-bounce{
          animation: p5bounce 0.55s ease-in-out infinite;
          border-color: var(--p5-accent) !important;
          border-width: 5px !important;
          box-shadow: 0 0 0 6px var(--p5-accent-soft);
        }
        @keyframes p5bounce{
          0%   { transform: scale(1.00); }
          50%  { transform: scale(1.02); }
          100% { transform: scale(1.00); }
        }

        .p5-shake{ animation: p5shake 0.18s linear infinite; }
        @keyframes p5shake{
          0%{ transform: translate(0px,0px); }
          25%{ transform: translate(1px,-1px); }
          50%{ transform: translate(-1px,1px); }
          75%{ transform: translate(1px,1px); }
          100%{ transform: translate(-1px,-1px); }
        }

        .p5-qbox{
          background:#fff;
          border-radius:18px;
          padding:22px 18px;
          border:5px solid var(--p5-accent);
          text-align:center;
          font-size:44px;
          font-weight:950;
          line-height:1.15;
          color:#000;
          box-shadow: 0 10px 30px rgba(0,0,0,0.22);
        }

        a[data-testid="stPageLink-NavLink"]{
          display:block !important;
          width:100% !important;
          padding: 12px 12px !important;
          border-radius: 14px !important;
          background: rgba(255,255,255,0.92) !important;
          border: 2px solid rgba(0,0,0,0.14) !important;
          font-weight: 900 !important;
          color: #000 !important;
          text-decoration: none !important;
          text-align:center !important;
          font-size: 16px !important;
        }

        /* =========================================================
           ✅ PASS(SAVE) BRIGHT LOCK (ULTRA)
           - expander 내부의 모든 하위 div까지 흰색/검정 강제
           - 밑으로 내려가도 절대 어두워지지 않게
           ========================================================= */

        /* PASS 영역 전체 배경도 흰색 레이어로 한번 덮기 */
        .p5-passfix{
          background: rgba(255,255,255,0.00);
        }

        /* expander 본체 + 펼친 영역 + 하위 div 전부 WHITE */
        .p5-passfix div[data-testid="stExpander"],
        .p5-passfix div[data-testid="stExpander"] > details,
        .p5-passfix div[data-testid="stExpanderDetails"],
        .p5-passfix div[data-testid="stExpanderDetails"] > div,
        .p5-passfix div[data-testid="stExpanderDetails"] div,
        .p5-passfix div[data-testid="stExpander"] div{
          background: #ffffff !important;
        }

        .p5-passfix div[data-testid="stExpander"]{
          border: 1px solid rgba(0,0,0,0.12) !important;
          border-radius: 16px !important;
          box-shadow: 0 10px 22px rgba(0,0,0,0.12) !important;
        }

        .p5-passfix div[data-testid="stExpander"] summary{
          background: #ffffff !important;
          border-radius: 16px !important;
          padding: 14px 14px !important;
          font-weight: 950 !important;
          color: #111 !important;
        }
        .p5-passfix div[data-testid="stExpander"] summary *{ color:#111 !important; }

        /* PASS 영역 텍스트는 무조건 검정 */
        .p5-passfix [data-testid="stMarkdownContainer"],
        .p5-passfix .stMarkdown, .p5-passfix .stMarkdown *{
          color:#111 !important;
          opacity:1 !important;
          filter:none !important;
          text-shadow:none !important;
        }

        /* ✅ 우리가 넣는 카드 (정답/해석/해설) */
        .p5-expcard{
          background:#ffffff !important;
          border: 1px solid rgba(0,0,0,0.10) !important;
          border-radius: 14px !important;
          padding: 14px 14px !important;
          margin-top: 10px !important;
        }
        .p5-expcard *{ color:#111 !important; }

        .p5-line{
          font-size: 16px;
          line-height: 1.55;
          margin: 6px 0;
          font-weight: 850;
        }
        .p5-key{ font-weight: 950; }
        .p5-val{ font-weight: 900; }

        /* ✅ 체크박스 텍스트 굵게 */
        .p5-passfix label,
        .p5-passfix label *{
          color:#111 !important;
          opacity:1 !important;
          font-weight: 900 !important;
        }

        /* =========================================================
           ✅ MOBILE PASS MODE
           - 글자 1.1배 + line-height 1.6 + 체크박스 더 굵게
           ========================================================= */
        @media (max-width: 640px){
          .p5-line{
            font-size: 17.6px;   /* 16 * 1.1 */
            line-height: 1.6;
          }
          .p5-expcard{ padding: 16px 14px !important; }
          .p5-passfix label, .p5-passfix label *{
            font-weight: 950 !important;
          }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _nav_button(label: str, target: str, key: str):
    if hasattr(st, "page_link"):
        try:
            st.page_link(target, label=label, use_container_width=True)  # type: ignore[attr-defined]
            return
        except Exception:
            pass
    if hasattr(st, "switch_page"):
        if st.button(label, key=key, use_container_width=True):
            try:
                st.switch_page(target)  # type: ignore[attr-defined]
            except Exception:
                st.info("이 환경에선 네비게이션이 제한될 수 있어요. (브라우저 뒤로가기/좌측 메뉴)")
        return
    st.button(label, key=key, use_container_width=True, disabled=True)


@dataclass
class Q:
    sentence: str
    choices: list[str]
    answer: str
    ko: str
    explain: str


GRAMMAR_BANK = [
    Q("Please submit the form ____ Friday.", ["in", "on", "by", "at"], "by",
      "금요일까지 서류를 제출해 주세요.", "마감은 by. on은 '금요일에(그날)'."),

    Q("All employees must ____ their badges at all times.", ["wear", "wearing", "wore", "to wear"], "wear",
      "모든 직원은 항상 배지를 착용해야 합니다.", "must 뒤에는 동사원형."),

    Q("The manager ____ the report before the meeting.", ["review", "reviewing", "reviewed", "was review"], "reviewed",
      "매니저는 회의 전에 보고서를 검토했습니다.", "과거 시점이면 reviewed."),

    Q("The shipment ____ arrive by noon, according to the tracking system.", ["must", "should", "might", "would"], "must",
      "추적 시스템에 따르면 그 배송은 정오까지 도착할 것입니다.", "근거 기반 강한 추정 must."),

    Q("If you have any questions, please contact ____ immediately.", ["we", "us", "our", "ours"], "us",
      "질문이 있으면 즉시 저희에게 연락해 주세요.", "contact는 목적어 필요 → us."),

    Q("She will give ____ presentation tomorrow.", ["a", "an", "the", "no article"], "a",
      "그녀는 내일 발표를 할 것입니다.", "단수 가산명사 presentation 앞 a."),
]

VOCA_BANK = [
    Q("The word closest in meaning to 'rapid' is ____.", ["quick", "silent", "careful", "empty"], "quick",
      "‘rapid’와 의미가 가장 가까운 단어는 ____이다.", "rapid = quick/fast."),
]


def _ss_init():
    ss = st.session_state
    ss.setdefault("p5_mode", "grammar")
    ss.setdefault("p5_set_seconds", 40)
    ss.setdefault("p5_total", 5)
    ss.setdefault("p5_wrong_limit", 3)

    ss.setdefault("p5_bank", [])
    ss.setdefault("p5_idx", 0)
    ss.setdefault("p5_set_started_at", time.time())
    ss.setdefault("p5_done", False)
    ss.setdefault("p5_time_over", False)

    ss.setdefault("p5_wrong", 0)
    ss.setdefault("p5_correct", 0)
    ss.setdefault("p5_combo", 0)
    ss.setdefault("p5_best_combo", 0)

    ss.setdefault("p5_user_choices", [])  # [{q, picked, is_correct}]


def _pick_bank():
    return GRAMMAR_BANK if st.session_state.get("p5_mode") == "grammar" else VOCA_BANK


def _new_run():
    ss = st.session_state
    bank = _pick_bank()
    ss["p5_bank"] = random.sample(bank, k=min(ss["p5_total"], len(bank)))
    ss["p5_idx"] = 0
    ss["p5_done"] = False
    ss["p5_time_over"] = False
    ss["p5_wrong"] = 0
    ss["p5_correct"] = 0
    ss["p5_combo"] = 0
    ss["p5_best_combo"] = 0
    ss["p5_user_choices"] = []
    ss["p5_set_started_at"] = time.time()


def _remain() -> int:
    ss = st.session_state
    elapsed = int(time.time() - ss["p5_set_started_at"])
    return max(int(ss["p5_set_seconds"]) - elapsed, 0)


def _save_to_armory(selected_rows: list[dict]):
    base = Path("data/armory")
    base.mkdir(parents=True, exist_ok=True)
    path = base / "p5_saved.jsonl"
    payload = {
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "mode": st.session_state.get("p5_mode"),
        "set_seconds": st.session_state.get("p5_set_seconds"),
        "items": selected_rows,
    }
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return str(path)


def _append_to_secret_armory(selected_rows: list[dict]) -> str:
    """Secret Armory가 읽는 app/data/armory/secret_armory.json에 source='P5'로 append."""
    try:
        app_dir = Path(__file__).resolve().parents[1]  # .../app
        data_dir = app_dir / "data" / "armory"
        data_dir.mkdir(parents=True, exist_ok=True)
        armory_path = data_dir / "secret_armory.json"

        if armory_path.exists():
            raw = armory_path.read_text(encoding="utf-8", errors="ignore").strip()
            items = json.loads(raw) if raw else []
        else:
            items = []

        if not isinstance(items, list):
            items = []

        added = 0
        for r in selected_rows:
            sig = (r.get("sentence", ""), r.get("answer", ""))
            if any(
                isinstance(x, dict)
                and x.get("source") == "P5"
                and (x.get("sentence"), x.get("answer")) == sig
                for x in items
            ):
                continue

            items.append({
                "source": "P5",
                "mode": "p5_saved",
                "sentence": r.get("sentence", ""),
                "choices": r.get("choices", []),
                "answer": r.get("answer", ""),
                "ko": r.get("ko", ""),
                "explain": r.get("explain", ""),
            })
            added += 1

        armory_path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
        return f"{armory_path} (+{added})"
    except Exception:
        return "app/data/armory/secret_armory.json (write failed)"


def _render_hud_battle(remain: int):
    ss = st.session_state
    timer_card_cls = "p5-card"
    num_cls = "p5-hudtime"
    if remain <= 20:
        timer_card_cls = "p5-card p5-bounce"
        num_cls = "p5-hudtime p5-hudtime-accent"
    if remain <= 10:
        timer_card_cls = "p5-card p5-bounce p5-shake"
        num_cls = "p5-hudtime p5-hudtime-accent"

    st.markdown("<div class='p5-hudwrap'>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="p5-card" style="text-align:center; font-weight:950;">
          🧩 HUD<br/>전장 상태 모니터
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="{timer_card_cls}" style="text-align:center;">
          ⏱ 남은 시간<br/>
          <div class="{num_cls}">{remain:02d}s</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="p5-card" style="text-align:center;">
          💥 오답<br/>
          <div style="display:flex; justify-content:space-between; margin-top:10px;">
            <div style="font-weight:900;">누적</div>
            <div style="font-weight:950;">{ss['p5_wrong']} / {ss['p5_wrong_limit']}</div>
          </div>
          <div style="margin-top:8px; font-weight:900;">(3회면 폭발)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div class='p5-hud-bottom'>", unsafe_allow_html=True)
    _nav_button("🏠 MAIN HUB", "main_hub.py", "p5_battle_to_hub")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def _render_pass_screen():
    """PASS(SAVE) 화면: 밝기 고정 + 모바일 강화 + 정답/해석/해설만 출력"""
    ss = st.session_state
    st.markdown("<div class='p5-passfix'>", unsafe_allow_html=True)

    st.markdown(
        """
        <div style="background:#fff;border-radius:18px;padding:22px 18px;border:5px solid rgba(60,200,120,0.70);
          text-align:center;font-size:38px;font-weight:950;color:#000;">
          ✅ 통과! 해설/저장(SAVE) 해금
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    st.markdown("### ✅ 5문제 정답/해석/해설 + 저장(SAVE)")

    selected_rows: list[dict] = []
    for i, row in enumerate(ss["p5_user_choices"]):
        q: Q = row["q"]
        is_correct = row["is_correct"]

        with st.expander(f"Q{i+1} {'✅' if is_correct else '❌'}  {q.sentence}", expanded=False):
            st.markdown(
                f"""
                <div class="p5-expcard">
                  <div class="p5-line"><span class="p5-key">정답:</span> <span class="p5-val">{q.answer}</span></div>
                  <div class="p5-line"><span class="p5-key">해석:</span> <span class="p5-val">{q.ko}</span></div>
                  <div class="p5-line"><span class="p5-key">해설:</span> <span class="p5-val">{q.explain}</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            if st.checkbox("이 문항을 병기고에 저장(SAVE)", key=f"p5_save_{i}"):
                selected_rows.append(
                    {
                        "sentence": q.sentence,
                        "choices": q.choices,
                        "answer": q.answer,
                        "ko": q.ko,
                        "explain": q.explain,
                    }
                )

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 1], gap="medium")

    with c1:
        if st.button("💾 SAVE → 병기고(Secret Armory)", use_container_width=True, key="p5_save_btn"):
            if not selected_rows:
                st.warning("저장할 문항을 체크해 주세요.")
            else:
                saved_path = _save_to_armory(selected_rows)
                armory_path = _append_to_secret_armory(selected_rows)
                st.success(f"SAVE 완료! 1)백업:{saved_path}  2)Armory:{armory_path}")

    with c2:
        if st.button("🔄 새 런 시작", use_container_width=True, key="p5_restart_after_pass"):
            _new_run()
            _rerun()

    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
    n1, n2, n3 = st.columns(3, gap="medium")
    with n1:
        _nav_button("🏠 Main Hub", "main_hub.py", "p5_pass_nav_hub")
    with n2:
        _nav_button("📊 Scoreboard", "pages/04_Scoreboard.py", "p5_pass_nav_score")
    with n3:
        _nav_button("🗡 Secret Armory", "pages/03_Secret_Armory_Main.py", "p5_pass_nav_armory")

    st.markdown("</div>", unsafe_allow_html=True)  # p5-passfix end


def run():
    _ss_init()
    _inject_p5_css()

    ss = st.session_state
    if not ss["p5_bank"]:
        _new_run()

    if not ss["p5_done"]:
        _autorefresh(1000)

    remain = _remain()

    if remain <= 0 and not ss["p5_done"]:
        ss["p5_done"] = True
        ss["p5_time_over"] = True

    if ss["p5_done"] or ss["p5_idx"] >= ss["p5_total"] or ss["p5_wrong"] >= ss["p5_wrong_limit"]:
        ss["p5_done"] = True
        passed = (ss["p5_correct"] >= 4) and (not ss["p5_time_over"]) and (ss["p5_wrong"] < ss["p5_wrong_limit"])
        if passed:
            _render_pass_screen()
            return

        st.markdown(
            """
            <div style="background:#fff;border-radius:18px;padding:22px 18px;border:5px solid rgba(255,60,80,0.90);
              text-align:center;font-size:38px;font-weight:950;color:#000;">
              💥 폭발! (무효)
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 재도전(새 런)", use_container_width=True, key="p5_retry_fail"):
            _new_run()
            _rerun()
        _nav_button("🏠 MAIN HUB", "main_hub.py", "p5_fail_to_hub")
        return

    left, right = st.columns([2.2, 1.0], gap="large")
    with right:
        _render_hud_battle(remain)

    with left:
        q: Q = ss["p5_bank"][ss["p5_idx"]]
        st.markdown(
            f'<div class="p5-combo-banner">⚡ 명중! 콤보 +1 (현재 {ss["p5_combo"]})</div>',
            unsafe_allow_html=True,
        )

        st.markdown(f"""<div class="p5-qbox">{q.sentence}</div>""", unsafe_allow_html=True)
        st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)

        for i, c in enumerate(q.choices):
            key = f"p5_choice_{ss['p5_idx']}_{i}_{c}"
            if st.button(f"({chr(65+i)}) {c}", key=key, use_container_width=True):
                is_correct = (c == q.answer)
                ss["p5_user_choices"].append({"q": q, "picked": c, "is_correct": is_correct})

                if is_correct:
                    ss["p5_correct"] += 1
                    ss["p5_combo"] += 1
                    ss["p5_best_combo"] = max(ss["p5_best_combo"], ss["p5_combo"])
                else:
                    ss["p5_wrong"] += 1
                    ss["p5_combo"] = 0

                ss["p5_idx"] += 1
                if ss["p5_wrong"] >= ss["p5_wrong_limit"] or ss["p5_idx"] >= ss["p5_total"]:
                    ss["p5_done"] = True

                _rerun()
                return
