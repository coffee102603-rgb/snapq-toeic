"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE:     pages/03_POW_HQ.py (v6 — Streamlit 네이티브 시험)
ROLE:     단어 포로수용소
VERSION:  SnapQ TOEIC V3 — 2026.04.30
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v6 변경 (★ 진짜 작동!):
    - JS 두더지 게임 폐기 → Streamlit 네이티브 시험
    - 한 단어씩 표시 → Streamlit 버튼 4개
    - 클릭 즉시 log_word_attempt() 정확히 호출
    - 수배 감방 진짜 작동!

게임 흐름:
    main → study(JS 카드) → exam(Streamlit 단어별) → result → main

시험장 (한 단어씩):
    - 단어 #N 표시
    - 4지선다 (Streamlit 버튼)
    - 3초 타이머 (JS, 시간초과 시 자동 다음)
    - 클릭 → 즉시 기록 → 다음 단어 (자동 rerun)
    - 10단어 끝 → 결과 화면 → 메인
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import random
import time
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


BASE = Path(__file__).parent.parent
WORD_POOL_PATH = BASE / "data" / "word_pool_categorized.json"

GAME_WORD_COUNT = 10


@st.cache_data
def load_word_pool() -> dict:
    if WORD_POOL_PATH.exists():
        try:
            return json.loads(WORD_POOL_PATH.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {}


# 세션 키
PAGE_MODE_KEY = "_pow_mode"        # main / study / exam / result
GAME_WORDS_KEY = "_pow_words"      # 시험 대상 단어 리스트
GAME_TYPE_KEY = "_pow_type"        # master / wanted
EXAM_INDEX_KEY = "_pow_exam_idx"   # 현재 시험 단어 인덱스 (0~9)
EXAM_RESULTS_KEY = "_pow_results"  # 정답/오답 추적 [{word, pos, correct}, ...]
EXAM_FEEDBACK_KEY = "_pow_feedback"  # 직전 답변 피드백 (correct/wrong/timeout)


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
    padding-top: 8px !important;
    padding-bottom: 16px !important;
}
#MainMenu, footer, header { visibility: hidden; }

div.stButton > button {
    border-radius: 10px !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    padding: 10px !important;
    font-size: 14px !important;
}

/* 시험장 4지선다 버튼 (큼직하게) */
.exam-options div.stButton > button {
    padding: 16px 8px !important;
    font-size: 14px !important;
    border: 1.5px solid #3d5278 !important;
    background: #243044 !important;
    color: #ccddee !important;
    min-height: 60px !important;
    word-break: keep-all !important;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# 메인 화면
# ═══════════════════════════════════════════════════════════════

def render_main_screen():
    st.markdown("""
    <div style="text-align:center;margin-bottom:8px;">
        <div style="font-size:28px;line-height:1;">💀</div>
        <div style="color:#cc44ff;font-size:17px;font-weight:900;letter-spacing:2px;
                    margin-top:2px;">
            단어 포로수용소
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 직전 시험 결과 표시
    last_result = st.session_state.pop("_pow_last_result", None)
    if last_result:
        wrong_n = last_result["wrong"]
        correct_n = last_result["correct"]
        if wrong_n > 0:
            st.markdown(f"""
            <div style="background:#2a1a14;border:1.5px solid #ff8844;border-radius:8px;
                        padding:8px 12px;margin-bottom:8px;text-align:center;">
                <span style="color:#88ffcc;font-size:13px;font-weight:700;">✅ {correct_n}명 체포</span>
                <span style="color:#888;margin:0 6px;">·</span>
                <span style="color:#ff8844;font-size:13px;font-weight:700;">🎯 {wrong_n}명 수배행!</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="background:#0a2a1a;border:1.5px solid #22cc88;border-radius:8px;
                        padding:8px 12px;margin-bottom:8px;text-align:center;">
                <span style="color:#88ffcc;font-size:13px;font-weight:700;">🎉 전원 체포! 완벽!</span>
            </div>
            """, unsafe_allow_html=True)

    stats = get_mastery_stats(nickname)
    wanted = get_wanted_words(nickname, limit=20)

    total_mastered = stats["total_mastered"]
    tier_emoji = stats["tier_emoji"]
    tier_label = stats["tier_label"]
    next_at = stats.get("next_tier_at")
    wanted_count = len(wanted)
    progress_text = f"{total_mastered} / {next_at}" if next_at else f"{total_mastered}"

    # 🥉 마스터 감방
    master_html = (
        '<div style="background:linear-gradient(135deg,#2a1a4a 0%,#1a1228 100%);'
        'border:2.5px solid #cc44ff;border-radius:12px;padding:14px 16px;'
        'margin-bottom:8px;position:relative;overflow:hidden;">'
        '<div style="position:absolute;top:0;bottom:0;left:14%;width:2px;'
        'background:#cc44ff;opacity:0.35;"></div>'
        '<div style="position:absolute;top:0;bottom:0;left:38%;width:2px;'
        'background:#cc44ff;opacity:0.35;"></div>'
        '<div style="position:absolute;top:0;bottom:0;left:62%;width:2px;'
        'background:#cc44ff;opacity:0.35;"></div>'
        '<div style="position:absolute;top:0;bottom:0;left:86%;width:2px;'
        'background:#cc44ff;opacity:0.35;"></div>'
        '<div style="position:absolute;top:0;left:0;right:0;height:2px;'
        'background:#cc44ff;opacity:0.6;"></div>'
        '<div style="position:absolute;bottom:0;left:0;right:0;height:2px;'
        'background:#cc44ff;opacity:0.6;"></div>'
        '<div style="position:relative;text-align:center;">'
        '<div style="display:flex;align-items:center;justify-content:center;'
        'gap:10px;margin-bottom:4px;">'
        f'<span style="font-size:24px;">{tier_emoji}</span>'
        '<span style="color:#dd99ff;font-size:16px;font-weight:900;'
        'letter-spacing:2px;">마스터 감방</span>'
        '</div>'
        f'<div style="color:#ffaaff;font-size:24px;font-weight:900;'
        f'line-height:1;">{progress_text}</div>'
        '<div style="color:#aabbcc;font-size:11px;margin-top:4px;">'
        f'<strong style="color:#dd99ff;">{tier_label}</strong> 도전 중'
        '</div>'
        '</div>'
        '</div>'
    )
    st.markdown(master_html, unsafe_allow_html=True)

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
        wanted_html = (
            '<div style="background:linear-gradient(135deg,#4a1a28 0%,#1a0810 100%);'
            'border:2.5px solid #ff4477;border-radius:12px;padding:14px 16px;'
            'margin:10px 0 8px;position:relative;overflow:hidden;">'
            '<div style="position:absolute;top:0;left:0;right:0;height:4px;'
            'background:repeating-linear-gradient(90deg,#ff4477 0,#ff4477 8px,'
            '#220004 8px,#220004 16px);"></div>'
            '<div style="position:absolute;bottom:0;left:0;right:0;height:4px;'
            'background:repeating-linear-gradient(90deg,#ff4477 0,#ff4477 8px,'
            '#220004 8px,#220004 16px);"></div>'
            '<div style="position:absolute;top:0;bottom:0;left:20%;width:2px;'
            'background:#ff4477;opacity:0.5;"></div>'
            '<div style="position:absolute;top:0;bottom:0;left:50%;width:2px;'
            'background:#ff4477;opacity:0.5;"></div>'
            '<div style="position:absolute;top:0;bottom:0;left:80%;width:2px;'
            'background:#ff4477;opacity:0.5;"></div>'
            '<div style="position:relative;text-align:center;">'
            '<div style="display:flex;align-items:center;justify-content:center;'
            'gap:10px;margin-bottom:4px;">'
            '<span style="font-size:24px;">🎯</span>'
            '<span style="color:#ff99bb;font-size:16px;font-weight:900;'
            'letter-spacing:2px;">수배 감방</span>'
            '</div>'
            f'<div style="color:#ff4477;font-size:24px;font-weight:900;'
            f'line-height:1;">{wanted_count}명 수감</div>'
            '<div style="color:#aabbcc;font-size:11px;margin-top:4px;">'
            '<strong style="color:#ff99bb;">자꾸 도망친 놈들</strong>'
            '</div>'
            '</div>'
            '</div>'
        )
        st.markdown(wanted_html, unsafe_allow_html=True)

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
        <div style="background:#14171f;border:1.5px dashed #3a3f4a;border-radius:12px;
                    padding:12px 16px;margin:10px 0 8px;position:relative;opacity:0.7;">
            <div style="text-align:center;">
                <div style="display:flex;align-items:center;justify-content:center;gap:8px;">
                    <span style="font-size:20px;filter:grayscale(1);">🎯</span>
                    <span style="color:#666c7a;font-size:14px;font-weight:900;letter-spacing:1px;">
                        수배 감방
                    </span>
                    <span style="color:#22cc88;font-size:13px;font-weight:700;">
                        🎉 깨끗해!
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    if st.button("🏠 메인으로", use_container_width=True, key="btn_back_main"):
        st.switch_page("main_hub.py")


# ═══════════════════════════════════════════════════════════════
# 게임 단어 빌더
# ═══════════════════════════════════════════════════════════════

def _build_options(words: List[Dict], pool: dict) -> List[Dict]:
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
    pool = load_word_pool()
    if not pool:
        return []
    candidates = get_unmastered_words(nick, pos=None, limit=GAME_WORD_COUNT * 2)
    selected = candidates[:GAME_WORD_COUNT]
    if not selected:
        return []
    return _build_options(selected, pool)


def build_wanted_game_words(nick: str, wanted: List[Dict]) -> List[Dict]:
    pool = load_word_pool()
    if not pool:
        return []
    selected = wanted[:GAME_WORD_COUNT]
    return _build_options(selected, pool)


# ═══════════════════════════════════════════════════════════════
# 학습장 (그대로 유지)
# ═══════════════════════════════════════════════════════════════

def render_study_screen():
    words = st.session_state.get(GAME_WORDS_KEY, [])
    game_type = st.session_state.get(GAME_TYPE_KEY, "master")

    if not words:
        set_mode("main")
        st.rerun()
        return

    accent = "#ff4477" if game_type == "wanted" else "#cc44ff"
    title = "수배 감방 학습장" if game_type == "wanted" else "마스터 감방 학습장"

    st.markdown(f"""
    <div style="text-align:center;margin-bottom:6px;">
        <div style="display:flex;align-items:center;justify-content:center;gap:8px;">
            <span style="font-size:20px;">🃏</span>
            <span style="color:{accent};font-size:14px;font-weight:900;letter-spacing:2px;">
                {title}
            </span>
        </div>
        <div style="color:#557788;font-size:10px;margin-top:1px;">
            모르는 단어 카드 탭 → 뜻 보기
        </div>
    </div>
    """, unsafe_allow_html=True)

    words_simple = [
        {"word": w["word"], "meaning": w["meaning"], "no": i + 1}
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
    background: transparent; padding: 4px 0;
}
.card-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
}
.card {
    background: #1a2030;
    border: 1.5px solid #3d5278;
    border-radius: 8px;
    padding: 8px 4px;
    min-height: 56px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    cursor: pointer;
    transition: all 0.2s;
    position: relative;
    user-select: none;
}
.card:active { transform: scale(0.97); }
.card.flipped {
    background: #2a1a30;
    border-color: __ACCENT__;
}
.card.seen::after {
    content: "✓";
    position: absolute;
    top: 2px;
    right: 4px;
    color: __ACCENT__;
    font-size: 9px;
    font-weight: 700;
}
.card-no { color: #5a6878; font-size: 8px; font-weight: 700; margin-bottom: 2px; }
.card-en { color: #fff; font-size: 13px; font-weight: 800; word-break: break-word; line-height: 1.1; }
.card-kr { color: __ACCENT_LIGHT__; font-size: 11px; font-weight: 700; line-height: 1.2; word-break: keep-all; }
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
        } else {
            const en = document.createElement('div');
            en.className = 'card-en';
            en.textContent = w.word;
            card.appendChild(en);
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

    components.html(cards_html, height=370, scrolling=False)

    st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        if st.button("⚔️ 시험장 입장!", use_container_width=True, type="primary",
                     key="btn_to_exam"):
            # 시험장 진입 시 — 단어 셔플 + 인덱스 초기화
            exam_words = words.copy()
            random.shuffle(exam_words)
            for i, w in enumerate(exam_words, 1):
                w["display_no"] = i
            st.session_state[GAME_WORDS_KEY] = exam_words
            st.session_state[EXAM_INDEX_KEY] = 0
            st.session_state[EXAM_RESULTS_KEY] = []
            st.session_state.pop(EXAM_FEEDBACK_KEY, None)
            set_mode("exam")
            st.rerun()
    with col2:
        if st.button("← 돌아가기", use_container_width=True, key="btn_back_from_study"):
            st.session_state.pop(GAME_WORDS_KEY, None)
            st.session_state.pop(GAME_TYPE_KEY, None)
            set_mode("main")
            st.rerun()


# ═══════════════════════════════════════════════════════════════
# ⚔️ 시험장 — Streamlit 네이티브 (한 단어씩, 진짜 작동!)
# ═══════════════════════════════════════════════════════════════

def render_exam_screen():
    """
    시험장 — Streamlit 네이티브 한 단어씩.
    
    Flow:
        EXAM_INDEX_KEY = 현재 단어 (0~9)
        EXAM_RESULTS_KEY = [{word, pos, correct}, ...] 누적
        
        한 단어 표시 → 4지선다 버튼 → 클릭 즉시 기록 → 다음 단어
        시간 초과: JS가 자동으로 timeout 버튼 클릭
    """
    words = st.session_state.get(GAME_WORDS_KEY, [])
    game_type = st.session_state.get(GAME_TYPE_KEY, "master")
    idx = st.session_state.get(EXAM_INDEX_KEY, 0)
    results = st.session_state.get(EXAM_RESULTS_KEY, [])

    if not words:
        set_mode("main")
        st.rerun()
        return

    # 시험 끝!
    if idx >= len(words):
        finish_exam()
        return

    accent = "#ff4477" if game_type == "wanted" else "#cc44ff"
    current = words[idx]
    word = current["word"]
    options = current["options"]
    correct_idx = current["correct_index"]
    display_no = current["display_no"]
    pos = current.get("pos", "noun")

    total = len(words)
    remaining = total - idx

    # 헤더
    st.markdown(f"""
    <div style="background:#1a1f2e;border:1.5px solid {accent};border-radius:10px;
                padding:8px 12px;margin-bottom:8px;
                display:flex;align-items:center;gap:10px;">
        <span style="font-size:20px;">💀</span>
        <div>
            <div style="color:{accent};font-size:13px;font-weight:900;letter-spacing:2px;">
                시험장
            </div>
            <div style="color:#88aabb;font-size:9px;">⛓️ 3초 안에 답!</div>
        </div>
        <div style="margin-left:auto;text-align:right;">
            <div style="color:#7a8fa8;font-size:8px;">남은 단어</div>
            <div style="color:{accent};font-size:16px;font-weight:700;">
                {remaining} / {total}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 단어 카드 (창살 무늬)
    word_card_html = (
        '<div style="background:#243044;border:2px solid #3d5278;border-radius:10px;'
        'padding:14px 10px;text-align:center;margin-bottom:10px;'
        'position:relative;overflow:hidden;">'
        '<div style="position:absolute;top:0;bottom:0;left:0;width:100%;'
        'background:repeating-linear-gradient(0deg,transparent 0,transparent 20px,'
        'rgba(120,140,180,0.15) 20px,rgba(120,140,180,0.15) 22px);'
        'pointer-events:none;"></div>'
        '<div style="position:relative;display:flex;align-items:center;'
        'justify-content:center;gap:6px;margin-bottom:4px;">'
        '<span style="font-size:12px;">⛓️</span>'
        f'<span style="color:#7a8fa8;font-size:8px;font-weight:700;'
        f'letter-spacing:2px;">단어 #{display_no}</span>'
        '<span style="font-size:12px;">⛓️</span>'
        '</div>'
        f'<div style="position:relative;color:#fff;font-size:26px;'
        f'font-weight:800;letter-spacing:1px;">{word}</div>'
        '</div>'
    )
    st.markdown(word_card_html, unsafe_allow_html=True)

    # 3초 타이머 (JS, 시간초과 시 자동 timeout 버튼 클릭)
    timer_html = """
<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
body { margin: 0; padding: 0; background: transparent; font-family: system-ui; }
.timer-box {
    display: flex; align-items: center; gap: 6px; padding: 0;
}
.timer-icon { font-size: 11px; color: #88aabb; min-width: 16px; }
.timer-bar {
    flex: 1; background: #0e1220; border: 1px solid #2a3550;
    border-radius: 20px; height: 8px; overflow: hidden;
}
.timer-fill {
    height: 100%; width: 100%;
    background: linear-gradient(90deg, #22cc88, #88ffcc);
    transition: width 0.1s linear; border-radius: 20px;
}
.timer-text {
    color: #88ffcc; font-size: 13px; font-weight: 700;
    min-width: 32px; text-align: right;
}
@keyframes timerPulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.06); }
}
.timer-warn { animation: timerPulse 0.5s infinite ease-in-out; }
</style>
</head>
<body>
<div class="timer-box" id="tb">
    <span class="timer-icon">⏱</span>
    <div class="timer-bar"><div class="timer-fill" id="bar"></div></div>
    <span class="timer-text" id="txt">3.0s</span>
</div>
<script>
let timeLeft = 3.0;
const interval = setInterval(() => {
    timeLeft -= 0.1;
    if (timeLeft <= 0) {
        clearInterval(interval);
        timeLeft = 0;
        update();
        // 시간 초과 — 부모의 timeout 버튼을 자동 클릭 시도
        try {
            const buttons = window.parent.document.querySelectorAll('button');
            for (const btn of buttons) {
                if (btn.textContent && btn.textContent.includes('TIMEOUT_HIDDEN')) {
                    btn.click();
                    return;
                }
            }
        } catch(e) {
            // 부모 접근 불가 - 사용자가 수동으로 답변 필요
        }
        return;
    }
    update();
}, 100);

function update() {
    const pct = Math.max(0, (timeLeft / 3.0) * 100);
    document.getElementById('bar').style.width = pct + '%';
    document.getElementById('txt').textContent = timeLeft.toFixed(1) + 's';
    const bar = document.getElementById('bar');
    const txt = document.getElementById('txt');
    const tb = document.getElementById('tb');
    if (timeLeft <= 1.0) {
        bar.style.background = '#ff4422';
        txt.style.color = '#ff8844';
        tb.classList.add('timer-warn');
    } else if (timeLeft <= 2.0) {
        bar.style.background = 'linear-gradient(90deg,#ffaa55,#ff8844)';
        txt.style.color = '#ffaa55';
        tb.classList.remove('timer-warn');
    }
}
</script>
</body></html>
"""

    # 직전 답변 피드백
    feedback = st.session_state.pop(EXAM_FEEDBACK_KEY, None)
    if feedback:
        if feedback == "correct":
            st.markdown("""
            <div style="background:#0a3322;border:1.5px solid #22cc88;border-radius:8px;
                        padding:6px 10px;margin-bottom:8px;text-align:center;">
                <span style="color:#88ffcc;font-size:13px;font-weight:800;">🔒 체포!</span>
            </div>
            """, unsafe_allow_html=True)
        elif feedback == "wrong":
            st.markdown("""
            <div style="background:#3a1010;border:1.5px solid #ff4422;border-radius:8px;
                        padding:6px 10px;margin-bottom:8px;text-align:center;">
                <span style="color:#ffaa88;font-size:13px;font-weight:800;">💨 탈출! 수배행!</span>
            </div>
            """, unsafe_allow_html=True)
        elif feedback == "timeout":
            st.markdown("""
            <div style="background:#3a2010;border:1.5px solid #ff8844;border-radius:8px;
                        padding:6px 10px;margin-bottom:8px;text-align:center;">
                <span style="color:#ffaa88;font-size:13px;font-weight:800;">⏰ 시간 초과! 수배행!</span>
            </div>
            """, unsafe_allow_html=True)

    # 타이머 표시 (피드백 없을 때만)
    if not feedback:
        components.html(timer_html, height=24)

    # 4지선다 버튼 (Streamlit 네이티브!)
    st.markdown('<div class="exam-options">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button(options[0], use_container_width=True, key=f"opt_0_{idx}"):
            handle_answer(0, correct_idx, current)
        if st.button(options[2], use_container_width=True, key=f"opt_2_{idx}"):
            handle_answer(2, correct_idx, current)
    with col2:
        if st.button(options[1], use_container_width=True, key=f"opt_1_{idx}"):
            handle_answer(1, correct_idx, current)
        if st.button(options[3], use_container_width=True, key=f"opt_3_{idx}"):
            handle_answer(3, correct_idx, current)
    st.markdown('</div>', unsafe_allow_html=True)

    # 진행 표시
    st.markdown(f"""
    <div style="text-align:center;margin-top:8px;color:#557788;font-size:11px;">
        진행: {idx + 1} / {total}
    </div>
    """, unsafe_allow_html=True)

    # 시간 초과 처리용 hidden 버튼 (JS가 자동 클릭)
    if st.button("TIMEOUT_HIDDEN", key=f"timeout_{idx}",
                 help="시간 초과 자동 처리"):
        handle_timeout(current)


def handle_answer(picked: int, correct: int, item: Dict):
    """학생이 4지선다 클릭 시 호출."""
    is_correct = (picked == correct)
    pos = item.get("pos", "noun")
    word = item["word"]

    # word_mastery에 즉시 기록!
    try:
        log_word_attempt(
            nickname=nickname,
            word=word,
            pos=pos,
            is_correct=is_correct,
        )
    except Exception:
        pass

    # 결과 누적
    results = st.session_state.get(EXAM_RESULTS_KEY, [])
    results.append({"word": word, "pos": pos, "correct": is_correct})
    st.session_state[EXAM_RESULTS_KEY] = results

    # 피드백 + 다음 단어
    st.session_state[EXAM_FEEDBACK_KEY] = "correct" if is_correct else "wrong"
    st.session_state[EXAM_INDEX_KEY] = st.session_state.get(EXAM_INDEX_KEY, 0) + 1
    st.rerun()


def handle_timeout(item: Dict):
    """시간 초과 시."""
    pos = item.get("pos", "noun")
    word = item["word"]

    try:
        log_word_attempt(
            nickname=nickname,
            word=word,
            pos=pos,
            is_correct=False,
        )
    except Exception:
        pass

    results = st.session_state.get(EXAM_RESULTS_KEY, [])
    results.append({"word": word, "pos": pos, "correct": False})
    st.session_state[EXAM_RESULTS_KEY] = results

    st.session_state[EXAM_FEEDBACK_KEY] = "timeout"
    st.session_state[EXAM_INDEX_KEY] = st.session_state.get(EXAM_INDEX_KEY, 0) + 1
    st.rerun()


def finish_exam():
    """시험 종료 — 결과 집계 + 메인으로."""
    results = st.session_state.get(EXAM_RESULTS_KEY, [])
    correct = sum(1 for r in results if r["correct"])
    wrong = sum(1 for r in results if not r["correct"])

    st.session_state["_pow_last_result"] = {
        "correct": correct,
        "wrong": wrong,
    }

    # 정리
    st.session_state.pop(GAME_WORDS_KEY, None)
    st.session_state.pop(GAME_TYPE_KEY, None)
    st.session_state.pop(EXAM_INDEX_KEY, None)
    st.session_state.pop(EXAM_RESULTS_KEY, None)
    st.session_state.pop(EXAM_FEEDBACK_KEY, None)
    set_mode("main")
    st.rerun()


# ═══════════════════════════════════════════════════════════════
# 라우팅
# ═══════════════════════════════════════════════════════════════

mode = get_mode()
if mode == "study":
    render_study_screen()
elif mode == "exam":
    render_exam_screen()
else:
    render_main_screen()
