from __future__ import annotations

import json
import os
import random
import re
import time
from typing import Any, Dict, List, Tuple

import streamlit as st
from app.arenas import secret_armory as armory  # type: ignore[attr-defined]

SENTENCES = 5
TOTAL_Q = 10
TIME_LIMIT = 33  # total seconds (10Q)
# Sudden Death: any wrong or time up -> FAIL


def _load_word_bank() -> Dict[str, Any]:
    path = os.path.join("data", "word_bank.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            data.pop("_meta", None)
            return data
    except Exception:
        return {}
    return {}


def _tokenize(text: str) -> List[str]:
    return re.findall(r"[a-zA-Z]+", text.lower())


def _p5_items(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [x for x in items if isinstance(x, dict) and x.get("source") == "P5"]


def _pick_str(q: Dict[str, Any], keys: List[str], default: str = "") -> str:
    for k in keys:
        v = q.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return default


def _init():
    st.session_state.setdefault("ex10_active", False)
    st.session_state.setdefault("ex10_start", 0.0)
    st.session_state.setdefault("ex10_sent_idx", 0)
    st.session_state.setdefault("ex10_subq", 1)
    st.session_state.setdefault("ex10_score", 0)
    st.session_state.setdefault("ex10_pack", [])
    st.session_state.setdefault("ex10_done", False)
    st.session_state.setdefault("ex10_fail_reason", "")
    st.session_state.setdefault("ex10_q2", {})
    st.session_state.setdefault("ex10_target", "")
    st.session_state.setdefault("ex10_target_kind", "word")
    st.session_state.setdefault("ex10_sentence_u", "")


def reset():
    for k in [
        "ex10_active","ex10_start","ex10_sent_idx","ex10_subq","ex10_score",
        "ex10_pack","ex10_done","ex10_fail_reason","ex10_q2",
        "ex10_target","ex10_target_kind","ex10_sentence_u"
    ]:
        if k in st.session_state:
            del st.session_state[k]
    _init()


def _remain() -> int:
    start = float(st.session_state.get("ex10_start", 0.0) or 0.0)
    if start <= 0:
        return TIME_LIMIT
    return int(TIME_LIMIT - (time.time() - start))


def _fail(reason: str):
    st.session_state["ex10_done"] = True
    st.session_state["ex10_active"] = False
    st.session_state["ex10_fail_reason"] = reason


def _success():
    st.session_state["ex10_done"] = True
    st.session_state["ex10_active"] = False
    st.session_state["ex10_fail_reason"] = ""


def _find_phrase_targets(sentence_l: str, bank: Dict[str, Any]) -> List[str]:
    # phrase = key with space
    phrases = [k for k, v in bank.items() if isinstance(k, str) and " " in k and isinstance(v, dict) and v.get("kind") == "phrase"]
    hits = []
    for ph in phrases:
        if ph in sentence_l:
            hits.append(ph)
    return hits


def _find_word_targets(sentence: str, bank: Dict[str, Any]) -> List[str]:
    toks = _tokenize(sentence)
    hits = []
    for t in toks:
        v = bank.get(t)
        if isinstance(v, dict) and v.get("kind") == "word":
            hits.append(t)
    return list(dict.fromkeys(hits))  # unique preserve order


def _pick_target(sentence: str, bank: Dict[str, Any]) -> Tuple[str, str]:
    s_l = sentence.lower()

    # 1) phrase first (more educational)
    ph_hits = _find_phrase_targets(s_l, bank)
    if ph_hits:
        return random.choice(ph_hits), "phrase"

    # 2) word next
    w_hits = _find_word_targets(sentence, bank)
    if w_hits:
        # prefer longer words for better learning
        w_hits.sort(key=len, reverse=True)
        return w_hits[0], "word"

    return "", "word"


def _underline_once(sentence: str, target: str, kind: str) -> str:
    """
    Return HTML sentence with one underline for target.
    """
    if not target:
        return sentence

    if kind == "phrase":
        # case-insensitive replace first occurrence
        pattern = re.compile(re.escape(target), re.IGNORECASE)
        return pattern.sub(lambda m: f"<u>{m.group(0)}</u>", sentence, count=1)

    # word: underline whole word
    pattern = re.compile(rf"\b{re.escape(target)}\b", re.IGNORECASE)
    return pattern.sub(lambda m: f"<u>{m.group(0)}</u>", sentence, count=1)


def _make_q2(sentence: str, target: str, kind: str, bank: Dict[str, Any]) -> Dict[str, Any]:
    entry = bank.get(target, None)
    if not isinstance(entry, dict):
        return {}

    ko_correct = str(entry.get("ko_correct", "")).strip()
    ko_wrongs = entry.get("ko_wrongs", [])
    if not (ko_correct and isinstance(ko_wrongs, list) and len(ko_wrongs) >= 3):
        return {}

    # Only 2 types: word / phrase (prompt is English)
    if kind == "phrase":
        prompt = "What is the closest meaning of the underlined phrase?"
    else:
        prompt = "What is the closest meaning of the underlined word?"

    choices = [ko_correct] + [str(x) for x in ko_wrongs[:3]]
    random.shuffle(choices)
    return {"prompt": prompt, "choices": choices, "answer": ko_correct}


def _start_exam():
    bank = _load_word_bank()
    if not bank:
        # SAFE: do not Sudden-Death on missing word bank
        st.warning('🧩 Word Bank가 비어 있어요 → 일반 탄약으로 보충해서 진행합니다.')
        bank = {}
    items = armory._load_armory_items()  # type: ignore[attr-defined]
    p5 = _p5_items(items)
    if len(p5) < SENTENCES:
        _fail(f"Not enough P5 items in armory: {len(p5)} (need {SENTENCES})")
        return

    # ??Prefer sentences that can produce Q2 (have target in bank)
    eligible = []
    for q in p5:
        s = _pick_str(q, ["sentence","q","question"], "")
        if not s:
            continue
        t, k = _pick_target(s, bank)
        if t:
            eligible.append(q)

    if len(eligible) < SENTENCES:
        # SAFE: fill remaining from P5 pool (do not Sudden-Death on ammo shortage)
        need = SENTENCES - len(eligible)
        pool = [x for x in p5 if x not in eligible]
        random.shuffle(pool)
        eligible.extend(pool[:need])
        st.warning(f'🛡 Word Bank 매칭 문장이 부족합니다 → {need}개를 일반 문장으로 보충합니다.')
    pack = random.sample(eligible, SENTENCES)

    st.session_state["ex10_pack"] = pack
    st.session_state["ex10_active"] = True
    st.session_state["ex10_done"] = False
    st.session_state["ex10_fail_reason"] = ""
    st.session_state["ex10_start"] = time.time()
    st.session_state["ex10_sent_idx"] = 0
    st.session_state["ex10_subq"] = 1
    st.session_state["ex10_score"] = 0
    st.session_state["ex10_q2"] = {}
    st.session_state["ex10_target"] = ""
    st.session_state["ex10_target_kind"] = "word"
    st.session_state["ex10_sentence_u"] = ""


def render():
    _init()
    remain = max(0, _remain())

    st.markdown(
        f"""
        <div style="display:flex;justify-content:space-between;align-items:center;margin:6px 0 10px 0;">
          <div style="font-weight:950;font-size:34px;color:#f9fafb;">?뵦 P5 EXAM 쨌 10Q / 33s</div>
          <div style="padding:6px 10px;border-radius:999px;background:rgba(0,0,0,.32);
                      border:1px solid rgba(255,255,255,.18);color:#fff;font-weight:950;">
            ??{remain}s
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.get("ex10_done", False):
        score = int(st.session_state.get("ex10_score", 0))
        reason = st.session_state.get("ex10_fail_reason", "")
        if reason:
            st.error("??FAIL (Sudden Death)")
            st.write(reason)
        else:
            st.success("??CLEAR! (Perfect run)")
        st.markdown(f"### Score: {score} / {TOTAL_Q}")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("?봺 Retry", use_container_width=True):
                reset()
        with c2:
            if st.button("?룧 Hub", use_container_width=True):
                try:
                    st.switch_page("main_hub.py")
                except Exception:
                    pass
        st.stop()

    if not st.session_state.get("ex10_active", False):
        st.markdown(
            """
            <div style="background:rgba(20,25,45,.72);border:1px solid rgba(255,255,255,.16);
                        border-radius:16px;padding:14px 16px;box-shadow:0 18px 40px rgba(0,0,0,.22);color:#fff;">
              <div style="font-weight:950;font-size:18px;">?㎤ RULES</div>
              <div style="margin-top:6px;line-height:1.55;">
                ??5 sentences<br>
                ??Each sentence = Q1 (Grammar) ??Q2 (Meaning Check)<br>
                ??Total 10 questions / 33 seconds
              </div>
              <div style="margin-top:10px;font-weight:950;">?좑툘 Sudden Death</div>
              <div style="line-height:1.55;">
                ??Any wrong answer ??FAIL<br>
                ??Time over ??FAIL
              </div>
              <div style="opacity:.8;margin-top:8px;">Q2 is English prompt + Korean choices.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        if st.button("?? Start", use_container_width=True):
            _start_exam()
        st.stop()

    if remain <= 0:
        _fail("Time over (33s)")

    bank = _load_word_bank()
    pack: List[Dict[str, Any]] = st.session_state.get("ex10_pack", [])
    si = int(st.session_state.get("ex10_sent_idx", 0))
    subq = int(st.session_state.get("ex10_subq", 1))

    if si >= SENTENCES:
        if int(st.session_state.get("ex10_score", 0)) == TOTAL_Q:
            _success()
        else:
            _fail("Not perfect (must be 10/10)")

    q = pack[si]
    sentence = _pick_str(q, ["sentence","q","question"], "(No sentence)")
    choices = list(q.get("choices", []) or [])[:4]
    while len(choices) < 4:
        choices.append("")
    answer = _pick_str(q, ["answer","correct","correct_answer","ans"], "")

    # Sentence display:
    # - Q1: plain sentence
    # - Q2: underline target (HTML)
    sentence_u = st.session_state.get("ex10_sentence_u", "") or sentence

    st.markdown(
        f"""
        <div style="background:rgba(255,255,255,.96);border:3px solid rgba(203,213,225,.92);
                    border-radius:18px;padding:14px 16px;box-shadow:0 18px 40px rgba(0,0,0,.18);">
          <div style="font-weight:950;font-size:20px;color:#111827;">Set {si+1}/{SENTENCES} 쨌 Q{subq}</div>
          <div style="margin-top:6px;font-weight:950;font-size:24px;color:#111827;line-height:1.35;">
            {sentence_u}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    labels = ["(A)","(B)","(C)","(D)"]
    grid1 = st.columns(2, gap="large")
    grid2 = st.columns(2, gap="large")
    grid = grid1 + grid2

    if subq == 1:
        for i, opt in enumerate(choices[:4]):
            with grid[i]:
                if st.button(f"{labels[i]} {opt}".strip(), use_container_width=True, key=f"ex10_q1_{si}_{i}"):
                    if opt != answer:
                        _fail(f"Wrong: Set{si+1}-Q1")

                    st.session_state["ex10_score"] = int(st.session_state["ex10_score"]) + 1

                    # build Q2
                    t, k = _pick_target(sentence, bank)
                    if not t:
                        _fail(f"No Word Bank target found for Q2: Set{si+1}")

                    q2 = _make_q2(sentence, t, k, bank)
                    if not q2:
                        _fail(f"Q2 build failed for target '{t}'")

                    # store underline sentence for Q2
                    sent_u = _underline_once(sentence, t, k)

                    st.session_state["ex10_target"] = t
                    st.session_state["ex10_target_kind"] = k
                    st.session_state["ex10_q2"] = q2
                    st.session_state["ex10_sentence_u"] = sent_u
                    st.session_state["ex10_subq"] = 2

    else:
        q2 = st.session_state.get("ex10_q2", {}) or {}
        prompt = str(q2.get("prompt", "")).strip()
        opts = q2.get("choices", [])
        ans2 = str(q2.get("answer", "")).strip()

        st.markdown(
            f"""
            <div style="margin-top:10px;background:rgba(20,25,45,.72);border:1px solid rgba(255,255,255,.16);
                        border-radius:16px;padding:12px 14px;box-shadow:0 14px 30px rgba(0,0,0,.18);color:#fff;">
              <div style="font-weight:950;">Q2. {prompt}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

        if not (isinstance(opts, list) and len(opts) == 4 and ans2):
            _fail("Invalid Q2 data")

        for i, opt in enumerate(opts):
            with grid[i]:
                if st.button(f"{labels[i]} {opt}".strip(), use_container_width=True, key=f"ex10_q2_{si}_{i}"):
                    if opt != ans2:
                        _fail(f"Wrong: Set{si+1}-Q2")

                    st.session_state["ex10_score"] = int(st.session_state["ex10_score"]) + 1
                    st.session_state["ex10_sent_idx"] = si + 1
                    st.session_state["ex10_subq"] = 1
                    st.session_state["ex10_q2"] = {}
                    st.session_state["ex10_target"] = ""
                    st.session_state["ex10_target_kind"] = "word"
                    st.session_state["ex10_sentence_u"] = ""
