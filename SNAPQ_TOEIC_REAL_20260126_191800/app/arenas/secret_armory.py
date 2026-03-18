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
# SnapQ VOCA FINAL (Mobile-first)
#
# TRAIN (TV Screen + Remote)
# - Main content is ONE big "TV screen" card
# - Top-right progress: 2/33
# - Inside TV: Word(meaning) -> Chunk(meaning) -> Sentence(meaning)
# - Bottom remote buttons: [▶ NEXT] [🗑️ 폐기] only
# - Top: VOCA TRAIN title + small 🏠 Main Hub + small 🔥 BATTLE ▶
#
# BATTLE (44s interrogation)
# - 44 sec fixed / 10Q / HP=3
# - 2x2 big tap answers
# - Timer stages: gray (44~25), orange+shake (24~11), red+shake+pulse (10~0)
# - Fail(timeout/HP0): no answer reveal, force target word back to TRAIN
# - Top: VOCA BATTLE title + small 🏠 Main Hub + small 🟩 TRAIN ▶
#
# Data
# - Primary store: data/armory/secret_armory_words.json
# - Auto-import from ANY secret_armory.json under project (newest first)
#
# Wrapper compatibility: from app.arenas.secret_armory import render; render()
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

# Battle constants
BATTLE_LIMIT = 44
BATTLE_Q = 10
BATTLE_HP = 3


# -----------------------------
# Utils
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
        pass


# -----------------------------
# Data model
# -----------------------------
@dataclass
class Card:
    word: str
    word_ko: str = ""            # 한국어 뜻(단어)
    chunk_en: str = ""           # 토익 청크/숙어(영문)
    chunk_ko: str = ""           # 청크 해석(한글)
    sentence_en: str = ""        # 짧은 예문(영문)
    sentence_ko: str = ""        # 예문 해석(한글)
    tag: str = "P7"
    added_at: str = ""
    seen: int = 0

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Card":
        # tolerate legacy keys
        return Card(
            word=str(d.get("word", "")).strip(),
            word_ko=str(d.get("word_ko", d.get("meaning_ko", d.get("meaning", "")))).strip(),
            chunk_en=str(d.get("chunk_en", d.get("chunk", ""))).strip(),
            chunk_ko=str(d.get("chunk_ko", "")).strip(),
            sentence_en=str(d.get("sentence_en", d.get("sentence", d.get("example", "")))).strip(),
            sentence_ko=str(d.get("sentence_ko", "")).strip(),
            tag=str(d.get("tag", "P7")).strip() or "P7",
            added_at=str(d.get("added_at", "")).strip(),
            seen=int(d.get("seen", d.get("seen_count", 0)) or 0),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "word": self.word,
            "word_ko": self.word_ko,
            "chunk_en": self.chunk_en,
            "chunk_ko": self.chunk_ko,
            "sentence_en": self.sentence_en,
            "sentence_ko": self.sentence_ko,
            "tag": self.tag,
            "added_at": self.added_at,
            "seen": self.seen,
        }


def _dedupe(cards: List[Card]) -> List[Card]:
    seen = set()
    out: List[Card] = []
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
    out, replaced = [], False
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
        {"schema": "secret_armory_v2_tvtrain", "updated_at": _now(), "cards": [c.to_dict() for c in cards]},
    )


# -----------------------------
# Import P7 data
# - find ANY "secret_armory.json" under project (newest first)
# -----------------------------
def _find_secret_armory_json() -> List[Path]:
    found: List[Path] = []
    try:
        for p in PROJECT_ROOT.rglob("secret_armory.json"):
            if p.is_file():
                found.append(p)
    except Exception:
        pass
    try:
        found.sort(key=lambda x: x.stat().st_mtime, reverse=True)
    except Exception:
        pass

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
    # best-effort: "be + word" pattern
    if not sentence or not word:
        return word.strip()
    w = word.strip()
    m = re.search(rf"\b(am|is|are|was|were|be|been|being)\s+({re.escape(w)})\b", sentence, flags=re.I)
    if m:
        return f"{m.group(1)} {m.group(2)}"
    return w


def _import_p7_cards() -> Tuple[List[Card], Optional[str]]:
    """
    Accept list[dict] rows. We tolerate:
      - word, meaning/meaning_ko, chunk_en/chunk_ko, sentence/sentence_en, sentence_ko
      - source may be "P7" or missing
    """
    for p in _find_secret_armory_json():
        raw = _safe_read_json(p)
        if not isinstance(raw, list) or not raw:
            continue

        cards: List[Card] = []
        for it in raw:
            if not isinstance(it, dict):
                continue

            src = str(it.get("source", "")).upper().strip()
            if src and src != "P7":
                continue

            w = str(it.get("word", "")).strip()
            if not w:
                continue

            meaning = str(it.get("word_ko", it.get("meaning_ko", it.get("meaning", "")))).strip()
            sent = str(it.get("sentence_en", it.get("sentence", it.get("example", "")))).strip()
            chunk_en = str(it.get("chunk_en", "")).strip() or _extract_chunk(sent, w)

            cards.append(
                Card(
                    word=w,
                    word_ko=meaning,
                    chunk_en=chunk_en,
                    chunk_ko=str(it.get("chunk_ko", "")).strip(),
                    sentence_en=sent,
                    sentence_ko=str(it.get("sentence_ko", "")).strip(),
                    tag=str(it.get("tag", "P7")).strip() or "P7",
                    added_at=_now(),
                )
            )

        cards = _dedupe(cards)
        if cards:
            _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "p7_import", "from": str(p), "count": len(cards)})
            return cards, str(p)

    return [], None


def load_cards(force_import: bool = False) -> List[Card]:
    cards: List[Card] = []
    raw = _safe_read_json(WORDS_JSON)
    if isinstance(raw, dict) and isinstance(raw.get("cards"), list):
        for it in raw["cards"]:
            if isinstance(it, dict) and it.get("word"):
                cards.append(Card.from_dict(it))
    cards = _dedupe(cards)

    if force_import or len(cards) == 0:
        imported, _src = _import_p7_cards()
        if imported:
            cards = imported
            save_cards(cards)

    return _dedupe(cards)


# -----------------------------
# Navigation helpers
# -----------------------------
def _try_switch_page(candidates: List[str]) -> None:
    for c in candidates:
        try:
            st.switch_page(c)
            return
        except Exception:
            continue


def go_hub() -> None:
    # You may rename hub page later; we try a few common candidates.
    _try_switch_page(
        [
            "main_hub.py",
            "pages/00_Main_Hub.py",
            "pages/00_MainHub.py",
            "pages/00_Hub.py",
            "pages/01_Main_Hub.py",
            "pages/01_Hub.py",
            "pages/00_Home.py",
            "pages/01_Home.py",
        ]
    )
    st.toast("🏠 Main Hub 경로를 찾지 못했어요. (허브 페이지 파일명 확인 필요)", icon="⚠️")


def go_train() -> None:
    _try_switch_page(["pages/04_VOCA_Train_Arena.py", "pages/03_Secret_Armory_Main.py"])


def go_battle() -> None:
    _try_switch_page(["pages/04_VOCA_Battle_Arena.py", "pages/03_Secret_Armory_Main.py"])


# -----------------------------
# CSS (Mobile-first + TV Screen + Remote)
# -----------------------------
def inject_css() -> None:
    st.markdown(
        r"""
<style>
/* background */
.stApp{
  background:
    radial-gradient(900px 650px at 18% 12%, rgba(34,211,238,0.18), transparent 60%),
    radial-gradient(900px 650px at 76% 10%, rgba(167,139,250,0.14), transparent 62%),
    linear-gradient(180deg, rgba(2,6,23,1) 0%, rgba(2,6,23,1) 100%) !important;
  color:#F5F7FF !important;
}
[data-testid="stMarkdownContainer"], .stMarkdown, .stMarkdown p, label { color:#F5F7FF !important; }

.wrap{ max-width: 980px; margin: 0 auto; padding-bottom: 18px; }

/* top bar */
.topbar{
  border-radius: 18px;
  padding: 14px 16px;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(255,255,255,0.06);
  box-shadow: 0 12px 30px rgba(0,0,0,0.22);
  backdrop-filter: blur(10px);
}
.titleTrain{
  font-size: 30px; font-weight: 980; letter-spacing: -0.8px; margin:0;
  background: linear-gradient(90deg, #A78BFA, #22D3EE);
  -webkit-background-clip:text; background-clip:text; color: transparent;
}
.titleBattle{
  font-size: 30px; font-weight: 980; letter-spacing: -0.8px; margin:0;
  background: linear-gradient(90deg, #FF6B6B, #FFB86B);
  -webkit-background-clip:text; background-clip:text; color: transparent;
}
.tinyNav{
  display:flex; gap:10px; justify-content:flex-end; align-items:center;
  font-weight:900;
}
.tinyHint{opacity:.86; font-size:12px; font-weight:850;}

.smallbtn div[data-testid="stButton"]>button{
  padding: 8px 10px !important;
  border-radius: 999px !important;
  font-weight: 950 !important;
  font-size: 12px !important;
  min-height: 36px !important;
  border: 1px solid rgba(255,255,255,0.20) !important;
  background: rgba(255,255,255,0.12) !important;
  color: #F5F7FF !important;
}
.smallbtn div[data-testid="stButton"]>button:hover{
  background: rgba(255,255,255,0.22) !important;
}

/* TV screen */
.tv{
  border-radius: 22px;
  padding: 16px 16px;
  border: 1px solid rgba(255,255,255,0.16);
  background: rgba(255,255,255,0.08);
  box-shadow: 0 18px 44px rgba(0,0,0,0.25);
  backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
}
.tv:before{
  content:"";
  position:absolute; inset:-2px;
  background: radial-gradient(600px 220px at 30% 10%, rgba(34,211,238,0.14), transparent 70%),
              radial-gradient(600px 220px at 80% 10%, rgba(167,139,250,0.12), transparent 70%);
  pointer-events:none;
}
.progress{
  position:absolute; top:12px; right:14px;
  font-size: 12px; font-weight: 950;
  padding: 6px 10px; border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.18);
  background: rgba(0,0,0,0.18);
}
.kL{ font-size: 12px; opacity: 0.85; font-weight: 900; letter-spacing: 0.2px; margin-top: 6px; }
.kWord{ font-size: 34px; font-weight: 980; margin: 4px 0 10px 0; }
.kSub{ font-size: 16px; font-weight: 900; margin: 2px 0 10px 0; }
.kSent{ font-size: 16px; font-weight: 850; line-height: 1.55; }
.kKO{ font-size: 14px; opacity: 0.92; font-weight: 850; margin-top: 6px; }

/* Remote buttons (bottom, big tap) */
.remote2 div[data-testid="stButton"]>button{
  width:100% !important;
  min-height: 70px !important;
  border-radius: 18px !important;
  font-weight: 980 !important;
  font-size: 16px !important;
  padding: 14px 16px !important;
  border: 1px solid rgba(255,255,255,0.18) !important;
  background: rgba(255,255,255,0.95) !important;
  color: #0F172A !important;
  box-shadow: 0 12px 28px rgba(0,0,0,0.22) !important;
}
.remote2 div[data-testid="stButton"]>button:hover{
  transform: translateY(-1px);
  background: linear-gradient(135deg, #22D3EE, #A78BFA) !important;
  color:#ffffff !important;
}
.remote2 div[data-testid="stButton"]>button:hover *{ color:#ffffff !important; }

/* Battle HUD + pressure */
.hud{
  border-radius: 18px; padding: 12px 12px;
  border: 1px solid rgba(255,255,255,0.14);
  background: rgba(10,12,16,0.62);
  box-shadow: 0 16px 36px rgba(0,0,0,0.30);
  backdrop-filter: blur(10px);
}
.ht{ font-weight: 980; margin: 0 0 8px 0; }
.kpi{ font-size: 24px; font-weight: 980; margin: 0; }
.sub{ font-size: 12px; opacity: 0.86; font-weight: 850; margin-top: 2px; }
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

/* Battle answers */
.choice div[data-testid="stButton"] > button{
  width:100% !important;
  min-height: 92px !important;
  border-radius: 18px !important;
  font-weight: 980 !important;
  font-size: 17px !important;
  padding: 18px 16px !important;
  white-space: normal !important;
  line-height: 1.2 !important;
  background: rgba(255,255,255,0.98) !important;
  color:#111111 !important;
  border: 1px solid rgba(0,0,0,0.10) !important;
  box-shadow: 0 12px 28px rgba(0,0,0,0.20) !important;
}
.choice div[data-testid="stButton"] > button:hover{
  background: linear-gradient(135deg, #22D3EE, #4DA3FF) !important;
  color:#ffffff !important;
}
.choice div[data-testid="stButton"] > button:hover *{ color:#ffffff !important; }

@media (max-width: 640px){
  .block-container{ padding-left:0.75rem !important; padding-right:0.75rem !important; padding-top:0.25rem !important; }
  .kWord{ font-size: 34px; }
}
</style>
""",
        unsafe_allow_html=True,
    )


# -----------------------------
# Session state
# -----------------------------
def ensure_state() -> None:
    # Train
    st.session_state.setdefault("train_idx", 0)
    st.session_state.setdefault("train_force_queue", [])  # words forced back from battle

    # Battle
    st.session_state.setdefault("battle_running", False)
    st.session_state.setdefault("battle_started_at", None)
    st.session_state.setdefault("battle_hp", BATTLE_HP)
    st.session_state.setdefault("battle_q_index", 0)
    st.session_state.setdefault("battle_questions", [])
    st.session_state.setdefault("battle_locked", False)


# -----------------------------
# Train deck logic
# -----------------------------
def _merge_force(existing: List[str], add: List[str]) -> List[str]:
    out, seen = [], set()
    for w in (add or []) + (existing or []):
        k = (w or "").strip().lower()
        if not k or k in seen:
            continue
        seen.add(k)
        out.append(w)
    return out


def _train_deck(cards: List[Card]) -> List[Card]:
    fq = st.session_state.get("train_force_queue", []) or []
    if not fq:
        return cards
    fset = {w.strip().lower() for w in fq if w.strip()}
    forced = [c for c in cards if c.word.strip().lower() in fset]
    rest = [c for c in cards if c.word.strip().lower() not in fset]
    forced.sort(key=lambda x: fq.index(x.word) if x.word in fq else 999999)
    return forced + rest


def train_current(deck: List[Card]) -> Optional[Card]:
    if not deck:
        return None
    idx = int(st.session_state.get("train_idx", 0))
    idx = max(0, min(idx, len(deck) - 1))
    st.session_state["train_idx"] = idx
    return deck[idx]


def train_next(n: int) -> None:
    if n <= 0:
        st.session_state["train_idx"] = 0
        return
    st.session_state["train_idx"] = (int(st.session_state.get("train_idx", 0)) + 1) % n


def _remove_force_if_match(word: str) -> None:
    fq = st.session_state.get("train_force_queue", []) or []
    if not fq:
        return
    st.session_state["train_force_queue"] = [w for w in fq if w.strip().lower() != (word or "").strip().lower()]


# -----------------------------
# Battle logic
# -----------------------------
def battle_left() -> int:
    if not st.session_state.get("battle_running"):
        return BATTLE_LIMIT
    started = st.session_state.get("battle_started_at")
    if not started:
        return BATTLE_LIMIT
    return max(0, BATTLE_LIMIT - int(time.time() - float(started)))


def battle_stage(sec: int) -> str:
    if sec >= 25:
        return "gray"
    if sec >= 11:
        return "orange"
    return "red"


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
    # No answer reveal, reset battle state, force back to train
    st.session_state["battle_running"] = False
    st.session_state["battle_started_at"] = None
    st.session_state["battle_questions"] = []
    st.session_state["battle_q_index"] = 0
    st.session_state["battle_locked"] = False
    st.session_state["battle_hp"] = BATTLE_HP

    if target_word:
        st.session_state["train_force_queue"] = _merge_force(st.session_state.get("train_force_queue", []), [target_word])

    _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "battle_fail", "reason": reason, "word": target_word or ""})
    st.toast("아… 정리실에서 봤던 건데…", icon="🟩")
    go_train()


# -----------------------------
# Top bar UI
# -----------------------------
def _topbar_train() -> None:
    st.markdown('<div class="topbar">', unsafe_allow_html=True)
    cols = st.columns([2.2, 1.0], vertical_alignment="center")
    with cols[0]:
        st.markdown('<p class="titleTrain">VOCA TRAIN</p>', unsafe_allow_html=True)
        st.markdown('<p class="tinyHint">정리실 · TV 스크린 + 리모컨</p>', unsafe_allow_html=True)
    with cols[1]:
        st.markdown('<div class="tinyNav">', unsafe_allow_html=True)
        cA, cB = st.columns(2)
        with cA:
            st.markdown('<div class="smallbtn">', unsafe_allow_html=True)
            if st.button("🏠 Main Hub", key="train_hub"):
                go_hub()
            st.markdown("</div>", unsafe_allow_html=True)
        with cB:
            st.markdown('<div class="smallbtn">', unsafe_allow_html=True)
            if st.button("🔥 심문실 ▶", key="train_to_battle"):
                go_battle()
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def _topbar_battle() -> None:
    st.markdown('<div class="topbar">', unsafe_allow_html=True)
    cols = st.columns([2.2, 1.0], vertical_alignment="center")
    with cols[0]:
        st.markdown('<p class="titleBattle">VOCA BATTLE</p>', unsafe_allow_html=True)
        st.markdown('<p class="tinyHint">44초 심문실 · 10문제 · HP</p>', unsafe_allow_html=True)
    with cols[1]:
        st.markdown('<div class="tinyNav">', unsafe_allow_html=True)
        cA, cB = st.columns(2)
        with cA:
            st.markdown('<div class="smallbtn">', unsafe_allow_html=True)
            if st.button("🏠 Main Hub", key="battle_hub"):
                go_hub()
            st.markdown("</div>", unsafe_allow_html=True)
        with cB:
            st.markdown('<div class="smallbtn">', unsafe_allow_html=True)
            if st.button("🟩 정리실 ▶", key="battle_to_train"):
                go_train()
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# TRAIN render
# -----------------------------
def render_train(cards_all: List[Card]) -> None:
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    _topbar_train()
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    deck = _train_deck(cards_all)
    total = len(deck)

    if total == 0:
        st.error("P7 저장 단어가 아직 없어요. (secret_armory.json 임포트 실패 또는 데이터 없음)")
        st.markdown('<div class="smallbtn">', unsafe_allow_html=True)
        if st.button("🔄 P7 다시 읽기", key="force_import_train"):
            # force import: delete store then reload
            try:
                if WORDS_JSON.exists():
                    WORDS_JSON.unlink()
            except Exception:
                pass
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        return

    cur = train_current(deck)
    assert cur is not None
    pos = int(st.session_state.get("train_idx", 0)) + 1

    # TV screen
    st.markdown("<div class='tv'>", unsafe_allow_html=True)
    st.markdown(f"<div class='progress'>{pos} / {total}</div>", unsafe_allow_html=True)

    # WORD
    st.markdown("<div class='kL'>WORD</div>", unsafe_allow_html=True)
    w_line = cur.word if not cur.word_ko else f"{cur.word}  <span style='opacity:.92;font-weight:900;'>({cur.word_ko})</span>"
    st.markdown(f"<div class='kWord'>{w_line}</div>", unsafe_allow_html=True)

    # CHUNK
    st.markdown("<div class='kL'>TOEIC CHUNK</div>", unsafe_allow_html=True)
    ch = cur.chunk_en or "(chunk 없음)"
    if cur.chunk_ko:
        ch = f"{ch}  <span style='opacity:.88;font-weight:850;'>({cur.chunk_ko})</span>"
    st.markdown(f"<div class='kSub'>{ch}</div>", unsafe_allow_html=True)

    # SENTENCE
    st.markdown("<div class='kL'>TOEIC SENTENCE</div>", unsafe_allow_html=True)
    se = cur.sentence_en or "(sentence 없음)"
    st.markdown(f"<div class='kSent'>{se}</div>", unsafe_allow_html=True)
    if cur.sentence_ko:
        st.markdown(f"<div class='kKO'>({cur.sentence_ko})</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

    # Remote (NEXT / 폐기 only)
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown('<div class="remote2">', unsafe_allow_html=True)
        if st.button("▶ NEXT", use_container_width=True, key=f"train_next_{cur.word}"):
            _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "train_next", "word": cur.word})
            _remove_force_if_match(cur.word)
            train_next(total)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="remote2">', unsafe_allow_html=True)
        if st.button("🗑️ 폐기", use_container_width=True, key=f"train_discard_{cur.word}"):
            updated = _delete(cards_all, cur.word)
            save_cards(updated)
            _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "train_discard", "word": cur.word})
            st.toast("폐기 완료", icon="🗑️")
            st.session_state["train_idx"] = max(0, min(st.session_state.get("train_idx", 0), max(0, len(updated) - 1)))
            _remove_force_if_match(cur.word)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# BATTLE render
# -----------------------------
def render_battle(cards_all: List[Card]) -> None:
    st.markdown('<div class="wrap">', unsafe_allow_html=True)
    _topbar_battle()
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

    usable = [c for c in cards_all if c.word and c.sentence_en]
    if len(usable) < 1:
        st.error("BATTLE 재료가 없습니다. (예문 sentence 있는 카드가 최소 1개 필요)")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # If running and timeout => fail
    if st.session_state.get("battle_running") and battle_left() <= 0:
        qs = st.session_state.get("battle_questions", []) or []
        qi = int(st.session_state.get("battle_q_index", 0))
        target = qs[qi].get("answer") if 0 <= qi < len(qs) else None
        _battle_fail("timeout", target)
        return

    # Layout: question + HUD on mobile: stack; on wide: 2 columns
    left, right = st.columns([2.1, 1.0], gap="large")

    with right:
        sec = battle_left()
        stg = battle_stage(sec)
        pct = max(0, min(100, int((sec / BATTLE_LIMIT) * 100)))
        tcls = "t-gray" if stg == "gray" else ("t-orange shake" if stg == "orange" else "t-red shake")
        numcls = "pulse" if stg == "red" else ""

        qi = int(st.session_state.get("battle_q_index", 0))
        hp = int(st.session_state.get("battle_hp", BATTLE_HP))

        st.markdown("<div class='hud'>", unsafe_allow_html=True)
        st.markdown("<div class='ht'>🎛️ BATTLE HUD</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='sub'>Mission</div><p class='kpi'>{min(qi+1, BATTLE_Q)} / {BATTLE_Q}</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='sub'>HP</div><p class='kpi'>❤️ {hp}</p>", unsafe_allow_html=True)
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
        st.markdown(f"<div class='sub'>폭탄</div><p class='kpi {numcls}'>{sec}s</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='tbar {tcls}'><div class='tfill' style='width:{pct}%;'></div></div>", unsafe_allow_html=True)
        st.markdown("<hr style='opacity:0.18;'>", unsafe_allow_html=True)

        if not st.session_state.get("battle_running"):
            st.markdown('<div class="smallbtn">', unsafe_allow_html=True)
            if st.button("🚨 심문 시작", use_container_width=True, key="battle_start"):
                st.session_state["battle_running"] = True
                st.session_state["battle_started_at"] = time.time()
                st.session_state["battle_hp"] = BATTLE_HP
                st.session_state["battle_q_index"] = 0
                st.session_state["battle_locked"] = False
                st.session_state["battle_questions"] = make_questions(usable)
                _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "battle_start"})
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with left:
        if not st.session_state.get("battle_running"):
            st.info("🚨 ‘심문 시작’을 누르면 44초가 시작됩니다. (뜻 보기 없음)")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        qs: List[Dict[str, Any]] = st.session_state.get("battle_questions", []) or []
        if not qs:
            st.session_state["battle_questions"] = make_questions(usable)
            qs = st.session_state["battle_questions"]

        qi = int(st.session_state.get("battle_q_index", 0))
        hp = int(st.session_state.get("battle_hp", BATTLE_HP))

        # HP 0 => fail
        if hp <= 0:
            target = qs[qi].get("answer") if 0 <= qi < len(qs) else None
            _battle_fail("hp_zero", target)
            return

        # Clear
        if qi >= len(qs):
            st.session_state["battle_running"] = False
            st.session_state["battle_started_at"] = None
            st.session_state["battle_questions"] = []
            st.session_state["battle_q_index"] = 0
            st.session_state["battle_locked"] = False
            st.session_state["battle_hp"] = BATTLE_HP
            st.success("🏁 CLEAR! (정답 공개 없음)")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        q = qs[qi]
        sec = battle_left()
        stg = battle_stage(sec)
        shaky = "shake" if stg in ("orange", "red") else ""
        pulse = "pulse" if stg == "red" else ""

        st.markdown(
            f"<span style='display:inline-block;padding:6px 10px;border-radius:999px;border:1px solid rgba(255,255,255,0.18);background:rgba(0,0,0,0.22);font-weight:950;font-size:12px;'>🎯 심문 {qi+1}/{BATTLE_Q}</span>"
            f"&nbsp; <span style='display:inline-block;padding:6px 10px;border-radius:999px;border:1px solid rgba(255,255,255,0.18);background:rgba(0,0,0,0.22);font-weight:950;font-size:12px;'>⏱ {sec}s</span>",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        st.markdown(f"<div class='tv {shaky}'>", unsafe_allow_html=True)
        st.markdown(f"<div class='kSent {pulse}' style='font-size:18px;font-weight:950;'>{q.get('sentence','')}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

        choices = q.get("choices", []) or []
        if len(choices) < 4:
            _battle_fail("bad_choices", q.get("answer"))
            return

        c1, c2 = st.columns(2, gap="large")
        cols = [c1, c2, c1, c2]
        for i, ch in enumerate(choices[:4]):
            with cols[i]:
                st.markdown("<div class='choice'>", unsafe_allow_html=True)
                if st.button(ch, use_container_width=True, key=f"battle_ch_{qi}_{i}"):
                    if st.session_state.get("battle_locked"):
                        st.stop()
                    st.session_state["battle_locked"] = True

                    ans = q.get("answer")
                    if ch == ans:
                        _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "battle_correct", "q": qi + 1})
                        st.session_state["battle_q_index"] = qi + 1
                        st.session_state["battle_locked"] = False
                        st.rerun()
                    else:
                        _append_jsonl(EVENTS_JSONL, {"ts": _now(), "type": "battle_wrong", "q": qi + 1})
                        st.session_state["battle_hp"] = int(st.session_state.get("battle_hp", BATTLE_HP)) - 1
                        st.session_state["battle_locked"] = False
                        st.toast("MISS ❌", icon="❌")
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# Entry
# -----------------------------
def render() -> None:
    inject_css()
    ensure_state()

    # Decide mode by session
    mode = st.session_state.get("armory_mode", "VOCA_TRAIN")
    cards = load_cards(force_import=False)

    if mode == "VOCA_BATTLE":
        render_battle(cards)
    else:
        render_train(cards)


# For direct run
if __name__ == "__main__":
    st.set_page_config(page_title="SnapQ • VOCA", layout="wide")
    render()
