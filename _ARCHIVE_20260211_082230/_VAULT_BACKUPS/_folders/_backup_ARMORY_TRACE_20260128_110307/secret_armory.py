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
# UI/CSS (SAFE) : 밝기 + 문제집/시험지 + 우측 HUD
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

/* ✅ 전체 배경: 너무 어둡지 않게(밝기 올림) */
section[data-testid="stAppViewContainer"]{
  background:
    radial-gradient(1000px 700px at 10% 10%, rgba(190,120,255,.24), transparent 62%),
    radial-gradient(900px 620px at 90% 8%, rgba(120,160,255,.18), transparent 62%),
    linear-gradient(135deg, #101a28 0%, #162235 45%, #0f1724 100%) !important;
}

/* 컨테이너 투명 */
section[data-testid="stAppViewContainer"] div[data-testid="stContainer"],
section[data-testid="stAppViewContainer"] div[data-testid="stVerticalBlock"],
section[data-testid="stAppViewContainer"] div[data-testid="column"] > div{
  background: transparent !important;
}

/* ✅ 왼쪽 메인(문제집/시험지) 카드 */
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

/* ✅ 학습 패널(정답/해석/해설) */
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

/* ✅ Streamlit alert도 흰 패널로 강제 */
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

/* ✅ 선택지 버튼: 카드형(학습/시험 공통) */
section[data-testid="stAppViewContainer"] .stButton > button{
  border-radius: 16px !important;
  font-weight: 950 !important;
  min-height: 56px !important;
  font-size: 18px !important;
  border: 1px solid rgba(255,255,255,.18) !important;
  background: linear-gradient(180deg, rgba(255,255,255,.10), rgba(255,255,255,.06)) !important;
  box-shadow: 0 14px 34px rgba(0,0,0,.22) !important;
}



/* ✅ P5 TRAIN(학습) 전용: 문제집(흰 종이) + 2x2 선택지 */
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
  font-size: clamp(20px, 1.55vw, 26px) !important; /* ✅ 문제 = 더 큼 */
  line-height: 1.35 !important;
  text-shadow: none !important;
}
.p5-optbtn .stButton > button{
  background: rgba(255,255,255,.92) !important;
  color: var(--sa-ink) !important;
  border: 2px solid rgba(15,23,42,.20) !important;
  font-size: 20px !important; /* ✅ 선택지 = 문제보다 작게(체감 1.2배) */
  min-height: 72px !important;
  box-shadow: 0 14px 30px rgba(0,0,0,.16) !important;
}
.p5-optbtn .stButton > button:hover{
  border: 2px solid rgba(15,23,42,.45) !important;
  transform: translateY(-1px);
}
.p5-optbtn .stButton > button:active{ transform: translateY(0px); }

/* =========================================================
   ✅ P5 TRAIN 노트(BRIEF) 스타일: 형광펜/연필/볼펜
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

/* ✅ TRAIN 하단 버튼(문제집에서 제거/다음) – 조용한 버튼 */
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
/* ✅ 우측 HUD 카드 */
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

/* ✅ 시험 모드 타이머 강조 */
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

/* ✅ 모바일: 80/20이 세로로 쌓이게 */
@media (max-width: 768px){
  section[data-testid="stAppViewContainer"] .stButton > button{
    min-height: 66px !important;
    font-size: 20px !important;
  }
  .sa-timer{ font-size: 26px; }
}
/* ============================================================
   P5 EXAM VISIBILITY OVERRIDE (SAFE)
   - 시험지(왼쪽) 글자 확실히 검정
   - 선택지 버튼은 밝은 종이 + 검정 글자
   - 우측 HUD 버튼은 어두운 톤 유지
   ============================================================ */

/* 시험지 카드/본문은 무조건 진하게 */
.sa-book, .sa-book *{
  color: var(--sa-ink) !important;
  opacity: 1 !important;
  text-shadow: none !important;
  filter: none !important;
}

/* 시험지 내부 핵심 텍스트 더 진하게 */
.sa-q .stem{ color: var(--sa-ink) !important; font-weight: 950 !important; }
.sa-q .hint{ color: rgba(15,23,42,.70) !important; font-weight: 900 !important; }

/* 기본 버튼(왼쪽 선택지)은 '종이+검정'으로 강제 */
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

/* 우측 HUD 카드 내부 이동 버튼은 다시 어둡게(시험장 방해 최소화) */
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
# VOCA robust extractor (기존 유지)
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
        for sep in [" - ", " : ", " | ", "\t", "|", ":", "-", "—"]:
            if sep in s:
                left, right = s.split(sep, 1)
                return _postprocess_vocab_pair(left, right)
        return _postprocess_vocab_pair(s, "뜻")

    return ("WORD", "뜻")


# =========================================================
# Armory IO (list 구조 유지)
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
          <div class="h">🎛 HUD · 키워드</div>
          <div class="sa-chip">🎮 {mode_label}</div>
          <div class="sa-chip">📦 탄약 {ammo}</div>
          <div class="sa-chip">🔥 스트릭 {streak}</div>
          <div class="sa-chip">⚡ 콤보 {combo}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if extra_lines:
        st.markdown('<div class="sa-hudcard"><div class="h">🧾 미션</div>', unsafe_allow_html=True)
        for ln in extra_lines:
            st.write(ln)
        st.markdown("</div>", unsafe_allow_html=True)

    if show_controls:
        st.markdown('<div class="sa-hudcard"><div class="h">🔁 이동</div>', unsafe_allow_html=True)
        st.button("↩ 작전 선택으로", use_container_width=True, key=f"hud_back_{mode_label}")
        st.button("🏠 본부 복귀", use_container_width=True, key=f"hud_home_{mode_label}")
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
# TRAIN (학습) : 문제집 + 판정 후 정답/해석/해설 페이지 내부 표시
# =========================================================
def _render_p5_learning(items: List[Dict[str, Any]]) -> None:
    """(LEGACY) 기존 TRAIN 렌더러가 어딘가에서 호출되더라도
    항상 '문제집+노트' 최신 TRAIN UI로 강제 연결한다.
    """
    _render_p5_train_clean(items)
    return

    # ✅ 실제 저장된 문제를 우선 사용 (없으면 데모)
    if ammo > 0:
        pool = p5_items
        use_saved = True
    else:
        pool = [
            {
                "sentence": "Our company is trying to _____ costs without reducing quality.",
                "choices": ["increase", "raise", "cut", "spread"],
                "answer": "cut",
                "ko": "우리 회사는 품질을 떨어뜨리지 않으면서 비용을 줄이려고 한다.",
                "explain": "cut costs = 비용을 줄이다.",
            },
            {
                "sentence": "Please find the revised file _____ to this email.",
                "choices": ["attached", "attaching", "attachment", "to attach"],
                "answer": "attached",
                "ko": "이 이메일에 첨부된 수정 파일을 확인해 주세요.",
                "explain": "file attached to ~ : ~에 첨부된 파일 (과거분사 수식).",
            },
        ]
        use_saved = False

    # 문제집 느낌: 한 문제를 고치고 넘어감 (세션 고정)
    st.session_state.setdefault("p5_train_idx", random.randrange(len(pool)))
    q = pool[int(st.session_state["p5_train_idx"]) % len(pool)]

    # 상태
    st.session_state.setdefault("p5_train_streak", 0)
    st.session_state.setdefault("p5_train_combo", 0)
    st.session_state.setdefault("p5_train_judged", False)
    st.session_state.setdefault("p5_train_last_ok", None)

    # 학습 패널 버튼(페이지 내부)
    st.session_state.setdefault("p5_train_show_answer", False)
    st.session_state.setdefault("p5_train_show_ko", False)
    st.session_state.setdefault("p5_train_show_explain", False)

    def left_area():
        st.markdown(
            f"""
            <div class="sa-book">
              <div class="title">📗 P5 학습 모드 · 문제집 훈련</div>
              <div class="sub">이 페이지에서 끝낸다: 판정 → 정답/해석/해설 펼치기 → 폐기/다음 문제</div>

              <div class="sa-q">
                <div class="stem">🧠 {q.get('sentence','')}</div>
                <div class="hint">선택지 선택 후 <b>판정</b>을 눌러야 학습 패널이 열린다.</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### 🎯 선택지")
        picked = _choice_buttons_vertical_set("p5_train_pick", q.get("choices", []))

        c1, c2, c3 = st.columns(3, gap="large")
        with c1:
            if st.button("🧹 폐기", use_container_width=True, key="p5_train_discard"):
                # 학습자가 공부 끝낸 문제는 폐기(= 다음 문제로 이동 + 패널 닫기)
                st.session_state["p5_train_pick"] = None
                st.session_state["p5_train_judged"] = False
                st.session_state["p5_train_last_ok"] = None
                st.session_state["p5_train_show_answer"] = False
                st.session_state["p5_train_show_ko"] = False
                st.session_state["p5_train_show_explain"] = False
                st.success("폐기 완료. 다음 문제로 넘어가라.")
                # 다음 문제
                st.session_state["p5_train_idx"] = (int(st.session_state["p5_train_idx"]) + 1) % len(pool)
                st.rerun()

        with c2:
            if st.button("🔎 판정", use_container_width=True, key="p5_train_judge"):
                if not picked:
                    st.warning("먼저 선택지를 골라라.")
                else:
                    ok = (picked == q.get("answer"))
                    st.session_state["p5_train_judged"] = True
                    st.session_state["p5_train_last_ok"] = ok

                    if ok:
                        st.success("✅ 정답. 감각 유지!")
                        st.session_state["p5_train_streak"] = int(st.session_state["p5_train_streak"]) + 1
                        st.session_state["p5_train_combo"] = int(st.session_state["p5_train_combo"]) + 1
                    else:
                        st.error(f"❌ 오답. 정답: {q.get('answer','')}")
                        st.session_state["p5_train_streak"] = 0
                        st.session_state["p5_train_combo"] = 0

        with c3:
            if st.button("➡️ 다음 문제", use_container_width=True, key="p5_train_next"):
                st.session_state["p5_train_pick"] = None
                st.session_state["p5_train_judged"] = False
                st.session_state["p5_train_last_ok"] = None
                st.session_state["p5_train_show_answer"] = False
                st.session_state["p5_train_show_ko"] = False
                st.session_state["p5_train_show_explain"] = False
                st.session_state["p5_train_idx"] = (int(st.session_state["p5_train_idx"]) + 1) % len(pool)
                st.rerun()

        # ✅ 학습 패널: 판정 후 버튼으로 페이지 안에서 펼치기
        if st.session_state.get("p5_train_judged", False):
            st.markdown("### 📌 학습 패널 (정답/해석/해설)")
            b1, b2, b3 = st.columns(3, gap="large")
            with b1:
                if st.button("✅ 정답", use_container_width=True, key="train_btn_answer"):
                    st.session_state["p5_train_show_answer"] = True
            with b2:
                if st.button("📖 해석", use_container_width=True, key="train_btn_ko"):
                    st.session_state["p5_train_show_ko"] = True
            with b3:
                if st.button("🧩 해설", use_container_width=True, key="train_btn_explain"):
                    st.session_state["p5_train_show_explain"] = True

            if st.session_state.get("p5_train_show_answer", False):
                st.markdown(
                    f"""
                    <div class="sa-panel">
                      <div class="k">정답</div>
                      <div><b>{q.get('answer','')}</b></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            if st.session_state.get("p5_train_show_ko", False):
                st.markdown(
                    f"""
                    <div class="sa-panel">
                      <div class="k">해석</div>
                      <div>{q.get('ko','(해석 없음)')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            if st.session_state.get("p5_train_show_explain", False):
                st.markdown(
                    f"""
                    <div class="sa-panel">
                      <div class="k">해설</div>
                      <div>{q.get('explain','(해설 없음)')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.caption("🔒 학습 패널 잠금: 판정 후 열림")

        if use_saved:
            st.caption("📦 현재는 '저장된 P5 문제'로 학습 중.")
        else:
            st.caption("📦 저장된 P5 문제가 없어 데모 문제로 표시 중.")

    def right_area():
        _hud_right(
            mode_label="TRAIN",
            ammo=ammo,
            streak=int(st.session_state["p5_train_streak"]),
            combo=int(st.session_state["p5_train_combo"]),
            extra_lines=[
                "• 목표: 문제집처럼 한 문제 완전 정리",
                "• 흐름: 판정 → 패널 열기 → 폐기/다음",
            ],
            show_controls=True,
        )

    _two_pane_layout(left_area, right_area)


# =========================================================
# LIVE (시험) : 5문제/30초 세트 + 올정답이면 자동 폐기 / 1개라도 틀리면 유지
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

    # ✅ 시험은 반드시 '저장된 P5'에서만 진행 (룰: 5문제 30초)
    def left_area():
        st.markdown(
            """
            <div class="sa-book">
              <div class="title">📝 P5 시험 모드 · 5문항 타임어택</div>
              <div class="sub">룰: 5문제/30초. 5개 모두 정답이면 <b>자동 폐기</b>. 1개라도 틀리면 <b>유지(다시 저장)</b>.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if ammo < P5_EXAM_TOTAL_Q:
            st.warning(f"저장된 P5 문제가 부족합니다. (필요: {P5_EXAM_TOTAL_Q}개 / 현재: {ammo}개)")
            return
        # 시작 UI 제거(첫 페이지 제거): 진입 즉시 자동 출격
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
# 타이머 자동 갱신
        if st_autorefresh is not None:
            st_autorefresh(interval=200, key="p5_exam_tick")

        now = time.time()
        deadline = float(st.session_state.get("p5_exam_deadline", now))
        remaining = max(0.0, deadline - now)

        # 시간 종료 처리
        if remaining <= 0 and not st.session_state.get("p5_exam_done", False):
            st.session_state["p5_exam_wrong"] = True  # 시간초과 = 실패
            st.session_state["p5_exam_done"] = True
            st.session_state["p5_exam_msg"] = ("error", "⏰ 시간 초과. 시험 실패(유지).")
            st.rerun()

        # 진행
        exam_ids: List[int] = st.session_state.get("p5_exam_ids", [])
        q_idx = int(st.session_state.get("p5_exam_idx", 0))
        wrong = bool(st.session_state.get("p5_exam_wrong", False))
        score = int(st.session_state.get("p5_exam_score", 0))
        done = bool(st.session_state.get("p5_exam_done", False))

        # 상단 타이머(시험지 느낌)
        timer_cls = "sa-timer red" if remaining <= 8 else "sa-timer"
        st.markdown(f"<div class='{timer_cls}'>⏱ {remaining:04.1f}s</div>", unsafe_allow_html=True)
        st.progress(min(1.0, remaining / max(0.1, P5_EXAM_TOTAL_SECONDS)))

        st.caption(f"진행: {min(q_idx+1, P5_EXAM_TOTAL_Q)} / {P5_EXAM_TOTAL_Q}   |   점수: {score} / {P5_EXAM_TOTAL_Q}")

        # 종료 화면
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
                    "<div class='sa-panel'><div class='k'>결과</div><div>🎉 5문제 올정답! 자동 폐기 완료.</div></div>",
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    "<div class='sa-panel'><div class='k'>결과</div><div>❗ 한 문제라도 실패 → 문제는 유지(다시 저장).</div></div>",
                    unsafe_allow_html=True,
                )

            c1, c2 = st.columns(2, gap="large")
            with c1:
                if st.button("🔁 다시 시험", use_container_width=True, key="p5_exam_retry"):
                    _exam_reset_state()
                    st.rerun()
            with c2:
                if st.button("🧹 시험 종료(초기화)", use_container_width=True, key="p5_exam_exit"):
                    _exam_reset_state()
                    st.rerun()
            return

        # 현재 문제
        cur_global_idx = exam_ids[q_idx]
        q = p5_items[cur_global_idx]
        sentence = q.get("sentence", "")
        choices = q.get("choices", [])
        answer = q.get("answer", "")

        st.markdown(
            f"""
            <div class="sa-book" style="margin-top:12px;">
              <div class="title">📄 시험지</div>
              <div class="sub">선택지 클릭 = 즉시 제출 (판정 버튼 없음)</div>
              <div class="sa-q">
                <div class="stem">🧠 {sentence}</div>
                <div class="hint">5문제/30초. 올정답이면 자동 폐기.</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        def on_pick(ch: str) -> None:
            nonlocal q_idx, score, wrong
            if ch == answer:
                st.session_state["p5_exam_score"] = score + 1
                st.session_state["p5_exam_msg"] = ("success", "✅ 명중.")
            else:
                st.session_state["p5_exam_wrong"] = True
                st.session_state["p5_exam_msg"] = ("error", f"❌ 오답. 정답: {answer}")

            # 다음 문제로
            st.session_state["p5_exam_idx"] = q_idx + 1

            # 마지막 문제였으면 종료 처리
            if (q_idx + 1) >= P5_EXAM_TOTAL_Q:
                # 최종 판정
                final_score = int(st.session_state.get("p5_exam_score", 0))
                final_wrong = bool(st.session_state.get("p5_exam_wrong", False))
                # 지금 문제에서 점수 반영이 아직이면 보정
                if ch == answer:
                    final_score = final_score  # already incremented
                else:
                    final_wrong = True

                # 시간도 체크
                now2 = time.time()
                rem2 = max(0.0, float(st.session_state.get("p5_exam_deadline", now2)) - now2)
                if rem2 <= 0:
                    final_wrong = True

                # 올정답이면 자동 폐기
                if (not final_wrong) and final_score >= P5_EXAM_TOTAL_Q:
                    # items(list)에서 해당 5개를 제거 (matching by object identity/contents)
                    # 안전: sentence+answer 기준으로 제거
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
                    st.session_state["p5_exam_msg"] = ("success", f"🎉 올정답! 자동 폐기 완료 ({removed}개 제거)")
                else:
                    # 실패면 유지(= 아무것도 안 함)
                    st.session_state["p5_exam_done"] = True
                    st.session_state["p5_exam_msg"] = ("error", "❗ 실패. 문제는 유지(다시 저장).")

        st.markdown("#### 🎯 선택지 (즉시 제출)")
        _choice_buttons_grid_submit(choices, on_pick=on_pick, key_prefix=f"p5_exam_{q_idx}")

        msg = st.session_state.get("p5_exam_msg")
        if msg:
            kind, text = msg
            if kind == "success":
                st.success(text)
            else:
                st.error(text)

        # 중단/리셋
        c1, c2 = st.columns(2, gap="large")
        with c1:
            if st.button("🧨 시험 중단", use_container_width=True, key="p5_exam_abort"):
                _exam_reset_state()
                st.warning("시험 중단. 문제는 유지.")
                st.rerun()
        with c2:
            if st.button("🧹 강제 리셋", use_container_width=True, key="p5_exam_reset"):
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
            f"• 세트: {P5_EXAM_TOTAL_Q}문제",
            f"• 제한: {int(P5_EXAM_TOTAL_SECONDS)}초",
            f"• 진행: {min(q_idx+1, P5_EXAM_TOTAL_Q)} / {P5_EXAM_TOTAL_Q}" if active else "• 대기 중",
            f"• 점수: {score} / {P5_EXAM_TOTAL_Q}" if active else "• 점수: -",
            "• 상태: 실패(유지)" if wrong else "• 상태: 올정답이면 폐기",
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
            st.markdown(f"<div class='{cls}'>⏱ {remaining:04.1f}s</div>", unsafe_allow_html=True)

    _two_pane_layout(left_area, right_area)


# =========================================================
# VOCA TRAIN/LIVE (기존 유지)
# =========================================================
def _render_voca_flip(items: List[Dict[str, Any]]) -> None:
    _apply_armory_css()
    voca_items = _filter_voca(items)
    if not voca_items:
        st.info("VOCA 탄약이 없습니다. (병기고에 저장된 단어가 없어요)")
        return

    st.session_state.setdefault("voca_flip_idx", 0)
    idx = int(st.session_state["voca_flip_idx"]) % len(voca_items)
    word, meaning = _extract_vocab_pair(voca_items[idx])

    def left_area():
        st.markdown(
            f"""
            <div class="sa-book">
              <div class="title">🪖 VOCA 학습 · 단어수첩</div>
              <div class="sub">카드처럼 넘기며 외운다.</div>

              <div class="sa-q">
                <div class="stem">🧠 WORD · {word}</div>
                <div class="hint">버튼으로 뜻 공개 → 다음</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2, c3 = st.columns(3, gap="large")
        with c1:
            if st.button("📖 뜻 보기", use_container_width=True):
                st.markdown(
                    f"<div class='sa-panel'><div class='k'>뜻</div><div>{meaning}</div></div>",
                    unsafe_allow_html=True,
                )
        with c2:
            if st.button("➡️ 다음", use_container_width=True):
                st.session_state["voca_flip_idx"] = idx + 1
                st.rerun()
        with c3:
            st.button("🧹 숙달(폐기)", use_container_width=True)

    def right_area():
        _hud_right(
            mode_label="VOCA-TRAIN",
            ammo=len(voca_items),
            streak=0,
            combo=0,
            extra_lines=["• 목표: '바로 나오는 단어' 만들기"],
            show_controls=True,
        )

    _two_pane_layout(left_area, right_area)


def _render_voca_timebomb(items: List[Dict[str, Any]]) -> None:
    _apply_armory_css()
    st.info("VOCA 실전은 기존 로직 유지(추가 요구 시 EXAM 규칙도 동일 적용 가능).")

# =========================================================
# P5 TRAIN (CLEAN) : 게임형 학습 화면 (판정/HUD/잠금 제거)
# =========================================================
def _render_p5_train_clean(items: List[Dict[str, Any]]) -> None:
    """P5 TRAIN (학습) – 문제집 + 노트(BRIEF)

    ✅ 확정 반영(①B/②A/③A)
    - 선택 즉시 BRIEF 자동 펼침 (BRIEF 버튼 제거)
    - 버튼 2개만: '✅ 문제집에서 제거' / '➡️ 다음'
    - Undo 없음
    - 보조 선언: '☑ 이제 안 틀린다' (데이터 사용 안 함)
    - BRIEF 노트 구조: 정답 포인트(형광) → 해석(연필) → 시험 포인트(볼펜)
    """

    _apply_armory_css()

    p5_items = _filter_p5(items)
    ammo = len(p5_items)
    if ammo <= 0:
        st.info("P5 병기고가 비어 있습니다.")
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

    # ✅ 해설은 길면 키워드만(20~30초 체류를 위해 '짧게')
    def _to_exam_point(s: str) -> str:
        s = (s or "").strip()
        if not s:
            return "(포인트 없음)"
        for sep in ["\n", "•", "-", "—", ";"]:
            s = s.replace(sep, ". ")
        parts = [p.strip() for p in s.split(".") if p.strip()]
        if not parts:
            return s[:120]
        return " / ".join(parts[:2])

    exam_point = _to_exam_point(explain)

    # ---------------------------
    # 문제(문제집 박스)
    # ---------------------------
    st.markdown(
        f"""
        <div class="p5-qbox">
          <div class="p5-qtext">🧠 {sentence}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    # ---------------------------
    # 선택지 2x2 + A/B/C/D (선택 즉시 BRIEF 자동 오픈)
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
    # BRIEF 노트: 선택했을 때만 자동으로 펼치기
    # ---------------------------
    if st.session_state.get("p5_clean_brief", False):
        picked = st.session_state.get("p5_clean_pick")
        judged = (picked is not None) and bool(answer)
        ok = bool(judged and (str(picked).strip() == answer))

        verdict = "✅ 정답" if ok else "❌ 오답"
        picked_txt = str(picked).strip() if picked else "(선택 없음)"

        st.markdown(
            f"""
            <div class="p5-note">
              <div class="hd">✏️ BRIEF 노트</div>

              <div class="p5-row">
                <div class="p5-tag">① 정답 포인트</div><br/>
                <span class="p5-hl">Answer · {answer or '(정답 없음)'}</span>
                <span class="p5-judge">{verdict} · 너의 선택: <b>{picked_txt}</b></span>
              </div>

              <div class="p5-row">
                <div class="p5-tag">② 해석 (연필)</div>
                <div class="p5-pencil">{ko or '(해석 없음)'}</div>
              </div>

              <div class="p5-row">
                <div class="p5-tag">③ 시험 포인트 (볼펜)</div>
                <div class="p5-pen">{exam_point}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ✅ 보조 선언(데이터 사용 안 함)
        st.checkbox(
            "☑ 이제 안 틀린다",
            key="p5_clean_i_wont_miss",
        )

    # ---------------------------
    # 하단 버튼 2개만 (Undo 없음)
    # ---------------------------
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    b1, b2 = st.columns(2, gap="large")

    with b1:
        if st.button("✅ 문제집에서 제거", use_container_width=True, key="p5_clean_discard_btn"):
            # 안전 삭제: sentence + answer + choices 조합으로 제거
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

            # 상태 리셋(Undo 없음)
            st.session_state["p5_clean_pick"] = None
            st.session_state["p5_clean_brief"] = False
            st.session_state["p5_clean_i_wont_miss"] = False

            # 다음 문제
            next_ammo = max(1, ammo - 1)
            st.session_state["p5_clean_idx"] = random.randrange(next_ammo)
            st.rerun()

    with b2:
        if st.button("➡️ 다음", use_container_width=True, key="p5_clean_next_btn"):
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

    st.markdown("<h1 style='margin-top:0'>🟣 Secret Armory</h1>", unsafe_allow_html=True)
    st.caption("오늘 목표: 무기고 ‘작동’ 상태로 끝내기. (데이터 파일이 있으면 자동 표시)")

    root = Path(__file__).resolve().parents[2]  # SNAPQ_TOEIC/
    data_candidates = [
        root / "data",
        root / "app" / "data",
        root / "data" / "stats",
        root / "data" / "armory",
    ]

    st.markdown("### 📦 무기고 데이터 탐색")
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
        st.info("현재 무기고 데이터 파일을 찾지 못했어요. (정상)\\n"
                "지금은 UI만 먼저 살려두고, 내일 데이터 연결만 붙이면 됩니다.")
        st.markdown("### ✅ 오늘의 승리 조건 달성")
        st.success("HUB → ARMORY 연결 완료 + 무기고 화면 정상 출력")
        return

    st.success(f"발견된 파일: {len(uniq)}개")
    with st.expander("📄 발견된 파일 목록 보기", expanded=True):
        for f in uniq[:50]:
            st.write("•", str(f.relative_to(root)))
        if len(uniq) > 50:
            st.write(f"... (+{len(uniq)-50} more)")

    st.markdown("### 🔎 파일 내용 미리보기")
    pick = st.selectbox("열어볼 파일 선택", [str(f.relative_to(root)) for f in uniq], index=0)
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
        st.error(f"파일 읽기 실패: {e}")

