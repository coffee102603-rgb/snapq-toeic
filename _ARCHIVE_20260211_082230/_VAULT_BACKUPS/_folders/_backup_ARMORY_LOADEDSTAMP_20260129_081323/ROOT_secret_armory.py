# ============================================================
# SnapQ TOEIC - Secret Armory (VOCA) v1.0
#
# ✅ VOCA TRAIN  : "정리실 / 무기 손질소"  (타이머/HP/콤보/압박 없음)
# ✅ VOCA BATTLE : "44초 심문실" (44s 고정 / 10문제 / HP / 뜻보기없음 / 되돌리기없음)
#
# UX 핵심
# - TRAIN: 카드 1장(WORD/CHUNK/SENTENCE) + [뜻 보기] [다음] [폐기]
# - BATTLE: 4지선다(P5 스타일) / 문장 그대로 + 주인공 단어만 빈칸
# - 타이머 연출 3단계: 회색(44~25) → 주황(24~11) → 빨강(10~0)+진동+깜빡
# - 실패(시간초과): 정답공개X/점수X/스트릭리셋/단어 TRAIN 강제귀환
#
# COMPAT:
# pages/03_Secret_Armory_Main.py expects:
#   from app.arenas.secret_armory import render
#   render()
# ============================================================

from __future__ import annotations

import json
import random
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st


# ------------------------------------------------------------
# Project paths + storage
# ------------------------------------------------------------
THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parents[2]  # .../snapq_toeic
DATA_DIR = PROJECT_ROOT / "data"
ARMORY_DIR = DATA_DIR / "armory"
ARMORY_DIR.mkdir(parents=True, exist_ok=True)

# Primary storage (v1.0)
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
        # Logging failure must never break gameplay
        pass


# ------------------------------------------------------------
# Legacy auto-detect (to avoid "총 무기: 0" shock)
# - If v1.0 file is empty, we try to auto-load a likely legacy file
#   under data/ that contains "armory/weapon/vocab/saved/secret".
# ------------------------------------------------------------
def _find_legacy_candidates() -> List[Path]:
    if not DATA_DIR.exists():
        return []

    needles = ("armory", "weapon", "voca", "vocab", "saved", "secret")
    exts = (".json", ".jsonl")
    out: List[Path] = []
    try:
        for p in DATA_DIR.rglob("*"):
            if not p.is_file():
                continue
            if p.suffix.lower() not in exts:
                continue
            low = str(p).lower()
            if any(n in low for n in needles):
                out.append(p)
    except Exception:
        return []

    # newest first
    try:
        out.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    except Exception:
        pass
    return out


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
# Data model (v1.0)
# ------------------------------------------------------------
@dataclass
class VocaCard:
    word: str
    meaning_ko: str = ""
    chunk_en: str = ""
    chunk_ko: str = ""
    sentence_en: str = ""
    sentence_ko: str = ""
    tag: str = ""
    added_at: str = ""
    seen: int = 0
    discard: int = 0  # discard count (optional)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "VocaCard":
        # Backward-compat mappings:
        # - example -> sentence_en
        # - note -> sentence_ko (or chunk_ko if sentence_ko empty)
        return VocaCard(
            word=str(d.get("word", "")).strip(),
            meaning_ko=str(d.get("meaning_ko", d.get("meaning", ""))).strip(),
            chunk_en=str(d.get("chunk_en", d.get("chunk", ""))).strip(),
            chunk_ko=str(d.get("chunk_ko", "")).strip(),
            sentence_en=str(d.get("sentence_en", d.get("example", ""))).strip(),
            sentence_ko=str(d.get("sentence_ko", "") or d.get("note", "")).strip(),
            tag=str(d.get("tag", "")).strip(),
            added_at=str(d.get("added_at", "")).strip(),
            seen=int(d.get("seen", d.get("seen_count", 0)) or 0),
            discard=int(d.get("discard", 0) or 0),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "word": self.word,
            "meaning_ko": self.meaning_ko,
            "chunk_en": self.chunk_en,
            "chunk_ko": self.chunk_ko,
            "sentence_en": self.sentence_en,
            "sentence_ko": self.sentence_ko,
            "tag": self.tag,
            "added_at": self.added_at,
            "seen": self.seen,
            "discard": self.discard,
        }


def load_cards() -> List[VocaCard]:
    # 1) primary v1.0 file
    raw = _safe_read_json(WORDS_JSON)
    cards: List[VocaCard] = []

    if isinstance(raw, dict) and isinstance(raw.get("cards"), list):
        for it in raw["cards"]:
            if isinstance(it, dict):
                c = VocaCard.from_dict(it)
                if c.word:
                    cards.append(c)

    # 2) if empty, try legacy auto-detect once
    if len(cards) == 0:
        for cand in _find_legacy_candidates():
            # skip self
            if cand.resolve() == WORDS_JSON.resolve():
                continue

            legacy = _safe_read_json(cand)
            picked: List[VocaCard] = []

            # legacy pattern A: {"words":[...]} or {"cards":[...]}
            if isinstance(legacy, dict):
                if isinstance(legacy.get("words"), list):
                    for it in legacy["words"]:
                        if isinstance(it, dict):
                            c = VocaCard.from_dict(it)
                            if c.word:
                                picked.append(c)
                elif isinstance(legacy.get("cards"), list):
                    for it in legacy["cards"]:
                        if isinstance(it, dict):
                            c = VocaCard.from_dict(it)
                            if c.word:
                                picked.append(c)

            # legacy pattern B: jsonl lines with {"word":...}
            if len(picked) == 0 and cand.suffix.lower() == ".jsonl":
                try:
                    for line in cand.read_text(encoding="utf-8").splitlines():
                        line = line.strip()
                        if not line:
                            continue
                        obj = json.loads(line)
                        if isinstance(obj, dict) and obj.get("word"):
                            c = VocaCard.from_dict(obj)
                            if c.word:
                                picked.append(c)
                except Exception:
                    picked = []

            if len(picked) > 0:
                cards = _dedupe_cards(picked)
                # persist into v1.0 primary so next load is stable
                save_cards(cards)
                _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "legacy_import", "from": str(cand), "count": len(cards)})
                break

    return _dedupe_cards(cards)


def save_cards(cards: List[VocaCard]) -> None:
    payload = {
        "schema": "secret_armory_v1",
        "updated_at": _now(),
        "cards": [c.to_dict() for c in cards],
    }
    _safe_write_json(WORDS_JSON, payload)


def _dedupe_cards(cards: List[VocaCard]) -> List[VocaCard]:
    seen = set()
    out: List[VocaCard] = []
    for c in cards:
        k = c.word.strip().lower()
        if not k or k in seen:
            continue
        seen.add(k)
        out.append(c)
    return out


def _delete_card(cards: List[VocaCard], word: str) -> List[VocaCard]:
    key = (word or "").strip().lower()
    return [c for c in cards if c.word.strip().lower() != key]


# ------------------------------------------------------------
# UI / CSS
# ------------------------------------------------------------
def _inject_css() -> None:
    st.markdown(
        """
<style>
/* --- base --- */
.snapq-wrap { max-width: 1100px; margin: 0 auto; padding-bottom: 18px; }
.hero {
  border-radius: 18px;
  padding: 14px 16px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.05);
  box-shadow: 0 8px 24px rgba(0,0,0,0.25);
}
.h-title { font-size: 34px; font-weight: 950; letter-spacing: -0.8px; margin: 0; }
.h-sub { margin: 3px 0 0 0; opacity: 0.9; font-weight: 700; }

.badge {
  display:inline-block;
  padding: 5px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.18);
  background: rgba(0,0,0,0.18);
  font-size: 12px;
  font-weight: 900;
}

/* --- TRAIN (calm) --- */
.train-hero {
  border: 1px solid rgba(180,130,255,0.30);
  background: linear-gradient(135deg, rgba(180,130,255,0.18), rgba(0,0,0,0.00));
}
.card {
  border-radius: 18px;
  padding: 16px 18px;
  border: 1px solid rgba(255,255,255,0.12);
  background: rgba(255,255,255,0.06);
  box-shadow: 0 10px 30px rgba(0,0,0,0.22);
}
.k-label { font-size: 12px; opacity: 0.82; font-weight: 900; letter-spacing: 0.2px; }
.k-main  { font-size: 26px; font-weight: 950; margin: 2px 0 10px 0; }
.k-mid   { font-size: 16px; font-weight: 850; margin: 2px 0 10px 0; }
.k-sent  { font-size: 16px; font-weight: 800; line-height: 1.35; }
.k-ko    { font-size: 14px; opacity: 0.92; font-weight: 750; margin-top: 6px; }

/* TRAIN buttons */
.stButton>button { font-weight: 900; border-radius: 14px; }

/* --- BATTLE (pressure) --- */
.battle-hero {
  border: 1px solid rgba(120,210,255,0.30);
  background: linear-gradient(135deg, rgba(120,210,255,0.20), rgba(0,0,0,0.00));
}
.hud {
  position: sticky; top: 12px;
  border-radius: 18px;
  padding: 12px 12px;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(10,12,16,0.60);
  box-shadow: 0 10px 28px rgba(0,0,0,0.30);
}
.hud-title { font-weight: 950; margin: 0 0 8px 0; }
.hud-kpi { font-size: 26px; font-weight: 950; margin: 0; }
.hud-sub { opacity: 0.86; font-size: 12px; font-weight: 800; margin-top: 2px; }

/* timer bar */
.tbar {
  height: 10px;
  width: 100%;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.18);
  background: rgba(255,255,255,0.08);
  overflow: hidden;
}
.tfill { height: 100%; width: 50%; background: rgba(200,200,200,0.75); }

.t-gray  .tfill { background: rgba(200,200,200,0.75); }
.t-orange .tfill { background: rgba(255,170,60,0.85); }
.t-red   .tfill { background: rgba(255,70,70,0.88); }

@keyframes shake {
  0% { transform: translateX(0); }
  20% { transform: translateX(-2px); }
  40% { transform: translateX(2px); }
  60% { transform: translateX(-2px); }
  80% { transform: translateX(2px); }
  100% { transform: translateX(0); }
}
.shake { animation: shake 0.25s linear infinite; }

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.55; }
  100% { opacity: 1; }
}
.pulse { animation: pulse 0.8s ease-in-out infinite; }

.choice-grid .stButton>button{
  padding: 14px 12px !important;
  font-size: 16px !important;
  border-radius: 16px !important;
  white-space: normal !important;
  line-height: 1.15 !important;
}
</style>
""",
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# State
# ------------------------------------------------------------
def _ensure_state() -> None:
    # mode
    st.session_state.setdefault("voca_mode", "TRAIN")  # TRAIN/BATTLE

    # TRAIN state
    st.session_state.setdefault("train_idx", 0)
    st.session_state.setdefault("train_reveal", False)
    st.session_state.setdefault("train_force_queue", [])  # words forced back from battle
    st.session_state.setdefault("train_search", "")
    st.session_state.setdefault("train_tag", "ALL")

    # BATTLE state
    st.session_state.setdefault("battle_running", False)
    st.session_state.setdefault("battle_started_at", None)
    st.session_state.setdefault("battle_limit_sec", 44)  # fixed by design
    st.session_state.setdefault("battle_hp", 3)  # default
    st.session_state.setdefault("battle_q_index", 0)
    st.session_state.setdefault("battle_questions", [])  # list[dict]
    st.session_state.setdefault("battle_locked", False)  # prevent multi-click spam
    st.session_state.setdefault("battle_streak", 0)
    st.session_state.setdefault("battle_last_fail_reason", "")


def _set_mode(mode: str) -> None:
    st.session_state["voca_mode"] = mode


# ------------------------------------------------------------
# TRAIN logic (calm, 1-card)
# ------------------------------------------------------------
def _train_deck(cards: List[VocaCard]) -> List[VocaCard]:
    # If there are forced words from battle, put them first.
    force_words: List[str] = st.session_state.get("train_force_queue", []) or []
    if len(force_words) == 0:
        return cards

    forced = []
    rest = []
    fset = {w.strip().lower() for w in force_words if w.strip()}
    for c in cards:
        if c.word.strip().lower() in fset:
            forced.append(c)
        else:
            rest.append(c)
    # keep forced order as queue order
    forced.sort(key=lambda x: force_words.index(x.word) if x.word in force_words else 999999)
    return forced + rest


def _apply_train_filters(cards: List[VocaCard]) -> List[VocaCard]:
    q = (st.session_state.get("train_search", "") or "").strip().lower()
    tag = st.session_state.get("train_tag", "ALL")

    out: List[VocaCard] = []
    for c in cards:
        if tag != "ALL" and (c.tag or "").strip() != tag:
            continue
        if not q:
            out.append(c)
            continue
        hay = " ".join([c.word, c.meaning_ko, c.chunk_en, c.chunk_ko, c.sentence_en, c.sentence_ko, c.tag]).lower()
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


def _train_remove_forced_if_match(word: str) -> None:
    q = st.session_state.get("train_force_queue", []) or []
    if not q:
        return
    st.session_state["train_force_queue"] = [w for w in q if w.strip().lower() != (word or "").strip().lower()]


def render_train(cards_all: List[VocaCard]) -> None:
    st.markdown('<div class="snapq-wrap">', unsafe_allow_html=True)

    st.markdown('<div class="hero train-hero">', unsafe_allow_html=True)
    st.markdown('<div class="h-title">🟩 VOCA TRAIN</div>', unsafe_allow_html=True)
    st.markdown('<div class="h-sub">정리실 / 무기 손질소 · 타이머 없음 · 압박 없음</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # filters (calm)
    tags = ["ALL"] + sorted({c.tag for c in cards_all if c.tag.strip()})
    c1, c2 = st.columns([2.0, 1.0])
    with c1:
        st.session_state["train_search"] = st.text_input("🔎 검색 (단어/뜻/청크/문장/태그)", value=st.session_state.get("train_search", ""), key="train_search_in")
    with c2:
        cur = st.session_state.get("train_tag", "ALL")
        idx = tags.index(cur) if cur in tags else 0
        st.session_state["train_tag"] = st.selectbox("🏷️ 태그", options=tags, index=idx, key="train_tag_in")

    deck = _train_deck(cards_all)
    deck = _apply_train_filters(deck)

    st.markdown(
        f'<span class="badge">총 무기: {len(cards_all)}</span> &nbsp; <span class="badge">표시 중: {len(deck)}</span>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    # empty state
    if len(deck) == 0:
        st.info("표시할 무기가 없습니다. 검색/태그를 바꾸거나, 아래에서 신규 무기를 등록해보세요.")
        with st.expander("➕ 신규 무기 등록 (v1.0 카드)", expanded=True):
            _render_add_form(cards_all)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    current = _train_current(deck)
    assert current is not None

    # main card
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.markdown('<div class="k-label">WORD</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="k-main">{current.word}</div>', unsafe_allow_html=True)

    st.markdown('<div class="k-label">CHUNK (TOEIC 핵심)</div>', unsafe_allow_html=True)
    if current.chunk_en.strip():
        st.markdown(f'<div class="k-mid">{current.chunk_en}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="k-mid" style="opacity:0.55;">(chunk 없음)</div>', unsafe_allow_html=True)

    st.markdown('<div class="k-label">SENTENCE (실전 예문)</div>', unsafe_allow_html=True)
    if current.sentence_en.strip():
        st.markdown(f'<div class="k-sent">{current.sentence_en}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="k-sent" style="opacity:0.55;">(sentence 없음)</div>', unsafe_allow_html=True)

    # reveal area (only when clicked)
    if st.session_state.get("train_reveal", False):
        if current.meaning_ko.strip():
            st.markdown(f'<div class="k-ko">뜻: {current.meaning_ko}</div>', unsafe_allow_html=True)
        if current.chunk_ko.strip():
            st.markdown(f'<div class="k-ko">청크 해석: {current.chunk_ko}</div>', unsafe_allow_html=True)
        if current.sentence_ko.strip():
            st.markdown(f'<div class="k-ko">문장 해석: {current.sentence_ko}</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # controls: [뜻 보기] [다음] [폐기]
    b1, b2, b3 = st.columns([1.0, 1.0, 1.0])
    with b1:
        if st.button("뜻 보기", use_container_width=True, key=f"train_reveal_btn_{current.word}"):
            st.session_state["train_reveal"] = not bool(st.session_state.get("train_reveal", False))
            # seen++ only when reveal (optional) - harmless metric
            current.seen += 1
            current.added_at = current.added_at or _now()
            # persist seen update
            cards_all2 = _upsert_card(cards_all, current)
            save_cards(cards_all2)
            _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "train_reveal", "word": current.word})
            _train_remove_forced_if_match(current.word)
            st.rerun()

    with b2:
        if st.button("다음", use_container_width=True, key=f"train_next_btn_{current.word}"):
            _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "train_next", "word": current.word})
            _train_remove_forced_if_match(current.word)
            _train_next(len(deck))
            st.rerun()

    with b3:
        if st.button("폐기", use_container_width=True, key=f"train_discard_btn_{current.word}"):
            # delete from storage
            updated = _delete_card(cards_all, current.word)
            save_cards(updated)
            _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "train_discard", "word": current.word})
            st.toast("폐기 완료", icon="🧹")
            # keep index valid
            st.session_state["train_idx"] = max(0, min(st.session_state.get("train_idx", 0), max(0, len(updated) - 1)))
            _train_remove_forced_if_match(current.word)
            st.rerun()

    st.markdown("")
    with st.expander("➕ 신규 무기 등록 (v1.0 카드)", expanded=False):
        _render_add_form(cards_all)

    st.markdown("</div>", unsafe_allow_html=True)


def _upsert_card(cards: List[VocaCard], new: VocaCard) -> List[VocaCard]:
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


def _render_add_form(cards_all: List[VocaCard]) -> None:
    w = st.text_input("WORD", value="")
    meaning = st.text_input("뜻 (KO)", value="")
    chunk_en = st.text_input("CHUNK (EN)", value="")
    chunk_ko = st.text_input("CHUNK (KO)", value="")
    sent_en = st.text_area("SENTENCE (EN)", value="", height=70)
    sent_ko = st.text_area("SENTENCE (KO)", value="", height=70)
    tag = st.text_input("TAG (선택)", value="")
    if st.button("✅ 무기 등록", use_container_width=True):
        w2 = (w or "").strip()
        if not w2:
            st.warning("WORD는 필수입니다.")
            return
        card = VocaCard(
            word=w2,
            meaning_ko=(meaning or "").strip(),
            chunk_en=(chunk_en or "").strip(),
            chunk_ko=(chunk_ko or "").strip(),
            sentence_en=(sent_en or "").strip(),
            sentence_ko=(sent_ko or "").strip(),
            tag=(tag or "").strip(),
            added_at=_now(),
        )
        updated = _upsert_card(cards_all, card)
        save_cards(updated)
        _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "add_card", "word": w2})
        st.toast("무기 등록 완료", icon="✅")
        st.rerun()


# ------------------------------------------------------------
# BATTLE logic (44 sec / 10 questions / HP / no meaning)
# ------------------------------------------------------------
def _battle_left_sec() -> int:
    if not st.session_state.get("battle_running"):
        return int(st.session_state.get("battle_limit_sec", 44))
    started = st.session_state.get("battle_started_at")
    if not started:
        return int(st.session_state.get("battle_limit_sec", 44))
    limit = int(st.session_state.get("battle_limit_sec", 44))
    elapsed = int(time.time() - float(started))
    return max(0, limit - elapsed)


def _timer_stage(left_sec: int) -> str:
    # stage by design
    if left_sec >= 25:
        return "gray"     # 44~25
    if left_sec >= 11:
        return "orange"   # 24~11
    return "red"          # 10~0


def _timer_class(stage: str) -> str:
    if stage == "orange":
        return "t-orange shake"
    if stage == "red":
        return "t-red shake"
    return "t-gray"


def _timer_text_class(stage: str) -> str:
    # make it scarier under 10 sec
    if stage == "red":
        return "pulse"
    return ""


def _make_question_set(cards: List[VocaCard], n: int = 10) -> List[Dict[str, Any]]:
    # must have sentence + word
    pool = [c for c in cards if c.word.strip() and c.sentence_en.strip()]
    if len(pool) == 0:
        return []

    # pick up to n unique
    picked = random.sample(pool, k=min(n, len(pool)))

    # build each question with 4 choices
    words = [c.word for c in pool]
    out = []
    for c in picked:
        ans = c.word
        # choose 3 distractors
        distract = [w for w in words if w != ans]
        distract = random.sample(distract, k=min(3, len(distract)))
        choices = distract + [ans]
        random.shuffle(choices)

        # blank sentence (replace whole word occurrences carefully)
        sent = c.sentence_en
        # naive replacement (good enough for TOEIC single-word target)
        blank = "____"
        # replace first exact match (case-insensitive) by splitting tokens fallback
        replaced = False
        # attempt common patterns: " word " / "word." / "word," etc.
        for pat in [f" {ans} ", f"{ans}.", f"{ans},", f"{ans};", f"{ans}:", f"{ans}!", f"{ans}?", f"({ans})", f'"{ans}"']:
            if pat in sent:
                sent = sent.replace(pat, pat.replace(ans, blank), 1)
                replaced = True
                break
        if not replaced:
            # fallback: replace first occurrence as substring
            sent = sent.replace(ans, blank, 1)

        out.append(
            {
                "answer": ans,
                "sentence": sent,
                "choices": choices,
                "tag": c.tag,
                "source_word": c.word,
            }
        )
    return out


def _battle_fail(reason: str, force_words: List[str]) -> None:
    # fail design:
    # - no answer reveal
    # - no score
    # - streak reset
    st.session_state["battle_running"] = False
    st.session_state["battle_started_at"] = None
    st.session_state["battle_questions"] = []
    st.session_state["battle_q_index"] = 0
    st.session_state["battle_locked"] = False
    st.session_state["battle_streak"] = 0
    st.session_state["battle_last_fail_reason"] = reason

    # force return to train
    st.session_state["train_force_queue"] = list(_merge_force_queue(st.session_state.get("train_force_queue", []), force_words))
    _set_mode("TRAIN")

    _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "battle_fail", "reason": reason, "force_words": force_words})


def _merge_force_queue(existing: List[str], add: List[str]) -> List[str]:
    # keep order: new items first, avoid duplicates
    ex = [w for w in (existing or []) if w.strip()]
    new = [w for w in (add or []) if w.strip()]
    out = []
    seen = set()
    for w in new + ex:
        k = w.strip().lower()
        if not k or k in seen:
            continue
        seen.add(k)
        out.append(w)
    return out


def render_battle(cards_all: List[VocaCard]) -> None:
    st.markdown('<div class="snapq-wrap">', unsafe_allow_html=True)

    st.markdown('<div class="hero battle-hero">', unsafe_allow_html=True)
    st.markdown('<div class="h-title">🔥 VOCA BATTLE</div>', unsafe_allow_html=True)
    st.markdown('<div class="h-sub">44초 심문실 · 10문제 · HP · 뜻보기 없음 · 되돌리기 없음</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # build questions if not running
    pool_ok = len([c for c in cards_all if c.word.strip() and c.sentence_en.strip()]) >= 1
    if not pool_ok:
        st.error("BATTLE에 필요한 데이터가 없습니다: sentence(예문)가 있는 카드가 최소 1개 필요합니다.")
        st.info("TRAIN에서 v1.0 카드로 예문(sentence)을 추가한 뒤 다시 시도하세요.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # 2 columns + HUD (design)
    left, right = st.columns([2.15, 1.0], gap="large")

    # --- Right HUD ---
    with right:
        left_sec = _battle_left_sec()
        stage = _timer_stage(left_sec)
        tcls = _timer_class(stage)

        # timer bar fill %
        limit = int(st.session_state.get("battle_limit_sec", 44))
        pct = 0 if limit <= 0 else max(0, min(100, int((left_sec / limit) * 100)))

        st.markdown('<div class="hud">', unsafe_allow_html=True)
        st.markdown('<div class="hud-title">🎛️ BATTLE HUD</div>', unsafe_allow_html=True)

        # mission / hp
        q_idx = int(st.session_state.get("battle_q_index", 0))
        hp = int(st.session_state.get("battle_hp", 3))
        st.markdown(f'<div class="hud-sub">Mission</div><p class="hud-kpi">{min(q_idx+1,10)} / 10</p>', unsafe_allow_html=True)
        st.markdown(f'<div class="hud-sub">HP</div><p class="hud-kpi">❤️ {hp}</p>', unsafe_allow_html=True)

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        # timer UI
        ttxt = _timer_text_class(stage)
        st.markdown(f"<div class='hud-sub'>남은 시간</div>", unsafe_allow_html=True)
        st.markdown(f"<p class='hud-kpi {ttxt}'>{left_sec}s</p>", unsafe_allow_html=True)

        st.markdown(f"<div class='tbar {tcls}'><div class='tfill' style='width:{pct}%;'></div></div>", unsafe_allow_html=True)

        st.markdown("<hr style='opacity:0.18;'>", unsafe_allow_html=True)

        # Start / Stop / Reset
        if not st.session_state.get("battle_running"):
            if st.button("▶ BATTLE START", use_container_width=True):
                st.session_state["battle_running"] = True
                st.session_state["battle_started_at"] = time.time()
                st.session_state["battle_limit_sec"] = 44  # fixed
                st.session_state["battle_hp"] = 3
                st.session_state["battle_q_index"] = 0
                st.session_state["battle_locked"] = False
                st.session_state["battle_questions"] = _make_question_set(cards_all, n=10)
                st.session_state["battle_last_fail_reason"] = ""

                _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "battle_start", "limit_sec": 44})
                st.rerun()
        else:
            if st.button("⏹ STOP (포기)", use_container_width=True):
                _battle_fail("stop", force_words=_current_force_words())
                st.toast("전장 종료. TRAIN으로 귀환.", icon="🟩")
                st.rerun()

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

        # fail banner (if any)
        if st.session_state.get("battle_last_fail_reason"):
            st.markdown("<hr style='opacity:0.18;'>", unsafe_allow_html=True)
            st.error("🧨 실패: “아… 이거 TRAIN에서 봤던 건데…”")
            st.caption(f"사유: {st.session_state.get('battle_last_fail_reason')}")

        st.markdown("</div>", unsafe_allow_html=True)

    # --- Left main ---
    with left:
        # enforce timeout
        if st.session_state.get("battle_running") and _battle_left_sec() <= 0:
            # timeout fail rule
            _battle_fail("timeout", force_words=_current_force_words())
            st.rerun()

        if not st.session_state.get("battle_running"):
            st.info("▶ BATTLE START를 누르면 44초 심문실이 시작됩니다. (뜻보기 없음)")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        questions: List[Dict[str, Any]] = st.session_state.get("battle_questions", []) or []
        if len(questions) == 0:
            # If we can't make 10, still run what we can; but if 0 -> fail to train.
            _battle_fail("no_questions", force_words=[])
            st.rerun()

        q_idx = int(st.session_state.get("battle_q_index", 0))
        hp = int(st.session_state.get("battle_hp", 3))

        # if completed
        if q_idx >= len(questions):
            # success: streak++ and return to train (or keep battle ready)
            st.session_state["battle_running"] = False
            st.session_state["battle_started_at"] = None
            st.session_state["battle_locked"] = False
            st.session_state["battle_streak"] = int(st.session_state.get("battle_streak", 0)) + 1
            _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "battle_clear", "streak": st.session_state["battle_streak"]})

            st.success("🏁 CLEAR! (정답 공개는 안 해도 됨) → 다음 심문실 준비 완료")
            st.markdown(f"<span class='badge'>현재 스트릭: {st.session_state['battle_streak']}</span>", unsafe_allow_html=True)
            st.markdown("")
            if st.button("다시 BATTLE (새 44초)", use_container_width=True):
                st.session_state["battle_running"] = True
                st.session_state["battle_started_at"] = time.time()
                st.session_state["battle_limit_sec"] = 44
                st.session_state["battle_hp"] = 3
                st.session_state["battle_q_index"] = 0
                st.session_state["battle_locked"] = False
                st.session_state["battle_questions"] = _make_question_set(cards_all, n=10)
                st.session_state["battle_last_fail_reason"] = ""
                _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "battle_restart"})
                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
            return

        # if HP dead
        if hp <= 0:
            _battle_fail("hp_zero", force_words=_current_force_words())
            st.rerun()

        q = questions[q_idx]
        stage = _timer_stage(_battle_left_sec())
        shaky = "shake" if stage in ("orange", "red") else ""
        pulse = "pulse" if stage == "red" else ""

        # Title line
        st.markdown(
            f"<span class='badge'>Mission {q_idx+1} / 10</span> &nbsp; "
            f"<span class='badge'>⏱ {max(0,_battle_left_sec())}s</span>",
            unsafe_allow_html=True,
        )
        st.markdown("")

        # Question box (no meaning reveal!)
        st.markdown(f"<div class='card {shaky}'>", unsafe_allow_html=True)
        st.markdown(f"<div class='k-sent {pulse}'>{q.get('sentence','')}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("")

        # 4 choices (P5 style, clickable cards)
        choices: List[str] = q.get("choices", [])
        if len(choices) < 2:
            _battle_fail("bad_choices", force_words=_current_force_words())
            st.rerun()

        st.markdown("<div class='choice-grid'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        btn_cols = [c1, c2, c1, c2]  # 2x2
        for i, choice in enumerate(choices[:4]):
            with btn_cols[i]:
                if st.button(choice, use_container_width=True, key=f"battle_choice_{q_idx}_{i}"):
                    if st.session_state.get("battle_locked"):
                        st.stop()
                    st.session_state["battle_locked"] = True

                    ans = q.get("answer")
                    if choice == ans:
                        # correct -> next
                        _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "battle_correct", "q": q_idx+1, "word": ans})
                        st.session_state["battle_q_index"] = q_idx + 1
                        st.session_state["battle_locked"] = False
                        st.rerun()
                    else:
                        # wrong -> HP--
                        st.session_state["battle_hp"] = int(st.session_state.get("battle_hp", 3)) - 1
                        _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "battle_wrong", "q": q_idx+1, "picked": choice, "answer": ans})

                        # If HP is now <=0 -> fail immediately
                        if int(st.session_state.get("battle_hp", 0)) <= 0:
                            _battle_fail("hp_zero", force_words=_current_force_words())
                            st.rerun()

                        # no answer reveal, just pressure
                        st.toast("MISS ❌", icon="❌")
                        st.session_state["battle_locked"] = False
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def _current_force_words() -> List[str]:
    # Force the *current question's target word* back to TRAIN on fail
    qs: List[Dict[str, Any]] = st.session_state.get("battle_questions", []) or []
    q_idx = int(st.session_state.get("battle_q_index", 0))
    if 0 <= q_idx < len(qs):
        w = qs[q_idx].get("source_word") or qs[q_idx].get("answer")
        return [w] if w else []
    return []


# ------------------------------------------------------------
# Main render (mode switch)
# ------------------------------------------------------------
def app() -> None:
    _inject_css()
    _ensure_state()

    cards_all = load_cards()

    # Top mode selector
    mode = st.radio(
        "모드 선택",
        options=["TRAIN", "BATTLE"],
        index=0 if st.session_state.get("voca_mode", "TRAIN") == "TRAIN" else 1,
        horizontal=True,
        key="voca_mode_radio",
    )
    st.session_state["voca_mode"] = mode

    # TRAIN: single column (no HUD)
    if mode == "TRAIN":
        render_train(cards_all)
    else:
        render_battle(cards_all)


# ------------------------------------------------------------
# Compatibility for wrapper page
# pages/03_Secret_Armory_Main.py:
#   from app.arenas.secret_armory import render
#   render()
# ------------------------------------------------------------
def render() -> None:
    app()


# direct run (optional)
if __name__ == "__main__":
    st.set_page_config(page_title="SnapQ - Secret Armory v1.0", layout="wide")
    render()
