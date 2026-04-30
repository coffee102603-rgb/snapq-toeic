"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE:     pages/03_POW_HQ_NEW.py
ROLE:     단어 포로수용소 — 감방 2개 (마스터 / 수배)
VERSION:  SnapQ TOEIC V3 — 2026.04.30
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHILOSOPHY:
    단순! 손가락 한 번 → 게임 바로 시작.
    
    [감방 2개]
      🥉 마스터 감방  → 마스터 안 된 단어 5개 도전
      🎯 수배 감방    → 자주 틀린 단어 5개 진압
    
    수배 0명 → 회색 비활성화 ("🎉 깨끗해!")
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

# URL 쿼리 닉네임 복구
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

GAME_WORD_COUNT = 5
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

PAGE_MODE_KEY = "_pow_hq_mode"      # "main" / "game"
GAME_WORDS_KEY = "_pow_hq_words"
GAME_TYPE_KEY = "_pow_hq_type"      # "master" / "wanted"


def get_mode() -> str:
    return st.session_state.get(PAGE_MODE_KEY, "main")


def set_mode(m: str):
    st.session_state[PAGE_MODE_KEY] = m


# ═══════════════════════════════════════════════════════════════
# CSS — 다크 테마
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

/* 감방 카드 hover */
.cell-card {
    transition: transform 0.2s, box-shadow 0.2s;
    cursor: pointer;
}
.cell-card:hover {
    transform: translateY(-2px);
}

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
    """단어 포로수용소 메인 — 감방 2개만!"""

    # 헤더
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

    # 진행도 + 수배 단어 가져오기
    stats = get_mastery_stats(nickname)
    wanted = get_wanted_words(nickname, limit=20)

    total_mastered = stats["total_mastered"]
    tier_emoji = stats["tier_emoji"]
    tier_label = stats["tier_label"]
    next_at = stats.get("next_tier_at")
    next_label = stats.get("next_tier_label", "최고!")

    wanted_count = len(wanted)

    # ──────────────────────────────────────
    # 🥉 마스터 감방
    # ──────────────────────────────────────
    if next_at:
        progress_text = f"{total_mastered} / {next_at}"
    else:
        progress_text = f"{total_mastered}"

    st.markdown(f"""
    <div class="cell-card" style="
        background: linear-gradient(135deg, #2a1a4a 0%, #1a1228 100%);
        border: 2.5px solid #cc44ff;
        border-radius: 16px;
        padding: 26px 20px;
        margin-bottom: 16px;
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
            set_mode("game")
            st.rerun()

    # ──────────────────────────────────────
    # 🎯 수배 감방
    # ──────────────────────────────────────
    if wanted_count > 0:
        # 활성 상태
        st.markdown(f"""
        <div class="cell-card" style="
            background: linear-gradient(135deg, #4a1a28 0%, #281218 100%);
            border: 2.5px solid #ff4477;
            border-radius: 16px;
            padding: 26px 20px;
            margin: 18px 0 16px;
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
                set_mode("game")
                st.rerun()
    else:
        # 비활성 (회색)
        st.markdown("""
        <div style="
            background: #14171f;
            border: 2px dashed #3a3f4a;
            border-radius: 16px;
            padding: 24px 20px;
            margin: 18px 0 16px;
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

    # 메인으로 돌아가기
    st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
    if st.button("🏠 메인으로", use_container_width=True, key="btn_back"):
        st.switch_page("main_hub.py")


# ═══════════════════════════════════════════════════════════════
# 게임 단어 빌더
# ═══════════════════════════════════════════════════════════════

def _build_options(words: List[Dict], pool: dict) -> List[Dict]:
    """4지선다 옵션 생성."""
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
    """마스터 감방 — 마스터 안 된 단어 5개."""
    pool = load_word_pool()
    if not pool:
        return []
    candidates = get_unmastered_words(nick, pos=None, limit=GAME_WORD_COUNT * 2)
    selected = candidates[:GAME_WORD_COUNT]
    if not selected:
        return []
    return _build_options(selected, pool)


def build_wanted_game_words(nick: str, wanted: List[Dict]) -> List[Dict]:
    """수배 감방 — 자주 틀린 단어 5개."""
    pool = load_word_pool()
    if not pool:
        return []
    selected = wanted[:GAME_WORD_COUNT]
    return _build_options(selected, pool)


# ═══════════════════════════════════════════════════════════════
# 게임 화면
# ═══════════════════════════════════════════════════════════════

def render_game_screen():
    words = st.session_state.get(GAME_WORDS_KEY, [])
    game_type = st.session_state.get(GAME_TYPE_KEY, "master")

    if not words:
        set_mode("main")
        st.rerun()
        return

    if game_type == "wanted":
        title = "수배 감방 진압"
        subtitle = "⛓️ 도망친 놈들을 잡아라!"
        accent = "#ff4477"
    else:
        title = "마스터 감방"
        subtitle = "⛓️ 외울 때까지 가둔다"
        accent = "#cc44ff"

    words_json = json.dumps(words, ensure_ascii=False)

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
.round-banner {
    background: #2a1a30; border: 2px solid #cc44aa;
    border-radius: 12px; padding: 24px 16px; text-align: center;
    margin: 40px 0;
}
.round-banner-icon { font-size: 48px; margin-bottom: 12px; }
.round-banner-title {
    color: #ff66bb; font-size: 22px; font-weight: 900;
    letter-spacing: 2px; margin-bottom: 8px;
}
.round-banner-sub {
    color: #aabbcc; font-size: 13px; line-height: 1.5;
}
.clear-screen { text-align: center; padding: 40px 20px; }
.clear-emoji { font-size: 60px; }
.clear-text {
    color: #88ffcc; font-size: 24px; font-weight: 900;
    margin-top: 12px; letter-spacing: 2px;
}
.clear-sub { color: #888; font-size: 13px; margin-top: 8px; }
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
      <div class="header-title">__TITLE__</div>
      <div class="header-sub" id="round-sub">__SUBTITLE__</div>
    </div>
    <div class="header-counter">
      <div class="counter-label">남은 포로</div>
      <div class="counter-value" id="counter">0 / 0</div>
    </div>
  </div>
  <div class="skull-quote">
    <span style="font-size:14px;">💀</span>
    <div class="skull-quote-text" id="skull-quote">포로 입장 준비 중...</div>
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
      <span class="word-card-label-text" id="word-label">포로 #1</span>
      <span style="font-size:14px;">⛓️</span>
    </div>
    <div class="word-display" id="word-display">...</div>
  </div>
  <div class="options" id="options"></div>
  <div class="feedback" id="feedback"></div>
</div>

<div id="round-area" style="display:none;">
  <div class="round-banner">
    <div class="round-banner-icon">💀</div>
    <div class="round-banner-title" id="round-title">재진압!</div>
    <div class="round-banner-sub" id="round-desc">탈출한 포로를 다시 잡아라!</div>
  </div>
</div>

<div id="clear-area" style="display:none;">
  <div class="clear-screen">
    <div class="clear-emoji">🎉</div>
    <div class="clear-text">소탕 완료!</div>
    <div class="clear-sub">아래 ✅ 진행도 갱신을 눌러줘.</div>
  </div>
</div>

<script>
const ALL_WORDS = __WORDS_JSON__;
const TIMER_SEC = __TIMER__;

let queue = [...ALL_WORDS];
let currentRound = 1;
let failedThisRound = [];
let currentItem = null;
let timerInterval = null;
let timeLeft = TIMER_SEC;
let totalProgress = 0;
const totalRoundOne = ALL_WORDS.length;

const SKULL_QUOTES = [
    "이놈, 도망 못 가게 해라.",
    "빠르게! 시간 끌면 탈출이다.",
    "잡아내라!",
    "이번엔 놓치지 마라.",
    "정답을 골라!",
];

function pickQuote(item, roundNum) {
    if (roundNum === 2) return "탈출했던 놈이다. 다시 잡아라!";
    if (item.wrong_count >= 3) {
        return "이놈 " + item.wrong_count + "번 탈출했어. 이번엔 잡아.";
    }
    if (item.wrong_count >= 2) return "두 번 탈출한 놈이다.";
    return SKULL_QUOTES[Math.floor(Math.random() * SKULL_QUOTES.length)];
}

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
    document.getElementById('feedback').textContent = '⏰ 시간 초과! 포로 탈출!';
    failedThisRound.push(currentItem);
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
        currentItem._correct = true;
    } else {
        btn.classList.add('wrong');
        fb.style.color = '#ff8844';
        fb.textContent = '💨 탈출 시도! 놓쳤다!';
        failedThisRound.push(currentItem);
        currentItem._correct = false;
    }
    setTimeout(nextWord, 800);
}

function nextWord() {
    if (queue.length === 0) {
        if (currentRound === 1 && failedThisRound.length > 0) {
            showRoundBanner();
        } else {
            showClear();
        }
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
    const counterTotal = currentRound === 1 ? totalRoundOne : (failedThisRound.length + queue.length + 1);
    const remaining = currentRound === 1 ? (totalRoundOne - totalProgress + 1) : (queue.length + 1);
    document.getElementById('counter').textContent = remaining + ' / ' + counterTotal;
    document.getElementById('word-label').textContent = '포로 #' + currentItem.display_no;
    document.getElementById('skull-quote').textContent = pickQuote(currentItem, currentRound);
    const pct = ((counterTotal - remaining) / counterTotal) * 100;
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

function showRoundBanner() {
    document.getElementById('game-area').style.display = 'none';
    document.getElementById('round-area').style.display = 'block';
    const n = failedThisRound.length;
    document.getElementById('round-title').textContent = '🚨 재진압!';
    document.getElementById('round-desc').innerHTML =
        '탈출 포로 <strong style="color:#ff8844;">' + n + '명</strong> 발생!<br>다시 잡아라!';
    setTimeout(() => {
        currentRound = 2;
        queue = failedThisRound;
        failedThisRound = [];
        totalProgress = 0;
        document.getElementById('round-area').style.display = 'none';
        document.getElementById('game-area').style.display = 'block';
        document.getElementById('round-sub').textContent = '⛓️ 재진압 라운드!';
        nextWord();
    }, 2200);
}

function showClear() {
    if (timerInterval) clearInterval(timerInterval);
    document.getElementById('game-area').style.display = 'none';
    document.getElementById('round-area').style.display = 'none';
    document.getElementById('clear-area').style.display = 'block';
}

setTimeout(nextWord, 200);
</script>
</body></html>
"""

    game_html = game_html.replace("__WORDS_JSON__", words_json)
    game_html = game_html.replace("__TIMER__", str(TIMER_SECONDS))
    game_html = game_html.replace("__TITLE__", title)
    game_html = game_html.replace("__SUBTITLE__", subtitle)
    game_html = game_html.replace("__ACCENT__", accent)

    components.html(game_html, height=620, scrolling=False)

    # 종료 버튼
    st.markdown("<div style='margin-top:8px;'></div>", unsafe_allow_html=True)
    if st.button("✅ 진행도 갱신 + 돌아가기",
                 use_container_width=True, type="primary", key="btn_game_done"):
        on_game_clear()


def on_game_clear():
    """게임 종료 — word_mastery 카운트 +."""
    words = st.session_state.get(GAME_WORDS_KEY, [])
    for item in words:
        try:
            log_word_attempt(
                nickname=nickname,
                word=item["word"],
                pos=item.get("pos", "noun"),
                is_correct=True,
            )
        except Exception:
            pass

    st.session_state.pop(GAME_WORDS_KEY, None)
    st.session_state.pop(GAME_TYPE_KEY, None)
    set_mode("main")
    st.rerun()


# ═══════════════════════════════════════════════════════════════
# 라우팅
# ═══════════════════════════════════════════════════════════════

mode = get_mode()
if mode == "game":
    render_game_screen()
else:
    render_main_screen()
