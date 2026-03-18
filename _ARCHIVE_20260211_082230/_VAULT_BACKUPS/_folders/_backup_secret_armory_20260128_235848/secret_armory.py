from __future__ import annotations

import json
import random
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import streamlit as st

# =========================
# MARKER (for verification)
# =========================
ARMORY_BUILD = "ARMORY_SAFE_V2_TRAIN_TYPE1__2_BATTLES__NO_FORCED_RERUN__5WIN_REWARD__20260128"

def _root() -> Path:
    return Path(__file__).resolve().parents[2]

def _armory_path() -> Path:
    root = _root()
    candidates = [
        root / "data" / "armory" / "secret_armory.json",
        root / "app" / "data" / "armory" / "secret_armory.json",
        root / "data" / "secret_armory.json",
    ]
    for c in candidates:
        if c.exists():
            return c
    p = root / "data" / "armory" / "secret_armory.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        p.write_text("[]", encoding="utf-8")
    return p

ARMORY_PATH = _armory_path()

def _read_items() -> List[Dict[str, Any]]:
    try:
        raw = ARMORY_PATH.read_text(encoding="utf-8", errors="ignore").strip()
        if not raw:
            return []
        data = json.loads(raw)
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict) and isinstance(data.get("items"), list):
            items = data["items"]
        else:
            items = []
        out = [x for x in items if isinstance(x, dict)]

        seen = set()
        dedup = []
        for it in out:
            w = str(it.get("word", "")).strip()
            if not w:
                continue
            k = w.lower()
            if k in seen:
                continue
            seen.add(k)
            it["word"] = w
            dedup.append(it)
        return dedup
    except Exception:
        return []

def _write_items(items: List[Dict[str, Any]]) -> None:
    ARMORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARMORY_PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

# -------- TYPE1 fields (WORD/CORE/USE/KR) --------
def _pick_sentence(text: str, word: str) -> str:
    if not text:
        return ""
    w = (word or "").strip()
    parts = re.split(r"(?<=[\.\?\!;])\s+", text.strip())
    for p in parts:
        if re.search(rf"\b{re.escape(w)}\b", p, flags=re.IGNORECASE):
            return p.strip()
    for p in parts:
        if w.lower() in p.lower():
            return p.strip()
    return text.strip()

def _chunks_from_sentence(sentence: str, word: str) -> List[str]:
    sent = _pick_sentence(sentence or "", word or "")
    if not sent:
        return []
    toks = re.sub(r"\s+", " ", sent).split(" ")
    if not toks:
        return []

    w = (word or "").lower()
    idx = None
    for i, t in enumerate(toks):
        cleaned = re.sub(r"^[^\w]+|[^\w]+$", "", t).lower()
        if cleaned == w or w in cleaned:
            idx = i
            break
    if idx is None:
        return []

    windows = [(1, 1), (1, 0), (0, 1), (2, 1), (1, 2)]
    chunks = []
    for l, r in windows:
        a = max(0, idx - l)
        b = min(len(toks), idx + r + 1)
        c = " ".join(toks[a:b]).strip()
        if c and c not in chunks:
            ct = c.split()
            if len(ct) > 5:
                c = " ".join(ct[:5])
            chunks.append(c)
    return chunks[:6]

def _get_type1_fields(item: Dict[str, Any]) -> Tuple[str, str, str, str]:
    word = str(item.get("word", "")).strip()
    core = str(item.get("core", "") or item.get("chunk", "") or item.get("pattern", "") or "").strip()
    use  = str(item.get("use", "") or item.get("sentence", "") or item.get("source_sentence", "") or "").strip()
    kr   = str(item.get("kr", "") or item.get("meaning", "") or item.get("ko", "") or "").strip()

    if not core:
        chs = _chunks_from_sentence(use, word)
        if chs:
            core = chs[0]
    if not use and core:
        use = core
    return word, core, use, kr

def _blank(text: str, word: str) -> str:
    if not text:
        return ""
    w = (word or "").strip()
    if not w:
        return text
    pat = re.compile(rf"\b{re.escape(w)}\b", flags=re.IGNORECASE)
    if pat.search(text):
        return pat.sub("____", text, count=1)
    return text.replace(w, "____", 1)

# -------- CSS / HUD --------
def _apply_css():
    st.markdown("""
<style>
.main{
  background: radial-gradient(1200px 700px at 20% 0%, #2d3558 0%, #0f1724 45%, #0b1220 100%) !important;
}
h1,h2,h3,h4,h5,h6,p,div,span{ color:#e9edf7; }

.card{
  background:#ffffff;
  color:#0b1220;
  border-radius:18px;
  padding:18px;
  box-shadow:0 10px 24px rgba(0,0,0,.25);
}
.card *{ color:#0b1220 !important; }
.card .sub{ color:#1f2937 !important; font-weight:950 !important; }
.card .label{ font-size:12px; font-weight:950; opacity:.8; margin-top:10px; }
.card .line{ font-size:18px; font-weight:950; margin-top:4px; }
.card .use { font-size:16px; font-weight:850; margin-top:6px; }
.card .kr  { font-size:16px; font-weight:950; margin-top:6px; color:#111827 !important; }

.chip{
  display:inline-block;
  padding:6px 10px;
  border-radius:999px;
  background: rgba(24,160,251,.14);
  border:1px solid rgba(24,160,251,.35);
  color:#0b1220 !important;
  font-weight:950 !important;
}

.hud{
  background: rgba(0,0,0,.42) !important;
  border: 1px solid rgba(255,255,255,.26) !important;
  border-radius:16px;
  padding:12px;
  box-shadow:0 10px 20px rgba(0,0,0,.22);
}
.hud *{ color:#ffffff !important; font-weight: 950 !important; }
.hud h4{ white-space: nowrap !important; margin:0 0 8px 0; }
.hud .row{
  display:flex; justify-content:space-between; align-items:center;
  padding:10px 12px;
  border-radius:12px;
  background: rgba(0,0,0,.55) !important;
  margin-bottom:10px;
  white-space: nowrap !important;
}

.stButton > button{
  background: rgba(0,0,0,.35) !important;
  color: #ffffff !important;
  border: 1px solid rgba(255,255,255,.28) !important;
  border-radius: 14px !important;
  padding: 12px 14px !important;
  font-weight: 950 !important;
  box-shadow: 0 10px 18px rgba(0,0,0,.18) !important;
}
</style>
""", unsafe_allow_html=True)

def _hud(col, mode: str, ammo: int, streak: int, combo: int, hp=None, tleft=None, reward=None):
    with col:
        st.markdown(f"""
<div class="hud">
  <h4>📟 HUD · 키워드</h4>
  <div class="row"><b>🎮 모드</b><span>{mode}</span></div>
  <div class="row"><b>📦 탄약</b><span>{ammo}</span></div>
  <div class="row"><b>🔥 스트릭</b><span>{streak}</span></div>
  <div class="row"><b>⚡ 콤보</b><span>{combo}</span></div>
</div>
""", unsafe_allow_html=True)
        if hp is not None or tleft is not None or reward is not None:
            st.markdown(f"""
<div class="hud" style="margin-top:10px;">
  <h4>📜 미션</h4>
  {("<div class='row'><b>❤️ HP</b><span>"+str(hp)+"</span></div>") if hp is not None else ""}
  {("<div class='row'><b>⏱ 남은시간</b><span>"+str(tleft)+"s</span></div>") if tleft is not None else ""}
  {("<div class='row'><b>🎁 보급상자</b><span>"+str(reward)+"</span></div>") if reward is not None else ""}
</div>
""", unsafe_allow_html=True)

# -------- State --------
def _ensure():
    ss = st.session_state
    ss.setdefault("armory_submode", "TRAIN")

    ss.setdefault("voca_idx", 0)
    ss.setdefault("voca_show_kr", False)
    ss.setdefault("confirm_discard", False)

    ss.setdefault("battle_active", False)
    ss.setdefault("battle_qi", 0)
    ss.setdefault("battle_correct", 0)
    ss.setdefault("battle_wrong", 0)
    ss.setdefault("battle_hp", 3)
    ss.setdefault("battle_combo", 0)
    ss.setdefault("battle_best_combo", 0)
    ss.setdefault("battle_started_at", 0.0)
    ss.setdefault("battle_q_started", 0.0)
    ss.setdefault("battle_seed", random.randint(1, 10_000_000))

    ss.setdefault("battle_kind", "CHUNK_BLANK")
    ss.setdefault("battle_win_streak", 0)
    ss.setdefault("battle_reward_box", 0)

# -------- TRAIN (TYPE1) --------
def _train(items: List[Dict[str, Any]]):
    st.title("🟩 VOCA TRAIN")
    st.caption("CHUNK 타입1: WORD / CORE / USE / 한글")

    if not items:
        st.warning("무기고 저장 단어가 없습니다. (data/armory/secret_armory.json 확인)")
        return

    ss = st.session_state
    n = len(items)
    ss["voca_idx"] = max(0, min(int(ss["voca_idx"]), n - 1))
    it = items[ss["voca_idx"]]

    word, core, use, kr = _get_type1_fields(it)

    left, right = st.columns([3.7, 1.3], gap="large")
    _hud(right, "VOCA-TRAIN", n, int(ss["battle_win_streak"]), 0, reward=int(ss["battle_reward_box"]))

    with left:
        st.markdown(f"""
<div class="card">
  <div class="sub">🪖 VOCA 학습 · 타입1 단어수첩</div>

  <div class="label">WORD</div>
  <div class="line">{word or "(word 없음)"}</div>

  <div class="label">CORE</div>
  <div class="line"><span class="chip">CHUNK</span> · {core or "(core 없음)"}</div>

  <div class="label">USE</div>
  <div class="use">{use or "(use 없음)"}</div>
</div>
""", unsafe_allow_html=True)

        b1,b2,b3 = st.columns(3, gap="large")
        with b1:
            if st.button("📘 뜻 보기", use_container_width=True, key="train_toggle_kr"):
                ss["voca_show_kr"] = not bool(ss["voca_show_kr"])
        with b2:
            if st.button("➡️ 다음", use_container_width=True, key="train_next"):
                ss["voca_show_kr"] = False
                ss["voca_idx"] = (ss["voca_idx"] + 1) % n
        with b3:
            if st.button("🧹 숙달(폐기)", use_container_width=True, key="train_discard"):
                ss["confirm_discard"] = True

        if ss.get("voca_show_kr"):
            st.markdown(f"""
<div class="card" style="margin-top:14px;background:#f7f8fb;">
  <div class="sub">한글 (KR)</div>
  <div class="kr">{kr or "(한글 뜻 없음)"}</div>
</div>
""", unsafe_allow_html=True)

# -------- BATTLE (SAFE V2 유지) --------
def _battle(items: List[Dict[str, Any]]):
    st.title("🔥 VOCA BATTLE")
    st.caption("SAFE V2: 2배틀 + 5연승 보상")

    if not items:
        st.warning("무기고 저장 단어가 없습니다.")
        return

    ss = st.session_state
    kind_labels = {"CHUNK_BLANK": "🧩 CHUNK 빈칸", "MEANING_4CHOICE": "📘 뜻 4지선다"}
    new_kind = st.radio("battle_kind", ["CHUNK_BLANK","MEANING_4CHOICE"],
                        format_func=lambda x: kind_labels.get(x,x),
                        index=0 if ss.get("battle_kind","CHUNK_BLANK")=="CHUNK_BLANK" else 1,
                        label_visibility="collapsed", key="battle_kind_radio")
    if new_kind != ss.get("battle_kind"):
        ss["battle_kind"] = new_kind
        ss["battle_active"] = False

    QTIME = 8
    QTOT = min(10, len(items))

    if not ss.get("battle_active"):
        ss["battle_active"] = True
        ss["battle_qi"] = 0
        ss["battle_correct"] = 0
        ss["battle_wrong"] = 0
        ss["battle_hp"] = 3
        ss["battle_combo"] = 0
        ss["battle_best_combo"] = 0
        ss["battle_started_at"] = time.time()
        ss["battle_q_started"] = time.time()
        ss["battle_seed"] = random.randint(1, 10_000_000)

    rnd = random.Random(int(ss["battle_seed"]))
    pool = items[:]
    rnd.shuffle(pool)
    pool = pool[:QTOT]

    qi = int(ss["battle_qi"])
    if qi >= len(pool) or int(ss["battle_hp"]) <= 0:
        correct = int(ss["battle_correct"])
        rate = int((correct / max(1, len(pool))) * 100)
        won = (rate >= 80) and (int(ss["battle_hp"]) > 0)
        if won:
            ss["battle_win_streak"] = int(ss["battle_win_streak"]) + 1
            msg = "🏆 승리! → 연승 +1"
        else:
            ss["battle_win_streak"] = 0
            msg = "💥 패배… → 연승 초기화"
        if int(ss["battle_win_streak"]) >= 5:
            ss["battle_reward_box"] = int(ss["battle_reward_box"]) + 1
            ss["battle_win_streak"] = 0
            msg += "  🎁 5연승 보상: 보급상자 +1!"

        st.markdown(f"""
<div class="card">
  <div class="sub">🏁 전투 결과</div>
  <div style="height:10px;"></div>
  <div class="line">정답률 · {rate}%</div>
  <div class="kr">{msg}</div>
</div>
""", unsafe_allow_html=True)

        if st.button("🔁 다시 전장", use_container_width=True, key="battle_again"):
            ss["battle_active"] = False
        return

    it = pool[qi]
    word, core, use, kr = _get_type1_fields(it)

    elapsed = time.time() - float(ss["battle_q_started"])
    tleft = max(0, int(QTIME - elapsed))

    left,right = st.columns([3.7,1.3], gap="large")
    _hud(right, "VOCA-BATTLE", len(items), int(ss["battle_win_streak"]), int(ss["battle_combo"]),
         hp=int(ss["battle_hp"]), tleft=tleft, reward=int(ss["battle_reward_box"]))

    kind = ss.get("battle_kind","CHUNK_BLANK")
    if kind == "MEANING_4CHOICE" and not kr:
        kind = "CHUNK_BLANK"

    if kind == "MEANING_4CHOICE":
        all_kr = []
        for x in items:
            _, _, _, xkr = _get_type1_fields(x)
            if xkr:
                all_kr.append(xkr)
        all_kr = list(dict.fromkeys(all_kr))
        distract = [m for m in all_kr if m != kr]
        rnd2 = random.Random(int(ss["battle_seed"]) + qi + 777)
        rnd2.shuffle(distract)
        opts = [kr] + distract[:3]
        rnd2.shuffle(opts)

        prompt = f"WORD · {word}"
        answer = kr
        check = lambda c: c == answer
        chip = "MEANING"
    else:
        prompt = _blank(core or use, word)
        all_words = [str(x.get("word","")).strip() for x in items if str(x.get("word","")).strip()]
        distract = [w for w in all_words if w.lower() != word.lower()]
        rnd2 = random.Random(int(ss["battle_seed"]) + qi)
        rnd2.shuffle(distract)
        opts = [word] + distract[:3]
        rnd2.shuffle(opts)

        answer = word
        check = lambda c: c.lower() == answer.lower()
        chip = "CHUNK"

    with left:
        st.markdown(f"""
<div class="card">
  <div class="sub">🎯 미션 {qi+1}/{len(pool)}</div>
  <div class="label">{chip}</div>
  <div class="line">{prompt}</div>
</div>
""", unsafe_allow_html=True)

        if tleft <= 0:
            ss["battle_wrong"] += 1
            ss["battle_qi"] += 1
            ss["battle_hp"] -= 1
            ss["battle_combo"] = 0
            ss["battle_q_started"] = time.time()
            st.toast("⏰ 시간 초과!")
            return

        g1,g2 = st.columns(2, gap="large")
        clicked = None
        for i,opt in enumerate(opts):
            with (g1 if i % 2 == 0 else g2):
                if st.button(opt, use_container_width=True, key=f"bopt_{chip}_{qi}_{i}"):
                    clicked = opt

        if clicked is not None:
            if check(clicked):
                ss["battle_correct"] += 1
                ss["battle_combo"] += 1
                ss["battle_best_combo"] = max(ss["battle_best_combo"], ss["battle_combo"])
            else:
                ss["battle_wrong"] += 1
                ss["battle_hp"] -= 1
                ss["battle_combo"] = 0
            ss["battle_qi"] += 1
            ss["battle_q_started"] = time.time()

def render():
    _ensure()
    _apply_css()

    st.caption(f"✅ LOADED: {ARMORY_BUILD} · {__file__}")

    items = _read_items()

    t1,t2 = st.columns(2, gap="large")
    with t1:
        if st.button("🟩 TRAIN", use_container_width=True, key="top_train"):
            st.session_state["armory_submode"] = "TRAIN"
            st.session_state["battle_active"] = False
    with t2:
        if st.button("🔥 BATTLE", use_container_width=True, key="top_battle"):
            st.session_state["armory_submode"] = "BATTLE"
            st.session_state["battle_active"] = False

    if str(st.session_state.get("armory_submode","TRAIN")).upper() == "BATTLE":
        _battle(items)
    else:
        _train(items)
