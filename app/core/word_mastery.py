"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE:     app/core/word_mastery.py
ROLE:     단어 마스터 시스템 — 진행도 추적 + 수배 단어
VERSION:  SnapQ TOEIC V3 — 2026.04.30
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USAGE:
    from app.core.word_mastery import (
        log_word_attempt, get_mastery_stats,
        get_unmastered_words, get_wanted_words, get_tier,
    )

    # 게임 중 단어 시도 기록
    log_word_attempt("민지", "allocate", "verb", is_correct=True)

    # 진행도 조회
    stats = get_mastery_stats("민지")
    # → {"total_mastered": 47, "tier": "brick", "next_tier_at": 50, ...}

    # 게임용 단어 5개 추출 (마스터 안 된 단어 우선)
    words = get_unmastered_words("민지", pos="verb", limit=5)

    # 수배 단어 추출 (자주 틀리는 단어)
    wanted = get_wanted_words("민지", limit=5)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DESIGN:
    마스터 기준: 2번 연속 정답
    오답 → consecutive_correct = 0 (리셋)
    
TIERS (옵션 B — 5단계):
    🥉 브론즈    = 50개
    🥈 실버     = 100개
    🥇 골드     = 200개
    💎 플래티넘 = 350개
    👑 마스터   = 510개 (전체)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import random
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from app.core.inbody_db import get_conn


# ═══════════════════════════════════════════════════════════════
# 등급 시스템 (옵션 B — 5단계)
# ═══════════════════════════════════════════════════════════════

TIERS = [
    ("none",      0,    "❓", "신참"),
    ("bronze",    50,   "🥉", "브론즈"),
    ("silver",    100,  "🥈", "실버"),
    ("gold",      200,  "🥇", "골드"),
    ("platinum",  350,  "💎", "플래티넘"),
    ("master",    510,  "👑", "마스터"),
]


# ─────────────────────────────────────────────────────────────
# 단어 풀 경로
# ─────────────────────────────────────────────────────────────

BASE = Path(__file__).parent.parent.parent
WORD_POOL_PATH = BASE / "data" / "word_pool_categorized.json"


def _load_word_pool() -> dict:
    """카테고리화된 단어 풀 로드."""
    if WORD_POOL_PATH.exists():
        try:
            return json.loads(WORD_POOL_PATH.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"[word_mastery] 풀 로드 실패: {e}")
    return {}


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


# ═══════════════════════════════════════════════════════════════
# 1. 시도 기록
# ═══════════════════════════════════════════════════════════════

def log_word_attempt(nickname: str,
                     word: str,
                     pos: str,
                     is_correct: bool) -> Dict:
    """
    단어 한 번 시도 기록 + 마스터 판정.

    LOGIC:
        정답: consecutive_correct +1, total_correct +1
              → consecutive_correct >= 2 이면 mastered = 1
        오답: consecutive_correct = 0 (리셋)
              → mastered 가 1이었어도 유지 (한 번 마스터하면 풀리지 않음)

    RETURNS:
        {
            "word": str,
            "consecutive_correct": int,
            "mastered": bool,
            "newly_mastered": bool,  # 이번 시도로 새로 마스터됐는지
        }
    """
    if not nickname or not word:
        return {"error": "nickname/word required"}

    try:
        conn = get_conn()
        cur = conn.cursor()
        now = _now_iso()

        # 기존 레코드 조회
        cur.execute("""
            SELECT consecutive_correct, mastered, total_seen, total_correct, total_wrong
            FROM word_mastery
            WHERE nickname = ? AND word = ?
        """, (nickname, word))
        row = cur.fetchone()

        if row is None:
            # 신규 레코드
            consec = 1 if is_correct else 0
            mastered = 0  # 1회 정답으로는 마스터 안 됨
            newly_mastered = False
            cur.execute("""
                INSERT INTO word_mastery (
                    nickname, word, pos, consecutive_correct, mastered,
                    total_seen, total_correct, total_wrong, last_seen
                ) VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?)
            """, (
                nickname, word, pos,
                consec, mastered,
                1 if is_correct else 0,
                0 if is_correct else 1,
                now,
            ))
        else:
            # 기존 레코드 업데이트
            old_mastered = row["mastered"]
            old_consec = row["consecutive_correct"]

            if is_correct:
                new_consec = old_consec + 1
                new_total_correct = row["total_correct"] + 1
                new_total_wrong = row["total_wrong"]
                # 마스터 판정 (이미 마스터면 유지)
                if new_consec >= 2 and old_mastered == 0:
                    new_mastered = 1
                    newly_mastered = True
                    mastered_at = now
                else:
                    new_mastered = old_mastered
                    newly_mastered = False
                    mastered_at = None
            else:
                new_consec = 0  # 리셋
                new_total_correct = row["total_correct"]
                new_total_wrong = row["total_wrong"] + 1
                new_mastered = old_mastered  # 한 번 마스터한 건 유지
                newly_mastered = False
                mastered_at = None

            if newly_mastered:
                cur.execute("""
                    UPDATE word_mastery
                    SET consecutive_correct = ?, mastered = ?, mastered_at = ?,
                        total_seen = total_seen + 1,
                        total_correct = ?, total_wrong = ?,
                        last_seen = ?
                    WHERE nickname = ? AND word = ?
                """, (
                    new_consec, new_mastered, mastered_at,
                    new_total_correct, new_total_wrong, now,
                    nickname, word,
                ))
            else:
                cur.execute("""
                    UPDATE word_mastery
                    SET consecutive_correct = ?, mastered = ?,
                        total_seen = total_seen + 1,
                        total_correct = ?, total_wrong = ?,
                        last_seen = ?
                    WHERE nickname = ? AND word = ?
                """, (
                    new_consec, new_mastered,
                    new_total_correct, new_total_wrong, now,
                    nickname, word,
                ))

            consec = new_consec
            mastered = new_mastered

        conn.commit()
        conn.close()

        return {
            "word": word,
            "consecutive_correct": consec,
            "mastered": bool(mastered),
            "newly_mastered": newly_mastered,
        }

    except Exception as e:
        print(f"[word_mastery] log_word_attempt 실패: {e}")
        return {"error": str(e)}


# ═══════════════════════════════════════════════════════════════
# 2. 진행도 조회
# ═══════════════════════════════════════════════════════════════

def get_mastery_stats(nickname: str) -> Dict:
    """
    학생의 전체 마스터 진행도 + 카테고리별 + 등급.

    RETURNS:
        {
            "total_mastered": int,
            "tier": str,            # "bronze" / "silver" / ...
            "tier_emoji": str,
            "tier_label": str,
            "next_tier_at": int,    # 다음 등급까지 필요한 마스터 수
            "next_tier_label": str,
            "by_pos": {
                "noun":      {"mastered": 21, "total": 117},
                "verb":      {"mastered": 13, "total": 110},
                "adjective": {"mastered": 8,  "total": 181},
                "adverb":    {"mastered": 5,  "total": 102},
            },
        }
    """
    pool = _load_word_pool()

    result = {
        "total_mastered": 0,
        "tier": "none",
        "tier_emoji": "❓",
        "tier_label": "신참",
        "next_tier_at": 50,
        "next_tier_label": "🥉 브론즈",
        "by_pos": {},
    }

    if not nickname:
        return result

    try:
        conn = get_conn()
        cur = conn.cursor()

        # 카테고리별 외운 단어 개수 (한 번이라도 정답한 단어)
        cur.execute("""
            SELECT pos, COUNT(*) AS cnt
            FROM word_mastery
            WHERE nickname = ? AND total_correct >= 1
            GROUP BY pos
        """, (nickname,))

        mastered_by_pos = {row["pos"]: row["cnt"] for row in cur.fetchall()}
        total_mastered = sum(mastered_by_pos.values())

        # 카테고리별 전체 단어 수 (풀에서)
        for pos in ["noun", "verb", "adjective", "adverb"]:
            total = len(pool.get(pos, []))
            result["by_pos"][pos] = {
                "mastered": mastered_by_pos.get(pos, 0),
                "total":    total,
                "pct":      round(100.0 * mastered_by_pos.get(pos, 0) / total, 1) if total else 0,
            }

        result["total_mastered"] = total_mastered

        # 등급 판정
        current_tier = TIERS[0]
        next_tier = None
        for i, (tier_key, threshold, emoji, label) in enumerate(TIERS):
            if total_mastered >= threshold:
                current_tier = TIERS[i]
                next_tier = TIERS[i + 1] if i + 1 < len(TIERS) else None

        result["tier"] = current_tier[0]
        result["tier_emoji"] = current_tier[2]
        result["tier_label"] = current_tier[3]

        if next_tier:
            result["next_tier_at"] = next_tier[1]
            result["next_tier_label"] = f"{next_tier[2]} {next_tier[3]}"
            result["next_tier_remaining"] = next_tier[1] - total_mastered
        else:
            result["next_tier_at"] = None
            result["next_tier_label"] = "최고 등급!"
            result["next_tier_remaining"] = 0

        conn.close()
        return result

    except Exception as e:
        print(f"[word_mastery] get_mastery_stats 실패: {e}")
        return result


def get_tier(nickname: str) -> Tuple[str, str, str]:
    """
    현재 등급 반환 (간단 버전).

    RETURNS:
        (tier_key, emoji, label)
        예: ("bronze", "🥉", "브론즈")
    """
    stats = get_mastery_stats(nickname)
    return (stats["tier"], stats["tier_emoji"], stats["tier_label"])


def get_category_progress(nickname: str, pos: str) -> Dict:
    """특정 카테고리의 진행도."""
    stats = get_mastery_stats(nickname)
    return stats["by_pos"].get(pos, {"mastered": 0, "total": 0, "pct": 0})


# ═══════════════════════════════════════════════════════════════
# 3. 게임용 단어 추출
# ═══════════════════════════════════════════════════════════════

def get_unmastered_words(nickname: str,
                         pos: Optional[str] = None,
                         limit: int = 5) -> List[Dict]:
    """
    아직 마스터 안 된 단어 추출 (게임용).

    LOGIC:
        1. 한 번이라도 본 적 있는데 마스터 안 된 단어 우선 (consecutive_correct=1 이런 거)
        2. 그 다음 한 번도 안 본 단어 (신규)

    PARAMS:
        nickname: 학생
        pos:      품사 필터 (None이면 전체)
        limit:    개수

    RETURNS:
        [{"word": str, "meaning": str, "pos": str, "source": "in_progress"/"new"}, ...]
    """
    pool = _load_word_pool()

    if not nickname or not pool:
        return []

    try:
        conn = get_conn()
        cur = conn.cursor()

        # 학생이 본 단어 + 마스터 여부
        cur.execute("""
            SELECT word, mastered, consecutive_correct
            FROM word_mastery
            WHERE nickname = ?
        """, (nickname,))

        seen_data = {row["word"]: dict(row) for row in cur.fetchall()}

        # 카테고리 결정
        pos_list = [pos] if pos else ["noun", "verb", "adjective", "adverb"]

        # 모든 후보 단어 수집
        all_candidates = []
        for p in pos_list:
            for item in pool.get(p, []):
                w = item["word"]
                seen = seen_data.get(w)
                # 이미 마스터한 단어 제외
                if seen and seen["mastered"] == 1:
                    continue
                
                if seen:
                    # 본 적은 있지만 아직 마스터 안 됨
                    source = "in_progress"
                    consec = seen["consecutive_correct"]
                else:
                    source = "new"
                    consec = 0
                
                all_candidates.append({
                    "word":     w,
                    "meaning":  item["meaning"],
                    "pos":      p,
                    "source":   source,
                    "consecutive_correct": consec,
                })

        # 우선순위: in_progress 먼저, 그 다음 new
        in_progress = [c for c in all_candidates if c["source"] == "in_progress"]
        new_words = [c for c in all_candidates if c["source"] == "new"]

        random.shuffle(in_progress)
        random.shuffle(new_words)

        result = (in_progress + new_words)[:limit]
        conn.close()
        return result

    except Exception as e:
        print(f"[word_mastery] get_unmastered_words 실패: {e}")
        return []


def get_wanted_words(nickname: str, limit: int = 5) -> List[Dict]:
    """
    "수배 단어" 추출 — 자주 틀리는 단어.

    LOGIC:
        word_mastery에서 total_wrong > 0 AND mastered = 0
        오답 횟수 많은 순으로 정렬

    RETURNS:
        [{"word": str, "meaning": str, "pos": str,
          "wrong_count": int, "consecutive_correct": int}, ...]
    """
    pool = _load_word_pool()
    if not nickname or not pool:
        return []

    # word → meaning, pos 매핑
    word_info = {}
    for p in ["noun", "verb", "adjective", "adverb"]:
        for item in pool.get(p, []):
            word_info[item["word"]] = {"meaning": item["meaning"], "pos": p}

    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT word, total_wrong, total_correct, consecutive_correct
            FROM word_mastery
            WHERE nickname = ?
              AND total_wrong > 0
              AND mastered = 0
            ORDER BY total_wrong DESC, total_correct ASC
            LIMIT ?
        """, (nickname, limit))

        result = []
        for row in cur.fetchall():
            info = word_info.get(row["word"])
            if not info:
                continue
            result.append({
                "word":      row["word"],
                "meaning":   info["meaning"],
                "pos":       info["pos"],
                "wrong_count": row["total_wrong"],
                "consecutive_correct": row["consecutive_correct"],
            })

        conn.close()
        return result

    except Exception as e:
        print(f"[word_mastery] get_wanted_words 실패: {e}")
        return []


# ═══════════════════════════════════════════════════════════════
# 자가 점검
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    from app.core.inbody_db import init_db, get_conn
    from app.core.inbody_logger import ensure_student

    print("=" * 60)
    print("SnapQ word_mastery 자가 점검")
    print("=" * 60)

    init_db()

    # 1. 단어 풀 로드
    print("\n[1] 단어 풀 로드:")
    pool = _load_word_pool()
    if pool:
        for pos in ["noun", "verb", "adjective", "adverb"]:
            print(f"   {pos:10s}: {len(pool.get(pos, []))}개")
    else:
        print("   ❌ 단어 풀 없음 — prepare_word_pool.py 먼저 실행 필요")
        exit(1)

    # 2. 학생 등록
    nick = "마스터테스트"
    ensure_student(nick, cohort="2026-05", consent_inbody=True)
    print(f"\n[2] 학생 등록: {nick}")

    # 3. 단어 시도 시뮬 — 마스터까지
    print(f"\n[3] log_word_attempt 시뮬:")
    print(f"   첫 번째 정답:")
    r = log_word_attempt(nick, "allocate", "verb", is_correct=True)
    print(f"     consec={r['consecutive_correct']}, mastered={r['mastered']}, "
          f"new_master={r['newly_mastered']}")
    
    print(f"   두 번째 정답 (마스터!):")
    r = log_word_attempt(nick, "allocate", "verb", is_correct=True)
    print(f"     consec={r['consecutive_correct']}, mastered={r['mastered']}, "
          f"new_master={r['newly_mastered']}")
    
    print(f"   세 번째 오답 (마스터 유지):")
    r = log_word_attempt(nick, "allocate", "verb", is_correct=False)
    print(f"     consec={r['consecutive_correct']}, mastered={r['mastered']}")

    print(f"\n   '리셋' 단어 시뮬 (정답→오답→정답→정답=마스터):")
    log_word_attempt(nick, "implement", "verb", is_correct=True)
    log_word_attempt(nick, "implement", "verb", is_correct=False)  # 리셋!
    r = log_word_attempt(nick, "implement", "verb", is_correct=True)
    print(f"     1번 정답+오답 후: consec={r['consecutive_correct']} (오답으로 리셋됨)")
    r = log_word_attempt(nick, "implement", "verb", is_correct=True)
    print(f"     다시 정답 2회: consec={r['consecutive_correct']}, mastered={r['mastered']}")

    # 4. 더미 마스터 추가 (등급 확인용)
    print(f"\n[4] 51개 단어 마스터 추가 (브론즈 도달 테스트):")
    test_words = ["test_w" + str(i) for i in range(51)]
    for w in test_words:
        log_word_attempt(nick, w, "noun", is_correct=True)
        log_word_attempt(nick, w, "noun", is_correct=True)

    # 5. 진행도 조회
    print(f"\n[5] get_mastery_stats:")
    stats = get_mastery_stats(nick)
    print(f"   총 마스터: {stats['total_mastered']}개")
    print(f"   현재 등급: {stats['tier_emoji']} {stats['tier_label']} ({stats['tier']})")
    print(f"   다음 등급: {stats['next_tier_label']} ({stats.get('next_tier_remaining', 0)}개 남음)")
    print(f"   카테고리별:")
    for pos, info in stats["by_pos"].items():
        print(f"     {pos:10s}: {info['mastered']}/{info['total']} ({info['pct']}%)")

    # 6. 게임 단어 추출
    print(f"\n[6] get_unmastered_words (verb, 5개):")
    words = get_unmastered_words(nick, pos="verb", limit=5)
    for w in words:
        print(f"   [{w['source']:11s}] {w['word']:15s} → {w['meaning']}")

    # 7. 수배 단어
    print(f"\n[7] get_wanted_words (수배 — 자주 틀린 단어):")
    log_word_attempt(nick, "evaluate", "verb", is_correct=False)
    log_word_attempt(nick, "evaluate", "verb", is_correct=False)
    log_word_attempt(nick, "evaluate", "verb", is_correct=False)
    wanted = get_wanted_words(nick, limit=5)
    for w in wanted:
        print(f"   {w['word']:15s} (wrong {w['wrong_count']}회)")

    # 정리
    print(f"\n[정리] 테스트 데이터 삭제")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM word_mastery WHERE nickname = ?", (nick,))
    cur.execute("DELETE FROM students WHERE nickname = ?", (nick,))
    cur.execute("DELETE FROM sync_queue WHERE row_data LIKE ?", (f"%{nick}%",))
    conn.commit()
    conn.close()
    print("   완료")

    print("\n" + "=" * 60)
    print("자가 점검 완료! ✅")
    print("=" * 60)
