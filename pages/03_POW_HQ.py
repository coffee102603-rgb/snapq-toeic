"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE:     pages/03_POW_HQ.py (v4 — 자동 수배 + 감방 이미지화)
ROLE:     단어 포로수용소
VERSION:  SnapQ TOEIC V3 — 2026.04.30
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
v4 변경:
    1. 감방 이미지화 (마스터=보라 왕실, 수배=빨강 어둠)
    2. JS → Python 자동 통신 (URL params 활용)
    3. 결과 보기 화면 제거 → 시험 끝 자동 처리

PAGE FLOW:
    main → study → exam → (auto save) → main

JS → PYTHON 통신 방식:
    시험 끝 → JS가 self.location 변경:
        ?nick=X&ag=1&wrong=word1,word2&pos=v,n,n
    → 페이지 리로드 → Python이 query_params 읽음
    → log_word_attempt() 자동 호출
    → 수배 감방 자동 활성화!
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

GAME_WORD_COUNT = 10
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

PAGE_MODE_KEY = "_pow_mode"
GAME_WORDS_KEY = "_pow_words"
GAME_TYPE_KEY = "_pow_type"


def get_mode() -> str:
    return st.session_state.get(PAGE_MODE_KEY, "main")


def set_mode(m: str):
    st.session_state[PAGE_MODE_KEY] = m


# ═══════════════════════════════════════════════════════════════
# 🎯 자동 결과 처리 — URL params로 받기
# ═══════════════════════════════════════════════════════════════

def process_exam_results_from_url():
    """
    URL params에서 시험 결과 읽어서 word_mastery 자동 업데이트.
    
    URL 형식: ?wrong=word1,word2&correct=word3,word4&posmap=word1:v,word2:n,...
    
    호출 시점: 페이지 로드 후 즉시 (메인 화면 렌더 전)
    """
    qp = st.query_params
    wrong_str = qp.get("wrong", "")
    correct_str = qp.get("correct", "")
    posmap_str = qp.get("posmap", "")

    if not wrong_str and not correct_str:
        return None  # 처리할 결과 없음

    # 품사 맵 파싱: "word1:v,word2:n,..."
    pos_map = {}
    if posmap_str:
        for pair in posmap_str.split(","):
            if ":" in pair:
                w, p = pair.split(":", 1)
                pos_full = {"n": "noun", "v": "verb", "a": "adjective", "r": "adverb"}.get(p, "noun")
                pos_map[w.strip()] = pos_full

    wrong_count = 0
    correct_count = 0

    # 정답 처리
    if correct_str:
        for w in correct_str.split(","):
            w = w.strip()
            if not w:
                continue
            try:
                log_word_attempt(
                    nickname=nickname,
                    word=w,
                    pos=pos_map.get(w, "noun"),
                    is_correct=True,
                )
                correct_count += 1
            except Exception:
                pass

    # 오답 처리 (수배 감방행!)
    if wrong_str:
        for w in wrong_str.split(","):
            w = w.strip()
            if not w:
                continue
            try:
                log_word_attempt(
                    nickname=nickname,
                    word=w,
                    pos=pos_map.get(w, "noun"),
                    is_correct=False,
                )
                wrong_count += 1
            except Exception:
                pass

    # URL params 정리 (다시 처리 안 되도록)
    # nick, ag만 남기고 나머지 제거
    new_params = {}
    if _qs_nick:
        new_params["nick"] = _qs_nick
    if _qs_ag:
        new_params["ag"] = _qs_ag
    st.query_params.clear()
    for k, v in new_params.items():
        st.query_params[k] = v

    return {"wrong": wrong_count, "correct": correct_count}


# 페이지 로드 시 즉시 처리
_exam_result = process_exam_results_from_url()
if _exam_result:
    set_mode("main")
    # 결과 잠시 표시용 세션 키
    st.session_state["_pow_last_result"] = _exam_result


# ═══════════════════════════════════════════════════════════════
# CSS — 감방 이미지화 + 컴팩트
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
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════
# 메인 화면 — 감방 이미지화!
# ═══════════════════════════════════════════════════════════════

def render_main_screen():
    """단어 포로수용소 메인 — 감방 이미지화."""

    # 컴팩트 헤더
    st.markdown("""
    <div style="text-align:center;margin-bottom:8px;">
        <div style="font-size:28px;line-height:1;">💀</div>
        <div style="color:#cc44ff;font-size:17px;font-weight:900;letter-spacing:2px;
                    margin-top:2px;">
            단어 포로수용소
        </div>
    </div>
    """, unsafe_allow_html=True)

    # 직전 시험 결과 잠시 표시
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

    # 🥉 마스터 감방 — 보라 왕실 감옥 느낌
    master_html = (
        '<div style="background:linear-gradient(135deg,#2a1a4a 0%,#1a1228 100%);'
        'border:2.5px solid #cc44ff;border-radius:12px;padding:14px 16px;'
        'margin-bottom:8px;position:relative;overflow:hidden;">'
        # 세로 창살
        '<div style="position:absolute;top:0;bottom:0;left:14%;width:2px;'
        'background:#cc44ff;opacity:0.35;"></div>'
        '<div style="position:absolute;top:0;bottom:0;left:38%;width:2px;'
        'background:#cc44ff;opacity:0.35;"></div>'
        '<div style="position:absolute;top:0;bottom:0;left:62%;width:2px;'
        'background:#cc44ff;opacity:0.35;"></div>'
        '<div style="position:absolute;top:0;bottom:0;left:86%;width:2px;'
        'background:#cc44ff;opacity:0.35;"></div>'
        # 가로 창살
        '<div style="position:absolute;top:0;left:0;right:0;height:2px;'
        'background:#cc44ff;opacity:0.6;"></div>'
        '<div style="position:absolute;bottom:0;left:0;right:0;height:2px;'
        'background:#cc44ff;opacity:0.6;"></div>'
        # 콘텐츠
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

    # 🎯 수배 감방 — 빨강 어둠의 감옥 느낌
    if wanted_count > 0:
        wanted_html = (
            '<div style="background:linear-gradient(135deg,#4a1a28 0%,#1a0810 100%);'
            'border:2.5px solid #ff4477;border-radius:12px;padding:14px 16px;'
            'margin:10px 0 8px;position:relative;overflow:hidden;">'
            # 가로 창살 (굵게)
            '<div style="position:absolute;top:0;left:0;right:0;height:4px;'
            'background:repeating-linear-gradient(90deg,#ff4477 0,#ff4477 8px,'
            '#220004 8px,#220004 16px);"></div>'
            '<div style="position:absolute;bottom:0;left:0;right:0;height:4px;'
            'background:repeating-linear-gradient(90deg,#ff4477 0,#ff4477 8px,'
            '#220004 8px,#220004 16px);"></div>'
            # 세로 창살
            '<div style="position:absolute;top:0;bottom:0;left:20%;width:2px;'
            'background:#ff4477;opacity:0.5;"></div>'
            '<div style="position:absolute;top:0;bottom:0;left:50%;width:2px;'
            'background:#ff4477;opacity:0.5;"></div>'
            '<div style="position:absolute;top:0;bottom:0;left:80%;width:2px;'
            'background:#ff4477;opacity:0.5;"></div>'
            # 콘텐츠
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
        # 수배 감방 비활성 (회색)
        st.markdown("""
        <div style="
            background: #14171f;
            border: 1.5px dashed #3a3f4a;
            border-radius: 12px;
            padding: 12px 16px;
            margin: 10px 0 8px;
            position: relative;
            opacity: 0.7;
        ">
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

    # 메인으로
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
# 학습장
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
.card-no {
    color: #5a6878;
    font-size: 8px;
    font-weight: 700;
    margin-bottom: 2px;
}
.card-en {
    color: #fff;
    font-size: 13px;
    font-weight: 800;
    word-break: break-word;
    line-height: 1.1;
}
.card-kr {
    color: __ACCENT_LIGHT__;
    font-size: 11px;
    font-weight: 700;
    line-height: 1.2;
    word-break: keep-all;
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
    cards_html = cards_html.replace("__ACCENT_LIGHT__",
                                     "#ff99bb" if game_type == "wanted" else "#dd99ff")

    components.html(cards_html, height=370, scrolling=False)

    st.markdown("<div style='margin-top:6px;'></div>", unsafe_allow_html=True)

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
# 시험장 — 끝나면 자동으로 URL params로 결과 전송!
# ═══════════════════════════════════════════════════════════════

def render_exam_screen():
    """시험장 — 두더지 시험. 끝나면 자동 URL params 전송."""
    words = st.session_state.get(GAME_WORDS_KEY, [])
    game_type = st.session_state.get(GAME_TYPE_KEY, "master")

    if not words:
        set_mode("main")
        st.rerun()
        return

    accent = "#ff4477" if game_type == "wanted" else "#cc44ff"

    exam_words = words.copy()
    random.shuffle(exam_words)
    for i, w in enumerate(exam_words, 1):
        w["display_no"] = i

    words_json = json.dumps(exam_words, ensure_ascii=False)

    # 시험 끝나면 페이지 자체를 리다이렉트 (Streamlit page url + query params)
    # 현재 페이지 URL 그대로 + wrong=...&correct=... 추가
    nick_for_url = nickname or ""

    game_html = """
<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #1a1f2e; color: #fff;
    padding: 12px 12px; min-height: 480px;
    position: relative; overflow: hidden;
}
.top-bar {
    position: absolute; top: 0; left: 0; right: 0; height: 4px;
    background: repeating-linear-gradient(90deg,
        __ACCENT__ 0, __ACCENT__ 10px, #555 10px, #555 20px);
}
.header { display: flex; align-items: center; gap: 8px; margin: 6px 0 8px; }
.header-emoji { font-size: 22px; }
.header-title {
    color: __ACCENT__; font-size: 14px; font-weight: 800;
    letter-spacing: 2px;
}
.header-sub {
    color: #88aabb; font-size: 9px; margin-top: 1px;
    letter-spacing: 1px;
}
.header-counter { margin-left: auto; text-align: right; }
.counter-label { color: #7a8fa8; font-size: 8px; letter-spacing: 1px; }
.counter-value { color: __ACCENT__; font-size: 16px; font-weight: 700; }
.skull-quote {
    background: #243044; border: 1px solid #3d5278;
    border-radius: 6px; padding: 5px 8px; margin-bottom: 8px;
    display: flex; align-items: center; gap: 6px;
    min-height: 26px;
}
.skull-quote-text {
    color: #ddccaa; font-size: 10px; font-style: italic;
    line-height: 1.3; flex: 1;
}
.timer-box { margin-bottom: 10px; display: flex; align-items: center; gap: 6px; }
.timer-icon {
    font-size: 11px; color: #88aabb;
    font-weight: 700; min-width: 16px;
}
.timer-bar {
    flex: 1; background: #0e1220; border: 1px solid #2a3550;
    border-radius: 20px; height: 8px; overflow: hidden;
}
.timer-fill {
    height: 100%; width: 100%;
    background: linear-gradient(90deg, #22cc88, #88ffcc);
    transition: width 0.1s linear;
    border-radius: 20px;
}
.timer-text {
    color: #88ffcc; font-size: 13px; font-weight: 700;
    min-width: 32px; text-align: right;
}
.word-card {
    background: #243044; border: 2px solid #3d5278;
    border-radius: 10px; padding: 14px 10px;
    text-align: center; margin-bottom: 10px;
    position: relative; overflow: hidden;
}
.word-card-bars {
    position: absolute; top: 0; bottom: 0; left: 0; width: 100%;
    background: repeating-linear-gradient(0deg,
        transparent 0, transparent 20px,
        rgba(120,140,180,0.15) 20px,
        rgba(120,140,180,0.15) 22px);
    pointer-events: none;
}
.word-card-label {
    position: relative; display: flex;
    align-items: center; justify-content: center; gap: 6px;
    margin-bottom: 4px;
}
.word-card-label-text {
    color: #7a8fa8; font-size: 8px; font-weight: 700;
    letter-spacing: 2px;
}
.word-display {
    position: relative; color: #fff;
    font-size: 26px; font-weight: 800;
    letter-spacing: 1px;
}
.options { display: grid; grid-template-columns: 1fr 1fr; gap: 6px; }
.option-btn {
    background: #243044; border: 1px solid #3d5278;
    border-radius: 8px; padding: 11px 4px;
    color: #ccddee; font-size: 12px; font-weight: 700;
    cursor: pointer; font-family: inherit;
    transition: all 0.2s; width: 100%;
    word-break: keep-all;
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
    text-align: center; margin-top: 8px; height: 20px;
    font-size: 12px; font-weight: 800; letter-spacing: 1px;
}
.done-screen { text-align: center; padding: 20px 16px; }
.done-emoji { font-size: 48px; }
.done-text {
    color: __ACCENT__; font-size: 18px; font-weight: 900;
    margin-top: 8px; letter-spacing: 2px;
}
.done-stats {
    margin-top: 14px;
    background: #243044; border: 1px solid #3d5278;
    border-radius: 8px; padding: 10px;
}
.stat-row {
    display: flex; justify-content: space-between;
    padding: 4px 0; font-size: 12px;
}
.stat-row + .stat-row { border-top: 1px dashed #3d5278; }
.redirecting {
    color: #88aabb; font-size: 10px; margin-top: 12px;
    font-style: italic;
}
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
    <span style="font-size:12px;">💀</span>
    <div class="skull-quote-text" id="skull-quote">10명을 심문할 시간이다</div>
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
      <span style="font-size:12px;">⛓️</span>
      <span class="word-card-label-text" id="word-label">단어 #1</span>
      <span style="font-size:12px;">⛓️</span>
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
    <div class="redirecting">자동으로 처리 중... ⏳</div>
  </div>
</div>

<script>
const ALL_WORDS = __WORDS_JSON__;
const TIMER_SEC = __TIMER__;
const NICK = "__NICK__";

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
    document.getElementById('feedback').textContent = '⏰ 시간 초과! 수배행!';
    wrongList.push(currentItem);
    setTimeout(nextWord, 700);
}

function pickOpt(btn, idx) {
    if (timerInterval) clearInterval(timerInterval);
    document.querySelectorAll('.option-btn').forEach(b => b.disabled = true);
    const fb = document.getElementById('feedback');
    if (idx === currentItem.correct_index) {
        btn.classList.add('correct');
        fb.style.color = '#88ffcc';
        fb.textContent = '🔒 체포!';
        correctList.push(currentItem);
    } else {
        btn.classList.add('wrong');
        fb.style.color = '#ff8844';
        fb.textContent = '💨 탈출! 수배행!';
        wrongList.push(currentItem);
    }
    setTimeout(nextWord, 700);
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

function posCode(p) {
    const map = {noun:'n', verb:'v', adjective:'a', adverb:'r'};
    return map[p] || 'n';
}

function showDone() {
    if (timerInterval) clearInterval(timerInterval);
    document.getElementById('game-area').style.display = 'none';
    document.getElementById('done-area').style.display = 'block';
    const stats = document.getElementById('done-stats');
    stats.innerHTML =
        '<div class="stat-row"><span style="color:#88ffcc;">✅ 체포</span>' +
        '<span style="color:#fff;font-weight:900;">' + correctList.length + '명</span></div>' +
        '<div class="stat-row"><span style="color:#ff8844;">🎯 수배행</span>' +
        '<span style="color:#fff;font-weight:900;">' + wrongList.length + '명</span></div>';
    
    // 1.5초 후 자동으로 부모 페이지로 redirect (결과 URL params 포함)
    setTimeout(() => {
        const wrongStr = wrongList.map(w => w.word).join(',');
        const correctStr = correctList.map(w => w.word).join(',');
        const allItems = [...correctList, ...wrongList];
        const posStr = allItems.map(w => w.word + ':' + posCode(w.pos || 'noun')).join(',');
        
        const params = new URLSearchParams();
        if (NICK) {
            params.set('nick', NICK);
            params.set('ag', '1');
        }
        if (wrongStr) params.set('wrong', wrongStr);
        if (correctStr) params.set('correct', correctStr);
        if (posStr) params.set('posmap', posStr);
        
        const newUrl = window.parent.location.pathname + '?' + params.toString();
        try {
            window.parent.location.href = newUrl;
        } catch(e) {
            // 폴백: 같은 창에서 시도
            window.top.location.href = newUrl;
        }
    }, 1800);
}

setTimeout(nextWord, 200);
</script>
</body></html>
"""

    game_html = game_html.replace("__WORDS_JSON__", words_json)
    game_html = game_html.replace("__TIMER__", str(TIMER_SECONDS))
    game_html = game_html.replace("__ACCENT__", accent)
    game_html = game_html.replace("__NICK__", nick_for_url)

    components.html(game_html, height=540, scrolling=False)

    # 안내 — 자동 처리되니까 버튼 없음
    st.markdown("""
    <div style="text-align:center;margin-top:8px;color:#445566;font-size:11px;
                font-style:italic;">
        ⚡ 시험 끝나면 자동으로 처리돼
    </div>
    """, unsafe_allow_html=True)

    # 비상 탈출 버튼 (만약 자동 처리 안 될 때)
    if st.button("🏠 메인으로 (강제)", use_container_width=False, key="btn_emergency_back"):
        st.session_state.pop(GAME_WORDS_KEY, None)
        st.session_state.pop(GAME_TYPE_KEY, None)
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
