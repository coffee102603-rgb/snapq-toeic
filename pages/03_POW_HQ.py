"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE:     pages/03_POW_HQ.py (v7 — 분위기 차별화)
ROLE:     단어 포로수용소
VERSION:  SnapQ TOEIC V3 — 2026.04.30
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v7 변경:
    1. 마스터 감방 = 왕실 던전 (보라/금색, 위엄 톤)
    2. 수배 감방 = 지옥 감옥 (빨강/검정, 거친 톤)
    3. 결과 카드 위로 (시험 끝 후 한 화면에)
    4. TIMEOUT_HIDDEN 버튼 숨김
    5. 멘트 차별화 (마스터: 위엄 / 수배: 거침)
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
PAGE_MODE_KEY = "_pow_mode"
GAME_WORDS_KEY = "_pow_words"
GAME_TYPE_KEY = "_pow_type"
EXAM_INDEX_KEY = "_pow_exam_idx"
EXAM_RESULTS_KEY = "_pow_results"
EXAM_FEEDBACK_KEY = "_pow_feedback"


def get_mode() -> str:
    return st.session_state.get(PAGE_MODE_KEY, "main")


def set_mode(m: str):
    st.session_state[PAGE_MODE_KEY] = m


# ═══════════════════════════════════════════════════════════════
# 멘트 풀 (차별화)
# ═══════════════════════════════════════════════════════════════

MASTER_QUOTES = [
    "왕실의 시험이다.",
    "단어를 정복하라.",
    "이 단어를 외워라.",
    "위엄을 보여라.",
    "마스터의 길이다.",
]

WANTED_QUOTES = [
    "또 도망쳤어? 이번엔 잡는다!",
    "이놈 끈질기네. 잡아!",
    "수배범, 이번엔 못 도망간다.",
    "다시 만난 놈이다. 끝장낸다.",
    "이놈 또 탈출하려고? 안 된다!",
]


# ═══════════════════════════════════════════════════════════════
# CSS — TIMEOUT_HIDDEN 버튼 숨김 + 시험장 버튼 스타일
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

/* 시험장 4지선다 버튼 */
.exam-options div.stButton > button {
    padding: 16px 8px !important;
    font-size: 14px !important;
    border: 1.5px solid #3d5278 !important;
    background: #243044 !important;
    color: #ccddee !important;
    min-height: 60px !important;
    word-break: keep-all !important;
}

/* TIMEOUT_HIDDEN 버튼 숨기기 — 텍스트로 매칭 */
button:has(div p:contains("TIMEOUT_HIDDEN")),
[data-testid="stButton"] button[aria-label*="TIMEOUT"] {
    display: none !important;
    visibility: hidden !important;
}
</style>

<script>
// TIMEOUT_HIDDEN 버튼 숨기기 (CSS :contains이 모든 브라우저에서 안 되니 JS로도)
(function hideTimeoutButtons() {
    const buttons = document.querySelectorAll('button');
    for (const btn of buttons) {
        if (btn.textContent && btn.textContent.includes('TIMEOUT_HIDDEN')) {
            btn.style.display = 'none';
            btn.style.height = '0';
            btn.style.overflow = 'hidden';
            btn.style.padding = '0';
            btn.style.margin = '0';
            // 부모 컨테이너도 숨기기
            const parent = btn.closest('[data-testid="stButton"]');
            if (parent) {
                parent.style.display = 'none';
                parent.style.height = '0';
            }
        }
    }
})();

// 페이지 변화 감지해서 계속 숨기기
const observer = new MutationObserver(() => {
    const buttons = document.querySelectorAll('button');
    for (const btn of buttons) {
        if (btn.textContent && btn.textContent.includes('TIMEOUT_HIDDEN')) {
            btn.style.display = 'none';
            const parent = btn.closest('[data-testid="stButton"]');
            if (parent) parent.style.display = 'none';
        }
    }
});
observer.observe(document.body, { childList: true, subtree: true });
</script>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# 메인 화면 — 분위기 차별화!
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

    # 🥉 마스터 감방 — 왕실 던전 (보라+금색)
    master_html = (
        '<div style="background:linear-gradient(135deg,#2a1a4a 0%,#1a1228 50%,#3a2055 100%);'
        'border:2.5px solid #ffcc44;border-radius:12px;padding:16px 16px;'
        'margin-bottom:8px;position:relative;overflow:hidden;'
        'box-shadow:0 0 18px rgba(204,68,255,0.2);">'
        # 가는 세로 창살 (왕실 느낌)
        '<div style="position:absolute;top:0;bottom:0;left:14%;width:1.5px;'
        'background:linear-gradient(180deg,#ffcc44 0%,#cc44ff 100%);opacity:0.4;"></div>'
        '<div style="position:absolute;top:0;bottom:0;left:38%;width:1.5px;'
        'background:linear-gradient(180deg,#ffcc44 0%,#cc44ff 100%);opacity:0.4;"></div>'
        '<div style="position:absolute;top:0;bottom:0;left:62%;width:1.5px;'
        'background:linear-gradient(180deg,#ffcc44 0%,#cc44ff 100%);opacity:0.4;"></div>'
        '<div style="position:absolute;top:0;bottom:0;left:86%;width:1.5px;'
        'background:linear-gradient(180deg,#ffcc44 0%,#cc44ff 100%);opacity:0.4;"></div>'
        # 가로 — 왕실 띠 (금색)
        '<div style="position:absolute;top:0;left:0;right:0;height:2px;'
        'background:linear-gradient(90deg,transparent,#ffcc44,transparent);"></div>'
        '<div style="position:absolute;bottom:0;left:0;right:0;height:2px;'
        'background:linear-gradient(90deg,transparent,#ffcc44,transparent);"></div>'
        # 콘텐츠
        '<div style="position:relative;text-align:center;">'
        '<div style="display:flex;align-items:center;justify-content:center;'
        'gap:8px;margin-bottom:4px;">'
        '<span style="font-size:14px;color:#ffcc44;">⚜️</span>'
        f'<span style="font-size:24px;">{tier_emoji}</span>'
        '<span style="color:#ffd966;font-size:16px;font-weight:900;'
        'letter-spacing:2px;text-shadow:0 0 8px rgba(255,204,68,0.4);">'
        '👑 마스터 감방</span>'
        f'<span style="font-size:24px;">{tier_emoji}</span>'
        '<span style="font-size:14px;color:#ffcc44;">⚜️</span>'
        '</div>'
        f'<div style="color:#ffaaff;font-size:24px;font-weight:900;'
        f'line-height:1;">{progress_text}</div>'
        '<div style="color:#aabbcc;font-size:11px;margin-top:4px;">'
        f'<strong style="color:#ffcc44;">{tier_label}</strong> 도전 중'
        '</div>'
        '<div style="color:#7766aa;font-size:9px;margin-top:2px;font-style:italic;">'
        '⚜️ 왕실의 시험이다 ⚜️</div>'
        '</div>'
        '</div>'
    )
    st.markdown(master_html, unsafe_allow_html=True)

    if st.button("👑 마스터 감방 입장", use_container_width=True, type="primary",
                 key="btn_master"):
        words = build_master_game_words(nickname)
        if not words:
            st.warning("학습할 단어가 없어요.")
        else:
            st.session_state[GAME_WORDS_KEY] = words
            st.session_state[GAME_TYPE_KEY] = "master"
            set_mode("study")
            st.rerun()

    # 🎯 수배 감방 — 지옥 감옥 (빨강+검정)
    if wanted_count > 0:
        wanted_html = (
            '<div style="background:linear-gradient(135deg,#5a0a14 0%,#000 50%,#3a0a08 100%);'
            'border:2.5px solid #ff2244;border-radius:12px;padding:16px 16px;'
            'margin:10px 0 8px;position:relative;overflow:hidden;'
            'box-shadow:0 0 18px rgba(255,34,68,0.25);">'
            # 굵은 가로 창살 (지옥 느낌)
            '<div style="position:absolute;top:0;left:0;right:0;height:5px;'
            'background:repeating-linear-gradient(90deg,#ff2244 0,#ff2244 6px,'
            '#000 6px,#000 12px);"></div>'
            '<div style="position:absolute;bottom:0;left:0;right:0;height:5px;'
            'background:repeating-linear-gradient(90deg,#ff2244 0,#ff2244 6px,'
            '#000 6px,#000 12px);"></div>'
            # X자 사슬 느낌 (대각선)
            '<div style="position:absolute;top:0;bottom:0;left:25%;width:2px;'
            'background:#ff2244;opacity:0.4;transform:skewX(-5deg);"></div>'
            '<div style="position:absolute;top:0;bottom:0;left:50%;width:2px;'
            'background:#ff2244;opacity:0.6;"></div>'
            '<div style="position:absolute;top:0;bottom:0;left:75%;width:2px;'
            'background:#ff2244;opacity:0.4;transform:skewX(5deg);"></div>'
            # 콘텐츠
            '<div style="position:relative;text-align:center;">'
            '<div style="display:flex;align-items:center;justify-content:center;'
            'gap:8px;margin-bottom:4px;">'
            '<span style="font-size:14px;">⛓️</span>'
            '<span style="font-size:24px;">🎯</span>'
            '<span style="color:#ff6688;font-size:16px;font-weight:900;'
            'letter-spacing:2px;text-shadow:0 0 8px rgba(255,34,68,0.5);">'
            '🔥 수배 감방</span>'
            '<span style="font-size:24px;">🎯</span>'
            '<span style="font-size:14px;">⛓️</span>'
            '</div>'
            f'<div style="color:#ff4477;font-size:24px;font-weight:900;'
            f'line-height:1;text-shadow:0 0 6px rgba(255,68,119,0.6);">'
            f'{wanted_count}명 수감</div>'
            '<div style="color:#ffaa99;font-size:11px;margin-top:4px;">'
            '<strong style="color:#ff8844;">자꾸 도망친 놈들</strong>'
            '</div>'
            '<div style="color:#aa4455;font-size:9px;margin-top:2px;font-style:italic;">'
            '⛓️ 끝까지 잡아라 ⛓️</div>'
            '</div>'
            '</div>'
        )
        st.markdown(wanted_html, unsafe_allow_html=True)

        if st.button("🔥 수배 감방 진압", use_container_width=True,
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
# 학습장 — 분위기 차별화!
# ═══════════════════════════════════════════════════════════════

def render_study_screen():
    words = st.session_state.get(GAME_WORDS_KEY, [])
    game_type = st.session_state.get(GAME_TYPE_KEY, "master")

    if not words:
        set_mode("main")
        st.rerun()
        return

    # 게임 타입별 차별화
    if game_type == "wanted":
        accent = "#ff4477"
        accent_light = "#ff99bb"
        title = "🔥 수배 감방 학습장"
        subtitle = "⛓️ 도망친 놈들을 외워라"
        title_color = "#ff6688"
        bg_pattern = "wanted"
    else:
        accent = "#ffcc44"
        accent_light = "#ffd966"
        title = "👑 왕실 학습장"
        subtitle = "⚜️ 단어를 외워서 왕실에 입성하라"
        title_color = "#ffd966"
        bg_pattern = "master"

    st.markdown(f"""
    <div style="text-align:center;margin-bottom:6px;">
        <div style="display:flex;align-items:center;justify-content:center;gap:8px;">
            <span style="font-size:20px;">🃏</span>
            <span style="color:{title_color};font-size:14px;font-weight:900;letter-spacing:2px;
                        text-shadow:0 0 6px {accent}55;">
                {title}
            </span>
        </div>
        <div style="color:#557788;font-size:10px;margin-top:1px;font-style:italic;">
            {subtitle}
        </div>
    </div>
    """, unsafe_allow_html=True)

    words_simple = [
        {"word": w["word"], "meaning": w["meaning"], "no": i + 1}
        for i, w in enumerate(words)
    ]
    words_json = json.dumps(words_simple, ensure_ascii=False)

    # 카드 배경 차별화
    if bg_pattern == "wanted":
        card_bg = "#2a0e1a"
        card_border = "#5a2a3a"
        card_flipped_bg = "#3a1820"
    else:
        card_bg = "#1a1838"
        card_border = "#3d2a78"
        card_flipped_bg = "#2a1a48"

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
    background: __CARD_BG__;
    border: 1.5px solid __CARD_BORDER__;
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
    background: __CARD_FLIPPED_BG__;
    border-color: __ACCENT__;
    box-shadow: 0 0 8px __ACCENT__44;
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
.card-no {
    color: #5a6878; font-size: 8px; font-weight: 700; margin-bottom: 2px;
}
.card-en {
    color: #fff; font-size: 13px; font-weight: 800;
    word-break: break-word; line-height: 1.1;
}
.card-kr {
    color: __ACCENT_LIGHT__; font-size: 11px; font-weight: 700;
    line-height: 1.2; word-break: keep-all;
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
    cards_html = cards_html.replace("__ACCENT_LIGHT__", accent_light)
    cards_html = cards_html.replace("__CARD_BG__", card_bg)
    cards_html = cards_html.replace("__CARD_BORDER__", card_border)
    cards_html = cards_html.replace("__CARD_FLIPPED_BG__", card_flipped_bg)

    components.html(cards_html, height=370, scrolling=False)

    st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])
    with col1:
        exam_label = "🔥 진압 시작!" if game_type == "wanted" else "⚔️ 시험장 입장!"
        if st.button(exam_label, use_container_width=True, type="primary",
                     key="btn_to_exam"):
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
# ⚔️ 시험장 — 분위기 차별화!
# ═══════════════════════════════════════════════════════════════

def render_exam_screen():
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

    # 게임 타입별 차별화
    if game_type == "wanted":
        accent = "#ff4477"
        accent_dark = "#aa1133"
        title = "🔥 수배 진압"
        subtitle = "⛓️ 끝까지 잡아라!"
        timer_color_safe = "#ff8844"
        timer_color_warn = "#ff2244"
        word_card_bg = "#3a0a14"
        word_card_border = "#7a2a3a"
        bar_pattern = "wanted"
        quotes = WANTED_QUOTES
    else:
        accent = "#ffcc44"
        accent_dark = "#aa8822"
        title = "👑 왕실 시험"
        subtitle = "⚜️ 위엄을 보여라!"
        timer_color_safe = "#ffd966"
        timer_color_warn = "#ff8844"
        word_card_bg = "#2a1a4a"
        word_card_border = "#7a5acc"
        bar_pattern = "master"
        quotes = MASTER_QUOTES

    current = words[idx]
    word = current["word"]
    options = current["options"]
    correct_idx = current["correct_index"]
    display_no = current["display_no"]

    total = len(words)
    remaining = total - idx

    # 멘트 (랜덤)
    quote = random.choice(quotes)
    quote_emoji = "👑" if game_type == "master" else "💀"

    # 헤더 — 게임 타입별 차별화
    header_html = (
        f'<div style="background:#1a1f2e;border:1.5px solid {accent};border-radius:10px;'
        f'padding:8px 12px;margin-bottom:8px;display:flex;align-items:center;gap:10px;'
        f'box-shadow:0 0 12px {accent}22;">'
        f'<span style="font-size:20px;">{quote_emoji}</span>'
        f'<div>'
        f'<div style="color:{accent};font-size:13px;font-weight:900;letter-spacing:2px;">'
        f'{title}</div>'
        f'<div style="color:#88aabb;font-size:9px;">{subtitle}</div>'
        f'</div>'
        f'<div style="margin-left:auto;text-align:right;">'
        f'<div style="color:#7a8fa8;font-size:8px;">남은 단어</div>'
        f'<div style="color:{accent};font-size:16px;font-weight:700;">{remaining} / {total}</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(header_html, unsafe_allow_html=True)

    # 멘트 박스
    quote_html = (
        f'<div style="background:#243044;border:1px solid {accent_dark};'
        f'border-radius:6px;padding:5px 10px;margin-bottom:8px;'
        f'display:flex;align-items:center;gap:6px;min-height:26px;">'
        f'<span style="font-size:12px;">{quote_emoji}</span>'
        f'<div style="color:#ddccaa;font-size:11px;font-style:italic;flex:1;">'
        f'{quote}</div>'
        f'</div>'
    )
    st.markdown(quote_html, unsafe_allow_html=True)

    # 단어 카드 — 게임 타입별 차별화
    if bar_pattern == "wanted":
        # 가로 사슬 패턴
        bar_style = (
            "background:repeating-linear-gradient(90deg,transparent 0,transparent 18px,"
            "rgba(255,68,119,0.2) 18px,rgba(255,68,119,0.2) 20px);"
        )
    else:
        # 세로 왕실 창살
        bar_style = (
            "background:repeating-linear-gradient(0deg,transparent 0,transparent 20px,"
            "rgba(255,204,68,0.15) 20px,rgba(255,204,68,0.15) 22px);"
        )

    word_card_html = (
        f'<div style="background:{word_card_bg};border:2px solid {word_card_border};'
        f'border-radius:10px;padding:14px 10px;text-align:center;margin-bottom:10px;'
        f'position:relative;overflow:hidden;'
        f'box-shadow:0 0 14px {accent}22;">'
        f'<div style="position:absolute;top:0;bottom:0;left:0;right:0;'
        f'{bar_style}pointer-events:none;"></div>'
        f'<div style="position:relative;display:flex;align-items:center;'
        f'justify-content:center;gap:6px;margin-bottom:4px;">'
        f'<span style="font-size:12px;">⛓️</span>'
        f'<span style="color:{accent};font-size:8px;font-weight:700;'
        f'letter-spacing:2px;">단어 #{display_no}</span>'
        f'<span style="font-size:12px;">⛓️</span>'
        f'</div>'
        f'<div style="position:relative;color:#fff;font-size:26px;'
        f'font-weight:800;letter-spacing:1px;">{word}</div>'
        f'</div>'
    )
    st.markdown(word_card_html, unsafe_allow_html=True)

    # 직전 답변 피드백
    feedback = st.session_state.pop(EXAM_FEEDBACK_KEY, None)
    if feedback:
        if feedback == "correct":
            msg_color = "#88ffcc"
            msg_bg = "#0a3322"
            msg_border = "#22cc88"
            msg_text = "🔒 체포!"
        elif feedback == "wrong":
            msg_color = "#ffaa88"
            msg_bg = "#3a1010"
            msg_border = "#ff4422"
            msg_text = "💨 탈출! 수배행!"
        else:  # timeout
            msg_color = "#ffaa88"
            msg_bg = "#3a2010"
            msg_border = "#ff8844"
            msg_text = "⏰ 시간 초과! 수배행!"

        st.markdown(f"""
        <div style="background:{msg_bg};border:1.5px solid {msg_border};border-radius:8px;
                    padding:6px 10px;margin-bottom:8px;text-align:center;">
            <span style="color:{msg_color};font-size:13px;font-weight:800;">{msg_text}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        # 타이머 (피드백 없을 때만, 게임 타입별 색)
        timer_html = """
<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
body { margin: 0; padding: 0; background: transparent; font-family: system-ui; }
.timer-box { display: flex; align-items: center; gap: 6px; padding: 0; }
.timer-icon { font-size: 11px; color: #88aabb; min-width: 16px; }
.timer-bar {
    flex: 1; background: #0e1220; border: 1px solid #2a3550;
    border-radius: 20px; height: 8px; overflow: hidden;
}
.timer-fill {
    height: 100%; width: 100%;
    background: linear-gradient(90deg, __TIMER_SAFE__, __TIMER_SAFE_END__);
    transition: width 0.1s linear; border-radius: 20px;
}
.timer-text {
    color: __TIMER_SAFE__; font-size: 13px; font-weight: 700;
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
        // 시간 초과 시 시각 효과만 (자동 처리 X)
        document.getElementById('txt').textContent = '⏰ 빨리!';
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
        bar.style.background = '__TIMER_WARN__';
        txt.style.color = '__TIMER_WARN__';
        tb.classList.add('timer-warn');
    } else if (timeLeft <= 2.0) {
        bar.style.background = 'linear-gradient(90deg,__TIMER_SAFE_END__,__TIMER_WARN__)';
        txt.style.color = '__TIMER_SAFE_END__';
        tb.classList.remove('timer-warn');
    }
}
</script>
</body></html>
"""
        # 게임 타입별 타이머 색
        if game_type == "wanted":
            timer_safe = "#ff8844"
            timer_safe_end = "#ffcc88"
        else:
            timer_safe = "#ffcc44"
            timer_safe_end = "#ffe699"

        timer_html = timer_html.replace("__TIMER_SAFE__", timer_safe)
        timer_html = timer_html.replace("__TIMER_SAFE_END__", timer_safe_end)
        timer_html = timer_html.replace("__TIMER_WARN__", timer_color_warn)
        components.html(timer_html, height=24)

    # 4지선다 버튼
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

    # 시간 초과 기능 제거 (학생이 직접 클릭해야 함)


def handle_answer(picked: int, correct: int, item: Dict):
    is_correct = (picked == correct)
    pos = item.get("pos", "noun")
    word = item["word"]

    try:
        log_word_attempt(
            nickname=nickname,
            word=word,
            pos=pos,
            is_correct=is_correct,
        )
    except Exception:
        pass

    results = st.session_state.get(EXAM_RESULTS_KEY, [])
    results.append({"word": word, "pos": pos, "correct": is_correct})
    st.session_state[EXAM_RESULTS_KEY] = results

    st.session_state[EXAM_FEEDBACK_KEY] = "correct" if is_correct else "wrong"
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
