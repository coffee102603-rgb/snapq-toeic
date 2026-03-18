# ============================================
# LOSTLOCK_PATCHED_v2: wrong answer immediately ends set (YOU LOST screen); no answer reveal
# Timebomb + Vocab Save(클릭 세이브) + Level System
# ============================================
# FINAL_PATCHED_LOST_SCREEN_V4: fail -> YOU LOST only; analysis/armory unlock only on 3/3

import time
import random
import json
import os
from dataclasses import dataclass, field
from typing import List, Dict

import streamlit as st

def inject_css():
    """Small CSS helpers for the P7 battle screen (keeps the module self-contained)."""
    st.markdown(
        """<style>
        /* hide default sidebar space if any */
        section[data-testid="stSidebar"]{ display:none !important; }
        [data-testid="collapsedControl"]{ display:none !important; }

        /* ===== P7 DARK ARCADE THEME (Option1) ===== */
        .stApp{
            background: radial-gradient(1200px 800px at 10% 0%, rgba(124,58,237,.35) 0%, rgba(6,182,212,.18) 35%, rgba(2,6,23,1) 100%) !important;
            color: #f5f7ff !important;
        }
        /* default text colors */
        .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span, .stMarkdown div,
        [data-testid="stMarkdownContainer"]{
            color:#f5f7ff !important;
        }
        /* inputs + radio label color */
        label, .stRadio label, .stRadio div, .stSelectbox label, .stTextInput label{
            color:#f5f7ff !important;
        }

        /* right HUD title (verification marker: p7_hud_title) */
        .p7_hud_title{
            font-size: 30px;
            font-weight: 900;
            letter-spacing: .2px;
            text-align: right;
            margin: 2px 0 10px 0;
            color: #ffffff;
            text-shadow: 0 10px 30px rgba(0,0,0,.35);
        }
        

        /* STEP HUD panel */
        .p7_step_panel{
            width: 100%;
            padding: 14px 14px 10px 14px;
            border-radius: 18px;
            background: rgba(255,255,255,0.10);
            border: 1px solid rgba(255,255,255,0.12);
            box-shadow: 0 10px 30px rgba(0,0,0,0.22);
            backdrop-filter: blur(10px);
            margin-bottom: 8px;
        }
        .p7_step_title{
            font-weight: 900;
            letter-spacing: 0.08em;
            opacity: 0.85;
            margin-bottom: 8px;
        }
        </style>""",
        unsafe_allow_html=True,
    )


def _safe_switch_page(candidates, fallback_hint: str = "") -> bool:
    """
    st.switch_page()를 안전하게 호출한다.
    - candidates: 시도할 페이지 경로 후보 리스트
    - 성공하면 True / 모두 실패하면 False
    """
    for p in candidates:
        try:
            st.switch_page(p)
            return True
        except Exception:
            continue
    if fallback_hint:
        st.warning(f"이동 경로를 찾지 못했습니다. ({fallback_hint}) 페이지 파일명/경로를 확인해주세요.")
    else:
        st.warning("이동 경로를 찾지 못했습니다. 페이지 파일명/경로를 확인해주세요.")
    return False


# --------------------------------------------
# 🔗 P7 / Vocab 기록 & 비밀무기고 카운트 연동
#   - record_p7_result(...)
#   - update_secret_armory_count(reason="add_from_p7")
# --------------------------------------------
try:
    # app 패키지 안에 있을 때 (예: app/stats_p7_vocab.py)
    from app.stats_p7_vocab import record_p7_result, update_secret_armory_count
except Exception:
    try:
        # 프로젝트 루트에 있을 때 (예: stats_p7_vocab.py)
        from stats_p7_vocab import record_p7_result, update_secret_armory_count
    except Exception:
        # 개발 중 import 에러가 나도 화면이 완전히 죽지 않게 방어
        record_p7_result = None
        update_secret_armory_count = None

IS_DIRECT_RUN = __name__ == "__main__"

if IS_DIRECT_RUN:
    st.set_page_config(
        page_title="SnapQ P7 Reading + Armory",
        page_icon="🔥",
        layout="wide",
    )

# ---------- 점수/랭킹 통계 파일 설정 ----------

STATS_FILE = "p7_vocab_stats.json"


def _get_stats_path() -> str:
    base_dir = os.path.dirname(__file__) if "__file__" in globals() else os.getcwd()
    return os.path.join(base_dir, STATS_FILE)


def _get_default_stats() -> Dict:
    return {
        "p7": {
            "total_sets": 0,
            "total_correct": 0,
            "total_questions": 0,
            "best_combo": 0,
            "last_played": "",
        },
        "vocab": {
            "total_sets": 0,
            "total_correct": 0,
            "total_questions": 0,
            "best_score": 0,
            "last_played": "",
        },
    }


def load_stats() -> Dict:
    path = _get_stats_path()
    if not os.path.exists(path):
        return _get_default_stats()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return _get_default_stats()

    base = _get_default_stats()
    for key in base:
        if key not in data or not isinstance(data[key], dict):
            data[key] = base[key]
        else:
            for sub_k, sub_v in base[key].items():
                if sub_k not in data[key]:
                    data[key][sub_k] = sub_v
    return data


def save_stats(stats: Dict) -> None:
    path = _get_stats_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def update_stats_after_p7_set(correct_count: int, total_questions: int, max_combo: int) -> None:
    stats = load_stats()
    p7 = stats.get("p7", {})
    p7["total_sets"] = p7.get("total_sets", 0) + 1
    p7["total_correct"] = p7.get("total_correct", 0) + int(correct_count)
    p7["total_questions"] = p7.get("total_questions", 0) + int(total_questions)
    prev_best = p7.get("best_combo", 0)
    p7["best_combo"] = max(prev_best, int(max_combo))
    p7["last_played"] = time.strftime("%Y-%m-%d %H:%M", time.localtime())
    stats["p7"] = p7
    save_stats(stats)


def update_stats_after_vocab_set(score: int, total_questions: int) -> None:
    stats = load_stats()
    vocab = stats.get("vocab", {})
    vocab["total_sets"] = vocab.get("total_sets", 0) + 1
    vocab["total_correct"] = vocab.get("total_correct", 0) + int(score)
    vocab["total_questions"] = vocab.get("total_questions", 0) + int(total_questions)
    prev_best = vocab.get("best_score", 0)
    vocab["best_score"] = max(prev_best, int(score))
    vocab["last_played"] = time.strftime("%Y-%m-%d %H:%M", time.localtime())
    stats["vocab"] = vocab
    save_stats(stats)

# ---------- P7 레벨 시스템 파일 설정 ----------

LEVEL_FILE = "p7_level_progress.json"


def _get_level_path() -> str:
    base_dir = os.path.dirname(__file__) if "__file__" in globals() else os.getcwd()
    return os.path.join(base_dir, LEVEL_FILE)


def _default_level_progress() -> Dict:
    return {
        "categories": {},
        "last_updated": "",
    }


def load_level_progress() -> Dict:
    path = _get_level_path()
    if not os.path.exists(path):
        return _default_level_progress()
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return _default_level_progress()

    if "categories" not in data or not isinstance(data["categories"], dict):
        data["categories"] = {}
    if "last_updated" not in data:
        data["last_updated"] = ""
    return data


def save_level_progress(progress: Dict) -> None:
    path = _get_level_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(progress, f, ensure_ascii=False, indent=2)
    except OSError:
        pass


def _ensure_category(progress: Dict, category: str) -> Dict:
    cat = progress["categories"].get(category)
    if not cat:
        cat = {
            "level": 1,         # Lv1 시작
            "streak": 0,        # 현재 레벨에서 연속 클리어 횟수
            "cleared_sets": 0,  # 클리어한 세트 수
            "total_sets": 0,    # 전체 세트 수
        }
    else:
        # 누락 필드 보정
        cat.setdefault("level", 1)
        cat.setdefault("streak", 0)
        cat.setdefault("cleared_sets", 0)
        cat.setdefault("total_sets", 0)
    progress["categories"][category] = cat
    return cat


def update_p7_level(category: str, cleared: bool):
    """
    한 세트가 끝났을 때 레벨/연승 정보를 업데이트.
    - cleared=True: 연승 +1, 5연승이면 레벨업(Lv5까지), streak 0으로 리셋
    - cleared=False: streak 0으로 리셋
    """
    progress = load_level_progress()
    cat = _ensure_category(progress, category)

    prev_level = cat["level"]

    cat["total_sets"] += 1
    if cleared:
        cat["cleared_sets"] += 1
        cat["streak"] += 1
        if cat["streak"] >= 5 and cat["level"] < 5:
            cat["level"] += 1
            cat["streak"] = 0
    else:
        cat["streak"] = 0

    progress["categories"][category] = cat
    progress["last_updated"] = time.strftime("%Y-%m-%d %H:%M", time.localtime())
    save_level_progress(progress)

    leveled_up = cat["level"] > prev_level
    return cat, leveled_up, prev_level


def get_p7_level_info(category: str) -> Dict:
    """
    특정 카테고리의 현재 레벨 정보 반환.
    없으면 기본값(Lv1, streak 0)으로 초기화한 뒤 반환.
    """
    progress = load_level_progress()
    cat = _ensure_category(progress, category)
    save_level_progress(progress)
    return cat


def get_all_p7_levels() -> Dict[str, Dict]:
    """전체 카테고리의 레벨 정보를 반환."""
    progress = load_level_progress()
    return progress.get("categories", {})

# ---------- 데이터 구조 정의 ----------

@dataclass
class StepData:
    sentences: List[str]
    question_en: str
    options_en: List[str]
    answer_index: int
    question_ko: str = ""
    options_ko: List[str] = field(default_factory=list)


@dataclass
class P7Set:
    set_id: str
    title: str
    category: str
    step1: StepData
    step2: StepData
    step3: StepData
    all_sentences_en: List[str]
    all_sentences_ko: List[str]


@dataclass
class P7Result:
    step: int
    is_correct: bool
    user_choice: int
    correct_choice: int


@dataclass
class TimebombState:
    total_limit: int = 150
    start_time: float = 0.0
    remaining: int = 150
    is_over: bool = False


@dataclass
class ComboState:
    current_combo: int = 0
    max_combo: int = 0
    timebomb_gauge: int = 0

# ---------- 데모용 P7 세트 ----------

P7_DEMO_SET = P7Set(
    set_id="DEMO_01",
    title="[공지] 고객지원팀 사무실 이전 안내",
    category="공지 / 안내",
    step1=StepData(
        sentences=[
            "Dear staff,",
            "This is to inform you that our customer support team will be relocated next month.",
        ],
        question_en="What is the main purpose of this message?",
        options_en=[
            "To ask employees to work overtime this weekend",
            "To notify staff about a team relocation",
            "To announce a new product for customers",
            "To invite staff to a training workshop",
        ],
        answer_index=1,
        question_ko="이 메시지의 주요 목적은 무엇입니까?",
        options_ko=[
            "직원들에게 이번 주말 야근을 요청하기",
            "팀 이전에 대해 직원들에게 알리기",
            "고객에게 신규 제품을 발표하기",
            "직원들을 연수 워크숍에 초대하기",
        ],
    ),
    step2=StepData(
        sentences=[
            "Dear staff,",
            "This is to inform you that our customer support team will be relocated next month.",
            "Starting from May 3, the team will move from the 5th floor to the 9th floor of the same building.",
            "The new office will have a larger meeting room and upgraded computer equipment.",
            "Please make sure to pack all personal belongings by April 28.",
        ],
        question_en="According to the notice, what will NOT change after the relocation?",
        options_en=[
            "The building where the team works",
            "The floor where the team works",
            "The size of the meeting room",
            "The quality of the computer equipment",
        ],
        answer_index=0,
        question_ko="안내문에 따르면, 이전 후에도 변하지 않는 것은 무엇입니까?",
        options_ko=[
            "팀이 근무하는 건물",
            "팀이 근무하는 층",
            "회의실의 크기",
            "컴퓨터 장비의 품질",
        ],
    ),
    step3=StepData(
        sentences=[
            "Dear staff,",
            "This is to inform you that our customer support team will be relocated next month.",
            "Starting from May 3, the team will move from the 5th floor to the 9th floor of the same building.",
            "The new office will have a larger meeting room and upgraded computer equipment.",
            "Please make sure to pack all personal belongings by April 28.",
            "IT staff will assist you with moving your desktop computers on April 30.",
            "If you need temporary storage boxes, please contact Ms. Rivera in the HR department.",
            "We appreciate your cooperation during this transition period.",
        ],
        question_en="What can be inferred about the relocation?",
        options_en=[
            "The move will be completed in one day without any preparation.",
            "Employees are expected to handle all technical tasks by themselves.",
            "Some preparation and support are planned before and during the move.",
            "The team will move to a different company building in another city.",
        ],
        answer_index=2,
        question_ko="사무실 이전에 대해 알 수 있는 사실은 무엇입니까?",
        options_ko=[
            "사전 준비 없이 하루 만에 이전이 끝난다.",
            "직원들이 모든 기술적인 일을 스스로 처리해야 한다.",
            "이전 전과 진행 중에 어느 정도 준비와 지원이 계획되어 있다.",
            "팀이 다른 도시의 다른 회사 건물로 옮겨 간다.",
        ],
    ),
    all_sentences_en=[
        "Dear staff,",
        "This is to inform you that our customer support team will be relocated next month.",
        "Starting from May 3, the team will move from the 5th floor to the 9th floor of the same building.",
        "The new office will have a larger meeting room and upgraded computer equipment.",
        "Please make sure to pack all personal belongings by April 28.",
        "IT staff will assist you with moving your desktop computers on April 30.",
        "If you need temporary storage boxes, please contact Ms. Rivera in the HR department.",
        "We appreciate your cooperation during this transition period.",
    ],
    all_sentences_ko=[
        "전 직원 여러분께,",
        "다음 달에 고객지원팀 사무실이 이전될 예정임을 알려드립니다.",
        "5월 3일부터 해당 팀은 같은 건물 5층에서 9층으로 이동합니다.",
        "새 사무실에는 더 큰 회의실과 업그레이드된 컴퓨터 장비가 마련될 예정입니다.",
        "개인 소지품은 4월 28일까지 모두 정리해 주시기 바랍니다.",
        "IT팀은 4월 30일에 데스크톱 컴퓨터 이동을 도울 예정입니다.",
        "임시 보관 박스가 필요하신 분은 인사부 리베라 씨에게 문의해 주세요.",
        "이전 기간 동안 협조해 주셔서 감사드립니다.",
    ],
)

# ---------- Armory용 P5 / 단어 구조 ----------

@dataclass
class P5Problem:
    problem_id: str
    question: str
    options: List[str]
    answer_index: int


@dataclass
class ArmoryVocabItem:
    word: str
    meaning: str
    source: str = "P7"


P5_SAMPLE_PROBLEMS: List[P5Problem] = [
    P5Problem(
        problem_id="P5_001",
        question="The manager _______ the report before the meeting.",
        options=["review", "reviewed", "reviewing", "to review"],
        answer_index=1,
    ),
    P5Problem(
        problem_id="P5_002",
        question="The new policy will be effective _______ July 1.",
        options=["in", "at", "on", "for"],
        answer_index=2,
    ),
    P5Problem(
        problem_id="P5_003",
        question="Employees must _______ their ID cards at all times.",
        options=["carry", "carried", "carries", "carrying"],
        answer_index=0,
    ),
]

SAMPLE_VOCAB_ITEMS: List[ArmoryVocabItem] = [
    ArmoryVocabItem(word="relocate", meaning="이전하다, 옮기다", source="P7-DEMO"),
    ArmoryVocabItem(word="transition", meaning="전환, 변화", source="P7-DEMO"),
    ArmoryVocabItem(word="assist", meaning="돕다, 지원하다", source="P7-DEMO"),
    ArmoryVocabItem(word="temporary", meaning="일시적인", source="P7-DEMO"),
    ArmoryVocabItem(word="effective", meaning="시행되는, 유효한", source="DEV"),
    ArmoryVocabItem(word="upgrade", meaning="업그레이드하다, 개선하다", source="DEV"),
    ArmoryVocabItem(word="department", meaning="부서, 부문", source="DEV"),
]

# ============================================
# 세션 상태 초기화
# ============================================

def init_session_state():
    if "p7_selected_category" not in st.session_state:
        st.session_state.p7_selected_category = "공지 / 안내"
    if "p7_selected_set_id" not in st.session_state:
        st.session_state.p7_selected_set_id = P7_DEMO_SET.set_id
    if "p7_current_step" not in st.session_state:
        st.session_state.p7_current_step = 1
    if "p7_results" not in st.session_state:
        st.session_state.p7_results: List[P7Result] = []
    if "p7_has_started" not in st.session_state:
        st.session_state.p7_has_started = False
    if "p7_has_finished" not in st.session_state:
        st.session_state.p7_has_finished = False

    if "p7_timebomb" not in st.session_state:
        st.session_state.p7_timebomb = TimebombState()
    if "p7_combo" not in st.session_state:
        st.session_state.p7_combo = ComboState()

    if "p7_stats_updated" not in st.session_state:
        st.session_state.p7_stats_updated = False

    if "p7_vocab_candidates" not in st.session_state:
        st.session_state.p7_vocab_candidates: List[Dict] = []

    if "p7_vocab_saved_this_set" not in st.session_state:
        st.session_state.p7_vocab_saved_this_set = False

    if "secret_armory_p5" not in st.session_state:
        st.session_state.secret_armory_p5: List[P5Problem] = []
    if "secret_armory_vocab" not in st.session_state:
        st.session_state.secret_armory_vocab: List[Dict] = []

    if "armory_section" not in st.session_state:
        st.session_state.armory_section = "hub"

    if "vocab_quiz_index" not in st.session_state:
        st.session_state.vocab_quiz_index = 0
    if "vocab_quiz_order" not in st.session_state:
        st.session_state.vocab_quiz_order: List[int] = []

    if "vocab_armory_mode" not in st.session_state:
        st.session_state.vocab_armory_mode = "study"
    if "vocab_current_set" not in st.session_state:
        st.session_state.vocab_current_set: List[Dict] = []

    # ✅ 플립 카드 학습 모드용 상태
    if "vocab_study_index" not in st.session_state:
        st.session_state.vocab_study_index = 0
    if "vocab_study_show_kor" not in st.session_state:
        st.session_state.vocab_study_show_kor = False

    if "vocab_lives" not in st.session_state:
        st.session_state.vocab_lives = 3
    if "vocab_score" not in st.session_state:
        st.session_state.vocab_score = 0
    if "vocab_stats_updated" not in st.session_state:
        st.session_state.vocab_stats_updated = False

    if "p5_quiz_index" not in st.session_state:
        st.session_state.p5_quiz_index = 0
    if "p5_quiz_order" not in st.session_state:
        st.session_state.p5_quiz_order: List[int] = []
    if "p5_quiz_started" not in st.session_state:
        st.session_state.p5_quiz_started = False

    # 현재 카테고리 레벨
    if "p7_level" not in st.session_state:
        st.session_state.p7_level = 1

    # ✅ P7 세트 전체 제한시간(초) - 전장 입장 전 선택
    if "p7_time_limit_choice" not in st.session_state:
        st.session_state.p7_time_limit_choice = 150

# ============================================
# Timebomb / 콤보 관련
# ============================================

def start_timebomb():
    tb = st.session_state.p7_timebomb
    # ✅ 전장 입장 전 선택한 시간(세트 전체 제한시간)을 반영
    tb.total_limit = int(st.session_state.get("p7_time_limit_choice", 150))
    tb.start_time = time.time()
    tb.remaining = tb.total_limit
    tb.is_over = False
    st.session_state.p7_timebomb = tb


def update_timebomb():
    tb: TimebombState = st.session_state.p7_timebomb
    if tb.is_over or tb.start_time == 0:
        return
    elapsed = int(time.time() - tb.start_time)
    remaining = tb.total_limit - elapsed
    if remaining <= 0:
        tb.remaining = 0
        tb.is_over = True
    else:
        tb.remaining = remaining
    st.session_state.p7_timebomb = tb


def get_time_display(sec: int) -> str:
    if sec < 0:
        sec = 0
    m, s = divmod(sec, 60)
    return f"{m:02d}:{s:02d}"


def add_combo(is_correct: bool):
    combo: ComboState = st.session_state.p7_combo
    if is_correct:
        combo.current_combo += 1
        if combo.current_combo > combo.max_combo:
            combo.max_combo = combo.current_combo
        combo.timebomb_gauge = min(100, combo.timebomb_gauge + 15)
    else:
        combo.current_combo = 0
        combo.timebomb_gauge = max(0, combo.timebomb_gauge - 20)
    st.session_state.p7_combo = combo


def render_timebomb_and_combo(compact: bool = False):
    update_timebomb()
    tb: TimebombState = st.session_state.p7_timebomb
    combo: ComboState = st.session_state.p7_combo

    # ✅ 타이머 현장감: 전투 중에는 자동 리프레시로 초 단위 카운트다운이 보이게
    if st.session_state.get("p7_has_started", False) and not st.session_state.get("p7_has_finished", False) and not tb.is_over:
        try:
            from streamlit_autorefresh import st_autorefresh
            st_autorefresh(interval=1000, key="p7_timebomb_tick")
        except ModuleNotFoundError:
            pass

    # ✅ COMPACT 모드: 위쪽 자리 차지 최소화
    if compact:
        # 타이머/콤보 영역의 위아래 여백을 줄이는 CSS
        st.markdown(
        """
        <style>
          .p7-hud-sticky{
            position: sticky;
            top: 0.75rem;
          }

          /* =========================
             P7 Reading Arena - UI v2.2.5 (A안-전투구역 분리)
             - 로직 0 변경 / CSS+마크업만
             ========================= */

          /* Compact topbar */
          .p7-topbar{
            display:flex;
            align-items:baseline;
            justify-content:space-between;
            gap:12px;
            margin: 0.15rem 0 0.35rem 0;
          }
          .p7-topbar .ttl{
            font-size: 20px;
            font-weight: 900;
            letter-spacing: -0.2px;
          }
          .p7-topbar .meta{
            font-size: 12px;
            font-weight: 700;
            color: #6b7280;
            white-space: nowrap;
          }
          .p7-divider{
            height:1px;
            background: rgba(17,24,39,0.10);
            margin: 0.35rem 0 0.6rem 0;
          }

          /* --- Zone cards (Intel / Mission) --- */
          .p7-zone{
            position: relative;
            border-radius: 16px;
            padding: 14px 16px;
            border: 1px solid rgba(17,24,39,0.10);
            background: #ffffff;
            box-shadow: 0 8px 22px rgba(15,23,42,0.06);
            margin: 10px 0;
            overflow: hidden;
          }
          .p7-zone:before{
            content:"";
            position:absolute;
            left:0; top:0; bottom:0;
            width: 6px;
            border-radius: 16px 0 0 16px;
            background: rgba(59,130,246,0.75);
          }
          .p7-zone .p7-zone-title{
            display:flex;
            align-items:center;
            gap:10px;
            font-size: 12px;
            font-weight: 900;
            letter-spacing: 0.6px;
            text-transform: uppercase;
            color: rgba(17,24,39,0.70);
            margin-bottom: 8px;
          }
          .p7-zone .p7-zone-body{
            font-size: 18px;
            font-weight: 700;
            color: #111827;
            line-height: 1.55;
          }
          /* Make the passage (intel zone) the main hero text */
          .p7-zone.intel .p7-zone-body{
            font-size: clamp(22px, 2.2vw, 34px);
            font-weight: 900;
            letter-spacing: 0.1px;
          }
          /* Question slightly smaller than passage */
          .p7-zone.mission .p7-zone-body{
            font-size: clamp(16px, 1.5vw, 22px);
            font-weight: 800;
          }
          .p7-zone.intel{
            background: linear-gradient(180deg, rgba(37,99,235,0.10), rgba(37,99,235,0.03));
            border-color: rgba(37,99,235,0.20);
          }
          .p7-zone.intel:before{ background: rgba(37,99,235,0.85); }
          .p7-zone.mission{
            background: linear-gradient(180deg, rgba(147,51,234,0.10), rgba(147,51,234,0.03));
            border-color: rgba(147,51,234,0.18);
            box-shadow: 0 10px 26px rgba(147,51,234,0.08);
          }
          .p7-zone.mission:before{ background: rgba(147,51,234,0.85); }

          /* --- Combat options label --- */
          .p7-combat-caption{
            display:flex;
            align-items:center;
            gap:10px;
            margin: 12px 0 8px 0;
            font-size: 12px;
            font-weight: 900;
            letter-spacing: 0.5px;
            color: rgba(17,24,39,0.75);
            text-transform: uppercase;
          }

          /* --- Radio -> Card options (Streamlit/BaseWeb) --- */
          /* Choice text = 2/3 of passage size */
          div[role="radiogroup"] > label span{ font-size: inherit !important; font-weight: 700 !important; }
          div[role="radiogroup"]{ gap: 0 !important; }
          div[role="radiogroup"] > label{
            width: 100% !important;
            font-size: clamp(14px, 1.25vw, 18px) !important;
            border-radius: 14px !important;
            border: 1px solid rgba(17,24,39,0.12) !important;
            background: linear-gradient(180deg, rgba(2,6,23,0.02), rgba(2,6,23,0.00)) !important;
            padding: 10px 12px !important;
            margin: 3px 0 !important; /* ✅ 위아래 간격 최대한 압축 */
            box-shadow: 0 8px 18px rgba(15,23,42,0.05) !important;
            transition: transform .12s ease, box-shadow .12s ease, border-color .12s ease, background .12s ease;
          }
          div[role="radiogroup"] > label:hover{
            transform: translateY(-1px);
            box-shadow: 0 12px 28px rgba(15,23,42,0.08) !important;
          }
          /* 선택됨: 파란 강조 + '잠김' 느낌 */
          div[role="radiogroup"] > label:has(input:checked){
            border-color: rgba(59,130,246,0.65) !important;
            background: linear-gradient(180deg, rgba(59,130,246,0.12), rgba(59,130,246,0.05)) !important;
            box-shadow: 0 10px 26px rgba(37,99,235,0.10) !important;
          }

          /* 라디오 원(기본) 공간을 조금 줄이기 */
          div[role="radiogroup"] > label > div{
            margin-top: 0 !important;
            margin-bottom: 0 !important;
          }

          /* 상단의 불필요한 빈 라벨/여백 최소화 */
          .stRadio > label{ display:none !important; }
          .stRadio{ margin-top: 0.15rem !important; }

          /* HUD '병기고' 버튼(세로) */
          .p7-armory-vert button{
            padding: 8px 10px !important;
            border-radius: 12px !important;
            border: 1px solid rgba(17,24,39,0.14) !important;
            background: #ffffff !important;
            font-weight: 900 !important;
          }

        </style>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([3, 2] if not compact else [2.2, 1.3])

    with col1:
        if compact:
            st.caption("⏱ TIMEBOMB")
        else:
            st.markdown("### ⏱ 시간폭탄 타이머")

        # 🔥 긴장감 연출(60/30/10초 구간)
        if tb.remaining <= 10:
            tone = ("#ffebee", "#c62828", "💥 폭발 임박! 10초!")
        elif tb.remaining <= 30:
            tone = ("#fff3e0", "#ef6c00", "🔥 30초 이하!")
        elif tb.remaining <= 60:
            tone = ("#fffde7", "#9e9d24", "⚠️ 60초 이하!")
        else:
            tone = ("#e8f5e9", "#2e7d32", "🟢 안정권")

        pad = "10px 12px" if compact else "12px 14px"
        title_fs = "12px" if compact else "14px"
        time_fs = "18px" if compact else "22px"

        st.markdown(
            f"""
            <div class="p7-hud-compact" style="padding:{pad}; border-radius:12px; background:{tone[0]}; border:1px solid {tone[1]};">
              <div style="font-size:{title_fs}; font-weight:800; color:{tone[1]}; margin-bottom:2px;">{tone[2]}</div>
              <div style="font-size:{time_fs}; font-weight:900; color:#111827;">
                {get_time_display(tb.remaining)}
                <span style="font-size:12px; font-weight:700; color:#6b7280;"> / {get_time_display(tb.total_limit)}</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        ratio = tb.remaining / tb.total_limit if tb.total_limit > 0 else 0
        st.progress(max(0.0, min(1.0, ratio)))

    with col2:
        if compact:
            st.caption("💣 COMBO")
        else:
            st.markdown("### 💣 콤보 게이지")

        if compact:
            st.write(f"현재 **{combo.current_combo}**  ·  최고 **{combo.max_combo}**")
        else:
            st.write(f"현재 콤보: **{combo.current_combo}연속**  |  최고 콤보: **{combo.max_combo}연속**")

        st.progress(max(0.0, min(1.0, combo.timebomb_gauge / 100)))

# ============================================
# P7 지문/문제 렌더링
# ============================================

def format_sentences_to_paragraph(sentences: List[str]) -> str:
    return " ".join(sentences)


def get_current_p7_set() -> P7Set:
    return P7_DEMO_SET


def render_step_intro(step: int):
    if step == 1:
        st.caption("Step 1 [정찰 단계] · 2문장으로 누가 / 누구에게 / 왜 쓴 글인지 먼저 스캔하는 단계입니다.")
    elif step == 2:
        st.caption("Step 2 [분석 단계] · 5문장으로 회사·사람·제품·날짜·요청 등 구체 정보를 정리하는 단계입니다.")
    else:
        st.caption("Step 3 [최종 전투] · 8문장 전체를 바탕으로 관계·의도·암시·추론을 잡아내는 단계입니다.")


def render_p7_step(step: int):
    current_set = get_current_p7_set()
    steps_results = st.session_state.get('p7_results', [])
    if step == 1:
        data = current_set.step1
    elif step == 2:
        data = current_set.step2
    else:
        data = current_set.step3

    # --- 전투 구역 UI (지문/문제/선택지) ---
    st.markdown(
        f"""
        <div class="p7-zone intel">
          <div class="p7-zone-body">{(" ".join(data.sentences)).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="p7-zone mission">
          <div class="p7-zone-body">{(data.question_en).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


    key = f"p7_step{step}_answer"
    chosen = st.radio(
        "",
        options=list(range(len(data.options_en))),
        format_func=lambda i: data.options_en[i],
        key=key,
        label_visibility="collapsed",
    )
    return data, chosen


def evaluate_step(step: int, chosen_index: int, data: StepData):
    is_correct = (chosen_index == data.answer_index)
    add_combo(is_correct)

    result = P7Result(
        step=step,
        is_correct=is_correct,
        user_choice=chosen_index,
        correct_choice=data.answer_index,
    )

    results_list: List[P7Result] = st.session_state.p7_results
    replaced = False
    for i, r in enumerate(results_list):
        if r.step == step:
            results_list[i] = result
            replaced = True
            break
    if not replaced:
        results_list.append(result)
    st.session_state.p7_results = results_list

    # 단어 후보 모으기 (정오답 관계없이)
    step_vocab_candidates: List[Dict] = []
    if step == 1:
        step_vocab_candidates = [
            {"word": "relocate", "meaning": "이전하다, 옮기다", "source": "P7-Step1"},
            {"word": "inform", "meaning": "알리다, 통지하다", "source": "P7-Step1"},
        ]
    elif step == 2:
        step_vocab_candidates = [
            {"word": "effective", "meaning": "시행되는, 유효한", "source": "P7-Step2"},
            {"word": "upgrade", "meaning": "업그레이드하다, 개선하다", "source": "P7-Step2"},
        ]
    else:
        step_vocab_candidates = [
            {"word": "transition", "meaning": "전환, 변화", "source": "P7-Step3"},
            {"word": "assist", "meaning": "돕다, 지원하다", "source": "P7-Step3"},
            {"word": "temporary", "meaning": "일시적인", "source": "P7-Step3"},
        ]

    pool: List[Dict] = st.session_state.get("p7_vocab_candidates", [])
    for item in step_vocab_candidates:
        if not any(v["word"] == item["word"] for v in pool):
            pool.append(item)
    st.session_state.p7_vocab_candidates = pool


def _add_vocab_to_armory(word: str, meaning: str, source: str = "P7"):
    """
    ✅ P7 VOCA 저장(핵심):
    - 기존 동작(세션 내 단어무기고 리스트 유지)은 그대로
    - 추가로 app/data/armory/secret_armory.json 에 'p7_vocab' 포맷으로 영구 저장
      -> Secret Armory(별도 파일) VOCA 저장고가 바로 이 포맷만 안정적으로 인식
    """
    # 1) 기존: 세션 내 단어 무기고 유지(이 파일 내부 UX 유지)
    vocab_list: List[Dict] = st.session_state.secret_armory_vocab
    for v in vocab_list:
        if v.get("word") == word and v.get("meaning") == meaning:
            break
    else:
        vocab_list.append({"word": word, "meaning": meaning, "source": source})
        st.session_state.secret_armory_vocab = vocab_list

    # 2) ✅ 영구 저장: Secret Armory 공용 JSON에 p7_vocab 형태로 추가
    try:
        # 표준 저장 모듈이 있으면 그걸 우선 사용
        from app.core.armory_store import append_p7_vocab  # type: ignore
        append_p7_vocab(str(word), str(meaning), extra={"source": "P7"})
        return
    except Exception:
        pass

    # fallback: 직접 JSON에 추가 (모듈이 없거나 import 실패 시)
    try:
        from pathlib import Path
        import json

        armory_path = Path("app/data/armory/secret_armory.json")
        if armory_path.exists():
            raw = json.loads(armory_path.read_text(encoding="utf-8-sig"))
        else:
            raw = []

        items = raw if isinstance(raw, list) else raw.get("items", [])
        if not isinstance(items, list):
            items = []

        word_s = (str(word) if word is not None else "").strip()
        meaning_s = (str(meaning) if meaning is not None else "").strip()
        if not word_s or not meaning_s:
            return

        # 중복 방지
        for it in items:
            if (
                isinstance(it, dict)
                and it.get("mode") == "p7_vocab"
                and it.get("word") == word_s
                and it.get("meaning") == meaning_s
            ):
                return

        items.append({
            "source": "P7",
            "mode": "p7_vocab",
            "word": word_s,
            "meaning": meaning_s,
        })

        armory_path.parent.mkdir(parents=True, exist_ok=True)
        armory_path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")

    except Exception:
        # 저장 실패해도 전투 진행은 막지 않음(UX 보호)
        return


def _add_p5_to_armory(problem: P5Problem):
    p5_list: List[P5Problem] = st.session_state.secret_armory_p5
    for p in p5_list:
        if p.problem_id == problem.problem_id:
            return
    p5_list.append(problem)
    st.session_state.secret_armory_p5 = p5_list

# ============================================
# P7 결과 / 해설 / 단어 저장 + 레벨업
# ============================================

def render_p7_feedback():
    # === RESULT / FEEDBACK SCREEN (neon skin: purple + cyan) ===
    st.markdown(
        """
        <style>
        /* tighten vertical gaps on the debrief screen */
        .block-container { padding-top: 1.0rem; padding-bottom: 2.0rem; }
        h1, h2, h3 { margin-top: 0.2rem !important; margin-bottom: 0.5rem !important; }

        /* Neon card vibe (purple + cyan) */
        .p7-neon-banner {
            border: 1px solid rgba(140, 120, 255, 0.35);
            background: linear-gradient(90deg, rgba(120, 90, 255, 0.10), rgba(0, 255, 255, 0.07));
            border-radius: 14px;
            padding: 10px 14px;
            box-shadow:
                0 0 0 1px rgba(0, 255, 255, 0.10) inset,
                0 0 18px rgba(120, 90, 255, 0.10),
                0 0 18px rgba(0, 255, 255, 0.08);
        }

        /* Metrics: smaller + boxed */
        div[data-testid="stMetric"] {
            border: 1px solid rgba(0, 255, 255, 0.18);
            border-radius: 14px;
            padding: 10px 12px;
            background: rgba(10, 15, 25, 0.02);
            box-shadow: 0 0 14px rgba(0, 255, 255, 0.06);
        }
        div[data-testid="stMetricValue"] { font-size: 2.0rem !important; }
        div[data-testid="stMetricLabel"] { font-size: 0.95rem !important; opacity: 0.9; }

        /* Expanders: neon outline */
        div[data-testid="stExpander"] {
            border: 1px solid rgba(120, 90, 255, 0.32) !important;
            border-radius: 16px !important;
            box-shadow: 0 0 16px rgba(120, 90, 255, 0.12), 0 0 12px rgba(0, 255, 255, 0.08);
        }
        div[data-testid="stExpander"] > details {
            border-radius: 16px !important;
        }

        /* Reduce extra whitespace around dividers */
        hr { margin: 0.8rem 0 !important; opacity: 0.25; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("## 📊 전투 결과 브리핑 · 해설 & 단어 저장")

    tb: TimebombState = st.session_state.p7_timebomb
    results: List[P7Result] = st.session_state.p7_results
    # --- HOTFIX: support both dict-style and object-style result items (P7Result) ---
    def _rg(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    correct_count = sum(1 for r in results if r.is_correct)
    wrong_count = len(results) - correct_count
    total_questions = len(results)
    step_reached = total_questions
    time_used = tb.total_limit - tb.remaining if tb.total_limit > 0 else 0
    if time_used < 0:
        time_used = 0
    cleared = (
        total_questions == 3
        and correct_count == total_questions
        and step_reached == 3
        and not tb.is_over
    )

    if not st.session_state.get("p7_stats_updated", False):
        if record_p7_result is not None:
            try:
                record_p7_result(
                    category=st.session_state.get("p7_selected_category", "P7"),
                    level=st.session_state.get("p7_level", 1),
                    correct_count=correct_count,
                    total_questions=total_questions,
                    time_used=time_used,
                    step_reached=step_reached,
                    cleared=cleared,
                )
            except Exception as e:
                st.warning(f"기록 저장 중 오류가 발생했습니다 (record_p7_result): {e}")

        # ✅ 레벨 시스템 업데이트
        try:
            cat_name = st.session_state.get("p7_selected_category", "P7")
            cat_info, leveled_up, prev_level = update_p7_level(cat_name, cleared)
            st.session_state.p7_level = cat_info["level"]
            if leveled_up:
                st.success(
                    f"🎉 랭크 업! [{cat_name}] 카테고리에서 Lv{prev_level} → Lv{cat_info['level']} 로 상승했습니다."
                )
            else:
                st.info(
                    f"[{cat_name}] 현재 레벨: Lv{cat_info['level']} · "
                    f"연속 클리어: {cat_info['streak']}/5"
                )
        except Exception as e:
            st.warning(f"레벨 기록을 업데이트하는 중 오류가 발생했습니다: {e}")

        st.session_state.p7_stats_updated = True

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("정답 개수", f"{correct_count} / 3")
    with col2:
        st.metric("오답 개수", f"{wrong_count}")
    with col3:
        st.metric("남은 시간", get_time_display(tb.remaining))

    # --- (A) 요약 브리핑: 기본 화면의 주인공 ---
    can_open = (correct_count == 3) and (not tb.is_over)

    if not can_open:
        st.markdown("---")
        st.markdown(
            f"""
            <div style="padding:18px;border-radius:16px;border:2px solid #ff4d4f;background:rgba(255,77,79,0.06);">
              <div style="font-size:26px;font-weight:800;letter-spacing:0.5px;">💀 YOU LOST!</div>
              <div style="margin-top:6px;font-size:15px;">
                이번 세트는 <b>올클리어</b> 실패. (정답 {correct_count}/3 · 오답 {wrong_count})
              </div>
              <div style="margin-top:4px;font-size:13px;opacity:0.85;">
                해석/정답/단어 보상은 <b>3/3 올클리어</b>일 때만 해금됩니다.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns(2, gap="small")
        with c1:
            if st.button("🔥 다시 도전!", use_container_width=True, key="p7_lost_retry"):
                _reset_p7_battle(keep_time_choice=True)
                st.session_state["p7_started"] = False
                st.session_state["p7_phase"] = "setup"
                st.session_state["p7_show_feedback"] = False
                st.rerun()

        with c2:
            if st.button("🏠 메인 허브로", use_container_width=True, key="p7_lost_to_hub"):
                _safe_switch_page(
                    ["main_hub.py", "./main_hub.py", "pages/00_Main_Hub.py", "pages\\00_Main_Hub.py"],
                    fallback_hint="메인 허브",
                )
        return
    st.markdown("### 🧾 요약 브리핑 (Step 1~3)")
    # ✅ HOTFIX: steps_results가 로컬 스코프에 없어서 NameError가 발생했음
    # p7_results는 각 Step 결과(정답/오답/선택/정답 등)를 누적 저장하는 세션 키
    steps_results = st.session_state.get('p7_results', []) or []

    def _choice_letter(idx: int) -> str:
        letters = ["A", "B", "C", "D"]
        return letters[idx] if isinstance(idx, int) and 0 <= idx < 4 else "-"

    # step별 결과 조회
    r_by_step = {r.step: r for r in results}

    c1, c2, c3 = st.columns(3)
    for _col, _step in [(c1, 1), (c2, 2), (c3, 3)]:
        with _col:
            r = r_by_step.get(_step)
            if r is None:
                st.markdown(f"**Step {_step}**")
                st.caption("미진입")
                st.write("—")
            else:
                badge = "✅ CLEAR" if r.is_correct else "❌ MISS"
                st.markdown(f"**Step {_step} · {badge}**")
                st.write(f"내 선택: **{_choice_letter(r.user_choice)}**  |  정답: **{_choice_letter(r.correct_choice)}**")
                if r.is_correct:
                    st.caption("다음 훈련: 템포 유지 + 근거문장 1회 재확인")
                else:
                    st.caption("왜 틀렸나: 근거문장/키워드 매칭 미스 → ‘근거 1문장’ 먼저 잡기")

    st.success("✅ 축하합니다! 이번 세트는 해석/정답/어휘 화면이 열립니다.")

    # ✅ 결과 브리핑 하단 이동 버튼(항상 노출) — Expander 밖
    st.markdown("---")
    b1, b2 = st.columns(2, gap="small")
    with b1:
        if st.button("🧰 비밀 무기고로 이동", use_container_width=True, key="p7_result_to_armory"):
            _safe_switch_page(["pages/03_Secret_Armory.py"], fallback_hint="비밀 무기고")
    with b2:
        if st.button("🔥 P7 게임 한 판 더! (리매치)", use_container_width=True, key="p7_result_rematch"):
            _reset_p7_battle(keep_timer=False)
            st.session_state["p7_started"] = False
            st.session_state["p7_phase"] = "setup"
            st.session_state["p7_show_feedback"] = False
            st.session_state.pop("p7_feedback_open", None)
            st.rerun()


    current_set = get_current_p7_set()

        # ✅ 전투 로그(해석/정답/단어) — 결과 브리핑에서만 열람 가능
    st.markdown("### 🧾 전투 기록 열람 (클릭해서 보기)")
    # ✅ 열람 패널은 '항상 닫힘'으로 시작해야 함.
    # Streamlit expander는 key를 받지 않으므로,
    # 새 전투(세트)마다 nonce를 올려 토글 상태를 안전하게 초기화합니다.
    panel_nonce = int(st.session_state.get("p7_panel_nonce", 0))
    st.session_state["p7_panel_nonce"] = int(st.session_state.get("p7_panel_nonce", 0)) + 1
    _p7_panel_label = "🔓 열람 패널 열기" + ("\u200b" * st.session_state["p7_panel_nonce"])
    with st.expander(_p7_panel_label, expanded=False):
        tab_labels = [
            "🛰️ 지문 해독 로그",
            "🎯 문제 작전 해설",
            "🧩 선택지 함정 분석",
            "🧨 핵심 단어 무기고",
        ]

        _panel_choice_key = f"p7_panel_choice_{st.session_state.get('p7_selected_set_id','P7')}_{panel_nonce}"
        if _panel_choice_key not in st.session_state:
            st.session_state[_panel_choice_key] = None

        st.caption("📚 열람 카테고리 선택 (버튼을 눌러야 내용이 펼쳐집니다)")
        cols = st.columns(4)
        for _idx, _lbl in enumerate(tab_labels):
            with cols[_idx]:
                if st.button(_lbl, use_container_width=True, key=f"{_panel_choice_key}_{_idx}"):
                    st.session_state[_panel_choice_key] = _lbl

        panel_choice = st.session_state[_panel_choice_key]
        if panel_choice is None:
            st.info("4개 카테고리 중 하나를 눌러 열람을 시작하세요.")
        else:
            # 선택 해제(초기화) 버튼
            if st.button("🧹 카테고리 닫기(초기화)", key=f"{_panel_choice_key}_clear"):
                st.session_state[_panel_choice_key] = None
                st.rerun()

            # 아래부터 선택된 카테고리 내용만 표시
        if panel_choice == tab_labels[0]:
            st.caption("문장을 클릭하면(펼치기) 한글 해석이 보입니다.")
            # NOTE: P7Set 필드명 호환 (sentences/translations vs all_sentences_en/all_sentences_ko)
            en_list = getattr(current_set, "sentences", None)
            if not isinstance(en_list, list):
                en_list = getattr(current_set, "all_sentences_en", [])
            ko_list = getattr(current_set, "translations", None)
            if not isinstance(ko_list, list):
                ko_list = getattr(current_set, "all_sentences_ko", [])

            for i, s in enumerate(en_list):
                ko = ko_list[i] if i < len(ko_list) else ""
                with st.expander(f"{i+1}. {s}", expanded=False):
                    st.write(ko if ko else "(해석 데이터 없음)")

                    # 2) 문제 해설

        elif panel_choice == tab_labels[1]:
            for step_idx in range(3):
                if step_idx < len(steps_results):
                    r = steps_results[step_idx]
                    st.markdown(f"#### Step {step_idx+1} — {'✅ CLEAR' if _rg(r, 'is_correct') else '❌ MISS'}")
                    if _rg(r, 'question'):
                        st.write(f"Q. {r['question']}")
                    if _rg(r, 'explanation'):
                        st.info(r['explanation'])
                    else:
                        st.caption("(해설 데이터 없음)")
                    st.markdown("---")

                    # 3) 선택지 분석

        elif panel_choice == tab_labels[2]:
            for step_idx in range(3):
                if step_idx < len(steps_results):
                    r = steps_results[step_idx]
                    st.markdown(f"#### Step {step_idx+1} — 선택지 분석")
                    choices = _rg(r, 'choices', [])
                    correct = _rg(r, 'correct_choice')
                    picked = _rg(r, 'selected_choice')
                    if choices:
                        for ci, ctext in enumerate(choices):
                            label = chr(ord('A') + ci)
                            tag = ""
                            if correct == label:
                                tag = "✅ 정답"
                            elif picked == label:
                                tag = "❌ 선택"
                            st.write(f"- **{label})** {ctext} {tag}")
                    if _rg(r, 'choice_explanations'):
                        st.caption("선택지 해설")
                        for k, v in r['choice_explanations'].items():
                            st.write(f"- **{k})** {v}")
                    else:
                        st.caption("(선택지 해설 데이터 없음)")
                    st.markdown("---")

                    # 4) 핵심 단어 무기고

        elif panel_choice == tab_labels[3]:
            st.caption("지문에서 헷갈렸던 단어를 무기고에 저장해두고, 나중에 VOCA 모드에서 복습하세요.")
            vocab = current_set.vocab_to_save if hasattr(current_set, 'vocab_to_save') else []
            if not vocab:
                st.info("이번 지문에는 저장 가능한 단어가 아직 없습니다.")
            else:
                st.markdown("##### 📌 저장 후보 단어")
                cols = st.columns([1,1])
                with cols[0]:
                    selected = st.multiselect("저장할 단어 선택", vocab, key="p7_vocab_pick")
                with cols[1]:
                    st.write("")
                    if st.button("💾 선택 단어 무기고에 저장", use_container_width=True, key="p7_vocab_save_btn"):
                        saved = save_vocab_to_armory(selected, source="P7")
                        st.success(f"저장 완료: {len(saved)}개")
                        st.session_state.pop("p7_vocab_pick", None)
                        st.rerun()

            # ============================================
            # P7 Reading Arena 메인 페이지 (시간카드 선택 → 전투 → 피드백)
            # ============================================

def _reset_p7_battle(keep_time_choice: bool = True):
    """P7 전투 상태를 안전하게 초기화합니다. (기록 파일/무기고는 유지)"""
    time_choice = st.session_state.get("p7_time_limit_choice", 150) if keep_time_choice else 150
    st.session_state["p7_panel_nonce"] = int(st.session_state.get("p7_panel_nonce", 0)) + 1


    st.session_state.p7_current_step = 1
    st.session_state.p7_results = []
    st.session_state.p7_has_started = False
    st.session_state.p7_has_finished = False
    st.session_state.p7_stats_updated = False
    st.session_state.p7_vocab_candidates = []
    st.session_state.p7_vocab_saved_this_set = False

    # 콤보/타임봄 리셋
    st.session_state.p7_combo = ComboState()
    st.session_state.p7_timebomb = TimebombState(total_limit=int(time_choice), remaining=int(time_choice))

    # 체크박스 키(단어 저장 선택) 정리
    for k in list(st.session_state.keys()):
        if isinstance(k, str) and k.startswith("p7_save_"):
            del st.session_state[k]



def reading_arena_page():
    """Render the P7 Reading Arena (battle only).
    Layout: 80% battlefield (passage/question/choices) + 20% HUD (step/timer/combo).
    """
    inject_css()
    st.markdown("<!-- p7_hud_title -->", unsafe_allow_html=True)

    # ---- ensure state ----
    init_session_state()

    if not st.session_state.get("p7_has_started", False):
        # Auto-start: no lobby in this module.
        st.session_state["p7_has_started"] = True
        st.session_state.setdefault("p7_current_step", 1)
        st.session_state.setdefault("p7_max_step_reached", 1)
        start_timebomb()

    update_timebomb()

    # ---- top header (minimal) ----
    top_main, top_right = st.columns([8, 4], vertical_alignment="center")

    with top_main:
        # (전장 집중) 왼쪽은 지문/문제만 두기 위해 타이틀은 HUD(오른쪽)로 이동
        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)

    with top_right:
        st.markdown("<div class='p7_hud_title'>🔥 P7 Reading Arena</div><!-- p7_hud_title -->", unsafe_allow_html=True)
        # ✅ 메인허브 버튼을 오른쪽으로 이동 (본문 공간 확보)
        if st.button("🏠 메인허브", use_container_width=True, key="p7_go_mainhub"):
            _safe_switch_page(
                candidates=[
                    "main_hub.py",
                    "pages/00_Main_Hub.py",
                    "pages/00_main_hub.py",
                    "pages/00_Home.py",
                ],
                fallback_hint="main_hub.py 또는 pages/00_* 경로를 확인하세요."
            )
            return

        rank = int(st.session_state.get("p7_rank", 1))
        streak = int(st.session_state.get("p7_streak", 0))
        nxt = "다음 레벨" if rank < 5 else "MAX"
        st.markdown(
            f"<div style='text-align:right; opacity:.85; font-weight:700; margin-top:6px;'>랭크 Lv{rank} · {streak}연승 → {nxt}</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")

    # ---- layout: 80/20 ----
    main_col, hud_col = st.columns([6, 1], gap="medium")

    current_step = int(st.session_state.get("p7_current_step", 1))
    max_reached = int(st.session_state.get("p7_max_step_reached", current_step))

    with hud_col:
        # STEP panel (HUD only)
        st.markdown(
            """<div class='p7_step_panel'>
                <div class='p7_step_title'>STEP</div>
            </div>""",
            unsafe_allow_html=True,
        )
        step_btns = st.columns(3, gap="small")
        for i, col in enumerate(step_btns, start=1):
            with col:
                disabled = i > max_reached
                label = str(i)
                if i == current_step:
                    label = f"✅ {i}"
                if st.button(label, use_container_width=True, key=f"p7_step_btn_{i}", disabled=disabled):
                    st.session_state["p7_current_step"] = i
                    st.rerun()

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        # TIMEBOMB + COMBO
        render_timebomb_and_combo()

        st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)

        # Quick actions
        if st.button("🏳️ 전투 포기", use_container_width=True, key=f"p7_abort_{current_step}"):
            st.session_state["p7_has_finished"] = True
            st.rerun()

        if st.button("🔁 세트 재시작", use_container_width=True, key="p7_restart_set"):
            _reset_p7_battle(keep_time_choice=True)
            st.session_state["p7_has_started"] = True
            st.session_state["p7_current_step"] = 1
            st.session_state["p7_max_step_reached"] = 1
            start_timebomb()
            st.rerun()

        if st.button("🧰 병기고", use_container_width=True, key="p7_open_armory"):
            _safe_switch_page(
                candidates=[
                    "app/arenas/secret_armory.py",
                    "pages/03_Secret_Armory.py",
                    "pages/03_Secret_Armory_Arena.py",
                    "pages/03_Armory.py",
                ],
                fallback_hint="secret_armory.py / pages/03_* 경로를 확인하세요."
            )
            return

    with main_col:
        # Battlefield: passage + question + choices
        render_p7_step(current_step)


def init_armory_state():
    if not st.session_state.secret_armory_p5:
        for p in P5_SAMPLE_PROBLEMS:
            _add_p5_to_armory(p)
    if not st.session_state.secret_armory_vocab:
        for item in SAMPLE_VOCAB_ITEMS:
            _add_vocab_to_armory(item.word, item.meaning, item.source)


def render_armory_hub():
    st.markdown("## 📕 Secret Armory – 비밀 병기고 허브")
    st.write("P5에서 저장된 문제들과 P7에서 SAVE한 단어들이 모여 있는 개인 무기고입니다.")
    st.write("여기서 다시 학습하거나, 미니 전투(퀴즈)를 통해 불필요한 무기들을 정리할 수 있습니다.")

    col_p5, col_vocab = st.columns(2)

    with col_p5:
        st.markdown("### 💣 P5 문제 무기고")
        p5_list: List[P5Problem] = st.session_state.secret_armory_p5
        st.write(f"현재 쌓인 P5 문제: **{len(p5_list)}개**")

        if p5_list:
            st.write("예시로 몇 문제만 보여드릴게요:")
            for p in p5_list[:3]:
                st.write(f"- ({p.problem_id}) {p.question}")

        if st.button("⚔ P5 미니 전투 실행 (랜덤 5문제)", use_container_width=True):
            start_p5_quiz()
            st.session_state.armory_section = "p5"
            st.rerun()

    with col_vocab:
        st.markdown("### 📚 단어 무기고 (P7 + P5)")
        vocab_list: List[Dict] = st.session_state.secret_armory_vocab
        st.write(f"현재 저장된 단어: **{len(vocab_list)}개**")

        if vocab_list:
            st.write("예시로 몇 단어만 보여드릴게요:")
            for v in vocab_list[:5]:
                st.write(f"- {v['word']} : {v['meaning']} ({v['source']})")

        if st.button("🧠 Vocab Timebomb (학습 + 퀴즈 모드)", use_container_width=True):
            prepare_vocab_quiz_set()
            st.session_state.armory_section = "vocab"
            st.rerun()

    st.info(
        "비밀 병기고는 마구 저장만 하는 창고가 아니라, "
        "매일 들어와서 청소하고 강화하는 전투 무기고입니다."
    )

# ---------- P5 미니 전투 ----------

def start_p5_quiz():
    p5_list: List[P5Problem] = st.session_state.secret_armory_p5
    if not p5_list:
        return
    indices = list(range(len(p5_list)))
    random.shuffle(indices)
    indices = indices[:5]
    st.session_state.p5_quiz_order = indices
    st.session_state.p5_quiz_index = 0
    st.session_state.p5_quiz_started = True


def render_p5_armory():
    st.markdown("## 💣 P5 Timebomb – 무기고 미니 전투")

    p5_list: List[P5Problem] = st.session_state.secret_armory_p5
    if not p5_list:
        st.info("현재 비밀 병기고에 저장된 P5 문제가 없습니다.")
        if st.button("⬅ 허브로 돌아가기"):
            st.session_state.armory_section = "hub"
            st.rerun()
            return
        return

    if not st.session_state.p5_quiz_started:
        st.warning("먼저 허브에서 미니 전투를 시작해 주세요.")
        if st.button("⬅ 허브로 돌아가기"):
            st.session_state.armory_section = "hub"
            st.rerun()
        return

    order = st.session_state.p5_quiz_order
    idx = st.session_state.p5_quiz_index

    if idx >= len(order):
        st.success("🎉 P5 미니 전투를 모두 마쳤습니다!")
        if st.button("⬅ 허브로 돌아가기"):
            st.session_state.armory_section = "hub"
            st.session_state.p5_quiz_started = False
            st.rerun()
        return

    problem = p5_list[order[idx]]

    st.write(f"문제 {idx+1} / {len(order)}")
    st.write(problem.question)

    key = f"p5_quiz_answer_{idx}"
    chosen = st.radio(
        "",
        options=list(range(len(problem.options))),
        format_func=lambda i: problem.options[i],
        key=key,
        label_visibility="collapsed",
    )

    if st.button("정답 확인 및 다음 문제로 ➡", use_container_width=True):
        if chosen == problem.answer_index:
            st.success("정답입니다!")
            if st.checkbox("이 문제는 이제 무기고에서 삭제하기", key=f"p5_delete_{idx}"):
                to_delete_id = problem.problem_id
                new_list = [p for p in p5_list if p.problem_id != to_delete_id]
                st.session_state.secret_armory_p5 = new_list
                st.info(f"문제 {to_delete_id} 가 비밀 병기고에서 삭제되었습니다.")
        else:
            st.error("오답입니다. 다시 복습해 주세요.")

        st.session_state.p5_quiz_index = idx + 1
        st.rerun()

    if st.button("⚓ 전투 중단하고 허브로 돌아가기", use_container_width=True):
        st.session_state.armory_section = "hub"
        st.session_state.p5_quiz_started = False
        st.rerun()

# ---------- Vocab Timebomb (학습 + 퀴즈) ----------

def prepare_vocab_quiz_set():
    vocab_list: List[Dict] = st.session_state.secret_armory_vocab
    if not vocab_list:
        st.session_state.vocab_current_set = []
        st.session_state.vocab_quiz_order = []
        st.session_state.vocab_quiz_index = 0
        st.session_state.vocab_lives = 3
        st.session_state.vocab_score = 0
        st.session_state.vocab_stats_updated = False
        # ✅ 플립 카드 인덱스도 초기화
        st.session_state.vocab_study_index = 0
        st.session_state.vocab_study_show_kor = False
        return

    indices = list(range(len(vocab_list)))
    random.shuffle(indices)
    indices = indices[:10]
    current_set = [vocab_list[i] for i in indices]
    st.session_state.vocab_current_set = current_set

    # ✅ 학습 모드(플립 카드)도 첫 카드부터 시작
    st.session_state.vocab_study_index = 0
    st.session_state.vocab_study_show_kor = False

    order = list(range(len(current_set)))
    random.shuffle(order)
    st.session_state.vocab_quiz_order = order
    st.session_state.vocab_quiz_index = 0
    st.session_state.vocab_lives = 3
    st.session_state.vocab_score = 0
    st.session_state.vocab_stats_updated = False


def _generate_distractors(correct_word: str, all_words: List[str], num_choices: int = 4) -> List[str]:
    distractors = set()

    def tweak_word(w: str) -> str:
        if len(w) <= 2:
            return w.swapcase()
        mode = random.choice(["swap_case", "replace_char", "delete_char", "insert_char"])
        chars = list(w)
        if mode == "swap_case":
            return w.swapcase()
        elif mode == "replace_char":
            idx = random.randint(0, len(chars) - 1)
            chars[idx] = random.choice("abcdefghijklmnopqrstuvwxyz")
            return "".join(chars)
        elif mode == "delete_char":
            idx = random.randint(0, len(chars) - 1)
            return "".join(chars[:idx] + chars[idx + 1 :])
        else:
            idx = random.randint(0, len(chars))
            c = random.choice("abcdefghijklmnopqrstuvwxyz")
            return "".join(chars[:idx] + [c] + chars[idx:])

    pool = [w for w in all_words if w != correct_word]
    while len(distractors) < num_choices - 1 and pool:
        base = random.choice(pool)
        pool.remove(base)
        d = tweak_word(base)
        if d != correct_word:
            distractors.add(d)
    while len(distractors) < num_choices - 1:
        d = tweak_word(correct_word)
        if d != correct_word:
            distractors.add(d)
    return list(distractors)


def render_vocab_study_mode():
    st.markdown("### 🧠 Vocab Timebomb – 학습 모드 (플립 카드)")

    vocab_set: List[Dict] = st.session_state.vocab_current_set
    if not vocab_set:
        st.info("현재 비밀 병기고에 저장된 단어가 없어 학습할 내용이 없습니다.")
        if st.button("⬅ 허브로 돌아가기"):
            st.session_state.armory_section = "hub"
            st.rerun()
        return

    # 인덱스 / 앞뒤면 상태 보정
    if "vocab_study_index" not in st.session_state:
        st.session_state.vocab_study_index = 0
    if "vocab_study_show_kor" not in st.session_state:
        st.session_state.vocab_study_show_kor = False

    idx = st.session_state.vocab_study_index
    show_kor = st.session_state.vocab_study_show_kor

    if idx < 0:
        idx = len(vocab_set) - 1
    if idx >= len(vocab_set):
        idx = 0
    st.session_state.vocab_study_index = idx

    item = vocab_set[idx]
    eng_word = item["word"]
    kor_meaning = item["meaning"]

    st.caption(f"카드 {idx + 1} / {len(vocab_set)}")

    # 앞면/뒷면 텍스트
    if show_kor:
        main_text = kor_meaning
        sub_text = f"= {eng_word}"
    else:
        main_text = eng_word
        sub_text = "카드를 뒤집어 한국어 뜻을 확인해 보세요."

    st.markdown(
        f"""
        <div style="
            width: 100%;
            max-width: 480px;
            margin: 16px auto 24px auto;
            padding: 30px 24px;
            border-radius: 18px;
            background: linear-gradient(135deg, #fff9e6, #ffe8f0);
            box-shadow: 0 6px 18px rgba(0,0,0,0.08);
            text-align: center;
        ">
            <div style="font-size: 34px; font-weight: 700; margin-bottom: 10px;">
                {main_text}
            </div>
            <div style="font-size: 18px; color: #555;">
                {sub_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_prev, col_flip, col_next = st.columns(3)

    with col_prev:
        if st.button("⬅ 이전 카드", use_container_width=True):
            st.session_state.vocab_study_index = (idx - 1) % len(vocab_set)
            st.session_state.vocab_study_show_kor = False
            st.rerun()

    with col_flip:
        if st.button("🔄 카드 뒤집기", use_container_width=True):
            st.session_state.vocab_study_show_kor = not show_kor
            st.rerun()

    with col_next:
        if st.button("다음 카드 ➡", use_container_width=True):
            st.session_state.vocab_study_index = (idx + 1) % len(vocab_set)
            st.session_state.vocab_study_show_kor = False
            st.rerun()

    st.markdown("---")
    st.info(
        "플립 카드로 충분히 눈에 익힌 뒤, 아래 버튼을 눌러 "
        "같은 단어들로 타임어택 4지선다 퀴즈에 도전해 보세요."
    )

    if st.button("🎯 이 단어들로 퀴즈 모드 돌입 (KOR → ENG 4지선다)", use_container_width=True):
        st.session_state.vocab_armory_mode = "quiz"
        st.session_state.vocab_quiz_index = 0
        st.session_state.vocab_stats_updated = False
        st.rerun()


def render_vocab_quiz_mode():
    import time as _time
    try:
        from streamlit_autorefresh import st_autorefresh
    except ModuleNotFoundError:
        st_autorefresh = None
        st.warning(
            "자동 타이머를 사용하려면 'pip install streamlit-autorefresh' 후 다시 실행해 주세요. "
            "지금은 일반 카드 배틀 모드로 동작합니다."
        )

    st.markdown("### 🎮 Vocab Timebomb – 타임어택 카드 배틀 (ENG → KOR 4지선다)")

    vocab_set: List[Dict] = st.session_state.vocab_current_set
    if not vocab_set:
        st.info("현재 비밀 병기고에 저장된 단어가 없어 퀴즈를 진행할 수 없습니다.")
        if st.button("⬅ 허브로 돌아가기", use_container_width=True):
            st.session_state.armory_section = "hub"
            st.session_state.vocab_armory_mode = "study"
            st.rerun()
        return

    if "vocab_lives" not in st.session_state:
        st.session_state.vocab_lives = 3
    if "vocab_score" not in st.session_state:
        st.session_state.vocab_score = 0
    if "vocab_quiz_index" not in st.session_state:
        st.session_state.vocab_quiz_index = 0
    if "vocab_stats_updated" not in st.session_state:
        st.session_state.vocab_stats_updated = False
    if "vocab_last_result" not in st.session_state:
        st.session_state.vocab_last_result = None

    order = st.session_state.vocab_quiz_order
    idx = st.session_state.vocab_quiz_index
    total_q = len(order)
    lives = st.session_state.vocab_lives
    score = st.session_state.vocab_score

    if total_q == 0:
        st.info("이번 세트에 포함된 단어가 없습니다. 허브에서 다시 세트를 준비해 주세요.")
        if st.button("⬅ 허브로 돌아가기", use_container_width=True):
            st.session_state.armory_section = "hub"
            st.session_state.vocab_armory_mode = "study"
            st.rerun()
        return

    last = st.session_state.get("vocab_last_result")
    if last:
        if last["type"] == "correct":
            st.success(f"직전 카드 정답! {last['word']} : {last['meaning']}")
        elif last["type"] == "wrong":
            st.error(f"직전 카드 오답! {last['word']} : {last['meaning']}")
        elif last["type"] == "timeout":
            st.warning(f"시간초과! {last['word']} 카드를 놓쳤어요.")

        if last["type"] == "correct":
            if st.button(
                f"🧹 이제 '{last['word']}' 단어는 무기고에서 삭제하기",
                key="delete_last_vocab",
                use_container_width=True,
            ):
                new_list = [
                    v for v in st.session_state.secret_armory_vocab
                    if v["word"] != last["word"]
                ]
                st.session_state.secret_armory_vocab = new_list
                st.success(f"'{last['word']}' 단어가 무기고에서 삭제되었습니다.")
                st.session_state.vocab_last_result = None
                st.rerun()

    lives_clamped = max(0, min(3, lives))
    hearts = "❤️" * lives_clamped + "🤍" * (3 - lives_clamped)
    st.markdown(f"**{hearts} | 현재 점수 {score}/{total_q}**")

    if lives_clamped <= 0:
        st.error("목숨이 모두 소진되었습니다! 이번 세트는 여기까지예요.")
        st.info(f"최종 점수: {score} / {total_q}")

        col_retry, col_home = st.columns(2)
        with col_retry:
            if st.button("🔁 같은 무기고 단어로 다시 도전하기", use_container_width=True):
                prepare_vocab_quiz_set()
                st.session_state.vocab_armory_mode = "quiz"
                st.rerun()
        with col_home:
            if st.button("🏠 허브로 돌아가기", use_container_width=True):
                st.session_state.armory_section = "hub"
                st.session_state.vocab_armory_mode = "study"
                st.rerun()
        return

    if idx >= total_q:
        if not st.session_state.get("vocab_stats_updated", False):
            update_stats_after_vocab_set(score, total_q)
            st.session_state.vocab_stats_updated = True

        st.success("이번 Vocab Timebomb 타임어택 세트를 모두 마쳤습니다!")
        st.info(f"최종 점수: {score} / {total_q}")

        col_retry, col_home = st.columns(2)
        with col_retry:
            if st.button("🔁 같은 무기고 단어로 다시 도전하기", use_container_width=True):
                prepare_vocab_quiz_set()
                st.session_state.vocab_armory_mode = "quiz"
                st.rerun()
        with col_home:
            if st.button("🏠 허브로 돌아가기", use_container_width=True):
                st.session_state.armory_section = "hub"
                st.session_state.vocab_armory_mode = "study"
                st.rerun()
        return

    q_index = order[idx]
    target = vocab_set[q_index]
    eng_word = target["word"]
    kor_correct = target["meaning"]
    current_q_id = f"{idx}_{eng_word}"

    if st.session_state.get("vocab_q_current_id") != current_q_id:
        st.session_state.vocab_q_current_id = current_q_id
        st.session_state.vocab_q_start_time = _time.time()
        st.session_state.vocab_q_timeout_handled = False

    if st_autorefresh is not None:
        st_autorefresh(interval=1000, key="vocab_quiz_tick")

    start_time = st.session_state.get("vocab_q_start_time", _time.time())
    elapsed = _time.time() - start_time
    limit_sec = 3.0
    remaining = max(0.0, limit_sec - elapsed)

    st.markdown(f"⏱ 남은 시간: **{remaining:0.1f}초**")
    st.progress(remaining / limit_sec if limit_sec > 0 else 0)

    if remaining <= 0 and not st.session_state.get("vocab_q_timeout_handled", False):
        st.session_state.vocab_q_timeout_handled = True
        st.session_state.vocab_lives = max(0, lives_clamped - 1)
        st.session_state.vocab_quiz_index = idx + 1
        st.session_state.vocab_last_result = {
            "type": "timeout",
            "word": eng_word,
            "meaning": kor_correct,
        }
        st.warning("시간 초과! 이 카드는 자동으로 지나갔습니다.")
        st.rerun()

    st.write(f"문제 {idx + 1} / {total_q}")

    st.markdown(
        f"""
        <div style="
            font-size: 28px; font-weight: 700;
            padding: 10px 18px; border-radius: 14px;
            background-color: #fff3cd; display: inline-block;
            margin-top: 6px; margin-bottom: 12px;">
            🃏 {eng_word}
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("👉 이 단어의 뜻 카드를 하나 골라보세요. (3초 안에 선택!)")

    meanings_pool = [v["meaning"] for v in vocab_set if v["meaning"] != kor_correct]
    seed = q_index * 7919 + len(kor_correct)
    rng = random.Random(seed)
    rng.shuffle(meanings_pool)

    distractors = meanings_pool[:3]
    options = [kor_correct] + distractors
    rng.shuffle(options)

    for j, opt in enumerate(options):
        label = f"🃏 {opt}"
        if st.button(label, key=f"vocab_opt_{idx}_{j}", use_container_width=True):
            if opt == kor_correct:
                st.session_state.vocab_score = score + 1
                st.session_state.vocab_last_result = {
                    "type": "correct",
                    "word": eng_word,
                    "meaning": kor_correct,
                }
            else:
                st.session_state.vocab_lives = max(0, lives_clamped - 1)
                st.session_state.vocab_last_result = {
                    "type": "wrong",
                    "word": eng_word,
                    "meaning": kor_correct,
                }

            st.session_state.vocab_quiz_index = idx + 1
            st.session_state.vocab_q_start_time = _time.time()
            st.session_state.vocab_q_timeout_handled = False
            st.rerun()

    if st.button("⚓ 퀴즈 중단하고 허브로 돌아가기", use_container_width=True):
        st.session_state.armory_section = "hub"
        st.session_state.vocab_armory_mode = "study"
        st.rerun()


def render_vocab_armory():
    st.markdown("## 📚 Vocab Timebomb – 단어 무기고 전장")

    vocab_set: List[Dict] = st.session_state.vocab_current_set

    if not st.session_state.secret_armory_vocab:
        st.info("현재 비밀 병기고에 저장된 단어가 없습니다.")
        if st.button("⬅ 허브로 돌아가기"):
            st.session_state.armory_section = "hub"
            st.rerun()
        return

    if not vocab_set:
        st.warning("먼저 허브에서 Vocab Timebomb 세트를 준비해 주세요.")
        if st.button("⬅ 허브로 돌아가기"):
            st.session_state.armory_section = "hub"
            st.rerun()
        return

    mode = st.session_state.vocab_armory_mode

    col1, col2 = st.columns(2)
    with col1:
        if st.button("📖 학습 모드로 보기", use_container_width=True):
            st.session_state.vocab_armory_mode = "study"
            st.rerun()

    with col2:
        if st.button("🎯 퀴즈 모드로 도전", use_container_width=True):
            st.session_state.vocab_armory_mode = "quiz"
            st.rerun()

    st.markdown("---")

    if mode == "study":
        render_vocab_study_mode()
    else:
        render_vocab_quiz_mode()

# ============================================
# Score & Ranking 화면
# ============================================

def score_ranking_page():
    st.markdown("## 🏆 Score & Ranking – P7 + Vocab 종합 기록")

    stats = load_stats()
    p7 = stats.get("p7", {})
    vocab = stats.get("vocab", {})

    p7_sets = p7.get("total_sets", 0)
    p7_correct = p7.get("total_correct", 0)
    p7_total_q = p7.get("total_questions", 0)
    p7_acc = (p7_correct / p7_total_q * 100.0) if p7_total_q > 0 else 0.0
    p7_best_combo = p7.get("best_combo", 0)
    p7_last = p7.get("last_played", "")

    v_sets = vocab.get("total_sets", 0)
    v_correct = vocab.get("total_correct", 0)
    v_total_q = vocab.get("total_questions", 0)
    v_acc = (v_correct / v_total_q * 100.0) if v_total_q > 0 else 0.0
    v_best_score = vocab.get("best_score", 0)
    v_last = vocab.get("last_played", "")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📖 P7 Reading Arena 기록")
        st.metric("총 플레이 세트 수", p7_sets)
        st.metric("총 정답 수 / 총 문항 수", f"{p7_correct} / {p7_total_q}")
        st.metric("평균 정답률(%)", f"{p7_acc:.1f}%")
        st.metric("최고 콤보", f"{p7_best_combo} 연속")
        if p7_last:
            st.caption(f"마지막 플레이: {p7_last}")
        else:
            st.caption("아직 기록된 세트가 없습니다.")

        # ✅ 레벨 현황 테이블
        levels = get_all_p7_levels()
        if levels:
            st.markdown("#### 카테고리별 레벨 현황")
            rows = []
            for cat, info in levels.items():
                rows.append({
                    "Category": cat,
                    "Level": f"Lv{info.get('level', 1)}",
                    "Streak": f"{info.get('streak', 0)}/5",
                    "Cleared Sets": info.get("cleared_sets", 0),
                    "Total Sets": info.get("total_sets", 0),
                })
            st.table(rows)

    with col2:
        st.markdown("### 💣 Vocab Timebomb 기록")
        st.metric("총 퀴즈 세트 수", v_sets)
        st.metric("총 정답 수 / 총 문항 수", f"{v_correct} / {v_total_q}")
        st.metric("평균 정답률(%)", f"{v_acc:.1f}%")
        st.metric("한 세트 최고 점수", v_best_score)
        if v_last:
            st.caption(f"마지막 플레이: {v_last}")
        else:
            st.caption("아직 기록된 Vocab 세트가 없습니다.")

    st.markdown("---")
    st.info(
        "이 화면은 나만 보는 개인 랭킹 보드입니다. "
        "P7 세트와 Vocab Timebomb를 플레이할수록 기록과 레벨이 함께 쌓입니다."
    )

# ============================================
# Secret Armory 전체 페이지
# ============================================

def secret_armory_page():
    st.markdown("## 🧨 Secret Armory – 개인 비밀 무기고")

    init_armory_state()

    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🏠 허브", use_container_width=True):
            st.session_state.armory_section = "hub"
    with col2:
        if st.button("💣 P5 무기고", use_container_width=True):
            st.session_state.armory_section = "p5"
    with col3:
        if st.button("📚 단어 무기고", use_container_width=True):
            st.session_state.armory_section = "vocab"

    st.markdown("---")

    section = st.session_state.armory_section
    if section == "hub":
        render_armory_hub()
    elif section == "p5":
        render_p5_armory()
    else:
        render_vocab_armory()

# ============================================
# 메인 엔트리
# ============================================

def run():
    """Entry point used by pages/01_P7_Reading_Arena.py and main_hub.py.
    This module renders ONLY the P7 Reading Arena battle screen (80% battlefield + 20% HUD).
    """
    init_session_state()
    return reading_arena_page()


# direct run safety (dev only)
if __name__ == "__main__":
    try:
        st.set_page_config(page_title="SnapQ P7 Reading Arena", page_icon="🔥", layout="wide", initial_sidebar_state="collapsed")
    except Exception:
        pass
    run()