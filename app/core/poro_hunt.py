"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE:     app/core/poro_hunt.py
ROLE:     포로소탕 v3 — 5단어 + 3초 타이머 + 재진압 라운드
VERSION:  SnapQ TOEIC V3 — 2026.04.30
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USAGE:
    from app.core.poro_hunt import maybe_show_poro_hunt
    maybe_show_poro_hunt(nickname)

GAME FLOW (v3):
    Round 1: 5개 단어 × 3초 타이머
        - 정답          → word_prison 석방 + 다음
        - 오답/시간초과 → 다음 (틀린 것 기록)
    Round 2 (재진압): Round 1에서 틀린 단어만
        - 정답          → 석방 + 다음
        - 오답/시간초과 → wrong_count 증가 + 다음
    클리어 → 메인

DESIGN (v3):
    - 다크 블루 베이스 (#1a1f2e)
    - 오렌지·코랄 액센트
    - 3초 카운트다운 (그린 → 오렌지 → 레드)
    - 깜빡임 제거
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import random
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional

import streamlit as st
import streamlit.components.v1 as components

from app.core.inbody_db import get_conn
from app.core.inbody_logger import update_word_prison


BASE = Path(__file__).parent.parent.parent
WORD_FAMILY_PATH = BASE / "data" / "word_family_db.json"
ARMORY_WORDS_PATH = BASE / "data" / "armory" / "secret_armory_words.json"

GAME_WORD_COUNT = 5
TIMER_SECONDS = 3.0


def _load_word_family() -> Dict[str, str]:
    try:
        if WORD_FAMILY_PATH.exists():
            data = json.loads(WORD_FAMILY_PATH.read_text(encoding="utf-8"))
            return data.get("words", {})
    except Exception as e:
        print(f"[poro_hunt] word_family_db 로드 실패: {e}")
    return {}


def _load_armory_words() -> Dict[str, str]:
    result = {}
    try:
        if ARMORY_WORDS_PATH.exists():
            data = json.loads(ARMORY_WORDS_PATH.read_text(encoding="utf-8"))
            for card in data.get("cards", []):
                w = card.get("word", "").strip()
                m = card.get("meaning_ko", "").strip()
                if w and m and w not in result:
                    result[w] = m
    except Exception as e:
        print(f"[poro_hunt] armory_words 로드 실패: {e}")
    return result


def _get_prison_words(nickname: str) -> List[Dict[str, str]]:
    family = _load_word_family()
    armory = _load_armory_words()
    combined_meanings = {**family, **armory}

    result = []
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT word, wrong_count
            FROM word_prison
            WHERE nickname = ? AND released = 0 AND wrong_count >= 2
            ORDER BY wrong_count DESC, last_wrong DESC
            LIMIT 20
        """, (nickname,))
        for row in cur.fetchall():
            w = row["word"]
            meaning = combined_meanings.get(w)
            if meaning:
                result.append({
                    "word": w,
                    "meaning": meaning,
                    "wrong_count": row["wrong_count"],
                    "source": "prison",
                })
        conn.close()
    except Exception as e:
        print(f"[poro_hunt] prison 단어 추출 실패: {e}")
    return result


def build_game_words(nickname: str, count: int = GAME_WORD_COUNT) -> List[Dict]:
    """게임 단어 5개 + 4지선다 + display_no 생성."""
    family = _load_word_family()
    armory = _load_armory_words()
    combined_meanings = {**family, **armory}

    selected: List[Dict] = []
    used_words = set()

    for item in _get_prison_words(nickname):
        if len(selected) >= count:
            break
        w = item["word"]
        if w in used_words:
            continue
        selected.append({
            "word": w,
            "answer": item["meaning"],
            "source": item["source"],
            "wrong_count": item.get("wrong_count", 0),
        })
        used_words.add(w)

    if len(selected) < count:
        armory_pool = list(armory.items())
        random.shuffle(armory_pool)
        for w, m in armory_pool:
            if len(selected) >= count:
                break
            if w in used_words:
                continue
            selected.append({"word": w, "answer": m, "source": "armory", "wrong_count": 0})
            used_words.add(w)

    if len(selected) < count:
        family_pool = list(family.items())
        random.shuffle(family_pool)
        for w, m in family_pool:
            if len(selected) >= count:
                break
            if w in used_words:
                continue
            selected.append({"word": w, "answer": m, "source": "family", "wrong_count": 0})
            used_words.add(w)

    # 오답용 풀 만들기 (빈 값·중복 제거)
    raw_pool = [m for w, m in combined_meanings.items() if w not in used_words]
    distractor_pool = list({m.strip() for m in raw_pool if m and m.strip()})

    # 더 풍성하게: 사용된 단어들의 뜻도 다른 문제의 오답으로 활용 가능
    all_meanings = list({m.strip() for m in combined_meanings.values() if m and m.strip()})

    for i, item in enumerate(selected, 1):
        # 정답은 오답 풀에서 제외
        item_pool = [m for m in distractor_pool if m != item["answer"]]

        # 부족하면 전체 의미 풀에서 보충 (정답 제외)
        if len(item_pool) < 3:
            item_pool = [m for m in all_meanings if m != item["answer"]]

        # 그래도 부족하면 더미 채움 (이론상 882개 단어로 절대 안 옴)
        while len(item_pool) < 3:
            item_pool.append(f"(보기 {len(item_pool) + 1})")

        wrongs = random.sample(item_pool, 3)
        options = wrongs + [item["answer"]]
        random.shuffle(options)
        item["options"] = options
        item["correct_index"] = options.index(item["answer"])
        item["display_no"] = i

    return selected


def maybe_show_poro_hunt(nickname: str) -> None:
    if not nickname:
        return

    today_key = f"_poro_hunt_done_{date.today().isoformat()}"
    if st.session_state.get(today_key):
        return

    words_key = f"_poro_hunt_words_{date.today().isoformat()}"
    if words_key not in st.session_state:
        words = build_game_words(nickname, GAME_WORD_COUNT)
        if not words:
            st.session_state[today_key] = True
            return
        st.session_state[words_key] = words

    words = st.session_state[words_key]
    _render_game(nickname, words)


def _render_game(nickname: str, words: List[Dict]) -> None:
    """포로소탕 v3 게임 HTML."""

    st.markdown("""
    <style>
    .stApp { background: #1a1f2e !important; }
    .block-container {
        max-width: 540px !important;
        margin: 0 auto !important;
        padding-top: 18px !important;
    }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

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
        #ff8844 0, #ff8844 10px, #cc5522 10px, #cc5522 20px);
}
.header { display: flex; align-items: center; gap: 10px; margin: 8px 0 10px; }
.header-emoji { font-size: 24px; }
.header-title {
    color: #ff8844; font-size: 16px; font-weight: 800;
    letter-spacing: 2px;
}
.header-sub {
    color: #88aabb; font-size: 9px; margin-top: 1px;
    letter-spacing: 1px;
}
.header-counter { margin-left: auto; text-align: right; }
.counter-label { color: #7a8fa8; font-size: 8px; letter-spacing: 1px; }
.counter-value { color: #ffaa55; font-size: 18px; font-weight: 700; }
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
    background: linear-gradient(90deg, #ffaa55, #ff8844);
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
    transform: translateY(-1px);
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
      <div class="header-title">포로소탕</div>
      <div class="header-sub" id="round-sub">⛓️ 빠르게 잡아라!</div>
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
    <div class="clear-sub">잠시 후 메인 화면으로...</div>
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

const SKULL_QUOTES_R1 = [
    "이놈, 도망 못 가게 해라.",
    "빠르게! 시간 끌면 탈출이다.",
    "잡아내라!",
    "이번엔 놓치지 마라.",
    "정답을 골라!",
];

function pickQuote(item, roundNum) {
    if (roundNum === 1) {
        if (item.source === 'prison' && item.wrong_count >= 3) {
            return "이놈 " + item.wrong_count + "번 탈출했어. 이번엔 잡아.";
        }
        if (item.source === 'prison' && item.wrong_count >= 2) {
            return "두 번 탈출한 놈이다.";
        }
        return SKULL_QUOTES_R1[Math.floor(Math.random() * SKULL_QUOTES_R1.length)];
    }
    return "탈출했던 놈이다. 다시 잡아라!";
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
        currentItem._correct_round = currentRound;
    } else {
        btn.classList.add('wrong');
        fb.style.color = '#ff8844';
        fb.textContent = '💨 탈출 시도! 놓쳤다!';
        failedThisRound.push(currentItem);
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
        '탈출 포로 <strong style="color:#ff8844;">' + n + '명</strong> 발생!<br>' +
        '다시 잡아라!';
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
    try {
        window.parent.postMessage({ type: 'poro_hunt_done', results: ALL_WORDS }, '*');
    } catch(e) {}
}

setTimeout(nextWord, 200);
</script>
</body></html>
"""

    game_html = game_html.replace("__WORDS_JSON__", words_json)
    game_html = game_html.replace("__TIMER__", str(TIMER_SECONDS))

    components.html(game_html, height=620, scrolling=False)

    st.markdown("""
    <div style="text-align:center;margin-top:8px;color:#445566;font-size:11px;">
        모든 포로 처리 후 자동으로 입장돼.
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("✅ 입장", use_container_width=True, key="btn_poro_done"):
            _on_clear(nickname, words)
            return

    st.stop()


def _on_clear(nickname: str, words: List[Dict]) -> None:
    today_key = f"_poro_hunt_done_{date.today().isoformat()}"
    words_key = f"_poro_hunt_words_{date.today().isoformat()}"
    for item in words:
        try:
            update_word_prison(nickname, item["word"], is_correct=True)
        except Exception:
            pass
    st.session_state[today_key] = True
    st.session_state.pop(words_key, None)


# ─────────────────────────────────────────────────────────────
# 자가 점검
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("SnapQ poro_hunt v3 자가 점검")
    print("=" * 60)

    from app.core.inbody_db import init_db
    from app.core.inbody_logger import ensure_student, update_word_prison

    init_db()

    print("\n[1] 단어 풀 로드:")
    family = _load_word_family()
    armory = _load_armory_words()
    print(f"   word_family_db:        {len(family)}개")
    print(f"   secret_armory_words:   {len(armory)}개")

    print("\n[2] 게임 단어 빌드:")
    nick = "포로v3테스트"
    ensure_student(nick, cohort="2026-05", consent_inbody=True)

    for _ in range(3):
        update_word_prison(nick, "implementation", is_correct=False)
    for _ in range(2):
        update_word_prison(nick, "allocation", is_correct=False)

    words = build_game_words(nick, 5)
    print(f"   {len(words)}개 단어 (display_no, wrong_count 포함):")
    for w in words:
        print(f"   #{w['display_no']} [{w['source']:7s}] {w['word']:15s} wrong={w.get('wrong_count',0)}")

    print("\n[3] v3 설정:")
    print(f"   GAME_WORD_COUNT: {GAME_WORD_COUNT}")
    print(f"   TIMER_SECONDS:   {TIMER_SECONDS}초")
    print(f"   Round 시스템:    1차(5개) → 틀린 거 → 2차 재진압 → 통과")

    # 정리
    print("\n[정리] 테스트 데이터 삭제")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM word_prison WHERE nickname = ?", (nick,))
    cur.execute("DELETE FROM students WHERE nickname = ?", (nick,))
    cur.execute("DELETE FROM sync_queue WHERE row_data LIKE ?", (f"%{nick}%",))
    conn.commit()
    conn.close()
    print("   완료")

    print("\n" + "=" * 60)
    print("자가 점검 완료! ✅")
    print("=" * 60)
