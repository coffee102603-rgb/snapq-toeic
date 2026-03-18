from __future__ import annotations

import json
import random
import re
import time
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st

# =========================
# MARKER (for verification)
# =========================
ARMORY_BUILD = "CHUNK_ARMORY_FULLREPLACE_V1"

def _root() -> Path:
    # .../snapq_toeic/app/arenas/secret_armory.py -> project root is parents[2]
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
        # dedupe by word
        seen = set()
        dedup = []
        for it in out:
            w = str(it.get("word","")).strip()
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

def _chunks(item: Dict[str, Any]) -> List[str]:
    # prefer saved chunks
    ch = item.get("chunks")
    if isinstance(ch, list) and ch:
        out = [str(x).strip() for x in ch if str(x).strip()]
        if out:
            return out[:6]

    word = str(item.get("word","")).strip()
    sent = str(item.get("sentence","") or item.get("source_sentence","") or "").strip()
    s = _pick_sentence(sent, word)
    if not s:
        return [word] if word else []

    toks = re.sub(r"\s+", " ", s).split(" ")
    if not toks:
        return [word] if word else []

    w = word.lower()
    idx = None
    for i,t in enumerate(toks):
        cleaned = re.sub(r"^[^\w]+|[^\w]+$", "", t).lower()
        if cleaned == w or w in cleaned:
            idx = i; break
    if idx is None:
        return [word] if word else []

    windows = [(1,1),(1,0),(0,1),(2,1),(1,2)]
    chunks = []
    for l,r in windows:
        a = max(0, idx-l); b = min(len(toks), idx+r+1)
        c = " ".join(toks[a:b]).strip()
        if c and c not in chunks:
            # trim to max 4 tokens
            ct = c.split()
            if len(ct) > 4:
                c = " ".join(ct[:4])
            chunks.append(c)
    return chunks[:6]

def _blank(chunk: str, word: str) -> str:
    if not chunk:
        return ""
    w = (word or "").strip()
    if not w:
        return chunk
    pat = re.compile(rf"\b{re.escape(w)}\b", flags=re.IGNORECASE)
    if pat.search(chunk):
        return pat.sub("____", chunk, count=1)
    return chunk.replace(w, "____", 1)

def _apply_css():
    st.markdown("""
<style>
/* ===== SNAPQ ARMORY CSS (READABILITY v1) ===== */
.main{
  background: radial-gradient(1200px 700px at 20% 0%, #2d3558 0%, #0f1724 45%, #0b1220 100%) !important;
}

/* Global default text (outside cards) */
h1,h2,h3,h4,h5,h6,p,div,span{ color:#e9edf7; }

/* White card */
.card{
  background:#ffffff;
  color:#0b1220;
  border-radius:18px;
  padding:18px;
  box-shadow:0 10px 24px rgba(0,0,0,.25);
}

/* Card text must be DARK and strong */
.card *{
  color:#0b1220 !important;
}
.card .sub{
  color:#1f2937 !important;
  font-weight:900 !important;
}
.card .big{
  font-size:22px;
  font-weight:950 !important;
  color:#0b1220 !important;
}
.card .muted{
  color:#374151 !important;
  font-weight:900 !important;
}

/* CHUNK chip */
.chip{
  display:inline-block;
  padding:6px 10px;
  border-radius:999px;
  background: rgba(24,160,251,.14);
  border:1px solid rgba(24,160,251,.35);
  color:#0b1220 !important;
  font-weight:950 !important;
}

/* HUD stronger */
.hud{
  background: rgba(255,255,255,.10);
  border:1px solid rgba(255,255,255,.18);
  border-radius:16px;
  padding:12px;
  box-shadow:0 10px 20px rgba(0,0,0,.22);
}
.hud h4{ color:#ffffff !important; font-weight:950 !important; margin:0 0 8px 0; }
.hud .row{
  display:flex; justify-content:space-between; align-items:center;
  padding:10px 12px;
  border-radius:12px;
  background: rgba(0,0,0,.28);
  margin-bottom:10px;
}
.hud .row b{ color:#ffffff !important; font-weight:950 !important; }
.hud .row span{ color:#ffffff !important; font-weight:950 !important; }

/* Buttons text */
.stButton > button{
  font-weight:900 !important;
}
/* ===== HUD CONTRAST BOOST v1 ===== */
.hud{ background: rgba(0,0,0,.35) !important; border: 1px solid rgba(255,255,255,.22) !important; }
.hud h4{ color:#ffffff !important; font-weight:950 !important; }
.hud .row{ background: rgba(0,0,0,.45) !important; }
.hud .row b, .hud .row span{ color:#ffffff !important; font-weight:950 !important; }
/* ===== READABILITY BOOST v2 ===== */

/* 1) Big title + caption */
h1, h2 {
  color: #ffffff !important;
  font-weight: 950 !important;
  text-shadow: 0 2px 10px rgba(0,0,0,.45) !important;
}
[data-testid="stCaptionContainer"] p, .stCaption, small {
  color: rgba(255,255,255,.92) !important;
  font-weight: 800 !important;
  text-shadow: 0 2px 10px rgba(0,0,0,.35) !important;
}

/* 2) Make top TRAIN/BATTLE buttons look like real tabs */
.stButton > button{
  background: rgba(0,0,0,.35) !important;
  color: #ffffff !important;
  border: 1px solid rgba(255,255,255,.28) !important;
  border-radius: 14px !important;
  padding: 12px 14px !important;
  font-weight: 950 !important;
  box-shadow: 0 10px 18px rgba(0,0,0,.18) !important;
}
.stButton > button:hover{
  background: rgba(0,0,0,.50) !important;
  border: 1px solid rgba(255,255,255,.42) !important;
}

/* 3) HUD: no weird wrap + higher contrast */
.hud{
  background: rgba(0,0,0,.42) !important;
  border: 1px solid rgba(255,255,255,.26) !important;
}
.hud *{
  color:#ffffff !important;
  font-weight: 950 !important;
}
.hud h4{
  white-space: nowrap !important;
  letter-spacing: .2px !important;
}
.hud .row{
  background: rgba(0,0,0,.55) !important;
  white-space: nowrap !important;
}
.hud .row b, .hud .row span{
  white-space: nowrap !important;
}

/* 4) Fix faint Streamlit default text in dark background */
p, div, span {
  text-shadow: 0 2px 10px rgba(0,0,0,.25);
}
</style>
""", unsafe_allow_html=True)

def _hud(col, mode: str, ammo: int, streak: int, combo: int, hp=None, tleft=None):
    with col:
        st.markdown(f"""
<div class="hud">
  <h4 style="margin:0 0 8px 0;">📟 HUD · 키워드</h4>
  <div class="row"><b>🎮 모드</b><span>{mode}</span></div>
  <div class="row"><b>📦 탄약</b><span>{ammo}</span></div>
  <div class="row"><b>🔥 스트릭</b><span>{streak}</span></div>
  <div class="row"><b>⚡ 콤보</b><span>{combo}</span></div>
</div>
""", unsafe_allow_html=True)
        if hp is not None or tleft is not None:
            st.markdown(f"""
<div class="hud" style="margin-top:10px;">
  <h4 style="margin:0 0 8px 0;">📜 미션</h4>
  {("<div class='row'><b>❤️ HP</b><span>"+str(hp)+"</span></div>") if hp is not None else ""}
  {("<div class='row'><b>⏱ 남은시간</b><span>"+str(tleft)+"s</span></div>") if tleft is not None else ""}
</div>
""", unsafe_allow_html=True)

def _ensure():
    st.session_state.setdefault("armory_mode", "VOCA_TRAIN")
    st.session_state.setdefault("armory_submode", "TRAIN")
    st.session_state.setdefault("voca_idx", 0)
    st.session_state.setdefault("voca_chunk_idx", 0)
    st.session_state.setdefault("voca_show_meaning", False)

    st.session_state.setdefault("battle_active", False)
    st.session_state.setdefault("battle_qi", 0)
    st.session_state.setdefault("battle_correct", 0)
    st.session_state.setdefault("battle_wrong", 0)
    st.session_state.setdefault("battle_hp", 3)
    st.session_state.setdefault("battle_combo", 0)
    st.session_state.setdefault("battle_best_combo", 0)
    st.session_state.setdefault("battle_started_at", 0.0)
    st.session_state.setdefault("battle_q_started", 0.0)
    st.session_state.setdefault("battle_seed", random.randint(1, 10_000_000))

def _train(items: List[Dict[str, Any]]):
    st.title("🟩 VOCA TRAIN")
    st.caption("시간 제한 없음. 단어를 넘기며 감각을 만든다.")
    if not items:
        st.warning("무기고 저장 단어가 없습니다.")
        return

    n = len(items)
    st.session_state["voca_idx"] = max(0, min(int(st.session_state["voca_idx"]), n-1))
    it = items[st.session_state["voca_idx"]]
    word = str(it.get("word","")).strip()
    meaning = str(it.get("meaning","") or it.get("ko","") or "").strip()

    chs = _chunks(it)
    if not chs:
        chs = [word] if word else ["(no chunk)"]
    st.session_state["voca_chunk_idx"] = max(0, min(int(st.session_state["voca_chunk_idx"]), len(chs)-1))
    chunk = chs[st.session_state["voca_chunk_idx"]]

    left,right = st.columns([3.7,1.3], gap="large")
    _hud(right, "VOCA-TRAIN", n, 0, 0)

    with left:
        st.markdown(f"""
<div class="card">
  <div class="sub">🪖 VOCA 학습 · 단어수첩</div>
  <div style="height:10px;"></div>
  <div class="big"><span class="chip">CHUNK</span> · {chunk}</div>
  <div style="margin-top:8px;color:#6b7280;font-weight:800;">WORD · {word}</div>
</div>
""", unsafe_allow_html=True)

        b1,b2,b3 = st.columns(3, gap="large")
        with b1:
            if st.button("📘 뜻 보기", use_container_width=True):
                st.session_state["voca_show_meaning"] = not bool(st.session_state["voca_show_meaning"])
        with b2:
            if st.button("➡️ 다음", use_container_width=True):
                st.session_state["voca_show_meaning"] = False
                st.session_state["voca_chunk_idx"] = 0
                st.session_state["voca_idx"] = (st.session_state["voca_idx"] + 1) % n
                st.rerun()
        with b3:
            if st.button("🧹 숙달(폐기)", use_container_width=True):
                st.session_state["confirm_discard"] = True

        if len(chs) > 1 and st.button("🔁 다른 조각(Chunk) 보기", use_container_width=True):
            st.session_state["voca_chunk_idx"] = (st.session_state["voca_chunk_idx"] + 1) % len(chs)
            st.rerun()

        if st.session_state.get("voca_show_meaning"):
            st.markdown(f"""
<div class="card" style="margin-top:14px;background:#f7f8fb;">
  <div class="sub">뜻</div>
  <div style="height:6px;"></div>
  <div style="font-size:18px;font-weight:950;color:#0b1220;">{meaning or "(뜻 없음)"}</div>
</div>
""", unsafe_allow_html=True)

        if st.session_state.get("confirm_discard"):
            st.warning("정말 폐기할까요? (단어수첩에서 제거)")
            c1,c2 = st.columns(2)
            with c1:
                if st.button("✅ 예, 폐기", use_container_width=True):
                    new_items = [x for x in items if str(x.get("word","")).strip().lower() != word.lower()]
                    _write_items(new_items)
                    st.session_state["confirm_discard"] = False
                    st.session_state["voca_show_meaning"] = False
                    st.session_state["voca_chunk_idx"] = 0
                    st.session_state["voca_idx"] = 0
                    st.rerun()
            with c2:
                if st.button("❌ 취소", use_container_width=True):
                    st.session_state["confirm_discard"] = False
                    st.rerun()

def _battle(items: List[Dict[str, Any]]):
    st.title("🔥 VOCA BATTLE (CHUNK)")
    st.caption("빈칸(____) + 4지선다 · 타이핑 금지 · 시간폭탄")

    if not items:
        st.warning("무기고 저장 단어가 없습니다.")
        return

    QTIME = 8
    QTOT = min(10, len(items))
    if not st.session_state.get("battle_active"):
        st.session_state["battle_active"] = True
        st.session_state["battle_qi"] = 0
        st.session_state["battle_correct"] = 0
        st.session_state["battle_wrong"] = 0
        st.session_state["battle_hp"] = 3
        st.session_state["battle_combo"] = 0
        st.session_state["battle_best_combo"] = 0
        st.session_state["battle_started_at"] = time.time()
        st.session_state["battle_q_started"] = time.time()
        st.session_state["battle_seed"] = random.randint(1, 10_000_000)

    rnd = random.Random(int(st.session_state["battle_seed"]))
    pool = items[:]
    rnd.shuffle(pool)
    pool = pool[:QTOT]

    qi = int(st.session_state["battle_qi"])
    if qi >= len(pool) or int(st.session_state["battle_hp"]) <= 0:
        _battle_result(len(pool))
        return

    it = pool[qi]
    word = str(it.get("word","")).strip()
    chs = _chunks(it)
    chunk = chs[0] if chs else word
    prompt = _blank(chunk, word)

    # options
    all_words = [str(x.get("word","")).strip() for x in items if str(x.get("word","")).strip()]
    distract = [w for w in all_words if w.lower() != word.lower()]
    rnd2 = random.Random(int(st.session_state["battle_seed"]) + qi)
    rnd2.shuffle(distract)
    opts = [word] + distract[:3]
    rnd2.shuffle(opts)

    elapsed = time.time() - float(st.session_state["battle_q_started"])
    tleft = max(0, int(QTIME - elapsed))

    left,right = st.columns([3.7,1.3], gap="large")
    _hud(right, "VOCA-BATTLE", len(items), int(st.session_state["battle_correct"]), int(st.session_state["battle_combo"]), hp=int(st.session_state["battle_hp"]), tleft=tleft)

    with left:
        st.markdown(f"""
<div class="card">
  <div class="sub">🎯 미션 {qi+1}/{len(pool)}</div>
  <div style="height:10px;"></div>
  <div class="big"><span class="chip">CHUNK</span> · {prompt}</div>
  <div style="margin-top:8px;color:#6b7280;font-weight:800;">정답 단어를 골라라</div>
</div>
""", unsafe_allow_html=True)

        if tleft <= 0:
            _mark_wrong()
            st.rerun()

        g1,g2 = st.columns(2, gap="large")
        clicked = None
        for i,opt in enumerate(opts):
            with (g1 if i % 2 == 0 else g2):
                if st.button(opt, use_container_width=True, key=f"bopt_{qi}_{i}"):
                    clicked = opt

        if clicked is not None:
            if clicked.lower() == word.lower():
                _mark_correct()
                st.success("✅ 명중!")
            else:
                _mark_wrong()
                st.error(f"❌ 오답! 정답: {word}")
            time.sleep(0.15)
            st.rerun()

def _mark_correct():
    st.session_state["battle_correct"] += 1
    st.session_state["battle_qi"] += 1
    st.session_state["battle_combo"] += 1
    st.session_state["battle_best_combo"] = max(st.session_state["battle_best_combo"], st.session_state["battle_combo"])
    st.session_state["battle_q_started"] = time.time()

def _mark_wrong():
    st.session_state["battle_wrong"] += 1
    st.session_state["battle_qi"] += 1
    st.session_state["battle_hp"] -= 1
    st.session_state["battle_combo"] = 0
    st.session_state["battle_q_started"] = time.time()

def _battle_result(total: int):
    correct = int(st.session_state["battle_correct"])
    wrong = int(st.session_state["battle_wrong"])
    best = int(st.session_state["battle_best_combo"])
    secs = int(time.time() - float(st.session_state["battle_started_at"]))
    rate = int((correct / max(1,total)) * 100)

    st.markdown(f"""
<div class="card">
  <div class="sub">🏁 전투 결과</div>
  <div style="height:10px;"></div>
  <div class="big">정답률 · {rate}%</div>
  <div style="margin-top:8px;color:#6b7280;font-weight:800;">✅ {correct} / ❌ {wrong} · 최고 콤보 {best} · 소요 {secs}s</div>
</div>
""", unsafe_allow_html=True)

    c1,c2,c3 = st.columns(3, gap="large")
    with c1:
        if st.button("🔁 다시 전장", use_container_width=True):
            st.session_state["battle_active"] = False
            st.rerun()
    with c2:
        if st.button("🟩 TRAIN 복귀", use_container_width=True):
            st.session_state["armory_submode"] = "TRAIN"
            st.session_state["battle_active"] = False
            st.rerun()
    with c3:
        if st.button("🏠 본부 복귀", use_container_width=True):
            st.info("허브 이동은 main_hub에서 처리됩니다.")

def render():
    # This MUST exist. pages/04 calls arena.render()
    _ensure()
    _apply_css()

    # debug line (remove later)
    st.caption(f"✅ LOADED: {ARMORY_BUILD} · {__file__}")

    items = _read_items()

    # top buttons (train/battle)
    t1,t2 = st.columns(2, gap="large")
    with t1:
        if st.button("🟩 TRAIN", use_container_width=True):
            st.session_state["armory_submode"] = "TRAIN"
            st.session_state["battle_active"] = False
            st.rerun()
    with t2:
        if st.button("🔥 BATTLE", use_container_width=True):
            st.session_state["armory_submode"] = "BATTLE"
            st.session_state["battle_active"] = False
            st.rerun()

    if str(st.session_state.get("armory_submode","TRAIN")).upper() == "BATTLE":
        _battle(items)
    else:
        _train(items)



