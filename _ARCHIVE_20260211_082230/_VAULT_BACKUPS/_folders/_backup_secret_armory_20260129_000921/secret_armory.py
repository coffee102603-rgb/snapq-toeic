# ============================================================
# SnapQ TOEIC - Secret Armory (TRAIN / BATTLE)
# - TRAIN: single column (NO right HUD)
# - BATTLE: 2 columns + right HUD
# ============================================================

from __future__ import annotations

import json
import time
from dataclasses import dataclass
from datetime import datetime, date
from pathlib import Path
from typing import Any, Dict, List, Optional

import streamlit as st


# -----------------------------
# Path / Data IO
# -----------------------------
ROOT = Path(__file__).resolve()
# .../app/arenas/secret_armory.py -> project root is 3 levels up (snapq_toeic)
PROJECT_ROOT = ROOT.parents[3] if len(ROOT.parents) >= 4 else ROOT.parents[0]

DATA_DIR = PROJECT_ROOT / "data"
ARMORY_DIR = DATA_DIR / "armory"
ARMORY_DIR.mkdir(parents=True, exist_ok=True)

# Default storage (safe, standalone)
ARMORY_WORDS_JSON = ARMORY_DIR / "secret_armory_words.json"
ARMORY_EVENTS_JSONL = ARMORY_DIR / "secret_armory_events.jsonl"


def _now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _today_str() -> str:
    return date.today().isoformat()


def _safe_read_json(path: Path, default: Any) -> Any:
    try:
        if not path.exists():
            return default
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _safe_write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(payload, ensure_ascii=False)
    with path.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


# -----------------------------
# Model
# -----------------------------
@dataclass
class ArmoryWord:
    word: str
    meaning_ko: str = ""
    example: str = ""
    note: str = ""
    tag: str = ""
    added_at: str = ""
    last_seen_at: str = ""
    seen_count: int = 0
    correct: int = 0
    wrong: int = 0

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "ArmoryWord":
        return ArmoryWord(
            word=str(d.get("word", "")).strip(),
            meaning_ko=str(d.get("meaning_ko", "")).strip(),
            example=str(d.get("example", "")).strip(),
            note=str(d.get("note", "")).strip(),
            tag=str(d.get("tag", "")).strip(),
            added_at=str(d.get("added_at", "")).strip(),
            last_seen_at=str(d.get("last_seen_at", "")).strip(),
            seen_count=int(d.get("seen_count", 0) or 0),
            correct=int(d.get("correct", 0) or 0),
            wrong=int(d.get("wrong", 0) or 0),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "word": self.word,
            "meaning_ko": self.meaning_ko,
            "example": self.example,
            "note": self.note,
            "tag": self.tag,
            "added_at": self.added_at,
            "last_seen_at": self.last_seen_at,
            "seen_count": self.seen_count,
            "correct": self.correct,
            "wrong": self.wrong,
        }


def load_armory_words() -> List[ArmoryWord]:
    raw = _safe_read_json(ARMORY_WORDS_JSON, default={"words": []})
    items = raw.get("words", []) if isinstance(raw, dict) else []
    words: List[ArmoryWord] = []
    for it in items:
        try:
            w = ArmoryWord.from_dict(it)
            if w.word:
                words.append(w)
        except Exception:
            continue
    # de-dup by word (keep first)
    seen = set()
    deduped = []
    for w in words:
        key = w.word.lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(w)
    return deduped


def save_armory_words(words: List[ArmoryWord]) -> None:
    payload = {"updated_at": _now_str(), "words": [w.to_dict() for w in words]}
    _safe_write_json(ARMORY_WORDS_JSON, payload)


# -----------------------------
# UI Helpers / Style
# -----------------------------
def inject_css() -> None:
    st.markdown(
        """
<style>
/* ---- Base ---- */
.snapq-page { max-width: 1200px; margin: 0 auto; padding-bottom: 16px; }
.snapq-title {
  font-weight: 900; letter-spacing: -0.6px;
  font-size: 30px; line-height: 1.1; margin: 8px 0 2px 0;
}
.snapq-sub { opacity: 0.9; margin: 0 0 12px 0; }

/* ---- Cards ---- */
.card {
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.10);
  padding: 14px 14px;
  background: rgba(255,255,255,0.05);
  box-shadow: 0 6px 18px rgba(0,0,0,0.25);
}
.card h4 { margin: 0 0 6px 0; font-size: 16px; }
.mini { opacity: 0.85; font-size: 13px; }
.badge {
  display:inline-block; padding: 4px 10px; border-radius: 999px;
  border: 1px solid rgba(255,255,255,0.18);
  background: rgba(0,0,0,0.15);
  font-size: 12px; font-weight: 800;
}

/* ---- TRAIN look (single column) ---- */
.train-hero {
  border: 1px solid rgba(180,130,255,0.28);
  background: linear-gradient(135deg, rgba(180,130,255,0.18), rgba(20,20,28,0.02));
}
.train-word {
  font-size: 18px; font-weight: 900;
}
.train-meaning {
  font-size: 14px; font-weight: 800; opacity: 0.95;
}

/* ---- BATTLE look (2col + HUD) ---- */
.battle-hero {
  border: 1px solid rgba(120,210,255,0.26);
  background: linear-gradient(135deg, rgba(120,210,255,0.18), rgba(20,20,28,0.02));
}
.hud {
  position: sticky; top: 12px;
  border: 1px solid rgba(120,210,255,0.20);
  background: rgba(10,12,16,0.60);
  border-radius: 16px;
  padding: 12px 12px;
}
.hud .hud-title { font-weight: 900; margin-bottom: 6px; }
.hud .kpi { font-weight: 900; font-size: 20px; }
.hud .label { font-size: 12px; opacity: 0.85; }

/* ---- Timer shake (battle only) ---- */
@keyframes shake {
  0% { transform: translateX(0); }
  20% { transform: translateX(-2px); }
  40% { transform: translateX(2px); }
  60% { transform: translateX(-2px); }
  80% { transform: translateX(2px); }
  100% { transform: translateX(0); }
}
.shake { animation: shake 0.25s linear infinite; }

/* Buttons */
.stButton>button { font-weight: 800; border-radius: 12px; }
</style>
""",
        unsafe_allow_html=True,
    )


def _ensure_state() -> None:
    st.session_state.setdefault("armory_mode", "TRAIN")  # TRAIN / BATTLE
    st.session_state.setdefault("armory_query", "")
    st.session_state.setdefault("armory_tag", "ALL")
    st.session_state.setdefault("armory_sort", "RECENT")
    st.session_state.setdefault("armory_selected_word", None)

    # battle timer state
    st.session_state.setdefault("armory_battle_running", False)
    st.session_state.setdefault("armory_battle_started_at", None)  # epoch
    st.session_state.setdefault("armory_battle_limit_sec", 60)
    st.session_state.setdefault("armory_battle_last_tick", None)

    # daily counter (session-local)
    st.session_state.setdefault("armory_today_seen", 0)
    st.session_state.setdefault("armory_today_correct", 0)
    st.session_state.setdefault("armory_today_wrong", 0)
    st.session_state.setdefault("armory_today_date", _today_str())


def _roll_daily_if_needed() -> None:
    if st.session_state.get("armory_today_date") != _today_str():
        st.session_state["armory_today_date"] = _today_str()
        st.session_state["armory_today_seen"] = 0
        st.session_state["armory_today_correct"] = 0
        st.session_state["armory_today_wrong"] = 0


def _get_all_tags(words: List[ArmoryWord]) -> List[str]:
    tags = sorted({w.tag.strip() for w in words if w.tag.strip()})
    return ["ALL"] + tags


def _apply_filters(words: List[ArmoryWord], query: str, tag: str) -> List[ArmoryWord]:
    q = (query or "").strip().lower()
    out = []
    for w in words:
        if tag != "ALL" and (w.tag or "").strip() != tag:
            continue
        if not q:
            out.append(w)
            continue
        hay = " ".join([w.word, w.meaning_ko, w.example, w.note, w.tag]).lower()
        if q in hay:
            out.append(w)
    return out


def _apply_sort(words: List[ArmoryWord], sort_key: str) -> List[ArmoryWord]:
    if sort_key == "A→Z":
        return sorted(words, key=lambda x: x.word.lower())
    if sort_key == "MOST_WRONG":
        return sorted(words, key=lambda x: (x.wrong, x.seen_count), reverse=True)
    if sort_key == "MOST_SEEN":
        return sorted(words, key=lambda x: x.seen_count, reverse=True)
    # RECENT default: by added_at (fallback: keep order)
    def _ts(s: str) -> float:
        try:
            return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").timestamp()
        except Exception:
            return 0.0
    return sorted(words, key=lambda x: _ts(x.added_at), reverse=True)


def _upsert_word(words: List[ArmoryWord], new_word: ArmoryWord) -> List[ArmoryWord]:
    key = new_word.word.strip().lower()
    if not key:
        return words
    out = []
    replaced = False
    for w in words:
        if w.word.strip().lower() == key:
            out.append(new_word)
            replaced = True
        else:
            out.append(w)
    if not replaced:
        out.insert(0, new_word)
    return out


def _delete_word(words: List[ArmoryWord], word_str: str) -> List[ArmoryWord]:
    key = (word_str or "").strip().lower()
    return [w for w in words if w.word.strip().lower() != key]


# -----------------------------
# BATTLE Timer
# -----------------------------
def _battle_time_left() -> int:
    if not st.session_state.get("armory_battle_running"):
        return int(st.session_state.get("armory_battle_limit_sec", 60))
    started = st.session_state.get("armory_battle_started_at")
    if not started:
        return int(st.session_state.get("armory_battle_limit_sec", 60))
    limit = int(st.session_state.get("armory_battle_limit_sec", 60))
    elapsed = int(time.time() - float(started))
    return max(0, limit - elapsed)


def _battle_tick_if_running() -> None:
    if not st.session_state.get("armory_battle_running"):
        return
    left = _battle_time_left()
    if left <= 0:
        st.session_state["armory_battle_running"] = False
        _append_jsonl(
            ARMORY_EVENTS_JSONL,
            {"ts": _now_str(), "type": "battle_timeout", "limit_sec": st.session_state.get("armory_battle_limit_sec", 60)},
        )
        st.toast("⏰ TIME OUT! 전장 종료 (BATTLE)", icon="⏰")
        return


# -----------------------------
# TRAIN UI (single column)
# -----------------------------
def render_train(words_all: List[ArmoryWord]) -> None:
    st.markdown('<div class="snapq-page">', unsafe_allow_html=True)
    st.markdown('<div class="card train-hero">', unsafe_allow_html=True)
    st.markdown('<div class="snapq-title">🟣 Secret Armory — TRAIN</div>', unsafe_allow_html=True)
    st.markdown('<div class="snapq-sub">훈련 모드: 단일열 집중 / 우측 HUD 없음</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    tags = _get_all_tags(words_all)

    c1, c2, c3 = st.columns([2.2, 1.2, 1.1])
    with c1:
        st.session_state["armory_query"] = st.text_input(
            "🔎 검색 (단어/뜻/예문/메모/태그)", value=st.session_state.get("armory_query", ""), key="armory_query_train"
        )
    with c2:
        st.session_state["armory_tag"] = st.selectbox(
            "🏷️ 태그", options=tags, index=tags.index(st.session_state.get("armory_tag", "ALL")) if st.session_state.get("armory_tag", "ALL") in tags else 0,
            key="armory_tag_train",
        )
    with c3:
        st.session_state["armory_sort"] = st.selectbox(
            "↕️ 정렬", options=["RECENT", "A→Z", "MOST_SEEN", "MOST_WRONG"],
            index=["RECENT", "A→Z", "MOST_SEEN", "MOST_WRONG"].index(st.session_state.get("armory_sort", "RECENT")),
            key="armory_sort_train",
        )

    filtered = _apply_filters(words_all, st.session_state["armory_query"], st.session_state["armory_tag"])
    filtered = _apply_sort(filtered, st.session_state["armory_sort"])

    top = st.columns([1.2, 1.2, 1.6])
    with top[0]:
        st.markdown(f'<div class="badge">총 무기: {len(words_all)}</div>', unsafe_allow_html=True)
    with top[1]:
        st.markdown(f'<div class="badge">표시 중: {len(filtered)}</div>', unsafe_allow_html=True)
    with top[2]:
        with st.expander("➕ 신규 무기 등록 (단어 추가)", expanded=False):
            w = st.text_input("Word", value="")
            m = st.text_input("Meaning (KO)", value="")
            ex = st.text_area("Example (EN)", value="", height=80)
            note = st.text_area("Note", value="", height=80)
            tag = st.text_input("Tag (선택)", value="")
            add = st.button("✅ 등록", use_container_width=True)
            if add:
                w2 = (w or "").strip()
                if not w2:
                    st.warning("단어(Word)는 필수입니다.")
                else:
                    nw = ArmoryWord(
                        word=w2,
                        meaning_ko=(m or "").strip(),
                        example=(ex or "").strip(),
                        note=(note or "").strip(),
                        tag=(tag or "").strip(),
                        added_at=_now_str(),
                        last_seen_at="",
                        seen_count=0,
                        correct=0,
                        wrong=0,
                    )
                    updated = _upsert_word(words_all, nw)
                    save_armory_words(updated)
                    _append_jsonl(ARMORY_EVENTS_JSONL, {"ts": _now_str(), "type": "add_word", "word": w2})
                    st.toast("무기 등록 완료 ✅", icon="✅")
                    st.rerun()

    st.markdown("")

    if len(filtered) == 0:
        st.info("표시할 무기가 없습니다. 검색/태그를 바꾸거나 새 무기를 등록해보세요.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    # List cards (single column)
    for w in filtered[:250]:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown(f'<div class="train-word">{w.word}</div>', unsafe_allow_html=True)
        if w.meaning_ko:
            st.markdown(f'<div class="train-meaning">뜻: {w.meaning_ko}</div>', unsafe_allow_html=True)
        if w.example:
            st.markdown(f'<div class="mini">예문: {w.example}</div>', unsafe_allow_html=True)
        if w.note:
            st.markdown(f'<div class="mini">메모: {w.note}</div>', unsafe_allow_html=True)
        meta = f"seen {w.seen_count} / ✅ {w.correct} / ❌ {w.wrong}"
        if w.tag:
            meta += f" / tag: {w.tag}"
        st.markdown(f'<div class="mini">{meta}</div>', unsafe_allow_html=True)

        colA, colB, colC = st.columns([1.1, 1.1, 1.1])
        with colA:
            if st.button("👀 봤음(+1)", key=f"train_seen_{w.word}", use_container_width=True):
                w.last_seen_at = _now_str()
                w.seen_count += 1
                st.session_state["armory_today_seen"] += 1
                updated = _upsert_word(words_all, w)
                save_armory_words(updated)
                _append_jsonl(ARMORY_EVENTS_JSONL, {"ts": _now_str(), "type": "train_seen", "word": w.word})
                st.rerun()
        with colB:
            if st.button("✅ 암기됨(+1)", key=f"train_ok_{w.word}", use_container_width=True):
                w.last_seen_at = _now_str()
                w.seen_count += 1
                w.correct += 1
                st.session_state["armory_today_seen"] += 1
                st.session_state["armory_today_correct"] += 1
                updated = _upsert_word(words_all, w)
                save_armory_words(updated)
                _append_jsonl(ARMORY_EVENTS_JSONL, {"ts": _now_str(), "type": "train_correct", "word": w.word})
                st.rerun()
        with colC:
            with st.popover("🧹 삭제/수정", use_container_width=True):
                st.caption("삭제는 즉시 반영됩니다. (안전 백업은 PowerShell에서 이미 생성됨)")
                new_m = st.text_input("뜻 수정", value=w.meaning_ko, key=f"edit_m_{w.word}")
                new_ex = st.text_area("예문 수정", value=w.example, height=70, key=f"edit_ex_{w.word}")
                new_note = st.text_area("메모 수정", value=w.note, height=70, key=f"edit_note_{w.word}")
                new_tag = st.text_input("태그 수정", value=w.tag, key=f"edit_tag_{w.word}")
                cX, cY = st.columns([1, 1])
                with cX:
                    if st.button("💾 저장", key=f"save_{w.word}", use_container_width=True):
                        w.meaning_ko = (new_m or "").strip()
                        w.example = (new_ex or "").strip()
                        w.note = (new_note or "").strip()
                        w.tag = (new_tag or "").strip()
                        updated = _upsert_word(words_all, w)
                        save_armory_words(updated)
                        _append_jsonl(ARMORY_EVENTS_JSONL, {"ts": _now_str(), "type": "edit_word", "word": w.word})
                        st.toast("저장 완료 💾", icon="💾")
                        st.rerun()
                with cY:
                    if st.button("🗑️ 삭제", key=f"del_{w.word}", use_container_width=True):
                        updated = _delete_word(words_all, w.word)
                        save_armory_words(updated)
                        _append_jsonl(ARMORY_EVENTS_JSONL, {"ts": _now_str(), "type": "delete_word", "word": w.word})
                        st.toast("삭제 완료 🗑️", icon="🗑️")
                        st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("")

    st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# BATTLE UI (2 columns + HUD)
# -----------------------------
def render_battle(words_all: List[ArmoryWord]) -> None:
    _battle_tick_if_running()

    st.markdown('<div class="snapq-page">', unsafe_allow_html=True)
    st.markdown('<div class="card battle-hero">', unsafe_allow_html=True)
    st.markdown('<div class="snapq-title">🔵 Secret Armory — BATTLE</div>', unsafe_allow_html=True)
    st.markdown('<div class="snapq-sub">전장 모드: 2컬럼 + 우측 HUD 유지</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # layout: left main / right HUD
    left, right = st.columns([2.15, 1.0], gap="large")

    # --- Right HUD ---
    with right:
        _roll_daily_if_needed()
        left_sec = _battle_time_left()
        shaky = "shake" if (st.session_state.get("armory_battle_running") and left_sec <= 15) else ""
        st.markdown(f'<div class="hud {shaky}">', unsafe_allow_html=True)
        st.markdown('<div class="hud-title">🎛️ BATTLE HUD</div>', unsafe_allow_html=True)

        st.markdown(f'<div class="label">남은 시간</div><div class="kpi">{left_sec}s</div>', unsafe_allow_html=True)
        st.markdown("<hr style='opacity:0.15;'>", unsafe_allow_html=True)

        st.markdown(f'<div class="label">총 무기</div><div class="kpi">{len(words_all)}</div>', unsafe_allow_html=True)
        st.markdown("<hr style='opacity:0.15;'>", unsafe_allow_html=True)

        st.markdown(f'<div class="label">오늘 본 무기</div><div class="kpi">{st.session_state.get("armory_today_seen", 0)}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="mini">✅ {st.session_state.get("armory_today_correct", 0)} / ❌ {st.session_state.get("armory_today_wrong", 0)}</div>', unsafe_allow_html=True)

        st.markdown("<hr style='opacity:0.15;'>", unsafe_allow_html=True)

        # controls
        limit = st.selectbox("⏱️ 제한시간", options=[40, 60, 90, 120], index=[40,60,90,120].index(int(st.session_state.get("armory_battle_limit_sec",60))), key="armory_limit_select")
        st.session_state["armory_battle_limit_sec"] = int(limit)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("▶ START", use_container_width=True):
                st.session_state["armory_battle_running"] = True
                st.session_state["armory_battle_started_at"] = time.time()
                _append_jsonl(ARMORY_EVENTS_JSONL, {"ts": _now_str(), "type": "battle_start", "limit_sec": int(limit)})
                st.rerun()
        with c2:
            if st.button("⏸ STOP", use_container_width=True):
                st.session_state["armory_battle_running"] = False
                _append_jsonl(ARMORY_EVENTS_JSONL, {"ts": _now_str(), "type": "battle_stop"})
                st.rerun()

        if st.button("🔁 RESET (새 전장)", use_container_width=True):
            st.session_state["armory_battle_running"] = False
            st.session_state["armory_battle_started_at"] = None
            st.session_state["armory_selected_word"] = None
            _append_jsonl(ARMORY_EVENTS_JSONL, {"ts": _now_str(), "type": "battle_reset"})
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # --- Left main panel ---
    with left:
        tags = _get_all_tags(words_all)

        top = st.columns([2.0, 1.0, 1.0])
        with top[0]:
            st.session_state["armory_query"] = st.text_input(
                "🔎 BATTLE 검색 (단어/뜻/예문/메모/태그)", value=st.session_state.get("armory_query", ""), key="armory_query_battle"
            )
        with top[1]:
            st.session_state["armory_tag"] = st.selectbox(
                "🏷️ 태그", options=tags,
                index=tags.index(st.session_state.get("armory_tag", "ALL")) if st.session_state.get("armory_tag", "ALL") in tags else 0,
                key="armory_tag_battle",
            )
        with top[2]:
            st.session_state["armory_sort"] = st.selectbox(
                "↕️ 정렬", options=["RECENT", "A→Z", "MOST_SEEN", "MOST_WRONG"],
                index=["RECENT", "A→Z", "MOST_SEEN", "MOST_WRONG"].index(st.session_state.get("armory_sort", "RECENT")),
                key="armory_sort_battle",
            )

        filtered = _apply_filters(words_all, st.session_state["armory_query"], st.session_state["armory_tag"])
        filtered = _apply_sort(filtered, st.session_state["armory_sort"])

        st.markdown(f'<div class="badge">표시 중: {len(filtered)}</div>', unsafe_allow_html=True)
        st.markdown("")

        if len(filtered) == 0:
            st.info("표시할 무기가 없습니다. 검색/태그를 바꿔보세요.")
        else:
            # pick panel
            pick_cols = st.columns([1.4, 1.2, 1.0])
            with pick_cols[0]:
                options = [w.word for w in filtered[:200]]
                default_idx = 0
                cur = st.session_state.get("armory_selected_word")
                if cur in options:
                    default_idx = options.index(cur)
                selected = st.selectbox("🎯 타겟 선택", options=options, index=default_idx, key="battle_target_select")
                st.session_state["armory_selected_word"] = selected

            # fetch word object
            chosen: Optional[ArmoryWord] = None
            for w in filtered:
                if w.word == st.session_state["armory_selected_word"]:
                    chosen = w
                    break

            if chosen:
                st.markdown('<div class="card">', unsafe_allow_html=True)
                st.markdown(f'<div class="train-word">{chosen.word}</div>', unsafe_allow_html=True)

                # “전장” 느낌: 뜻은 펼쳐보기로 (학습자 클릭)
                with st.expander("🧠 뜻 / 메모 / 예문 펼치기", expanded=False):
                    if chosen.meaning_ko:
                        st.markdown(f"**뜻:** {chosen.meaning_ko}")
                    if chosen.note:
                        st.markdown(f"**메모:** {chosen.note}")
                    if chosen.example:
                        st.markdown(f"**예문:** {chosen.example}")

                # Battle actions
                b1, b2, b3 = st.columns([1.1, 1.1, 1.1])
                with b1:
                    if st.button("👀 조준(봤음)", use_container_width=True):
                        if st.session_state.get("armory_battle_running") and _battle_time_left() <= 0:
                            st.warning("시간 종료!")
                        else:
                            chosen.last_seen_at = _now_str()
                            chosen.seen_count += 1
                            st.session_state["armory_today_seen"] += 1
                            updated = _upsert_word(words_all, chosen)
                            save_armory_words(updated)
                            _append_jsonl(ARMORY_EVENTS_JSONL, {"ts": _now_str(), "type": "battle_seen", "word": chosen.word})
                            st.rerun()
                with b2:
                    if st.button("✅ HIT (정답)", use_container_width=True):
                        if st.session_state.get("armory_battle_running") and _battle_time_left() <= 0:
                            st.warning("시간 종료!")
                        else:
                            chosen.last_seen_at = _now_str()
                            chosen.seen_count += 1
                            chosen.correct += 1
                            st.session_state["armory_today_seen"] += 1
                            st.session_state["armory_today_correct"] += 1
                            updated = _upsert_word(words_all, chosen)
                            save_armory_words(updated)
                            _append_jsonl(ARMORY_EVENTS_JSONL, {"ts": _now_str(), "type": "battle_correct", "word": chosen.word})
                            st.toast("HIT ✅", icon="✅")
                            st.rerun()
                with b3:
                    if st.button("❌ MISS (오답)", use_container_width=True):
                        if st.session_state.get("armory_battle_running") and _battle_time_left() <= 0:
                            st.warning("시간 종료!")
                        else:
                            chosen.last_seen_at = _now_str()
                            chosen.seen_count += 1
                            chosen.wrong += 1
                            st.session_state["armory_today_seen"] += 1
                            st.session_state["armory_today_wrong"] += 1
                            updated = _upsert_word(words_all, chosen)
                            save_armory_words(updated)
                            _append_jsonl(ARMORY_EVENTS_JSONL, {"ts": _now_str(), "type": "battle_wrong", "word": chosen.word})
                            st.toast("MISS ❌", icon="❌")
                            st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


# -----------------------------
# Main Entrypoint
# -----------------------------
def app() -> None:
    inject_css()
    _ensure_state()

    words_all = load_armory_words()

    # mode switch (top) - compact
    mode = st.radio(
        "모드 선택",
        options=["TRAIN", "BATTLE"],
        horizontal=True,
        index=0 if st.session_state.get("armory_mode", "TRAIN") == "TRAIN" else 1,
        key="armory_mode_radio",
    )
    st.session_state["armory_mode"] = mode

    # IMPORTANT: TRAIN must be single column. BATTLE uses 2col + HUD.
    if mode == "TRAIN":
        render_train(words_all)
    else:
        render_battle(words_all)


# Streamlit direct run compatibility
if __name__ == "__main__":
    st.set_page_config(page_title="SnapQ - Secret Armory", layout="wide")
    app()
