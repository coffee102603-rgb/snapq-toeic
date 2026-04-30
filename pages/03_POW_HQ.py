"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE:     pages/03_POW_HQ.py (v2 — 학습장 + 시험장)
ROLE:     단어 포로수용소
VERSION:  SnapQ TOEIC V3 — 2026.04.30
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHILOSOPHY:
    학습 → 평가 분리.
    먼저 외우게 하고, 그 다음 시험.

PAGE FLOW:
    [메인 — 감방 2개]
        🥉 마스터 감방 / 🎯 수배 감방
        ↓
    [학습장 — 낱말카드 10개]
        2x5 그리드, 클릭 시 영어 ↔ 한글 토글
        ↓
    [⚔️ 시험장 입장]
        ↓
    [시험장 — 두더지 시험]
        무작위 순서, 4지선다, 3초 타이머
        오답/시간초과 → 수배 감방 직행
        ↓
    [결과 화면]
        ✅ 정답 N개
        🎯 수배 감방행 N개
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import random
from datetime import date
from pathlib import Path
from typing import Dict, List

import streamlit as st
import streamlit.components.v1 as components

from app.core.access_guard import require_access
from app.core.inbody_db import init_db
from app.core.word_mastery import (
    log_word_attempt,
    get_mastery_stats,
    get_unmastered_words,
    get_wanted_words,
)


# ═══════════════════════════════════════════════════════════════
# 페이지 설정
# ═══════════════════════════════════════════════════════════════

st.set_page_config(
    page_title='단어 포로수용소',
    page_icon='💀',
    layout='wide',
    initial_sidebar_state='collapsed'
)

nickname = require_access()
init_db()

_qs_nick = st.query_params.get("nick", "")
_qs_ag = st.query_params.get("ag", "")
if _qs_nick and _qs_ag == "1":
    if not st.session_state.get("battle_nickname"):
        st.session_state["battle_nickname"] = _qs_nick
        st.session_state["nickname"] = _qs_nick
        nickname = _qs_nick


# ═══════════════════════════════════════════════════════════════
# 상수
# ═══════════════════════════════════════════════════════════════

BASE = Path(__file__).parent.parent
WORD_POOL_PATH = BASE / "data" / "word_pool_categorized.json"

GAME_WORD_COUNT = 10  # 카드 10개!
TIMER_SECONDS = 3.0


@st.cache_data
def load_word_pool() -> dict:
    if WORD_POOL_PATH.exists():
        try:
            return json.loads(WORD_POOL_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


# ═══════════════════════════════════════════════════════════════
# 페이지 모드
# ═══════════════════════════════════════════════════════════════

PAGE_MODE_KEY = "_pow_mode"          # main / study / exam / result
GAME_WORDS_KEY = "_pow_words"
GAME_TYPE_KEY = "_pow_type"          # master / wanted
EXAM_RESULTS_KEY = "_pow_results"    # 시험 결과 임시 저장


def get_mode() -> str:
    return st.session_state.get(PAGE_MODE_KEY, "main")


def set_mode(m: str):
    st.session_state[PAGE_MODE_KEY] = m


# ═══════════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════════

st.markdown("""
<style>
.stApp { background: #0a0d18 !important; }
.block-container {
    max-width: 540px !important;
    margin: 0 auto !important;
    padding-top: 18px !important;
    padding-bottom: 40px !important;
}
#MainMenu, footer, header { visibility: hidden; }

div.stButton > button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    padding: 14px !important;
    font-size: 15px !important;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# 메인 화면 — 감방 2개
# ═══════════════════════════════════════════════════════════════

def render_main_screen():
    """단어 포로수용소 메인 — 감방 2개."""

    st.markdown("""
    <div style="text-align:center;margin-bottom:24px;">
        <div style="font-size:48px;margin-bottom:6px;">💀</div>
        <div style="color:#cc44ff;font-size:22px;font-weight:900;letter-spacing:2px;">
            단어 포로수용소
        </div>
        <div style="color:#557788;font-size:11px;margin-top:4px;letter-spacing:1px;">
            POW HQ
        </div>
    </div>
    """, unsafe_allow_html=True)

    stats = get_mastery_stats(nickname)
    wanted = get_wanted_words(nickname, limit=20)

    total_mastered = stats["total_mastered"]
    tier_emoji = stats["tier_emoji"]
    tier_label = stats["tier_label"]
    next_at = stats.get("next_tier_at")

    wanted_count = len(wanted)

    # 🥉 마스터 감방
    progress_text = f"{total_mastered} / {next_at}" if next_at else f"{total_mastered}"

    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #2a1a4a 0%, #1a1228 100%);
        border: 2.5px solid #cc44ff;
        border-radius: 16px;
        padding: 26px 20px;
        margin-bottom: 12px;
        text-align: center;
        position: relative;
    ">
        <div style="position:absolute;top:10px;left:10px;right:10px;
                    height:3px;background:repeating-linear-gradient(90deg,
                    #cc44ff 0, #cc44ff 8px, transparent 8px, transparent 16px);
                    opacity:0.5;"></div>
        <div style="position:absolute;bottom:10px;left:10px;right:10px;
                    height:3px;background:repeating-linear-gradient(90deg,
                    #cc44ff 0, #cc44ff 8px, transparent 8px, transparent 16px);
                    opacity:0.5;"></div>
        <div style="font-size:42px;margin-bottom:8px;">{tier_emoji}</div>
        <div style="color:#dd99ff;font-size:20px;font-weight:900;letter-spacing:2px;
                    margin-bottom:6px;">
            마스터 감방
        </div>
        <div style="color:#ffaaff;font-size:28px;font-weight:900;margin:8px 0;">
            {progress_text}
        </div>
        <div style="color:#aabbcc;font-size:12px;margin-bottom:4px;">
            <strong style="color:#dd99ff;">{tier_label}</strong> 도전 중
        </div>
        <div style="color:#7766aa;font-size:10px;font-style:italic;">
            ⛓️ 단어를 외울 때까지 가둔다
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🥉 마스터 감방 입장", use_container_width=True, type="primary",
                 key="btn_master"):
        words = build_master_game_words(nickname)
        if not words:
            st.warning("학습할 단어가 없어요.")
        else:
            st.session_state[GAME_WORDS_KEY] = words
            st.session_state[GAME_TYPE_KEY] = "master"
            set_mode("study")
            st.rerun()

    # 🎯 수배 감방
    if wanted_count > 0:
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #4a1a28 0%, #281218 100%);
            border: 2.5px solid #ff4477;
            border-radius: 16px;
            padding: 26px 20px;
            margin: 18px 0 12px;
            text-align: center;
            position: relative;
        ">
            <div style="position:absolute;top:10px;left:10px;right:10px;
                        height:3px;background:repeating-linear-gradient(90deg,
                        #ff4477 0, #ff4477 8px, transparent 8px, transparent 16px);
                        opacity:0.5;"></div>
            <div style="position:absolute;bottom:10px;left:10px;right:10px;
                        height:3px;background:repeating-linear-gradient(90deg,
                        #ff4477 0, #ff4477 8px, transparent 8px, transparent 16px);
                        opacity:0.5;"></div>
            <div style="font-size:42px;margin-bottom:8px;">🎯</div>
            <div style="color:#ff99bb;font-size:20px;font-weight:900;letter-spacing:2px;
                        margin-bottom:6px;">
                수배 감방
            </div>
            <div style="color:#ff4477;font-size:28px;font-weight:900;margin:8px 0;">
                {wanted_count}명 수감
            </div>
            <div style="color:#aabbcc;font-size:12px;margin-bottom:4px;">
                <strong style="color:#ff99bb;">자꾸 도망친 놈들</strong>
            </div>
            <div style="color:#aa6677;font-size:10px;font-style:italic;">
                ⚠️ 약점 단어, 끝까지 잡아라
            </div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🎯 수배 감방 입장", use_container_width=True,
                     key="btn_wanted"):
            words = build_wanted_game_words(nickname, wanted)
            if words:
                st.session_state[GAME_WORDS_KEY] = words
                st.session_state[GAME_TYPE_KEY] = "wanted"
                set_mode("study")
                st.rerun()
    else:
        st.markdown("""
        <div style="
            background: #14171f;
            border: 2px dashed #3a3f4a;
            border-radius: 16px;
            padding: 24px 20px;
            margin: 18px 0 12px;
            text-align: center;
            opacity: 0.7;
        ">
            <div style="font-size:36px;margin-bottom:6px;filter:grayscale(1);">🎯</div>
            <div style="color:#666c7a;font-size:18px;font-weight:900;letter-spacing:2px;
                        margin-bottom:6px;">
                수배 감방
            </div>
            <div style="color:#22cc88;font-size:16px;font-weight:700;margin:6px 0;">
                🎉 깨끗해!
            </div>
            <div style="color:#555;font-size:11px;font-style:italic;">
                수배 단어가 없어. 잘하고 있다.
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 메인으로
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    if st.button("🏠 메인으로", use_container_width=True, key="btn_back_main"):
        st.switch_page("main_hub.py")


# ═══════════════════════════════════════════════════════════════
# 게임 단어 빌더
# ═══════════════════════════════════════════════════════════════

def _build_options(words: List[Dict], pool: dict) -> List[Dict]:
    """4지선다 옵션 생성 (시험용)."""
    all_meanings = list({
        item["meaning"].strip()
        for pos in ["noun", "verb", "adjective", "adverb"]
        for item in pool.get(pos, [])
        if item.get("meaning")
    })

    for i, item in enumerate(words, 1):
        item_pool = [m for m in all_meanings if m != item["meaning"]]
        wrongs = random.sample(item_pool, min(3, len(item_pool)))
        while len(wrongs) < 3:
            wrongs.append(f"(보기 {len(wrongs)+1})")
        options = wrongs + [item["meaning"]]
        random.shuffle(options)
        item["options"] = options
        item["correct_index"] = options.index(item["meaning"])
        item["display_no"] = i

    return words


def build_master_game_words(nick: str) -> List[Dict]:
    """마스터 감방 — 마스터 안 된 단어 10개."""
    pool = load_word_pool()
    if not pool:
        return []
    candidates = get_unmastered_words(nick, pos=None, limit=GAME_WORD_COUNT * 2)
    selected = candidates[:GAME_WORD_COUNT]
    if not selected:
        return []
    return _build_options(selected, pool)


def build_wanted_game_words(nick: str, wanted: List[Dict]) -> List[Dict]:
    """수배 감방 — 수배 단어 최대 10개."""
    pool = load_word_pool()
    if not pool:
        return []
    selected = wanted[:GAME_WORD_COUNT]
    return _build_options(selected, pool)


# ═══════════════════════════════════════════════════════════════
# 학습장 — 낱말카드 2x5 그리드
# ═══════════════════════════════════════════════════════════════

def render_study_screen():
    """학습장 — 낱말카드 10개 표시 (자유 토글)."""
    words = st.session_state.get(GAME_WORDS_KEY, [])
    game_type = st.session_state.get(GAME_TYPE_KEY, "master")

    if not words:
        set_mode("main")
        st.rerun()
        return

    accent = "#ff4477" if game_type == "wanted" else "#cc44ff"
    title = "수배 감방 학습장" if game_type == "wanted" else "마스터 감방 학습장"

    # 헤더
    st.markdown(f"""
    <div style="text-align:center;margin-bottom:18px;">
        <div style="font-size:36px;margin-bottom:4px;">🃏</div>
        <div style="color:{accent};font-size:18px;font-weight:900;letter-spacing:2px;">
            {title}
        </div>
        <div style="color:#557788;font-size:11px;margin-top:4px;letter-spacing:1px;">
            모르는 단어 카드를 탭해서 확인해
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 낱말카드 — JS로 처리 (Python rerun 안 함, 토글 효과)
    words_simple = [
        {
            "word": w["word"],
            "meaning": w["meaning"],
            "no": i + 1,
        }
        for i, w in enumerate(words)
    ]
    words_json = json.dumps(words_simple, ensure_ascii=False)

    cards_html = """
<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: transparent;
    padding: 8px 0;
}
.card-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}
.card {
    background: #1a2030;
    border: 2px solid #3d5278;
    border-radius: 12px;
    padding: 18px 8px;
    min-height: 90px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s;
    position: relative;
    user-select: none;
}
.card:hover {
    background: #243044;
    border-color: __ACCENT__;
    transform: translateY(-2px);
}
.card.flipped {
    background: #2a1a30;
    border-color: __ACCENT__;
}
.card.seen::after {
    content: "✓";
    position: absolute;
    top: 4px;
    right: 6px;
    color: __ACCENT__;
    font-size: 11px;
    font-weight: 700;
}
.card-no {
    color: #5a6878;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 1px;
    margin-bottom: 4px;
}
.card-en {
    color: #fff;
    font-size: 16px;
    font-weight: 800;
    letter-spacing: 0.5px;
}
.card-kr {
    color: __ACCENT_LIGHT__;
    font-size: 13px;
    font-weight: 700;
    line-height: 1.4;
}
.card .hint {
    color: #5a6878;
    font-size: 8px;
    margin-top: 4px;
    font-style: italic;
}
</style>
</head>
<body>
<div class="card-grid" id="grid"></div>
<script>
const WORDS = __WORDS_JSON__;
const seen = new Set();

function render() {
    const grid = document.getElementById('grid');
    grid.innerHTML = '';
    WORDS.forEach((w, idx) => {
        const card = document.createElement('div');
        card.className = 'card';
        if (seen.has(idx)) card.classList.add('seen');
        if (w._flipped) card.classList.add('flipped');
        
        const no = document.createElement('div');
        no.className = 'card-no';
        no.textContent = '#' + w.no;
        card.appendChild(no);
        
        if (w._flipped) {
            const kr = document.createElement('div');
            kr.className = 'card-kr';
            kr.textContent = w.meaning;
            card.appendChild(kr);
            
            const hint = document.createElement('div');
            hint.className = 'hint';
            hint.textContent = '탭하면 영어';
            card.appendChild(hint);
        } else {
            const en = document.createElement('div');
            en.className = 'card-en';
            en.textContent = w.word;
            card.appendChild(en);
            
            if (!seen.has(idx)) {
                const hint = document.createElement('div');
                hint.className = 'hint';
                hint.textContent = '탭해서 뜻 보기';
                card.appendChild(hint);
            }
        }
        
        card.onclick = () => {
            w._flipped = !w._flipped;
            seen.add(idx);
            render();
        };
        
        grid.appendChild(card);
    });
}

render();
</script>
</body></html>
"""

    cards_html = cards_html.replace("__WORDS_JSON__", words_json)
    cards_html = cards_html.replace("__ACCENT__", accent)
    cards_html = cards_html.replace("__ACCENT_LIGHT__",
                                     "#ff99bb" if game_type == "wanted" else "#dd99ff")

    components.html(cards_html, height=560, scrolling=False)

    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)

    # 시험장 입장 + 돌아가기
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("⚔️ 시험장 입장!", use_container_width=True, type="primary",
                     key="btn_to_exam"):
            set_mode("exam")
            st.rerun()
    with col2:
        if st.button("← 돌아가기", use_container_width=True, key="btn_back_from_study"):
            st.session_state.pop(GAME_WORDS_KEY, None)
            st.session_state.pop(GAME_TYPE_KEY, None)
            set_mode("main")
            st.rerun()


# ═══════════════════════════════════════════════════════════════
# 시험장 — 두더지 시험 (HTML/JS)
# ═══════════════════════════════════════════════════════════════

def render_exam_screen():
    """시험장 — 두더지 스타일 4지선다 + 3초 타이머."""
    words = st.session_state.get(GAME_WORDS_KEY, [])
    game_type = st.session_state.get(GAME_TYPE_KEY, "master")

    if not words:
        set_mode("main")
        st.rerun()
        return

    accent = "#ff4477" if game_type == "wanted" else "#cc44ff"

    # 무작위 셔플
    exam_words = words.copy()
    random.shuffle(exam_words)
    for i, w in enumerate(exam_words, 1):
        w["display_no"] = i

    words_json = json.dumps(exam_words, ensure_ascii=False)

    game_html = """
<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #1a1f2e; color: #fff;
    padding: 16px 14px; min-height: 540px;
    position: relative; overflow: hidden;
}
.top-bar {
    position: absolute; top: 0; left: 0; right: 0; height: 5px;
    background: repeating-linear-gradient(90deg,
        __ACCENT__ 0, __ACCENT__ 10px, #555 10px, #555 20px);
}
.header { display: flex; align-items: center; gap: 10px; margin: 8px 0 10px; }
.header-emoji { font-size: 24px; }
.header-title {
    color: __ACCENT__; font-size: 16px; font-weight: 800;
    letter-spacing: 2px;
}
.header-sub {
    color: #88aabb; font-size: 9px; margin-top: 1px;
    letter-spacing: 1px;
}
.header-counter { margin-left: auto; text-align: right; }
.counter-label { color: #7a8fa8; font-size: 8px; letter-spacing: 1px; }
.counter-value { color: __ACCENT__; font-size: 18px; font-weight: 700; }
.skull-quote {
    background: #243044; border: 1px solid #3d5278;
    border-radius: 8px; padding: 7px 10px; margin-bottom: 12px;
    display: flex; align-items: center; gap: 8px;
    min-height: 32px;
}
.skull-quote-text {
    color: #ddccaa; font-size: 11px; font-style: italic;
    line-height: 1.4; flex: 1;
}
.progress {
    background: #0e1220; border-radius: 4px; height: 6px;
    margin-bottom: 10px; overflow: hidden;
    border: 1px solid #2a3550;
}
.progress-fill {
    background: linear-gradient(90deg, #ffaa55, __ACCENT__);
    height: 100%; width: 0%;
    transition: width 0.35s ease;
}
.timer-box { margin-bottom: 14px; display: flex; align-items: center; gap: 8px; }
.timer-icon {
    font-size: 12px; color: #88aabb;
    font-weight: 700; min-width: 20px;
}
.timer-bar {
    flex: 1; background: #0e1220; border: 1px solid #2a3550;
    border-radius: 20px; height: 10px; overflow: hidden;
}
.timer-fill {
    height: 100%; width: 100%;
    background: linear-gradient(90deg, #22cc88, #88ffcc);
    transition: width 0.1s linear;
    border-radius: 20px;
}
.timer-text {
    color: #88ffcc; font-size: 14px; font-weight: 700;
    min-width: 36px; text-align: right;
}
.word-card {
    background: #243044; border: 2px solid #3d5278;
    border-radius: 12px; padding: 18px 12px;
    text-align: center; margin-bottom: 14px;
    position: relative; overflow: hidden;
}
.word-card-bars {
    position: absolute; top: 0; bottom: 0; left: 0; width: 100%;
    background: repeating-linear-gradient(0deg,
        transparent 0, transparent 24px,
        rgba(120,140,180,0.15) 24px,
        rgba(120,140,180,0.15) 26px);
    pointer-events: none;
}
.word-card-label {
    position: relative; display: flex;
    align-items: center; justify-content: center; gap: 8px;
    margin-bottom: 8px;
}
.word-card-label-text {
    color: #7a8fa8; font-size: 9px; font-weight: 700;
    letter-spacing: 3px;
}
.word-display {
    position: relative; color: #fff;
    font-size: 30px; font-weight: 800;
    letter-spacing: 1.5px;
}
.options { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.option-btn {
    background: #243044; border: 1px solid #3d5278;
    border-radius: 8px; padding: 13px 6px;
    color: #ccddee; font-size: 13px; font-weight: 700;
    cursor: pointer; font-family: inherit;
    transition: all 0.2s; width: 100%;
}
.option-btn:hover:not(:disabled) {
    background: #1e2940; border-color: #5d72a8;
}
.option-btn.correct {
    background: #00553a !important; border-color: #22cc88 !important;
    color: #88ffcc !important;
}
.option-btn.wrong {
    background: #5a1a14 !important; border-color: #ff6644 !important;
    color: #ffaa88 !important;
    animation: shake 0.4s ease;
}
.option-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.feedback {
    text-align: center; margin-top: 12px; height: 24px;
    font-size: 13px; font-weight: 800; letter-spacing: 1px;
}
.done-screen { text-align: center; padding: 30px 20px; }
.done-emoji { font-size: 60px; }
.done-text {
    color: __ACCENT__; font-size: 22px; font-weight: 900;
    margin-top: 12px; letter-spacing: 2px;
}
.done-stats {
    margin-top: 20px;
    background: #243044; border: 1px solid #3d5278;
    border-radius: 10px; padding: 16px;
}
.stat-row {
    display: flex; justify-content: space-between;
    padding: 6px 0; font-size: 13px;
}
.stat-row + .stat-row { border-top: 1px dashed #3d5278; }
@keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-6px); }
    75% { transform: translateX(6px); }
}
@keyframes timerPulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.06); }
}
.timer-warn { animation: timerPulse 0.5s infinite ease-in-out; }
</style>
</head>
<body>
<div class="top-bar"></div>

<div id="game-area">
  <div class="header">
    <span class="header-emoji">💀</span>
    <div>
      <div class="header-title">시험장</div>
      <div class="header-sub">⛓️ 3초 안에 답!</div>
    </div>
    <div class="header-counter">
      <div class="counter-label">남은 단어</div>
      <div class="counter-value" id="counter">0 / 0</div>
    </div>
  </div>
  <div class="skull-quote">
    <span style="font-size:14px;">💀</span>
    <div class="skull-quote-text" id="skull-quote">10명을 심문할 시간이다</div>
  </div>
  <div class="progress">
    <div class="progress-fill" id="progress-bar"></div>
  </div>
  <div class="timer-box" id="timer-box">
    <span class="timer-icon">⏱</span>
    <div class="timer-bar">
      <div class="timer-fill" id="timer-bar"></div>
    </div>
    <span class="timer-text" id="timer-text">3.0s</span>
  </div>
  <div class="word-card">
    <div class="word-card-bars"></div>
    <div class="word-card-label">
      <span style="font-size:14px;">⛓️</span>
      <span class="word-card-label-text" id="word-label">단어 #1</span>
      <span style="font-size:14px;">⛓️</span>
    </div>
    <div class="word-display" id="word-display">...</div>
  </div>
  <div class="options" id="options"></div>
  <div class="feedback" id="feedback"></div>
</div>

<div id="done-area" style="display:none;">
  <div class="done-screen">
    <div class="done-emoji">🎉</div>
    <div class="done-text">시험 종료!</div>
    <div class="done-stats" id="done-stats"></div>
    <div style="color:#888;font-size:11px;margin-top:14px;">
      아래 ✅ 결과 보기 버튼을 눌러줘
    </div>
  </div>
</div>

<script>
const ALL_WORDS = __WORDS_JSON__;
const TIMER_SEC = __TIMER__;

let queue = [...ALL_WORDS];
let currentItem = null;
let timerInterval = null;
let timeLeft = TIMER_SEC;
let totalProgress = 0;
const totalWords = ALL_WORDS.length;

const correctList = [];
const wrongList = [];

const SKULL_QUOTES = [
    "이놈, 도망 못 가게 해라.",
    "빠르게! 시간 끌면 탈출이다.",
    "잡아내라!",
    "이번엔 놓치지 마라.",
    "정답을 골라!",
];

function startTimer() {
    if (timerInterval) clearInterval(timerInterval);
    timeLeft = TIMER_SEC;
    updateTimerUI();
    document.getElementById('timer-box').classList.remove('timer-warn');
    timerInterval = setInterval(() => {
        timeLeft -= 0.1;
        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            timeLeft = 0;
            updateTimerUI();
            onTimeout();
            return;
        }
        updateTimerUI();
    }, 100);
}

function updateTimerUI() {
    const pct = Math.max(0, (timeLeft / TIMER_SEC) * 100);
    document.getElementById('timer-bar').style.width = pct + '%';
    document.getElementById('timer-text').textContent = timeLeft.toFixed(1) + 's';
    const bar = document.getElementById('timer-bar');
    const text = document.getElementById('timer-text');
    const box = document.getElementById('timer-box');
    if (timeLeft <= 1.0) {
        bar.style.background = '#ff4422';
        text.style.color = '#ff8844';
        box.classList.add('timer-warn');
    } else if (timeLeft <= 2.0) {
        bar.style.background = 'linear-gradient(90deg,#ffaa55,#ff8844)';
        text.style.color = '#ffaa55';
        box.classList.remove('timer-warn');
    } else {
        bar.style.background = 'linear-gradient(90deg,#22cc88,#88ffcc)';
        text.style.color = '#88ffcc';
        box.classList.remove('timer-warn');
    }
}

function onTimeout() {
    document.querySelectorAll('.option-btn').forEach(b => b.disabled = true);
    document.getElementById('feedback').style.color = '#ff8844';
    document.getElementById('feedback').textContent = '⏰ 시간 초과! 수배 감방행!';
    wrongList.push({ word: currentItem.word, pos: currentItem.pos });
    setTimeout(nextWord, 800);
}

function pickOpt(btn, idx) {
    if (timerInterval) clearInterval(timerInterval);
    document.querySelectorAll('.option-btn').forEach(b => b.disabled = true);
    const fb = document.getElementById('feedback');
    if (idx === currentItem.correct_index) {
        btn.classList.add('correct');
        fb.style.color = '#88ffcc';
        fb.textContent = '🔒 체포 완료!';
        correctList.push({ word: currentItem.word, pos: currentItem.pos });
    } else {
        btn.classList.add('wrong');
        fb.style.color = '#ff8844';
        fb.textContent = '💨 탈출! 수배 감방행!';
        wrongList.push({ word: currentItem.word, pos: currentItem.pos });
    }
    setTimeout(nextWord, 800);
}

function nextWord() {
    if (queue.length === 0) {
        showDone();
        return;
    }
    currentItem = queue.shift();
    totalProgress++;
    renderWord();
    startTimer();
}

function renderWord() {
    document.getElementById('word-display').textContent = currentItem.word;
    document.getElementById('feedback').textContent = '';
    const remaining = queue.length + 1;
    document.getElementById('counter').textContent = remaining + ' / ' + totalWords;
    document.getElementById('word-label').textContent = '단어 #' + currentItem.display_no;
    document.getElementById('skull-quote').textContent = 
        SKULL_QUOTES[Math.floor(Math.random() * SKULL_QUOTES.length)];
    const pct = ((totalWords - remaining) / totalWords) * 100;
    document.getElementById('progress-bar').style.width = pct + '%';
    const optsDiv = document.getElementById('options');
    optsDiv.innerHTML = '';
    currentItem.options.forEach((opt, idx) => {
        const btn = document.createElement('button');
        btn.className = 'option-btn';
        btn.textContent = opt;
        btn.onclick = () => pickOpt(btn, idx);
        optsDiv.appendChild(btn);
    });
}

function showDone() {
    if (timerInterval) clearInterval(timerInterval);
    document.getElementById('game-area').style.display = 'none';
    document.getElementById('done-area').style.display = 'block';
    
    const stats = document.getElementById('done-stats');
    stats.innerHTML = 
        '<div class="stat-row"><span style="color:#88ffcc;">✅ 체포 (정답)</span>' +
        '<span style="color:#fff;font-weight:900;">' + correctList.length + '명</span></div>' +
        '<div class="stat-row"><span style="color:#ff8844;">🎯 수배 감방행</span>' +
        '<span style="color:#fff;font-weight:900;">' + wrongList.length + '명</span></div>';
    
    // 결과를 storage에 저장 (Streamlit이 못 읽을 수 있어서 백업 방안)
    try {
        const result = { correct: correctList, wrong: wrongList };
        localStorage.setItem('pow_exam_result', JSON.stringify(result));
    } catch(e) {}
}

setTimeout(nextWord, 200);
</script>
</body></html>
"""

    game_html = game_html.replace("__WORDS_JSON__", words_json)
    game_html = game_html.replace("__TIMER__", str(TIMER_SECONDS))
    game_html = game_html.replace("__ACCENT__", accent)

    components.html(game_html, height=620, scrolling=False)

    # 결과 보기 버튼 (학생이 시험 끝낸 후 누름)
    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
    if st.button("✅ 결과 보기", use_container_width=True, type="primary",
                 key="btn_to_result"):
        # 시험 결과 처리: 모든 단어 처리되었다고 가정
        # JS에서 정확한 결과를 못 받기 때문에 학생 자율에 맡김
        # → 결과 화면에서 학생이 직접 어느 단어를 틀렸는지 표시
        on_exam_done(exam_words)


def on_exam_done(exam_words):
    """시험 종료 — 결과 화면으로."""
    # 시험 결과 (이번 라운드의 단어들)
    st.session_state[EXAM_RESULTS_KEY] = exam_words
    set_mode("result")
    st.rerun()


# ═══════════════════════════════════════════════════════════════
# 결과 화면 — 어떤 단어를 틀렸는지 학생이 표시
# ═══════════════════════════════════════════════════════════════

def render_result_screen():
    """
    시험 결과 — 학생이 직접 정답/오답 체크.
    
    이유: HTML/JS에서 Python으로 데이터 전달이 모바일에서 신뢰 불가.
    → 학생 정직성에 맡기는 셀프 평가 (대부분 정직함)
    """
    exam_words = st.session_state.get(EXAM_RESULTS_KEY, [])
    game_type = st.session_state.get(GAME_TYPE_KEY, "master")

    if not exam_words:
        set_mode("main")
        st.rerun()
        return

    accent = "#ff4477" if game_type == "wanted" else "#cc44ff"

    st.markdown(f"""
    <div style="text-align:center;margin-bottom:14px;">
        <div style="font-size:36px;margin-bottom:4px;">📊</div>
        <div style="color:{accent};font-size:18px;font-weight:900;letter-spacing:2px;">
            시험 결과 정직 보고
        </div>
        <div style="color:#7a8fa8;font-size:11px;margin-top:4px;">
            틀린 단어를 체크해줘 (수배 감방으로 직행)
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 단어별 체크박스
    st.markdown("""
    <div style="background:#243044;border:1px solid #3d5278;border-radius:10px;
                padding:8px 12px;margin-bottom:10px;color:#aabbcc;font-size:11px;
                font-style:italic;text-align:center;">
        💀 틀린 단어만 체크 → 정답은 안 체크하면 자동 처리
    </div>
    """, unsafe_allow_html=True)

    # 각 단어별 체크박스 (틀린 거)
    wrong_keys = []
    for w in exam_words:
        key = f"_wrong_{w['word']}"
        wrong_keys.append((w, key))
        # 단어 정보 카드
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"""
            <div style="background:#1a2030;border:1px solid #2a3550;border-radius:8px;
                        padding:8px 12px;margin-bottom:4px;">
                <span style="color:#fff;font-size:14px;font-weight:700;">
                    {w['word']}
                </span>
                <span style="color:#7a8fa8;font-size:12px;margin-left:8px;">
                    → {w['meaning']}
                </span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.checkbox("틀림", key=key, label_visibility="collapsed")

    st.markdown("<div style='margin-top:14px;'></div>", unsafe_allow_html=True)

    # 결과 처리
    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("💾 결과 저장 + 돌아가기", use_container_width=True,
                     type="primary", key="btn_save_result"):
            wrong_count = 0
            correct_count = 0
            for w, key in wrong_keys:
                is_wrong = st.session_state.get(key, False)
                try:
                    log_word_attempt(
                        nickname=nickname,
                        word=w["word"],
                        pos=w.get("pos", "noun"),
                        is_correct=not is_wrong,
                    )
                    if is_wrong:
                        wrong_count += 1
                    else:
                        correct_count += 1
                except Exception:
                    pass
                # 체크박스 정리
                st.session_state.pop(key, None)

            # 안내 메시지
            if wrong_count > 0:
                st.success(f"✅ {correct_count}명 체포 / 🎯 {wrong_count}명 수배 감방행")
            else:
                st.success(f"🎉 전원 체포! 완벽!")

            # 정리
            st.session_state.pop(GAME_WORDS_KEY, None)
            st.session_state.pop(GAME_TYPE_KEY, None)
            st.session_state.pop(EXAM_RESULTS_KEY, None)
            set_mode("main")
            st.rerun()

    with col2:
        if st.button("🔁 다시", use_container_width=True, key="btn_redo"):
            # 같은 단어로 다시
            set_mode("study")
            st.rerun()


# ═══════════════════════════════════════════════════════════════
# 라우팅
# ═══════════════════════════════════════════════════════════════

mode = get_mode()
if mode == "study":
    render_study_screen()
elif mode == "exam":
    render_exam_screen()
elif mode == "result":
    render_result_screen()
else:
    render_main_screen()
