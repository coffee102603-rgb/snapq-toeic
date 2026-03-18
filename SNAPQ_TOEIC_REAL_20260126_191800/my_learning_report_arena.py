import datetime
import json
from pathlib import Path

import streamlit as st


# ---------------------------------------------------------
# My Learning Report – 월간 성장 성적표
# (파일 기반 추정치 + 가능한 경우 stats JSON을 읽어 요약)
# ---------------------------------------------------------

_ROOT = Path(__file__).resolve().parent


def _safe_load_json(path: Path):
    try:
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None


def _pct(correct: int, total: int):
    if total <= 0:
        return None
    return round((correct / total) * 100.0, 1)


def _fmt_rate(correct: int, total: int):
    p = _pct(correct, total)
    if p is None:
        return "— (0/0)"
    return f"{p}% ({correct}/{total})"


def _month_range(today: datetime.date):
    start = today.replace(day=1)
    if start.month == 12:
        end = start.replace(year=start.year + 1, month=1)
    else:
        end = start.replace(month=start.month + 1)
    return start, end


def _estimate_active_days_this_month():
    """현재는 '월간 로그'가 없으니, 주요 데이터 파일의 수정일로 추정."""
    today = datetime.date.today()
    start, end = _month_range(today)

    candidates = [
        _ROOT / "data" / "profiles",
        _ROOT / "snapq_data",
        _ROOT / "data",
        _ROOT / "app" / "data",
    ]

    days = set()
    for base in candidates:
        if not base.exists():
            continue
        try:
            if base.is_file():
                mt = datetime.date.fromtimestamp(base.stat().st_mtime)
                if start <= mt < end:
                    days.add(mt)
            else:
                for p in base.rglob("*.json"):
                    mt = datetime.date.fromtimestamp(p.stat().st_mtime)
                    if start <= mt < end:
                        days.add(mt)
        except Exception:
            continue

    return len(days)


def _extract_correct_total(obj):
    """stats json 형태가 달라도 최대한 (correct,total)을 뽑아낸다."""
    if not isinstance(obj, dict):
        return (0, 0)

    for ck, tk in [
        ("correct", "total"),
        ("num_correct", "num_total"),
        ("correct_count", "total_count"),
        ("right", "attempts"),
    ]:
        if ck in obj and tk in obj:
            try:
                return (int(obj.get(ck, 0)), int(obj.get(tk, 0)))
            except Exception:
                pass

    for lk in ["records", "items", "rows", "history", "log"]:
        v = obj.get(lk)
        if isinstance(v, list) and v:
            c = 0
            t = 0
            for it in v:
                if isinstance(it, dict):
                    if "is_correct" in it:
                        t += 1
                        c += 1 if it.get("is_correct") else 0
                    elif "correct" in it and "total" in it:
                        cc, tt = _extract_correct_total(it)
                        c += cc
                        t += tt
            if t > 0:
                return (c, t)

    c = 0
    t = 0
    for v in obj.values():
        if isinstance(v, dict):
            cc, tt = _extract_correct_total(v)
            c += cc
            t += tt
    return (c, t)


def _load_rate_summary():
    """가능한 파일들을 뒤져서 P5/P7/VOCA 정답률 요약을 만든다."""
    candidates = {
        "p5": [
            _ROOT / "data" / "p5" / "p5_stats.json",
            _ROOT / "data" / "p5_bank" / "p5_stats.json",
            _ROOT / "snapq_data" / "p5_stats.json",
        ],
        "p7": [
            _ROOT / "data" / "p7" / "p7_reading_stats.json",
            _ROOT / "snapq_data" / "p7_reading_stats.json",
        ],
        "voca": [
            _ROOT / "data" / "p7_vocab_stats.json",
            _ROOT / "data" / "p7" / "p7_vocab_stats.json",
            _ROOT / "snapq_data" / "p7_vocab_stats.json",
        ],
    }

    out = {"p5": (0, 0), "p7": (0, 0), "voca": (0, 0)}
    for key, paths in candidates.items():
        for p in paths:
            obj = _safe_load_json(p)
            if obj is None:
                continue
            out[key] = _extract_correct_total(obj)
            break
    return out


def run_my_learning_report_arena():
    st.header("📄 My Learning Report – 월간 성장 성적표")

    active_days = _estimate_active_days_this_month()
    st.subheader("✅ 이번 달 활동한 날")
    st.metric("이번 달 활동한 날", f"{active_days}일")

    st.subheader("📊 P5 / P7 / VOCA 정답률 요약")
    rates = _load_rate_summary()
    p5_c, p5_t = rates["p5"]
    p7_c, p7_t = rates["p7"]
    vo_c, vo_t = rates["voca"]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("P5", _fmt_rate(p5_c, p5_t))
    with c2:
        st.metric("P7", _fmt_rate(p7_c, p7_t))
    with c3:
        st.metric("VOCA", _fmt_rate(vo_c, vo_t))

    st.caption(
        "※ active_days는 현재 ‘파일 수정일’ 기반 추정치라 작게 나올 수 있어요. "
        "다음 단계에서 ‘월간 로그’를 날짜별로 저장하면 100% 정확해집니다."
    )
