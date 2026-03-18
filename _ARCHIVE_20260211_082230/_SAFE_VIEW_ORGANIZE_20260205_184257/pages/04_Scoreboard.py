import json
from pathlib import Path
from typing import List, Dict, Any, Optional

import streamlit as st

# --- SNAPQ_MAIN_HUB_NAV (auto) ---
try:
    _hub_col, _hub_spacer = st.columns([1.4, 8.6])
    with _hub_col:
        if st.button("🏠 MAIN HUB", key=f"hub_{__file__}", use_container_width=True):
            try:
                st.switch_page("main_hub.py")
            except Exception:
                st.info("좌측 메뉴(사이드바)에서 Main Hub로 이동해주세요.")
except Exception:
    pass
# --- /SNAPQ_MAIN_HUB_NAV ---


st.set_page_config(
    page_title="📊 Scoreboard · SnapQ TOEIC",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# SNAPQ_GLOBAL_CSS_LOADER
import os as _os
def _snapq_load_global_css():
    _candidates = [
        _os.path.join("styles","global.css"),
        _os.path.join("assets","global.css"),
    ]
    _css = ""
    for _p in _candidates:
        if _os.path.exists(_p):
            try:
                with open(_p, "r", encoding="utf-8") as _f:
                    _css = _f.read()
                break
            except Exception:
                pass
    if _css:
        st.markdown("<style>" + _css + "</style>", unsafe_allow_html=True)

_snapq_load_global_css()
# SNAPQ_GLOBAL_CSS_LOADER
# ✅ 통일: 사이드바 완전 제거 + 모바일 패딩 유지
from app.core.ui_shell import apply_ui_shell
apply_ui_shell()

from app.core.battle_theme import apply_battle_theme
from app.arenas.p7_vocab_scoreboard import run_p7_vocab_scoreboard


# ============================================================
# P5 기록 로딩 유틸 (p5_runs.jsonl)
# ============================================================

def _resolve_p5_runs_path() -> Optional[Path]:
    """
    p5_runs.jsonl 위치 후보를 순서대로 탐색.
    - Windows에서 replace("\\") 같은 위험한 문자열 조작 절대 금지.
    """
    candidates = [
        Path("data") / "stats" / "p5_runs.jsonl",
        Path("app") / "data" / "stats" / "p5_runs.jsonl",
    ]
    for p in candidates:
        if p.exists():
            return p
    return None


def load_p5_runs(limit: int = 200) -> List[Dict[str, Any]]:
    """p5_runs.jsonl에서 최근 limit개 기록 로딩(최신순)"""
    path = _resolve_p5_runs_path()
    if not path:
        return []

    rows: List[Dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    rows.append(obj)
            except Exception:
                continue
    except Exception:
        return []

    # 최신순(가능하면 ts 기준)
    rows.sort(key=lambda r: str(r.get("ts", "")), reverse=True)
    return rows[: max(1, int(limit))]


# ============================================================
# 스키마 호환(구버전/신버전 혼용 대응)
# ============================================================

def _get_int(r: Dict[str, Any], keys: List[str], default: int = 0) -> int:
    for k in keys:
        if k in r and r.get(k) is not None:
            try:
                return int(r.get(k))
            except Exception:
                pass
    return default


def _get_str(r: Dict[str, Any], keys: List[str], default: str = "-") -> str:
    for k in keys:
        v = r.get(k)
        if v is None:
            continue
        s = str(v).strip()
        if s:
            return s
    return default


def _mode_label(r: Dict[str, Any]) -> str:
    """
    mode 호환:
    - 신버전: "GRAMMAR"/"VOCAB"
    - 구버전: "grammar"/"vocab"
    """
    mode = _get_str(r, ["mode"], "").lower()
    if mode == "grammar":
        cat = _get_str(r, ["category"], "-")
        return f"🧠 어법 / {cat}"
    if mode == "vocab":
        lvl = _get_str(r, ["level"], "-")
        return f"⚡ 어휘 / {lvl}"
    return "🧨 P5"


def _calc_accuracy(r: Dict[str, Any]) -> int:
    """
    정확도 호환:
    - 구버전: accuracy(%)
    - 신버전: correct/total (또는 correct/5)
    """
    # 1) 구버전 accuracy 우선
    if "accuracy" in r and r.get("accuracy") is not None:
        try:
            return int(r.get("accuracy"))
        except Exception:
            pass

    correct = _get_int(r, ["correct"], 0)
    total = _get_int(r, ["total"], 0)

    # total이 없으면 5문제 세트로 가정(현재 P5 구조)
    if total <= 0:
        total = 5

    if total <= 0:
        return 0

    return int(round((correct / total) * 100))


def _is_success(r: Dict[str, Any]) -> bool:
    """
    성공/실패 호환:
    - 신버전: success(True/False)
    - 구버전: status == "SAFE" 가 성공
    """
    if "success" in r:
        return bool(r.get("success"))

    status = _get_str(r, ["status"], "").upper()
    if status:
        return status == "SAFE"

    # 둘 다 없으면: 보수적으로 correct>=4면 성공 처리
    correct = _get_int(r, ["correct"], 0)
    return correct >= 4


def _time_limit_sec(r: Dict[str, Any]) -> int:
    """
    시간 호환:
    - 신버전: timer
    - 구버전: time_limit
    """
    return _get_int(r, ["timer", "time_limit"], 0)


def _line_summary(r: Dict[str, Any]) -> str:
    correct = _get_int(r, ["correct"], 0)
    total = _get_int(r, ["total"], 5) or 5
    acc = _calc_accuracy(r)
    t = _time_limit_sec(r)
    ts = _get_str(r, ["ts"], "-")
    tag = "🟢 SAFE" if _is_success(r) else "💥 BOOM"
    return f"{ts} | {_mode_label(r)} | ⏱ {t}s | ✅ {correct}/{total} | 🎯 {acc}% | {tag}"


# ============================================================
# P5 카드 렌더
# ============================================================

def render_p5_scoreboard_card():
    runs = load_p5_runs(limit=200)

    st.markdown("## 🧨 P5 TIMEBOMB — 전투 리포트")

    path = _resolve_p5_runs_path()
    if not runs:
        st.info("아직 P5 기록이 없습니다.")
        if path:
            st.caption(f"기록 파일: {path.as_posix()}")
        else:
            st.caption("기록 파일을 찾지 못했습니다: data/stats/p5_runs.jsonl 또는 app/data/stats/p5_runs.jsonl")
        st.caption("P5 한 판만 돌리고 다시 오면 여기로 전적이 누적됩니다.")
        return

    total_runs = len(runs)
    success_runs = sum(1 for r in runs if _is_success(r))
    boom_runs = total_runs - success_runs

    # 최근 20판 평균 정확도
    recent = runs[:20]
    avg_acc = int(round(sum(_calc_accuracy(r) for r in recent) / max(1, len(recent))))

    best_acc = max((_calc_accuracy(r) for r in runs), default=0)

    # 콤보(구버전 best_combo / 신버전엔 없을 수 있음)
    best_combo = max((_get_int(r, ["best_combo"], 0) for r in runs), default=0)

    last = runs[0]
    last_line = _line_summary(last)

    with st.container(border=True):
        st.markdown("**최근 전투 요약**")
        st.write(last_line)
        st.caption(f"마지막 기록: {_get_str(last, ['ts'], '-')}")
        if path:
            st.caption(f"기록 파일: {path.as_posix()}")

        st.markdown("---")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("총 출격", total_runs)
        with c2:
            st.metric("🟢 SAFE", success_runs)
        with c3:
            st.metric("💥 BOOM", boom_runs)
        with c4:
            st.metric("최근20판 평균", f"{avg_acc}%")

        st.markdown("---")
        c5, c6 = st.columns(2)
        with c5:
            st.metric("최고 정확도", f"{best_acc}%")
        with c6:
            st.metric("최고 콤보", best_combo)

    # 최근 10판 로그
    with st.expander("📜 최근 10판 로그 보기", expanded=False):
        for r in runs[:10]:
            st.write("• " + _line_summary(r))


# ============================================================
# 메인
# ============================================================

def main():
    apply_battle_theme()

    st.title("📊 Scoreboard")

    # ✅ P5 리포트 (2단계)
    render_p5_scoreboard_card()

    st.markdown("---")

    # ✅ 기존 P7 / VOCA 리포트 (유지)
    run_p7_vocab_scoreboard()


main()