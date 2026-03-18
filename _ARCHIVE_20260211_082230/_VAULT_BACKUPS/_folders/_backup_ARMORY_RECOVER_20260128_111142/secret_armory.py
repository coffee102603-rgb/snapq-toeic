# ===== SNAPQ ARMORY TRACE BANNER (AUTO) =====
try:
    import streamlit as st
    st.error("🔥 SECRET ARMORY FILE LOADED: __FILE__ = " + __file__)
except Exception:
    pass
# ===========================================
# app/arenas/secret_armory.py
import json
from pathlib import Path
import random
import time
from typing import Any, Dict, List, Tuple, Optional

import streamlit as st

ARMORY_VER = "ARMORY_VER__2026-01-20__P5_TRAIN_NOTEBOOK__FORCE_CLEAN__SAFE"

# --- Paths ---
APP_DIR = Path(__file__).resolve().parents[1]  # .../app
DATA_DIR = APP_DIR / "data" / "armory"
ARMORY_PATH = DATA_DIR / "secret_armory.json"

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    st_autorefresh = None


# =========================================================
# UI/CSS (SAFE) : 諛앷린 + 臾몄젣吏??쒗뿕吏 + ?곗륫 HUD
# =========================================================
def _apply_armory_css() -> None:
    st.markdown(
        r"""
<style>
:root{
  --sa-bg1: #152233;
  --sa-bg2: #0f1724;
  --sa-ink: #0b1220;
  --sa-ink2: #1f2937;
  --sa-white: #ffffff;
  --sa-paper: #fbfbfd;
  --sa-paper2: #f4f6fb;
  --sa-stroke: rgba(15,23,42,0.18);
  --sa-stroke2: rgba(255,255,255,.16);
  --sa-accent: #9c5cff;
  --sa-accent2: #ff4fd8;
  --sa-shadow: 0 16px 40px rgba(0,0,0,.20);
  --sa-shadow2: 0 10px 26px rgba(0,0,0,.14);
}

/* ???꾩껜 諛곌꼍: ?덈Т ?대몼吏 ?딄쾶(諛앷린 ?щ┝) */
section[data-testid="stAppViewContainer"]{
  background:
    radial-gradient(1000px 700px at 10% 10%, rgba(190,120,255,.24), transparent 62%),
    radial-gradient(900px 620px at 90% 8%, rgba(120,160,255,.18), transparent 62%),
    linear-gradient(135deg, #101a28 0%, #162235 45%, #0f1724 100%) !important;
}

/* 而⑦뀒?대꼫 ?щ챸 */
section[data-testid="stAppViewContainer"] div[data-testid="stContainer"],
section[data-testid="stAppViewContainer"] div[data-testid="stVerticalBlock"],
section[data-testid="stAppViewContainer"] div[data-testid="column"] > div{
  background: transparent !important;
}

/* ???쇱そ 硫붿씤(臾몄젣吏??쒗뿕吏) 移대뱶 */
.sa-book{
  background: linear-gradient(180deg, var(--sa-paper), var(--sa-paper2));
  border: 1px solid var(--sa-stroke);
  border-radius: 18px;
  box-shadow: var(--sa-shadow);
  padding: 16px 16px;
  position: relative;
  overflow: hidden;
}
.sa-book::before{
  content:"";
  position:absolute;
  left:0; top:0; bottom:0;
  width:10px;
  background: linear-gradient(180deg, rgba(156,92,255,.95), rgba(255,79,216,.85));
  opacity:.95;
}
.sa-book .title{
  font-weight: 950;
  font-size: 18px;
  color: var(--sa-ink);
  padding-left: 10px;
}
.sa-book .sub{
  margin-top: 6px;
  color: rgba(15,23,42,.62);
  font-weight: 850;
  padding-left: 10px;
  font-size: 13px;
}
.sa-q{
  margin-top: 12px;
  padding: 14px 14px;
  border-radius: 14px;
  border: 1px solid rgba(15,23,42,.12);
  background: rgba(255,255,255,.78);
}
.sa-q .stem{
  font-weight: 950;
  font-size: clamp(19px, 1.35vw, 24px);
  line-height: 1.35;
  color: var(--sa-ink);
}
.sa-q .hint{
  margin-top: 7px;
  font-weight: 850;
  font-size: 12px;
  color: rgba(15,23,42,.60);
}

/* ???숈뒿 ?⑤꼸(?뺣떟/?댁꽍/?댁꽕) */
.sa-panel{
  background: var(--sa-white);
  border: 1px solid var(--sa-stroke);
  border-radius: 14px;
  box-shadow: var(--sa-shadow2);
  padding: 12px 12px;
  margin-top: 10px;
}
.sa-panel *{ color: var(--sa-ink) !important; text-shadow:none !important; }
.sa-panel .k{
  font-weight: 950;
  margin-bottom: 6px;
}

/* ??Streamlit alert?????⑤꼸濡?媛뺤젣 */
div[data-testid="stAlert"]{
  background: var(--sa-white) !important;
  border: 1px solid var(--sa-stroke) !important;
  border-radius: 14px !important;
  box-shadow: var(--sa-shadow2) !important;
}
div[data-testid="stAlert"] *{
  color: var(--sa-ink) !important;
  text-shadow: none !important;
  font-weight: 900 !important;
}

/* ???좏깮吏 踰꾪듉: 移대뱶???숈뒿/?쒗뿕 怨듯넻) */
section[data-testid="stAppViewContainer"] .stButton > button{
  border-radius: 16px !important;
  font-weight: 950 !important;
  min-height: 56px !important;
  font-size: 18px !important;
  border: 1px solid rgba(255,255,255,.18) !important;
  background: linear-gradient(180deg, rgba(255,255,255,.10), rgba(255,255,255,.06)) !important;
  box-shadow: 0 14px 34px rgba(0,0,0,.22) !important;
}



/* ??P5 TRAIN(?숈뒿) ?꾩슜: 臾몄젣吏???醫낆씠) + 2x2 ?좏깮吏 */
.p5-qbox{
  margin-top: 10px;
  padding: 14px 14px;
  border-radius: 16px;
  border: 2px solid rgba(15,23,42,.18);
  background: rgba(255,255,255,.92);
  box-shadow: 0 16px 36px rgba(0,0,0,.14);
}
.p5-qtext{
  color: var(--sa-ink) !important;
  font-weight: 950 !important;
  font-size: clamp(20px, 1.55vw, 26px) !important; /* ??臾몄젣 = ????*/
  line-height: 1.35 !important;
  text-shadow: none !important;
}
.p5-optbtn .stButton > button{
  background: rgba(255,255,255,.92) !important;
  color: var(--sa-ink) !important;
  border: 2px solid rgba(15,23,42,.20) !important;
  font-size: 20px !important; /* ???좏깮吏 = 臾몄젣蹂대떎 ?묎쾶(泥닿컧 1.2諛? */
  min-height: 72px !important;
  box-shadow: 0 14px 30px rgba(0,0,0,.16) !important;
}
.p5-optbtn .stButton > button:hover{
  border: 2px solid rgba(15,23,42,.45) !important;
  transform: translateY(-1px);
}
.p5-optbtn .stButton > button:active{ transform: translateY(0px); }

/* =========================================================
   ??P5 TRAIN ?명듃(BRIEF) ?ㅽ??? ?뺢킅???고븘/蹂쇳렂
   ========================================================= */
.p5-note{
  margin-top: 14px;
  padding: 14px 14px;
  border-radius: 16px;
  border: 1px solid rgba(15,23,42,.14);
  background: rgba(255,255,255,.96);
  box-shadow: 0 14px 30px rgba(0,0,0,.12);
}
.p5-note .hd{
  font-weight: 950;
  color: rgba(15,23,42,.92);
  margin-bottom: 8px;
}
.p5-row{ margin-top: 10px; }
.p5-tag{
  display:inline-block;
  font-weight: 950;
  font-size: 12px;
  color: rgba(15,23,42,.70);
  margin-bottom: 6px;
}
.p5-hl{
  background: rgba(255, 235, 59, .40);
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: 950;
  color: rgba(15,23,42,.92);
}
.p5-pencil{
  color: rgba(15,23,42,.72);
  font-weight: 900;
}
.p5-pen{
  color: rgba(37, 99, 235, .92);
  font-weight: 950;
}

/* ??TRAIN ?섎떒 踰꾪듉(臾몄젣吏묒뿉???쒓굅/?ㅼ쓬) ??議곗슜??踰꾪듉 */
.p5-softbtn .stButton > button{
  background: rgba(255,255,255,.88) !important;
  color: rgba(15,23,42,.92) !important;
  border: 2px solid rgba(15,23,42,.18) !important;
  min-height: 68px !important;
  font-size: 18px !important;
  box-shadow: 0 12px 24px rgba(0,0,0,.12) !important;
}
.p5-softbtn .stButton > button:hover{
  border: 2px solid rgba(15,23,42,.34) !important;
  transform: translateY(-1px);
}
/* ???곗륫 HUD 移대뱶 */
.sa-hudcard{
  background: linear-gradient(180deg, rgba(255,255,255,.10), rgba(255,255,255,.06));
  border: 1px solid rgba(255,255,255,.14);
  border-radius: 16px;
  padding: 12px 12px;
  box-shadow: 0 14px 34px rgba(0,0,0,.22);
  margin-bottom: 10px;
}
.sa-hudcard .h{
  font-weight: 950;
  color: rgba(255,255,255,.95);
  margin-bottom: 6px;
}
.sa-chip{
  display:inline-flex;
  align-items:center;
  gap:6px;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(255,255,255,.08);
  border: 1px solid rgba(255,255,255,.14);
  color: rgba(255,255,255,.92);
  font-weight: 950;
  font-size: 13px;
  margin: 4px 6px 0 0;
}

/* ???쒗뿕 紐⑤뱶 ??대㉧ 媛뺤“ */
.sa-timer{
  font-size: 28px;
  font-weight: 950;
  color: #ffffff;
  letter-spacing: .5px;
  text-shadow: 0 2px 14px rgba(0,0,0,.45);
}
.sa-timer.red{
  color: #ff6a6a;
}

/* ??紐⑤컮?? 80/20???몃줈濡??볦씠寃?*/
@media (max-width: 768px){
  section[data-testid="stAppViewContainer"] .stButton > button{
    min-height: 66px !important;
    font-size: 20px !important;
  }
  .sa-timer{ font-size: 26px; }
}
/* ============================================================
   P5 EXAM VISIBILITY OVERRIDE (SAFE)
   - ?쒗뿕吏(?쇱そ) 湲???뺤떎??寃??   - ?좏깮吏 踰꾪듉? 諛앹? 醫낆씠 + 寃??湲??   - ?곗륫 HUD 踰꾪듉? ?대몢?????좎?
   ============================================================ */

/* ?쒗뿕吏 移대뱶/蹂몃Ц? 臾댁“嫄?吏꾪븯寃?*/
.sa-book, .sa-book *{
  color: var(--sa-ink) !important;
  opacity: 1 !important;
  text-shadow: none !important;
  filter: none !important;
}

/* ?쒗뿕吏 ?대? ?듭떖 ?띿뒪????吏꾪븯寃?*/
.sa-q .stem{ color: var(--sa-ink) !important; font-weight: 950 !important; }
.sa-q .hint{ color: rgba(15,23,42,.70) !important; font-weight: 900 !important; }

/* 湲곕낯 踰꾪듉(?쇱そ ?좏깮吏)? '醫낆씠+寃???쇰줈 媛뺤젣 */
section[data-testid="stAppViewContainer"] .stButton > button{
  background: linear-gradient(180deg, rgba(255,255,255,0.98), rgba(255,248,235,0.92)) !important;
  border: 2px solid rgba(203,213,225,0.95) !important;
  box-shadow: 0 14px 30px rgba(0,0,0,0.14) !important;
}
section[data-testid="stAppViewContainer"] .stButton > button,
section[data-testid="stAppViewContainer"] .stButton > button *{
  color: #111827 !important;
  -webkit-text-fill-color:#111827 !important;
  font-weight: 950 !important;
  opacity: 1 !important;
  text-shadow: none !important;
}

/* ?곗륫 HUD 移대뱶 ?대? ?대룞 踰꾪듉? ?ㅼ떆 ?대몼寃??쒗뿕??諛⑺빐 理쒖냼?? */
.sa-hudcard section[data-testid="stAppViewContainer"] .stButton > button,
.sa-hudcard .stButton > button{
  background: rgba(255,255,255,0.08) !important;
  border: 1px solid rgba(255,255,255,0.16) !important;
  box-shadow: 0 14px 30px rgba(0,0,0,0.18) !important;
}
.sa-hudcard .stButton > button, .sa-hudcard .stButton > button *{
  color: rgba(255,255,255,0.92) !important;
  -webkit-text-fill-color: rgba(255,255,255,0.92) !important;
  text-shadow: 0 2px 10px rgba(0,0,0,0.55) !important;
}
</style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# VOCA robust extractor (湲곗〈 ?좎?)
# =========================================================
_WORD_KEYS = ["word", "eng", "english", "en", "term", "front", "headword", "lemma", "vocab_word"]
_MEAN_KEYS = ["meaning", "kor", "korean", "ko", "translation", "definition", "gloss", "vocab_meaning"]


def _pick_first_str(item: Dict[str, Any], keys: List[str]) -> Optional[str]:
    for k in keys:
        v = item.get(k)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return None


def _postprocess_vocab_pair(word: str, meaning: str) -> Tuple[str, str]:
    w = (word or "").strip()
    m = (meaning or "").strip()
    if not w:
        w = "WORD"
    if not m:
        m = "MEANING"
    for ch in ["\n", "\r", "\t"]:
        w = w.replace(ch, " ").strip()
        m = m.replace(ch, " ").strip()
    return (w, m)


def _extract_vocab_pair(item: Any) -> Tuple[str, str]:
    if isinstance(item, dict):
        w = _pick_first_str(item, _WORD_KEYS) or ""
        m = _pick_first_str(item, _MEAN_KEYS) or ""
        if not w:
            combined = None
            for k in ["text", "value", "line", "content", "raw", "entry"]:
                v = item.get(k)
                if isinstance(v, str) and v.strip():
                    combined = v.strip()
                    break
            if combined:
                item = combined
            else:
                nested = item.get("data")
                if isinstance(nested, dict):
                    w = _pick_first_str(nested, _WORD_KEYS) or w
                    m = _pick_first_str(nested, _MEAN_KEYS) or m
        if w or m:
            return _postprocess_vocab_pair(w, m)

    if isinstance(item, str):
        s = item.strip()
        for sep in [" - ", " : ", " | ", "\t", "|", ":", "-", "??"]:
            if sep in s:
                left, right = s.split(sep, 1)
                return _postprocess_vocab_pair(left, right)
        return _postprocess_vocab_pair(s, "??)

    return ("WORD", "??)



# =========================================================
# VOCA context extractor (SAFE)
# - P7?먯꽌 "臾몄옣(sentence)"源뚯? ??λ릺???덉쑝硫?洹몃?濡?蹂댁뿬二쇨린
# - ?놁쑝硫?None (?⑥뼱留뚯쑝濡?TRAIN)
# =========================================================
_SENTENCE_KEYS = [
    "sentence",
    "context",
    "source_sentence",
    "example",
    "example_sentence",
    "origin_sentence",
]

def _extract_vocab_sentence(item: Any) -> Optional[str]:
    if isinstance(item, dict):
        for k in _SENTENCE_KEYS:
            v = item.get(k)
            if isinstance(v, str) and v.strip():
                return v.strip()
    return None


def _highlight_word_in_sentence(sentence: str, word: str) -> str:
    s = (sentence or "")
    w = (word or "")
    if not s or not w:
        return s

    # minimal HTML escape
    s_esc = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    w_esc = w.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    low = s_esc.lower()
    idx = low.find(w_esc.lower())
    if idx < 0:
        return s_esc

    before = s_esc[:idx]
    mid = s_esc[idx: idx + len(w_esc)]
    after = s_esc[idx + len(w_esc):]
    return f"{before}<span class='sa-hl'>{mid}</span>{after}"




# =========================================================
# Armory IO (list 援ъ“ ?좎?)
# =========================================================
def _load_armory_items() -> List[Dict[str, Any]]:
    try:
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        if ARMORY_PATH.exists():
            raw = ARMORY_PATH.read_text(encoding="utf-8", errors="ignore").strip()
            if not raw:
                return []
            data = json.loads(raw)
            if isinstance(data, list):
                return data
        return []
    except Exception:
        return []


def _save_armory_items(items: List[Dict[str, Any]]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARMORY_PATH.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")


# =========================================================
# Filters
# =========================================================
def _is_p5_item(x: Dict[str, Any]) -> bool:
    return x.get("source") == "P5"


def _is_p7_vocab_item(x: Dict[str, Any]) -> bool:
    src = x.get("source")
    t = x.get("type")
    return (src in ("VOCA", "P7", "VOCAB")) or (t in ("vocab", "word"))


def _filter_p5(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [x for x in items if _is_p5_item(x)]


def _filter_voca(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [x for x in items if _is_p7_vocab_item(x)]


# =========================================================
# 80/20 Layout helper
# =========================================================
def _two_pane_layout(left_fn, right_fn) -> None:
    # desktop: 80/20, mobile: stacked
    left, right = st.columns([4, 1], gap="large")
    with left:
        left_fn()
    with right:
        right_fn()


def _hud_right(
    *,
    mode_label: str,
    ammo: int,
    streak: int = 0,
    combo: int = 0,
    extra_lines: Optional[List[str]] = None,
    show_controls: bool = True,
) -> None:
    st.markdown(
        f"""
        <div class="sa-hudcard">
          <div class="h">?럾 HUD 쨌 ?ㅼ썙??/div>
          <div class="sa-chip">?렜 {mode_label}</div>
          <div class="sa-chip">?벀 ?꾩빟 {ammo}</div>
          <div class="sa-chip">?뵦 ?ㅽ듃由?{streak}</div>
          <div class="sa-chip">??肄ㅻ낫 {combo}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if extra_lines:
        st.markdown('<div class="sa-hudcard"><div class="h">?㎨ 誘몄뀡</div>', unsafe_allow_html=True)
        for ln in extra_lines:
            st.write(ln)
        st.markdown("</div>", unsafe_allow_html=True)

    if show_controls:
        st.markdown('<div class="sa-hudcard"><div class="h">?봺 ?대룞</div>', unsafe_allow_html=True)
        st.button("???묒쟾 ?좏깮?쇰줈", use_container_width=True, key=f"hud_back_{mode_label}")
        st.button("?룧 蹂몃? 蹂듦?", use_container_width=True, key=f"hud_home_{mode_label}")
        st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# Button choices
# =========================================================
def _choice_buttons_vertical_set(state_key: str, choices: List[str]) -> Optional[str]:
    picked = st.session_state.get(state_key)
    for i, ch in enumerate(choices):
        if st.button(ch, use_container_width=True, key=f"{state_key}__{i}__{ch}"):
            st.session_state[state_key] = ch
            picked = ch
            st.rerun()
    return picked


def _choice_buttons_grid_submit(choices: List[str], on_pick, key_prefix: str) -> None:
    cols = st.columns(2, gap="large")
    for idx, ch in enumerate(choices):
        with cols[idx % 2]:
            if st.button(ch, use_container_width=True, key=f"{key_prefix}__pick__{idx}__{ch}"):
                on_pick(ch)
                st.rerun()


# =========================================================
# TRAIN (?숈뒿) : 臾몄젣吏?+ ?먯젙 ???뺣떟/?댁꽍/?댁꽕 ?섏씠吏 ?대? ?쒖떆
# =========================================================
def _render_p5_learning(items: List[Dict[str, Any]]) -> None:
    """(LEGACY) 湲곗〈 TRAIN ?뚮뜑?ш? ?대뵖媛?먯꽌 ?몄텧?섎뜑?쇰룄
    ??긽 '臾몄젣吏??명듃' 理쒖떊 TRAIN UI濡?媛뺤젣 ?곌껐?쒕떎.
    """
    _render_p5_train_clean(items)
    return

    # ???ㅼ젣 ??λ맂 臾몄젣瑜??곗꽑 ?ъ슜 (?놁쑝硫??곕え)
    if ammo > 0:
        pool = p5_items
        use_saved = True
    else:
        pool = [
            {
                "sentence": "Our company is trying to _____ costs without reducing quality.",
                "choices": ["increase", "raise", "cut", "spread"],
                "answer": "cut",
                "ko": "?곕━ ?뚯궗???덉쭏???⑥뼱?⑤━吏 ?딆쑝硫댁꽌 鍮꾩슜??以꾩씠?ㅺ퀬 ?쒕떎.",
                "explain": "cut costs = 鍮꾩슜??以꾩씠??",
            },
            {
                "sentence": "Please find the revised file _____ to this email.",
                "choices": ["attached", "attaching", "attachment", "to attach"],
                "answer": "attached",
                "ko": "???대찓?쇱뿉 泥⑤????섏젙 ?뚯씪???뺤씤??二쇱꽭??",
                "explain": "file attached to ~ : ~??泥⑤????뚯씪 (怨쇨굅遺꾩궗 ?섏떇).",
            },
        ]
        use_saved = False

    # 臾몄젣吏??먮굦: ??臾몄젣瑜?怨좎튂怨??섏뼱媛?(?몄뀡 怨좎젙)
    st.session_state.setdefault("p5_train_idx", random.randrange(len(pool)))
    q = pool[int(st.session_state["p5_train_idx"]) % len(pool)]

    # ?곹깭
    st.session_state.setdefault("p5_train_streak", 0)
    st.session_state.setdefault("p5_train_combo", 0)
    st.session_state.setdefault("p5_train_judged", False)
    st.session_state.setdefault("p5_train_last_ok", None)

    # ?숈뒿 ?⑤꼸 踰꾪듉(?섏씠吏 ?대?)
    st.session_state.setdefault("p5_train_show_answer", False)
    st.session_state.setdefault("p5_train_show_ko", False)
    st.session_state.setdefault("p5_train_show_explain", False)

    def left_area():
        st.markdown(
            f"""
            <div class="sa-book">
              <div class="title">?뱱 P5 ?숈뒿 紐⑤뱶 쨌 臾몄젣吏??덈젴</div>
              <div class="sub">???섏씠吏?먯꽌 ?앸궦?? ?먯젙 ???뺣떟/?댁꽍/?댁꽕 ?쇱튂湲????먭린/?ㅼ쓬 臾몄젣</div>

              <div class="sa-q">
                <div class="stem">?쭬 {q.get('sentence','')}</div>
                <div class="hint">?좏깮吏 ?좏깮 ??<b>?먯젙</b>???뚮윭???숈뒿 ?⑤꼸???대┛??</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### ?렞 ?좏깮吏")
        picked = _choice_buttons_vertical_set("p5_train_pick", q.get("choices", []))

        c1, c2, c3 = st.columns(3, gap="large")
        with c1:
            if st.button("?㏏ ?먭린", use_container_width=True, key="p5_train_discard"):
                # ?숈뒿?먭? 怨듬? ?앸궦 臾몄젣???먭린(= ?ㅼ쓬 臾몄젣濡??대룞 + ?⑤꼸 ?リ린)
                st.session_state["p5_train_pick"] = None
                st.session_state["p5_train_judged"] = False
                st.session_state["p5_train_last_ok"] = None
                st.session_state["p5_train_show_answer"] = False
                st.session_state["p5_train_show_ko"] = False
                st.session_state["p5_train_show_explain"] = False
                st.success("?먭린 ?꾨즺. ?ㅼ쓬 臾몄젣濡??섏뼱媛??")
                # ?ㅼ쓬 臾몄젣
                st.session_state["p5_train_idx"] = (int(st.session_state["p5_train_idx"]) + 1) % len(pool)
                st.rerun()

        with c2:
            if st.button("?뵊 ?먯젙", use_container_width=True, key="p5_train_judge"):
                if not picked:
                    st.warning("癒쇱? ?좏깮吏瑜?怨⑤씪??")
                else:
                    ok = (picked == q.get("answer"))
                    st.session_state["p5_train_judged"] = True
                    st.session_state["p5_train_last_ok"] = ok

                    if ok:
                        st.success("???뺣떟. 媛먭컖 ?좎?!")
                        st.session_state["p5_train_streak"] = int(st.session_state["p5_train_streak"]) + 1
                        st.session_state["p5_train_combo"] = int(st.session_state["p5_train_combo"]) + 1
                    else:
                        st.error(f"???ㅻ떟. ?뺣떟: {q.get('answer','')}")
                        st.session_state["p5_train_streak"] = 0
                        st.session_state["p5_train_combo"] = 0

        with c3:
            if st.button("?∽툘 ?ㅼ쓬 臾몄젣", use_container_width=True, key="p5_train_next"):
                st.session_state["p5_train_pick"] = None
                st.session_state["p5_train_judged"] = False
                st.session_state["p5_train_last_ok"] = None
                st.session_state["p5_train_show_answer"] = False
                st.session_state["p5_train_show_ko"] = False
                st.session_state["p5_train_show_explain"] = False
                st.session_state["p5_train_idx"] = (int(st.session_state["p5_train_idx"]) + 1) % len(pool)
                st.rerun()

        # ???숈뒿 ?⑤꼸: ?먯젙 ??踰꾪듉?쇰줈 ?섏씠吏 ?덉뿉???쇱튂湲?        if st.session_state.get("p5_train_judged", False):
            st.markdown("### ?뱦 ?숈뒿 ?⑤꼸 (?뺣떟/?댁꽍/?댁꽕)")
            b1, b2, b3 = st.columns(3, gap="large")
            with b1:
                if st.button("???뺣떟", use_container_width=True, key="train_btn_answer"):
                    st.session_state["p5_train_show_answer"] = True
            with b2:
                if st.button("?뱰 ?댁꽍", use_container_width=True, key="train_btn_ko"):
                    st.session_state["p5_train_show_ko"] = True
            with b3:
                if st.button("?㎥ ?댁꽕", use_container_width=True, key="train_btn_explain"):
                    st.session_state["p5_train_show_explain"] = True

            if st.session_state.get("p5_train_show_answer", False):
                st.markdown(
                    f"""
                    <div class="sa-panel">
                      <div class="k">?뺣떟</div>
                      <div><b>{q.get('answer','')}</b></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            if st.session_state.get("p5_train_show_ko", False):
                st.markdown(
                    f"""
                    <div class="sa-panel">
                      <div class="k">?댁꽍</div>
                      <div>{q.get('ko','(?댁꽍 ?놁쓬)')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            if st.session_state.get("p5_train_show_explain", False):
                st.markdown(
                    f"""
                    <div class="sa-panel">
                      <div class="k">?댁꽕</div>
                      <div>{q.get('explain','(?댁꽕 ?놁쓬)')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.caption("?뵏 ?숈뒿 ?⑤꼸 ?좉툑: ?먯젙 ???대┝")

        if use_saved:
            st.caption("?벀 ?꾩옱??'??λ맂 P5 臾몄젣'濡??숈뒿 以?")
        else:
            st.caption("?벀 ??λ맂 P5 臾몄젣媛 ?놁뼱 ?곕え 臾몄젣濡??쒖떆 以?")

    def right_area():
        _hud_right(
            mode_label="TRAIN",
            ammo=ammo,
            streak=int(st.session_state["p5_train_streak"]),
            combo=int(st.session_state["p5_train_combo"]),
            extra_lines=[
                "??紐⑺몴: 臾몄젣吏묒쿂????臾몄젣 ?꾩쟾 ?뺣━",
                "???먮쫫: ?먯젙 ???⑤꼸 ?닿린 ???먭린/?ㅼ쓬",
            ],
            show_controls=True,
        )

    _two_pane_layout(left_area, right_area)


# =========================================================
# LIVE (?쒗뿕) : 5臾몄젣/30珥??명듃 + ?ъ젙?듭씠硫??먮룞 ?먭린 / 1媛쒕씪???由щ㈃ ?좎?
# =========================================================
P5_EXAM_TOTAL_Q = 5
P5_EXAM_TOTAL_SECONDS = 30.0


def _exam_reset_state():
    for k in [
        "p5_exam_active",
        "p5_exam_ids",
        "p5_exam_idx",
        "p5_exam_wrong",
        "p5_exam_deadline",
        "p5_exam_score",
        "p5_exam_done",
        "p5_exam_msg",
    ]:
        st.session_state.pop(k, None)


def _render_p5_timebomb(items: List[Dict[str, Any]]) -> None:
    _apply_armory_css()

    p5_items = _filter_p5(items)
    ammo = len(p5_items)

    # ???쒗뿕? 諛섎뱶??'??λ맂 P5'?먯꽌留?吏꾪뻾 (猷? 5臾몄젣 30珥?
    def left_area():
        st.markdown(
            """
            <div class="sa-book">
              <div class="title">?뱷 P5 ?쒗뿕 紐⑤뱶 쨌 5臾명빆 ??꾩뼱??/div>
              <div class="sub">猷? 5臾몄젣/30珥? 5媛?紐⑤몢 ?뺣떟?대㈃ <b>?먮룞 ?먭린</b>. 1媛쒕씪???由щ㈃ <b>?좎?(?ㅼ떆 ???</b>.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if ammo < P5_EXAM_TOTAL_Q:
            st.warning(f"??λ맂 P5 臾몄젣媛 遺議깊빀?덈떎. (?꾩슂: {P5_EXAM_TOTAL_Q}媛?/ ?꾩옱: {ammo}媛?")
            return
        # ?쒖옉 UI ?쒓굅(泥??섏씠吏 ?쒓굅): 吏꾩엯 利됱떆 ?먮룞 異쒓꺽
        if not st.session_state.get("p5_exam_active", False):
            idxs = list(range(len(p5_items)))
            random.shuffle(idxs)
            picked = idxs[:P5_EXAM_TOTAL_Q]

            st.session_state["p5_exam_active"] = True
            st.session_state["p5_exam_ids"] = picked
            st.session_state["p5_exam_idx"] = 0
            st.session_state["p5_exam_wrong"] = False
            st.session_state["p5_exam_score"] = 0
            st.session_state["p5_exam_done"] = False
            st.session_state["p5_exam_msg"] = None
            st.session_state["p5_exam_deadline"] = time.time() + P5_EXAM_TOTAL_SECONDS
            st.rerun()
# ??대㉧ ?먮룞 媛깆떊
        if st_autorefresh is not None:
            st_autorefresh(interval=200, key="p5_exam_tick")

        now = time.time()
        deadline = float(st.session_state.get("p5_exam_deadline", now))
        remaining = max(0.0, deadline - now)

        # ?쒓컙 醫낅즺 泥섎━
        if remaining <= 0 and not st.session_state.get("p5_exam_done", False):
            st.session_state["p5_exam_wrong"] = True  # ?쒓컙珥덇낵 = ?ㅽ뙣
            st.session_state["p5_exam_done"] = True
            st.session_state["p5_exam_msg"] = ("error", "???쒓컙 珥덇낵. ?쒗뿕 ?ㅽ뙣(?좎?).")
            st.rerun()

        # 吏꾪뻾
        exam_ids: List[int] = st.session_state.get("p5_exam_ids", [])
        q_idx = int(st.session_state.get("p5_exam_idx", 0))
        wrong = bool(st.session_state.get("p5_exam_wrong", False))
        score = int(st.session_state.get("p5_exam_score", 0))
        done = bool(st.session_state.get("p5_exam_done", False))

        # ?곷떒 ??대㉧(?쒗뿕吏 ?먮굦)
        timer_cls = "sa-timer red" if remaining <= 8 else "sa-timer"
        st.markdown(f"<div class='{timer_cls}'>??{remaining:04.1f}s</div>", unsafe_allow_html=True)
        st.progress(min(1.0, remaining / max(0.1, P5_EXAM_TOTAL_SECONDS)))

        st.caption(f"吏꾪뻾: {min(q_idx+1, P5_EXAM_TOTAL_Q)} / {P5_EXAM_TOTAL_Q}   |   ?먯닔: {score} / {P5_EXAM_TOTAL_Q}")

        # 醫낅즺 ?붾㈃
        if done:
            msg = st.session_state.get("p5_exam_msg")
            if msg:
                kind, text = msg
                if kind == "success":
                    st.success(text)
                else:
                    st.error(text)

            if (not wrong) and score == P5_EXAM_TOTAL_Q:
                st.markdown(
                    "<div class='sa-panel'><div class='k'>寃곌낵</div><div>?럦 5臾몄젣 ?ъ젙?? ?먮룞 ?먭린 ?꾨즺.</div></div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    "<div class='sa-panel'><div class='k'>寃곌낵</div><div>????臾몄젣?쇰룄 ?ㅽ뙣 ??臾몄젣???좎?(?ㅼ떆 ???.</div></div>",
                    unsafe_allow_html=True,
                )

            c1, c2 = st.columns(2, gap="large")
            with c1:
                if st.button("?봺 ?ㅼ떆 ?쒗뿕", use_container_width=True, key="p5_exam_retry"):
                    _exam_reset_state()
                    st.rerun()
            with c2:
                if st.button("?㏏ ?쒗뿕 醫낅즺(珥덇린??", use_container_width=True, key="p5_exam_exit"):
                    _exam_reset_state()
                    st.rerun()
            return

        # ?꾩옱 臾몄젣
        cur_global_idx = exam_ids[q_idx]
        q = p5_items[cur_global_idx]
        sentence = q.get("sentence", "")
        choices = q.get("choices", [])
        answer = q.get("answer", "")

        st.markdown(
            f"""
            <div class="sa-book" style="margin-top:12px;">
              <div class="title">?뱞 ?쒗뿕吏</div>
              <div class="sub">?좏깮吏 ?대┃ = 利됱떆 ?쒖텧 (?먯젙 踰꾪듉 ?놁쓬)</div>
              <div class="sa-q">
                <div class="stem">?쭬 {sentence}</div>
                <div class="hint">5臾몄젣/30珥? ?ъ젙?듭씠硫??먮룞 ?먭린.</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        def on_pick(ch: str) -> None:
            nonlocal q_idx, score, wrong
            if ch == answer:
                st.session_state["p5_exam_score"] = score + 1
                st.session_state["p5_exam_msg"] = ("success", "??紐낆쨷.")
            else:
                st.session_state["p5_exam_wrong"] = True
                st.session_state["p5_exam_msg"] = ("error", f"???ㅻ떟. ?뺣떟: {answer}")

            # ?ㅼ쓬 臾몄젣濡?            st.session_state["p5_exam_idx"] = q_idx + 1

            # 留덉?留?臾몄젣??쇰㈃ 醫낅즺 泥섎━
            if (q_idx + 1) >= P5_EXAM_TOTAL_Q:
                # 理쒖쥌 ?먯젙
                final_score = int(st.session_state.get("p5_exam_score", 0))
                final_wrong = bool(st.session_state.get("p5_exam_wrong", False))
                # 吏湲?臾몄젣?먯꽌 ?먯닔 諛섏쁺???꾩쭅?대㈃ 蹂댁젙
                if ch == answer:
                    final_score = final_score  # already incremented
                else:
                    final_wrong = True

                # ?쒓컙??泥댄겕
                now2 = time.time()
                rem2 = max(0.0, float(st.session_state.get("p5_exam_deadline", now2)) - now2)
                if rem2 <= 0:
                    final_wrong = True

                # ?ъ젙?듭씠硫??먮룞 ?먭린
                if (not final_wrong) and final_score >= P5_EXAM_TOTAL_Q:
                    # items(list)?먯꽌 ?대떦 5媛쒕? ?쒓굅 (matching by object identity/contents)
                    # ?덉쟾: sentence+answer 湲곗??쇰줈 ?쒓굅
                    targets = []
                    for gi in exam_ids:
                        it = p5_items[gi]
                        targets.append((it.get("sentence", ""), it.get("answer", ""), it.get("choices", [])))

                    new_items = []
                    removed = 0
                    for it in items:
                        if it.get("source") == "P5":
                            key = (it.get("sentence", ""), it.get("answer", ""), it.get("choices", []))
                            if key in targets:
                                removed += 1
                                continue
                        new_items.append(it)

                    _save_armory_items(new_items)
                    st.session_state["p5_exam_done"] = True
                    st.session_state["p5_exam_msg"] = ("success", f"?럦 ?ъ젙?? ?먮룞 ?먭린 ?꾨즺 ({removed}媛??쒓굅)")
                else:
                    # ?ㅽ뙣硫??좎?(= ?꾨Т寃껊룄 ????
                    st.session_state["p5_exam_done"] = True
                    st.session_state["p5_exam_msg"] = ("error", "???ㅽ뙣. 臾몄젣???좎?(?ㅼ떆 ???.")

        st.markdown("#### ?렞 ?좏깮吏 (利됱떆 ?쒖텧)")
        _choice_buttons_grid_submit(choices, on_pick=on_pick, key_prefix=f"p5_exam_{q_idx}")

        msg = st.session_state.get("p5_exam_msg")
        if msg:
            kind, text = msg
            if kind == "success":
                st.success(text)
            else:
                st.error(text)

        # 以묐떒/由ъ뀑
        c1, c2 = st.columns(2, gap="large")
        with c1:
            if st.button("?㎤ ?쒗뿕 以묐떒", use_container_width=True, key="p5_exam_abort"):
                _exam_reset_state()
                st.warning("?쒗뿕 以묐떒. 臾몄젣???좎?.")
                st.rerun()
        with c2:
            if st.button("?㏏ 媛뺤젣 由ъ뀑", use_container_width=True, key="p5_exam_reset"):
                _exam_reset_state()
                st.rerun()

    def right_area():
        active = bool(st.session_state.get("p5_exam_active", False))
        done = bool(st.session_state.get("p5_exam_done", False))
        q_idx = int(st.session_state.get("p5_exam_idx", 0))
        score = int(st.session_state.get("p5_exam_score", 0))
        wrong = bool(st.session_state.get("p5_exam_wrong", False))

        now = time.time()
        deadline = float(st.session_state.get("p5_exam_deadline", now))
        remaining = max(0.0, deadline - now)

        extra = [
            f"???명듃: {P5_EXAM_TOTAL_Q}臾몄젣",
            f"???쒗븳: {int(P5_EXAM_TOTAL_SECONDS)}珥?,
            f"??吏꾪뻾: {min(q_idx+1, P5_EXAM_TOTAL_Q)} / {P5_EXAM_TOTAL_Q}" if active else "???湲?以?,
            f"???먯닔: {score} / {P5_EXAM_TOTAL_Q}" if active else "???먯닔: -",
            "???곹깭: ?ㅽ뙣(?좎?)" if wrong else "???곹깭: ?ъ젙?듭씠硫??먭린",
        ]
        _hud_right(
            mode_label="EXAM",
            ammo=ammo,
            streak=0,
            combo=0,
            extra_lines=extra,
            show_controls=True,
        )
        if active and (not done):
            cls = "sa-timer red" if remaining <= 8 else "sa-timer"
            st.markdown(f"<div class='{cls}'>??{remaining:04.1f}s</div>", unsafe_allow_html=True)

    _two_pane_layout(left_area, right_area)


# =========================================================
# VOCA TRAIN/LIVE (湲곗〈 ?좎?)
# =========================================================
def _render_voca_flip(items: List[Dict[str, Any]]) -> None:
    _apply_armory_css()
    voca_items = _filter_voca(items)
    if not voca_items:
        st.info("VOCA ?꾩빟???놁뒿?덈떎. (蹂묎린怨좎뿉 ??λ맂 ?⑥뼱媛 ?놁뼱??")
        return

    # sentence highlight style
    st.markdown(
        """
<style>
.sa-hl{
  background: rgba(255, 235, 59, .55);
  padding: 1px 6px;
  border-radius: 10px;
  font-weight: 950;
}
</style>
        """,
        unsafe_allow_html=True,
    )

    st.session_state.setdefault("voca_flip_idx", 0)
    idx = int(st.session_state["voca_flip_idx"]) % len(voca_items)

    item = voca_items[idx]
    word, meaning = _extract_vocab_pair(item)
    sentence = _extract_vocab_sentence(item)

    def left_area():
        st.markdown(
            f"""
            <div class="sa-book">
              <div class="title">?첉 VOCA ?숈뒿 쨌 P7 由ы뵆?덉씠 ?덈젴</div>
              <div class="sub">?먮Ц 臾몄옣???덉쑝硫?洹몃?濡?由ы뵆?덉씠?섍퀬, ?놁쑝硫??⑥뼱留뚯쑝濡??ъ옣?꾪븳??</div>

              <div class="sa-q">
                <div class="stem">?쭬 WORD 쨌 {word}</div>
                <div class="hint">?살쓣 ?뺤씤?섍퀬, ?ㅼ쓬?쇰줈 ?섍꺼??</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ??P7 ?먮Ц 臾몄옣(?덉쓣 ?뚮쭔)
        if isinstance(sentence, str) and sentence.strip():
            hi = _highlight_word_in_sentence(sentence, word)
            st.markdown(
                f"""
                <div class="sa-panel">
                  <div class="k">?뱦 P7 ?먮Ц 臾몄옣 (洹몃?濡?</div>
                  <div style="font-weight:900; font-size:18px; line-height:1.55;">{hi}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.caption("?뱦 ?먮Ц 臾몄옣????λ릺???덉? ?딆븘, ?꾩옱???⑥뼱 以묒떖?쇰줈 TRAIN?⑸땲?? (?덉쟾 紐⑤뱶)")

        c1, c2, c3 = st.columns(3, gap="large")
        with c1:
            if st.button("?뱰 ??蹂닿린", use_container_width=True, key=f"voca_show_{idx}"):
                st.markdown(
                    f"<div class='sa-panel'><div class='k'>??/div><div>{meaning}</div></div>",
                    unsafe_allow_html=True,
                )
        with c2:
            if st.button("?∽툘 ?ㅼ쓬", use_container_width=True, key=f"voca_next_{idx}"):
                st.session_state["voca_flip_idx"] = idx + 1
                st.rerun()
        with c3:
            # (A?? ?꾩쭅 ??젣/泥?냼 濡쒖쭅? 嫄대뱶由ъ? ?딆쓬 ???덉쟾)
            st.button("?㏏ ?숇떖(?먭린)", use_container_width=True, key=f"voca_master_{idx}")

    def right_area():
        _hud_right(
            mode_label="VOCA-TRAIN",
            ammo=len(voca_items),
            streak=0,
            combo=0,
            extra_lines=[
                "??紐⑺몴: P7?먯꽌 留됲엺 ?⑥뼱瑜?'臾몄옣 ??諛섏궗'濡?諛붽씀湲?,
                "???먮Ц 臾몄옣???덉쑝硫?洹몃?濡?由ы뵆?덉씠",
            ],
            show_controls=True,
        )

    _two_pane_layout(left_area, right_area)


def _render_voca_timebomb(items: List[Dict[str, Any]]) -> None:
    _apply_armory_css()
    st.info("VOCA ?ㅼ쟾? 湲곗〈 濡쒖쭅 ?좎?(異붽? ?붽뎄 ??EXAM 洹쒖튃???숈씪 ?곸슜 媛??.")

# =========================================================
# P5 TRAIN (CLEAN) : 寃뚯엫???숈뒿 ?붾㈃ (?먯젙/HUD/?좉툑 ?쒓굅)
# =========================================================
def _render_p5_train_clean(items: List[Dict[str, Any]]) -> None:
    """P5 TRAIN (?숈뒿) ??臾몄젣吏?+ ?명듃(BRIEF)

    ???뺤젙 諛섏쁺(?잹/?좥/?줐)
    - ?좏깮 利됱떆 BRIEF ?먮룞 ?쇱묠 (BRIEF 踰꾪듉 ?쒓굅)
    - 踰꾪듉 2媛쒕쭔: '??臾몄젣吏묒뿉???쒓굅' / '?∽툘 ?ㅼ쓬'
    - Undo ?놁쓬
    - 蹂댁“ ?좎뼵: '???댁젣 ???由곕떎' (?곗씠???ъ슜 ????
    - BRIEF ?명듃 援ъ“: ?뺣떟 ?ъ씤???뺢킅) ???댁꽍(?고븘) ???쒗뿕 ?ъ씤??蹂쇳렂)
    """

    _apply_armory_css()

    p5_items = _filter_p5(items)
    ammo = len(p5_items)
    if ammo <= 0:
        st.info("P5 蹂묎린怨좉? 鍮꾩뼱 ?덉뒿?덈떎.")
        return

    st.session_state.setdefault("p5_clean_idx", random.randrange(ammo))
    idx = int(st.session_state["p5_clean_idx"]) % ammo
    q = p5_items[idx]

    st.session_state.setdefault("p5_clean_pick", None)
    st.session_state.setdefault("p5_clean_brief", False)
    st.session_state.setdefault("p5_clean_i_wont_miss", False)

    sentence = str(q.get("sentence", "")).strip()
    choices: List[str] = list(q.get("choices", []) or [])

    answer = (q.get("answer") or q.get("correct") or q.get("correct_answer") or q.get("ans") or "")
    answer = str(answer).strip()

    ko = (q.get("ko") or q.get("korean") or q.get("translation") or q.get("kr") or q.get("meaning_ko") or "")
    ko = str(ko).strip()

    explain = (q.get("explain") or q.get("explanation") or q.get("commentary") or q.get("note") or "")
    explain = str(explain).strip()

    # ???댁꽕? 湲몃㈃ ?ㅼ썙?쒕쭔(20~30珥?泥대쪟瑜??꾪빐 '吏㏐쾶')
    def _to_exam_point(s: str) -> str:
        s = (s or "").strip()
        if not s:
            return "(?ъ씤???놁쓬)"
        for sep in [" - ", " : ", " | ", "\t", "|", ":", "-", "??"]:]:
            s = s.replace(sep, ". ")
        parts = [p.strip() for p in s.split(".") if p.strip()]
        if not parts:
            return s[:120]
        return " / ".join(parts[:2])

    exam_point = _to_exam_point(explain)

    # ---------------------------
    # 臾몄젣(臾몄젣吏?諛뺤뒪)
    # ---------------------------
    st.markdown(
        f"""
        <div class="p5-qbox">
          <div class="p5-qtext">?쭬 {sentence}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    # ---------------------------
    # ?좏깮吏 2x2 + A/B/C/D (?좏깮 利됱떆 BRIEF ?먮룞 ?ㅽ뵂)
    # ---------------------------
    labels = ["(A)", "(B)", "(C)", "(D)"]
    cols1 = st.columns(2, gap="large")
    cols2 = st.columns(2, gap="large")
    grid = cols1 + cols2

    for i, opt in enumerate(choices[:4]):
        with grid[i]:
            st.markdown('<div class="p5-optbtn">', unsafe_allow_html=True)
            if st.button(
                f"{labels[i]}  {opt}",
                key=f"p5_clean_opt_{idx}_{i}",
                use_container_width=True,
            ):
                st.session_state["p5_clean_pick"] = opt
                st.session_state["p5_clean_brief"] = True
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:22px'></div>", unsafe_allow_html=True)

    # ---------------------------
    # BRIEF ?명듃: ?좏깮?덉쓣 ?뚮쭔 ?먮룞?쇰줈 ?쇱튂湲?    # ---------------------------
    if st.session_state.get("p5_clean_brief", False):
        picked = st.session_state.get("p5_clean_pick")
        judged = (picked is not None) and bool(answer)
        ok = bool(judged and (str(picked).strip() == answer))

        verdict = "???뺣떟" if ok else "???ㅻ떟"
        picked_txt = str(picked).strip() if picked else "(?좏깮 ?놁쓬)"

        st.markdown(
            f"""
            <div class="p5-note">
              <div class="hd">?륅툘 BRIEF ?명듃</div>

              <div class="p5-row">
                <div class="p5-tag">???뺣떟 ?ъ씤??/div><br/>
                <span class="p5-hl">Answer 쨌 {answer or '(?뺣떟 ?놁쓬)'}</span>
                <span class="p5-judge">{verdict} 쨌 ?덉쓽 ?좏깮: <b>{picked_txt}</b></span>
              </div>

              <div class="p5-row">
                <div class="p5-tag">???댁꽍 (?고븘)</div>
                <div class="p5-pencil">{ko or '(?댁꽍 ?놁쓬)'}</div>
              </div>

              <div class="p5-row">
                <div class="p5-tag">???쒗뿕 ?ъ씤??(蹂쇳렂)</div>
                <div class="p5-pen">{exam_point}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ??蹂댁“ ?좎뼵(?곗씠???ъ슜 ????
        st.checkbox(
            "???댁젣 ???由곕떎",
            key="p5_clean_i_wont_miss",
        )

    # ---------------------------
    # ?섎떒 踰꾪듉 2媛쒕쭔 (Undo ?놁쓬)
    # ---------------------------
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    b1, b2 = st.columns(2, gap="large")

    with b1:
        if st.button("??臾몄젣吏묒뿉???쒓굅", use_container_width=True, key="p5_clean_discard_btn"):
            # ?덉쟾 ??젣: sentence + answer + choices 議고빀?쇰줈 ?쒓굅
            target = (sentence, answer, tuple(choices))
            new_items: List[Dict[str, Any]] = []
            for it in items:
                if it.get("source") == "P5":
                    key = (
                        str(it.get("sentence", "")).strip(),
                        str(it.get("answer", it.get("correct", ""))).strip(),
                        tuple(it.get("choices", []) or []),
                    )
                    if key == target:
                        continue
                new_items.append(it)

            _save_armory_items(new_items)

            # ?곹깭 由ъ뀑(Undo ?놁쓬)
            st.session_state["p5_clean_pick"] = None
            st.session_state["p5_clean_brief"] = False
            st.session_state["p5_clean_i_wont_miss"] = False

            # ?ㅼ쓬 臾몄젣
            next_ammo = max(1, ammo - 1)
            st.session_state["p5_clean_idx"] = random.randrange(next_ammo)
            st.rerun()

    with b2:
        if st.button("?∽툘 ?ㅼ쓬", use_container_width=True, key="p5_clean_next_btn"):
            st.session_state["p5_clean_pick"] = None
            st.session_state["p5_clean_brief"] = False
            st.session_state["p5_clean_i_wont_miss"] = False
            st.session_state["p5_clean_idx"] = random.randrange(ammo)
            st.rerun()



# =========================
# SNAPQ ENTRYPOINT (AUTO)
# =========================


# =========================
# SNAPQ SECRET ARMORY (MIN UI)
# =========================
def render():
    import streamlit as st
    from pathlib import Path
    import json

    st.markdown("<h1 style='margin-top:0'>?윢 Secret Armory</h1>", unsafe_allow_html=True)
    st.caption("?ㅻ뒛 紐⑺몴: 臾닿린怨??섏옉?쇺??곹깭濡??앸궡湲? (?곗씠???뚯씪???덉쑝硫??먮룞 ?쒖떆)")

    root = Path(__file__).resolve().parents[2]  # SNAPQ_TOEIC/
    data_candidates = [
        root / "data",
        root / "app" / "data",
        root / "data" / "stats",
        root / "data" / "armory",
    ]

    st.markdown("### ?벀 臾닿린怨??곗씠???먯깋")
    found_files = []
    for d in data_candidates:
        if d.exists():
            for pat in ["*armory*.json*", "*saved*.json*", "*vocab*.json*", "*p5*.json*", "*p7*.json*"]:
                found_files += list(d.rglob(pat))
    # dedupe
    uniq = []
    seen = set()
    for f in found_files:
        if f.as_posix() not in seen and f.is_file():
            uniq.append(f); seen.add(f.as_posix())

    if not uniq:
        st.info("?꾩옱 臾닿린怨??곗씠???뚯씪??李얠? 紐삵뻽?댁슂. (?뺤긽)\\n"
                "吏湲덉? UI留?癒쇱? ?대젮?먭퀬, ?댁씪 ?곗씠???곌껐留?遺숈씠硫??⑸땲??")
        st.markdown("### ???ㅻ뒛???밸━ 議곌굔 ?ъ꽦")
        st.success("HUB ??ARMORY ?곌껐 ?꾨즺 + 臾닿린怨??붾㈃ ?뺤긽 異쒕젰")
        return

    st.success(f"諛쒓껄???뚯씪: {len(uniq)}媛?)
    with st.expander("?뱞 諛쒓껄???뚯씪 紐⑸줉 蹂닿린", expanded=True):
        for f in uniq[:50]:
            st.write("??, str(f.relative_to(root)))
        if len(uniq) > 50:
            st.write(f"... (+{len(uniq)-50} more)")

    st.markdown("### ?뵊 ?뚯씪 ?댁슜 誘몃━蹂닿린")
    pick = st.selectbox("?댁뼱蹂??뚯씪 ?좏깮", [str(f.relative_to(root)) for f in uniq], index=0)
    fp = root / pick

    try:
        txt = fp.read_text(encoding="utf-8", errors="ignore")
        # try json preview
        try:
            obj = json.loads(txt)
            st.json(obj if isinstance(obj, (dict, list)) else {"value": obj})
        except Exception:
            st.text(txt[:4000])
    except Exception as e:
        st.error(f"?뚯씪 ?쎄린 ?ㅽ뙣: {e}")



