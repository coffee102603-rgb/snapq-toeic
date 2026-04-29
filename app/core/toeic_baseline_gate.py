"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE:     app/core/toeic_baseline_gate.py
ROLE:     매월 TOEIC 점수 입력 게이트 + toeic_level 자동 분류 + cohort_id 매핑
VERSION:  v1.0 — 2026.04.27 (박사 1년차 학위논문 통계 기반 변수 확보)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USAGE (main_hub.py 753~754행 사이에 추가):
    nickname = require_access()
    require_toeic_baseline_gate(nickname)   # ← 이 줄 추가
    require_pretest_gate()

FLOW:
    매월 1일~말일, 첫 접속 시:
      ① 이번 달 TOEIC 점수 입력 (필수)
      ② 응시일자 입력
      ③ 점수 출처 선택 (정기시험/모의고사/자가측정)
      ④ 자동 처리:
         - toeic_level 자동 분류 (선생님 기준: 700/800/900)
         - cohort_id 자동 매핑 (C1~C5)
         - 이전 달 점수 비교 → score_diff 계산
         - Google Sheets toeic_scores_monthly 시트 저장

DATA OUT:
    로컬:    data/students/{nickname}/toeic_history.jsonl  (학생별 시계열)
            data/cohorts/{month}/roster.jsonl  (latest_toeic_* 갱신)
    Sheets:  toeic_scores_monthly 시트 (Level 1·2 변수 통합)

PAPER LINKS:
    ⑩ SSCI 통합:    종속변수 — 월별 TOEIC 점수 변화량
    ⑪ 박사학위논문: ★★★ 핵심 — Growth Curve Model의 Level 1 시계열
    ② ADDIE:        UI 설계 사례 (점수 입력 UX)

ACADEMIC RATIONALE (점수 절단점):
    - 700점 미만: 초급 (TOEIC 평균 이하)
    - 700~800점: 중급 (대학 졸업 기준선)
    - 800~900점: 고급 (취업 기준선)
    - 900점 이상: 최상급 (전문가 수준)
    근거: 한국 TOEIC 응시자 분포 및 기업 채용 기준 평균
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
from __future__ import annotations

import json
from datetime import datetime, date
from pathlib import Path
from typing import Optional, Dict, List

import streamlit as st

# IRB_GUARD_MARKER: RESEARCH_MODE import
try:
    from app.core.attendance_engine import RESEARCH_MODE
except Exception:
    RESEARCH_MODE = False


# =========================================================
# 핵심 상수 — 박사학위논문 통계 기반
# =========================================================
TOEIC_LEVEL_CUTOFFS = {
    "초급":   (0,    700),   # < 700
    "중급":   (700,  800),   # 700 ≤ x < 800
    "고급":   (800,  900),   # 800 ≤ x < 900
    "최상급": (900,  991),   # ≥ 900
}

# 5개 코호트 매핑 (10개월 대장정: 2026.05 ~ 2027.02)
COHORT_MAP = {
    "2026-05": "C1", "2026-06": "C1",   # 1차 5-6월
    "2026-07": "C2", "2026-08": "C2",   # 2차 7-8월
    "2026-09": "C3", "2026-10": "C3",   # 3차 9-10월
    "2026-11": "C4", "2026-12": "C4",   # 4차 11-12월
    "2027-01": "C5", "2027-02": "C5",   # 5차 1-2월
}

# 점수 출처 분류 (학술적 신뢰도 반영)
SCORE_SOURCES = {
    "official":     "정기 TOEIC 시험 (가장 신뢰)",
    "mock":         "공식 모의고사",
    "self_test":    "온라인 자가 측정",
    "estimate":     "예상 점수 (확실치 않음)",
}

BASE = Path(__file__).parent.parent.parent


# =========================================================
# 분류·매핑 함수 (외부 모듈에서도 import해서 사용)
# =========================================================
def get_toeic_level(score: int) -> str:
    """
    TOEIC 점수를 4개 레벨로 자동 분류.

    EXAMPLES:
        get_toeic_level(650) → "초급"
        get_toeic_level(750) → "중급"
        get_toeic_level(850) → "고급"
        get_toeic_level(950) → "최상급"
    """
    if not isinstance(score, (int, float)) or score < 0:
        return "미분류"
    for level, (lo, hi) in TOEIC_LEVEL_CUTOFFS.items():
        if lo <= score < hi:
            return level
    return "미분류"


def get_cohort_id(month_key: str) -> str:
    """
    월별 코드 → 코호트 ID 매핑.

    EXAMPLES:
        get_cohort_id("2026-05") → "C1"
        get_cohort_id("2026-12") → "C4"
        get_cohort_id("2026-04") → "PRE"  (연구 개시 전)
    """
    return COHORT_MAP.get(month_key, "PRE")


# =========================================================
# 학생별 TOEIC 시계열 파일 관리
# =========================================================
def _student_dir(nickname: str) -> Path:
    """학생별 데이터 폴더 (cross-cohort 시계열용)"""
    return BASE / "data" / "students" / nickname


def _toeic_history_path(nickname: str) -> Path:
    return _student_dir(nickname) / "toeic_history.jsonl"


def _ensure_student_dir(nickname: str):
    _student_dir(nickname).mkdir(parents=True, exist_ok=True)


def _load_toeic_history(nickname: str) -> List[Dict]:
    """학생의 TOEIC 점수 시계열 전체 로드 (오래된 순)"""
    path = _toeic_history_path(nickname)
    if not path.exists():
        return []
    history = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                history.append(json.loads(line.strip()))
            except Exception:
                continue
    return sorted(history, key=lambda x: x.get("month", ""))


def _has_this_month_score(nickname: str, month_key: str) -> bool:
    """이번 달에 이미 점수를 입력했는가?"""
    history = _load_toeic_history(nickname)
    return any(h.get("month") == month_key for h in history)


def _get_previous_score(nickname: str, current_month: str) -> Optional[Dict]:
    """가장 최근 입력된 이전 달 점수 (없으면 None)"""
    history = _load_toeic_history(nickname)
    earlier = [h for h in history if h.get("month", "") < current_month]
    return earlier[-1] if earlier else None


# =========================================================
# Google Sheets 저장 (toeic_scores_monthly 시트)
# =========================================================
def _save_to_sheets(entry: Dict) -> bool:
    """toeic_scores_monthly 시트에 1행 추가 (실패해도 게임 계속)"""
    try:
        import gspread
        gc = gspread.service_account_from_dict(dict(st.secrets["gcp_service_account"]))
        sh = gc.open_by_key(st.secrets["SPREADSHEET_ID"])
        headers = [
            "timestamp", "user_id", "month", "cohort_id",
            "toeic_score", "toeic_level", "score_source", "test_date",
            "previous_score", "score_diff",
            "consent_research", "consent_version",
            "research_phase",
        ]
        try:
            ws = sh.worksheet("toeic_scores_monthly")
        except Exception:
            ws = sh.add_worksheet(title="toeic_scores_monthly",
                                   rows=5000, cols=len(headers))
            ws.append_row(headers)
        if not ws.row_values(1):
            ws.append_row(headers)
        row = [str(entry.get(h, "")) if entry.get(h) is not None else "" for h in headers]
        ws.append_row(row)
        return True
    except Exception as e:
        try:
            st.session_state["_sheets_err_toeic"] = str(e)[:300]
        except Exception:
            pass
        return False


# =========================================================
# 점수 저장 (로컬 + Sheets + roster 갱신)
# =========================================================
def _save_toeic_score(nickname: str,
                      month_key: str,
                      score: int,
                      source: str,
                      test_date: str,
                      consent_research: bool = True,
                      consent_version: str = "v1.0_2026-04-27") -> Dict:
    """
    TOEIC 점수 저장 — 로컬 시계열 + Sheets + roster 갱신.

    RETURNS:
        저장된 entry dict (UI 결과 표시용)
    """
    _ensure_student_dir(nickname)

    # 이전 달 점수 찾기 (변화량 계산)
    prev = _get_previous_score(nickname, month_key)
    prev_score = prev.get("toeic_score") if prev else None
    score_diff = (score - prev_score) if prev_score is not None else None

    # 자동 분류
    level = get_toeic_level(score)
    cohort = get_cohort_id(month_key)

    entry = {
        "timestamp":         datetime.now().isoformat(timespec="seconds"),
        "user_id":           nickname,
        "month":             month_key,
        "cohort_id":         cohort,
        "toeic_score":       int(score),
        "toeic_level":       level,
        "score_source":      source,
        "test_date":         test_date,
        "previous_score":    prev_score,
        "score_diff":        score_diff,
        "consent_research":  bool(consent_research),
        "consent_version":   consent_version,
        "research_phase":    "pre_irb",  # IRB 승인 후 "main"
    }

    # 1) 로컬 시계열 저장
    try:
        with open(_toeic_history_path(nickname), "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass

    # 2) Sheets 저장
    _save_to_sheets(entry)

    # 3) 현재 달 roster.jsonl의 latest_* 필드 갱신
    try:
        from app.core.access_guard import update_student_record
        update_student_record(nickname, month_key, {
            "latest_toeic_score":  int(score),
            "latest_toeic_level":  level,
            "latest_toeic_month":  month_key,
            "latest_toeic_source": source,
            "cohort_id":           cohort,
        })
    except Exception:
        pass

    return entry


# =========================================================
# 메인 게이트 함수
# =========================================================
def require_toeic_baseline_gate(nickname: str,
                                month_key: Optional[str] = None) -> None:
    """
    매월 TOEIC 점수 입력 게이트.

    이번 달 점수가 이미 입력되어 있으면 즉시 통과.
    없으면 입력 화면 표시 → 입력 완료 시 통과.

    USAGE:
        nickname = require_access()
        require_toeic_baseline_gate(nickname)   # ← 추가
        require_pretest_gate()
    """
    if not RESEARCH_MODE:
        return  # IRB pilot: TOEIC baseline disabled
    if not nickname:
        return

    if not month_key:
        month_key = date.today().strftime("%Y-%m")

    # 이미 이번 달 점수 입력했으면 통과
    if _has_this_month_score(nickname, month_key):
        return

    # 세션 내 캐시 (rerun 시 중복 표시 방지)
    if st.session_state.get(f"_toeic_gate_done_{month_key}"):
        return

    # ── 입력 화면 표시 ──
    _show_toeic_input_screen(nickname, month_key)
    st.stop()  # 입력 완료 전까지 다음 게이트로 못 넘어감


# =========================================================
# 입력 화면 UI
# =========================================================
def _show_toeic_input_screen(nickname: str, month_key: str) -> None:
    """
    이번 달 TOEIC 점수 입력 화면.

    UX 설계 원칙 (박사 ② ADDIE 사례):
        - 이전 달 점수가 있으면 "지난달 750 → 이번 달은?" 보여주기
        - 점수 입력 → 응시일 → 출처 → 한 화면에서
        - 모바일 대응 (큰 버튼·큰 입력창)
    """
    cohort = get_cohort_id(month_key)
    cohort_label = {
        "C1": "1차 (5-6월)",
        "C2": "2차 (7-8월)",
        "C3": "3차 (9-10월)",
        "C4": "4차 (11-12월)",
        "C5": "5차 (1-2월)",
        "PRE": "사전 운영기",
    }.get(cohort, cohort)

    prev = _get_previous_score(nickname, month_key)

    # ── CSS ──
    st.markdown("""
    <style>
    .stApp { background: #0D0F1A !important; }
    .block-container { max-width: 480px !important; margin: 0 auto !important;
                       padding-top: 40px !important; }
    .toeic-card {
        background: linear-gradient(135deg, rgba(244,201,93,0.1) 0%, rgba(125,211,252,0.05) 100%);
        border: 1px solid rgba(244,201,93,0.3);
        border-radius: 20px;
        padding: 32px 24px;
        margin-bottom: 20px;
        color: #fff;
    }
    .toeic-title { font-size: 24px; font-weight: 900; color: #F4C95D;
                   margin-bottom: 12px; text-align: center; }
    .toeic-subtitle { font-size: 14px; color: rgba(255,255,255,0.6);
                      margin-bottom: 24px; text-align: center; }
    .prev-score-box {
        background: rgba(125,211,252,0.1);
        border-left: 4px solid #7DD3FC;
        padding: 14px 18px;
        margin: 16px 0;
        border-radius: 8px;
        color: rgba(255,255,255,0.85);
        font-size: 14px;
    }
    .cohort-badge {
        display: inline-block;
        background: rgba(244,201,93,0.2);
        border: 1px solid rgba(244,201,93,0.4);
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 12px;
        color: #F4C95D;
        font-weight: 700;
        letter-spacing: 1px;
    }
    div.stNumberInput > div > input {
        background: rgba(255,255,255,0.07) !important;
        border: 1px solid rgba(255,255,255,0.15) !important;
        border-radius: 12px !important;
        color: #fff !important;
        font-size: 28px !important;
        font-weight: 900 !important;
        text-align: center !important;
        padding: 14px !important;
    }
    div.stDateInput > div > div > input {
        background: rgba(255,255,255,0.07) !important;
        color: #fff !important;
        border-radius: 12px !important;
    }
    #MainMenu, footer, header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

    # ── 헤더 ──
    st.markdown(f"""
    <div class="toeic-card">
        <div style="text-align:center; margin-bottom:16px;">
            <span class="cohort-badge">📅 {cohort_label}</span>
        </div>
        <div class="toeic-title">📊 이번 달 TOEIC 점수</div>
        <div class="toeic-subtitle">
            {month_key} · 매월 한 번만 입력해주세요!<br>
            여러분의 점수 변화가 박사 연구의 핵심 데이터예요 🎓
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── 이전 달 점수 비교 (있으면) ──
    if prev:
        prev_score = prev.get("toeic_score", 0)
        prev_month = prev.get("month", "")
        prev_level = prev.get("toeic_level", "")
        st.markdown(f"""
        <div class="prev-score-box">
            <strong>📌 지난번 입력:</strong> {prev_month} → <strong>{prev_score}점</strong> ({prev_level})<br>
            <span style="font-size:12px; color:rgba(255,255,255,0.5);">
                이번 달은 어떻게 변했나요?
            </span>
        </div>
        """, unsafe_allow_html=True)

    # ── 입력 필드 ──
    with st.form(key=f"toeic_form_{month_key}", clear_on_submit=False):
        score = st.number_input(
            "💯 TOEIC 점수 (200~990)",
            min_value=200, max_value=990, value=700, step=5,
            help="가장 최근에 본 TOEIC 점수를 입력해주세요",
        )

        test_date = st.date_input(
            "📆 응시일자",
            value=date.today(),
            help="언제 본 점수인가요?",
        )

        source = st.selectbox(
            "📋 점수 출처",
            options=list(SCORE_SOURCES.keys()),
            format_func=lambda x: SCORE_SOURCES[x],
            help="가장 신뢰도 높은 점수를 골라주세요",
        )

        # 미리보기
        preview_level = get_toeic_level(score)
        st.markdown(f"""
        <div style="text-align:center; margin:16px 0; padding:12px;
             background:rgba(244,201,93,0.05); border-radius:12px;
             color:rgba(255,255,255,0.85); font-size:14px;">
            자동 분류: <strong style="color:#F4C95D;">{preview_level}</strong>
            · 코호트: <strong style="color:#7DD3FC;">{cohort_label}</strong>
        </div>
        """, unsafe_allow_html=True)

        submitted = st.form_submit_button(
            "✅ 입력 완료 · Snap 토익 시작!",
            use_container_width=True,
            type="primary",
        )

        if submitted:
            # 동의 여부는 access_guard에서 이미 받았다고 가정
            consent = st.session_state.get("consent_research_given", True)
            consent_ver = st.session_state.get("consent_version",
                                               "v1.0_2026-04-27")

            entry = _save_toeic_score(
                nickname=nickname,
                month_key=month_key,
                score=int(score),
                source=source,
                test_date=test_date.isoformat(),
                consent_research=consent,
                consent_version=consent_ver,
            )

            # 결과 화면
            diff_text = ""
            if entry.get("score_diff") is not None:
                d = entry["score_diff"]
                if d > 0:
                    diff_text = f"📈 지난번 대비 +{d}점!"
                elif d < 0:
                    diff_text = f"📉 지난번 대비 {d}점"
                else:
                    diff_text = "➡️ 지난번과 동일"

            st.success(
                f"✅ {month_key} 점수 입력 완료!\n\n"
                f"점수: **{entry['toeic_score']}** ({entry['toeic_level']})\n\n"
                f"{diff_text}\n\n"
                f"잠시 후 Snap 토익으로 자동 입장합니다... 🚀"
            )
            st.session_state[f"_toeic_gate_done_{month_key}"] = True
            st.balloons()
            # ── v1.3 BUG FIX (2026-04-27) ──
            # 기존: st.form 안에서 st.button(on_click=...) 호출 → StreamlitInvalidFormCallbackError
            # 변경: 2초 대기 후 자동 rerun (form 안에서 안전)
            import time
            time.sleep(2)
            st.rerun()


# =========================================================
# 외부에서 조회용 헬퍼
# =========================================================
def get_current_toeic_info(nickname: str,
                           month_key: Optional[str] = None) -> Dict:
    """
    현재 학생의 TOEIC 정보 조회 (다른 페이지에서 사용).

    RETURNS:
        {
            "score": int or None,
            "level": str,
            "cohort_id": str,
            "month": str,
            "history_count": int,
            "growth_trend": float (이전 달 대비 변화량 평균),
        }
    """
    if not month_key:
        month_key = date.today().strftime("%Y-%m")

    history = _load_toeic_history(nickname)
    if not history:
        return {
            "score": None, "level": "미분류",
            "cohort_id": get_cohort_id(month_key),
            "month": month_key, "history_count": 0,
            "growth_trend": 0.0,
        }

    latest = history[-1]
    diffs = [h.get("score_diff", 0) for h in history if h.get("score_diff") is not None]
    growth = sum(diffs) / len(diffs) if diffs else 0.0

    return {
        "score":         latest.get("toeic_score"),
        "level":         latest.get("toeic_level"),
        "cohort_id":     latest.get("cohort_id", get_cohort_id(month_key)),
        "month":         latest.get("month"),
        "history_count": len(history),
        "growth_trend":  round(growth, 1),
    }
