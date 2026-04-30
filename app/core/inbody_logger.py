"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FILE:     app/core/inbody_logger.py
ROLE:     인바디 시스템 데이터 로깅 함수 모음
VERSION:  SnapQ TOEIC V3 — 2026.04.30
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
USAGE:
    from app.core.inbody_logger import (
        ensure_student, start_session, end_session,
        log_response, update_word_prison, enqueue_sync,
    )

    # 1. 학생 등록 (로그인 직후)
    ensure_student(nickname, cohort="2026-05")

    # 2. 세션 시작 (페이지 진입 시)
    session_id = start_session(nickname)

    # 3. 매 문제마다 응답 기록
    log_response(
        nickname=nickname,
        session_id=session_id,
        arena="P5",
        sub_type="grammar",
        q_id="G1",
        category="수동태",
        diff="easy",
        is_correct=True,
        response_time_ms=2340,
        target_words=["require", "mandatory"],
    )

    # 4. 단어 포로 추가 (오답 시)
    update_word_prison(nickname, "allocate", is_correct=False)

    # 5. 세션 종료 (페이지 이탈 시)
    end_session(session_id)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DESIGN:
    ─ 모든 함수는 try/except로 감싸 실패해도 학습 도구는 정상 작동
    ─ INBODY_MODE 플래그로 전체 로깅 ON/OFF 가능
    ─ 학생이 미니 동의서 동의해야만 실제 기록 (consent_inbody=1)
    ─ 모든 쓰기는 sync_queue에도 적재 → 5분 후 Sheets 백업
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import sqlite3
from datetime import datetime
from typing import Optional, List

from app.core.inbody_db import get_conn, init_db


# ═══════════════════════════════════════════════════════════════
# ★ INBODY MODE FLAG ★
# ═══════════════════════════════════════════════════════════════
# 인바디 시스템 전체 ON/OFF 스위치.
# 문제 발생 시 즉시 False로 변경하면 모든 로깅 중단.
# (단, IRB와는 별개 — 학생 본인 진단용 데이터)
INBODY_MODE = True
# ═══════════════════════════════════════════════════════════════


# ─────────────────────────────────────────────────────────────
# 내부 유틸
# ─────────────────────────────────────────────────────────────

def _now_iso() -> str:
    """현재 시각을 ISO 형식 문자열로 (초 단위까지)."""
    return datetime.now().isoformat(timespec="seconds")


def _check_consent(conn: sqlite3.Connection, nickname: str) -> bool:
    """
    학생이 인바디 동의를 했는지 확인.
    - 동의 안 했거나 학생이 없으면 False
    - 동의했으면 True
    """
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT consent_inbody FROM students WHERE nickname = ?",
            (nickname,)
        )
        row = cur.fetchone()
        return bool(row and row["consent_inbody"] == 1)
    except Exception:
        return False


# ─────────────────────────────────────────────────────────────
# 공개 API
# ─────────────────────────────────────────────────────────────

def ensure_student(nickname: str,
                   cohort: str = "",
                   consent_inbody: bool = False) -> bool:
    """
    학생을 students 테이블에 등록 or last_seen_at 업데이트.

    PARAMS:
        nickname:       별명 (PRIMARY KEY)
        cohort:         코호트 (예: "2026-05")
        consent_inbody: 인바디 동의 여부 (첫 등록 시만 적용)

    USAGE:
        # 첫 로그인 (동의 후)
        ensure_student("민지", cohort="2026-05", consent_inbody=True)

        # 재로그인 (last_seen_at만 갱신)
        ensure_student("민지")

    RETURNS:
        True: 성공
        False: 실패
    """
    if not INBODY_MODE or not nickname:
        return False

    try:
        conn = get_conn()
        cur = conn.cursor()
        now = _now_iso()

        # 이미 있는지 확인
        cur.execute("SELECT nickname FROM students WHERE nickname = ?", (nickname,))
        exists = cur.fetchone() is not None

        if exists:
            # last_seen_at만 갱신
            cur.execute(
                "UPDATE students SET last_seen_at = ? WHERE nickname = ?",
                (now, nickname)
            )
        else:
            # 새 학생 등록
            cur.execute("""
                INSERT INTO students (
                    nickname, cohort, consent_inbody, consent_inbody_at,
                    registered_at, last_seen_at
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                nickname,
                cohort,
                1 if consent_inbody else 0,
                now if consent_inbody else None,
                now,
                now,
            ))
            # 동기화 큐에 등록
            _enqueue_inline(cur, "students", {
                "nickname": nickname,
                "cohort": cohort,
                "consent_inbody": 1 if consent_inbody else 0,
                "registered_at": now,
            })

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print(f"[inbody_logger] ensure_student 실패: {e}")
        return False


def grant_consent(nickname: str) -> bool:
    """
    이미 등록된 학생이 미니 동의서에 동의했을 때 호출.
    consent_inbody = 1, consent_inbody_at = 현재 시각으로 업데이트.
    """
    if not INBODY_MODE or not nickname:
        return False

    try:
        conn = get_conn()
        cur = conn.cursor()
        now = _now_iso()
        cur.execute("""
            UPDATE students
            SET consent_inbody = 1, consent_inbody_at = ?
            WHERE nickname = ?
        """, (now, nickname))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"[inbody_logger] grant_consent 실패: {e}")
        return False


def start_session(nickname: str) -> Optional[int]:
    """
    새 세션 시작. 동의한 학생만 기록.

    RETURNS:
        session_id (int): 성공
        None: 동의 없음 or 실패
    """
    if not INBODY_MODE or not nickname:
        return None

    try:
        conn = get_conn()

        # 동의 확인
        if not _check_consent(conn, nickname):
            conn.close()
            return None

        cur = conn.cursor()
        now = _now_iso()
        cur.execute(
            "INSERT INTO sessions (nickname, start_ts) VALUES (?, ?)",
            (nickname, now)
        )
        session_id = cur.lastrowid
        conn.commit()
        conn.close()
        return session_id

    except Exception as e:
        print(f"[inbody_logger] start_session 실패: {e}")
        return None


def end_session(session_id: int) -> bool:
    """
    세션 종료. duration_sec 자동 계산.

    PARAMS:
        session_id: start_session()이 반환한 ID
    """
    if not INBODY_MODE or not session_id:
        return False

    try:
        conn = get_conn()
        cur = conn.cursor()
        now = _now_iso()

        # 시작 시간 조회
        cur.execute("SELECT start_ts, nickname FROM sessions WHERE id = ?", (session_id,))
        row = cur.fetchone()
        if not row:
            conn.close()
            return False

        # duration 계산
        try:
            start_dt = datetime.fromisoformat(row["start_ts"])
            duration = int((datetime.now() - start_dt).total_seconds())
        except Exception:
            duration = 0

        cur.execute("""
            UPDATE sessions
            SET end_ts = ?, duration_sec = ?
            WHERE id = ?
        """, (now, duration, session_id))

        # 동기화 큐
        _enqueue_inline(cur, "sessions", {
            "id": session_id,
            "nickname": row["nickname"],
            "end_ts": now,
            "duration_sec": duration,
        })

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print(f"[inbody_logger] end_session 실패: {e}")
        return False


def log_response(nickname: str,
                 arena: str,
                 q_id: str,
                 is_correct: bool,
                 session_id: Optional[int] = None,
                 sub_type: str = "",
                 category: str = "",
                 diff: str = "",
                 q_type: str = "",
                 target_words: Optional[List[str]] = None,
                 response_time_ms: int = 0) -> bool:
    """
    문제 응답 1건 기록 — ★ 가장 자주 호출되는 함수

    PARAMS:
        nickname:         학생
        arena:            'P5' / 'P7' / 'POW_p5exam' 등
        q_id:             문제 ID ('G1', 'V42' 등)
        is_correct:       정답 여부
        session_id:       (선택) 현재 세션
        sub_type:         (선택) 'grammar' / 'vocab' / 'cipher' 등
        category:         (선택) cat 필드 값 — '수동태' / '관계대명사' 등
        diff:             (선택) 'easy' / 'mid' / 'hard'
        q_type:           (선택) P7용 'purpose' / 'detail' / 'inference'
        target_words:     (선택) 단어 리스트 (자동으로 JSON 변환)
        response_time_ms: (선택) 응답 시간 (밀리초)

    DESIGN:
        - 동의 안 한 학생은 조용히 무시
        - 실패해도 예외 안 날림 (학습 도구 정상 작동 유지)
    """
    if not INBODY_MODE or not nickname or not q_id:
        return False

    try:
        conn = get_conn()

        # 동의 확인
        if not _check_consent(conn, nickname):
            conn.close()
            return False

        cur = conn.cursor()
        now = _now_iso()
        target_words_json = json.dumps(target_words or [], ensure_ascii=False)

        cur.execute("""
            INSERT INTO responses (
                nickname, session_id, arena, sub_type, q_id,
                category, diff, q_type, target_words,
                is_correct, response_time_ms, ts
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            nickname, session_id, arena, sub_type, q_id,
            category, diff, q_type, target_words_json,
            1 if is_correct else 0,
            int(response_time_ms) if response_time_ms else 0,
            now,
        ))

        # 동기화 큐
        _enqueue_inline(cur, "responses", {
            "nickname": nickname,
            "session_id": session_id,
            "arena": arena,
            "sub_type": sub_type,
            "q_id": q_id,
            "category": category,
            "diff": diff,
            "q_type": q_type,
            "target_words": target_words_json,
            "is_correct": 1 if is_correct else 0,
            "response_time_ms": int(response_time_ms) if response_time_ms else 0,
            "ts": now,
        })

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print(f"[inbody_logger] log_response 실패: {e}")
        return False


def update_word_prison(nickname: str,
                       word: str,
                       is_correct: bool) -> bool:
    """
    단어 포로 테이블 업데이트.

    LOGIC:
        - 오답이면 wrong_count 증가, last_wrong 갱신
        - 정답이면 released = 1 (석방)
        - 동의한 학생만 기록

    USAGE:
        update_word_prison("민지", "allocate", is_correct=False)  # 추가
        update_word_prison("민지", "allocate", is_correct=True)   # 석방
    """
    if not INBODY_MODE or not nickname or not word:
        return False

    try:
        conn = get_conn()

        if not _check_consent(conn, nickname):
            conn.close()
            return False

        cur = conn.cursor()
        now = _now_iso()

        # 기존 포로 확인
        cur.execute("""
            SELECT word, wrong_count, released
            FROM word_prison
            WHERE nickname = ? AND word = ?
        """, (nickname, word))
        existing = cur.fetchone()

        if is_correct:
            # 정답 → 석방
            if existing:
                cur.execute("""
                    UPDATE word_prison
                    SET released = 1, released_at = ?
                    WHERE nickname = ? AND word = ?
                """, (now, nickname, word))
        else:
            # 오답 → 추가 or 카운트 증가
            if existing:
                cur.execute("""
                    UPDATE word_prison
                    SET wrong_count = wrong_count + 1,
                        last_wrong = ?,
                        released = 0,
                        released_at = NULL
                    WHERE nickname = ? AND word = ?
                """, (now, nickname, word))
            else:
                cur.execute("""
                    INSERT INTO word_prison (
                        nickname, word, wrong_count,
                        first_wrong, last_wrong, released
                    ) VALUES (?, ?, 1, ?, ?, 0)
                """, (nickname, word, now, now))

        # 동기화 큐
        _enqueue_inline(cur, "word_prison", {
            "nickname": nickname,
            "word": word,
            "is_correct": 1 if is_correct else 0,
            "ts": now,
        })

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print(f"[inbody_logger] update_word_prison 실패: {e}")
        return False


# ─────────────────────────────────────────────────────────────
# 동기화 큐 (5분 주기 + 세션 종료 시 처리)
# ─────────────────────────────────────────────────────────────

def _enqueue_inline(cur: sqlite3.Cursor, table_name: str, row_data: dict) -> None:
    """
    내부 유틸: 같은 트랜잭션 안에서 동기화 큐에 적재.
    별도 connection 안 열고 cursor만 받아서 INSERT.
    """
    try:
        cur.execute("""
            INSERT INTO sync_queue (table_name, row_data, created_at, synced)
            VALUES (?, ?, ?, 0)
        """, (
            table_name,
            json.dumps(row_data, ensure_ascii=False),
            _now_iso(),
        ))
    except Exception:
        pass


def get_pending_sync_count() -> int:
    """동기화 대기 중인 행 개수 반환 (디버깅용)."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sync_queue WHERE synced = 0")
        count = cur.fetchone()[0]
        conn.close()
        return count
    except Exception:
        return -1


# ─────────────────────────────────────────────────────────────
# 자가 점검 (직접 실행 시)
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("SnapQ inbody_logger 자가 점검")
    print("=" * 60)

    # DB 초기화
    print("\n[0] DB 초기화...")
    init_db()
    print("    OK")

    # 1. 학생 등록 (동의 포함)
    print("\n[1] ensure_student('테스트', consent_inbody=True)")
    ok = ensure_student("테스트", cohort="2026-05", consent_inbody=True)
    print(f"    결과: {'✅' if ok else '❌'}")

    # 2. 세션 시작
    print("\n[2] start_session('테스트')")
    sid = start_session("테스트")
    print(f"    session_id: {sid}")

    # 3. 응답 3개 기록
    print("\n[3] log_response x3")
    log_response(
        nickname="테스트", session_id=sid,
        arena="P5", sub_type="grammar", q_id="G1",
        category="수동태", diff="easy", is_correct=True,
        response_time_ms=2300,
        target_words=["require", "mandatory"],
    )
    log_response(
        nickname="테스트", session_id=sid,
        arena="P5", sub_type="grammar", q_id="G2",
        category="가정법", diff="mid", is_correct=False,
        response_time_ms=4500,
    )
    log_response(
        nickname="테스트", session_id=sid,
        arena="P7", sub_type="cipher", q_id="C1",
        q_type="purpose", is_correct=True,
        response_time_ms=18500,
    )
    print(f"    응답 3개 기록 완료")

    # 4. 단어 포로 (오답 → 추가, 정답 → 석방)
    print("\n[4] update_word_prison")
    update_word_prison("테스트", "allocate", is_correct=False)
    update_word_prison("테스트", "allocate", is_correct=False)  # 2번째 오답
    update_word_prison("테스트", "implement", is_correct=False)
    update_word_prison("테스트", "implement", is_correct=True)  # 석방
    print(f"    포로 처리 완료")

    # 5. 세션 종료
    print("\n[5] end_session")
    end_session(sid)
    print(f"    세션 종료 완료")

    # 6. 검증 — 직접 SQL로 확인
    print("\n[6] 검증 (직접 SQL):")
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM students WHERE nickname = '테스트'")
    print(f"  students:    {dict(cur.fetchone())}")

    cur.execute("SELECT COUNT(*) AS cnt FROM responses WHERE nickname = '테스트'")
    print(f"  responses:   {cur.fetchone()['cnt']}건")

    cur.execute("SELECT word, wrong_count, released FROM word_prison WHERE nickname = '테스트'")
    for row in cur.fetchall():
        print(f"  word_prison: {row['word']} — {row['wrong_count']}회 오답, "
              f"{'석방' if row['released'] else '수감'}")

    cur.execute("SELECT duration_sec FROM sessions WHERE id = ?", (sid,))
    print(f"  session:     duration {cur.fetchone()['duration_sec']}초")

    conn.close()

    # 7. 동기화 큐 확인
    pending = get_pending_sync_count()
    print(f"\n[7] sync_queue 대기 중: {pending}건")

    # 정리 (테스트 데이터 삭제)
    print("\n[8] 테스트 데이터 정리...")
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM responses WHERE nickname = '테스트'")
    cur.execute("DELETE FROM word_prison WHERE nickname = '테스트'")
    cur.execute("DELETE FROM sessions WHERE nickname = '테스트'")
    cur.execute("DELETE FROM students WHERE nickname = '테스트'")
    cur.execute("DELETE FROM sync_queue WHERE row_data LIKE '%테스트%'")
    conn.commit()
    conn.close()
    print("    정리 완료")

    print("\n" + "=" * 60)
    print("자가 점검 완료! ✅")
    print("=" * 60)
