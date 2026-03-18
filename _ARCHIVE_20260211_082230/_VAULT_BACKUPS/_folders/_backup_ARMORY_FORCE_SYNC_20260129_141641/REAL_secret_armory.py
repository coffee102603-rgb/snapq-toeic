from __future__ import annotations

import json
import random
import re
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

# ============================================================
# SnapQ VOCA v1.0 (FINAL SPEC)
#
# TRAIN = "정리실 / 무기 손질소"
#   - NO timer / NO HP / NO combo / NO pressure
#   - 1-card learning: WORD / CHUNK / SENTENCE
#   - Buttons: [뜻 보기] [다음] [폐기] (big tap, mobile-first)
#
# BATTLE = "44초 심문실"
#   - 44 sec fixed / 10 Q / HP=3
#   - NO meaning reveal / NO rollback / NO rest
#   - Same sentence, target word -> ____ (4 choices)
#   - Timer stages:
#       44~25: gray (calm)
#       24~11: orange + shake
#       10~0 : red + shake + pulse
#   - FAIL (timeout / hp=0):
#       - NO answer reveal
#       - NO score reveal
#       - streak reset
#       - target word forced back to TRAIN (priority queue)
#
# DATA:
#   - Primary store: data/armory/secret_armory_words.json
#   - Auto-import from ANY secret_armory.json under PROJECT_ROOT (newest first)
#
# Wrapper compatibility:
#   from app.arenas.secret_armory import render
#   render()
# ============================================================

# -----------------------------
# Paths
# -----------------------------
THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parents[2]
DATA_DIR = PROJECT_ROOT / "data"
ARMORY_DIR = DATA_DIR / "armory"
ARMORY_DIR.mkdir(parents=True, exist_ok=True)

WORDS_JSON = ARMORY_DIR / "secret_armory_words.json"
EVENTS_JSONL = ARMORY_DIR / "secret_armory_events.jsonl"

# battle constants
BATTLE_LIMIT = 44
BATTLE_Q = 10
BATTLE_HP = 3

# toggles
DEBUG_BANNER = False  # True면 상단에 로드 경로/버전 표시
APP_VER = "VOCA_v1.0_FINALSPEC_20260129"


# -----------------------------
# utils
# -----------------------------
def _now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


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


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        # logging must never break gameplay
        pass


# -----------------------------
# model
# -----------------------------
@dataclass
class Card:
    word: str
    meaning_ko: str = ""
    chunk_en: str = ""
    sentence_en: str = ""
    tag: str = "P7"
    added_at: str = ""
    seen: int = 0

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Card":
        return Card(
            word=str(d.get("word", "")).strip(),
            meaning_ko=str(d.get("meaning_ko", d.get("meaning", ""))).strip(),
            chunk_en=str(d.get("chunk_en", d.get("chunk", ""))).strip(),
            sentence_en=str(d.get("sentence_en", d.get("sentence", d.get("example", "")))).strip(),
            tag=str(d.get("tag", "P7")).strip() or "P7",
            added_at=str(d.get("added_at", "")).strip(),
            seen=int(d.get("seen", d.get("seen_count", 0)) or 0),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "word": self.word,
            "meaning_ko": self.meaning_ko,
            "chunk_en": self.chunk_en,
            "sentence_en": self.sentence_en,
            "tag": self.tag,
            "added_at": self.added_at,
            "seen": self.seen,
        }


def _dedupe(cards: List[Card]) -> List[Card]:
    seen = set()
    out = []
    for c in cards:
        k = c.word.strip().lower()
        if not k or k in seen:
            continue
        seen.add(k)
        out.append(c)
    return out


def _upsert(cards: List[Card], new: Card) -> List[Card]:
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


def _delete(cards: List[Card], word: str) -> List[Card]:
    key = (word or "").strip().lower()
    return [c for c in cards if c.word.strip().lower() != key]


def save_cards(cards: List[Card]) -> None:
    _safe_write_json(
        WORDS_JSON,
        {"schema": "secret_armory_v1", "updated_at": _now(), "cards": [c.to_dict() for c in cards]},
    )


# -----------------------------
# Import P7 data
# - find ANY "secret_armory.json" under project (including app/data/armory)
# - newest first
# -----------------------------
def _find_secret_armory_json() -> List[Path]:
    found: List[Path] = []
    try:
        for p in PROJECT_ROOT.rglob("secret_armory.json"):
            if p.is_file():
                found.append(p)
    except Exception:
        pass

    # newest first
    try:
        found.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    except Exception:
        pass

    # unique
    uniq: List[Path] = []
    seen = set()
    for p in found:
        rp = str(p.resolve())
        if rp in seen:
            continue
        seen.add(rp)
        uniq.append(p)
    return uniq


def _extract_chunk(sentence: str, word: str) -> str:
    if not sentence or not word:
        return word.strip()
    w = word.strip()
    m = re.search(rf"\b(am|is|are|was|were|be|been|being)\s+({re.escape(w)})\b", sentence, flags=re.I)
    if m:
        return f"{m.group(1)} {m.group(2)}"
    return w


def _import_from_any_secret_armory_json() -> Tuple[List[Card], Optional[str]]:
    for p in _find_secret_armory_json():
        raw = _safe_read_json(p)
        if not isinstance(raw, list) or not raw:
            continue

        cards: List[Card] = []
        for it in raw:
            if not isinstance(it, dict):
                continue

            # accept either source=P7 or missing source
            src = str(it.get("source", "")).upper().strip()
            if src and src != "P7":
                continue

            w = str(it.get("word", "")).strip()
            if not w:
                continue

            meaning = str(it.get("meaning_ko", it.get("meaning", ""))).strip()
            sent = str(it.get("sentence_en", it.get("sentence", it.get("example", "")))).strip()
            chunk = str(it.get("chunk_en", "")).strip() or _extract_chunk(sent, w)

            cards.append(
                Card(
                    word=w,
                    meaning_ko=meaning,
                    chunk_en=chunk,
                    sentence_en=sent,
                    tag=str(it.get("tag", "P7")) or "P7",
                    added_at=_now(),
                )
            )

        cards = _dedupe(cards)
        if cards:
            _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "p7_import", "from": str(p), "count": len(cards)})
            return cards, str(p)

    return [], None


def load_cards(force_import: bool = False) -> List[Card]:
    raw = _safe_read_json(WORDS_JSON)
    cards: List[Card] = []
    if isinstance(raw, dict) and isinstance(raw.get("cards"), list):
        for it in raw["cards"]:
            if isinstance(it, dict) and it.get("word"):
                cards.append(Card.from_dict(it))
    cards = _dedupe(cards)

    # force import OR empty store -> import
    if force_import or len(cards) == 0:
        imported, src = _import_from_any_secret_armory_json()
        if imported:
            cards = imported
            save_cards(cards)
        else:
            # keep empty if none found
            if force_import:
                _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "p7_import_failed", "reason": "no_valid_secret_armory_json"})

    return _dedupe(cards)


# -----------------------------
# CSS (mobile big tap + game vibe)
# -----------------------------
def inject_css() -> None:
    st.markdown(
        """
<style>
.stApp{
  background:
    radial-gradient(900px 650px at 18% 12%, rgba(34,211,238,0.18), transparent 60%),
    radial-gradient(900px 650px at 76% 10%, rgba(167,139,250,0.14), transparent 62%),
    linear-gradient(180deg, rgba(2,6,23,1) 0%, rgba(2,6,23,1) 100%) !important;
  color:#F5F7FF !important;
}
[data-testid="stMarkdownContainer"], .stMarkdown, .stMarkdown p, label { color:#F5F7FF !important; }

.wrap{ max-width: 980px; margin: 0 auto; padding-bottom: 18px; }
.hero{
  border-radius: 18px; padding: 14px 16px;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.06);
  box-shadow: 0 12px 30px rgba(0,0,0,0.22);
  backdrop-filter: blur(10px);
}
.h1{ font-size: 30px; font-weight: 950; letter-spacing: -0.6px; margin:0; }
.h2{ margin: 4px 0 0 0; opacity: 0.90; font-weight: 850; font-size: 13px; }

.badge{
  display:inline-block; padding: 6px 10px; border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.18);
  background: rgba(0,0,0,0.22);
  font-size: 12px; font-weight: 900;
}

.card{
  border-radius: 18px; padding: 16px 16px;
  border: 1px solid rgba(255,255,255,0.16);
  background: rgba(255,255,255,0.08);
  box-shadow: 0 16px 36px rgba(0,0,0,0.22);
  backdrop-filter: blur(10px);
}
.kL{ font-size: 12px; opacity: 0.85; font-weight: 900; letter-spacing: 0.2px; }
.kW{ font-size: 32px; font-weight: 950; margin: 2px 0 10px 0; }
.kC{ font-size: 16px; font-weight: 900; margin: 2px 0 10px 0; }
.kS{ font-size: 16px; font-weight: 850; line-height: 1.55; }
.kKO{ font-size: 14px; opacity: 0.95; font-weight: 850; margin-top: 6px; }

.bigbtn div[data-testid="stButton"] > button{
  width:100% !important; min-height: 74px !important; border-radius: 18px !important;
  font-weight: 950 !important; font-size: 16px !important; padding: 14px 16px !important;
  border: 1px solid rgba(255,255,255,0.18) !important; background: rgba(255,255,255,0.95) !important;
  color: #0F172A !important; box-shadow: 0 12px 28px rgba(0,0,0,0.22) !important;
}
.bigbtn div[data-testid="stButton"] > button:hover{
  transform: translateY(-1px);
  background: linear-gradient(135deg, #22D3EE, #A78BFA) !important;
  color:#ffffff !important;
}
.bigbtn div[data-testid="stButton"] > button:hover *{ color:#ffffff !important; }

.hud{
  position: sticky; top: 10px; border-radius: 18px; padding: 12px 12px;
  border: 1px solid rgba(255,255,255,0.14); background: rgba(10,12,16,0.62);
  box-shadow: 0 16px 36px rgba(0,0,0,0.30); backdrop-filter: blur(10px);
}
.ht{ font-weight: 950; margin: 0 0 8px 0; }
.kpi{ font-size: 26px; font-weight: 950; margin: 0; }
.sub{ font-size: 12px; opacity: 0.86; font-weight: 800; margin-top: 2px; }

.tbar{ height: 10px; width: 100%; border-radius: 999px; border:1px solid rgba(255,255,255,0.16);
  background: rgba(255,255,255,0.08); overflow:hidden; }
.tfill{ height:100%; width:50%; background: rgba(200,200,200,0.80); }
.t-gray .tfill{ background: rgba(200,200,200,0.78); }
.t-orange .tfill{ background: rgba(255,170,60,0.86); }
.t-red .tfill{ background: rgba(255,70,70,0.90); }

@keyframes shake { 0%{transform:translateX(0)} 20%{transform:translateX(-2px)} 40%{transform:translateX(2px)} 60%{transform:translateX(-2px)} 80%{transform:translateX(2px)} 100%{transform:translateX(0)} }
@keyframes pulse { 0%{opacity:1} 50%{opacity:0.55} 100%{opacity:1} }
.shake{ animation: shake 0.25s linear infinite; }
.pulse{ animation: pulse 0.8s ease-in-out infinite; }

.choice div[data-testid="stButton"] > button{
  width:100% !important; min-height: 92px !important; border-radius: 18px !important;
  font-weight: 950 !important; font-size: 17px !important; padding: 18px 16px !important;
  white-space: normal !important; line-height: 1.2 !important;
  background: rgba(255,255,255,0.98) !important; color:#111111 !important;
  border: 1px solid rgba(0,0,0,0.10) !important; box-shadow: 0 12px 28px rgba(0,0,0,0.20) !important;
}
.choice div[data-testid="stButton"] > button:hover{
  background: linear-gradient(135deg, #22D3EE, #4DA3FF) !important;
  color:#ffffff !important;
}
.choice div[data-testid="stButton"] > button:hover *{ color:#ffffff !important; }
</style>
""",
        unsafe_allow_html=True,
    )


# -----------------------------
# state
# -----------------------------
def ensure_state() -> None:
    st.session_state.setdefault("voca_mode", "TRAIN")

    # TRAIN
    st.session_state.setdefault("train_idx", 0)
    st.session_state.setdefault("train_reveal", False)
    st.session_state.setdefault("train_search", "")
    st.session_state.setdefault("train_tag", "ALL")
    st.session_state.setdefault("train_force_queue", [])  # forced return words from battle (priority)

    # BATTLE
    st.session_state.setdefault("battle_running", False)
    st.session_state.setdefault("battle_started_at", None)
    st.session_state.setdefault("battle_hp", BATTLE_HP)
    st.session_state.setdefault("battle_q_index", 0)
    st.session_state.setdefault("battle_questions", [])
    st.session_state.setdefault("battle_locked", False)
    st.session_state.setdefault("battle_streak", 0)  # resets on fail


# -----------------------------
# TRAIN helpers
# -----------------------------
def _merge_force_queue(existing: List[str], add: List[str]) -> List[str]:
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


def _train_deck(cards_all: List[Card]) -> List[Card]:
    # forced words first (priority training after fail)
    fq = st.session_state.get("train_force_queue", []) or []
    if not fq:
        return cards_all
    forced_set = {w.strip().lower() for w in fq if w.strip()}
    forced = [c for c in cards_all if c.word.strip().lower() in forced_set]
    rest = [c for c in cards_all if c.word.strip().lower() not in forced_set]
    # keep forced order
    forced.sort(key=lambda x: fq.index(x.word) if x.word in fq else 999999)
    return forced + rest


def train_filtered(cards_all: List[Card]) -> List[Card]:
    q = (st.session_state.get("train_search", "") or "").strip().lower()
    tag = st.session_state.get("train_tag", "ALL")
    deck = _train_deck(cards_all)

    out = []
    for c in deck:
        if tag != "ALL" and (c.tag or "").strip() != tag:
            continue
        if not q:
            out.append(c)
            continue
        hay = " ".join([c.word, c.meaning_ko, c.chunk_en, c.sentence_en, c.tag]).lower()
        if q in hay:
            out.append(c)
    return out


def train_current(deck: List[Card]) -> Optional[Card]:
    if not deck:
        return None
    idx = int(st.session_state.get("train_idx", 0))
    idx = max(0, min(idx, len(deck) - 1))
    st.session_state["train_idx"] = idx
    return deck[idx]


def train_next(n: int) -> None:
    st.session_state["train_reveal"] = False
    if n <= 0:
        st.session_state["train_idx"] = 0
        return
    st.session_state["train_idx"] = (int(st.session_state.get("train_idx", 0)) + 1) % n


def _train_remove_force_if_match(word: str) -> None:
    fq = st.session_state.get("train_force_queue", []) or []
    if not fq:
        return
    st.session_state["train_force_queue"] = [w for w in fq if w.strip().lower() != (word or "").strip().lower()]


# -----------------------------
# TRAIN UI
# -----------------------------
def render_add_form(cards_all: List[Card]) -> None:
    # manual add (only for emergency / empty deck)
    w = st.text_input("WORD", value="")
    m = st.text_input("뜻 (KO)", value="")
    ch = st.text_input("CHUNK (EN)", value="")
    se = st.text_area("SENTENCE (EN)", value="", height=80)
    tag = st.text_input("TAG (선택)", value="MANUAL")

    st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
    if st.button("✅ 무기 등록", use_container_width=True):
        w2 = (w or "").strip()
        if not w2:
            st.warning("WORD는 필수입니다.")
        else:
            new = Card(
                word=w2,
                meaning_ko=(m or "").strip(),
                chunk_en=(ch or "").strip(),
                sentence_en=(se or "").strip(),
                tag=(tag or "MANUAL"),
                added_at=_now(),
            )
            cards_all2 = _upsert(cards_all, new)
            save_cards(cards_all2)
            _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "manual_add", "word": w2})
            st.toast("등록 완료", icon="✅")
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def render_train(cards_all: List[Card]) -> None:
    st.markdown('<div class="wrap">', unsafe_allow_html=True)

    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.markdown('<p class="h1">🟩 VOCA TRAIN</p>', unsafe_allow_html=True)
    st.markdown('<p class="h2">정리실 / 무기 손질소 · 타이머 없음 · 압박 없음</p>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # filters
    tags = ["ALL"] + sorted({c.tag for c in cards_all if (c.tag or "").strip()})
    c1, c2 = st.columns([2.0, 1.0])
    with c1:
        st.session_state["train_search"] = st.text_input(
            "🔎 검색 (단어/뜻/청크/문장/태그)",
            value=st.session_state.get("train_search", ""),
            key="train_search_in",
        )
    with c2:
        cur = st.session_state.get("train_tag", "ALL")
        st.session_state["train_tag"] = st.selectbox(
            "🏷️ 태그",
            options=tags,
            index=(tags.index(cur) if cur in tags else 0),
            key="train_tag_in",
        )

    deck = train_filtered(cards_all)
    st.markdown(
        f"<span class='badge'>총 무기:{len(cards_all)}</span> &nbsp; <span class='badge'>표시 중:{len(deck)}</span>",
        unsafe_allow_html=True,
    )
    st.markdown("")

    # empty
    if not deck:
        st.error("표시할 무기가 없습니다. (P7 저장 단어가 없거나 임포트 실패)")
        st.caption("해결: P7에서 단어 저장을 한 번 더 하고, 아래 '강제 재임포트' 버튼을 눌러보세요.")
        st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
        if st.button("🔄 P7 강제 재임포트", use_container_width=True):
            # remove store to force reload next run
            try:
                if WORDS_JSON.exists():
                    WORDS_JSON.unlink()
            except Exception:
                pass
            _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "force_reimport_clicked"})
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("➕ 신규 무기 등록(수동)", expanded=True):
            render_add_form(cards_all)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    cur_card = train_current(deck)
    assert cur_card is not None

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='kL'>WORD</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='kW'>{cur_card.word}</div>", unsafe_allow_html=True)

    st.markdown("<div class='kL'>CHUNK</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='kC'>{cur_card.chunk_en or '(chunk 없음)'}</div>", unsafe_allow_html=True)

    st.markdown("<div class='kL'>SENTENCE</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='kS'>{cur_card.sentence_en or '(sentence 없음)'}</div>", unsafe_allow_html=True)

    if st.session_state.get("train_reveal", False):
        if cur_card.meaning_ko:
            st.markdown(f"<div class='kKO'>뜻: {cur_card.meaning_ko}</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # buttons
    b1, b2, b3 = st.columns(3)
    with b1:
        st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
        if st.button("뜻 보기", use_container_width=True, key=f"reveal_{cur_card.word}"):
            st.session_state["train_reveal"] = not bool(st.session_state.get("train_reveal", False))
            cur_card.seen += 1
            cur_card.added_at = cur_card.added_at or _now()
            save_cards(_upsert(cards_all, cur_card))
            _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "train_reveal", "word": cur_card.word})
            _train_remove_force_if_match(cur_card.word)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with b2:
        st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
        if st.button("다음", use_container_width=True, key=f"next_{cur_card.word}"):
            _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "train_next", "word": cur_card.word})
            _train_remove_force_if_match(cur_card.word)
            train_next(len(deck))
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with b3:
        st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
        if st.button("폐기", use_container_width=True, key=f"del_{cur_card.word}"):
            save_cards(_delete(cards_all, cur_card.word))
            _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "train_discard", "word": cur_card.word})
            st.toast("폐기 완료", icon="🧹")
            st.session_state["train_idx"] = 0
            _train_remove_force_if_match(cur_card.word)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # manual add collapsed (not dominant)
    with st.expander("➕ 신규 무기 등록(수동)", expanded=False):
        render_add_form(cards_all)

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# BATTLE helpers
# -----------------------------
def battle_left() -> int:
    if not st.session_state.get("battle_running"):
        return BATTLE_LIMIT
    started = st.session_state.get("battle_started_at")
    if not started:
        return BATTLE_LIMIT
    return max(0, BATTLE_LIMIT - int(time.time() - float(started)))


def stage(sec: int) -> str:
    if sec >= 25:
        return "gray"
    if sec >= 11:
        return "orange"
    return "red"


def _timer_classes(sec: int) -> Tuple[str, str]:
    stg = stage(sec)
    if stg == "gray":
        return "t-gray", ""
    if stg == "orange":
        return "t-orange shake", ""
    return "t-red shake", "pulse"


def make_questions(cards_all: List[Card]) -> List[Dict[str, Any]]:
    pool = [c for c in cards_all if c.word and c.sentence_en]
    if not pool:
        return []
    picked = random.sample(pool, k=min(BATTLE_Q, len(pool)))
    words = [c.word for c in pool]

    qs = []
    for c in picked:
        ans = c.word
        distract_pool = [w for w in words if w != ans]
        distract = random.sample(distract_pool, k=min(3, len(distract_pool)))
        choices = distract + [ans]
        random.shuffle(choices)

        sent2, cnt = re.subn(rf"\b{re.escape(ans)}\b", "____", c.sentence_en, count=1, flags=re.I)
        if cnt == 0:
            sent2 = c.sentence_en.replace(ans, "____", 1)

        qs.append({"answer": ans, "sentence": sent2, "choices": choices})
    return qs


def _battle_fail(reason: str, target_word: Optional[str]) -> None:
    # no answer reveal, no score reveal, reset streak
    st.session_state["battle_running"] = False
    st.session_state["battle_started_at"] = None
    st.session_state["battle_questions"] = []
    st.session_state["battle_q_index"] = 0
    st.session_state["battle_locked"] = False
    st.session_state["battle_hp"] = BATTLE_HP
    st.session_state["battle_streak"] = 0

    # force to train
    st.session_state["voca_mode"] = "TRAIN"

    # push failed word to force queue
    if target_word:
        st.session_state["train_force_queue"] = _merge_force_queue(st.session_state.get("train_force_queue", []), [target_word])

    _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "battle_fail", "reason": reason, "word": target_word or ""})


# -----------------------------
# BATTLE UI
# -----------------------------
def render_battle(cards_all: List[Card]) -> None:
    st.markdown('<div class="wrap">', unsafe_allow_html=True)

    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.markdown('<p class="h1">🔥 VOCA BATTLE</p>', unsafe_allow_html=True)
    st.markdown('<p class="h2">44초 심문실 · 10문제 · HP · 뜻보기 없음 · 되돌리기 없음</p>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if len([c for c in cards_all if c.word and c.sentence_en]) < 1:
        st.error("BATTLE 재료가 없습니다. (예문 sentence 있는 카드가 최소 1개 필요)")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    left, right = st.columns([2.1, 1.0], gap="large")

    # HUD
    with right:
        sec = battle_left()
        tcls, numcls = _timer_classes(sec)
        pct = max(0, min(100, int((sec / BATTLE_LIMIT) * 100)))

        qi = int(st.session_state.get("battle_q_index", 0))
        hp = int(st.session_state.get("battle_hp", BATTLE_HP))

        st.markdown('<div class="hud">', unsafe_allow_html=True)
        st.markdown('<div class="ht">🎛️ BATTLE HUD</div>', unsafe_allow_html=True)

        st.markdown(f"<div class='sub'>Mission</div><p class='kpi'>{min(qi+1,BATTLE_Q)} / {BATTLE_Q}</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='sub'>HP</div><p class='kpi'>❤️ {hp}</p>", unsafe_allow_html=True)

        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='sub'>남은 시간</div><p class='kpi {numcls}'>{sec}s</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='tbar {tcls}'><div class='tfill' style='width:{pct}%;'></div></div>", unsafe_allow_html=True)
        st.markdown("<hr style='opacity:0.18;'>", unsafe_allow_html=True)

        if not st.session_state.get("battle_running"):
            st.markdown('<div class="bigbtn">', unsafe_allow_html=True)
            if st.button("▶ BATTLE START", use_container_width=True):
                st.session_state["battle_running"] = True
                st.session_state["battle_started_at"] = time.time()
                st.session_state["battle_hp"] = BATTLE_HP
                st.session_state["battle_q_index"] = 0
                st.session_state["battle_locked"] = False
                st.session_state["battle_questions"] = make_questions(cards_all)
                _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "battle_start"})
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # main
    with left:
        # timeout -> fail
        if st.session_state.get("battle_running") and battle_left() <= 0:
            # determine current target word (no reveal)
            qs = st.session_state.get("battle_questions", []) or []
            qi = int(st.session_state.get("battle_q_index", 0))
            target = None
            if 0 <= qi < len(qs):
                target = qs[qi].get("answer")
            st.toast("⏰ TIME OUT! (정답 공개 없음) → TRAIN", icon="⏰")
            _battle_fail("timeout", target)
            st.rerun()

        if not st.session_state.get("battle_running"):
            st.info("▶ START를 누르면 44초 심문실이 시작됩니다. (뜻보기 없음)")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        qs: List[Dict[str, Any]] = st.session_state.get("battle_questions", []) or []
        if not qs:
            st.session_state["battle_questions"] = make_questions(cards_all)
            qs = st.session_state["battle_questions"]

        qi = int(st.session_state.get("battle_q_index", 0))
        hp = int(st.session_state.get("battle_hp", BATTLE_HP))

        # HP 0 -> fail
        if hp <= 0:
            target = None
            if 0 <= qi < len(qs):
                target = qs[qi].get("answer")
            st.toast("💥 HP 0! (정답 공개 없음) → TRAIN", icon="💥")
            _battle_fail("hp_zero", target)
            st.rerun()

        # clear
        if qi >= len(qs):
            st.session_state["battle_running"] = False
            st.session_state["battle_started_at"] = None
            st.session_state["battle_questions"] = []
            st.session_state["battle_q_index"] = 0
            st.session_state["battle_locked"] = False
            st.session_state["battle_hp"] = BATTLE_HP
            st.session_state["battle_streak"] = int(st.session_state.get("battle_streak", 0)) + 1
            _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "battle_clear", "streak": st.session_state["battle_streak"]})
            st.success("🏁 CLEAR! (정답 공개 없음) → 다음 심문실 준비 완료")
            st.markdown(f"<span class='badge'>스트릭:{st.session_state['battle_streak']}</span>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            return

        q = qs[qi]
        sec = battle_left()
        _, pulse = _timer_classes(sec)
        stg = stage(sec)
        shaky = "shake" if stg in ("orange", "red") else ""

        st.markdown(
            f"<span class='badge'>Mission {qi+1}/{BATTLE_Q}</span> &nbsp; <span class='badge'>⏱ {sec}s</span>",
            unsafe_allow_html=True,
        )
        st.markdown("")

        st.markdown(f"<div class='card {shaky}'>", unsafe_allow_html=True)
        st.markdown(f"<div class='kS {pulse}'>{q.get('sentence','')}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("")

        choices = q.get("choices", []) or []
        if len(choices) < 4:
            st.error("선택지 생성 실패")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        c1, c2 = st.columns(2)
        cols = [c1, c2, c1, c2]
        for i, ch in enumerate(choices[:4]):
            with cols[i]:
                st.markdown('<div class="choice">', unsafe_allow_html=True)
                if st.button(ch, use_container_width=True, key=f"ch_{qi}_{i}"):
                    if st.session_state.get("battle_locked"):
                        st.stop()
                    st.session_state["battle_locked"] = True

                    ans = q.get("answer")
                    if ch == ans:
                        st.session_state["battle_q_index"] = qi + 1
                        st.session_state["battle_locked"] = False
                        _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "battle_correct", "q": qi+1})
                        st.rerun()
                    else:
                        st.session_state["battle_hp"] = int(st.session_state.get("battle_hp", BATTLE_HP)) - 1
                        st.session_state["battle_locked"] = False
                        _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "battle_wrong", "q": qi+1})
                        st.toast("MISS ❌", icon="❌")
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# main
# -----------------------------
def app() -> None:
    inject_css()
    ensure_state()

    if DEBUG_BANNER:
        st.caption(f"LOADED: {__file__} | {APP_VER}")

    # mode selector
    mode = st.radio(
        "모드 선택",
        ["TRAIN", "BATTLE"],
        index=0 if st.session_state.get("voca_mode", "TRAIN") == "TRAIN" else 1,
        horizontal=True,
        key="voca_mode_radio",
    )
    st.session_state["voca_mode"] = mode

    # load cards (normal)
    cards = load_cards(force_import=False)

    if mode == "TRAIN":
        render_train(cards)
    else:
        render_battle(cards)


def render() -> None:
    app()


if __name__ == "__main__":
    st.set_page_config(page_title="SnapQ • Secret Armory", layout="wide")
    render()
