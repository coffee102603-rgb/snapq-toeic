# >>> REMAIN_SERVER_GUARD_v1
try:
    remain_server
except Exception:
    try:
        remain_server = int(_remain()) if '_remain' in globals() else None
    except Exception:
        remain_server = None
    if remain_server is None:
        try:
            import streamlit as st
            remain_server = int(st.session_state.get('server_remain', 9999))
        except Exception:
            remain_server = 9999
# <<< REMAIN_SERVER_GUARD_v1

from __future__ import annotations

import json
import random
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import streamlit as st
st.sidebar.error("🔥 ENGINE CHECK: LOADED THIS FILE")
from app.arenas import secret_armory as armory


# ============================================================
# SNAPQ TOEIC - P5 EXAM (10Q · 33s TOTAL) [HARDCORE]
# - 전체 33초(10문항 합산)
# - 오답 즉사(Sudden Death)
# - 1세트 = 좌/우 2레인(왼쪽 P5 원형, 오른쪽 뜻체크)
# - 선택지는 2x2 카드 터치(클릭 즉시 판정)
# - ✅ LIVE TIMER: JS에서 33,32,31... 확실히 감소 + POP + SHAKE
# - ✅ TIMER GAUGE: 상단 바가 같이 줄어듦(드라마틱)
# - ✅ MOBILE: 2열 -> 1열 자동 스택(공간 절약)
# ============================================================

ARENA_VER = "P5_EXAM_10Q_33S__v1.8__A_PLAN_HUD__SHAKE10S__2026-01-26"

TOTAL_Q = 10
SETS = 5
TIME_LIMIT = 33  # ✅ 전체 33초 TOTAL


# ----------------------------
# Basic helpers
# ----------------------------
def _rerun() -> None:
    st.rerun()


def _project_root_guess() -> Path:
    return Path(__file__).resolve().parents[2]


def _init_state() -> None:
    ss = st.session_state
    ss.setdefault("ex10_active", False)
    ss.setdefault("ex10_start", 0.0)
    ss.setdefault("ex10_done", False)
    ss.setdefault("ex10_fail_reason", "")
    ss.setdefault("ex10_score", 0)
    ss.setdefault("ex10_pack", [])
    ss.setdefault("ex10_set_idx", 0)

    ss.setdefault("ex10_q1_done", False)
    ss.setdefault("ex10_q2_done", False)

    ss.setdefault("ex10_q1_pick", None)  # str
    ss.setdefault("ex10_q2_pick", None)  # str

    ss.setdefault("ex10_bank_path_used", "")


def _remain() -> int:
    start = float(st.session_state.get("ex10_start", 0.0) or 0.0)
    if start <= 0:
        return TIME_LIMIT
    return max(0, int(TIME_LIMIT - (time.time() - start)))


def _fail(reason: str) -> None:
    st.session_state["ex10_done"] = True
    st.session_state["ex10_active"] = False
    st.session_state["ex10_fail_reason"] = reason


def _success() -> None:
    st.session_state["ex10_done"] = True
    st.session_state["ex10_active"] = False
    st.session_state["ex10_fail_reason"] = ""


def _reset_run() -> None:
    st.session_state["ex10_active"] = False
    st.session_state["ex10_start"] = 0.0
    st.session_state["ex10_done"] = False
    st.session_state["ex10_fail_reason"] = ""
    st.session_state["ex10_score"] = 0
    st.session_state["ex10_pack"] = []
    st.session_state["ex10_set_idx"] = 0
    st.session_state["ex10_q1_done"] = False
    st.session_state["ex10_q2_done"] = False
    st.session_state["ex10_q1_pick"] = None
    st.session_state["ex10_q2_pick"] = None

    for k in list(st.session_state.keys()):
        if k.startswith("ex10_btn_"):
            try:
                del st.session_state[k]
            except Exception:
                pass


# ----------------------------
# Word bank loader
# ----------------------------
def _load_word_bank() -> Tuple[Dict[str, Any], str]:
    root = _project_root_guess()
    candidates = [
        root / "data" / "word_bank.json",
        root / "app" / "data" / "word_bank.json",
        Path.cwd() / "data" / "word_bank.json",
    ]

    for p in candidates:
        try:
            if p.exists():
                with p.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict):
                    data.pop("_meta", None)
                    return data, str(p)
        except Exception:
            continue

    return {}, "(not found)"


# ----------------------------
# Armory items -> P5 items
# ----------------------------
def _pick_str(d: Dict[str, Any], keys: List[str], default: str = "") -> str:
    for k in keys:
        v = d.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return default


def _p5_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        tag = _pick_str(it, ["tag", "arena", "type", "kind"], "").upper()
        if "P5" in tag:
            out.append(it)
            continue

        s = _pick_str(it, ["sentence", "q", "question"], "")
        choices = it.get("choices")
        ans = _pick_str(it, ["answer", "ans", "correct"], "")
        if s and isinstance(choices, list) and len(choices) >= 4 and ans:
            out.append(it)
    return out


def _find_target_word(sentence: str, bank: Dict[str, Any]) -> Tuple[str, str]:
    if not sentence or not bank:
        return "", "word"
    lower = sentence.lower()
    hits = []
    for k in bank.keys():
        if not isinstance(k, str) or not k.strip():
            continue
        kk = k.strip().lower()
        if kk and kk in lower:
            hits.append(k.strip())
    if hits:
        hits.sort(key=len, reverse=True)
        return hits[0], "word"
    return "", "word"


def _make_q2(target: str, bank: Dict[str, Any]) -> Dict[str, Any]:
    entry = bank.get(target)
    if not isinstance(entry, dict):
        return {}
    ko_correct = str(entry.get("ko_correct", "")).strip()
    ko_wrongs = entry.get("ko_wrongs", [])
    if not (ko_correct and isinstance(ko_wrongs, list) and len(ko_wrongs) >= 3):
        return {}

    wrongs = [str(x).strip() for x in ko_wrongs if isinstance(x, str) and str(x).strip()]
    if len(wrongs) < 3:
        return {}

    choices = wrongs[:3] + [ko_correct]
    random.shuffle(choices)
    return {"target": target, "choices": choices[:4], "answer": ko_correct}


def _highlight_target(sentence: str, target: str) -> str:
    if not sentence:
        return ""
    if target:
        pattern = re.compile(re.escape(target), re.IGNORECASE)
        return pattern.sub(lambda m: f"<span class='ex10-neon'>{m.group(0)}</span>", sentence)
    p = re.compile(r"\b([A-Za-z][A-Za-z'\-]{2,})\b", re.IGNORECASE)
    return p.sub(lambda m: f"<span class='ex10-blink'>{m.group(0)}</span>", sentence, count=1)


# ----------------------------
# Game start: build pack (5 sets)
# ----------------------------
def _start_game() -> None:
    bank, used_path = _load_word_bank()
    st.session_state["ex10_bank_path_used"] = used_path

    if not bank:
        _fail(f"Word Bank not found or empty: {used_path}")
        return

    items = armory._load_armory_items()
    p5 = _p5_items(items)
    if len(p5) < SETS:
        _fail(f"Not enough P5 items in armory: {len(p5)} (need {SETS})")
        return

    eligible: List[Dict[str, Any]] = []
    for q in p5:
        sentence = _pick_str(q, ["sentence", "q", "question"], "")
        choices = q.get("choices", [])
        answer = _pick_str(q, ["answer", "ans", "correct"], "")
        if sentence and isinstance(choices, list) and len(choices) >= 4 and answer:
            eligible.append(q)

    if len(eligible) < SETS:
        _fail(f"Not enough eligible items: {len(eligible)} (need {SETS})")
        return

    random.shuffle(eligible)
    picked = eligible[:SETS]

    pack: List[Dict[str, Any]] = []
    for q in picked:
        sentence = _pick_str(q, ["sentence", "q", "question"], "")
        target, _kind = _find_target_word(sentence, bank)
        q2 = _make_q2(target, bank) if target else {}

        pack.append(
            {
                "sentence": sentence,
                "target": target,
                "sentence_html": _highlight_target(sentence, target),
                "q1_choices": list(q.get("choices", []))[:4],
                "q1_answer": _pick_str(q, ["answer", "ans", "correct"], ""),
                "q2": q2,
            }
        )

    st.session_state["ex10_pack"] = pack
    st.session_state["ex10_set_idx"] = 0

    st.session_state["ex10_q1_done"] = False
    st.session_state["ex10_q2_done"] = False
    st.session_state["ex10_q1_pick"] = None
    st.session_state["ex10_q2_pick"] = None

    st.session_state["ex10_score"] = 0
    st.session_state["ex10_active"] = True
    st.session_state["ex10_done"] = False
    st.session_state["ex10_fail_reason"] = ""
    st.session_state["ex10_start"] = time.time()
    _rerun()


# ----------------------------
# ✅ DRAMATIC LIVE TIMER (Front-end JS)
# - 숫자: 매초 POP(커졌다가 복귀)
# - 10초 이하: SHAKE + 붉은 flash
# - 게이지: width%가 계속 줄어듦
# ----------------------------
def _render_live_timer_js() -> None:
    if not st.session_state.get("ex10_active", False):
        return
    start = float(st.session_state.get("ex10_start", 0.0) or 0.0)
    if start <= 0:
        return

    start_ms = int(start * 1000)
    limit = int(TIME_LIMIT)

    st.markdown(
        f"""
<script>
(function() {{
  const START_MS = {start_ms};
  const LIMIT = {limit};

  const numId = "ex10-timer-num";
  const badgeId = "ex10-timer-badge";
  const gaugeId = "ex10-gauge-fill";

  let lastSec = null;

  function tick() {{
    const now = Date.now();
    let remain = Math.floor(LIMIT - (now - START_MS)/1000);
    if (remain < 0) remain = 0;

    const numEl = document.getElementById(numId);
    const badge = document.getElementById(badgeId);
    const gauge = document.getElementById(gaugeId);

    if (numEl) numEl.textContent = String(remain);

    // gauge
    if (gauge) {{
      const pct = Math.max(0, Math.min(100, (remain / LIMIT) * 100));
      gauge.style.width = pct.toFixed(2) + "%";
      if (remain <= 10) gauge.classList.add("panic");
      else gauge.classList.remove("panic");
    }}

    // danger class
    if (badge) {{
      if (remain <= 12) badge.classList.add("danger");
      else badge.classList.remove("danger");
      if (remain <= 10) badge.classList.add("panic");
      else badge.classList.remove("panic");
    }}

    // per-second "POP" animation
    if (lastSec === null) lastSec = remain;
    if (remain !== lastSec) {{
      lastSec = remain;
      if (badge) {{
        badge.classList.remove("tick");
        void badge.offsetWidth; // reflow
        badge.classList.add("tick");
      }}
      if (remain <= 10 && badge) {{
        badge.classList.remove("flash");
        void badge.offsetWidth;
        badge.classList.add("flash");
      }}
    }}
  }}

  tick();
  if (!window.__EX10_TIMER__) {{
    window.__EX10_TIMER__ = setInterval(tick, 120);
  }}
}})();
</script>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------
# UI: Card grid (2x2) touch
# ----------------------------
def _render_card_grid(
    options: List[str],
    selected: str | None,
    disabled: bool,
    key_prefix: str,
    tone: str,
) -> str | None:
    if not options or len(options) < 4:
        return None

    rows = [(0, 1), (2, 3)]
    clicked: str | None = None
    hint_cls = "ex10-cardhint-left" if tone == "left" else "ex10-cardhint-right"

    for r_i, (a, b) in enumerate(rows):
        c1, c2 = st.columns(2, gap="small")
        with c1:
            k = f"{key_prefix}_{r_i}_{a}"
            is_sel = (selected == options[a])
            if st.button(options[a], use_container_width=True, disabled=disabled, key=k):
                clicked = options[a]
            st.markdown(f"<div class='{hint_cls} {'sel' if is_sel else ''}'></div>", unsafe_allow_html=True)
        with c2:
            k = f"{key_prefix}_{r_i}_{b}"
            is_sel = (selected == options[b])
            if st.button(options[b], use_container_width=True, disabled=disabled, key=k):
                clicked = options[b]
            st.markdown(f"<div class='{hint_cls} {'sel' if is_sel else ''}'></div>", unsafe_allow_html=True)

    return clicked


# ----------------------------
# CSS
# ----------------------------
def _inject_css() -> None:
    st.markdown(
        r"""
<style>
/* ===== SCOPE ===== */
.ex10-scope, .ex10-scope *{ opacity:1 !important; filter:none !important; color:inherit; }
.ex10-scope{ color:#f9fafb !important; }

div[data-testid="stAppViewContainer"]{
  background: radial-gradient(1200px 800px at 20% 10%, rgba(120,30,60,.35), transparent 60%),
              radial-gradient(1200px 800px at 80% 20%, rgba(30,80,140,.30), transparent 55%),
              linear-gradient(180deg, rgba(8,10,14,1) 0%, rgba(12,12,16,1) 100%) !important;
}
.block-container{ max-width: 1150px !important; padding-top: 0.75rem !important; }

/* HUD */
.ex10-hud{display:flex;align-items:center;justify-content:space-between;margin:6px 0 10px 0;}

/* A-PLAN: ultra compact mode pills */
.ex10-hud-left{display:flex;flex-direction:column;gap:6px;min-width:0;}
.ex10-modebar{display:flex;gap:8px;flex-wrap:wrap;align-items:center;}
.ex10-pill{
  display:inline-flex;align-items:center;gap:6px;
  padding:6px 10px;border-radius:999px;
  font-weight:950;font-size:12px;letter-spacing:.2px;
  border:1px solid rgba(255,255,255,.18);
  background: rgba(0,0,0,.26);
  color:#fff !important;
  line-height:1;
}
.ex10-pill.red{border-color:rgba(255,120,120,.30); background:rgba(255,60,60,.12);}
.ex10-pill.green{border-color:rgba(120,255,220,.28); background:rgba(40,255,190,.10);}
.ex10-pill.gray{border-color:rgba(255,255,255,.14); background:rgba(255,255,255,.07); color:#e9e9ff !important;}

.ex10-title{font-weight:950;font-size:44px;letter-spacing:-0.6px;color:#fff !important;text-shadow:0 2px 12px rgba(0,0,0,.35);}
.ex10-title .sub{font-weight:900;font-size:20px;margin-left:10px;color:#e7e7ff !important;}

/* TIMER BADGE (dramatic) */
.ex10-timer{
  padding:10px 14px;border-radius:999px;
  background:rgba(0,0,0,.40);
  border:1px solid rgba(255,255,255,.22);
  font-weight:950;font-size:22px;color:#fff !important;
  display:flex; align-items:center; gap:8px;
  box-shadow: 0 14px 28px rgba(0,0,0,.28);
  animation: ex10float 2.0s ease-in-out infinite;
  will-change: transform;
}
@keyframes ex10float{
  0%{ transform: translateY(0px); }
  50%{ transform: translateY(-3px); }
  100%{ transform: translateY(0px); }
}
.ex10-timer.danger{
  background:rgba(255,60,60,.24);
  border:1px solid rgba(255,120,120,.55);
}
.ex10-timer.tick{
  animation: ex10pop .22s ease-out 1, ex10float 2.0s ease-in-out infinite;
}
@keyframes ex10pop{
  0%{ transform: scale(1); }
  55%{ transform: scale(1.10); }
  100%{ transform: scale(1); }
}
.ex10-timer.panic{
  box-shadow: 0 0 0 2px rgba(255,80,80,.10), 0 18px 40px rgba(255,60,60,.16);
}
.ex10-timer.flash{
  animation: ex10flash .18s ease-out 1, ex10float 2.0s ease-in-out infinite;
}

@keyframes ex10shake{
  0%{ transform: translateX(0px); }
  20%{ transform: translateX(-2px); }
  40%{ transform: translateX(2px); }
  60%{ transform: translateX(-1px); }
  80%{ transform: translateX(1px); }
  100%{ transform: translateX(0px); }
}
.ex10-timer.shake{
  animation: ex10shake .35s ease-in-out infinite, ex10float 2.0s ease-in-out infinite;
}

@keyframes ex10flash{
  0%{ filter: brightness(1.0); }
  40%{ filter: brightness(1.35); }
  100%{ filter: brightness(1.0); }
}
@keyframes ex10shake{
  0%{ transform: translateX(0); }
  25%{ transform: translateX(-2px); }
  50%{ transform: translateX(2px); }
  75%{ transform: translateX(-2px); }
  100%{ transform: translateX(0); }
}
.ex10-timer.panic.tick{ animation: ex10pop .22s ease-out 1, ex10shake .18s linear 1, ex10float 2.0s ease-in-out infinite; }

/* TIMER GAUGE */
.ex10-gauge{
  height: 10px;
  border-radius: 999px;
  border:1px solid rgba(255,255,255,.10);
  background: rgba(255,255,255,.06);
  overflow:hidden;
  margin: 6px 0 12px 0;
}
.ex10-gauge > div{
  height:100%;
  width:100%;
  border-radius:999px;
  background: linear-gradient(90deg, rgba(255,120,120,.36), rgba(255,255,255,.07), rgba(90,255,210,.36));
  transition: width .12s linear;
}
.ex10-gauge > div.panic{
  background: linear-gradient(90deg, rgba(255,70,70,.55), rgba(255,255,255,.06), rgba(255,70,70,.40));
  box-shadow: inset 0 0 12px rgba(255,60,60,.18);
}

/* Chips */
.ex10-topchips{display:flex;gap:10px;align-items:center;margin:0 0 8px 0;}
.ex10-chip{
  display:inline-block;
  padding:6px 12px;border-radius:999px;
  font-weight:950;font-size:12px;
  border:1px solid rgba(255,255,255,.18);
  background: rgba(0,0,0,.25);
  color:#fff !important;
}
.ex10-chip.red { border-color: rgba(255,150,150,.45); background: rgba(255,80,80,.10); }
.ex10-chip.green{ border-color: rgba(120,255,220,.55); background: rgba(30,255,190,.12); }

/* Lanes container (PC=2col, Mobile=1col) */
.ex10-lanes{display:grid;grid-template-columns: 1fr 1fr; gap:12px; margin-top:6px;}
.ex10-divider{
  height: 10px;border-radius:999px;margin: 8px 0 10px 0;
  background: linear-gradient(90deg, rgba(255,120,120,.26), rgba(255,255,255,.06), rgba(90,255,210,.26));
  border:1px solid rgba(255,255,255,.10);
}

/* Lane cards */
.ex10-lane{
  border-radius:18px;
  border:1px solid rgba(255,255,255,.16);
  box-shadow: 0 12px 26px rgba(0,0,0,.28);
  padding:12px 12px;
}
.ex10-lane.left{
  background: radial-gradient(900px 360px at 10% 0%, rgba(255,80,80,.20), transparent 60%),
              linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.03));
}
.ex10-lane.right{
  background: radial-gradient(900px 360px at 10% 0%, rgba(40,255,190,.18), transparent 60%),
              linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.03));
  border-color: rgba(120,255,220,.22);
}

.ex10-lane-title{
  font-weight:950;font-size:16px;margin-bottom:8px;color:#fff !important;
  display:flex;align-items:center;gap:8px;
}

/* Question box */
.ex10-sentence{
  border-radius:14px;
  border:1px solid rgba(255,255,255,.14);
  background: rgba(0,0,0,.32);
  padding:12px 12px;
  font-weight:900;font-size:20px;line-height:1.33;
  color:#fff !important;margin-bottom:10px;
}
.ex10-lane.right .ex10-sentence{
  border-color: rgba(120,255,220,.20);
  background: rgba(0,0,0,.28);
}

/* target */
.ex10-neon{
  padding:0 4px;border-radius:6px;
  background: rgba(40,255,190,.20);
  box-shadow: 0 0 0 2px rgba(40,255,190,.12);
  font-weight:950;
}
.ex10-blink{animation: ex10blink 1s infinite;font-weight:950;}
@keyframes ex10blink { 0%{opacity:1} 50%{opacity:.22} 100%{opacity:1} }

/* Buttons */
div[data-testid="stButton"] > button{
  border-radius:14px !important;
  padding:14px 12px !important;
  font-weight:950 !important;
  font-size:17px !important;
  text-align:left !important;
  border:1px solid rgba(255,255,255,.18) !important;
  background: rgba(255,255,255,.10) !important;
  color:#ffffff !important;
  box-shadow: 0 10px 22px rgba(0,0,0,.22);
  transition: .12s ease;
  cursor: pointer !important;
}
div[data-testid="stButton"] > button:hover{ transform: translateY(-1px); filter: brightness(1.06); }

/* Selection hints */
.ex10-cardhint-left, .ex10-cardhint-right{
  height:6px;margin:6px 2px 10px 2px;border-radius:999px;background:rgba(255,255,255,.10);
}
.ex10-cardhint-left.sel{background: rgba(255,120,120,.45);}
.ex10-cardhint-right.sel{background: rgba(120,255,220,.45);}

/* START zone */
.ex10-startzone{
  margin-top:14px;border-radius:20px;border:1px solid rgba(255,255,255,.18);
  background: linear-gradient(135deg, rgba(16,16,22,.78), rgba(50,12,22,.62));
  padding:16px 16px;
  box-shadow: 0 12px 26px rgba(0,0,0,.32);
}
.ex10-startzone *{ color:#fff !important; }
.ex10-brief{font-weight:950;font-size:17px;line-height:1.55;}

/* ✅ MOBILE OPTIMIZATION */
@media (max-width: 720px){
  .block-container{ padding-left: .6rem !important; padding-right: .6rem !important; padding-top:.55rem !important; }
  .ex10-title{ font-size:34px; }
  .ex10-title .sub{ font-size:16px; }
  .ex10-timer{ font-size:18px; padding:8px 12px; }
  .ex10-lanes{ grid-template-columns: 1fr; gap:10px; }
  .ex10-sentence{ font-size:18px; padding:10px 10px; }
  div[data-testid="stButton"] > button{ font-size:16px !important; padding:12px 10px !important; }

  /* Streamlit columns -> 모바일에서 1열로 자연 스택 (공간 압박 해결) */
  div[data-testid="stHorizontalBlock"]{ gap: .5rem !important; }
  div[data-testid="column"]{ width:100% !important; flex: 1 1 100% !important; }
}
</style>
        """,
        unsafe_allow_html=True,
    )


# ----------------------------
# Main render
# ----------------------------
def render() -> None:
    # ✅ ALWAYS define set_idx before any use (prevents UnboundLocalError)
    if 'p5_exam_set_idx' not in st.session_state:
        st.session_state['p5_exam_set_idx'] = 0
    set_idx = int(st.session_state.get('p5_exam_set_idx', 0))

    remain_server = _remain()
    st.markdown("<div class='ex10-scope'>", unsafe_allow_html=True)

    # HUD
# >>> REMAIN_SERVER_GUARD_v1
try:
    remain_server
except Exception:
    try:
        # prefer a helper if present
        remain_server = int(_remain()) if '_remain' in globals() else None
    except Exception:
        remain_server = None
    if remain_server is None:
        # last resort: infer from session_state timer if any
        try:
            remain_server = int(st.session_state.get('server_remain', 9999))
        except Exception:
            remain_server = 9999
# <<< REMAIN_SERVER_GUARD_v1

    timer_cls = "danger" if remain_server <= 12 else ""
    st.markdown(
        f"""
<div class="ex10-hud">
  <div class="ex10-hud-left">
    <div class="ex10-title">🔥 P5 EXAM <span class="sub">10Q · 33s</span></div>
    <div class="ex10-modebar">
      <span class="ex10-pill red">🧱 P5 ORIGINAL</span>
      <span class="ex10-pill green">💡 MEANING CHECK</span>
      <span class="ex10-pill gray">{'SET '+str(set_idx+1)+'/5' if st.session_state.get('ex10_active', False) else 'READY'}</span>
    </div>
  </div>
  <div class="ex10-timer {timer_cls}" id="ex10-timer-badge">
    💣 <span id="ex10-timer-num">{remain_server}</span>s
  </div>
</div>
<div class="ex10-gauge">
  <div id="ex10-gauge-fill"></div>
</div>
        """,
        unsafe_allow_html=True,
    )
    _render_live_timer_js()

    # DEBUG
    with st.sidebar.expander("🛠 DEBUG HUD", expanded=False):
                st.code(f"""__file__:
        {Path(__file__).resolve()}

        cwd:
        {Path.cwd()}""")
        st.json(
            {
                "ARENA_VER": ARENA_VER,
                "active": st.session_state.get("ex10_active"),
                "done": st.session_state.get("ex10_done"),
                "remain_server": remain_server,
                "score": st.session_state.get("ex10_score"),
                "set_idx": st.session_state.get("ex10_set_idx"),
                "q1_done": st.session_state.get("ex10_q1_done"),
                "q2_done": st.session_state.get("ex10_q2_done"),
                "q1_pick": st.session_state.get("ex10_q1_pick"),
                "q2_pick": st.session_state.get("ex10_q2_pick"),
                "fail_reason": st.session_state.get("ex10_fail_reason"),
                "bank_path_used": st.session_state.get("ex10_bank_path_used"),
            }
        )
        if st.button("🔄 SAFE RESET (this run only)", use_container_width=True):
            _reset_run()
            _rerun()

    # RESULT
    if st.session_state.get("ex10_done", False):
        score = int(st.session_state.get("ex10_score", 0))
        reason = str(st.session_state.get("ex10_fail_reason", "")).strip()

        if reason:
            st.error(f"💀 FAIL (Sudden Death) — {reason}")
        else:
            st.success(f"🏆 CLEAR! Perfect 10/10 — Score: {score}/{TOTAL_Q}")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔁 Restart", use_container_width=True):
                _reset_run()
                _rerun()
        with c2:
            if st.button("🚪 Back to Start", use_container_width=True):
                _reset_run()
                _rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        return

    # START
    if not bool(st.session_state.get("ex10_active", False)):
        st.markdown(
            """
<div class="ex10-startzone">
  <div class="ex10-brief">
    🎮 Commander Brief<br>
    - <b>10Q</b> / <b>33s TOTAL</b> (ultra hardcore)<br>
    - Wrong = <b>Sudden Death</b><br>
    - Perfect <b>10/10</b> only = CLEAR
  </div>
</div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("🚀 START MISSION", use_container_width=True):
            _start_game()
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # TIME OVER (서버 판정)
    if remain_server <= 0:
        _fail("Timebomb exploded: Time over (33s total)")
        _rerun()
        return

    # ACTIVE SET
    pack: List[Dict[str, Any]] = st.session_state.get("ex10_pack", [])
    set_idx = int(st.session_state.get("ex10_set_idx", 0))

    if set_idx >= SETS:
        if int(st.session_state.get("ex10_score", 0)) == TOTAL_Q:
            _success()
        else:
            _fail("Not perfect (must be 10/10)")
        _rerun()
        return

    q = pack[set_idx]
    sentence_html = str(q.get("sentence_html", q.get("sentence", "")))
    target = str(q.get("target", "")).strip()

    q1_choices = list(q.get("q1_choices", []) or [])[:4]
    q1_answer = str(q.get("q1_answer", "")).strip()

    q2_obj = q.get("q2", {}) if isinstance(q.get("q2", {}), dict) else {}
    q2_choices = list(q2_obj.get("choices", []) or [])[:4]
    q2_answer = str(q2_obj.get("answer", "")).strip()

    labels = ["(A)", "(B)", "(C)", "(D)"]
    q1_cards = [f"{labels[i]} {q1_choices[i]}".strip() for i in range(4)] if len(q1_choices) == 4 else []
    q2_cards = [f"{labels[i]} {q2_choices[i]}".strip() for i in range(4)] if len(q2_choices) == 4 else []
    # (A-PLAN) Top chips moved into HUD to save vertical space.
    # 2-LANE layout (모바일은 CSS에서 1열로 자동)
    st.markdown("<div class='ex10-lanes'>", unsafe_allow_html=True)

    # LEFT: P5 Original
    st.markdown("<div class='ex10-lane left'>", unsafe_allow_html=True)
    st.markdown("<div class='ex10-lane-title'>🧱 <span class='ex10-chip red'>P5 Original</span></div>", unsafe_allow_html=True)
    st.markdown(f"<div class='ex10-sentence'>{sentence_html}</div>", unsafe_allow_html=True)

    q1_done = bool(st.session_state.get("ex10_q1_done", False))
    q1_pick = st.session_state.get("ex10_q1_pick")

    clicked_q1 = _render_card_grid(
        options=q1_cards,
        selected=q1_pick,
        disabled=q1_done,
        key_prefix=f"ex10_btn_q1_set{set_idx}",
        tone="left",
    )

    if clicked_q1 and not q1_done:
        st.session_state["ex10_q1_pick"] = clicked_q1
        picked_raw = clicked_q1[4:].strip() if clicked_q1.startswith("(") else clicked_q1
        if picked_raw != q1_answer:
            _fail(f"Wrong: Set{set_idx+1}-Q1")
            _rerun()
            return

        st.session_state["ex10_score"] = int(st.session_state["ex10_score"]) + 1
        st.session_state["ex10_q1_done"] = True
        _rerun()
        return

    if q1_done:
        st.success("Q1 ✅ CLEAR")

    st.markdown("</div>", unsafe_allow_html=True)

    # RIGHT: Meaning Check
    st.markdown("<div class='ex10-lane right'>", unsafe_allow_html=True)
    st.markdown("<div class='ex10-lane-title'>💡 <span class='ex10-chip green'>Meaning Check</span></div>", unsafe_allow_html=True)

    if not target:
        st.info("Target word not detected in sentence.")
    else:
        st.markdown(
            f"<div class='ex10-sentence'>Target: <span class='ex10-neon'>{target}</span></div>",
            unsafe_allow_html=True,
        )

    q2_done = bool(st.session_state.get("ex10_q2_done", False))
    q2_pick = st.session_state.get("ex10_q2_pick")

    if not q2_cards or not q2_answer:
        st.warning("Q2 data 부족(Word Bank 매칭 실패).")
        st.caption("word_bank.json에 target 항목이 있는지 확인 필요")
    else:
        clicked_q2 = _render_card_grid(
            options=q2_cards,
            selected=q2_pick,
            disabled=q2_done,
            key_prefix=f"ex10_btn_q2_set{set_idx}",
            tone="right",
        )

        if clicked_q2 and not q2_done:
            st.session_state["ex10_q2_pick"] = clicked_q2
            picked_raw = clicked_q2[4:].strip() if clicked_q2.startswith("(") else clicked_q2
            if picked_raw != q2_answer:
                _fail(f"Wrong: Set{set_idx+1}-Q2")
                _rerun()
                return

            st.session_state["ex10_score"] = int(st.session_state["ex10_score"]) + 1
            st.session_state["ex10_q2_done"] = True
            _rerun()
            return

        if q2_done:
            st.success("Q2 ✅ CLEAR")

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)  # lanes end

    # 세트 완료 → 다음 세트
    if bool(st.session_state.get("ex10_q1_done", False)) and bool(st.session_state.get("ex10_q2_done", False)):
        st.session_state["ex10_set_idx"] = set_idx + 1
        st.session_state["ex10_q1_done"] = False
        st.session_state["ex10_q2_done"] = False
        st.session_state["ex10_q1_pick"] = None
        st.session_state["ex10_q2_pick"] = None
        _rerun()
        return

    st.markdown("</div>", unsafe_allow_html=True)

