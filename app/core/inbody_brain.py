"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE:     app/core/inbody_brain.py
ROLE:     인바디 멘트 선택 두뇌 (학생 데이터 → 멘트 결정)
VERSION:  SnapQ TOEIC V3 — 2026.04.30
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USAGE:
    from app.core.inbody_brain import build_inbody_messages

    messages = build_inbody_messages(nickname)
    # messages = [
    #   {"character": "skull", "text": "포로 23명. 이건 직무유기야.",
    #    "priority": "prison_overflow", "size": "main"},
    #   {"character": "tori",  "text": "수동태 47%.",
    #    "priority": "weak_p5_category", "size": "sub"},
    #   ...
    # ]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DESIGN (B안):
    데이터 있는 만큼 1~3명 가변 등장.
    - 첫날 (데이터 0)      → 환영 시퀀스 (별도 처리)
    - 1주차 (데이터 적음)  → 1~2명 멘트
    - 정착 (데이터 많음)   → 최대 3명 멘트

PRIORITY ORDER:
    가장 시급한 것 → 메인 (큰 카드)
    그 다음 2개   → 서브 (작은 라인)

    1. same_word_3plus      (같은 단어 3+ 오답) ★ 철학 핵심
    2. prison_overflow      (포로 16명+) 긴급
    3. absent_4plus_days    (4일+ 결석)
    4. trend_drop_10pct     (급격 하락)
    5. new_only_90pct       (새 문제만 풀기)
    6. milestone_unlock     (마일스톤 달성)
    7. weak_category        (약점 카테고리)
    8. trend_3day_up        (3일 연속 상승)
    9. streak_milestone     (출석 스트릭)
   10. today_time           (오늘 학습 시간)
   11. time_of_day          (시간대 — 마지막 보루)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NOTE:
    멘트 풀은 inbody_messages.py에 정의 (다음 파일).
    이 파일은 "어떤 멘트를 띄울지" 결정만.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import random
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple

from app.core.inbody_db import get_conn


# ─────────────────────────────────────────────────────────────
# cat 필드 → 멘트 그룹 매핑 (회의록 02번 파일 기준)
# ─────────────────────────────────────────────────────────────
CAT_TO_TORI_GROUP = {
    "수동태":         "passive_agreement",
    "수동태/수일치":  "passive_agreement",
    "수일치":         "passive_agreement",
    "시제":           "tense",
    "관계대명사":     "relative",
    "동명사/준동사":  "verbal",
    "분사구문":       "verbal",
    "동사형":         "form",
    "명사형":         "form",
    "부사형":         "form",
    "형용사형":       "form",
    "분사형":         "form",
    "문맥어휘":       "vocab",
    "콜로케이션":     "vocab",
    "혼동어휘":       "vocab",
    "전치사":         "linker",
    "접속부사":       "linker",
    "접속사":         "linker",
}


# ─────────────────────────────────────────────────────────────
# 1. 학생 통계 종합 분석
# ─────────────────────────────────────────────────────────────

def get_student_stats(nickname: str) -> Dict:
    """
    학생의 모든 데이터를 종합 분석해 stats 딕셔너리 반환.
    멘트 선택의 기준이 되는 "원천 데이터".

    RETURNS:
        {
            "has_data": bool,          # 데이터가 충분한가?
            "is_first_visit": bool,    # 첫 방문인가?
            "days_since_last": int,    # 마지막 방문 후 며칠?
            "streak_days": int,        # 연속 출석 일수
            "total_responses": int,    # 누적 응답 수
            "today_minutes": int,      # 오늘 학습 시간(분)
            "today_hour": int,         # 현재 시각(시)
            "is_weekend": bool,
            "p5_accuracy": float,      # P5 전체 정답률(0-100)
            "p7_accuracy": float,
            "yesterday_acc": float,    # 어제 정답률
            "today_acc": float,        # 오늘까지 정답률
            "trend": str,              # "up" / "down" / "flat"
            "weak_categories": [(cat, acc, count), ...],  # 약점 cat
            "prison_count": int,       # 수감 중 단어 수
            "repeat_words": [(word, count), ...],  # 3회+ 오답 단어
            "milestone_just_hit": str, # 방금 도달한 마일스톤
            "review_ratio": float,     # 복습 비율(0-1)
        }
    """
    try:
        conn = get_conn()
        cur = conn.cursor()
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")
        stats = _empty_stats(now)

        # 1. 학생 존재 여부
        cur.execute("SELECT registered_at, last_seen_at FROM students WHERE nickname = ?", (nickname,))
        student = cur.fetchone()
        if not student:
            conn.close()
            return stats  # 빈 stats (has_data=False)

        # 2. 누적 응답 수
        cur.execute("SELECT COUNT(*) FROM responses WHERE nickname = ?", (nickname,))
        stats["total_responses"] = cur.fetchone()[0]
        stats["has_data"] = stats["total_responses"] > 0
        stats["is_first_visit"] = stats["total_responses"] == 0

        # 3. 마지막 응답 날짜 → 결석 일수
        cur.execute("""
            SELECT MAX(DATE(ts)) FROM responses WHERE nickname = ?
        """, (nickname,))
        last_date_str = cur.fetchone()[0]
        if last_date_str:
            try:
                last_dt = datetime.strptime(last_date_str, "%Y-%m-%d").date()
                stats["days_since_last"] = (now.date() - last_dt).days
            except Exception:
                stats["days_since_last"] = 0

        # 4. 연속 출석 일수 (오늘 포함, 거꾸로 검사)
        stats["streak_days"] = _calc_streak(cur, nickname, now.date())

        # 5. 오늘 학습 시간 (sessions 합산)
        cur.execute("""
            SELECT COALESCE(SUM(duration_sec), 0)
            FROM sessions
            WHERE nickname = ? AND DATE(start_ts) = ?
        """, (nickname, today_str))
        sec = cur.fetchone()[0] or 0
        stats["today_minutes"] = sec // 60

        # 6. P5 / P7 정답률
        stats["p5_accuracy"] = _arena_accuracy(cur, nickname, "P5")
        stats["p7_accuracy"] = _arena_accuracy(cur, nickname, "P7")

        # 7. 어제 vs 오늘 정답률 → 추세
        yesterday_str = (now.date() - timedelta(days=1)).strftime("%Y-%m-%d")
        stats["today_acc"] = _date_accuracy(cur, nickname, today_str)
        stats["yesterday_acc"] = _date_accuracy(cur, nickname, yesterday_str)
        if stats["today_acc"] is not None and stats["yesterday_acc"] is not None:
            diff = stats["today_acc"] - stats["yesterday_acc"]
            if diff >= 5:
                stats["trend"] = "up"
            elif diff <= -5:
                stats["trend"] = "down"
            else:
                stats["trend"] = "flat"

        # 8. 약점 카테고리 (정답률 ≤70%, 응답 ≥3건)
        stats["weak_categories"] = _weak_categories(cur, nickname)

        # 9. 단어 포로 (수감 중)
        cur.execute("""
            SELECT COUNT(*) FROM word_prison
            WHERE nickname = ? AND released = 0
        """, (nickname,))
        stats["prison_count"] = cur.fetchone()[0]

        # 10. 같은 단어 3+ 오답
        cur.execute("""
            SELECT word, wrong_count FROM word_prison
            WHERE nickname = ? AND wrong_count >= 3 AND released = 0
            ORDER BY wrong_count DESC LIMIT 5
        """, (nickname,))
        stats["repeat_words"] = [(r["word"], r["wrong_count"]) for r in cur.fetchall()]

        # 11. 마일스톤 도달 여부
        stats["milestone_just_hit"] = _check_milestone(cur, nickname, stats["total_responses"])

        # 12. 복습 비율 (단어 포로 재출제율 — 추후 정교화)
        # 일단은 스킵 (시범 운영 후 데이터 쌓이면 추가)
        stats["review_ratio"] = 0.5  # 기본값

        conn.close()
        return stats

    except Exception as e:
        print(f"[inbody_brain] get_student_stats 실패: {e}")
        return _empty_stats(datetime.now())


def _empty_stats(now: datetime) -> Dict:
    """기본값으로 채워진 빈 stats 반환."""
    return {
        "has_data": False,
        "is_first_visit": True,
        "days_since_last": 0,
        "streak_days": 0,
        "total_responses": 0,
        "today_minutes": 0,
        "today_hour": now.hour,
        "is_weekend": now.weekday() >= 5,
        "p5_accuracy": None,
        "p7_accuracy": None,
        "yesterday_acc": None,
        "today_acc": None,
        "trend": "flat",
        "weak_categories": [],
        "prison_count": 0,
        "repeat_words": [],
        "milestone_just_hit": None,
        "review_ratio": 0.5,
    }


def _calc_streak(cur, nickname: str, today: date) -> int:
    """오늘부터 거꾸로 연속 출석 일수 계산."""
    streak = 0
    check = today
    while True:
        cur.execute("""
            SELECT 1 FROM responses
            WHERE nickname = ? AND DATE(ts) = ?
            LIMIT 1
        """, (nickname, check.strftime("%Y-%m-%d")))
        if cur.fetchone():
            streak += 1
            check -= timedelta(days=1)
            if streak > 365:  # 안전장치
                break
        else:
            break
    return streak


def _arena_accuracy(cur, nickname: str, arena: str) -> Optional[float]:
    """특정 arena의 누적 정답률(%). 응답 < 3건이면 None."""
    cur.execute("""
        SELECT COUNT(*) AS total,
               SUM(is_correct) AS correct
        FROM responses
        WHERE nickname = ? AND arena = ?
    """, (nickname, arena))
    row = cur.fetchone()
    if not row or row["total"] < 3:
        return None
    return round(100.0 * row["correct"] / row["total"], 1)


def _date_accuracy(cur, nickname: str, date_str: str) -> Optional[float]:
    """특정 날짜의 정답률(%). 응답 0건이면 None."""
    cur.execute("""
        SELECT COUNT(*) AS total,
               SUM(is_correct) AS correct
        FROM responses
        WHERE nickname = ? AND DATE(ts) = ?
    """, (nickname, date_str))
    row = cur.fetchone()
    if not row or row["total"] == 0:
        return None
    return round(100.0 * row["correct"] / row["total"], 1)


def _weak_categories(cur, nickname: str) -> List[Tuple[str, float, int]]:
    """
    약점 카테고리 (정답률 ≤70%, 응답 ≥3건) 목록.
    정답률 낮은 순으로 반환.
    """
    cur.execute("""
        SELECT category,
               COUNT(*) AS total,
               SUM(is_correct) AS correct
        FROM responses
        WHERE nickname = ?
          AND category IS NOT NULL AND category != ''
        GROUP BY category
        HAVING total >= 3
    """, (nickname,))
    weak = []
    for row in cur.fetchall():
        acc = 100.0 * row["correct"] / row["total"]
        if acc <= 70:
            weak.append((row["category"], round(acc, 1), row["total"]))
    weak.sort(key=lambda x: x[1])  # 정답률 낮은 순
    return weak


def _check_milestone(cur, nickname: str, total: int) -> Optional[str]:
    """방금 도달한 마일스톤 (오늘 처음 넘겼으면 반환)."""
    # 단순화: 100/500/1000 도달 즈음이면 표시
    # (정확하게는 "오늘 첫 응답 전엔 99 였는데 지금은 100 이상" 체크)
    milestones = [(1000, "1000"), (500, "500"), (100, "100")]
    today_str = datetime.now().strftime("%Y-%m-%d")
    cur.execute("""
        SELECT COUNT(*) FROM responses
        WHERE nickname = ? AND DATE(ts) < ?
    """, (nickname, today_str))
    yesterday_total = cur.fetchone()[0]

    for threshold, label in milestones:
        if yesterday_total < threshold <= total:
            return label
    return None


# ─────────────────────────────────────────────────────────────
# 2. 우선순위 시그널 추출 (어떤 멘트 카테고리가 트리거되나)
# ─────────────────────────────────────────────────────────────

def detect_signals(stats: Dict) -> List[Dict]:
    """
    stats에서 트리거된 모든 시그널을 우선순위 순으로 반환.

    각 시그널: {"key": str, "character": str, "data": dict}

    character: "skull" / "tori" / "hae"
    """
    signals = []

    # ─── 최우선: 같은 단어 3+ 오답 ─────────────────────
    if stats["repeat_words"]:
        word, count = stats["repeat_words"][0]
        signals.append({
            "key": "same_word_3plus",
            "character": "skull",
            "data": {"word": word, "count": count},
        })

    # ─── 긴급: 포로 16명+ ──────────────────────────────
    if stats["prison_count"] >= 16:
        signals.append({
            "key": "prison_overflow",
            "character": "skull",
            "data": {"count": stats["prison_count"]},
        })

    # ─── 긴급: 4일+ 결석 ───────────────────────────────
    if stats["days_since_last"] >= 4:
        signals.append({
            "key": "absent_4plus_days",
            "character": "skull",
            "data": {"days": stats["days_since_last"]},
        })
    elif stats["days_since_last"] >= 1:
        signals.append({
            "key": "absent_short",
            "character": "skull",
            "data": {"days": stats["days_since_last"]},
        })

    # ─── 주의: 급격 하락 ───────────────────────────────
    if (stats["yesterday_acc"] is not None
        and stats["today_acc"] is not None
        and stats["yesterday_acc"] - stats["today_acc"] >= 10):
        signals.append({
            "key": "trend_drop_10pct",
            "character": "skull",
            "data": {
                "yesterday": stats["yesterday_acc"],
                "today": stats["today_acc"],
            },
        })

    # ─── 축하: 마일스톤 ────────────────────────────────
    if stats["milestone_just_hit"]:
        signals.append({
            "key": "milestone_unlock",
            "character": "skull",
            "data": {"milestone": stats["milestone_just_hit"]},
        })

    # ─── 약점 카테고리 (P5 우선) ───────────────────────
    if stats["weak_categories"]:
        cat, acc, count = stats["weak_categories"][0]
        group = CAT_TO_TORI_GROUP.get(cat)
        if group:
            signals.append({
                "key": "weak_p5_category",
                "character": "tori",
                "data": {
                    "category": cat,
                    "group": group,
                    "accuracy": acc,
                    "count": count,
                },
            })

    # ─── 추세: 3일 연속 상승 (단순화: 오늘 +5%) ────────
    if stats["trend"] == "up":
        signals.append({
            "key": "trend_up",
            "character": "skull",
            "data": {
                "yesterday": stats["yesterday_acc"],
                "today": stats["today_acc"],
            },
        })

    # ─── 출석 스트릭 ───────────────────────────────────
    if stats["streak_days"] >= 2:
        signals.append({
            "key": "streak_milestone",
            "character": "skull",
            "data": {"days": stats["streak_days"]},
        })

    # ─── 오늘 학습 시간 ────────────────────────────────
    if stats["today_minutes"] > 0:
        signals.append({
            "key": "today_time",
            "character": "skull",
            "data": {"minutes": stats["today_minutes"]},
        })

    # ─── 마지막 보루: 시간대 ────────────────────────────
    signals.append({
        "key": "time_of_day",
        "character": "skull",
        "data": {
            "hour": stats["today_hour"],
            "is_weekend": stats["is_weekend"],
        },
    })

    return signals


# ─────────────────────────────────────────────────────────────
# 3. 메시지 빌더 (메인 1개 + 보조 최대 2개)
# ─────────────────────────────────────────────────────────────

def build_inbody_messages(nickname: str, max_count: int = 3) -> List[Dict]:
    """
    인바디에 표시할 메시지 1~3개 반환.
    데이터 적으면 1~2개, 풍성하면 3개.

    RETURNS:
        [
            {"character": "skull", "size": "main", "key": "...", "data": {...}},
            {"character": "tori",  "size": "sub",  "key": "...", "data": {...}},
            {"character": "hae",   "size": "sub",  "key": "...", "data": {...}},
        ]

    NOTE:
        실제 멘트 텍스트는 inbody_messages.py에서 풀에서 랜덤 선택.
        여기선 어떤 시그널을 띄울지만 결정.
    """
    stats = get_student_stats(nickname)

    # 첫 방문 (데이터 0)은 별도 처리
    if stats["is_first_visit"]:
        return []  # → 환영 시퀀스로 분기 (UI 단에서 처리)

    signals = detect_signals(stats)
    if not signals:
        return []

    # 캐릭터별 1개씩만 (다양성 보장)
    selected = []
    used_chars = set()

    for sig in signals:
        if len(selected) >= max_count:
            break
        if sig["character"] in used_chars:
            continue
        selected.append(sig)
        used_chars.add(sig["character"])

    # 캐릭터 다 쓴 후에도 자리 남으면 같은 캐릭터 허용 (시그널 키만 다르면)
    if len(selected) < max_count:
        used_keys = {s["key"] for s in selected}
        for sig in signals:
            if len(selected) >= max_count:
                break
            if sig["key"] not in used_keys:
                selected.append(sig)
                used_keys.add(sig["key"])

    # 사이즈 부여: 첫 번째 = main, 나머지 = sub
    for i, sig in enumerate(selected):
        sig["size"] = "main" if i == 0 else "sub"

    return selected


# ─────────────────────────────────────────────────────────────
# 자가 점검
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from app.core.inbody_db import init_db
    from app.core.inbody_logger import (
        ensure_student, start_session, end_session,
        log_response, update_word_prison,
    )

    print("=" * 60)
    print("SnapQ inbody_brain 자가 점검")
    print("=" * 60)

    init_db()

    # ─── 시나리오 1: 신규 학생 (데이터 없음) ──────────
    print("\n[시나리오 1] 신규 학생")
    ensure_student("브레인1", cohort="2026-05", consent_inbody=True)
    stats = get_student_stats("브레인1")
    msgs = build_inbody_messages("브레인1")
    print(f"  is_first_visit: {stats['is_first_visit']}")
    print(f"  메시지: {len(msgs)}개 (예상: 0개 — 환영 시퀀스로 분기)")
    assert len(msgs) == 0, "신규는 0개여야 함"
    print("  ✅")

    # ─── 시나리오 2: 약점 + 포로 + 시간대 ─────────────
    print("\n[시나리오 2] 약점 카테고리 + 포로 + 시간대")
    ensure_student("브레인2", cohort="2026-05", consent_inbody=True)
    sid = start_session("브레인2")

    # 수동태 약점 (5문제 중 1개 정답 = 20%)
    for i, ok in enumerate([True, False, False, False, False]):
        log_response(
            nickname="브레인2", session_id=sid,
            arena="P5", sub_type="grammar", q_id=f"G{100+i}",
            category="수동태", diff="easy",
            is_correct=ok, response_time_ms=2000,
        )

    # 단어 포로 — allocate 3회 오답 (반복 단어 트리거)
    for _ in range(3):
        update_word_prison("브레인2", "allocate", is_correct=False)

    end_session(sid)

    stats = get_student_stats("브레인2")
    msgs = build_inbody_messages("브레인2")

    print(f"  P5 정답률: {stats['p5_accuracy']}%")
    print(f"  약점 cat: {stats['weak_categories']}")
    print(f"  포로 수: {stats['prison_count']}")
    print(f"  반복 단어: {stats['repeat_words']}")
    print(f"\n  메시지 {len(msgs)}개:")
    for i, m in enumerate(msgs):
        print(f"    [{m['size']}] {m['character']:5s}  key={m['key']}")
        print(f"           data={m['data']}")
    assert len(msgs) >= 1, "메시지가 있어야 함"
    assert msgs[0]["size"] == "main"
    print("  ✅")

    # ─── 시나리오 3: 풍부한 데이터 ────────────────────
    print("\n[시나리오 3] 풍부한 데이터 (3개 멘트 기대)")
    ensure_student("브레인3", cohort="2026-05", consent_inbody=True)
    sid = start_session("브레인3")

    # 약점 (P5 관계대명사)
    for i, ok in enumerate([True] * 2 + [False] * 4):
        log_response(
            nickname="브레인3", session_id=sid,
            arena="P5", sub_type="grammar", q_id=f"G{200+i}",
            category="관계대명사", diff="mid",
            is_correct=ok, response_time_ms=3000,
        )

    # 포로 다수 (16명 트리거)
    for i in range(20):
        update_word_prison("브레인3", f"word{i}", is_correct=False)

    # 반복 오답
    for _ in range(4):
        update_word_prison("브레인3", "implement", is_correct=False)

    end_session(sid)

    msgs = build_inbody_messages("브레인3")
    print(f"  메시지 {len(msgs)}개:")
    for m in msgs:
        print(f"    [{m['size']:5s}] {m['character']:5s}  {m['key']}")

    # ─── 정리 ────────────────────────────────────────
    print("\n[정리] 테스트 데이터 삭제")
    conn = get_conn()
    cur = conn.cursor()
    for nick in ["브레인1", "브레인2", "브레인3"]:
        cur.execute("DELETE FROM responses WHERE nickname = ?", (nick,))
        cur.execute("DELETE FROM word_prison WHERE nickname = ?", (nick,))
        cur.execute("DELETE FROM sessions WHERE nickname = ?", (nick,))
        cur.execute("DELETE FROM students WHERE nickname = ?", (nick,))
        cur.execute("DELETE FROM sync_queue WHERE row_data LIKE ?", (f"%{nick}%",))
    conn.commit()
    conn.close()
    print("  완료")

    print("\n" + "=" * 60)
    print("자가 점검 완료! ✅")
    print("=" * 60)
