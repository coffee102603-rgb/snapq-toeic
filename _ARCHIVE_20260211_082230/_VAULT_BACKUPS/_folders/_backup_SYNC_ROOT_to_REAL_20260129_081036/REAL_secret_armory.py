# ============================================================
# SnapQ TOEIC - Secret Armory (VOCA) v1.0  ✅FINAL (Mobile+P7 link)
#
# TRAIN = "정리실/무기 손질소" (NO timer/NO HP/NO pressure)
#  - P7 saved vocab auto-load from secret_armory.json if v1 storage empty
#  - 1-card learning: WORD / CHUNK / SENTENCE + [뜻 보기][다음][폐기]
#
# BATTLE = "44초 심문실" (44s fixed / 10Q / HP / no meaning / no rollback)
#  - Questions are generated from TRAIN cards (sentence 그대로 + 단어만 ____ )
#  - 4-choice big tap cards (2x2) mobile-first
#  - Timer pressure 3 stages: gray -> orange(shake) -> red(shake+pulse)
#  - Timeout: no answer reveal, no score, streak reset, FORCE back to TRAIN
#
# COMPAT:
# pages/03_Secret_Armory_Main.py expects:
#   from app.arenas.secret_armory import render
#   render()
# ============================================================

from __future__ import annotations

import json
import random
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st


# ------------------------------------------------------------
# Paths
# ------------------------------------------------------------
THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parents[2]  # .../snapq_toeic
DATA_DIR = PROJECT_ROOT / "data"
ARMORY_DIR = DATA_DIR / "armory"
ARMORY_DIR.mkdir(parents=True, exist_ok=True)

# v1 primary storage
WORDS_JSON = ARMORY_DIR / "secret_armory_words.json"
EVENTS_JSONL = ARMORY_DIR / "secret_armory_events.jsonl"


def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass


def _safe_read_json(path: Path) -> Optional[Any]:
    try:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _safe_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


# ------------------------------------------------------------
# Data model
# ------------------------------------------------------------
@dataclass
class VocaCard:
    word: str
    meaning_ko: str = ""
    chunk_en: str = ""
    chunk_ko: str = ""
    sentence_en: str = ""
    sentence_ko: str = ""
    tag: str = "P7"
    added_at: str = ""
    seen: int = 0


def _dedupe(cards: List[VocaCard]) -> List[VocaCard]:
    seen = set()
    out = []
    for c in cards:
        k = c.word.strip().lower()
        if not k or k in seen:
            continue
        seen.add(k)
        out.append(c)
    return out


def _upsert(cards: List[VocaCard], new: VocaCard) -> List[VocaCard]:
    key = new.word.strip().lower()
    if not key:
        return cards
    out = []
    replaced = False
    for c in cards:
        if c.word.strip().lower() == key:
            out.append(new)
            replaced = True
        else:
            out.append(c)
    if not replaced:
        out.insert(0, new)
    return out


def _delete(cards: List[VocaCard], word: str) -> List[VocaCard]:
    key = (word or "").strip().lower()
    return [c for c in cards if c.word.strip().lower() != key]


def save_cards(cards: List[VocaCard]) -> None:
    payload = {
        "schema": "secret_armory_v1",
        "updated_at": _now(),
        "cards": [c.__dict__ for c in cards],
    }
    _safe_write_json(WORDS_JSON, payload)


# ------------------------------------------------------------
# P7 / legacy import
#  - IMPORTANT: Your uploaded secret_armory.json contains P7 vocab rows:
#    {"source":"P7","mode":"p7_vocab","word":...,"meaning":...,"sentence":...}
# ------------------------------------------------------------
def _candidate_secret_armory_json_paths() -> List[Path]:
    # We try multiple likely locations.
    return [
        PROJECT_ROOT / "secret_armory.json",
        DATA_DIR / "secret_armory.json",
        ARMORY_DIR / "secret_armory.json",
        DATA_DIR / "armory" / "secret_armory.json",
    ]


def _extract_chunk(sentence: str, word: str) -> str:
    # super simple TOEIC chunk helper:
    # try "be + past participle" for common words like relocated, informed, etc.
    w = word.strip()
    if not sentence or not w:
        return w
    # if sentence already contains "be <word>" pattern:
    m = re.search(rf"\b(am|is|are|was|were|be|been|being)\s+({re.escape(w)})\b", sentence, flags=re.I)
    if m:
        return f"{m.group(1)} {m.group(2)}"
    return w


def _import_from_secret_armory_json() -> List[VocaCard]:
    for p in _candidate_secret_armory_json_paths():
        raw = _safe_read_json(p)
        if not isinstance(raw, list) or len(raw) == 0:
            continue

        cards: List[VocaCard] = []
        for it in raw:
            if not isinstance(it, dict):
                continue
            if str(it.get("source", "")).upper() != "P7":
                continue
            w = str(it.get("word", "")).strip()
            if not w:
                continue
            meaning = str(it.get("meaning", "")).strip()
            sent = str(it.get("sentence", "")).strip()
            cards.append(
                VocaCard(
                    word=w,
                    meaning_ko=meaning,
                    chunk_en=_extract_chunk(sent, w),
                    chunk_ko="",
                    sentence_en=sent,
                    sentence_ko="",
                    tag="P7",
                    added_at=_now(),
                )
            )

        cards = _dedupe(cards)
        if cards:
            _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "import_secret_armory_json", "from": str(p), "count": len(cards)})
            return cards

    return []


def load_cards() -> List[VocaCard]:
    # 1) primary storage
    raw = _safe_read_json(WORDS_JSON)
    cards: List[VocaCard] = []
    if isinstance(raw, dict) and isinstance(raw.get("cards"), list):
        for it in raw["cards"]:
            if isinstance(it, dict) and it.get("word"):
                cards.append(
                    VocaCard(
                        word=str(it.get("word", "")).strip(),
                        meaning_ko=str(it.get("meaning_ko", "")).strip(),
                        chunk_en=str(it.get("chunk_en", "")).strip(),
                        chunk_ko=str(it.get("chunk_ko", "")).strip(),
                        sentence_en=str(it.get("sentence_en", "")).strip(),
                        sentence_ko=str(it.get("sentence_ko", "")).strip(),
                        tag=str(it.get("tag", "P7")).strip() or "P7",
                        added_at=str(it.get("added_at", "")).strip(),
                        seen=int(it.get("seen", 0) or 0),
                    )
                )

    cards = _dedupe(cards)

    # 2) If empty -> import from secret_armory.json (P7 saved)
    if len(cards) == 0:
        imported = _import_from_secret_armory_json()
        if imported:
            cards = imported
            save_cards(cards)

    return cards


# ------------------------------------------------------------
# CSS (Mobile-first, arcade)
# ------------------------------------------------------------
def inject_css() -> None:
    st.markdown(
        """
<style>
/* ===== Page background (arcade) ===== */
.stApp{
  background:
    radial-gradient(900px 650px at 15% 10%, rgba(34,211,238,0.14), transparent 60%),
    radial-gradient(900px 650px at 75% 10%, rgba(167,139,250,0.12), transparent 62%),
    linear-gradient(180deg, rgba(2,6,23,1) 0%, rgba(2,6,23,1) 100%) !important;
  color: #f5f7ff !important;
}
[data-testid="stMarkdownContainer"], .stMarkdown, .stMarkdown p, label { color:#f5f7ff !important; }

.snap-wrap{ max-width: 980px; margin: 0 auto; padding-bottom: 18px; }
.hero{
  border-radius: 18px;
  padding: 14px 16px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.06);
  box-shadow: 0 10px 26px rgba(0,0,0,0.22);
  backdrop-filter: blur(10px);
}
.h1{ font-size: 30px; font-weight: 950; letter-spacing: -0.6px; margin:0; }
.h2{ margin: 4px 0 0 0; opacity: 0.90; font-weight: 800; font-size: 13px; }

.badge{
  display:inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.16);
  background: rgba(0,0,0,0.22);
  font-size: 12px;
  font-weight: 900;
}

.card{
  border-radius: 18px;
  padding: 16px 16px;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.08);
  box-shadow: 0 14px 34px rgba(0,0,0,0.22);
  backdrop-filter: blur(10px);
}
.k-label{ font-size: 12px; opacity: 0.85; font-weight: 900; letter-spacing: 0.2px; }
.k-word{ font-size: 28px; font-weight: 950; margin: 2px 0 10px 0; }
.k-chunk{ font-size: 16px; font-weight: 900; margin: 2px 0 10px 0; }
.k-sent{ font-size: 16px; font-weight: 850; line-height: 1.5; }
.k-ko{ font-size: 14px; opacity: 0.95; font-weight: 800; margin-top: 6px; }

.bigbtn div[data-testid="stButton"] > button{
  width:100% !important;
  min-height: 56px !important;
  border-radius: 18px !important;
  font-weight: 950 !important;
  font-size: 16px !important;
  padding: 14px 16px !important;
  border: 1px solid rgba(255,255,255,0.18) !important;
  background: rgba(255,255,255,0.92) !important;
  color: #0F172A !important;
  box-shadow: 0 10px 28px rgba(0,0,0,0.22) !important;
}
.bigbtn div[data-testid="stButton"] > button:hover{
  transform: translateY(-1px);
  background: linear-gradient(135deg, #22D3EE, #A78BFA) !important;
  color:#ffffff !important;
}
.bigbtn div[data-testid="stButton"] > button:hover *{ color:#ffffff !important; }

@media (max-width: 640px){
  .block-container{ padding-left:0.75rem !important; padding-right:0.75rem !important; padding-top:0.25rem !important; }
  .h1{ font-size: 28px; }
  .k-word{ font-size: 30px; }
  .bigbtn div[data-testid="stButton"] > button{ min-height: 62px !important; font-size: 16px !important; }
}

/* ===== BATTLE HUD + pressure ===== */
.hud{
  position: sticky; top: 10px;
  border-radius: 18px;
  padding: 12px 12px;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(10,12,16,0.62);
  box-shadow: 0 14px 34px rgba(0,0,0,0.30);
  backdrop-filter: blur(10px);
}
.hudT{ font-weight: 950; margin: 0 0 8px 0; }
.kpi{ font-size: 26px; font-weight: 950; margin: 0; }
.sub{ font-size: 12px; opacity: 0.86; font-weight: 800; margin-top: 2px; }

.tbar{ height: 10px; width: 100%; border-radius: 999px; border:1px solid rgba(255,255,255,0.16); background: rgba(255,255,255,0.08); overflow:hidden; }
.tfill{ height:100%; width:50%; background: rgba(200,200,200,0.80); }
.t-gray .tfill{ background: rgba(200,200,200,0.78); }
.t-orange .tfill{ background: rgba(255,170,60,0.86); }
.t-red .tfill{ background: rgba(255,70,70,0.90); }

@keyframes shake { 0%{transform:translateX(0)} 20%{transform:translateX(-2px)} 40%{transform:translateX(2px)} 60%{transform:translateX(-2px)} 80%{transform:translateX(2px)} 100%{transform:translateX(0)} }
@keyframes pulse { 0%{opacity:1} 50%{opacity:0.55} 100%{opacity:1} }
.shake{ animation: shake 0.25s linear infinite; }
.pulse{ animation: pulse 0.8s ease-in-out infinite; }

/* choice cards (2x2) */
.choice div[data-testid="stButton"] > button{
  width:100% !important;
  min-height: 74px !important;
  border-radius: 18px !important;
  font-weight: 950 !important;
  font-size: 17px !important;
  padding: 18px 16px !important;
  white-space: normal !important;
  line-height: 1.2 !important;
  background: rgba(255,255,255,0.98) !important;
  color:#111111 !important;
  border: 1px solid rgba(0,0,0,0.10) !important;
  box-shadow: 0 10px 28px rgba(0,0,0,0.20) !important;
}
.choice div[data-testid="stButton"] > button:hover{
  background: linear-gradient(135deg, #22D3EE, #4DA3FF) !important;
  color:#ffffff !important;
}
.choice div[data-testid="stButton"] > button:hover *{ color:#ffffff !important; }
@media (max-width: 640px){
  .choice div[data-testid="stButton"] > button{ min-height: 84px !important; }
}
</style>
""",
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# Session State
# ------------------------------------------------------------
def ensure_state() -> None:
    st.session_state.setdefault("voca_mode", "TRAIN")

    # TRAIN
    st.session_state.setdefault("train_idx", 0)
    st.session_state.setdefault("train_reveal", False)
    st.session_state.setdefault("train_force_queue", [])  # forced back from battle
    st.session_state.setdefault("train_search", "")
    st.session_state.setdefault("train_tag", "ALL")

    # BATTLE
    st.session_state.setdefault("battle_running", False)
    st.session_state.setdefault("battle_started_at", None)
    st.session_state.setdefault("battle_limit_sec", 44)
    st.session_state.setdefault("battle_hp", 3)
    st.session_state.setdefault("battle_q_index", 0)
    st.session_state.setdefault("battle_questions", [])
    st.session_state.setdefault("battle_locked", False)
    st.session_state.setdefault("battle_streak", 0)
    st.session_state.setdefault("battle_last_fail_reason", "")


# ------------------------------------------------------------
# TRAIN
# ------------------------------------------------------------
def _train_deck(cards: List[VocaCard]) -> List[VocaCard]:
    force_words = st.session_state.get("train_force_queue", []) or []
    if not force_words:
        return cards

    forced, rest = [], []
    fset = {w.strip().lower() for w in force_words if w.strip()}
    for c in cards:
        if c.word.strip().lower() in fset:
            forced.append(c)
        else:
            rest.append(c)
    forced.sort(key=lambda x: force_words.index(x.word) if x.word in force_words else 999999)
    return forced + rest


def _apply_train_filters(cards: List[VocaCard]) -> List[VocaCard]:
    q = (st.session_state.get("train_search", "") or "").strip().lower()
    tag = st.session_state.get("train_tag", "ALL")

    out = []
    for c in cards:
        if tag != "ALL" and (c.tag or "").strip() != tag:
            continue
        if not q:
            out.append(c)
            continue
        hay = " ".join([c.word, c.meaning_ko, c.chunk_en, c.sentence_en, c.tag]).lower()
        if q in hay:
            out.append(c)
    return out


def _train_next(max_len: int) -> None:
    st.session_state["train_reveal"] = False
    if max_len <= 0:
        st.session_state["train_idx"] = 0
        return
    st.session_state["train_idx"] = (int(st.session_state.get("train_idx", 0)) + 1) % max_len


def _train_current(cards: List[VocaCard]) -> Optional[VocaCard]:
    if not cards:
        return None
    idx = int(st.session_state.get("train_idx", 0))
    idx = max(0, min(idx, len(cards) - 1))
    st.session_state["train_idx"] = idx
    return cards[idx]


def _train_remove_forced(word: str) -> None:
    q = st.session_state.get("train_force_queue", []) or []
    if not q:
        return
    st.session_state["train_force_queue"] = [w for w in q if w.strip().lower() != (word or "").strip().lower()]


def render_train(cards_all: List[VocaCard]) -> None:
    st.markdown('<div class="snap-wrap">', unsafe_allow_html=True)

    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.markdown('<p class="h1">🟩 VOCA TRAIN</p>', unsafe_allow_html=True)
    st.markdown('<p class="h2">정리실 / 무기 손질소 · 타이머 없음 · 압박 없음</p>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    tags = ["ALL"] + sorted({c.tag for c in cards_all if (c.tag or "").strip()})
    c1, c2 = st.columns([2.0, 1.0])
    with c1:
        st.session_state["train_search"] = st.text_input(
            "🔎 검색 (단어/청크/문장/태그)",
            value=st.session_state.get("train_search", ""),
            key="train_search_in",
        )
    with c2:
        cur = st.session_state.get("train_tag", "ALL")
        idx = tags.index(cur) if cur in tags else 0
        st.session_state["train_tag"] = st.selectbox("🏷️ 태그", options=tags, index=idx, key="train_tag_in")

    deck = _apply_train_filters(_train_deck(cards_all))

    st.markdown(
        f'<span class="badge">총 무기: {len(cards_all)}</span> &nbsp; <span class="badge">표시 중: {len(deck)}</span>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    if len(deck) == 0:
        st.warning("표시할 무기가 없습니다. (P7 저장 단어가 있다면 secret_armory.json을 확인해주세요)")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    cur_card = _train_current(deck)
    assert cur_card is not None

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="k-label">WORD</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="k-word">{cur_card.word}</div>', unsafe_allow_html=True)

    st.markdown('<div class="k-label">CHUNK (TOEIC 핵심)</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="k-chunk">{cur_card.chunk_en or "(chunk 없음)"}</div>', unsafe_allow_html=True)

    st.markdown('<div class="k-label">SENTENCE (실전 예문)</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="k-sent">{cur_card.sentence_en or "(sentence 없음)"}</div>', unsafe_allow_html=True)

    if st.session_state.get("train_reveal", False):
        if cur_card.meaning_ko:
            st.markdown(f'<div class="k-ko">뜻: {cur_card.meaning_ko}</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # 3 buttons (big tap)
    b1, b2, b3 = st.columns(3)
    with b1:
        st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
        if st.button("뜻 보기", use_container_width=True, key=f"train_reveal_{cur_card.word}"):
            st.session_state["train_reveal"] = not bool(st.session_state.get("train_reveal", False))
            cur_card.seen += 1
            cur_card.added_at = cur_card.added_at or _now()
            cards_all2 = _upsert(cards_all, cur_card)
            save_cards(cards_all2)
            _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "train_reveal", "word": cur_card.word})
            _train_remove_forced(cur_card.word)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with b2:
        st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
        if st.button("다음", use_container_width=True, key=f"train_next_{cur_card.word}"):
            _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "train_next", "word": cur_card.word})
            _train_remove_forced(cur_card.word)
            _train_next(len(deck))
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with b3:
        st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
        if st.button("폐기", use_container_width=True, key=f"train_discard_{cur_card.word}"):
            updated = _delete(cards_all, cur_card.word)
            save_cards(updated)
            _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "train_discard", "word": cur_card.word})
            st.toast("폐기 완료", icon="🧹")
            st.session_state["train_idx"] = max(0, min(st.session_state.get("train_idx", 0), max(0, len(updated) - 1)))
            _train_remove_forced(cur_card.word)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------------------
# BATTLE
# ------------------------------------------------------------
def _battle_left_sec() -> int:
    if not st.session_state.get("battle_running"):
        return 44
    started = st.session_state.get("battle_started_at")
    if not started:
        return 44
    elapsed = int(time.time() - float(started))
    return max(0, 44 - elapsed)


def _timer_stage(left_sec: int) -> str:
    if left_sec >= 25:
        return "gray"
    if left_sec >= 11:
        return "orange"
    return "red"


def _make_question_set(cards: List[VocaCard], n: int = 10) -> List[Dict[str, Any]]:
    pool = [c for c in cards if c.word.strip() and c.sentence_en.strip()]
    if not pool:
        return []

    picked = random.sample(pool, k=min(n, len(pool)))
    all_words = [c.word for c in pool]

    out: List[Dict[str, Any]] = []
    for c in picked:
        ans = c.word
        distract_pool = [w for w in all_words if w != ans]
        distract = random.sample(distract_pool, k=min(3, len(distract_pool)))
        choices = distract + [ans]
        random.shuffle(choices)

        sent = c.sentence_en
        blank = "____"
        # safer: replace the first word boundary match (case-insensitive)
        sent2, cnt = re.subn(rf"\b{re.escape(ans)}\b", blank, sent, count=1, flags=re.I)
        if cnt == 0:
            sent2 = sent.replace(ans, blank, 1)

        out.append({"answer": ans, "sentence": sent2, "choices": choices, "source_word": ans})
    return out


def _current_force_words() -> List[str]:
    qs = st.session_state.get("battle_questions", []) or []
    q_idx = int(st.session_state.get("battle_q_index", 0))
    if 0 <= q_idx < len(qs):
        w = qs[q_idx].get("source_word") or qs[q_idx].get("answer")
        return [w] if w else []
    return []


def _battle_fail(reason: str) -> None:
    st.session_state["battle_running"] = False
    st.session_state["battle_started_at"] = None
    st.session_state["battle_questions"] = []
    st.session_state["battle_q_index"] = 0
    st.session_state["battle_locked"] = False
    st.session_state["battle_streak"] = 0
    st.session_state["battle_last_fail_reason"] = reason

    # FORCE back to TRAIN
    force_words = _current_force_words()
    prev = st.session_state.get("train_force_queue", []) or []
    merged = []
    seen = set()
    for w in force_words + prev:
        k = (w or "").strip().lower()
        if not k or k in seen:
            continue
        seen.add(k)
        merged.append(w)
    st.session_state["train_force_queue"] = merged
    st.session_state["voca_mode"] = "TRAIN"

    _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "battle_fail", "reason": reason, "force_words": force_words})


def render_battle(cards_all: List[VocaCard]) -> None:
    st.markdown('<div class="snap-wrap">', unsafe_allow_html=True)

    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.markdown('<p class="h1">🔥 VOCA BATTLE</p>', unsafe_allow_html=True)
    st.markdown('<p class="h2">44초 심문실 · 10문제 · HP · 뜻보기 없음 · 되돌리기 없음</p>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    pool_ok = len([c for c in cards_all if c.word.strip() and c.sentence_en.strip()]) >= 1
    if not pool_ok:
        st.error("BATTLE 재료가 없습니다. (예문 sentence가 있는 카드가 최소 1개 필요)")
        st.info("P7 저장 단어가 secret_armory.json에 있다면 자동으로 불러와야 합니다.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    left, right = st.columns([2.15, 1.0], gap="large")

    with right:
        left_sec = _battle_left_sec()
        stage = _timer_stage(left_sec)

        pct = int((left_sec / 44) * 100) if 44 > 0 else 0
        pct = max(0, min(100, pct))

        tcls = "t-gray" if stage == "gray" else ("t-orange shake" if stage == "orange" else "t-red shake")
        numcls = "" if stage != "red" else "pulse"

        st.markdown('<div class="hud">', unsafe_allow_html=True)
        st.markdown('<div class="hudT">🎛️ BATTLE HUD</div>', unsafe_allow_html=True)

        q_idx = int(st.session_state.get("battle_q_index", 0))
        hp = int(st.session_state.get("battle_hp", 3))
        st.markdown(f'<div class="sub">Mission</div><p class="kpi">{min(q_idx+1,10)} / 10</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="sub">HP</div><p class="kpi">❤️ {hp}</p>', unsafe_allow_html=True)

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='sub'>남은 시간</div><p class='kpi {numcls}'>{left_sec}s</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='tbar {tcls}'><div class='tfill' style='width:{pct}%;'></div></div>", unsafe_allow_html=True)
        st.markdown("<hr style='opacity:0.18;'>", unsafe_allow_html=True)

        if not st.session_state.get("battle_running"):
            st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
            if st.button("▶ BATTLE START", use_container_width=True):
                st.session_state["battle_running"] = True
                st.session_state["battle_started_at"] = time.time()
                st.session_state["battle_hp"] = 3
                st.session_state["battle_q_index"] = 0
                st.session_state["battle_locked"] = False
                st.session_state["battle_questions"] = _make_question_set(cards_all, n=10)
                st.session_state["battle_last_fail_reason"] = ""
                _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "battle_start", "limit_sec": 44})
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
            if st.button("⏹ STOP (포기)", use_container_width=True):
                _battle_fail("stop")
                st.toast("전장 종료 → TRAIN 귀환", icon="🟩")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
        if st.button("🔁 RESET", use_container_width=True):
            st.session_state["battle_running"] = False
            st.session_state["battle_started_at"] = None
            st.session_state["battle_questions"] = []
            st.session_state["battle_q_index"] = 0
            st.session_state["battle_locked"] = False
            st.session_state["battle_hp"] = 3
            st.session_state["battle_last_fail_reason"] = ""
            _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "battle_reset"})
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.get("battle_last_fail_reason"):
            st.markdown("<hr style='opacity:0.18;'>", unsafe_allow_html=True)
            st.error("🧨 실패: “아… 이거 TRAIN에서 봤던 건데…”")
            st.caption(f"사유: {st.session_state.get('battle_last_fail_reason')}")

        st.markdown("</div>", unsafe_allow_html=True)

    with left:
        # timeout check
        if st.session_state.get("battle_running") and _battle_left_sec() <= 0:
            # timeout: NO answer reveal / NO score
            _battle_fail("timeout")
            st.rerun()

        if not st.session_state.get("battle_running"):
            st.info("▶ START를 누르면 44초 심문실 시작. (뜻보기 없음)")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        questions: List[Dict[str, Any]] = st.session_state.get("battle_questions", []) or []
        if not questions:
            _battle_fail("no_questions")
            st.rerun()

        q_idx = int(st.session_state.get("battle_q_index", 0))
        hp = int(st.session_state.get("battle_hp", 3))

        if hp <= 0:
            _battle_fail("hp_zero")
            st.rerun()

        if q_idx >= len(questions):
            # clear
            st.session_state["battle_running"] = False
            st.session_state["battle_started_at"] = None
            st.session_state["battle_locked"] = False
            st.session_state["battle_streak"] = int(st.session_state.get("battle_streak", 0)) + 1
            _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "battle_clear", "streak": st.session_state["battle_streak"]})

            st.success("🏁 CLEAR! 다음 심문실 준비 완료.")
            st.markdown(f"<span class='badge'>현재 스트릭: {st.session_state['battle_streak']}</span>", unsafe_allow_html=True)
            st.markdown("")
            st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
            if st.button("다시 BATTLE (새 44초)", use_container_width=True):
                st.session_state["battle_running"] = True
                st.session_state["battle_started_at"] = time.time()
                st.session_state["battle_hp"] = 3
                st.session_state["battle_q_index"] = 0
                st.session_state["battle_locked"] = False
                st.session_state["battle_questions"] = _make_question_set(cards_all, n=10)
                st.session_state["battle_last_fail_reason"] = ""
                _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "battle_restart"})
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            return

        q = questions[q_idx]
        left_sec = _battle_left_sec()

        st.markdown(
            f"<span class='badge'>Mission {q_idx+1} / 10</span> &nbsp; <span class='badge'>⏱ {left_sec}s</span>",
            unsafe_allow_html=True,
        )
        st.markdown("")

        stage = _timer_stage(left_sec)
        shaky = "shake" if stage in ("orange", "red") else ""
        pulse = "pulse" if stage == "red" else ""

        st.markdown(f"<div class='card {shaky}'>", unsafe_allow_html=True)
        st.markdown(f"<div class='k-sent {pulse}'>{q.get('sentence','')}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("")

        choices: List[str] = q.get("choices", []) or []
        if len(choices) < 4:
            _battle_fail("bad_choices")
            st.rerun()

        # 2x2 choice cards
        c1, c2 = st.columns(2)
        cols = [c1, c2, c1, c2]
        for i, choice in enumerate(choices[:4]):
            with cols[i]:
                st.markdown('<div class="choice">', unsafe_allow_html=True)
                if st.button(choice, use_container_width=True, key=f"battle_{q_idx}_{i}"):
                    if st.session_state.get("battle_locked"):
                        st.stop()
                    st.session_state["battle_locked"] = True

                    ans = q.get("answer")
                    if choice == ans:
                        _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "battle_correct", "q": q_idx+1, "word": ans})
                        st.session_state["battle_q_index"] = q_idx + 1
                        st.session_state["battle_locked"] = False
                        st.rerun()
                    else:
                        st.session_state["battle_hp"] = int(st.session_state.get("battle_hp", 3)) - 1
                        _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "battle_wrong", "q": q_idx+1, "picked": choice, "answer": ans})

                        if int(st.session_state.get("battle_hp", 0)) <= 0:
                            _battle_fail("hp_zero")
                            st.rerun()

                        st.toast("MISS ❌", icon="❌")
                        st.session_state["battle_locked"] = False
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def app() -> None:
    inject_css()
    ensure_state()

    cards_all = load_cards()

    mode = st.radio(
        "모드 선택",
        options=["TRAIN", "BATTLE"],
        index=0 if st.session_state.get("voca_mode", "TRAIN") == "TRAIN" else 1,
        horizontal=True,
        key="voca_mode_radio",
    )
    st.session_state["voca_mode"] = mode

    if mode == "TRAIN":
        render_train(cards_all)
    else:
        render_battle(cards_all)


def render() -> None:
    # wrapper compatibility
    app()


if __name__ == "__main__":
    st.set_page_config(page_title="SnapQ - Secret Armory v1.0", layout="wide")
    render()
